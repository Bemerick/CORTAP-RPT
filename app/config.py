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
        ...,
        description="API key for Riskuity authentication"
    )
    riskuity_base_url: str = Field(
        default="https://api.riskuity.com/v1",
        description="Base URL for Riskuity API"
    )

    # AWS Configuration
    s3_bucket_name: str = Field(
        ...,
        description="S3 bucket name for document storage"
    )
    aws_region: str = Field(
        default="us-east-1",
        description="AWS region for S3 and other services"
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


# Global settings instance
settings = Settings()
