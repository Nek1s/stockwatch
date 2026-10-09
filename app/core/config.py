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
    jwt_secret_key: str = "development-only-secret-key-must-be-at-least-32-chars"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    telegram_bot_token: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Create and cache the settings instance for the current process."""
    return Settings()
