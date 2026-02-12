"""
Pydantic models for Data Service API endpoints.

Defines request/response schemas for project data fetching and caching.
"""

from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, Field

from app.services.validator import CompletenessResult


class FetchDataRequest(BaseModel):
    """
    Request model for fetching project data.

    Attributes:
        force_refresh: Bypass cache and fetch fresh data
        include_validation: Run schema and completeness validation
        template_id: Template to check completeness against (optional)
    """
    force_refresh: bool = Field(
        default=False,
        description="Bypass cache and fetch fresh data from Riskuity"
    )
    include_validation: bool = Field(
        default=True,
        description="Include schema and completeness validation results"
    )
    template_id: Optional[str] = Field(
        default=None,
        description="Template ID for completeness checking (e.g., 'draft-audit-report')"
    )


class CacheMetadata(BaseModel):
    """
    Cache metadata included in data service responses.

    Attributes:
        cached: Whether data was served from cache
        cache_age_seconds: Age of cached data in seconds
        expires_at: ISO timestamp when cache expires
        cache_miss_reason: Reason for cache miss (if applicable)
    """
    cached: bool = Field(..., description="True if served from cache")
    cache_age_seconds: int = Field(..., description="Age of cached data in seconds")
    expires_at: Optional[str] = Field(None, description="ISO timestamp when cache expires")
    cache_miss_reason: Optional[str] = Field(
        None,
        description="Reason for cache miss (force_refresh, caching_disabled, cache_miss_or_expired)"
    )


class ValidationSummary(BaseModel):
    """
    Summary of validation results.

    Attributes:
        schema_valid: Whether JSON passes schema validation
        error_count: Number of schema validation errors
        warning_count: Number of validation warnings
        errors: List of validation error messages (max 10)
        warnings: List of validation warnings
    """
    schema_valid: bool = Field(..., description="JSON schema validation passed")
    error_count: int = Field(..., description="Number of validation errors")
    warning_count: int = Field(..., description="Number of validation warnings")
    errors: List[str] = Field(default_factory=list, description="Schema validation errors")
    warnings: List[str] = Field(default_factory=list, description="Data quality warnings")


class DataServiceResponse(BaseModel):
    """
    Response model for data service endpoints.

    Attributes:
        project_id: Riskuity project identifier
        generated_at: ISO timestamp when data was generated
        data_version: Schema version (e.g., "1.0")
        cached: Whether data was served from cache
        cache: Cache metadata
        validation: Validation summary (if requested)
        completeness: Completeness check results (if template_id provided)
        data: Canonical JSON data
        correlation_id: Request correlation ID
    """
    project_id: str = Field(..., description="Riskuity project identifier")
    generated_at: str = Field(..., description="ISO timestamp when data was generated")
    data_version: str = Field(default="1.0", description="Canonical schema version")
    cached: bool = Field(..., description="True if served from cache")
    cache: CacheMetadata = Field(..., description="Cache metadata")
    validation: Optional[ValidationSummary] = Field(
        None,
        description="Validation results (if include_validation=true)"
    )
    completeness: Optional[CompletenessResult] = Field(
        None,
        description="Completeness check results (if template_id provided)"
    )
    data: dict = Field(..., description="Canonical JSON project data")
    correlation_id: str = Field(..., description="Request correlation ID")


class RefreshDataResponse(BaseModel):
    """
    Response model for data refresh endpoint.

    Attributes:
        status: Operation status
        message: Human-readable message
        project_id: Riskuity project identifier
        refreshed_at: ISO timestamp when refresh completed
        review_areas: Number of review areas in data
        correlation_id: Request correlation ID
    """
    status: str = Field(..., description="Operation status (success/error)")
    message: str = Field(..., description="Human-readable message")
    project_id: str = Field(..., description="Riskuity project identifier")
    refreshed_at: str = Field(..., description="ISO timestamp when refresh completed")
    review_areas: int = Field(..., description="Number of review areas in data")
    correlation_id: str = Field(..., description="Request correlation ID")


class InvalidateCacheResponse(BaseModel):
    """
    Response model for cache invalidation endpoint.

    Attributes:
        status: Operation status
        message: Human-readable message
        project_id: Riskuity project identifier
        correlation_id: Request correlation ID
    """
    status: str = Field(..., description="Operation status (success/not_found)")
    message: str = Field(..., description="Human-readable message")
    project_id: str = Field(..., description="Riskuity project identifier")
    correlation_id: str = Field(..., description="Request correlation ID")
