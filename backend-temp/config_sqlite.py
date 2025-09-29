from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database - Using SQLite for MVP testing
    database_url: str = "sqlite+aiosqlite:///./figma_catalog.db"

    # Application
    secret_key: str = "dev-secret-key-change-in-production"
    debug: bool = True
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5175",
        "http://localhost:5176",  # Default frontend port
        "http://localhost:5178"   # Current frontend port
    ]

    # API
    api_v1_prefix: str = "/api/v1"
    project_name: str = "Figma Product Catalog API"

    class Config:
        env_file = ".env"


settings = Settings()