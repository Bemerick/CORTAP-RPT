"""
Pydantic models for document generation endpoints.

Defines request/response schemas for synchronous and asynchronous
report generation endpoints.
"""

from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class GenerateReportRequest(BaseModel):
    """
    Request model for report generation.

    Attributes:
        project_id: Riskuity project identifier
        report_type: Template identifier for report generation
    """
    project_id: int = Field(
        ...,
        description="Riskuity project identifier",
        gt=0,
        examples=[33]
    )
    report_type: str = Field(
        ...,
        description="Report template identifier",
        examples=["draft_audit_report", "recipient_information_request"]
    )

    @field_validator('report_type')
    @classmethod
    def validate_report_type(cls, v: str) -> str:
        """Validate report_type is supported."""
        valid_types = ["draft_audit_report", "recipient_information_request"]
        if v not in valid_types:
            raise ValueError(
                f"report_type must be one of {valid_types}, got '{v}'"
            )
        return v


class ReportMetadata(BaseModel):
    """
    Metadata about generated report.

    Attributes:
        recipient_name: Name of transit agency
        review_type: Type of review (Triennial Review, SMR, etc.)
        review_areas: Number of review areas assessed
        deficiency_count: Number of deficiencies found
        generation_time_ms: Time taken to generate report (milliseconds)
    """
    recipient_name: str = Field(..., description="Transit agency name")
    review_type: str = Field(..., description="Review type")
    review_areas: int = Field(..., description="Number of review areas", ge=0)
    deficiency_count: int = Field(..., description="Number of deficiencies", ge=0)
    generation_time_ms: int = Field(..., description="Generation time in ms", ge=0)


class GenerateReportResponse(BaseModel):
    """
    Response model for synchronous report generation.

    Attributes:
        status: Always "completed" for synchronous generation
        report_id: Unique report identifier
        project_id: Echo of request project_id
        report_type: Echo of request report_type
        download_url: Presigned S3 URL for document download
        expires_at: ISO 8601 timestamp when download URL expires
        generated_at: ISO 8601 timestamp when report was generated
        file_size_bytes: Size of generated document in bytes
        metadata: Report metadata for display
        correlation_id: Request correlation ID for tracing
    """
    status: str = Field(
        default="completed",
        description="Report generation status"
    )
    report_id: str = Field(..., description="Unique report identifier")
    project_id: int = Field(..., description="Riskuity project ID")
    report_type: str = Field(..., description="Report template identifier")
    download_url: str = Field(..., description="Presigned S3 download URL")
    expires_at: str = Field(..., description="URL expiration timestamp (ISO 8601)")
    generated_at: str = Field(..., description="Generation timestamp (ISO 8601)")
    file_size_bytes: int = Field(..., description="File size in bytes", ge=0)
    metadata: ReportMetadata = Field(..., description="Report metadata")
    correlation_id: str = Field(..., description="Request correlation ID")


class GenerateReportError(BaseModel):
    """
    Error response for report generation failures.

    Attributes:
        error: Machine-readable error code
        message: Human-readable error message
        details: Additional error context
        timestamp: ISO 8601 timestamp when error occurred
        correlation_id: Request correlation ID for tracing
    """
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(default=None, description="Error details")
    timestamp: str = Field(..., description="Error timestamp (ISO 8601)")
    correlation_id: str = Field(..., description="Request correlation ID")
