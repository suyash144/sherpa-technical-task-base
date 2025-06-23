from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Iterator, Dict, List
import json
from sqlalchemy.orm import Session
from src.models.chat import SimpleChatRequest, Message, StreamingChatMetadata, ChatResponse, ChatSessionCreate, ChatSessionsResponse, ChatHistoryResponse
from src.models.database import get_db
from src.services.chat_service import ChatService
from src.services.openai_client import get_openai
from src.services.rag import RAGEngine
from src.settings import settings

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/sessions")
async def create_session(req: ChatSessionCreate, db: Session = Depends(get_db)):
    """Create a new chat session"""
    try:
        session = ChatService.create_session(db, req.title)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")

@router.get("/sessions", response_model=ChatSessionsResponse)
async def get_sessions(db: Session = Depends(get_db)):
    """Get all chat sessions"""
    try:
        return ChatService.get_all_sessions(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sessions: {str(e)}")

@router.get("/sessions/{session_id}/history", response_model=ChatHistoryResponse)
async def get_session_history(session_id: str, db: Session = Depends(get_db)):
    """Get chat history for a specific session"""
    try:
        return ChatService.get_session_history(db, session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching session history: {str(e)}")

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Delete a chat session"""
    try:
        success = ChatService.delete_session(db, session_id)
        if success:
            return {"message": "Session deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")

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
async def send_message(req: SimpleChatRequest, session_id: str = "default", db: Session = Depends(get_db)):
    """
    Send a message to the chatbot. The backend manages conversation history with persistent storage.
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
    
    # Ensure session exists
    ChatService.get_or_create_session(db, session_id)
    
    # Add user message to database
    ChatService.add_message(db, session_id, "user", req.message)
    
    # Get conversation history from database
    history = ChatService.get_session_history(db, session_id)
    conversation = [{"role": msg.role, "content": msg.content} for msg in history.messages]
    
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
            
            # Add assistant response to database with sources
            ChatService.add_message(db, session_id, "assistant", assistant_response, sources)
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate_response(), media_type="text/event-stream")

@router.post("/message-sync", response_model=ChatResponse)
async def send_message_sync(req: SimpleChatRequest, session_id: str = "default", db: Session = Depends(get_db)):
    """
    Send a message to the chatbot with a synchronous, structured response.
    Includes source references in the response metadata.
    """
    
    # Ensure session exists
    ChatService.get_or_create_session(db, session_id)
    
    # Add user message to database
    ChatService.add_message(db, session_id, "user", req.message)
    
    # Get conversation history from database
    history = ChatService.get_session_history(db, session_id)
    conversation = [{"role": msg.role, "content": msg.content} for msg in history.messages]
    
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
        
        # Get sources used
        sources = rag_engine.get_last_sources()
        
        # Add assistant response to database with sources
        ChatService.add_message(db, session_id, "assistant", assistant_response, sources)
        
        return ChatResponse(response=assistant_response, sources=sources)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

# Legacy endpoints for backward compatibility
@router.get("/history")
async def get_conversation_history(session_id: str = "default", db: Session = Depends(get_db)):
    """Get the current conversation history for a session (legacy endpoint)"""
    try:
        history = ChatService.get_session_history(db, session_id)
        # Convert to legacy format
        messages = [{"role": msg.role, "content": msg.content} for msg in history.messages]
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")

@router.delete("/history")
async def clear_conversation_history(session_id: str = "default", db: Session = Depends(get_db)):
    """Clear the conversation history for a session (legacy endpoint)"""
    try:
        success = ChatService.delete_session(db, session_id)
        if success:
            return {"message": "Conversation history cleared"}
        else:
            return {"message": "Session not found or already empty"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing history: {str(e)}")
