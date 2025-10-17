import os
from pydantic import field_validator, Field
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database - Using SQLite for MVP testing
    database_url: str = "sqlite+aiosqlite:///./figma_catalog.db"

    # Application - Secret key MUST be explicitly set (fail fast if not configured)
    secret_key: str = Field(
        ...,  # Required - no default value
        min_length=32,
        description="JWT secret key - MUST be set to secure random value (min 32 chars)"
    )
    debug: bool = True

    # API
    api_v1_prefix: str = "/api/v1"
    project_name: str = "Figma Product Catalog API"

    # Server Configuration
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

    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate that secret_key is secure (non-empty check done by Field(...))"""
        if not v:  # Extra safety check (should be caught by Field(...) required)
            raise ValueError(
                "❌ SECURITY ERROR: SECRET_KEY environment variable not set. "
                "This is REQUIRED for secure token signing. "
                "Set SECRET_KEY env var to a secure random string (minimum 32 characters). "
                "Generate with: python -c \"import secrets; print(secrets.token_urlsafe(32))\" "
                "For local development, create backend/.env with: SECRET_KEY=<your-key>"
            )

        # Reject known insecure/development values
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

        # Length check (should be caught by Field(min_length=32) but extra safety)
        if len(v) < 32:
            raise ValueError(f"secret_key must be at least 32 characters, got {len(v)}")

        return v

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