"""
Custom middleware for rate limiting and security.
"""
import time
from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio
from collections import defaultdict, deque
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window algorithm."""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls  # Number of calls allowed
        self.period = period  # Time period in seconds
        self.clients: Dict[str, deque] = defaultdict(deque)
        self.lock = asyncio.Lock()
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and static files
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"] or request.url.path.startswith("/static"):
            return await call_next(request)
        
        # Get client identifier (IP address)
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        if await self._is_rate_limited(client_ip):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {self.calls} per {self.period} seconds",
                    "retry_after": self.period
                },
                headers={"Retry-After": str(self.period)}
            )
        
        # Process request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add performance headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Rate-Limit-Limit"] = str(self.calls)
        response.headers["X-Rate-Limit-Remaining"] = str(max(0, self.calls - len(self.clients[client_ip])))
        response.headers["X-Rate-Limit-Reset"] = str(int(time.time()) + self.period)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request."""
        # Check for forwarded headers (behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"
    
    async def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if client is rate limited."""
        async with self.lock:
            now = time.time()
            client_requests = self.clients[client_ip]
            
            # Remove old requests outside the time window
            while client_requests and client_requests[0] <= now - self.period:
                client_requests.popleft()
            
            # Check if limit is exceeded
            if len(client_requests) >= self.calls:
                return True
            
            # Add current request
            client_requests.append(now)
            return False

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Only add HSTS in production with HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for monitoring."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path} from {self._get_client_ip(request)}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code} for {request.method} {request.url.path} "
                f"in {process_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error: {str(e)} for {request.method} {request.url.path} "
                f"in {process_time:.3f}s"
            )
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"

class MetricsMiddleware(BaseHTTPMiddleware):
    """Collect metrics for monitoring."""
    
    def __init__(self, app):
        super().__init__(app)
        self.request_count = defaultdict(int)
        self.response_times = defaultdict(list)
        self.error_count = defaultdict(int)
        self.start_time = datetime.now()
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        method_path = f"{request.method} {request.url.path}"
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Collect metrics
            self.request_count[method_path] += 1
            self.response_times[method_path].append(process_time)
            
            # Keep only last 1000 response times per endpoint
            if len(self.response_times[method_path]) > 1000:
                self.response_times[method_path] = self.response_times[method_path][-1000:]
            
            # Track errors
            if response.status_code >= 400:
                self.error_count[method_path] += 1
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            self.error_count[method_path] += 1
            raise
    
    def get_metrics(self) -> Dict:
        """Get collected metrics."""
        metrics = {
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "total_requests": sum(self.request_count.values()),
            "total_errors": sum(self.error_count.values()),
            "endpoints": {}
        }
        
        for endpoint in self.request_count:
            response_times = self.response_times[endpoint]
            metrics["endpoints"][endpoint] = {
                "request_count": self.request_count[endpoint],
                "error_count": self.error_count[endpoint],
                "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0
            }
        
        return metrics
