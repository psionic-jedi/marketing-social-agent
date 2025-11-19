"""
Application configuration using Pydantic settings.
Loads environment variables and provides typed configuration.
"""
from typing import List, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    # API Keys
    anthropic_api_key: str
    google_api_key: str

    # Database
    database_url: str

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Storage Configuration
    storage_type: Literal["local", "s3"] = "local"
    local_storage_path: str = "./storage"

    # AWS S3 (only needed if storage_type=s3)
    s3_bucket: str = ""
    aws_region: str = "eu-west-2"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""

    # Application
    secret_key: str
    debug: bool = False
    environment: Literal["development", "production", "testing"] = "development"
    log_level: str = "INFO"

    # CORS
    allowed_origins: str = "http://localhost:3000"

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse CORS allowed origins into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    # SMTP (optional, for test emails)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    # Application metadata
    app_name: str = "Marketing Agent System"
    app_version: str = "1.0.0"

    # Agent configuration
    default_temperature: float = 0.7
    max_tokens: int = 4000
    use_real_scraping: bool = True  # Enable real web scraping with fallback to mock data

    # Performance
    max_concurrent_campaigns: int = 10
    campaign_timeout_minutes: int = 15


# Global settings instance
settings = Settings()
