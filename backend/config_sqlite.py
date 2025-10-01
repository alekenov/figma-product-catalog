import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database - Using SQLite for MVP testing
    database_url: str = "sqlite+aiosqlite:///./figma_catalog.db"

    # Application
    secret_key: str = "dev-secret-key-change-in-production"
    debug: bool = True

    # API
    api_v1_prefix: str = "/api/v1"
    project_name: str = "Figma Product Catalog API"

    # Server Configuration
    port: int = int(os.getenv("PORT", "8014"))
    api_host: str = os.getenv("API_HOST", "0.0.0.0")

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()

# Handle CORS origins separately to avoid Pydantic's auto-JSON parsing issues
# For local development, we use a default list of localhost ports
cors_str = os.getenv("CORS_ORIGINS") or os.getenv("CORS_ORIGINS_STR") or ""
if not cors_str:
    # Default localhost origins for development
    default_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5175",
        "http://localhost:5176",  # Admin frontend port
        "http://localhost:5177",  # Website port
        "http://localhost:5178",
        "http://localhost:5179",  # Admin frontend (alternative port)
        "http://localhost:5180"   # Website (alternative port)
    ]
    settings.cors_origins = default_origins
else:
    # Parse comma-separated string if provided via environment
    settings.cors_origins = [origin.strip() for origin in cors_str.split(",") if origin.strip()]