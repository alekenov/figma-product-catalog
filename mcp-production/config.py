"""Configuration for mcp-production server."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Production API
    cvety_production_token: str = "ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144"
    cvety_api_base_url: str = "https://cvety.kz/api/v2"
    cvety_shop_id: int = 17008
    cvety_city_id: int = 2

    # Railway MCP Server
    railway_mcp_url: str = "http://localhost:8000"
    railway_webhook_secret: str = "change-me-in-production"

    # Logging
    log_level: str = "INFO"
    log_json: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
