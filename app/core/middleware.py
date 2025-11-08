"""
Observability middleware for request tracing and logging
"""
import time
import uuid
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.metrics import MetricsCollector, RequestTimer

logger = logging.getLogger(__name__)
metrics = MetricsCollector()


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Middleware for request tracing, logging, and metrics"""
    
    async def dispatch(self, request: Request, call_next: ASGIApp) -> Response:
        # Generate request ID for tracing
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        # Extract request details
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        
        # Start timer
        start_time = time.time()
        
        # Log request start
        logger.info(
            f"Request started: {method} {path}",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "client_ip": client_ip,
                "component": "middleware"
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
            duration = time.time() - start_time
            
            # Record metrics
            metrics.record_http_request(method, path, status_code, duration)
            
            # Log request completion
            logger.info(
                f"Request completed: {method} {path} - {status_code}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "duration_ms": int(duration * 1000),
                    "component": "middleware"
                }
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time-MS"] = str(int(duration * 1000))
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            error_type = type(e).__name__
            
            # Record error metrics
            metrics.record_error(error_type, "middleware")
            
            # Log error
            logger.error(
                f"Request failed: {method} {path} - {error_type}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "error_type": error_type,
                    "duration_ms": int(duration * 1000),
                    "component": "middleware"
                },
                exc_info=True
            )
            
            # Record failed request metrics
            metrics.record_http_request(method, path, 500, duration)
            
            raise
