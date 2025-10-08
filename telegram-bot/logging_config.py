"""
Structured logging configuration for Telegram Bot.
Uses structlog for JSON-formatted logs with request tracing.
"""
import logging
import sys

import structlog


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure structured logging for the Telegram Bot.

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
        logger.info("message_received",
                    request_id="req_123",
                    telegram_user_id="626599",
                    chat_id=123456,
                    message_type="text")
    """
    return structlog.get_logger(name)


def bind_request_context(request_id: str, telegram_user_id: str = None, chat_id: int = None) -> None:
    """
    Bind request-level context to all subsequent logs.

    Args:
        request_id: Unique request identifier
        telegram_user_id: Telegram user ID
        chat_id: Telegram chat ID

    Example:
        bind_request_context("req_abc123", telegram_user_id="626599", chat_id=123456)
        logger.info("processing_callback")  # Includes all context
    """
    context = {"request_id": request_id}
    if telegram_user_id:
        context["telegram_user_id"] = str(telegram_user_id)
    if chat_id:
        context["chat_id"] = chat_id

    structlog.contextvars.bind_contextvars(**context)


def clear_request_context() -> None:
    """Clear all request-specific context variables."""
    structlog.contextvars.clear_contextvars()
