from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, create_engine, Enum
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker
from datetime import datetime
import os
import enum

class Base(DeclarativeBase):
    pass

class SourceType(enum.Enum):
    DOCUMENT = "document"
    WEB = "web"

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
    
    # Source type to distinguish between document and web sources
    source_type = Column(Enum(SourceType), nullable=False, default=SourceType.DOCUMENT)
    
    # Common fields for both source types
    document_id = Column(String, nullable=False)  # For web: use URL as ID, for docs: document ID
    filename = Column(String, nullable=False)     # For web: use title, for docs: filename
    relevance_score = Column(Float, nullable=False)
    
    # Document-specific fields (nullable for web sources)
    page = Column(Integer, nullable=True)           # Only for document sources
    
    # Web-specific fields (nullable for document sources)
    url = Column(String, nullable=True)                                                     # Full URL for web sources
    domain = Column(String, nullable=True)                                                  # Domain extracted from URL
    description = Column(Text, nullable=True)                                               # Description/snippet from web result
    published_date = Column(String, nullable=True)                                          # Publication date from web source
    
    # Relationship to message
    message = relationship("ChatMessage", back_populates="sources")
    
    def to_source_reference(self):
        """Convert database record to SourceReference object"""
        from src.models.chat import SourceReference
        
        return SourceReference(
            document_id=self.document_id,
            filename=self.filename,
            page=self.page or 0,
            relevance_score=self.relevance_score,
            url=self.url,
            source_type=self.source_type.value,
            domain=self.domain,
            description=self.description,
            published_date=self.published_date
        )
    
    @classmethod
    def from_source_reference(cls, source_ref, message_id: int):
        """Create MessageSource from SourceReference object"""
        # Determine source type
        source_type = SourceType.WEB if source_ref.document_id.startswith("web_") else SourceType.DOCUMENT
        
        return cls(
            message_id=message_id,
            source_type=source_type,
            document_id=source_ref.document_id,
            filename=source_ref.filename,
            relevance_score=source_ref.relevance_score,
            page=source_ref.page if source_type == SourceType.DOCUMENT else None,
            url=getattr(source_ref, 'url', None),
            domain=getattr(source_ref, 'domain', None),
            description=getattr(source_ref, 'description', None),
            published_date=getattr(source_ref, 'published_date', None)
        )

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

