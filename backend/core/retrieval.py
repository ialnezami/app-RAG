"""
Vector search and retrieval functionality.
"""
import uuid
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.orm import selectinload
# Using manual similarity calculation instead of pgvector functions

from .database import get_db
from .models import DocumentChunk, Document, Profile
from .db_utils import DocumentChunkRepository
from .embeddings import get_embedding_generator, cosine_similarity
from config.settings import get_settings

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Search result with relevance score."""
    chunk: DocumentChunk
    similarity_score: float
    rank: int
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SearchResponse:
    """Response from vector search."""
    results: List[SearchResult]
    total_results: int
    query_embedding: Optional[List[float]] = None
    search_time: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class VectorRetriever:
    """Handles vector similarity search and retrieval."""
    
    def __init__(self):
        self.settings = get_settings()
        self.embedding_generator = get_embedding_generator()
    
    async def search_similar_chunks(
        self,
        session: AsyncSession,
        query: str,
        profile_id: int,
        limit: int = 10,
        similarity_threshold: float = 0.7,
        include_metadata: bool = True
    ) -> SearchResponse:
        """
        Search for similar chunks using vector similarity.
        
        Args:
            session: Database session
            query: Search query text
            profile_id: Profile ID to search within
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            include_metadata: Whether to include document metadata
            
        Returns:
            SearchResponse with results and metadata
        """
        import time
        start_time = time.time()
        
        logger.info(f"Searching for similar chunks: '{query[:50]}...' (profile: {profile_id})")
        
        # Generate query embedding
        query_embedding = await self.embedding_generator.generate_single_embedding(query)
        if not query_embedding:
            logger.error("Failed to generate query embedding")
            return SearchResponse(
                results=[],
                total_results=0,
                query_embedding=None,
                search_time=time.time() - start_time,
                metadata={"error": "Failed to generate query embedding"}
            )
        
        # Perform vector search
        results = await self._perform_vector_search(
            session=session,
            query_embedding=query_embedding,
            profile_id=profile_id,
            limit=limit,
            similarity_threshold=similarity_threshold,
            include_metadata=include_metadata
        )
        
        search_time = time.time() - start_time
        logger.info(f"Found {len(results)} results in {search_time:.3f}s")
        
        return SearchResponse(
            results=results,
            total_results=len(results),
            query_embedding=query_embedding,
            search_time=search_time,
            metadata={
                "profile_id": profile_id,
                "similarity_threshold": similarity_threshold,
                "limit": limit
            }
        )
    
    async def _perform_vector_search(
        self,
        session: AsyncSession,
        query_embedding: List[float],
        profile_id: int,
        limit: int,
        similarity_threshold: float,
        include_metadata: bool
    ) -> List[SearchResult]:
        """Perform the actual vector search."""
        # Build query with optional metadata loading
        query_options = [selectinload(DocumentChunk.document)]
        if include_metadata:
            query_options.append(selectinload(DocumentChunk.profile))
        
        # Execute vector similarity search
        query = (
            select(DocumentChunk)
            .options(*query_options)
            .where(
                and_(
                    DocumentChunk.profile_id == profile_id,
                    DocumentChunk.embedding.is_not(None)
                )
            )
            .order_by(cosine_distance(DocumentChunk.embedding, query_embedding))
            .limit(limit * 2)  # Get more results for filtering
        )
        
        result = await session.execute(query)
        chunks = result.scalars().all()
        
        # Calculate similarity scores and filter
        search_results = []
        for i, chunk in enumerate(chunks):
            if chunk.embedding:
                similarity = 1 - cosine_distance(chunk.embedding, query_embedding)
                
                if similarity >= similarity_threshold:
                    metadata = {}
                    if include_metadata:
                        metadata = {
                            "document_filename": chunk.document.filename if chunk.document else None,
                            "document_id": str(chunk.document.id) if chunk.document else None,
                            "chunk_index": chunk.chunk_index,
                            "profile_name": chunk.profile.name if chunk.profile else None
                        }
                    
                    search_results.append(SearchResult(
                        chunk=chunk,
                        similarity_score=float(similarity),
                        rank=len(search_results) + 1,
                        metadata=metadata
                    ))
        
        # Limit results
        return search_results[:limit]
    
    async def get_context_chunks(
        self,
        session: AsyncSession,
        query: str,
        profile_id: int,
        max_chunks: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Get context chunks for RAG response generation.
        
        Args:
            session: Database session
            query: User query
            profile_id: Profile ID
            max_chunks: Maximum number of context chunks
            similarity_threshold: Minimum similarity threshold
            
        Returns:
            List of context chunk dictionaries
        """
        search_response = await self.search_similar_chunks(
            session=session,
            query=query,
            profile_id=profile_id,
            limit=max_chunks,
            similarity_threshold=similarity_threshold,
            include_metadata=True
        )
        
        context_chunks = []
        for result in search_response.results:
            context_chunks.append({
                "id": str(result.chunk.id),
                "content": result.chunk.content,
                "similarity": result.similarity_score,
                "document_filename": result.metadata.get("document_filename"),
                "document_id": result.metadata.get("document_id"),
                "chunk_index": result.chunk.chunk_index,
                "metadata": result.chunk.metadata
            })
        
        return context_chunks
    
    async def search_by_document(
        self,
        session: AsyncSession,
        document_id: uuid.UUID,
        query: str,
        limit: int = 10
    ) -> List[SearchResult]:
        """
        Search within a specific document.
        
        Args:
            session: Database session
            document_id: Document UUID
            query: Search query
            limit: Maximum results
            
        Returns:
            List of SearchResult objects
        """
        # Generate query embedding
        query_embedding = await self.embedding_generator.generate_single_embedding(query)
        if not query_embedding:
            return []
        
        # Search within document
        query_sql = (
            select(DocumentChunk)
            .options(selectinload(DocumentChunk.document))
            .where(
                and_(
                    DocumentChunk.document_id == document_id,
                    DocumentChunk.embedding.is_not(None)
                )
            )
            .order_by(cosine_distance(DocumentChunk.embedding, query_embedding))
            .limit(limit)
        )
        
        result = await session.execute(query_sql)
        chunks = result.scalars().all()
        
        # Calculate similarity scores
        search_results = []
        for i, chunk in enumerate(chunks):
            if chunk.embedding:
                similarity = 1 - cosine_distance(chunk.embedding, query_embedding)
                search_results.append(SearchResult(
                    chunk=chunk,
                    similarity_score=float(similarity),
                    rank=i + 1,
                    metadata={
                        "document_filename": chunk.document.filename if chunk.document else None,
                        "chunk_index": chunk.chunk_index
                    }
                ))
        
        return search_results
    
    async def get_related_chunks(
        self,
        session: AsyncSession,
        chunk_id: uuid.UUID,
        limit: int = 5
    ) -> List[SearchResult]:
        """
        Find chunks related to a specific chunk.
        
        Args:
            session: Database session
            chunk_id: Source chunk UUID
            limit: Maximum results
            
        Returns:
            List of related SearchResult objects
        """
        # Get the source chunk
        chunk_query = (
            select(DocumentChunk)
            .options(selectinload(DocumentChunk.document))
            .where(DocumentChunk.id == chunk_id)
        )
        
        result = await session.execute(chunk_query)
        source_chunk = result.scalar_one_or_none()
        
        if not source_chunk or not source_chunk.embedding:
            return []
        
        # Find similar chunks (excluding the source)
        similar_query = (
            select(DocumentChunk)
            .options(selectinload(DocumentChunk.document))
            .where(
                and_(
                    DocumentChunk.id != chunk_id,
                    DocumentChunk.profile_id == source_chunk.profile_id,
                    DocumentChunk.embedding.is_not(None)
                )
            )
            .order_by(cosine_distance(DocumentChunk.embedding, source_chunk.embedding))
            .limit(limit)
        )
        
        result = await session.execute(similar_query)
        chunks = result.scalars().all()
        
        # Calculate similarity scores
        search_results = []
        for i, chunk in enumerate(chunks):
            if chunk.embedding:
                similarity = 1 - cosine_distance(chunk.embedding, source_chunk.embedding)
                search_results.append(SearchResult(
                    chunk=chunk,
                    similarity_score=float(similarity),
                    rank=i + 1,
                    metadata={
                        "document_filename": chunk.document.filename if chunk.document else None,
                        "chunk_index": chunk.chunk_index
                    }
                ))
        
        return search_results
    
    async def get_profile_statistics(
        self,
        session: AsyncSession,
        profile_id: int
    ) -> Dict[str, Any]:
        """
        Get statistics for a profile's vector data.
        
        Args:
            session: Database session
            profile_id: Profile ID
            
        Returns:
            Dictionary with statistics
        """
        # Count total chunks
        total_chunks_query = (
            select(func.count(DocumentChunk.id))
            .where(DocumentChunk.profile_id == profile_id)
        )
        result = await session.execute(total_chunks_query)
        total_chunks = result.scalar()
        
        # Count chunks with embeddings
        embedded_chunks_query = (
            select(func.count(DocumentChunk.id))
            .where(
                and_(
                    DocumentChunk.profile_id == profile_id,
                    DocumentChunk.embedding.is_not(None)
                )
            )
        )
        result = await session.execute(embedded_chunks_query)
        embedded_chunks = result.scalar()
        
        # Count documents
        documents_query = (
            select(func.count(Document.id))
            .where(Document.profile_id == profile_id)
        )
        result = await session.execute(documents_query)
        total_documents = result.scalar()
        
        # Count processed documents
        processed_docs_query = (
            select(func.count(Document.id))
            .where(
                and_(
                    Document.profile_id == profile_id,
                    Document.processed == True
                )
            )
        )
        result = await session.execute(processed_docs_query)
        processed_documents = result.scalar()
        
        return {
            "total_chunks": total_chunks,
            "embedded_chunks": embedded_chunks,
            "total_documents": total_documents,
            "processed_documents": processed_documents,
            "embedding_coverage": embedded_chunks / total_chunks if total_chunks > 0 else 0,
            "processing_coverage": processed_documents / total_documents if total_documents > 0 else 0
        }


class HybridRetriever:
    """Hybrid retrieval combining vector search with keyword search."""
    
    def __init__(self):
        self.vector_retriever = VectorRetriever()
    
    async def hybrid_search(
        self,
        session: AsyncSession,
        query: str,
        profile_id: int,
        limit: int = 10,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> SearchResponse:
        """
        Perform hybrid search combining vector and keyword search.
        
        Args:
            session: Database session
            query: Search query
            profile_id: Profile ID
            limit: Maximum results
            vector_weight: Weight for vector similarity
            keyword_weight: Weight for keyword matching
            
        Returns:
            SearchResponse with hybrid results
        """
        import time
        start_time = time.time()
        
        # Perform vector search
        vector_results = await self.vector_retriever.search_similar_chunks(
            session=session,
            query=query,
            profile_id=profile_id,
            limit=limit * 2,
            similarity_threshold=0.5,
            include_metadata=True
        )
        
        # Perform keyword search
        keyword_results = await self._keyword_search(
            session=session,
            query=query,
            profile_id=profile_id,
            limit=limit * 2
        )
        
        # Combine and rerank results
        combined_results = self._combine_results(
            vector_results.results,
            keyword_results,
            vector_weight,
            keyword_weight
        )
        
        # Sort by combined score and limit
        combined_results.sort(key=lambda x: x.similarity_score, reverse=True)
        final_results = combined_results[:limit]
        
        search_time = time.time() - start_time
        
        return SearchResponse(
            results=final_results,
            total_results=len(final_results),
            search_time=search_time,
            metadata={
                "search_type": "hybrid",
                "vector_weight": vector_weight,
                "keyword_weight": keyword_weight,
                "vector_results": len(vector_results.results),
                "keyword_results": len(keyword_results)
            }
        )
    
    async def _keyword_search(
        self,
        session: AsyncSession,
        query: str,
        profile_id: int,
        limit: int
    ) -> List[SearchResult]:
        """Perform keyword search using full-text search."""
        # Simple keyword search using ILIKE
        keywords = query.lower().split()
        
        conditions = []
        for keyword in keywords:
            conditions.append(DocumentChunk.content.ilike(f'%{keyword}%'))
        
        query_sql = (
            select(DocumentChunk)
            .options(
                selectinload(DocumentChunk.document),
                selectinload(DocumentChunk.profile)
            )
            .where(
                and_(
                    DocumentChunk.profile_id == profile_id,
                    or_(*conditions)
                )
            )
            .limit(limit)
        )
        
        result = await session.execute(query_sql)
        chunks = result.scalars().all()
        
        # Calculate keyword relevance scores
        search_results = []
        for chunk in chunks:
            score = self._calculate_keyword_score(chunk.content, keywords)
            search_results.append(SearchResult(
                chunk=chunk,
                similarity_score=score,
                rank=0,  # Will be set after combining
                metadata={
                    "document_filename": chunk.document.filename if chunk.document else None,
                    "chunk_index": chunk.chunk_index,
                    "search_type": "keyword"
                }
            ))
        
        return search_results
    
    def _calculate_keyword_score(self, content: str, keywords: List[str]) -> float:
        """Calculate keyword relevance score."""
        content_lower = content.lower()
        total_score = 0
        
        for keyword in keywords:
            # Count occurrences
            count = content_lower.count(keyword)
            # Weight by keyword length (longer keywords are more specific)
            weight = len(keyword) / 10
            total_score += count * weight
        
        # Normalize by content length
        return min(total_score / len(content) * 1000, 1.0)
    
    def _combine_results(
        self,
        vector_results: List[SearchResult],
        keyword_results: List[SearchResult],
        vector_weight: float,
        keyword_weight: float
    ) -> List[SearchResult]:
        """Combine vector and keyword search results."""
        # Create a map of chunk ID to results
        combined_map = {}
        
        # Add vector results
        for result in vector_results:
            chunk_id = result.chunk.id
            combined_map[chunk_id] = result
            result.metadata["vector_score"] = result.similarity_score
        
        # Add keyword results
        for result in keyword_results:
            chunk_id = result.chunk.id
            if chunk_id in combined_map:
                # Combine scores
                existing = combined_map[chunk_id]
                combined_score = (
                    existing.similarity_score * vector_weight +
                    result.similarity_score * keyword_weight
                )
                existing.similarity_score = combined_score
                existing.metadata["keyword_score"] = result.similarity_score
            else:
                result.similarity_score *= keyword_weight
                result.metadata["keyword_score"] = result.similarity_score
                combined_map[chunk_id] = result
        
        return list(combined_map.values())


# Global instances
_vector_retriever: Optional[VectorRetriever] = None
_hybrid_retriever: Optional[HybridRetriever] = None


def get_vector_retriever() -> VectorRetriever:
    """Get global vector retriever instance."""
    global _vector_retriever
    if _vector_retriever is None:
        _vector_retriever = VectorRetriever()
    return _vector_retriever


def get_hybrid_retriever() -> HybridRetriever:
    """Get global hybrid retriever instance."""
    global _hybrid_retriever
    if _hybrid_retriever is None:
        _hybrid_retriever = HybridRetriever()
    return _hybrid_retriever
