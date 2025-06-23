from typing import Literal, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class SimpleChatRequest(BaseModel):
    message: str = Field(..., example="Hello there!")

class SourceReference(BaseModel):
    document_id: str
    filename: str
    page: int
    relevance_score: float

class StreamingChatMetadata(BaseModel):
    sources: List[SourceReference]

class ChatResponse(BaseModel):
    response: str
    sources: List[SourceReference] = Field(default_factory=list)

# New models for session management
class ChatSessionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)

class ChatSessionResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    last_message: Optional[str] = None

class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    sources: List[SourceReference] = Field(default_factory=list)

class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[ChatMessageResponse]

class ChatSessionsResponse(BaseModel):
    sessions: List[ChatSessionResponse]
