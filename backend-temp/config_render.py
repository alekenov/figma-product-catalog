import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database - Render provides DATABASE_URL environment variable
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://figma_catalog_db_user:cj3U4fmMKXpMl2lRMa4A9CalUGBzWBzJ@dpg-d3d3i07diees738dl92g-a.oregon-postgres.render.com/figma_catalog_db"
    )

    # For async support with asyncpg
    database_url_async: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Convert postgres:// to postgresql:// for SQLAlchemy compatibility
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)

        # Create async version of database URL
        if self.database_url.startswith("postgresql://"):
            self.database_url_async = self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        else:
            self.database_url_async = self.database_url

        # Parse CORS origins from comma-separated string
        self.cors_origins = [origin.strip() for origin in self.cors_origins_str.split(",")]

    # Application
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # CORS - parse comma-separated origins
    cors_origins_str: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:5175,http://localhost:3000"
    )
    cors_origins: List[str] = []

    # API
    api_v1_prefix: str = "/api/v1"
    project_name: str = os.getenv("PROJECT_NAME", "Figma Product Catalog API")

    # Server
    port: int = int(os.getenv("PORT", "8000"))

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()