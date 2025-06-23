from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker
from datetime import datetime
import os

class Base(DeclarativeBase):
    pass

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to messages
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # user or assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to session
    session = relationship("ChatSession", back_populates="messages")
    
    # Relationship to sources
    sources = relationship("MessageSource", back_populates="message", cascade="all, delete-orphan")

class MessageSource(Base):
    __tablename__ = "message_sources"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("chat_messages.id"), nullable=False)
    document_id = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    page = Column(Integer, nullable=False)
    relevance_score = Column(Float, nullable=False)
    
    # Relationship to message
    message = relationship("ChatMessage", back_populates="sources")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/database/chat_history.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 