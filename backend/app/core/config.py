import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application configuration from environment variables."""

    # Application
    app_name: str = "brand_engineer"
    app_secret_key: str
    log_level: str = "INFO"
    environment: str = "development"

    # Database
    database_url: str

    model_config = {
        "env_file": ".env.test" if os.getenv("ENVIRONMENT") == "test" else ".env",
        "case_sensitive": False,
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
