"""
CORTAP-RPT Configuration Module.

This module defines application configuration using Pydantic Settings
for environment-based configuration management.
"""

from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Supports loading from .env file in development environments.
    All settings can be overridden via environment variables.
    """

    # Riskuity API Configuration
    riskuity_api_key: str = Field(
        default="",
        description="API key for Riskuity authentication"
    )
    riskuity_base_url: str = Field(
        default="https://api.riskuity.com/v1",
        description="Base URL for Riskuity API"
    )
    riskuity_timeout: int = Field(
        default=10,
        description="Riskuity API request timeout in seconds"
    )
    riskuity_max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts for Riskuity API calls"
    )

    # AWS Configuration
    s3_bucket_name: str = Field(
        default="",
        description="S3 bucket name for document storage"
    )
    aws_region: str = Field(
        default="us-gov-west-1",
        description="AWS region for S3 and other services (GovCloud)"
    )
    s3_presigned_url_expiration: int = Field(
        default=86400,
        description="Pre-signed URL expiration time in seconds (default: 24 hours)"
    )
    s3_json_cache_ttl_hours: int = Field(
        default=1,
        description="JSON data cache TTL in hours (default: 1 hour)"
    )

    # Cache Configuration
    cache_ttl_seconds: int = Field(
        default=3600,
        description="Cache time-to-live in seconds (default: 3600 = 1 hour)"
    )
    enable_caching: bool = Field(
        default=True,
        description="Enable/disable caching (default: True)"
    )

    # Application Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    # FastAPI Configuration
    api_v1_prefix: str = Field(
        default="/api/v1",
        description="API v1 route prefix"
    )
    project_name: str = Field(
        default="CORTAP-RPT",
        description="Project name for OpenAPI docs"
    )
    environment: str = Field(
        default="development",
        description="Application environment (development, staging, production)"
    )

    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["https://riskuity.com"],
        description="Allowed CORS origins"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Uppercase aliases for convenience
    @property
    def RISKUITY_API_KEY(self) -> str:
        return self.riskuity_api_key

    @property
    def RISKUITY_API_BASE_URL(self) -> str:
        return self.riskuity_base_url


# Global settings instance
settings = Settings()
