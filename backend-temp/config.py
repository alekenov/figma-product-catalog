from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/figma_catalog"

    # Application
    secret_key: str = "dev-secret-key-change-in-production"
    debug: bool = True
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # API
    api_v1_prefix: str = "/api/v1"
    project_name: str = "Figma Product Catalog API"

    class Config:
        env_file = ".env"


settings = Settings()