"""
Database utility functions for common operations.
"""
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
# Vector similarity functions will be calculated manually

from .models import Profile, Document, DocumentChunk, ChatSession, ChatMessage


class ProfileRepository:
    """Repository for Profile operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        name: str,
        description: Optional[str],
        prompt: str,
        provider: str,
        model: str,
        settings: Dict[str, Any]
    ) -> Profile:
        """Create a new profile."""
        profile = Profile(
            name=name,
            description=description,
            prompt=prompt,
            provider=provider,
            model=model,
            settings=settings
        )
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile
    
    async def get_by_id(self, profile_id: int) -> Optional[Profile]:
        """Get profile by ID."""
        result = await self.session.execute(
            select(Profile).where(Profile.id == profile_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[Profile]:
        """Get all profiles."""
        result = await self.session.execute(select(Profile))
        return result.scalars().all()
    
    async def update(
        self,
        profile_id: int,
        **updates
    ) -> Optional[Profile]:
        """Update profile."""
        await self.session.execute(
            update(Profile)
            .where(Profile.id == profile_id)
            .values(**updates)
        )
        await self.session.commit()
        return await self.get_by_id(profile_id)
    
    async def delete(self, profile_id: int) -> bool:
        """Delete profile."""
        result = await self.session.execute(
            delete(Profile).where(Profile.id == profile_id)
        )
        await self.session.commit()
        return result.rowcount > 0


class DocumentRepository:
    """Repository for Document operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        filename: str,
        original_filename: str,
        profile_id: int,
        file_path: Optional[str] = None,
        file_size: Optional[int] = None,
        mime_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Document:
        """Create a new document."""
        document = Document(
            filename=filename,
            original_filename=original_filename,
            profile_id=profile_id,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            metadata=metadata or {}
        )
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        return document
    
    async def get_by_id(self, document_id: uuid.UUID) -> Optional[Document]:
        """Get document by ID."""
        result = await self.session.execute(
            select(Document)
            .options(selectinload(Document.profile))
            .where(Document.id == document_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_profile(
        self,
        profile_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Document]:
        """Get documents by profile."""
        result = await self.session.execute(
            select(Document)
            .where(Document.profile_id == profile_id)
            .order_by(Document.upload_date.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def mark_processed(self, document_id: uuid.UUID) -> bool:
        """Mark document as processed."""
        await self.session.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(processed=True)
        )
        await self.session.commit()
        return True
    
    async def delete(self, document_id: uuid.UUID) -> bool:
        """Delete document."""
        result = await self.session.execute(
            delete(Document).where(Document.id == document_id)
        )
        await self.session.commit()
        return result.rowcount > 0


class DocumentChunkRepository:
    """Repository for DocumentChunk operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        document_id: uuid.UUID,
        profile_id: int,
        chunk_index: int,
        content: str,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DocumentChunk:
        """Create a new document chunk."""
        chunk = DocumentChunk(
            document_id=document_id,
            profile_id=profile_id,
            chunk_index=chunk_index,
            content=content,
            embedding=embedding,
            metadata=metadata or {}
        )
        self.session.add(chunk)
        await self.session.commit()
        await self.session.refresh(chunk)
        return chunk
    
    async def search_similar(
        self,
        profile_id: int,
        query_embedding: List[float],
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[DocumentChunk]:
        """Search for similar chunks using vector similarity."""
        result = await self.session.execute(
            select(DocumentChunk)
            .options(
                selectinload(DocumentChunk.document),
                selectinload(DocumentChunk.profile)
            )
            .where(
                and_(
                    DocumentChunk.profile_id == profile_id,
                    DocumentChunk.embedding.is_not(None)
                )
            )
            .order_by(
                DocumentChunk.embedding.cosine_distance(query_embedding)
            )
            .limit(limit)
        )
        chunks = result.scalars().all()
        
        # Filter by similarity threshold
        filtered_chunks = []
        for chunk in chunks:
            if chunk.embedding:
                # Calculate cosine similarity manually
                import numpy as np
                embedding_array = np.array(chunk.embedding)
                query_array = np.array(query_embedding)
                similarity = float(np.dot(embedding_array, query_array) / (np.linalg.norm(embedding_array) * np.linalg.norm(query_array)))
                if similarity >= similarity_threshold:
                    chunk.metadata = chunk.metadata or {}
                    chunk.metadata["similarity"] = float(similarity)
                    filtered_chunks.append(chunk)
        
        return filtered_chunks
    
    async def get_by_document(
        self,
        document_id: uuid.UUID
    ) -> List[DocumentChunk]:
        """Get all chunks for a document."""
        result = await self.session.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
        )
        return result.scalars().all()


class ChatSessionRepository:
    """Repository for ChatSession operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        profile_id: int,
        session_name: Optional[str] = None
    ) -> ChatSession:
        """Create a new chat session."""
        session = ChatSession(
            profile_id=profile_id,
            session_name=session_name
        )
        self.session.add(session)
        await self.session.commit()
        await self.session.refresh(session)
        return session
    
    async def get_by_id(self, session_id: uuid.UUID) -> Optional[ChatSession]:
        """Get chat session by ID."""
        result = await self.session.execute(
            select(ChatSession)
            .options(
                selectinload(ChatSession.profile),
                selectinload(ChatSession.messages)
            )
            .where(ChatSession.id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_profile(
        self,
        profile_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[ChatSession]:
        """Get chat sessions by profile."""
        result = await self.session.execute(
            select(ChatSession)
            .where(ChatSession.profile_id == profile_id)
            .order_by(ChatSession.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def delete(self, session_id: uuid.UUID) -> bool:
        """Delete chat session."""
        result = await self.session.execute(
            delete(ChatSession).where(ChatSession.id == session_id)
        )
        await self.session.commit()
        return result.rowcount > 0


class ChatMessageRepository:
    """Repository for ChatMessage operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        session_id: uuid.UUID,
        role: str,
        content: str,
        context_chunks: Optional[List[Dict[str, Any]]] = None
    ) -> ChatMessage:
        """Create a new chat message."""
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            context_chunks=context_chunks or []
        )
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message
    
    async def get_by_session(
        self,
        session_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0
    ) -> List[ChatMessage]:
        """Get messages for a session."""
        result = await self.session.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.timestamp.asc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
