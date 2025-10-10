"""
Configuration for integration tests.

Supports both local development and CI environments.
"""
import os
from typing import Optional


class TestConfig:
    """Integration test configuration."""

    # Service URLs (override with environment variables)
    # Docker Compose default: AI Agent on 8000, Standalone: 8015
    AI_AGENT_URL: str = os.getenv("AI_AGENT_URL", "http://localhost:8000")
    MCP_SERVER_URL: str = os.getenv("MCP_SERVER_URL", "http://localhost:8001")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8014")

    # Test shop configuration
    TEST_SHOP_ID: int = int(os.getenv("TEST_SHOP_ID", "8"))

    # Test user credentials (for authenticated tests)
    TEST_USER_PHONE: str = os.getenv("TEST_USER_PHONE", "77015211545")
    TEST_USER_PASSWORD: str = os.getenv("TEST_USER_PASSWORD", "1234")

    # Test customer data
    TEST_CUSTOMER_NAME: str = "Integration Test Customer"
    TEST_CUSTOMER_PHONE: str = "77777777777"
    TEST_DELIVERY_ADDRESS: str = "ул. Тестовая, дом 1, кв. 1"

    # Timeouts
    REQUEST_TIMEOUT: int = 30  # seconds
    HEALTH_CHECK_TIMEOUT: int = 60  # seconds
    HEALTH_CHECK_INTERVAL: int = 2  # seconds

    # Test mode flags
    SKIP_HEALTH_CHECKS: bool = os.getenv("SKIP_HEALTH_CHECKS", "false").lower() == "true"
    VERBOSE_LOGGING: bool = os.getenv("VERBOSE_LOGGING", "false").lower() == "true"

    # Claude API key (optional - can use mocked responses)
    CLAUDE_API_KEY: Optional[str] = os.getenv("CLAUDE_API_KEY")
    USE_MOCKED_AI: bool = os.getenv("USE_MOCKED_AI", "false").lower() == "true"


config = TestConfig()
