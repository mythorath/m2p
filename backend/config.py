"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str = "postgresql://m2p_user:m2p_password@localhost:5432/m2p_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Application
    SECRET_KEY: str = "your-secret-key-here"
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Leaderboard
    LEADERBOARD_CACHE_TTL: int = 300  # 5 minutes
    LEADERBOARD_UPDATE_INTERVAL: int = 300  # 5 minutes
    LEADERBOARD_TOP_LIMIT: int = 1000

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
