"""
Reusable HTTP client for backend API communication.
Handles authentication, retries, logging, and exception mapping.
"""
import httpx
from typing import Optional, Dict, Any, TypeVar
import structlog
from .config import Config
from .exceptions import map_status_to_exception, APIError

# Use structured logger
logger = structlog.get_logger(__name__)

T = TypeVar('T')


class APIClient:
    """
    HTTP client for backend API with built-in error handling and retries.

    Features:
    - Automatic JWT token handling
    - Typed exceptions mapped from HTTP status codes
    - Request/response logging for debugging
    - Retry logic with exponential backoff
    - Timeout configuration
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ):
        self.base_url = base_url or Config.API_BASE_URL
        self.timeout = timeout or Config.REQUEST_TIMEOUT
        self.max_retries = max_retries or Config.MAX_RETRIES

    async def request(
        self,
        method: str,
        endpoint: str,
        token: Optional[str] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> Any:
        """
        Make HTTP request with automatic error handling.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint (e.g., "/products")
            token: Optional JWT token for authentication
            json_data: Request body as dictionary
            params: Query parameters
            request_id: Optional request ID for tracing

        Returns:
            Parsed JSON response

        Raises:
            APIError: On HTTP error (typed exception based on status code)
        """
        url = Config.get_api_url(endpoint)
        headers = {}

        if token:
            headers["Authorization"] = f"Bearer {token}"

        # Add request ID for distributed tracing
        # If not provided, try to get from structlog context
        if not request_id:
            try:
                # Access contextvars bound data
                context = structlog.contextvars.get_contextvars()
                request_id = context.get("request_id")
            except:
                pass

        if request_id:
            headers["X-Request-ID"] = request_id

        # Log request if enabled
        if Config.LOG_REQUESTS:
            logger.debug(f"{method} {url}")
            if json_data:
                logger.debug(f"Request body: {json_data}")
            if params:
                logger.debug(f"Query params: {params}")

        # Make request with retry logic
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(
                    timeout=self.timeout,
                    follow_redirects=True
                ) as client:
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        json=json_data,
                        params=params,
                    )

                    # Log response if enabled
                    if Config.LOG_REQUESTS:
                        logger.debug(f"Response status: {response.status_code}")

                    # Handle error responses
                    if response.status_code >= 400:
                        exception = map_status_to_exception(
                            response.status_code,
                            response.text
                        )
                        logger.error(
                            f"API error: {exception.message} "
                            f"(attempt {attempt + 1}/{self.max_retries})"
                        )
                        raise exception

                    # Success - return JSON
                    return response.json()

            except httpx.TimeoutException as e:
                last_exception = APIError(
                    f"Request timeout after {self.timeout}s",
                    status_code=408
                )
                logger.warning(
                    f"Timeout on attempt {attempt + 1}/{self.max_retries}: {e}"
                )

            except httpx.NetworkError as e:
                last_exception = APIError(
                    f"Network error: {str(e)}",
                    status_code=503
                )
                logger.warning(
                    f"Network error on attempt {attempt + 1}/{self.max_retries}: {e}"
                )

            except APIError:
                # Don't retry on client errors (4xx)
                raise

            except Exception as e:
                last_exception = APIError(
                    f"Unexpected error: {str(e)}",
                    status_code=500
                )
                logger.error(
                    f"Unexpected error on attempt {attempt + 1}/{self.max_retries}: {e}"
                )

            # Wait before retry (exponential backoff)
            if attempt < self.max_retries - 1:
                import asyncio
                wait_time = Config.RETRY_BACKOFF * (2 ** attempt)
                logger.debug(f"Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

        # All retries exhausted
        if last_exception:
            raise last_exception
        else:
            raise APIError("Request failed after all retries")

    async def get(
        self,
        endpoint: str,
        token: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> Any:
        """GET request."""
        return await self.request("GET", endpoint, token=token, params=params, request_id=request_id)

    async def post(
        self,
        endpoint: str,
        json_data: Dict[str, Any],
        token: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> Any:
        """POST request."""
        return await self.request(
            "POST", endpoint, token=token, json_data=json_data, params=params, request_id=request_id
        )

    async def put(
        self,
        endpoint: str,
        json_data: Dict[str, Any],
        token: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> Any:
        """PUT request."""
        return await self.request(
            "PUT", endpoint, token=token, json_data=json_data, params=params, request_id=request_id
        )

    async def patch(
        self,
        endpoint: str,
        json_data: Dict[str, Any],
        token: Optional[str] = None,
        request_id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """PATCH request."""
        return await self.request(
            "PATCH", endpoint, token=token, json_data=json_data, params=params, request_id=request_id
        )

    async def delete(
        self,
        endpoint: str,
        token: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> Any:
        """DELETE request."""
        return await self.request("DELETE", endpoint, token=token, params=params, request_id=request_id)


# Global client instance
api_client = APIClient()
