import os
from pydantic import field_validator, model_validator, Field
from pydantic_settings import BaseSettings
from typing import List, Any, Dict, Optional


class Settings(BaseSettings):
    # Database - Render provides DATABASE_URL environment variable
    database_url: str = os.getenv("DATABASE_URL", "")

    # For async support with asyncpg
    database_url_async: str = ""

    # Application - Secret key MUST be explicitly set in production (fail fast if not configured)
    # In development, it can be empty if DATABASE_URL is not set
    secret_key: str = Field(
        default="",  # Overridden by load_secret_key_from_env validator
        min_length=32,
        description="JWT secret key - MUST be set to secure random value (min 32 chars) in production"
    )
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    @field_validator('database_url')
    @classmethod
    def fix_postgres_url(cls, v: str) -> str:
        """Convert postgres:// to postgresql:// for SQLAlchemy compatibility"""
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    @field_validator('secret_key', mode='before')
    @classmethod
    def load_secret_key_from_env(cls, v: str) -> str:
        """Load secret_key from SECRET_KEY environment variable"""
        return os.getenv("SECRET_KEY", v)

    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate that secret_key is not using insecure defaults"""
        if not v:
            # Allow empty only in development mode
            if not os.getenv("DATABASE_URL"):
                return v
            raise ValueError(
                "❌ PRODUCTION ERROR: SECRET_KEY not set. "
                "Set SECRET_KEY env var to a secure random string (min 32 chars). "
                "Generate with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )

        insecure_values = [
            "dev-secret-key-change-in-production",
            "dev-secret-key",
            "secret",
            "password",
            "12345",
        ]

        if v.lower() in [x.lower() for x in insecure_values]:
            raise ValueError(
                "❌ SECURITY ERROR: secret_key has insecure value. "
                "Set SECRET_KEY env var to a secure random string (min 32 chars). "
                "Generate with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )

        if len(v) < 32:
            raise ValueError(f"secret_key must be at least 32 characters, got {len(v)}")

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

    # Kaspi Pay - Credentials must be explicitly set in production
    kaspi_api_base_url: str = os.getenv("KASPI_API_BASE_URL", "https://cvety.kz/api/v2/paymentkaspi")
    kaspi_access_token: str = Field(
        default="",
        description="Kaspi Pay API access token (required for production)"
    )
    kaspi_organization_bin: str = Field(
        default="",
        description="Kaspi Pay organization BIN (required for production)"
    )

    @field_validator('kaspi_access_token', mode='before')
    @classmethod
    def load_kaspi_token_from_env(cls, v: str) -> str:
        """Load Kaspi token from environment"""
        return os.getenv("KASPI_ACCESS_TOKEN", v)

    @field_validator('kaspi_access_token')
    @classmethod
    def validate_kaspi_token(cls, v: str) -> str:
        """Validate Kaspi token is not using development/hardcoded values"""
        if not v:
            # Empty is OK if not using Kaspi payments
            return v

        # Reject known hardcoded/development tokens
        if v in ["ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144", "test", "dev"]:
            raise ValueError(
                "❌ SECURITY ERROR: kaspi_access_token has hardcoded test value. "
                "Set KASPI_ACCESS_TOKEN env var to your actual Kaspi API token."
            )

        return v

    @field_validator('kaspi_organization_bin', mode='before')
    @classmethod
    def load_kaspi_bin_from_env(cls, v: str) -> str:
        """Load Kaspi BIN from environment"""
        return os.getenv("KASPI_ORGANIZATION_BIN", v)

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