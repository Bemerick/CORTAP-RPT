"""
Unit tests for synchronous report generation endpoint.

Tests the /generate-report-sync endpoint with mocked dependencies.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app
from app.models.generate_models import GenerateReportRequest
from app.services.riskuity_client import RiskuityClient
from app.services.data_transformer import DataTransformer
from app.services.validator import JsonValidator, ValidationResult, CompletenessResult
from app.services.document_generator import DocumentGenerator
from app.services.s3_storage import S3Storage
from app.exceptions import RiskuityAPIError, ValidationError, DocumentGenerationError, S3StorageError


client = TestClient(app)


@pytest.fixture
def mock_riskuity_data():
    """Mock Riskuity project and controls data."""
    return {
        "project": {
            "id": 33,
            "name": "Test Transit Authority",
            "region": 1
        },
        "controls": [
            {
                "id": 1,
                "name": "Financial Management",
                "status": "ND"
            }
        ]
    }


@pytest.fixture
def mock_canonical_json():
    """Mock canonical JSON format."""
    return {
        "project_id": "RSKTY-0033",
        "project": {
            "region_number": 1,
            "review_type": "Triennial Review",
            "recipient_name": "Test Transit Authority",
            "recipient_id": "TTA001",
            "recipient_acronym": "TTA",
            "recipient_city_state": "Test City, TS",
            "report_date": "2026-02-12",
            "exit_conference_format": "virtual"
        },
        "contractor": {
            "company_name": "Test Contractor Inc.",
            "contractor_name": "Test Contractor Inc.",
            "lead_reviewer_name": "Jane Smith"
        },
        "fta_program_manager": {
            "fta_program_manager_name": "John Doe"
        },
        "assessments": [
            {
                "area_number": "01",
                "review_area": "Financial Management and Capacity",
                "status": "ND",
                "finding": "ND",
                "deficiency_code": None,
                "description": None
            }
        ],
        "metadata": {
            "has_deficiencies": False,
            "deficiency_count": 0,
            "deficiency_areas": [],
            "erf_count": 0,
            "fiscal_year": "FY2026",
            "review_status": "Draft"
        },
        "generated_at": "2026-02-12T10:00:00Z",
        "data_version": "1.0"
    }


class TestGenerateReportSync:
    """Test suite for synchronous report generation endpoint."""

    @patch('app.api.v1.endpoints.generate.RiskuityClient')
    @patch('app.api.v1.endpoints.generate.DataTransformer')
    @patch('app.api.v1.endpoints.generate.JsonValidator')
    @patch('app.api.v1.endpoints.generate.DocumentGenerator')
    @patch('app.api.v1.endpoints.generate.S3Storage')
    def test_successful_generation(
        self,
        mock_s3_class,
        mock_generator_class,
        mock_validator_class,
        mock_transformer_class,
        mock_riskuity_class,
        mock_riskuity_data,
        mock_canonical_json
    ):
        """Test successful report generation end-to-end."""
        # Setup mocks
        mock_riskuity = mock_riskuity_class.return_value
        mock_riskuity.get_project = AsyncMock(return_value=mock_riskuity_data["project"])
        mock_riskuity.get_project_controls = AsyncMock(return_value=mock_riskuity_data["controls"])

        mock_transformer = mock_transformer_class.return_value
        mock_transformer.transform = AsyncMock(return_value=mock_canonical_json)

        mock_validator = mock_validator_class.return_value
        mock_validator.validate_json_schema = AsyncMock(
            return_value=ValidationResult(valid=True, errors=[], warnings=[])
        )
        mock_validator.check_completeness = AsyncMock(
            return_value=CompletenessResult(
                missing_critical_fields=[],
                missing_optional_fields=[],
                data_quality_score=100,
                can_generate=True
            )
        )

        mock_generator = mock_generator_class.return_value
        mock_generator.generate = AsyncMock(return_value=b"mock document content")

        mock_s3 = mock_s3_class.return_value
        mock_s3.upload_document = AsyncMock(return_value="s3://bucket/key")
        mock_s3.generate_presigned_url = AsyncMock(return_value="https://s3.aws.com/presigned")

        # Make request
        response = client.post(
            "/api/v1/generate-report-sync",
            json={
                "project_id": 33,
                "report_type": "draft_audit_report"
            },
            headers={"Authorization": "Bearer test-token-12345"}
        )

        # Assert response
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "completed"
        assert data["project_id"] == 33
        assert data["report_type"] == "draft_audit_report"
        assert data["download_url"] == "https://s3.aws.com/presigned"
        assert "report_id" in data
        assert "expires_at" in data
        assert "generated_at" in data
        assert data["file_size_bytes"] == len(b"mock document content")

        # Check metadata
        assert data["metadata"]["recipient_name"] == "Test Transit Authority"
        assert data["metadata"]["review_type"] == "Triennial Review"
        assert data["metadata"]["review_areas"] == 1
        assert data["metadata"]["deficiency_count"] == 0
        assert data["metadata"]["generation_time_ms"] >= 0  # Can be 0 in tests

    def test_missing_authorization_header(self):
        """Test request without Authorization header returns 422."""
        response = client.post(
            "/api/v1/generate-report-sync",
            json={
                "project_id": 33,
                "report_type": "draft_audit_report"
            }
        )

        assert response.status_code == 422  # FastAPI validation error

    def test_invalid_authorization_header(self):
        """Test request with invalid Authorization header."""
        response = client.post(
            "/api/v1/generate-report-sync",
            json={
                "project_id": 33,
                "report_type": "draft_audit_report"
            },
            headers={"Authorization": "InvalidFormat"}
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["error"] == "invalid_authorization_header"

    def test_invalid_report_type(self):
        """Test request with invalid report_type."""
        response = client.post(
            "/api/v1/generate-report-sync",
            json={
                "project_id": 33,
                "report_type": "invalid_type"
            },
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 422  # Pydantic validation error
        data = response.json()
        assert "detail" in data

    def test_invalid_project_id(self):
        """Test request with invalid project_id."""
        response = client.post(
            "/api/v1/generate-report-sync",
            json={
                "project_id": -1,  # Invalid: must be > 0
                "report_type": "draft_audit_report"
            },
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 422  # Pydantic validation error

    @patch('app.api.v1.endpoints.generate.RiskuityClient')
    def test_riskuity_api_error(self, mock_riskuity_class):
        """Test handling of Riskuity API errors."""
        mock_riskuity = mock_riskuity_class.return_value
        mock_riskuity.get_project = AsyncMock(
            side_effect=RiskuityAPIError(
                message="Riskuity API unavailable",
                error_code="API_UNAVAILABLE"
            )
        )

        response = client.post(
            "/api/v1/generate-report-sync",
            json={
                "project_id": 33,
                "report_type": "draft_audit_report"
            },
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 502
        data = response.json()
        assert data["detail"]["error"] == "riskuity_api_error"

    @patch('app.api.v1.endpoints.generate.RiskuityClient')
    @patch('app.api.v1.endpoints.generate.DataTransformer')
    @patch('app.api.v1.endpoints.generate.JsonValidator')
    def test_validation_error(
        self,
        mock_validator_class,
        mock_transformer_class,
        mock_riskuity_class,
        mock_riskuity_data,
        mock_canonical_json
    ):
        """Test handling of data validation errors."""
        # Setup mocks
        mock_riskuity = mock_riskuity_class.return_value
        mock_riskuity.get_project = AsyncMock(return_value=mock_riskuity_data["project"])
        mock_riskuity.get_project_controls = AsyncMock(return_value=mock_riskuity_data["controls"])

        mock_transformer = mock_transformer_class.return_value
        mock_transformer.transform = AsyncMock(return_value=mock_canonical_json)

        mock_validator = mock_validator_class.return_value
        mock_validator.validate_json_schema = AsyncMock(
            return_value=ValidationResult(
                valid=False,
                errors=["project.recipient_name: required field missing"],
                warnings=[]
            )
        )

        response = client.post(
            "/api/v1/generate-report-sync",
            json={
                "project_id": 33,
                "report_type": "draft_audit_report"
            },
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "invalid_data"
        assert len(data["detail"]["details"]["errors"]) > 0

    @patch('app.api.v1.endpoints.generate.RiskuityClient')
    @patch('app.api.v1.endpoints.generate.DataTransformer')
    @patch('app.api.v1.endpoints.generate.JsonValidator')
    def test_missing_critical_fields(
        self,
        mock_validator_class,
        mock_transformer_class,
        mock_riskuity_class,
        mock_riskuity_data,
        mock_canonical_json
    ):
        """Test handling when critical fields are missing for template."""
        # Setup mocks
        mock_riskuity = mock_riskuity_class.return_value
        mock_riskuity.get_project = AsyncMock(return_value=mock_riskuity_data["project"])
        mock_riskuity.get_project_controls = AsyncMock(return_value=mock_riskuity_data["controls"])

        mock_transformer = mock_transformer_class.return_value
        mock_transformer.transform = AsyncMock(return_value=mock_canonical_json)

        mock_validator = mock_validator_class.return_value
        mock_validator.validate_json_schema = AsyncMock(
            return_value=ValidationResult(valid=True, errors=[], warnings=[])
        )
        mock_validator.check_completeness = AsyncMock(
            return_value=CompletenessResult(
                missing_critical_fields=["project.recipient_contact_email"],
                missing_optional_fields=[],
                data_quality_score=95,
                can_generate=False
            )
        )

        response = client.post(
            "/api/v1/generate-report-sync",
            json={
                "project_id": 33,
                "report_type": "draft_audit_report"
            },
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "missing_required_data"
        assert len(data["detail"]["details"]["missing_fields"]) > 0
        assert data["detail"]["details"]["quality_score"] == 95
