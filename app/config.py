"""Configuration utilities for the social network application."""

from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    app_name: str = Field("Mamontov Social Network", env="APP_NAME")
    database_url: str = Field("sqlite:///./social.db", env="DATABASE_URL")
    access_token_expire_minutes: int = Field(60 * 24, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    secret_key: str = Field("CHANGE_ME", env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings instance."""

    return Settings()
