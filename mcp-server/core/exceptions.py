"""
Typed exceptions for API errors.
Maps HTTP status codes to domain-specific exceptions for better error handling.
"""
from typing import Optional, Dict, Any


class APIError(Exception):
    """Base exception for all API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class NotFoundError(APIError):
    """Resource not found (404)."""

    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} not found: {identifier}",
            status_code=404
        )


class ValidationError(APIError):
    """Invalid input data (422)."""

    def __init__(self, message: str, errors: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Validation error: {message}",
            status_code=422,
            response_data={"errors": errors or {}}
        )


class AuthenticationError(APIError):
    """Authentication required or failed (401)."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message=message, status_code=401)


class PermissionError(APIError):
    """Insufficient permissions (403)."""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(message=message, status_code=403)


class RateLimitError(APIError):
    """Rate limit exceeded (429)."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        super().__init__(
            message=message,
            status_code=429,
            response_data={"retry_after": retry_after}
        )


class ServerError(APIError):
    """Internal server error (500-599)."""

    def __init__(self, message: str = "Internal server error", status_code: int = 500):
        super().__init__(message=message, status_code=status_code)


def map_status_to_exception(status_code: int, response_text: str) -> APIError:
    """
    Map HTTP status code to appropriate exception type.

    Args:
        status_code: HTTP status code
        response_text: Raw response text

    Returns:
        Appropriate APIError subclass
    """
    error_map = {
        401: lambda: AuthenticationError(response_text),
        403: lambda: PermissionError(response_text),
        404: lambda: NotFoundError("Resource", response_text),
        422: lambda: ValidationError(response_text),
        429: lambda: RateLimitError(response_text),
    }

    if status_code in error_map:
        return error_map[status_code]()
    elif 500 <= status_code < 600:
        return ServerError(response_text, status_code)
    else:
        return APIError(response_text, status_code)
