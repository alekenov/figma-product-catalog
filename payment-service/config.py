"""
Configuration for Payment Service

Uses pydantic-settings for environment variable management.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/payment_service"

    # Production API (cvety.kz PHP endpoints)
    production_api_url: str = "https://cvety.kz/api/v2/paymentkaspi"
    kaspi_access_token: str = ""

    # Service
    port: int = 8015
    debug: bool = False
    cors_origins: str = "http://localhost:5176,http://localhost:5180"

    # Kaspi API settings
    kaspi_api_timeout: int = 30
    kaspi_max_retries: int = 3
    kaspi_retry_delay: int = 1

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
