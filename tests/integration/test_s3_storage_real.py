"""
Integration tests for S3Storage service with real AWS S3.

These tests require:
- AWS credentials configured (aws configure)
- S3 bucket created (cortap-documents-dev)
- Proper IAM permissions

Run with:
    pytest tests/integration/test_s3_storage_real.py -v -m integration

Skip if no AWS access:
    pytest tests/ -v -m "not integration"
"""

import os
import json
from datetime import datetime
from io import BytesIO

import pytest
import requests

from app.services.s3_storage import S3Storage
from app.exceptions import S3StorageError


# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def s3_storage():
    """Create S3Storage instance for integration testing."""
    bucket_name = os.getenv("S3_BUCKET_NAME", "cortap-documents-dev")
    aws_region = os.getenv("AWS_REGION", "us-gov-west-1")

    return S3Storage(
        bucket_name=bucket_name,
        aws_region=aws_region
    )


@pytest.fixture
def sample_document():
    """Create a sample Word document."""
    content = b"Mock Word document content for integration testing"
    return BytesIO(content)


@pytest.fixture
def sample_json_data():
    """Create sample JSON data."""
    return {
        "project_id": "INTEGRATION-TEST-001",
        "recipient_name": "Test Transit Authority",
        "recipient_acronym": "TTA",
        "review_type": "Triennial Review",
        "region_number": 1,
        "site_visit_start_date": "2025-03-01",
        "site_visit_end_date": "2025-03-05",
        "assessments": [
            {
                "review_area": "Legal",
                "finding": "ND"
            },
            {
                "review_area": "Financial Management",
                "finding": "D",
                "deficiency_code": "FM-001"
            }
        ]
    }


class TestRealS3DocumentOperations:
    """Test document operations with real S3."""

    @pytest.mark.asyncio
    async def test_upload_and_retrieve_document(self, s3_storage, sample_document):
        """Test uploading document to real S3 and retrieving it."""
        project_id = "INTEGRATION-TEST-001"
        template_id = "test-template"

        try:
            # Upload document
            s3_key = await s3_storage.upload_document(
                project_id=project_id,
                template_id=template_id,
                content=sample_document,
                filename="integration_test_doc.docx"
            )

            # Verify S3 key format
            assert s3_key.startswith(f"documents/{project_id}/")
            assert s3_key.endswith(".docx")

            # Check if document exists
            exists = await s3_storage.document_exists(s3_key)
            assert exists is True

            # Generate pre-signed URL
            download_url = s3_storage.generate_presigned_url(s3_key, expires_in=300)
            assert download_url is not None
            assert "cortap-documents" in download_url
            assert s3_key in download_url

        finally:
            # Cleanup: delete test document
            try:
                await s3_storage.delete_document(s3_key)
            except:
                pass  # Best effort cleanup

    @pytest.mark.asyncio
    async def test_presigned_url_download(self, s3_storage, sample_document):
        """Test that pre-signed URLs actually work for downloading."""
        project_id = "INTEGRATION-TEST-002"
        test_content = b"Test document for URL download"
        sample_document = BytesIO(test_content)

        try:
            # Upload document
            s3_key = await s3_storage.upload_document(
                project_id=project_id,
                template_id="url-test",
                content=sample_document
            )

            # Generate pre-signed URL
            download_url = s3_storage.generate_presigned_url(s3_key, expires_in=300)

            # Download using the URL
            response = requests.get(download_url, timeout=10)

            assert response.status_code == 200
            assert response.content == test_content

        finally:
            # Cleanup
            try:
                await s3_storage.delete_document(s3_key)
            except:
                pass

    @pytest.mark.asyncio
    async def test_document_deletion(self, s3_storage, sample_document):
        """Test document deletion from real S3."""
        project_id = "INTEGRATION-TEST-003"

        # Upload document
        s3_key = await s3_storage.upload_document(
            project_id=project_id,
            template_id="delete-test",
            content=sample_document
        )

        # Verify it exists
        exists_before = await s3_storage.document_exists(s3_key)
        assert exists_before is True

        # Delete it
        result = await s3_storage.delete_document(s3_key)
        assert result is True

        # Verify it's gone
        exists_after = await s3_storage.document_exists(s3_key)
        assert exists_after is False

    @pytest.mark.asyncio
    async def test_nonexistent_document(self, s3_storage):
        """Test checking for document that doesn't exist."""
        fake_s3_key = "documents/FAKE-PROJECT/nonexistent.docx"

        exists = await s3_storage.document_exists(fake_s3_key)
        assert exists is False


class TestRealS3JsonCaching:
    """Test JSON data caching with real S3."""

    @pytest.mark.asyncio
    async def test_upload_and_retrieve_json(self, s3_storage):
        """Test uploading JSON data to S3 and retrieving it."""
        project_id = "JSON-TEST-001"

        # Create test data specific to this test
        test_json_data = {
            "project_id": project_id,
            "recipient_name": "Test Transit Authority",
            "recipient_acronym": "TTA",
            "review_type": "Triennial Review"
        }

        try:
            # Upload JSON data
            s3_key = await s3_storage.upload_json_data(
                project_id=project_id,
                data=test_json_data,
                ttl_hours=1
            )

            assert s3_key == f"data/{project_id}_project-data.json"

            # Retrieve cached JSON
            cached_data = await s3_storage.get_json_data(project_id)

            assert cached_data is not None
            assert cached_data["project_id"] == project_id
            assert cached_data["recipient_name"] == "Test Transit Authority"

            # Verify metadata was added
            assert "_metadata" in cached_data
            assert "generated_at" in cached_data["_metadata"]
            assert "expires_at" in cached_data["_metadata"]

        finally:
            # Cleanup
            try:
                await s3_storage.delete_document(s3_key)
            except:
                pass

    @pytest.mark.asyncio
    async def test_json_cache_miss(self, s3_storage):
        """Test retrieving JSON that doesn't exist."""
        project_id = "NONEXISTENT-PROJECT"

        cached_data = await s3_storage.get_json_data(project_id)

        # Should return None for missing data
        assert cached_data is None

    @pytest.mark.asyncio
    async def test_json_with_complex_data(self, s3_storage):
        """Test JSON caching with complex nested data structures."""
        project_id = "COMPLEX-JSON-TEST"

        complex_data = {
            "project_id": project_id,
            "nested": {
                "level1": {
                    "level2": {
                        "array": [1, 2, 3],
                        "string": "value"
                    }
                }
            },
            "assessments": [
                {"id": 1, "status": "complete"},
                {"id": 2, "status": "pending"}
            ],
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "flags": ["urgent", "reviewed"]
            }
        }

        try:
            # Upload complex JSON
            s3_key = await s3_storage.upload_json_data(
                project_id=project_id,
                data=complex_data
            )

            # Retrieve and verify structure preserved
            cached_data = await s3_storage.get_json_data(project_id)

            assert cached_data is not None
            assert cached_data["nested"]["level1"]["level2"]["array"] == [1, 2, 3]
            assert len(cached_data["assessments"]) == 2
            assert "urgent" in cached_data["metadata"]["flags"]

        finally:
            # Cleanup
            try:
                await s3_storage.delete_document(s3_key)
            except:
                pass


class TestRealS3ErrorHandling:
    """Test error handling with real S3."""

    @pytest.mark.asyncio
    async def test_invalid_bucket_name(self):
        """Test error when bucket doesn't exist."""
        invalid_storage = S3Storage(
            bucket_name="nonexistent-bucket-12345678",
            aws_region="us-gov-west-1"
        )

        sample_doc = BytesIO(b"test")

        with pytest.raises(S3StorageError) as exc_info:
            await invalid_storage.upload_document(
                project_id="TEST",
                template_id="test",
                content=sample_doc
            )

        assert exc_info.value.error_code == "S3_UPLOAD_ERROR"

    @pytest.mark.asyncio
    async def test_presigned_url_for_nonexistent_file(self, s3_storage):
        """Test generating pre-signed URL for file that doesn't exist."""
        # This should succeed (S3 doesn't validate existence for pre-signed URLs)
        url = s3_storage.generate_presigned_url(
            "documents/fake/nonexistent.docx"
        )

        assert url is not None

        # But downloading should fail with 404
        response = requests.get(url)
        assert response.status_code == 404


class TestRealS3FullWorkflow:
    """Test complete end-to-end workflows with real S3."""

    @pytest.mark.asyncio
    async def test_complete_document_generation_workflow(self, s3_storage):
        """Simulate complete document generation workflow."""
        project_id = "WORKFLOW-TEST-001"

        try:
            # Step 1: Check if JSON data exists (cache miss)
            cached_json = await s3_storage.get_json_data(project_id)
            assert cached_json is None

            # Step 2: Upload JSON data (simulating Riskuity fetch)
            project_data = {
                "project_id": project_id,
                "recipient_name": "Metro Transit",
                "assessments": [{"area": "Safety", "finding": "ND"}]
            }

            json_s3_key = await s3_storage.upload_json_data(
                project_id=project_id,
                data=project_data
            )

            # Step 3: Retrieve cached JSON
            cached_json = await s3_storage.get_json_data(project_id)
            assert cached_json is not None

            # Step 4: Generate document (simulated)
            doc_content = f"Report for {cached_json['recipient_name']}".encode()
            doc_bytes = BytesIO(doc_content)

            doc_s3_key = await s3_storage.upload_document(
                project_id=project_id,
                template_id="draft-audit-report",
                content=doc_bytes
            )

            # Step 5: Generate download URL
            download_url = s3_storage.generate_presigned_url(doc_s3_key)
            assert download_url is not None

            # Step 6: Verify download works
            response = requests.get(download_url, timeout=10)
            assert response.status_code == 200
            assert b"Metro Transit" in response.content

        finally:
            # Cleanup both files
            try:
                await s3_storage.delete_document(json_s3_key)
                await s3_storage.delete_document(doc_s3_key)
            except:
                pass


# Pytest configuration for integration tests
def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests (require real AWS)"
    )
