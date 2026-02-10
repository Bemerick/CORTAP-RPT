"""
Template data models for CORTAP document generation.

Provides Pydantic models for type-safe template data structures,
separate models for different template types (RIR, Draft Report, etc.).
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr


class RIRTemplateData(BaseModel):
    """
    Data model for Recipient Information Request (RIR) template.

    This model represents the 16 fields required for the RIR template,
    extracted from the canonical JSON schema and transformed for rendering.

    Example:
        >>> data = RIRTemplateData(
        ...     region_number=1,
        ...     review_type="Triennial Review",
        ...     recipient_name="Metro Transit",
        ...     recipient_city_state="Minneapolis, MN",
        ...     recipient_id="1234",
        ...     site_visit_dates="June 15-17, 2025",
        ...     contractor_name="Qi Tech, LLC",
        ...     lead_reviewer_name="Jane Smith",
        ...     lead_reviewer_phone="555-1234",
        ...     lead_reviewer_email="jane@example.com",
        ...     fta_program_manager_name="John Doe",
        ...     fta_program_manager_title="General Engineer",
        ...     fta_program_manager_phone="555-5678",
        ...     fta_program_manager_email="john@dot.gov"
        ... )
    """

    # Project Information
    region_number: int = Field(
        ...,
        ge=1,
        le=10,
        description="FTA Region number (1-10)"
    )

    review_type: Literal[
        "Triennial Review",
        "State Management Review",
        "Combined Triennial and State Management Review",
        "Special Review",
        "Limited Scope Review"
    ] = Field(
        ...,
        description="Type of FTA compliance review"
    )

    recipient_name: str = Field(
        ...,
        min_length=1,
        description="Full legal name of the transit agency"
    )

    recipient_city_state: str = Field(
        ...,
        min_length=1,
        description="Recipient location in 'City, ST' format"
    )

    recipient_id: str = Field(
        ...,
        min_length=1,
        description="FTA-assigned recipient identifier"
    )

    recipient_website: Optional[str] = Field(
        default="N/A",
        description="Recipient's public website URL"
    )

    # Site Visit Information
    site_visit_dates: str = Field(
        default="TBD",
        description="Site visit date range (e.g., 'June 15-17, 2025') or 'TBD'"
    )

    # Contractor Information
    contractor_name: str = Field(
        ...,
        min_length=1,
        description="Name of the contracting firm conducting the review"
    )

    lead_reviewer_name: str = Field(
        ...,
        min_length=1,
        description="Name of the lead reviewer"
    )

    lead_reviewer_phone: str = Field(
        ...,
        min_length=1,
        description="Lead reviewer contact phone number"
    )

    lead_reviewer_email: EmailStr = Field(
        ...,
        description="Lead reviewer contact email address"
    )

    # FTA Program Manager Information
    fta_program_manager_name: str = Field(
        ...,
        min_length=1,
        description="Name of the FTA Program Manager assigned to this recipient"
    )

    fta_program_manager_title: str = Field(
        ...,
        min_length=1,
        description="Job title of the FTA Program Manager (e.g., 'General Engineer')"
    )

    fta_program_manager_phone: str = Field(
        ...,
        min_length=1,
        description="FTA Program Manager contact phone number"
    )

    fta_program_manager_email: EmailStr = Field(
        ...,
        description="FTA Program Manager contact email address"
    )

    # Optional Fields
    due_date: Optional[str] = Field(
        default=None,
        description="Response due date (if specified)"
    )

    class Config:
        """Pydantic model configuration."""
        # Allow validation to strip extra whitespace
        str_strip_whitespace = True
        # Validate on assignment
        validate_assignment = True
        # Use enum values (not names)
        use_enum_values = True

    def to_template_context(self) -> dict:
        """
        Convert model to dictionary for Jinja2 template rendering.

        Returns:
            dict: Template context with all fields
        """
        return self.dict()
