"""
Main FastAPI application for the RAG system.
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from core.database import init_db, close_db, check_db_health
from core.middleware import RateLimitMiddleware, SecurityHeadersMiddleware, RequestLoggingMiddleware, MetricsMiddleware
from api.routes import health, profiles, documents, chat, auth, analytics
from api.websocket import chat as ws_chat


# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("🚀 Starting RAG Application...")
    
    # Initialize database
    try:
        await init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    # Check database health
    if not await check_db_health():
        logger.error("❌ Database health check failed")
        raise RuntimeError("Database is not accessible")
    
    logger.info("✅ Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down RAG Application...")
    await close_db()
    logger.info("✅ Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="RAG Application API",
    description="Full-Stack RAG Application with AI-powered document search and chat",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Custom middleware (order matters - first added is outermost)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Create global metrics middleware instance
metrics_middleware = MetricsMiddleware(app)
app.add_middleware(MetricsMiddleware)

# Rate limiting (configurable)
if os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true":
    rate_limit_calls = int(os.getenv("RATE_LIMIT_CALLS", "100"))
    rate_limit_period = int(os.getenv("RATE_LIMIT_PERIOD", "60"))
    app.add_middleware(RateLimitMiddleware, calls=rate_limit_calls, period=rate_limit_period)

# CORS middleware
cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:3000")
if cors_origins_env:
    cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
else:
    cors_origins = ["http://localhost:3000"]

# Add common development origins
development_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

# Use wildcard for development, specific origins for production
if os.getenv("ENVIRONMENT") == "production":
    allowed_origins = cors_origins
else:
    allowed_origins = ["*"]  # Allow all origins in development

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware (for production)
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["your-domain.com", "*.your-domain.com"]
    )

# Rate limiting middleware (if enabled)
if os.getenv("ENABLE_RATE_LIMITING", "false").lower() == "true":
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "code": "INTERNAL_ERROR",
            "details": "An unexpected error occurred"
        }
    )


# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(profiles.router, prefix="/api/v1", tags=["Profiles"])
app.include_router(documents.router, prefix="/api/v1", tags=["Documents"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])

# WebSocket endpoint
app.add_websocket_route("/ws", ws_chat.websocket_endpoint)

# Metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """Get application metrics."""
    return metrics_middleware.get_metrics()

# Static files (for uploaded files)
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RAG Application API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Development server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=os.getenv("RELOAD", "false").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
