"""
S3 Storage Service for CORTAP-RPT.

Handles document and JSON data file storage in AWS S3 GovCloud.
Provides pre-signed URL generation for secure document downloads.
"""

import json
from datetime import datetime, timedelta
from io import BytesIO
from typing import BinaryIO, Optional, Dict, Any
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError

from app.config import settings
from app.exceptions import S3StorageError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class S3Storage:
    """
    S3 storage service for CORTAP documents and data files.

    Handles:
    - Document upload (.docx files)
    - JSON data file upload/retrieval
    - Pre-signed URL generation
    - File existence checks
    """

    def __init__(self, bucket_name: Optional[str] = None, aws_region: Optional[str] = None):
        """
        Initialize S3 storage service.

        Args:
            bucket_name: S3 bucket name (defaults to settings)
            aws_region: AWS region (defaults to settings)
        """
        self.bucket_name = bucket_name or settings.s3_bucket_name
        self.aws_region = aws_region or settings.aws_region

        # Initialize boto3 S3 client
        try:
            self.s3_client = boto3.client(
                "s3",
                region_name=self.aws_region
            )
            logger.info(f"S3 client initialized for bucket: {self.bucket_name}, region: {self.aws_region}")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {str(e)}")
            raise S3StorageError(
                message=f"Failed to initialize S3 client: {str(e)}",
                error_code="S3_CLIENT_INIT_ERROR",
                details={"bucket": self.bucket_name, "region": self.aws_region}
            )

    async def upload_document(
        self,
        project_id: str,
        template_id: str,
        content: BinaryIO,
        filename: Optional[str] = None
    ) -> str:
        """
        Upload generated document to S3.

        Args:
            project_id: Riskuity project ID
            template_id: Template identifier (e.g., 'draft-audit-report')
            content: Document content as BytesIO
            filename: Optional custom filename (auto-generated if not provided)

        Returns:
            str: S3 key (path) of uploaded document

        Raises:
            S3StorageError: If upload fails
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        if not filename:
            filename = f"{template_id}_{timestamp}.docx"

        # S3 key structure: documents/{project_id}/{filename}
        s3_key = f"documents/{project_id}/{filename}"

        try:
            # Reset stream position to beginning
            if hasattr(content, 'seek'):
                content.seek(0)

            # Upload to S3 with metadata
            self.s3_client.upload_fileobj(
                content,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    "ContentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "ServerSideEncryption": "AES256",
                    "Metadata": {
                        "project-id": project_id,
                        "template-id": template_id,
                        "generated-at": timestamp
                    }
                }
            )

            logger.info(
                f"Document uploaded successfully",
                extra={
                    "project_id": project_id,
                    "template_id": template_id,
                    "s3_key": s3_key,
                    "bucket": self.bucket_name
                }
            )

            return s3_key

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(
                f"S3 upload failed: {error_code}",
                extra={
                    "project_id": project_id,
                    "s3_key": s3_key,
                    "error": str(e)
                }
            )
            raise S3StorageError(
                message=f"Failed to upload document to S3: {error_code}",
                error_code="S3_UPLOAD_ERROR",
                details={
                    "project_id": project_id,
                    "s3_key": s3_key,
                    "aws_error": error_code
                }
            )

    async def upload_json_data(
        self,
        project_id: str,
        data: Dict[str, Any],
        ttl_hours: int = 1
    ) -> str:
        """
        Upload JSON data file to S3 (for caching Riskuity data).

        Args:
            project_id: Riskuity project ID
            data: Python dict to serialize as JSON
            ttl_hours: Cache TTL in hours (default: 1 hour)

        Returns:
            str: S3 key of uploaded JSON file

        Raises:
            S3StorageError: If upload fails
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{project_id}_project-data.json"

        # S3 key structure: data/{project_id}_project-data.json
        s3_key = f"data/{filename}"

        try:
            # Add metadata to JSON
            data["_metadata"] = {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "expires_at": (datetime.utcnow() + timedelta(hours=ttl_hours)).isoformat() + "Z",
                "project_id": project_id
            }

            # Serialize to JSON
            json_content = json.dumps(data, indent=2, default=str)
            json_bytes = BytesIO(json_content.encode('utf-8'))

            # Upload to S3
            self.s3_client.upload_fileobj(
                json_bytes,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    "ContentType": "application/json",
                    "ServerSideEncryption": "AES256",
                    "Metadata": {
                        "project-id": project_id,
                        "data-type": "project-data",
                        "ttl-hours": str(ttl_hours)
                    }
                }
            )

            logger.info(
                f"JSON data uploaded successfully",
                extra={
                    "project_id": project_id,
                    "s3_key": s3_key,
                    "ttl_hours": ttl_hours
                }
            )

            return s3_key

        except Exception as e:
            logger.error(
                f"JSON upload failed",
                extra={
                    "project_id": project_id,
                    "error": str(e)
                }
            )
            raise S3StorageError(
                message=f"Failed to upload JSON data to S3: {str(e)}",
                error_code="S3_JSON_UPLOAD_ERROR",
                details={"project_id": project_id}
            )

    async def get_json_data(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached JSON data from S3.

        Args:
            project_id: Riskuity project ID

        Returns:
            Optional[Dict]: Parsed JSON data or None if not found/expired

        Raises:
            S3StorageError: If retrieval fails (other than not found)
        """
        s3_key = f"data/{project_id}_project-data.json"

        try:
            # Download from S3
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )

            # Parse JSON
            json_content = response["Body"].read().decode('utf-8')
            data = json.loads(json_content)

            # Check if expired
            metadata = data.get("_metadata", {})
            expires_at_str = metadata.get("expires_at")

            if expires_at_str:
                expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
                if datetime.utcnow() > expires_at.replace(tzinfo=None):
                    logger.info(
                        f"Cached JSON data expired",
                        extra={
                            "project_id": project_id,
                            "expires_at": expires_at_str
                        }
                    )
                    return None

            logger.info(
                f"JSON data retrieved from cache",
                extra={
                    "project_id": project_id,
                    "s3_key": s3_key
                }
            )

            return data

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")

            if error_code == "NoSuchKey":
                logger.info(f"No cached JSON data found for project {project_id}")
                return None

            logger.error(
                f"Failed to retrieve JSON data: {error_code}",
                extra={
                    "project_id": project_id,
                    "s3_key": s3_key
                }
            )
            raise S3StorageError(
                message=f"Failed to retrieve JSON data from S3: {error_code}",
                error_code="S3_JSON_RETRIEVAL_ERROR",
                details={"project_id": project_id, "aws_error": error_code}
            )

    def generate_presigned_url(
        self,
        s3_key: str,
        expires_in: int = 86400
    ) -> str:
        """
        Generate pre-signed URL for document download.

        Args:
            s3_key: S3 key (path) of the document
            expires_in: URL expiration time in seconds (default: 86400 = 24 hours)

        Returns:
            str: Pre-signed URL

        Raises:
            S3StorageError: If URL generation fails
        """
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": s3_key
                },
                ExpiresIn=expires_in
            )

            logger.info(
                f"Pre-signed URL generated",
                extra={
                    "s3_key": s3_key,
                    "expires_in": expires_in
                }
            )

            return url

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(
                f"Failed to generate pre-signed URL: {error_code}",
                extra={"s3_key": s3_key}
            )
            raise S3StorageError(
                message=f"Failed to generate pre-signed URL: {error_code}",
                error_code="S3_PRESIGNED_URL_ERROR",
                details={"s3_key": s3_key, "aws_error": error_code}
            )

    async def document_exists(self, s3_key: str) -> bool:
        """
        Check if document exists in S3.

        Args:
            s3_key: S3 key to check

        Returns:
            bool: True if exists, False otherwise
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "404":
                return False
            # Other errors (permissions, etc.) should be logged but return False
            logger.warning(
                f"Error checking document existence: {error_code}",
                extra={"s3_key": s3_key}
            )
            return False

    async def delete_document(self, s3_key: str) -> bool:
        """
        Delete document from S3.

        Args:
            s3_key: S3 key to delete

        Returns:
            bool: True if deleted successfully, False otherwise

        Raises:
            S3StorageError: If deletion fails
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )

            logger.info(
                f"Document deleted",
                extra={"s3_key": s3_key}
            )

            return True

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(
                f"Failed to delete document: {error_code}",
                extra={"s3_key": s3_key}
            )
            raise S3StorageError(
                message=f"Failed to delete document: {error_code}",
                error_code="S3_DELETE_ERROR",
                details={"s3_key": s3_key, "aws_error": error_code}
            )
