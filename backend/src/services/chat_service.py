from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from src.models.database import ChatSession, ChatMessage, MessageSource
from src.models.chat import SourceReference, ChatSessionResponse, ChatMessageResponse, ChatHistoryResponse, ChatSessionsResponse
import uuid
from datetime import datetime

class ChatService:
    
    @staticmethod
    def create_session(db: Session, title: str) -> ChatSessionResponse:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        db_session = ChatSession(
            id=session_id,
            title=title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        
        return ChatSessionResponse(
            id=db_session.id,
            title=db_session.title,
            created_at=db_session.created_at,
            updated_at=db_session.updated_at
        )
    
    @staticmethod
    def get_session(db: Session, session_id: str) -> Optional[ChatSession]:
        """Get a chat session by ID"""
        return db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    @staticmethod
    def get_or_create_session(db: Session, session_id: str, title: str = None) -> ChatSession:
        """Get existing session or create a new one"""
        session = ChatService.get_session(db, session_id)
        if not session:
            if not title:
                title = f"Chat Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
            db_session = ChatSession(
                id=session_id,
                title=title,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(db_session)
            db.commit()
            db.refresh(db_session)
            return db_session
        return session
    
    @staticmethod
    def get_all_sessions(db: Session) -> ChatSessionsResponse:
        """Get all chat sessions with their last message"""
        sessions = db.query(ChatSession).order_by(desc(ChatSession.updated_at)).all()
        
        session_responses = []
        for session in sessions:
            # Get the last message
            last_message = db.query(ChatMessage).filter(
                ChatMessage.session_id == session.id
            ).order_by(desc(ChatMessage.created_at)).first()
            
            session_responses.append(ChatSessionResponse(
                id=session.id,
                title=session.title,
                created_at=session.created_at,
                updated_at=session.updated_at,
                last_message=last_message.content[:50] + "..." if last_message and len(last_message.content) > 50 else last_message.content if last_message else None
            ))
        
        return ChatSessionsResponse(sessions=session_responses)
    
    @staticmethod
    def add_message(db: Session, session_id: str, role: str, content: str, sources: List[SourceReference] = None) -> ChatMessageResponse:
        """Add a message to a chat session"""
        # Update session timestamp
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            session.updated_at = datetime.utcnow()
            
            # Update session title based on first user message
            if role == "user" and not db.query(ChatMessage).filter(ChatMessage.session_id == session_id).first():
                session.title = content[:50] + "..." if len(content) > 50 else content
        
        # Create message
        db_message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            created_at=datetime.utcnow()
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        
        # Add sources if provided
        if sources:
            for source in sources:
                db_source = MessageSource(
                    message_id=db_message.id,
                    document_id=source.document_id,
                    filename=source.filename,
                    page=source.page,
                    relevance_score=source.relevance_score
                )
                db.add(db_source)
            db.commit()
        
        # Return response with sources
        message_sources = []
        if db_message.sources:
            message_sources = [
                SourceReference(
                    document_id=source.document_id,
                    filename=source.filename,
                    page=source.page,
                    relevance_score=source.relevance_score
                ) for source in db_message.sources
            ]
        
        return ChatMessageResponse(
            id=db_message.id,
            role=db_message.role,
            content=db_message.content,
            created_at=db_message.created_at,
            sources=message_sources
        )
    
    @staticmethod
    def get_session_history(db: Session, session_id: str) -> ChatHistoryResponse:
        """Get chat history for a session"""
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at).all()
        
        message_responses = []
        for message in messages:
            sources = [
                SourceReference(
                    document_id=source.document_id,
                    filename=source.filename,
                    page=source.page,
                    relevance_score=source.relevance_score
                ) for source in message.sources
            ]
            
            message_responses.append(ChatMessageResponse(
                id=message.id,
                role=message.role,
                content=message.content,
                created_at=message.created_at,
                sources=sources
            ))
        
        return ChatHistoryResponse(
            session_id=session_id,
            messages=message_responses
        )
    
    @staticmethod
    def delete_session(db: Session, session_id: str) -> bool:
        """Delete a chat session and all its messages"""
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            db.delete(session)
            db.commit()
            return True
        return False 