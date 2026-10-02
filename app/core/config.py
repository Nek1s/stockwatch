from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables and .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "StockWatch"
    app_env: str = "local"
    debug: bool = False
    database_url: str = "postgresql+psycopg://stockwatch:stockwatch@localhost:5432/stockwatch"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: str = "unsafe-development-key"


@lru_cache
def get_settings() -> Settings:
    """Create and cache the settings instance for the current process."""
    return Settings()
