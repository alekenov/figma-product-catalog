"""
Configuration management for MCP server.
Centralizes environment variable loading and validation.
"""
import os
from typing import Optional


class Config:
    """Application configuration loaded from environment variables."""

    # API settings
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8014/api/v1")
    DEFAULT_SHOP_ID: int = int(os.getenv("DEFAULT_SHOP_ID", "8"))

    # HTTP client settings
    REQUEST_TIMEOUT: float = float(os.getenv("REQUEST_TIMEOUT", "30.0"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_BACKOFF: float = float(os.getenv("RETRY_BACKOFF", "1.0"))

    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_REQUESTS: bool = os.getenv("LOG_REQUESTS", "true").lower() == "true"

    @classmethod
    def validate(cls) -> None:
        """Validate configuration values."""
        if not cls.API_BASE_URL:
            raise ValueError("API_BASE_URL must be set")

        if cls.DEFAULT_SHOP_ID < 1:
            raise ValueError("DEFAULT_SHOP_ID must be positive")

        if cls.REQUEST_TIMEOUT <= 0:
            raise ValueError("REQUEST_TIMEOUT must be positive")

    @classmethod
    def get_api_url(cls, endpoint: str) -> str:
        """
        Construct full API URL from endpoint.

        Args:
            endpoint: API endpoint path (e.g., "/products")

        Returns:
            Full URL (e.g., "http://localhost:8014/api/v1/products")
        """
        # Ensure endpoint starts with /
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"

        return f"{cls.API_BASE_URL}{endpoint}"


# Validate config on import
Config.validate()
