"""
SQLAlchemy models for the RAG application.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, BigInteger, 
    DateTime, ForeignKey, Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from .database import Base


class Profile(Base):
    """AI provider profiles and configurations."""
    
    __tablename__ = "profiles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    settings: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    documents: Mapped[List["Document"]] = relationship(
        "Document", 
        back_populates="profile",
        cascade="all, delete-orphan"
    )
    document_chunks: Mapped[List["DocumentChunk"]] = relationship(
        "DocumentChunk",
        back_populates="profile",
        cascade="all, delete-orphan"
    )
    chat_sessions: Mapped[List["ChatSession"]] = relationship(
        "ChatSession",
        back_populates="profile",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Profile(id={self.id}, name='{self.name}', provider='{self.provider}')>"


class Document(Base):
    """Document metadata and file information."""
    
    __tablename__ = "documents"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(500))
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100))
    upload_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    profile_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    
    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="documents")
    chunks: Mapped[List["DocumentChunk"]] = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Document(id={self.id}, filename='{self.filename}', processed={self.processed})>"


class DocumentChunk(Base):
    """Text chunks with vector embeddings."""
    
    __tablename__ = "document_chunks"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    profile_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Optional[List[float]]] = mapped_column(
        Vector(1536),  # OpenAI embedding dimension
        nullable=True
    )
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="chunks")
    profile: Mapped["Profile"] = relationship("Profile", back_populates="document_chunks")
    
    # Indexes for vector similarity search
    __table_args__ = (
        Index(
            "idx_document_chunks_embedding",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
            postgresql_ops={"embedding": "vector_cosine_ops"}
        ),
        Index("idx_document_chunks_profile_document", "profile_id", "document_id"),
        Index("idx_document_chunks_profile_index", "profile_id", "chunk_index"),
    )
    
    def __repr__(self) -> str:
        return f"<DocumentChunk(id={self.id}, chunk_index={self.chunk_index}, profile_id={self.profile_id})>"


class ChatSession(Base):
    """Chat conversation sessions."""
    
    __tablename__ = "chat_sessions"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    profile_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    session_name: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="chat_sessions")
    messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.timestamp"
    )
    
    def __repr__(self) -> str:
        return f"<ChatSession(id={self.id}, profile_id={self.profile_id}, name='{self.session_name}')>"


class ChatMessage(Base):
    """Individual chat messages."""
    
    __tablename__ = "chat_messages"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    context_chunks: Mapped[List[dict]] = mapped_column(
        JSONB,
        default=list,
        nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    
    # Relationships
    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant')",
            name="ck_chat_messages_role"
        ),
        Index("idx_chat_messages_session_timestamp", "session_id", "timestamp"),
    )
    
    def __repr__(self) -> str:
        return f"<ChatMessage(id={self.id}, role='{self.role}', session_id={self.session_id})>"


# Additional indexes for performance
Index("idx_documents_profile_processed", Document.profile_id, Document.processed)
Index("idx_documents_upload_date", Document.upload_date)
Index("idx_chat_sessions_profile_updated", ChatSession.profile_id, ChatSession.updated_at)
Index("idx_chat_messages_role_timestamp", ChatMessage.role, ChatMessage.timestamp)
