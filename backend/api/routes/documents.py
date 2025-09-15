"""
Document management endpoints.
"""
import uuid
import os
import aiofiles
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from core.database import get_db
from core.db_utils import DocumentRepository, DocumentChunkRepository
from core.chunking import get_document_processor
from core.embeddings import get_embedding_generator
from config.settings import get_settings

router = APIRouter()


# Pydantic models
class DocumentResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    file_size: Optional[int]
    mime_type: Optional[str]
    upload_date: str
    processed: bool
    profile_id: int
    metadata: dict

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
    page: int
    limit: int


class DocumentProcessRequest(BaseModel):
    document_id: str
    profile_id: int


class DocumentProcessResponse(BaseModel):
    document_id: str
    status: str
    chunks_created: int
    message: str


class SearchRequest(BaseModel):
    query: str
    profile_id: int
    limit: int = Field(default=10, ge=1, le=50)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    id: str
    content: str
    similarity: float
    document_filename: str
    document_id: str
    chunk_index: int
    metadata: dict


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_results: int
    query: str
    search_time: float


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    profile_id: Optional[int] = None,
    page: int = 1,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List documents with optional profile filtering and pagination."""
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 50
    
    document_repo = DocumentRepository(db)
    
    if profile_id:
        documents = await document_repo.get_by_profile(profile_id, limit, (page - 1) * limit)
    else:
        # Get all documents (you might want to implement this in the repository)
        documents = await document_repo.get_by_profile(1, limit * 10, 0)  # Temporary
    
    return DocumentListResponse(
        documents=[
            DocumentResponse(
                id=str(doc.id),
                filename=doc.filename,
                original_filename=doc.original_filename,
                file_size=doc.file_size,
                mime_type=doc.mime_type,
                upload_date=doc.upload_date.isoformat(),
                processed=doc.processed,
                profile_id=doc.profile_id,
                metadata=doc.metadata
            )
            for doc in documents
        ],
        total=len(documents),
        page=page,
        limit=limit
    )


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific document by ID."""
    try:
        doc_uuid = uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID format"
        )
    
    document_repo = DocumentRepository(db)
    document = await document_repo.get_by_id(doc_uuid)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    return DocumentResponse(
        id=str(document.id),
        filename=document.filename,
        original_filename=document.original_filename,
        file_size=document.file_size,
        mime_type=document.mime_type,
        upload_date=document.upload_date.isoformat(),
        processed=document.processed,
        profile_id=document.profile_id,
        metadata=document.metadata
    )


@router.post("/documents/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    profile_id: int = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload a new document."""
    settings = get_settings()
    
    # Validate file size
    if file.size and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.max_file_size} bytes"
        )
    
    # Validate file type
    file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    if file_extension not in settings.allowed_file_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{file_extension}' is not allowed. Allowed types: {settings.allowed_file_types}"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = settings.upload_dir
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_id = uuid.uuid4()
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'txt'
    filename = f"{file_id}.{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    try:
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Create document record
        document_repo = DocumentRepository(db)
        document = await document_repo.create(
            filename=filename,
            original_filename=file.filename,
            profile_id=profile_id,
            file_path=file_path,
            file_size=len(content),
            mime_type=file.content_type,
            metadata={"upload_source": "api"}
        )
        
        # Schedule background processing
        background_tasks.add_task(
            process_document_background,
            str(document.id),
            file_path,
            file.content_type,
            profile_id
        )
        
        return DocumentResponse(
            id=str(document.id),
            filename=document.filename,
            original_filename=document.original_filename,
            file_size=document.file_size,
            mime_type=document.mime_type,
            upload_date=document.upload_date.isoformat(),
            processed=document.processed,
            profile_id=document.profile_id,
            metadata=document.metadata
        )
        
    except Exception as e:
        # Clean up file if document creation failed
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )


@router.post("/documents/process", response_model=DocumentProcessResponse)
async def process_document(
    request: DocumentProcessRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Manually trigger document processing."""
    try:
        doc_uuid = uuid.UUID(request.document_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID format"
        )
    
    document_repo = DocumentRepository(db)
    document = await document_repo.get_by_id(doc_uuid)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {request.document_id} not found"
        )
    
    if document.processed:
        return DocumentProcessResponse(
            document_id=request.document_id,
            status="already_processed",
            chunks_created=0,
            message="Document is already processed"
        )
    
    # Schedule background processing
    background_tasks.add_task(
        process_document_background,
        request.document_id,
        document.file_path,
        document.mime_type,
        request.profile_id
    )
    
    return DocumentProcessResponse(
        document_id=request.document_id,
        status="processing",
        chunks_created=0,
        message="Document processing started"
    )


async def process_document_background(
    document_id: str,
    file_path: str,
    mime_type: str,
    profile_id: int
):
    """Background task to process a document."""
    from core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            # Process document
            processor = get_document_processor()
            text, doc_metadata, chunks = processor.process_document(
                file_path=file_path,
                mime_type=mime_type,
                metadata={"profile_id": profile_id}
            )
            
            # Generate embeddings for chunks
            embedding_generator = get_embedding_generator()
            chunk_texts = [chunk.content for chunk in chunks]
            
            embedding_result = await embedding_generator.generate_embeddings(chunk_texts)
            
            # Save chunks to database
            chunk_repo = DocumentChunkRepository(db)
            chunks_created = 0
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embedding_result.embeddings)):
                await chunk_repo.create(
                    document_id=uuid.UUID(document_id),
                    profile_id=profile_id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    embedding=embedding,
                    metadata=chunk.metadata
                )
                chunks_created += 1
            
            # Mark document as processed
            document_repo = DocumentRepository(db)
            await document_repo.mark_processed(uuid.UUID(document_id))
            
            print(f"✅ Processed document {document_id}: {chunks_created} chunks created")
            
        except Exception as e:
            print(f"❌ Failed to process document {document_id}: {e}")


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a document and its chunks."""
    try:
        doc_uuid = uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID format"
        )
    
    document_repo = DocumentRepository(db)
    document = await document_repo.get_by_id(doc_uuid)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    try:
        # Delete file from filesystem
        if document.file_path and os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete document (chunks will be deleted by cascade)
        success = await document_repo.delete(doc_uuid)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete document"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """Search documents using vector similarity."""
    from core.retrieval import get_vector_retriever
    
    vector_retriever = get_vector_retriever()
    
    search_response = await vector_retriever.search_similar_chunks(
        session=db,
        query=request.query,
        profile_id=request.profile_id,
        limit=request.limit,
        similarity_threshold=request.similarity_threshold,
        include_metadata=True
    )
    
    results = [
        SearchResult(
            id=str(result.chunk.id),
            content=result.chunk.content,
            similarity=result.similarity_score,
            document_filename=result.metadata.get("document_filename", ""),
            document_id=result.metadata.get("document_id", ""),
            chunk_index=result.chunk.chunk_index,
            metadata=result.chunk.metadata
        )
        for result in search_response.results
    ]
    
    return SearchResponse(
        results=results,
        total_results=search_response.total_results,
        query=request.query,
        search_time=search_response.search_time
    )


@router.post("/search/similar", response_model=SearchResponse)
async def search_similar_chunks(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """Find similar chunks to a given text."""
    from core.retrieval import get_vector_retriever
    
    vector_retriever = get_vector_retriever()
    
    search_response = await vector_retriever.search_similar_chunks(
        session=db,
        query=request.query,
        profile_id=request.profile_id,
        limit=request.limit,
        similarity_threshold=request.similarity_threshold,
        include_metadata=True
    )
    
    results = [
        SearchResult(
            id=str(result.chunk.id),
            content=result.chunk.content,
            similarity=result.similarity_score,
            document_filename=result.metadata.get("document_filename", ""),
            document_id=result.metadata.get("document_id", ""),
            chunk_index=result.chunk.chunk_index,
            metadata=result.chunk.metadata
        )
        for result in search_response.results
    ]
    
    return SearchResponse(
        results=results,
        total_results=search_response.total_results,
        query=request.query,
        search_time=search_response.search_time
    )


@router.get("/documents/{document_id}/chunks")
async def get_document_chunks(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all chunks for a specific document."""
    try:
        doc_uuid = uuid.UUID(document_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID format"
        )
    
    chunk_repo = DocumentChunkRepository(db)
    chunks = await chunk_repo.get_by_document(doc_uuid)
    
    return {
        "document_id": document_id,
        "chunks": [
            {
                "id": str(chunk.id),
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "has_embedding": chunk.embedding is not None,
                "metadata": chunk.metadata,
                "created_at": chunk.created_at.isoformat()
            }
            for chunk in chunks
        ],
        "total_chunks": len(chunks)
    }
