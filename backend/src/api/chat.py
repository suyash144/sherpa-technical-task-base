from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Iterator, Dict, List
import json
from src.models.chat import SimpleChatRequest, Message, StreamingChatMetadata, ChatResponse
from src.services.openai_client import get_openai
from src.services.rag import RAGEngine
from src.settings import settings

router = APIRouter(prefix="/chat", tags=["chat"])

# Simple in-memory conversation storage
# In production, you'd want to use a database with user sessions
conversations: Dict[str, List[Dict]] = {}

def get_or_create_conversation(session_id: str = "default") -> List[Dict]:
    """Get existing conversation or create a new one"""
    if session_id not in conversations:
        conversations[session_id] = []
    return conversations[session_id]

def stream_completion(openai, **kwargs) -> Iterator[str]:
    """Stream OpenAI completion responses"""
    try:
        for chunk in openai.chat.completions.create(stream=True, **kwargs):
            # Check if chunk has choices and the first choice has content
            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    yield f"data: {delta.content}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: Error: {str(e)}\n\n"
        yield "data: [DONE]\n\n"

@router.post("/message", 
    responses={
        200: {
            "description": "Streaming chat response with source references",
            "content": {
                "text/event-stream": {
                    "example": """data: Hello

data: !

data:  How

data:  can

data:  I

data:  assist

data:  you

data:  today

data: ?

data:  😊

data: [SOURCES]{"sources":[{"document_id":"abc123","filename":"example.pdf","page":1,"relevance_score":0.85}]}

data: [DONE]

"""
                }
            }
        }
    }
)
async def send_message(req: SimpleChatRequest, session_id: str = "default"):
    """
    Send a message to the chatbot. The backend manages conversation history.
    Always streams responses and uses RAG for context.
    
    The response is streamed as Server-Sent Events (SSE) format where each chunk
    of the AI's response is sent as a separate 'data:' line.
    
    After the response is complete, a 'data: [SOURCES]' line contains JSON metadata
    about the documents used to generate the response, followed by 'data: [DONE]'.
    
    Example flow:
    1. data: Hello
    2. data:  there!
    3. data: [SOURCES]{"sources":[{"document_id":"abc","filename":"doc.pdf","page":1}]}
    4. data: [DONE]
    """
    # Get conversation history
    conversation = get_or_create_conversation(session_id)
    
    # Add user message to conversation
    user_message = {"role": "user", "content": req.message}
    conversation.append(user_message)
    
    # Use RAG to augment messages with relevant context
    rag_engine = RAGEngine()
    augmented_messages = rag_engine.augment_messages(conversation.copy())
    
    # Get OpenAI client and stream response
    openai = get_openai()
    
    def generate_response():
        assistant_response = ""
        try:
            for chunk in openai.chat.completions.create(
                stream=True,
                model=settings.azure_openai_deployment,
                temperature=settings.openai_model_temperature,
                messages=augmented_messages
            ):
                # Check if chunk has choices and the first choice has content
                if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        content = delta.content
                        assistant_response += content
                        yield f"data: {content}\n\n"
            
            # Send source metadata as a special message
            sources = rag_engine.get_last_sources()
            if sources:
                metadata = StreamingChatMetadata(sources=sources)
                yield f"data: [SOURCES]{metadata.model_dump_json()}\n\n"
            
            # Add assistant response to conversation history
            conversation.append({"role": "assistant", "content": assistant_response})
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate_response(), media_type="text/event-stream")

@router.post("/message-sync", response_model=ChatResponse)
async def send_message_sync(req: SimpleChatRequest, session_id: str = "default"):
    """
    Send a message to the chatbot with a synchronous, structured response.
    Includes source references in the response metadata.
    """
    
    # Get conversation history
    conversation = get_or_create_conversation(session_id)
    
    # Add user message to conversation
    user_message = {"role": "user", "content": req.message}
    conversation.append(user_message)
    
    # Use RAG to augment messages with relevant context
    rag_engine = RAGEngine()
    augmented_messages = rag_engine.augment_messages(conversation.copy())
    
    # Get OpenAI client and generate response
    openai = get_openai()
    
    try:
        completion = openai.chat.completions.create(
            model=settings.azure_openai_deployment,
            temperature=settings.openai_model_temperature,
            messages=augmented_messages
        )
        
        assistant_response = completion.choices[0].message.content
        
        # Add assistant response to conversation history
        conversation.append({"role": "assistant", "content": assistant_response})
        
        # Get sources used
        sources = rag_engine.get_last_sources()
        
        return ChatResponse(response=assistant_response, sources=sources)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@router.get("/history")
async def get_conversation_history(session_id: str = "default"):
    """Get the current conversation history for a session"""
    conversation = get_or_create_conversation(session_id)
    return {"messages": conversation}

@router.delete("/history")
async def clear_conversation_history(session_id: str = "default"):
    """Clear the conversation history for a session"""
    if session_id in conversations:
        del conversations[session_id]
    return {"message": "Conversation history cleared"}
