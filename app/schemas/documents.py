"""
Request and response schemas for document generation API endpoints.

Provides Pydantic models for API request validation and response formatting.
"""

from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class GenerateDocumentRequest(BaseModel):
    """
    Request model for POST /api/v1/generate-document endpoint.

    Example:
        >>> request = GenerateDocumentRequest(
        ...     project_id="RSKTY-12345",
        ...     template_id="rir-package",
        ...     user_id="auditor@fta.gov"
        ... )
    """

    project_id: str = Field(
        ...,
        min_length=1,
        description="Project identifier from Riskuity",
        examples=["RSKTY-12345", "PRJ-2025-001"]
    )

    template_id: str = Field(
        ...,
        min_length=1,
        description="Template identifier (e.g., 'rir-package', 'draft-audit-report')",
        examples=["rir-package", "draft-audit-report"]
    )

    user_id: str = Field(
        ...,
        min_length=1,
        description="ID of user requesting document generation",
        examples=["auditor@fta.gov", "john.doe@contractor.com"]
    )

    format: Literal["docx"] = Field(
        default="docx",
        description="Output document format (currently only 'docx' supported)"
    )

    data_source: Optional[str] = Field(
        default=None,
        description="Optional S3 path to pre-cached JSON data. If not provided, system fetches latest.",
        examples=["s3://bucket/data/RSKTY-12345.json"]
    )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "project_id": "RSKTY-12345",
                "template_id": "rir-package",
                "user_id": "auditor@fta.gov",
                "format": "docx"
            }
        }


class GenerateDocumentResponse(BaseModel):
    """
    Response model for successful document generation.

    Example:
        >>> response = GenerateDocumentResponse(
        ...     status="success",
        ...     document_id="550e8400-e29b-41d4-a716-446655440000",
        ...     download_url="https://s3.amazonaws.com/...",
        ...     generated_at="2025-12-03T14:32:00Z"
        ... )
    """

    status: Literal["success"] = Field(
        default="success",
        description="Generation status"
    )

    document_id: str = Field(
        ...,
        description="Unique identifier for generated document (UUID)",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )

    s3_key: str = Field(
        ...,
        description="S3 object key where document is stored",
        examples=["documents/RSKTY-12345/rir-package_20250210_143200.docx"]
    )

    download_url: str = Field(
        ...,
        description="Pre-signed S3 URL for downloading the generated document (valid for 24 hours)",
        examples=["https://s3-us-gov-west-1.amazonaws.com/cortap-documents-dev/documents/...?X-Amz-Signature=..."]
    )

    generated_at: str = Field(
        ...,
        description="ISO 8601 timestamp when document was generated",
        examples=["2025-12-03T14:32:00Z"]
    )

    cached_data_used: bool = Field(
        default=False,
        description="Whether cached project data was used (vs. fresh Riskuity fetch)"
    )

    cache_age_seconds: Optional[int] = Field(
        default=None,
        description="Age of cached data in seconds (if cached_data_used=true)",
        examples=[1234, 3600]
    )

    warnings: List[str] = Field(
        default_factory=list,
        description="Non-critical warnings (e.g., missing optional fields)",
        examples=[["Optional field 'recipient_website' not provided, using default 'N/A'"]]
    )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "status": "success",
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "s3_key": "documents/RSKTY-12345/rir-package_20250210_143200.docx",
                "download_url": "https://s3-us-gov-west-1.amazonaws.com/cortap-documents-dev/documents/RSKTY-12345/rir-package_20250210_143200.docx?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=...",
                "generated_at": "2025-12-03T14:32:00Z",
                "cached_data_used": True,
                "cache_age_seconds": 1234,
                "warnings": []
            }
        }


class TemplateInfo(BaseModel):
    """
    Information about a single document template.

    Example:
        >>> template = TemplateInfo(
        ...     id="rir-package",
        ...     name="Recipient Information Request Package",
        ...     description="Information request sent before site visits",
        ...     required_fields=["region_number", "review_type", ...],
        ...     optional_fields=["recipient_website", "site_visit_dates"]
        ... )
    """

    id: str = Field(
        ...,
        description="Template identifier used in API requests",
        examples=["rir-package", "draft-audit-report"]
    )

    name: str = Field(
        ...,
        description="Human-readable template name",
        examples=["Recipient Information Request Package"]
    )

    description: str = Field(
        ...,
        description="Template description and purpose",
        examples=["Information request sent to recipients before site visits"]
    )

    required_fields: List[str] = Field(
        ...,
        description="List of required field names for this template",
        examples=[["region_number", "review_type", "recipient_name"]]
    )

    optional_fields: List[str] = Field(
        default_factory=list,
        description="List of optional field names",
        examples=[["recipient_website", "site_visit_dates"]]
    )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "id": "rir-package",
                "name": "Recipient Information Request Package",
                "description": "Information request sent to recipients before site visits",
                "required_fields": [
                    "region_number",
                    "review_type",
                    "recipient_name",
                    "recipient_city_state",
                    "recipient_id",
                    "lead_reviewer_name",
                    "contractor_name",
                    "lead_reviewer_phone",
                    "lead_reviewer_email",
                    "fta_program_manager_name",
                    "fta_program_manager_title",
                    "fta_program_manager_phone",
                    "fta_program_manager_email"
                ],
                "optional_fields": [
                    "recipient_website",
                    "site_visit_dates",
                    "due_date"
                ]
            }
        }


class TemplatesListResponse(BaseModel):
    """
    Response model for GET /api/v1/templates endpoint.

    Returns list of all available document templates.

    Example:
        >>> response = TemplatesListResponse(templates=[...])
    """

    templates: List[TemplateInfo] = Field(
        ...,
        description="List of available document templates"
    )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "templates": [
                    {
                        "id": "rir-package",
                        "name": "Recipient Information Request Package",
                        "description": "Information request sent to recipients before site visits",
                        "required_fields": ["region_number", "review_type", "recipient_name"],
                        "optional_fields": ["recipient_website", "site_visit_dates"]
                    }
                ]
            }
        }
