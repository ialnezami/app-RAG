"""
Simple analytics endpoints without heavy dependencies.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, text
from pydantic import BaseModel

from core.database import get_db
from core.models import Profile, Document, DocumentChunk, ChatSession, ChatMessage

router = APIRouter()

class SimpleSystemMetrics(BaseModel):
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    uptime: float = 0.0
    timestamp: str

class DatabaseMetrics(BaseModel):
    total_profiles: int
    total_documents: int
    total_chunks: int
    total_chat_sessions: int
    total_messages: int
    processed_documents: int
    unprocessed_documents: int

class UsageMetrics(BaseModel):
    daily_queries: int
    weekly_queries: int
    monthly_queries: int
    average_response_time: float
    popular_models: List[Dict[str, Any]]
    active_profiles: int

class SimpleAnalyticsDashboard(BaseModel):
    system: SimpleSystemMetrics
    database: DatabaseMetrics
    usage: UsageMetrics
    timestamp: str

@router.get("/analytics/system", response_model=SimpleSystemMetrics)
async def get_system_metrics():
    """Get basic system metrics (placeholder values)."""
    return SimpleSystemMetrics(
        cpu_usage=15.5,  # Placeholder
        memory_usage=45.2,  # Placeholder
        disk_usage=23.8,  # Placeholder
        uptime=3600.0,  # Placeholder
        timestamp=datetime.utcnow().isoformat()
    )

@router.get("/analytics/database", response_model=DatabaseMetrics)
async def get_database_metrics(db: AsyncSession = Depends(get_db)):
    """Get database metrics."""
    try:
        # Count profiles
        result = await db.execute(select(func.count(Profile.id)))
        total_profiles = result.scalar() or 0
        
        # Count documents
        result = await db.execute(select(func.count(Document.id)))
        total_documents = result.scalar() or 0
        
        # Count processed/unprocessed documents
        result = await db.execute(select(func.count(Document.id)).where(Document.processed == True))
        processed_documents = result.scalar() or 0
        
        result = await db.execute(select(func.count(Document.id)).where(Document.processed == False))
        unprocessed_documents = result.scalar() or 0
        
        # Count chunks
        result = await db.execute(select(func.count(DocumentChunk.id)))
        total_chunks = result.scalar() or 0
        
        # Count chat sessions
        result = await db.execute(select(func.count(ChatSession.id)))
        total_chat_sessions = result.scalar() or 0
        
        # Count messages
        result = await db.execute(select(func.count(ChatMessage.id)))
        total_messages = result.scalar() or 0
        
        return DatabaseMetrics(
            total_profiles=total_profiles,
            total_documents=total_documents,
            total_chunks=total_chunks,
            total_chat_sessions=total_chat_sessions,
            total_messages=total_messages,
            processed_documents=processed_documents,
            unprocessed_documents=unprocessed_documents
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get database metrics: {str(e)}"
        )

@router.get("/analytics/usage", response_model=UsageMetrics)
async def get_usage_metrics(db: AsyncSession = Depends(get_db)):
    """Get usage analytics."""
    try:
        now = datetime.utcnow()
        
        # Daily queries (last 24 hours)
        daily_start = now - timedelta(days=1)
        result = await db.execute(
            select(func.count(ChatMessage.id))
            .where(and_(
                ChatMessage.role == 'user',
                ChatMessage.timestamp >= daily_start
            ))
        )
        daily_queries = result.scalar() or 0
        
        # Weekly queries (last 7 days)
        weekly_start = now - timedelta(days=7)
        result = await db.execute(
            select(func.count(ChatMessage.id))
            .where(and_(
                ChatMessage.role == 'user',
                ChatMessage.timestamp >= weekly_start
            ))
        )
        weekly_queries = result.scalar() or 0
        
        # Monthly queries (last 30 days)
        monthly_start = now - timedelta(days=30)
        result = await db.execute(
            select(func.count(ChatMessage.id))
            .where(and_(
                ChatMessage.role == 'user',
                ChatMessage.timestamp >= monthly_start
            ))
        )
        monthly_queries = result.scalar() or 0
        
        # Popular models (from profiles)
        result = await db.execute(
            select(Profile.provider, Profile.model, func.count(Profile.id).label('count'))
            .group_by(Profile.provider, Profile.model)
            .order_by(func.count(Profile.id).desc())
            .limit(5)
        )
        popular_models = [
            {
                "provider": row.provider,
                "model": row.model,
                "count": row.count
            }
            for row in result.all()
        ]
        
        # Active profiles (profiles with recent activity)
        result = await db.execute(
            select(func.count(func.distinct(ChatSession.profile_id)))
            .where(ChatSession.updated_at >= monthly_start)
        )
        active_profiles = result.scalar() or 0
        
        return UsageMetrics(
            daily_queries=daily_queries,
            weekly_queries=weekly_queries,
            monthly_queries=monthly_queries,
            average_response_time=2.1,  # Placeholder
            popular_models=popular_models,
            active_profiles=active_profiles
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage metrics: {str(e)}"
        )

@router.get("/analytics/dashboard", response_model=SimpleAnalyticsDashboard)
async def get_analytics_dashboard(db: AsyncSession = Depends(get_db)):
    """Get complete analytics dashboard."""
    try:
        system_metrics = await get_system_metrics()
        database_metrics = await get_database_metrics(db)
        usage_metrics = await get_usage_metrics(db)
        
        return SimpleAnalyticsDashboard(
            system=system_metrics,
            database=database_metrics,
            usage=usage_metrics,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics dashboard: {str(e)}"
        )

@router.get("/analytics/health")
async def get_health_analytics(db: AsyncSession = Depends(get_db)):
    """Get basic health analytics."""
    try:
        return {
            "database_status": "connected",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy"
        }
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error"
        }
