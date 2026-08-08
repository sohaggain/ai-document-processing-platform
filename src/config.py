"""
Centralized application configuration.

All runtime behavior is controlled via environment variables so that the
same codebase can move from local dev to Docker to production without
code changes. See .env.example for the full list of variables.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    # Security
    api_key: str = "changeme"
    webhook_signing_secret: str = "changeme"

    # Database
    database_url: str = "postgresql://docuser:docpass@localhost:5432/document_platform"

    # LLM
    llm_provider: str = "anthropic"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"
    openai_api_key: str = ""

    # Extraction
    confidence_threshold: float = 0.75
    max_upload_size_mb: int = 15
    allowed_file_types: str = "pdf,png,jpg,jpeg"

    # OCR
    tesseract_cmd: str = "/usr/bin/tesseract"

    # n8n
    n8n_webhook_url: str = ""
    n8n_webhook_enabled: bool = True

    # Storage
    storage_path: str = "./storage/uploads"

    @property
    def allowed_extensions(self) -> list[str]:
        return [ext.strip().lower() for ext in self.allowed_file_types.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
