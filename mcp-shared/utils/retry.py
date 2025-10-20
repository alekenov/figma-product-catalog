"""Retry logic with exponential backoff and circuit breaker pattern."""

import asyncio
import time
from functools import wraps
from typing import Callable, TypeVar, Any
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying async functions with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff (2.0 = double each time)
        exceptions: Tuple of exceptions to catch and retry

    Example:
        @retry_with_backoff(max_retries=3, base_delay=1)
        async def fetch_data():
            async with httpx.AsyncClient() as client:
                response = await client.get("https://api.example.com")
                response.raise_for_status()
                return response.json()
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries - 1:
                        # Last attempt failed, raise the exception
                        logger.error(
                            f"{func.__name__} failed after {max_retries} attempts: {e}"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )

                    logger.warning(
                        f"{func.__name__} attempt {attempt + 1}/{max_retries} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )

                    await asyncio.sleep(delay)

            # Should never reach here, but just in case
            raise last_exception  # type: ignore

        return wrapper

    return decorator


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for preventing cascading failures.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, reject requests immediately
    - HALF_OPEN: Test if service recovered

    Example:
        breaker = CircuitBreaker(failure_threshold=5, timeout=60)

        @breaker
        async def call_external_api():
            async with httpx.AsyncClient() as client:
                return await client.get("https://api.example.com")
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: type[Exception] = Exception
    ):
        """
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before attempting recovery (OPEN → HALF_OPEN)
            expected_exception: Exception type to count as failure
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: float | None = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    logger.info(f"Circuit breaker entering HALF_OPEN state for {func.__name__}")
                    self.state = "HALF_OPEN"
                else:
                    raise Exception(
                        f"Circuit breaker is OPEN for {func.__name__}. "
                        f"Service unavailable. Try again later."
                    )

            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise

        return wrapper

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self.last_failure_time is None:
            return True
        return (time.time() - self.last_failure_time) >= self.timeout

    def _on_success(self):
        """Handle successful call."""
        if self.state == "HALF_OPEN":
            logger.info("Circuit breaker recovered, entering CLOSED state")

        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            logger.error(
                f"Circuit breaker threshold reached ({self.failure_count} failures). "
                "Entering OPEN state."
            )
            self.state = "OPEN"
