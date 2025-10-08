"""
Structured logging configuration for MCP server.
Uses structlog for JSON-formatted logs with request tracing.
"""
import logging
import sys
from typing import Any, Dict

import structlog


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure structured logging for the MCP server.

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
        # Wrapper for standard library logger
        wrapper_class=structlog.stdlib.BoundLogger,
        # Context class for thread-local storage
        context_class=dict,
        # Logger factory
        logger_factory=structlog.stdlib.LoggerFactory(),
        # Clear context on each log call
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
                    customer_phone="77015211545")
    """
    return structlog.get_logger(name)


def bind_request_context(request_id: str, **kwargs: Any) -> None:
    """
    Bind request-level context to all subsequent logs.

    Args:
        request_id: Unique request identifier
        **kwargs: Additional context (shop_id, user_id, etc.)

    Example:
        bind_request_context("req_abc123", shop_id=8, user_id="626599")
        logger.info("processing_order")  # Will include request_id, shop_id, user_id
    """
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        **kwargs
    )


def clear_request_context() -> None:
    """Clear all request-specific context variables."""
    structlog.contextvars.clear_contextvars()
