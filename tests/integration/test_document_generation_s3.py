"""
Integration tests for document generation with S3 storage.

Tests the complete end-to-end flow:
1. Generate document from template with context data
2. Upload document to S3
3. Generate pre-signed URL
4. Verify document can be downloaded from URL
5. Clean up test data from S3

This validates Epic 5.2 integration.
"""

import pytest
import requests
from pathlib import Path
from io import BytesIO

from app.services.document_generator import DocumentGenerator
from app.services.s3_storage import S3Storage
from app.services.context_builder import RIRContextBuilder


# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration


# Test Fixtures

@pytest.fixture
def template_dir():
    """Path to templates directory."""
    return str(Path(__file__).parent.parent.parent / "app" / "templates")


@pytest.fixture
def s3_storage():
    """S3Storage instance for testing."""
    return S3Storage()


@pytest.fixture
def generator_with_s3(template_dir, s3_storage):
    """DocumentGenerator instance with S3 integration."""
    return DocumentGenerator(template_dir=template_dir, s3_storage=s3_storage)


@pytest.fixture
def generator_without_s3(template_dir):
    """DocumentGenerator instance without S3 (for comparison)."""
    return DocumentGenerator(template_dir=template_dir)


@pytest.fixture
def mock_context():
    """Mock context data for RIR document generation."""
    return {
        "region_number": 5,
        "review_type": "Triennial Review",
        "recipient_name": "Metro Transit",
        "recipient_acronym": "MT",
        "recipient_city_state": "Minneapolis, MN",
        "recipient_id": "TEST-001",
        "recipient_website": "https://metrotransit.org",
        "contractor_name": "Qi Tech, LLC",
        "lead_reviewer_name": "Test Reviewer",
        "lead_reviewer_phone": "612-555-1234",
        "lead_reviewer_email": "test@qitech.com",
        "fta_program_manager_name": "Test Manager",
        "fta_program_manager_title": "General Engineer",
        "fta_program_manager_phone": "202-555-5678",
        "fta_program_manager_email": "test@dot.gov",
        "site_visit_dates": "TBD",
        "site_visit_start_date": "2025-06-15",
        "site_visit_end_date": "2025-06-17",
    }


@pytest.fixture
def test_project_id():
    """Test project ID for S3 key generation."""
    return "TEST-INTEGRATION-001"


# Integration Tests

class TestDocumentGenerationWithS3:
    """Test document generation with S3 storage integration."""

    @pytest.mark.asyncio
    async def test_generate_and_upload_to_s3(
        self,
        generator_with_s3,
        mock_context,
        test_project_id,
        s3_storage
    ):
        """
        Test complete workflow: generate document and upload to S3.

        Verifies:
        - Document is generated successfully
        - Document is uploaded to S3
        - S3 key is returned in correct format
        - Pre-signed URL is returned
        """
        # Generate and upload
        s3_key, presigned_url = await generator_with_s3.generate_and_upload(
            template_id="rir-package",
            context=mock_context,
            project_id=test_project_id,
            correlation_id="test-generate-upload"
        )

        try:
            # Verify S3 key format
            assert s3_key.startswith(f"documents/{test_project_id}/")
            assert s3_key.endswith(".docx")
            assert "rir-package_" in s3_key

            # Verify pre-signed URL
            assert presigned_url.startswith("https://")
            assert "cortap-documents-dev" in presigned_url
            assert s3_key in presigned_url
            # Accept both v2 and v4 signature formats
            assert ("X-Amz-Algorithm" in presigned_url or "Signature" in presigned_url)

            # Verify document exists in S3
            exists = await s3_storage.document_exists(s3_key)
            assert exists is True

        finally:
            # Clean up - delete test document
            await s3_storage.delete_document(s3_key)

    @pytest.mark.asyncio
    async def test_download_document_from_presigned_url(
        self,
        generator_with_s3,
        mock_context,
        test_project_id,
        s3_storage
    ):
        """
        Test that generated document can be downloaded from pre-signed URL.

        Verifies:
        - Pre-signed URL works for HTTP GET
        - Downloaded content is valid .docx file
        - Content-Type header is correct
        """
        # Generate and upload
        s3_key, presigned_url = await generator_with_s3.generate_and_upload(
            template_id="rir-package",
            context=mock_context,
            project_id=test_project_id,
            correlation_id="test-download"
        )

        try:
            # Download document using pre-signed URL
            response = requests.get(presigned_url, timeout=10)

            # Verify HTTP response
            assert response.status_code == 200
            assert response.headers["Content-Type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

            # Verify content is not empty
            content = response.content
            assert len(content) > 0

            # Verify it's a valid .docx file (starts with PK zip header)
            assert content[:2] == b"PK"

        finally:
            # Clean up
            await s3_storage.delete_document(s3_key)

    @pytest.mark.asyncio
    async def test_generate_without_s3_raises_error(
        self,
        generator_without_s3,
        mock_context,
        test_project_id
    ):
        """
        Test that generate_and_upload raises ValueError when S3Storage not configured.
        """
        with pytest.raises(ValueError, match="S3Storage not configured"):
            await generator_without_s3.generate_and_upload(
                template_id="rir-package",
                context=mock_context,
                project_id=test_project_id,
                correlation_id="test-no-s3"
            )

    @pytest.mark.asyncio
    async def test_multiple_documents_same_project(
        self,
        generator_with_s3,
        mock_context,
        test_project_id,
        s3_storage
    ):
        """
        Test uploading multiple documents for the same project.

        Verifies:
        - Multiple documents can be stored for same project_id
        - Each document gets unique timestamp in S3 key
        - Both documents can be downloaded independently
        """
        # Generate first document
        s3_key_1, presigned_url_1 = await generator_with_s3.generate_and_upload(
            template_id="rir-package",
            context=mock_context,
            project_id=test_project_id,
            correlation_id="test-multi-1"
        )

        # Small delay to ensure different timestamp
        import asyncio
        await asyncio.sleep(1)

        # Generate second document
        s3_key_2, presigned_url_2 = await generator_with_s3.generate_and_upload(
            template_id="rir-package",
            context=mock_context,
            project_id=test_project_id,
            correlation_id="test-multi-2"
        )

        try:
            # Verify keys are different (due to timestamp)
            assert s3_key_1 != s3_key_2

            # Verify both documents exist
            exists_1 = await s3_storage.document_exists(s3_key_1)
            exists_2 = await s3_storage.document_exists(s3_key_2)
            assert exists_1 is True
            assert exists_2 is True

            # Verify both URLs work
            response_1 = requests.get(presigned_url_1, timeout=10)
            response_2 = requests.get(presigned_url_2, timeout=10)
            assert response_1.status_code == 200
            assert response_2.status_code == 200

        finally:
            # Clean up both documents
            await s3_storage.delete_document(s3_key_1)
            await s3_storage.delete_document(s3_key_2)

    @pytest.mark.asyncio
    async def test_s3_key_format_and_structure(
        self,
        generator_with_s3,
        mock_context,
        test_project_id,
        s3_storage
    ):
        """
        Test S3 key follows expected naming convention.

        Expected format: documents/{project_id}/{template_id}_{timestamp}.docx
        """
        # Generate and upload
        s3_key, _ = await generator_with_s3.generate_and_upload(
            template_id="rir-package",
            context=mock_context,
            project_id=test_project_id,
            correlation_id="test-key-format"
        )

        try:
            # Parse S3 key
            parts = s3_key.split("/")
            assert len(parts) == 3
            assert parts[0] == "documents"
            assert parts[1] == test_project_id

            filename = parts[2]
            assert filename.startswith("rir-package_")
            assert filename.endswith(".docx")

            # Verify timestamp format (YYYYMMDD_HHMMSS)
            timestamp_part = filename.replace("rir-package_", "").replace(".docx", "")
            assert len(timestamp_part) == 15  # YYYYMMDD_HHMMSS
            assert timestamp_part[8] == "_"  # Underscore separator

        finally:
            # Clean up
            await s3_storage.delete_document(s3_key)


class TestBackwardsCompatibility:
    """Test that existing generate() method still works without S3."""

    @pytest.mark.asyncio
    async def test_generate_without_s3_integration(
        self,
        generator_without_s3,
        mock_context
    ):
        """
        Test that DocumentGenerator.generate() still works without S3Storage.

        Ensures backwards compatibility with existing code.
        """
        # Generate document (in-memory only, no S3)
        document_bytes = await generator_without_s3.generate(
            template_id="rir-package",
            context=mock_context,
            correlation_id="test-backwards-compat"
        )

        # Verify document was generated
        assert isinstance(document_bytes, BytesIO)
        assert document_bytes.getbuffer().nbytes > 0

        # Verify it's a valid .docx file
        content = document_bytes.read()
        assert content[:2] == b"PK"

    @pytest.mark.asyncio
    async def test_generate_with_s3_still_works(
        self,
        generator_with_s3,
        mock_context
    ):
        """
        Test that generate() method works even when S3Storage is configured.

        Verifies that S3 is optional - generate() doesn't require S3.
        """
        # Generate document (in-memory only, no S3 upload)
        document_bytes = await generator_with_s3.generate(
            template_id="rir-package",
            context=mock_context,
            correlation_id="test-generate-with-s3-configured"
        )

        # Verify document was generated
        assert isinstance(document_bytes, BytesIO)
        assert document_bytes.getbuffer().nbytes > 0
