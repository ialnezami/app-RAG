"""
Health check endpoints.
"""
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db, check_db_health
from core.ai_providers import get_provider_manager
from core.embeddings import get_embedding_generator
from config.settings import get_settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "RAG Application API",
        "version": "1.0.0"
    }


@router.get("/status")
async def status_check(db: AsyncSession = Depends(get_db)):
    """Detailed status check with system information."""
    settings = get_settings()
    
    # Check database health
    db_healthy = await check_db_health()
    
    # Check AI providers
    provider_manager = get_provider_manager()
    available_providers = provider_manager.get_available_providers()
    
    # Test embedding generator
    embedding_generator = get_embedding_generator()
    embedding_providers = await embedding_generator.get_available_providers()
    
    # Overall status
    overall_status = "healthy" if db_healthy else "degraded"
    
    status_info = {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "RAG Application API",
        "version": "1.0.0",
        "environment": settings.environment,
        "components": {
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "connection": "connected" if db_healthy else "failed"
            },
            "ai_providers": {
                "status": "healthy" if available_providers else "no_providers",
                "available": available_providers,
                "count": len(available_providers)
            },
            "embeddings": {
                "status": "healthy" if embedding_providers else "no_providers",
                "available_providers": embedding_providers,
                "total_providers": sum(len(models) for models in embedding_providers.values())
            }
        },
        "configuration": {
            "debug_mode": settings.debug,
            "cors_origins": settings.cors_origins,
            "max_file_size": settings.max_file_size,
            "allowed_file_types": settings.allowed_file_types
        }
    }
    
    return status_info


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check with provider testing."""
    settings = get_settings()
    provider_manager = get_provider_manager()
    embedding_generator = get_embedding_generator()
    
    # Test database
    db_healthy = await check_db_health()
    
    # Test AI providers
    provider_tests = {}
    for provider_name in provider_manager.get_available_providers():
        try:
            # Test with a simple query
            response = await provider_manager.generate_response(
                provider_name=provider_name,
                model=provider_manager.get_available_models(provider_name)[0],
                prompt="Hello, this is a health check test.",
                max_tokens=10
            )
            provider_tests[provider_name] = {
                "status": "healthy" if not response.error else "error",
                "error": response.error,
                "response_time": "< 1s"  # Could be measured
            }
        except Exception as e:
            provider_tests[provider_name] = {
                "status": "error",
                "error": str(e)
            }
    
    # Test embedding providers
    embedding_tests = {}
    embedding_providers = await embedding_generator.get_available_providers()
    for provider_name, models in embedding_providers.items():
        if models:
            try:
                test_result = await embedding_generator.test_provider(
                    provider_name, models[0]
                )
                embedding_tests[provider_name] = test_result
            except Exception as e:
                embedding_tests[provider_name] = {
                    "success": False,
                    "error": str(e),
                    "provider": provider_name
                }
    
    detailed_status = {
        "status": "healthy" if db_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "database": {
            "status": "healthy" if db_healthy else "unhealthy",
            "connection": "connected" if db_healthy else "failed"
        },
        "ai_providers": provider_tests,
        "embedding_providers": embedding_tests,
        "system_info": {
            "environment": settings.environment,
            "debug_mode": settings.debug,
            "log_level": settings.log_level
        }
    }
    
    return detailed_status


@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Kubernetes readiness probe endpoint."""
    db_healthy = await check_db_health()
    
    if not db_healthy:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    return {"status": "ready"}


@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe endpoint."""
    return {"status": "alive"}
