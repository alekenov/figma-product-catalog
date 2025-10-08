"""
FastAPI middleware for request ID tracking and structured logging.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from .logging import get_logger, bind_request_context, clear_request_context, extract_request_id

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle request ID tracking across the application.

    - Extracts X-Request-ID from headers or generates new UUID
    - Binds request_id to structured logging context
    - Adds X-Request-ID to response headers
    - Logs request start and completion with timing
    """

    async def dispatch(self, request: Request, call_next):
        """Process request with request ID tracking."""
        # Extract or generate request ID
        request_id = extract_request_id(request)

        # Bind to logging context
        bind_request_context(
            request_id=request_id,
            method=request.method,
            path=request.url.path
        )

        # Log request start
        logger.info("request_started",
                    client_host=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"))

        try:
            # Process request
            response: Response = await call_next(request)

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            # Log successful completion
            logger.info("request_completed",
                        status_code=response.status_code)

            return response

        except Exception as e:
            # Log error
            logger.error("request_failed",
                        error=str(e),
                        error_type=type(e).__name__)
            raise

        finally:
            # Clear request context
            clear_request_context()
