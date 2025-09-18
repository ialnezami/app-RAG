"""
Analytics and monitoring endpoints.
"""
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, text
from pydantic import BaseModel

from core.database import get_db
from core.models import Profile, Document, DocumentChunk, ChatSession, ChatMessage, User
from core.auth import get_current_user, require_admin
from config.settings import get_settings

router = APIRouter()

class SystemMetrics(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    uptime: float
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

class AnalyticsDashboard(BaseModel):
    system: SystemMetrics
    database: DatabaseMetrics
    usage: UsageMetrics
    timestamp: str

@router.get("/analytics/system", response_model=SystemMetrics)
async def get_system_metrics(current_user: Optional[User] = Depends(get_current_user)):
    """Get system performance metrics."""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        # System uptime (approximate)
        boot_time = psutil.boot_time()
        uptime = datetime.now().timestamp() - boot_time
        
        return SystemMetrics(
            cpu_usage=cpu_percent,
            memory_usage=memory_percent,
            disk_usage=disk_percent,
            uptime=uptime,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system metrics: {str(e)}"
        )

@router.get("/analytics/database", response_model=DatabaseMetrics)
async def get_database_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
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
async def get_usage_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
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
            average_response_time=2.5,  # Placeholder - would need actual tracking
            popular_models=popular_models,
            active_profiles=active_profiles
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage metrics: {str(e)}"
        )

@router.get("/analytics/dashboard", response_model=AnalyticsDashboard)
async def get_analytics_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get complete analytics dashboard."""
    try:
        system_metrics = await get_system_metrics(current_user)
        database_metrics = await get_database_metrics(db, current_user)
        usage_metrics = await get_usage_metrics(db, current_user)
        
        return AnalyticsDashboard(
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
async def get_health_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get health and performance analytics."""
    try:
        # Database connection pool status
        engine_info = {
            "pool_size": db.bind.pool.size(),
            "checked_in": db.bind.pool.checkedin(),
            "checked_out": db.bind.pool.checkedout(),
            "overflow": db.bind.pool.overflow(),
            "invalidated": db.bind.pool.invalidated()
        }
        
        # Recent error counts
        error_window = datetime.utcnow() - timedelta(hours=1)
        
        return {
            "database_pool": engine_info,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy"
        }
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error"
        }

@router.get("/analytics/performance")
async def get_performance_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get detailed performance metrics."""
    try:
        # Database query performance
        db_stats = await db.execute(text("""
            SELECT 
                schemaname,
                tablename,
                attname,
                n_distinct,
                correlation
            FROM pg_stats 
            WHERE schemaname = 'public'
            LIMIT 10
        """))
        
        db_performance = [dict(row._mapping) for row in db_stats.all()]
        
        # Document processing performance
        result = await db.execute(
            select(
                func.avg(func.extract('epoch', func.now() - Document.upload_date)).label('avg_processing_time'),
                func.count(Document.id).label('total_documents'),
                func.count(Document.id).filter(Document.processed == True).label('processed_count')
            )
        )
        doc_stats = result.first()
        
        return {
            "database_performance": db_performance,
            "document_processing": {
                "average_processing_time": float(doc_stats.avg_processing_time or 0),
                "total_documents": doc_stats.total_documents,
                "processed_documents": doc_stats.processed_count,
                "processing_rate": float(doc_stats.processed_count / max(doc_stats.total_documents, 1) * 100)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance metrics: {str(e)}"
        )
