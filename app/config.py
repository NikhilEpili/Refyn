"""Configuration management for Refyn AI."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from typing import Literal

class Settings(BaseSettings):
    """Application settings, loaded from environment variables or .env file."""
    
    # GitHub App
    github_app_id: int | None = None
    github_private_key_path: str | None = None
    github_webhook_secret: SecretStr | None = None
    
    # LLM
    openai_api_key: SecretStr | None = None
    mistral_api_key: SecretStr | None = None
    llm_provider: Literal["openai", "mistral"] = "openai"
    
    # Infrastructure
    postgres_dsn: str = "postgresql://refyn:refyn_password@localhost:5432/refyn"
    qdrant_url: str = "http://localhost:6333"
    redis_url: str = "redis://localhost:6379"
    
    # Review quality
    confidence_threshold: float = 0.65
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
