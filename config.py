"""Configuration management for Local Recall."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from datetime import timezone, timedelta

# PST timezone (UTC-8)
PST = timezone(timedelta(hours=-8))


class Settings(BaseSettings):
    """Application settings."""

    # Paths
    DATABASE_PATH: str = "./data/local_recall.db"
    FAISS_INDEX_PATH: str = "./data/faiss_index"

    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    LLM_MODEL: str = "llama3.1:8b"

    # Server Configuration
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 8501

    # System
    LOG_LEVEL: str = "DEBUG"
    EMBEDDING_DIMENSION: int = 768  # nomic-embed-text dimension
    BATCH_SIZE: int = 10
    MAX_CONTEXT_SNIPPETS: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


def ensure_directories():
    """Ensure required directories exist."""
    settings = get_settings()
    # Create data directory for database
    Path(settings.DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
    # Create directory for FAISS index (it's a directory, not a file)
    Path(settings.FAISS_INDEX_PATH).mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = get_settings()
