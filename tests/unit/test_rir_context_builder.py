"""
Unit tests for RIR Context Builder and Template Data Model.

Tests cover:
- RIRTemplateData model validation
- RIRContextBuilder context transformation
- Date formatting logic
- Error handling for missing/invalid data
"""

import pytest
from pydantic import ValidationError

from app.models.template_data import RIRTemplateData
from app.services.context_builder import RIRContextBuilder
from app.exceptions import ValidationError as CORTAPValidationError


# Test Fixtures

@pytest.fixture
def valid_rir_data():
    """Valid RIR template data for testing."""
    return {
        "region_number": 1,
        "review_type": "Triennial Review",
        "recipient_name": "Metro Transit",
        "recipient_city_state": "Minneapolis, MN",
        "recipient_id": "1234",
        "recipient_website": "www.metrotransit.org",
        "site_visit_dates": "June 15-17, 2025",
        "contractor_name": "Qi Tech, LLC",
        "lead_reviewer_name": "Jane Smith",
        "lead_reviewer_phone": "555-1234",
        "lead_reviewer_email": "jane@qitechllc.com",
        "fta_program_manager_name": "John Doe",
        "fta_program_manager_title": "General Engineer",
        "fta_program_manager_phone": "555-5678",
        "fta_program_manager_email": "john@dot.gov"
    }


@pytest.fixture
def valid_canonical_json():
    """Valid canonical JSON data matching schema v1.0."""
    return {
        "project_id": "RSKTY-1234",
        "generated_at": "2025-11-19T10:00:00Z",
        "data_version": "1.0",
        "project": {
            "region_number": 1,
            "review_type": "Triennial Review",
            "recipient_name": "Metro Transit",
            "recipient_city_state": "Minneapolis, MN",
            "recipient_id": "1234",
            "recipient_website": "www.metrotransit.org",
            "site_visit_dates": "June 15-17, 2025",
            "site_visit_start_date": "2025-06-15",
            "site_visit_end_date": "2025-06-17",
            "report_date": "2025-08-01",
            "exit_conference_format": "virtual"
        },
        "contractor": {
            "lead_reviewer_name": "Jane Smith",
            "contractor_name": "Qi Tech, LLC",
            "lead_reviewer_phone": "555-1234",
            "lead_reviewer_email": "jane@qitechllc.com"
        },
        "fta_program_manager": {
            "fta_program_manager_name": "John Doe",
            "fta_program_manager_title": "General Engineer",
            "fta_program_manager_phone": "555-5678",
            "fta_program_manager_email": "john@dot.gov"
        },
        "assessments": [],
        "erf_items": [],
        "metadata": {
            "has_deficiencies": false,
            "deficiency_count": 0,
            "deficiency_areas": [],
            "erf_count": 0,
            "reviewed_subrecipients": false,
            "subrecipient_name": null,
            "fiscal_year": "FY2025",
            "review_status": "In Progress"
        }
    }


# RIRTemplateData Model Tests

class TestRIRTemplateDataModel:
    """Test RIRTemplateData Pydantic model validation."""

    def test_valid_data(self, valid_rir_data):
        """Test model creation with valid data."""
        model = RIRTemplateData(**valid_rir_data)

        assert model.region_number == 1
        assert model.review_type == "Triennial Review"
        assert model.recipient_name == "Metro Transit"
        assert model.fta_program_manager_title == "General Engineer"

    def test_region_number_validation_min(self, valid_rir_data):
        """Test region_number must be >= 1."""
        valid_rir_data["region_number"] = 0

        with pytest.raises(ValidationError) as exc_info:
            RIRTemplateData(**valid_rir_data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("region_number",) for e in errors)

    def test_region_number_validation_max(self, valid_rir_data):
        """Test region_number must be <= 10."""
        valid_rir_data["region_number"] = 11

        with pytest.raises(ValidationError) as exc_info:
            RIRTemplateData(**valid_rir_data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("region_number",) for e in errors)

    def test_review_type_enum_validation(self, valid_rir_data):
        """Test review_type must be one of allowed values."""
        valid_rir_data["review_type"] = "Invalid Review Type"

        with pytest.raises(ValidationError) as exc_info:
            RIRTemplateData(**valid_rir_data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("review_type",) for e in errors)

    def test_review_type_valid_values(self, valid_rir_data):
        """Test all valid review type values are accepted."""
        valid_types = [
            "Triennial Review",
            "State Management Review",
            "Combined Triennial and State Management Review",
            "Special Review",
            "Limited Scope Review"
        ]

        for review_type in valid_types:
            valid_rir_data["review_type"] = review_type
            model = RIRTemplateData(**valid_rir_data)
            assert model.review_type == review_type

    def test_email_validation_invalid(self, valid_rir_data):
        """Test email validation rejects invalid emails."""
        valid_rir_data["lead_reviewer_email"] = "not-an-email"

        with pytest.raises(ValidationError) as exc_info:
            RIRTemplateData(**valid_rir_data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("lead_reviewer_email",) for e in errors)

    def test_email_validation_valid(self, valid_rir_data):
        """Test email validation accepts valid emails."""
        valid_emails = [
            "user@example.com",
            "first.last@dot.gov",
            "reviewer_123@qitechllc.com"
        ]

        for email in valid_emails:
            valid_rir_data["lead_reviewer_email"] = email
            valid_rir_data["fta_program_manager_email"] = email
            model = RIRTemplateData(**valid_rir_data)
            assert model.lead_reviewer_email == email
            assert model.fta_program_manager_email == email

    def test_optional_fields_with_defaults(self, valid_rir_data):
        """Test optional fields use default values when not provided."""
        # Remove optional fields
        del valid_rir_data["recipient_website"]
        del valid_rir_data["site_visit_dates"]

        model = RIRTemplateData(**valid_rir_data)

        assert model.recipient_website == "N/A"
        assert model.site_visit_dates == "TBD"
        assert model.due_date is None

    def test_required_field_missing(self, valid_rir_data):
        """Test that missing required field raises validation error."""
        del valid_rir_data["recipient_name"]

        with pytest.raises(ValidationError) as exc_info:
            RIRTemplateData(**valid_rir_data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("recipient_name",) for e in errors)

    def test_to_template_context(self, valid_rir_data):
        """Test conversion to template context dictionary."""
        model = RIRTemplateData(**valid_rir_data)
        context = model.to_template_context()

        assert isinstance(context, dict)
        assert context["region_number"] == 1
        assert context["recipient_name"] == "Metro Transit"
        assert context["fta_program_manager_title"] == "General Engineer"
        assert len(context) >= 16  # All 16 fields


# RIRContextBuilder Tests

class TestRIRContextBuilder:
    """Test RIRContextBuilder context transformation."""

    def test_build_context_success(self, valid_canonical_json):
        """Test successful context building from canonical JSON."""
        context = RIRContextBuilder.build_context(valid_canonical_json)

        assert context["region_number"] == 1
        assert context["review_type"] == "Triennial Review"
        assert context["recipient_name"] == "Metro Transit"
        assert context["recipient_city_state"] == "Minneapolis, MN"
        assert context["recipient_id"] == "1234"
        assert context["contractor_name"] == "Qi Tech, LLC"
        assert context["lead_reviewer_name"] == "Jane Smith"
        assert context["fta_program_manager_name"] == "John Doe"
        assert context["fta_program_manager_title"] == "General Engineer"

    def test_build_context_with_correlation_id(self, valid_canonical_json):
        """Test context building includes correlation_id in logs."""
        correlation_id = "test-correlation-123"
        context = RIRContextBuilder.build_context(valid_canonical_json, correlation_id=correlation_id)

        assert context is not None
        assert context["recipient_name"] == "Metro Transit"

    def test_build_context_missing_required_field(self, valid_canonical_json):
        """Test context building fails with missing required field."""
        del valid_canonical_json["project"]["recipient_name"]

        with pytest.raises(CORTAPValidationError) as exc_info:
            RIRContextBuilder.build_context(valid_canonical_json)

        assert exc_info.value.error_code == "RIR_CONTEXT_VALIDATION_ERROR"

    def test_build_context_invalid_email(self, valid_canonical_json):
        """Test context building fails with invalid email."""
        valid_canonical_json["contractor"]["lead_reviewer_email"] = "not-an-email"

        with pytest.raises(CORTAPValidationError) as exc_info:
            RIRContextBuilder.build_context(valid_canonical_json)

        assert exc_info.value.error_code == "RIR_CONTEXT_VALIDATION_ERROR"

    def test_build_context_invalid_region(self, valid_canonical_json):
        """Test context building fails with invalid region number."""
        valid_canonical_json["project"]["region_number"] = 15

        with pytest.raises(CORTAPValidationError) as exc_info:
            RIRContextBuilder.build_context(valid_canonical_json)

        assert exc_info.value.error_code == "RIR_CONTEXT_VALIDATION_ERROR"

    def test_build_context_uses_default_values(self, valid_canonical_json):
        """Test context building uses default values for optional fields."""
        valid_canonical_json["project"]["recipient_website"] = None
        valid_canonical_json["project"]["site_visit_dates"] = None
        valid_canonical_json["project"]["site_visit_start_date"] = None
        valid_canonical_json["project"]["site_visit_end_date"] = None

        context = RIRContextBuilder.build_context(valid_canonical_json)

        assert context["recipient_website"] == "N/A"
        assert context["site_visit_dates"] == "TBD"


# Date Formatting Tests

class TestDateFormatting:
    """Test date range formatting logic."""

    def test_format_date_range_same_day(self):
        """Test formatting when start and end are the same day."""
        result = RIRContextBuilder.format_date_range("2025-03-10", "2025-03-10")
        assert result == "March 10, 2025"

    def test_format_date_range_same_month(self):
        """Test formatting when dates are in the same month."""
        result = RIRContextBuilder.format_date_range("2025-03-10", "2025-03-14")
        assert result == "March 10-14, 2025"

    def test_format_date_range_different_months_same_year(self):
        """Test formatting when dates are in different months, same year."""
        result = RIRContextBuilder.format_date_range("2025-03-28", "2025-04-02")
        assert result == "March 28 - April 02, 2025"

    def test_format_date_range_different_years(self):
        """Test formatting when dates are in different years."""
        result = RIRContextBuilder.format_date_range("2024-12-28", "2025-01-03")
        assert result == "December 28, 2024 - January 03, 2025"

    def test_format_date_range_no_start_date(self):
        """Test formatting returns TBD when start date is missing."""
        result = RIRContextBuilder.format_date_range(None, "2025-03-14")
        assert result == "TBD"

    def test_format_date_range_no_end_date(self):
        """Test formatting returns TBD when end date is missing."""
        result = RIRContextBuilder.format_date_range("2025-03-10", None)
        assert result == "TBD"

    def test_format_date_range_both_none(self):
        """Test formatting returns TBD when both dates are None."""
        result = RIRContextBuilder.format_date_range(None, None)
        assert result == "TBD"

    def test_format_date_range_invalid_format(self):
        """Test formatting handles invalid date format gracefully."""
        result = RIRContextBuilder.format_date_range("invalid-date", "2025-03-14")
        assert result == "TBD"

    def test_build_context_formats_dates_from_iso(self, valid_canonical_json):
        """Test context builder formats ISO dates into display format."""
        valid_canonical_json["project"]["site_visit_dates"] = None
        valid_canonical_json["project"]["site_visit_start_date"] = "2025-06-15"
        valid_canonical_json["project"]["site_visit_end_date"] = "2025-06-17"

        context = RIRContextBuilder.build_context(valid_canonical_json)

        assert context["site_visit_dates"] == "June 15-17, 2025"

    def test_build_context_preserves_formatted_dates(self, valid_canonical_json):
        """Test context builder preserves pre-formatted date strings."""
        valid_canonical_json["project"]["site_visit_dates"] = "June 15-17, 2025"

        context = RIRContextBuilder.build_context(valid_canonical_json)

        assert context["site_visit_dates"] == "June 15-17, 2025"
