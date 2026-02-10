"""Unit tests for S3Storage service."""

import json
from datetime import datetime, timedelta
from io import BytesIO
from unittest.mock import Mock, patch, MagicMock
import pytest
from botocore.exceptions import ClientError

from app.services.s3_storage import S3Storage
from app.exceptions import S3StorageError


@pytest.fixture
def s3_storage():
    """Create S3Storage instance with mocked boto3 client."""
    with patch('app.services.s3_storage.boto3.client') as mock_boto:
        mock_s3_client = Mock()
        mock_boto.return_value = mock_s3_client

        storage = S3Storage(
            bucket_name="test-bucket",
            aws_region="us-gov-west-1"
        )
        storage.s3_client = mock_s3_client

        yield storage, mock_s3_client


@pytest.fixture
def sample_document():
    """Create sample document content."""
    content = b"Sample Word document content"
    return BytesIO(content)


@pytest.fixture
def sample_json_data():
    """Create sample JSON data."""
    return {
        "project_id": "RSKTY-12345",
        "recipient_name": "Test Transit Authority",
        "review_type": "Triennial Review"
    }


class TestS3StorageInit:
    """Test S3Storage initialization."""

    def test_init_with_defaults(self):
        """Test initialization with default settings."""
        with patch('app.services.s3_storage.boto3.client') as mock_boto:
            with patch('app.services.s3_storage.settings') as mock_settings:
                mock_settings.s3_bucket_name = "default-bucket"
                mock_settings.aws_region = "us-gov-west-1"

                storage = S3Storage()

                assert storage.bucket_name == "default-bucket"
                assert storage.aws_region == "us-gov-west-1"
                mock_boto.assert_called_once_with("s3", region_name="us-gov-west-1")

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        with patch('app.services.s3_storage.boto3.client'):
            storage = S3Storage(
                bucket_name="custom-bucket",
                aws_region="us-gov-east-1"
            )

            assert storage.bucket_name == "custom-bucket"
            assert storage.aws_region == "us-gov-east-1"

    def test_init_boto3_error(self):
        """Test initialization failure when boto3 client creation fails."""
        with patch('app.services.s3_storage.boto3.client') as mock_boto:
            mock_boto.side_effect = Exception("AWS credentials not found")

            with pytest.raises(S3StorageError) as exc_info:
                S3Storage(bucket_name="test-bucket")

            assert "Failed to initialize S3 client" in str(exc_info.value.message)
            assert exc_info.value.error_code == "S3_CLIENT_INIT_ERROR"


class TestUploadDocument:
    """Test document upload functionality."""

    @pytest.mark.asyncio
    async def test_upload_document_success(self, s3_storage, sample_document):
        """Test successful document upload."""
        storage, mock_client = s3_storage

        result = await storage.upload_document(
            project_id="RSKTY-12345",
            template_id="draft-audit-report",
            content=sample_document,
            filename="test_report.docx"
        )

        # Verify upload was called
        mock_client.upload_fileobj.assert_called_once()
        call_args, call_kwargs = mock_client.upload_fileobj.call_args

        # Verify positional args (fileobj, bucket, key)
        assert len(call_args) == 3
        assert call_args[1] == "test-bucket"  # bucket_name
        assert "documents/RSKTY-12345/test_report.docx" in call_args[2]  # s3_key

        # Verify ExtraArgs keyword argument
        extra_args = call_kwargs["ExtraArgs"]
        assert extra_args["ContentType"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert extra_args["ServerSideEncryption"] == "AES256"
        assert extra_args["Metadata"]["project-id"] == "RSKTY-12345"
        assert extra_args["Metadata"]["template-id"] == "draft-audit-report"

        # Verify return value
        assert "documents/RSKTY-12345/test_report.docx" in result

    @pytest.mark.asyncio
    async def test_upload_document_auto_filename(self, s3_storage, sample_document):
        """Test document upload with auto-generated filename."""
        storage, mock_client = s3_storage

        result = await storage.upload_document(
            project_id="RSKTY-12345",
            template_id="draft-audit-report",
            content=sample_document
        )

        # Verify filename was auto-generated with timestamp
        assert "draft-audit-report_" in result
        assert ".docx" in result

    @pytest.mark.asyncio
    async def test_upload_document_client_error(self, s3_storage, sample_document):
        """Test document upload failure."""
        storage, mock_client = s3_storage

        error_response = {"Error": {"Code": "AccessDenied"}}
        mock_client.upload_fileobj.side_effect = ClientError(
            error_response,
            "PutObject"
        )

        with pytest.raises(S3StorageError) as exc_info:
            await storage.upload_document(
                project_id="RSKTY-12345",
                template_id="draft-audit-report",
                content=sample_document
            )

        assert exc_info.value.error_code == "S3_UPLOAD_ERROR"
        assert "AccessDenied" in str(exc_info.value.message)


class TestUploadJsonData:
    """Test JSON data upload functionality."""

    @pytest.mark.asyncio
    async def test_upload_json_data_success(self, s3_storage, sample_json_data):
        """Test successful JSON data upload."""
        storage, mock_client = s3_storage

        result = await storage.upload_json_data(
            project_id="RSKTY-12345",
            data=sample_json_data,
            ttl_hours=2
        )

        # Verify upload was called
        mock_client.upload_fileobj.assert_called_once()
        call_args, call_kwargs = mock_client.upload_fileobj.call_args

        # Verify positional args (fileobj, bucket, key)
        assert call_args[1] == "test-bucket"  # bucket_name
        assert result == "data/RSKTY-12345_project-data.json"

        # Verify metadata keyword argument
        extra_args = call_kwargs["ExtraArgs"]
        assert extra_args["ContentType"] == "application/json"
        assert extra_args["ServerSideEncryption"] == "AES256"
        assert extra_args["Metadata"]["project-id"] == "RSKTY-12345"
        assert extra_args["Metadata"]["ttl-hours"] == "2"

    @pytest.mark.asyncio
    async def test_upload_json_data_adds_metadata(self, s3_storage, sample_json_data):
        """Test that JSON data includes metadata fields."""
        storage, mock_client = s3_storage

        # Capture the uploaded content
        uploaded_content = None

        def capture_upload(fileobj, bucket, key, **kwargs):
            nonlocal uploaded_content
            uploaded_content = fileobj.read().decode('utf-8')

        mock_client.upload_fileobj.side_effect = capture_upload

        await storage.upload_json_data(
            project_id="RSKTY-12345",
            data=sample_json_data
        )

        # Parse uploaded JSON
        uploaded_data = json.loads(uploaded_content)

        assert "_metadata" in uploaded_data
        assert "generated_at" in uploaded_data["_metadata"]
        assert "expires_at" in uploaded_data["_metadata"]
        assert uploaded_data["_metadata"]["project_id"] == "RSKTY-12345"


class TestGetJsonData:
    """Test JSON data retrieval functionality."""

    @pytest.mark.asyncio
    async def test_get_json_data_success(self, s3_storage, sample_json_data):
        """Test successful JSON data retrieval."""
        storage, mock_client = s3_storage

        # Add metadata
        sample_json_data["_metadata"] = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z",
            "project_id": "RSKTY-12345"
        }

        # Mock S3 response
        mock_response = {
            "Body": MagicMock()
        }
        mock_response["Body"].read.return_value = json.dumps(sample_json_data).encode('utf-8')
        mock_client.get_object.return_value = mock_response

        result = await storage.get_json_data("RSKTY-12345")

        assert result is not None
        assert result["recipient_name"] == "Test Transit Authority"
        mock_client.get_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="data/RSKTY-12345_project-data.json"
        )

    @pytest.mark.asyncio
    async def test_get_json_data_expired(self, s3_storage, sample_json_data):
        """Test JSON data retrieval with expired cache."""
        storage, mock_client = s3_storage

        # Add expired metadata
        sample_json_data["_metadata"] = {
            "generated_at": (datetime.utcnow() - timedelta(hours=2)).isoformat() + "Z",
            "expires_at": (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z",
            "project_id": "RSKTY-12345"
        }

        # Mock S3 response
        mock_response = {
            "Body": MagicMock()
        }
        mock_response["Body"].read.return_value = json.dumps(sample_json_data).encode('utf-8')
        mock_client.get_object.return_value = mock_response

        result = await storage.get_json_data("RSKTY-12345")

        # Should return None for expired data
        assert result is None

    @pytest.mark.asyncio
    async def test_get_json_data_not_found(self, s3_storage):
        """Test JSON data retrieval when file doesn't exist."""
        storage, mock_client = s3_storage

        error_response = {"Error": {"Code": "NoSuchKey"}}
        mock_client.get_object.side_effect = ClientError(
            error_response,
            "GetObject"
        )

        result = await storage.get_json_data("RSKTY-99999")

        # Should return None for missing data
        assert result is None

    @pytest.mark.asyncio
    async def test_get_json_data_other_error(self, s3_storage):
        """Test JSON data retrieval with other S3 errors."""
        storage, mock_client = s3_storage

        error_response = {"Error": {"Code": "AccessDenied"}}
        mock_client.get_object.side_effect = ClientError(
            error_response,
            "GetObject"
        )

        with pytest.raises(S3StorageError) as exc_info:
            await storage.get_json_data("RSKTY-12345")

        assert exc_info.value.error_code == "S3_JSON_RETRIEVAL_ERROR"


class TestGeneratePresignedUrl:
    """Test pre-signed URL generation."""

    def test_generate_presigned_url_success(self, s3_storage):
        """Test successful pre-signed URL generation."""
        storage, mock_client = s3_storage

        mock_client.generate_presigned_url.return_value = "https://s3.amazonaws.com/presigned-url"

        url = storage.generate_presigned_url(
            s3_key="documents/RSKTY-12345/report.docx",
            expires_in=3600
        )

        assert url == "https://s3.amazonaws.com/presigned-url"
        mock_client.generate_presigned_url.assert_called_once_with(
            "get_object",
            Params={
                "Bucket": "test-bucket",
                "Key": "documents/RSKTY-12345/report.docx"
            },
            ExpiresIn=3600
        )

    def test_generate_presigned_url_default_expiration(self, s3_storage):
        """Test pre-signed URL generation with default expiration."""
        storage, mock_client = s3_storage

        mock_client.generate_presigned_url.return_value = "https://s3.amazonaws.com/presigned-url"

        storage.generate_presigned_url("documents/test.docx")

        call_args = mock_client.generate_presigned_url.call_args
        assert call_args[1]["ExpiresIn"] == 86400  # 24 hours

    def test_generate_presigned_url_error(self, s3_storage):
        """Test pre-signed URL generation failure."""
        storage, mock_client = s3_storage

        error_response = {"Error": {"Code": "NoSuchKey"}}
        mock_client.generate_presigned_url.side_effect = ClientError(
            error_response,
            "GeneratePresignedUrl"
        )

        with pytest.raises(S3StorageError) as exc_info:
            storage.generate_presigned_url("documents/nonexistent.docx")

        assert exc_info.value.error_code == "S3_PRESIGNED_URL_ERROR"


class TestDocumentExists:
    """Test document existence check."""

    @pytest.mark.asyncio
    async def test_document_exists_true(self, s3_storage):
        """Test document exists check returns True."""
        storage, mock_client = s3_storage

        mock_client.head_object.return_value = {"ContentLength": 1024}

        result = await storage.document_exists("documents/test.docx")

        assert result is True
        mock_client.head_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="documents/test.docx"
        )

    @pytest.mark.asyncio
    async def test_document_exists_false(self, s3_storage):
        """Test document exists check returns False for 404."""
        storage, mock_client = s3_storage

        error_response = {"Error": {"Code": "404"}}
        mock_client.head_object.side_effect = ClientError(
            error_response,
            "HeadObject"
        )

        result = await storage.document_exists("documents/nonexistent.docx")

        assert result is False

    @pytest.mark.asyncio
    async def test_document_exists_other_error(self, s3_storage):
        """Test document exists check handles other errors gracefully."""
        storage, mock_client = s3_storage

        error_response = {"Error": {"Code": "AccessDenied"}}
        mock_client.head_object.side_effect = ClientError(
            error_response,
            "HeadObject"
        )

        result = await storage.document_exists("documents/test.docx")

        # Should return False for other errors (logged as warning)
        assert result is False


class TestDeleteDocument:
    """Test document deletion."""

    @pytest.mark.asyncio
    async def test_delete_document_success(self, s3_storage):
        """Test successful document deletion."""
        storage, mock_client = s3_storage

        result = await storage.delete_document("documents/test.docx")

        assert result is True
        mock_client.delete_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="documents/test.docx"
        )

    @pytest.mark.asyncio
    async def test_delete_document_error(self, s3_storage):
        """Test document deletion failure."""
        storage, mock_client = s3_storage

        error_response = {"Error": {"Code": "AccessDenied"}}
        mock_client.delete_object.side_effect = ClientError(
            error_response,
            "DeleteObject"
        )

        with pytest.raises(S3StorageError) as exc_info:
            await storage.delete_document("documents/test.docx")

        assert exc_info.value.error_code == "S3_DELETE_ERROR"
