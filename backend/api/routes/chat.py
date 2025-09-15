"""
Chat endpoints for RAG conversations.
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from core.database import get_db
from core.db_utils import ChatSessionRepository, ChatMessageRepository, ProfileRepository
from core.ai_providers import get_provider_manager
from core.retrieval import get_vector_retriever
from config.settings import get_settings

router = APIRouter()


# Pydantic models
class ChatMessage(BaseModel):
    id: str
    role: str
    content: str
    context_chunks: List[dict]
    timestamp: str

    class Config:
        from_attributes = True


class ChatSession(BaseModel):
    id: str
    session_name: Optional[str]
    profile_id: int
    messages: List[ChatMessage]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ChatSessionList(BaseModel):
    sessions: List[ChatSession]
    total: int
    page: int
    limit: int


class CreateSessionRequest(BaseModel):
    profile_id: int
    session_name: Optional[str] = None


class SendMessageRequest(BaseModel):
    session_id: str
    message: str
    profile_id: int
    max_context_chunks: int = Field(default=5, ge=1, le=10)


class SendMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    context_chunks: List[dict]
    timestamp: str
    usage: Optional[dict] = None


class ChatQueryRequest(BaseModel):
    query: str
    profile_id: int
    max_context_chunks: int = Field(default=5, ge=1, le=10)


class ChatQueryResponse(BaseModel):
    response: str
    context_chunks: List[dict]
    usage: Optional[dict] = None
    search_time: float = 0.0


@router.get("/chat/sessions", response_model=ChatSessionList)
async def list_chat_sessions(
    profile_id: Optional[int] = None,
    page: int = 1,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List chat sessions with optional profile filtering."""
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 50
    
    session_repo = ChatSessionRepository(db)
    
    if profile_id:
        sessions = await session_repo.get_by_profile(profile_id, limit, (page - 1) * limit)
    else:
        # Get all sessions (you might want to implement this in the repository)
        sessions = await session_repo.get_by_profile(1, limit * 10, 0)  # Temporary
    
    return ChatSessionList(
        sessions=[
            ChatSession(
                id=str(session.id),
                session_name=session.session_name,
                profile_id=session.profile_id,
                messages=[
                    ChatMessage(
                        id=str(msg.id),
                        role=msg.role,
                        content=msg.content,
                        context_chunks=msg.context_chunks,
                        timestamp=msg.timestamp.isoformat()
                    )
                    for msg in session.messages
                ],
                created_at=session.created_at.isoformat(),
                updated_at=session.updated_at.isoformat()
            )
            for session in sessions
        ],
        total=len(sessions),
        page=page,
        limit=limit
    )


@router.post("/chat/sessions", response_model=ChatSession, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    request: CreateSessionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a new chat session."""
    # Validate profile exists
    profile_repo = ProfileRepository(db)
    profile = await profile_repo.get_by_id(request.profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with ID {request.profile_id} not found"
        )
    
    session_repo = ChatSessionRepository(db)
    session = await session_repo.create(
        profile_id=request.profile_id,
        session_name=request.session_name
    )
    
    return ChatSession(
        id=str(session.id),
        session_name=session.session_name,
        profile_id=session.profile_id,
        messages=[],
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat()
    )


@router.get("/chat/sessions/{session_id}", response_model=ChatSession)
async def get_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific chat session with messages."""
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )
    
    session_repo = ChatSessionRepository(db)
    session = await session_repo.get_by_id(session_uuid)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session with ID {session_id} not found"
        )
    
    return ChatSession(
        id=str(session.id),
        session_name=session.session_name,
        profile_id=session.profile_id,
        messages=[
            ChatMessage(
                id=str(msg.id),
                role=msg.role,
                content=msg.content,
                context_chunks=msg.context_chunks,
                timestamp=msg.timestamp.isoformat()
            )
            for msg in session.messages
        ],
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat()
    )


@router.post("/chat/query", response_model=SendMessageResponse)
async def send_chat_message(
    request: SendMessageRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send a message to a chat session and get AI response."""
    try:
        session_uuid = uuid.UUID(request.session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )
    
    # Validate session exists
    session_repo = ChatSessionRepository(db)
    session = await session_repo.get_by_id(session_uuid)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session with ID {request.session_id} not found"
        )
    
    # Validate profile
    profile_repo = ProfileRepository(db)
    profile = await profile_repo.get_by_id(request.profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with ID {request.profile_id} not found"
        )
    
    # Save user message
    message_repo = ChatMessageRepository(db)
    user_message = await message_repo.create(
        session_id=session_uuid,
        role="user",
        content=request.message
    )
    
    # Get context chunks using RAG
    vector_retriever = get_vector_retriever()
    context_chunks = await vector_retriever.get_context_chunks(
        session=db,
        query=request.message,
        profile_id=request.profile_id,
        max_chunks=request.max_context_chunks,
        similarity_threshold=0.7
    )
    
    # Generate AI response
    provider_manager = get_provider_manager()
    
    # Build context for the prompt
    context_text = "\n\n".join([
        f"Document: {chunk.get('document_filename', 'Unknown')}\nContent: {chunk['content']}"
        for chunk in context_chunks
    ])
    
    # Format prompt with context
    formatted_prompt = profile.prompt.format(
        context=context_text,
        question=request.message
    )
    
    # Generate response
    ai_response = await provider_manager.generate_response(
        provider_name=profile.provider,
        model=profile.model,
        prompt=formatted_prompt,
        temperature=profile.settings.get("temperature", 0.7),
        max_tokens=profile.settings.get("max_tokens", 1000)
    )
    
    if ai_response.error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI provider error: {ai_response.error}"
        )
    
    # Save AI response
    ai_message = await message_repo.create(
        session_id=session_uuid,
        role="assistant",
        content=ai_response.content,
        context_chunks=context_chunks
    )
    
    return SendMessageResponse(
        id=str(ai_message.id),
        role=ai_message.role,
        content=ai_message.content,
        context_chunks=ai_message.context_chunks,
        timestamp=ai_message.timestamp.isoformat(),
        usage=ai_response.usage
    )


@router.post("/chat/query-direct", response_model=ChatQueryResponse)
async def query_without_session(
    request: ChatQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """Query the RAG system directly without creating a session."""
    # Validate profile
    profile_repo = ProfileRepository(db)
    profile = await profile_repo.get_by_id(request.profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with ID {request.profile_id} not found"
        )
    
    # Get context chunks using RAG
    vector_retriever = get_vector_retriever()
    context_chunks = await vector_retriever.get_context_chunks(
        session=db,
        query=request.query,
        profile_id=request.profile_id,
        max_chunks=request.max_context_chunks,
        similarity_threshold=0.7
    )
    
    # Generate AI response
    provider_manager = get_provider_manager()
    
    # Build context for the prompt
    context_text = "\n\n".join([
        f"Document: {chunk.get('document_filename', 'Unknown')}\nContent: {chunk['content']}"
        for chunk in context_chunks
    ])
    
    # Format prompt with context
    formatted_prompt = profile.prompt.format(
        context=context_text,
        question=request.query
    )
    
    # Generate response
    ai_response = await provider_manager.generate_response(
        provider_name=profile.provider,
        model=profile.model,
        prompt=formatted_prompt,
        temperature=profile.settings.get("temperature", 0.7),
        max_tokens=profile.settings.get("max_tokens", 1000)
    )
    
    if ai_response.error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI provider error: {ai_response.error}"
        )
    
    return ChatQueryResponse(
        response=ai_response.content,
        context_chunks=context_chunks,
        usage=ai_response.usage,
        search_time=0.0  # Could be measured
    )


@router.delete("/chat/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a chat session and all its messages."""
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )
    
    session_repo = ChatSessionRepository(db)
    
    # Check if session exists
    session = await session_repo.get_by_id(session_uuid)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session with ID {session_id} not found"
        )
    
    try:
        success = await session_repo.delete(session_uuid)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete chat session"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete chat session: {str(e)}"
        )


@router.get("/chat/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get messages for a specific session."""
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )
    
    # Validate session exists
    session_repo = ChatSessionRepository(db)
    session = await session_repo.get_by_id(session_uuid)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session with ID {session_id} not found"
        )
    
    message_repo = ChatMessageRepository(db)
    messages = await message_repo.get_by_session(session_uuid, limit, offset)
    
    return {
        "session_id": session_id,
        "messages": [
            {
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "context_chunks": msg.context_chunks,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ],
        "total_messages": len(messages),
        "limit": limit,
        "offset": offset
    }
