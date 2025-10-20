"""HTTP client for cvety.kz Production API with retry logic."""

import sys
sys.path.append('../mcp-shared')

import httpx
from typing import Any
from mcp_shared.utils.retry import retry_with_backoff, CircuitBreaker
from mcp_shared.utils.logging import get_logger
from config import settings

logger = get_logger(__name__)

# Circuit breaker for Production API
production_breaker = CircuitBreaker(
    failure_threshold=5,
    timeout=300,  # 5 minutes
    expected_exception=httpx.HTTPError
)


class CvetyProductionClient:
    """
    HTTP client for cvety.kz Production API.

    Features:
    - Automatic retry with exponential backoff
    - Circuit breaker pattern
    - Request/response logging
    - Token authentication
    """

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        timeout: float = 30.0
    ):
        self.base_url = base_url or settings.cvety_api_base_url
        self.token = token or settings.cvety_production_token
        self.timeout = timeout

        logger.info(f"Initialized Production API client: {self.base_url}")

    @retry_with_backoff(max_retries=3, base_delay=1.0, exceptions=(httpx.HTTPError,))
    @production_breaker
    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Execute GET request to Production API.

        Args:
            endpoint: API endpoint (e.g., "/products", "/orders")
            params: Query parameters

        Returns:
            Response JSON data

        Raises:
            httpx.HTTPError: On HTTP errors (4xx, 5xx)
        """
        params = params or {}
        params["access_token"] = self.token

        url = f"{self.base_url}{endpoint}"

        logger.debug(f"GET {url} with params: {params}")

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            logger.debug(f"GET {url} -> {response.status_code}")

            return data

    @retry_with_backoff(max_retries=3, base_delay=1.0, exceptions=(httpx.HTTPError,))
    @production_breaker
    async def post(
        self,
        endpoint: str,
        json_data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Execute POST request to Production API.

        Args:
            endpoint: API endpoint
            json_data: Request body (JSON)
            params: Query parameters

        Returns:
            Response JSON data

        Raises:
            httpx.HTTPError: On HTTP errors
        """
        params = params or {}
        params["access_token"] = self.token

        url = f"{self.base_url}{endpoint}"

        logger.debug(f"POST {url} with data: {json_data}")

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.post(url, json=json_data, params=params)
            response.raise_for_status()

            data = response.json()

            logger.info(f"POST {url} -> {response.status_code}")

            return data

    async def delete(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Execute DELETE request to Production API.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Response JSON data
        """
        params = params or {}
        params["access_token"] = self.token

        url = f"{self.base_url}{endpoint}"

        logger.debug(f"DELETE {url}")

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.delete(url, params=params)
            response.raise_for_status()

            data = response.json()

            logger.warning(f"DELETE {url} -> {response.status_code}")

            return data
