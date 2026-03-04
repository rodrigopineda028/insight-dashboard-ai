"""Application settings and configuration."""
import os
from typing import Set


class Settings:
    """Application configuration settings."""
    
    # API Keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS: Set[str] = {".csv", ".xlsx"}
    
    # AI Configuration
    AI_MODEL: str = "claude-sonnet-4-5"
    AI_MAX_TOKENS: int = 2000
    AI_TEMPERATURE: float = 0.3
    AI_MAX_RETRIES: int = 2
    
    # Chart Configuration
    SCATTER_MAX_POINTS: int = 500
    PIE_CHART_MAX_CATEGORIES: int = 10
    
    @classmethod
    def validate(cls) -> None:
        """Validate required settings."""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")


settings = Settings()
