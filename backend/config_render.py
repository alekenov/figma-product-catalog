import os
from pydantic import field_validator, model_validator, Field
from pydantic_settings import BaseSettings
from typing import List, Any, Dict, Optional


class Settings(BaseSettings):
    # Database - Render provides DATABASE_URL environment variable
    database_url: str = os.getenv("DATABASE_URL", "")

    # For async support with asyncpg
    database_url_async: str = ""

    # Application
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    @field_validator('database_url')
    @classmethod
    def fix_postgres_url(cls, v: str) -> str:
        """Convert postgres:// to postgresql:// for SQLAlchemy compatibility"""
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    @model_validator(mode='after')
    def setup_async_database(self) -> 'Settings':
        """Set up async database URL"""
        # Create async version of database URL
        if self.database_url.startswith("postgresql://"):
            self.database_url_async = self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        else:
            self.database_url_async = self.database_url
        return self

    # API
    api_v1_prefix: str = "/api/v1"
    project_name: str = os.getenv("PROJECT_NAME", "Figma Product Catalog API")

    # Server
    port: int = int(os.getenv("PORT", "8014"))
    api_host: str = os.getenv("API_HOST", "0.0.0.0")

    # Kaspi Pay (production proxy)
    kaspi_api_base_url: str = os.getenv("KASPI_API_BASE_URL", "https://cvety.kz/api/v2/paymentkaspi")
    kaspi_access_token: str = os.getenv("KASPI_ACCESS_TOKEN", "ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144")
    kaspi_organization_bin: str = os.getenv("KASPI_ORGANIZATION_BIN", "891027350515")

    class Config:
        env_file = ".env"
        extra = "allow"


# Initialize settings
settings = Settings()

# Handle CORS origins separately to avoid Pydantic's auto-JSON parsing
cors_str = os.getenv("CORS_ORIGINS") or os.getenv("CORS_ORIGINS_STR") or ""
if not cors_str:
    # Default values if no env var is set
    cors_str = "http://localhost:5176,http://localhost:5173,http://localhost:5175,http://localhost:3000,https://figma-product-catalog-production.up.railway.app"

# Parse and set CORS origins as a simple attribute (not a Pydantic field)
settings.cors_origins = [origin.strip() for origin in cors_str.split(",") if origin.strip()]