"""
Structured logging configuration for Backend API.
Uses structlog for JSON-formatted logs with request tracing.
"""
import logging
import sys
from typing import Optional

import structlog
from fastapi import Request


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure structured logging for the Backend API.

    Outputs JSON-formatted logs to stdout for Railway log aggregation.
    Includes timestamp, log level, request_id, and structured context.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )

    # Configure structlog processors
    structlog.configure(
        processors=[
            # Add log level
            structlog.stdlib.add_log_level,
            # Add timestamp in ISO format
            structlog.processors.TimeStamper(fmt="iso"),
            # Add logger name
            structlog.stdlib.add_logger_name,
            # Stack info for exceptions
            structlog.processors.StackInfoRenderer(),
            # Format exception
            structlog.processors.format_exc_info,
            # Render as JSON for Railway
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured structlog logger

    Example:
        logger = get_logger(__name__)
        logger.info("order_created",
                    request_id="req_123",
                    shop_id=8,
                    order_id=456,
                    total_price=15000)
    """
    return structlog.get_logger(name)


def bind_request_context(
    request_id: str,
    shop_id: Optional[int] = None,
    user_id: Optional[str] = None,
    **kwargs
) -> None:
    """
    Bind request-level context to all subsequent logs.

    Args:
        request_id: Unique request identifier
        shop_id: Shop ID for multi-tenancy
        user_id: User/customer ID
        **kwargs: Additional context

    Example:
        bind_request_context("req_abc123", shop_id=8, user_id="456")
        logger.info("processing_request")  # Includes all context
    """
    context = {"request_id": request_id}
    if shop_id:
        context["shop_id"] = shop_id
    if user_id:
        context["user_id"] = user_id
    context.update(kwargs)

    structlog.contextvars.bind_contextvars(**context)


def clear_request_context() -> None:
    """Clear all request-specific context variables."""
    structlog.contextvars.clear_contextvars()


def extract_request_id(request: Request) -> str:
    """
    Extract or generate request_id from FastAPI Request.

    Looks for X-Request-ID header first, otherwise generates a new UUID.

    Args:
        request: FastAPI Request object

    Returns:
        Request ID string
    """
    import uuid

    request_id = request.headers.get("x-request-id")
    if not request_id:
        request_id = f"req_{uuid.uuid4().hex[:12]}"

    return request_id
