"""Configuration management using pydantic-settings."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings are loaded from .env file or environment.
    Critical settings (API keys, external URLs) are required and will raise
    ValidationError if missing.
    """

    # ===== API Keys (Required) =====
    CLAUDE_API_KEY: str  # No default - must be provided

    # ===== External Services (Required) =====
    MCP_SERVER_URL: str  # No default - must be provided
    BACKEND_API_URL: str  # No default - must be provided

    # ===== Server Configuration =====
    PORT: int = 8002
    HOST: str = "0.0.0.0"

    # ===== Database =====
    DB_FILE: str = "chat_sessions.db"

    # ===== Claude Configuration =====
    CLAUDE_MODEL: str = "claude-sonnet-4-5-20250929"
    DEFAULT_SHOP_ID: int = 8
    CACHE_REFRESH_INTERVAL_HOURS: int = 1
    ENABLE_AUTO_CACHE_REFRESH: bool = True

    # ===== Database (Optional - for Railway) =====
    DATABASE_URL: Optional[str] = None  # Optional, fallback to sqlite

    # ===== Logging =====
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True  # Preserve uppercase var names


# Global settings instance
settings = Settings()
