"""Application configuration via pydantic-settings.

All settings are driven by environment variables with safe defaults.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/strava"
    app_port: int = 8000
    host: str = "0.0.0.0"
    log_level: str = "info"
