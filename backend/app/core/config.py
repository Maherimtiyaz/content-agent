import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application configuration from environment variables."""

    # Application
    app_name: str = "brand_engineer"
    app_secret_key: str = "test-secret-key-for-testing-only"
    log_level: str = "INFO"
    environment: str = "development"

    # Database
    database_url: str = "sqlite:///./test.db"

    model_config = {
        "env_file": ".env.test" if os.getenv("TESTING") == "true" else ".env",
        "case_sensitive": False,
        "extra": "ignore",  # Ignore extra fields in env file
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    # Clear cache if TESTING env var is set to ensure fresh settings
    if os.getenv("TESTING") == "true":
        get_settings.cache_clear()
    return Settings()
