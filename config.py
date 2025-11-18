"""Configuration management for the Pool Monitoring Service."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/m2p_db"

    # SocketIO
    socketio_url: str = "http://localhost:3000"

    # Polling
    poll_interval_seconds: int = 60
    pool_request_timeout: int = 10

    # Rewards
    ap_per_advc: float = 100.0
    min_payout_delta: float = 0.0001

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Pool configurations
    cpu_pool_enabled: bool = True
    cpu_pool_url: str = "http://cpu-pool.com/api/worker_stats"

    rplant_enabled: bool = True
    rplant_url: str = "https://pool.rplant.xyz/api/walletEx/advc"

    zpool_enabled: bool = True
    zpool_url: str = "https://zpool.ca/api/walletEx"

    # Conversion rates
    btc_to_advc_rate: float = 1000000.0

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
