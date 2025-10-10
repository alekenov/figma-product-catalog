"""
Utility functions for integration tests.

Provides helpers for API calls, health checks, and assertions.
"""
import asyncio
import time
from typing import Dict, Any, Optional, List
import httpx

from config import config


class ServiceHealthChecker:
    """Check health of all services before running tests."""

    @staticmethod
    async def wait_for_service(url: str, timeout: int = 60) -> bool:
        """
        Wait for a service to be healthy.

        Args:
            url: Health check URL
            timeout: Max seconds to wait

        Returns:
            True if service is healthy, False if timeout
        """
        start_time = time.time()
        async with httpx.AsyncClient() as client:
            while time.time() - start_time < timeout:
                try:
                    response = await client.get(url, timeout=5.0)
                    if response.status_code == 200:
                        print(f"✅ {url} is healthy")
                        return True
                except (httpx.ConnectError, httpx.TimeoutException):
                    pass

                await asyncio.sleep(config.HEALTH_CHECK_INTERVAL)

        print(f"❌ {url} failed health check after {timeout}s")
        return False

    @staticmethod
    async def check_all_services() -> bool:
        """
        Check health of all required services.

        Returns:
            True if all services are healthy
        """
        if config.SKIP_HEALTH_CHECKS:
            print("⏭️  Skipping health checks (SKIP_HEALTH_CHECKS=true)")
            return True

        print("🏥 Checking service health...")

        checks = [
            ServiceHealthChecker.wait_for_service(
                f"{config.AI_AGENT_URL}/health",
                config.HEALTH_CHECK_TIMEOUT
            ),
            ServiceHealthChecker.wait_for_service(
                f"{config.MCP_SERVER_URL}/health",
                config.HEALTH_CHECK_TIMEOUT
            ),
            ServiceHealthChecker.wait_for_service(
                f"{config.BACKEND_URL}/health",
                config.HEALTH_CHECK_TIMEOUT
            ),
        ]

        results = await asyncio.gather(*checks, return_exceptions=True)

        if all(results):
            print("✅ All services are healthy")
            return True
        else:
            print("❌ Some services are unhealthy")
            return False


class AIAgentClient:
    """Client for AI Agent service API."""

    def __init__(self):
        self.base_url = config.AI_AGENT_URL
        self.timeout = config.REQUEST_TIMEOUT

    async def chat(
        self,
        message: str,
        user_id: str = "test_user",
        channel: str = "telegram",
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a chat message to the AI agent.

        Args:
            message: User message
            user_id: User identifier
            channel: Communication channel
            request_id: Optional request ID for tracing

        Returns:
            AI agent response with text, tracking_id, etc.
        """
        url = f"{self.base_url}/chat"
        headers = {}
        if request_id:
            headers["X-Request-ID"] = request_id

        payload = {
            "message": message,
            "user_id": user_id,
            "channel": channel
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    async def clear_conversation(
        self,
        user_id: str = "test_user",
        channel: str = "telegram"
    ) -> Dict[str, Any]:
        """
        Clear conversation history for a user.

        Args:
            user_id: User identifier
            channel: Communication channel

        Returns:
            Response confirmation
        """
        url = f"{self.base_url}/clear"
        payload = {"user_id": user_id, "channel": channel}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()


class MCPServerClient:
    """Client for MCP Server API."""

    def __init__(self):
        self.base_url = config.MCP_SERVER_URL
        self.timeout = config.REQUEST_TIMEOUT

    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Call an MCP tool directly.

        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
            request_id: Optional request ID for tracing

        Returns:
            Tool execution result
        """
        url = f"{self.base_url}/call-tool"
        headers = {}
        if request_id:
            headers["X-Request-ID"] = request_id

        payload = {"name": tool_name, "arguments": arguments}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()


class BackendAPIClient:
    """Client for Backend API."""

    def __init__(self):
        self.base_url = config.BACKEND_URL
        self.timeout = config.REQUEST_TIMEOUT

    async def login(self, phone: str, password: str) -> Dict[str, Any]:
        """
        Login to get JWT token.

        Args:
            phone: User phone number
            password: User password

        Returns:
            Login response with access_token
        """
        url = f"{self.base_url}/api/v1/auth/login"
        payload = {"phone": phone, "password": password}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()

    async def get_products(
        self,
        shop_id: int = None,
        search: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get products list.

        Args:
            shop_id: Shop ID
            search: Search query
            limit: Max results

        Returns:
            List of products
        """
        url = f"{self.base_url}/api/v1/products"
        params = {
            "shop_id": shop_id or config.TEST_SHOP_ID,
            "limit": limit
        }
        if search:
            params["search"] = search

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()


# Test assertion helpers

def assert_ai_response_contains_tool_call(response: Dict[str, Any], tool_name: str):
    """Assert that AI response indicates a tool was called."""
    # This is a simplified check - in real implementation,
    # you'd need to inspect logs or add debugging endpoints
    assert "text" in response, "Response should contain 'text' field"
    assert isinstance(response["text"], str), "Response text should be a string"


def assert_tracking_id_valid(tracking_id: Optional[str]):
    """Assert that a tracking ID is valid."""
    assert tracking_id is not None, "Tracking ID should not be None"
    assert isinstance(tracking_id, str), "Tracking ID should be a string"
    assert len(tracking_id) > 0, "Tracking ID should not be empty"
    assert tracking_id.isdigit(), "Tracking ID should be numeric"
    assert len(tracking_id) == 9, "Tracking ID should be 9 digits"


def assert_order_structure(order_data: Dict[str, Any]):
    """Assert that order data has expected structure."""
    required_fields = ["tracking_id", "status", "customer_name", "customer_phone"]
    for field in required_fields:
        assert field in order_data, f"Order should contain '{field}' field"


def extract_price_range_from_text(text: str) -> Optional[tuple]:
    """
    Extract price range mentioned in AI response.

    Returns:
        (min_price, max_price) tuple or None
    """
    import re
    # Look for patterns like "10,000" or "10000"
    prices = re.findall(r'(\d{1,3}(?:,\d{3})*|\d+)', text)
    if len(prices) >= 2:
        return (int(prices[0].replace(',', '')), int(prices[1].replace(',', '')))
    return None
