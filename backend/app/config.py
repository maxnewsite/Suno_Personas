"""Application configuration."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # LLM Configuration
    llm_provider: str = "openai"  # or "anthropic"
    openai_model: str = "gpt-4-turbo-preview"
    anthropic_model: str = "claude-3-sonnet-20240229"

    # File Upload Configuration
    max_file_size_mb: int = 10
    max_duration_seconds: int = 600  # 10 minutes
    upload_dir: str = "./temp_uploads"

    # CORS Settings
    cors_origins: str = "http://localhost:3000,http://localhost:3001"

    # Rate Limiting
    rate_limit_per_hour: int = 10

    # Scoring Weights
    audio_quality_weight: float = 0.15
    artistic_appeal_weight: float = 0.15
    persona_weight: float = 0.70

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        """Convert max file size to bytes."""
        return self.max_file_size_mb * 1024 * 1024

    def ensure_upload_dir(self):
        """Ensure upload directory exists."""
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.ensure_upload_dir()
