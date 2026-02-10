"""
DocumentGenerator Service - Core document generation functionality.

This service handles loading Word templates, caching them in memory,
and rendering them with context data using python-docxtpl.
"""

import os
from io import BytesIO
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from docxtpl import DocxTemplate
from jinja2.exceptions import TemplateError

from app.exceptions import DocumentGenerationError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class DocumentGenerator:
    """
    Core service for document generation from Word templates.

    Loads .docx templates with Jinja2 syntax, caches them in memory,
    and renders them with provided context data.

    Example:
        >>> generator = DocumentGenerator(template_dir="app/templates")
        >>> context = {"recipient_name": "Metro Transit", "region_number": 5}
        >>> document_bytes = await generator.generate("rir-package", context)
        >>> # document_bytes is a BytesIO ready for S3 upload
    """

    def __init__(self, template_dir: str, s3_storage=None):
        """
        Initialize DocumentGenerator with template directory.

        Args:
            template_dir: Path to directory containing .docx template files
            s3_storage: Optional S3Storage instance for uploading generated documents

        Raises:
            DocumentGenerationError: If template directory doesn't exist
        """
        self.template_dir = Path(template_dir)
        self.s3_storage = s3_storage
        self._template_cache: Dict[str, DocxTemplate] = {}

        # Validate template directory exists
        if not self.template_dir.exists():
            raise DocumentGenerationError(
                message=f"Template directory does not exist: {template_dir}",
                error_code="TEMPLATE_DIR_NOT_FOUND",
                details={"template_dir": str(template_dir)}
            )

        if not self.template_dir.is_dir():
            raise DocumentGenerationError(
                message=f"Template path is not a directory: {template_dir}",
                error_code="TEMPLATE_DIR_INVALID",
                details={"template_dir": str(template_dir)}
            )

        logger.info(
            f"DocumentGenerator initialized with template directory: {template_dir}",
            extra={
                "template_dir": str(template_dir),
                "s3_enabled": s3_storage is not None
            }
        )

    def _get_template_path(self, template_id: str) -> Path:
        """
        Get full path to template file.

        Args:
            template_id: Template identifier (without .docx extension)

        Returns:
            Path to template file

        Example:
            >>> path = generator._get_template_path("rir-package")
            >>> # Returns: Path("app/templates/rir-package.docx")
        """
        # Ensure .docx extension
        if not template_id.endswith(".docx"):
            template_id = f"{template_id}.docx"

        return self.template_dir / template_id

    def _load_template(self, template_id: str, correlation_id: Optional[str] = None) -> DocxTemplate:
        """
        Load template from disk with validation.

        Args:
            template_id: Template identifier
            correlation_id: Optional correlation ID for logging

        Returns:
            Loaded DocxTemplate instance

        Raises:
            DocumentGenerationError: If template doesn't exist or is invalid
        """
        template_path = self._get_template_path(template_id)

        # Check if template file exists
        if not template_path.exists():
            logger.error(
                f"Template file not found: {template_id}",
                extra={"template_id": template_id, "template_path": str(template_path), "correlation_id": correlation_id}
            )
            raise DocumentGenerationError(
                message=f"Template not found: {template_id}",
                error_code="TEMPLATE_NOT_FOUND",
                details={"template_id": template_id, "template_path": str(template_path)}
            )

        # Check if it's a file (not directory)
        if not template_path.is_file():
            logger.error(
                f"Template path is not a file: {template_id}",
                extra={"template_id": template_id, "template_path": str(template_path), "correlation_id": correlation_id}
            )
            raise DocumentGenerationError(
                message=f"Template path is not a file: {template_id}",
                error_code="TEMPLATE_INVALID",
                details={"template_id": template_id, "template_path": str(template_path)}
            )

        try:
            # Load template using python-docxtpl
            template = DocxTemplate(str(template_path))

            logger.info(
                f"Template loaded successfully: {template_id}",
                extra={"template_id": template_id, "template_path": str(template_path), "correlation_id": correlation_id}
            )

            return template

        except Exception as e:
            logger.error(
                f"Failed to load template: {template_id}",
                extra={"template_id": template_id, "error": str(e), "correlation_id": correlation_id},
                exc_info=True
            )
            raise DocumentGenerationError(
                message=f"Failed to load template: {template_id}",
                error_code="TEMPLATE_LOAD_ERROR",
                details={"template_id": template_id, "error": str(e)}
            ) from e

    def _get_cached_template(self, template_id: str, correlation_id: Optional[str] = None) -> DocxTemplate:
        """
        Get template from cache or load if not cached.

        Args:
            template_id: Template identifier
            correlation_id: Optional correlation ID for logging

        Returns:
            Cached or newly loaded DocxTemplate instance
        """
        # Check cache first
        if template_id in self._template_cache:
            logger.debug(
                f"Template retrieved from cache: {template_id}",
                extra={"template_id": template_id, "correlation_id": correlation_id}
            )
            return self._template_cache[template_id]

        # Load template and cache it
        template = self._load_template(template_id, correlation_id)
        self._template_cache[template_id] = template

        logger.info(
            f"Template cached: {template_id}",
            extra={"template_id": template_id, "cache_size": len(self._template_cache), "correlation_id": correlation_id}
        )

        return template

    async def generate(
        self,
        template_id: str,
        context: dict,
        correlation_id: Optional[str] = None
    ) -> BytesIO:
        """
        Generate document from template with provided context.

        Args:
            template_id: Template identifier (e.g., "rir-package" or "rir-package.docx")
            context: Dictionary of data to render in template
            correlation_id: Optional correlation ID for request tracing

        Returns:
            BytesIO containing the generated .docx document (in-memory)

        Raises:
            DocumentGenerationError: If generation fails

        Example:
            >>> context = {
            ...     "recipient_name": "Metro Transit",
            ...     "region_number": 5,
            ...     "review_type": "Triennial Review"
            ... }
            >>> doc = await generator.generate("rir-package", context, "abc-123")
            >>> # doc is a BytesIO ready for S3 upload or HTTP response
        """
        logger.info(
            f"Starting document generation: {template_id}",
            extra={
                "template_id": template_id,
                "context_keys": list(context.keys()),
                "correlation_id": correlation_id
            }
        )

        try:
            # Get template (from cache or load)
            template = self._get_cached_template(template_id, correlation_id)

            # Render template with context
            try:
                template.render(context)
            except TemplateError as e:
                logger.error(
                    f"Jinja2 template rendering error: {template_id}",
                    extra={
                        "template_id": template_id,
                        "error": str(e),
                        "correlation_id": correlation_id
                    },
                    exc_info=True
                )
                raise DocumentGenerationError(
                    message=f"Template rendering failed: {str(e)}",
                    error_code="TEMPLATE_RENDER_ERROR",
                    details={
                        "template_id": template_id,
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                ) from e
            except KeyError as e:
                logger.error(
                    f"Missing context variable in template: {template_id}",
                    extra={
                        "template_id": template_id,
                        "missing_key": str(e),
                        "provided_keys": list(context.keys()),
                        "correlation_id": correlation_id
                    },
                    exc_info=True
                )
                raise DocumentGenerationError(
                    message=f"Missing required context variable: {str(e)}",
                    error_code="MISSING_CONTEXT_VARIABLE",
                    details={
                        "template_id": template_id,
                        "missing_key": str(e),
                        "provided_keys": list(context.keys())
                    }
                ) from e

            # Save to BytesIO (in-memory, never write to disk)
            output = BytesIO()
            template.save(output)
            output.seek(0)  # Reset pointer to beginning for reading

            logger.info(
                f"Document generated successfully: {template_id}",
                extra={
                    "template_id": template_id,
                    "document_size_bytes": output.getbuffer().nbytes,
                    "correlation_id": correlation_id
                }
            )

            return output

        except DocumentGenerationError:
            # Re-raise our custom errors
            raise
        except Exception as e:
            # Catch any unexpected errors
            logger.error(
                f"Unexpected error during document generation: {template_id}",
                extra={
                    "template_id": template_id,
                    "error": str(e),
                    "correlation_id": correlation_id
                },
                exc_info=True
            )
            raise DocumentGenerationError(
                message=f"Unexpected error during document generation: {str(e)}",
                error_code="GENERATION_ERROR",
                details={
                    "template_id": template_id,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            ) from e

    async def generate_and_upload(
        self,
        template_id: str,
        context: dict,
        project_id: str,
        correlation_id: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Generate document and upload to S3 if S3Storage is configured.

        Args:
            template_id: Template identifier
            context: Dictionary of data to render in template
            project_id: Project identifier for S3 key naming
            correlation_id: Optional correlation ID for request tracing

        Returns:
            Tuple of (s3_key, presigned_url)

        Raises:
            DocumentGenerationError: If generation or upload fails
            ValueError: If S3Storage is not configured

        Example:
            >>> s3_key, url = await generator.generate_and_upload(
            ...     "rir-package", context, "RSKTY-12345", "abc-123"
            ... )
            >>> # Returns: ("documents/RSKTY-12345/rir-package_20250210_143200.docx", "https://...")
        """
        if self.s3_storage is None:
            raise ValueError("S3Storage not configured. Initialize DocumentGenerator with s3_storage parameter.")

        logger.info(
            f"Starting document generation and upload: {template_id}",
            extra={
                "template_id": template_id,
                "project_id": project_id,
                "correlation_id": correlation_id
            }
        )

        # Generate document
        document_bytes = await self.generate(template_id, context, correlation_id)

        # Create S3 key with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{template_id}_{timestamp}.docx"

        try:
            # Upload to S3
            s3_key = await self.s3_storage.upload_document(
                project_id=project_id,
                template_id=template_id,
                content=document_bytes,
                filename=filename
            )

            # Generate pre-signed URL for download
            presigned_url = self.s3_storage.generate_presigned_url(
                s3_key=s3_key
            )

            logger.info(
                f"Document uploaded to S3 successfully: {template_id}",
                extra={
                    "template_id": template_id,
                    "project_id": project_id,
                    "s3_key": s3_key,
                    "correlation_id": correlation_id
                }
            )

            return s3_key, presigned_url

        except Exception as e:
            logger.error(
                f"Failed to upload document to S3: {template_id}",
                extra={
                    "template_id": template_id,
                    "project_id": project_id,
                    "error": str(e),
                    "correlation_id": correlation_id
                },
                exc_info=True
            )
            raise DocumentGenerationError(
                message=f"Failed to upload document to S3: {str(e)}",
                error_code="S3_UPLOAD_ERROR",
                details={
                    "template_id": template_id,
                    "project_id": project_id,
                    "error": str(e)
                }
            ) from e

    def clear_cache(self) -> None:
        """
        Clear the template cache.

        Useful for testing or if templates are updated on disk.
        """
        cache_size = len(self._template_cache)
        self._template_cache.clear()
        logger.info(f"Template cache cleared ({cache_size} templates removed)")

    def get_cache_info(self) -> Dict[str, int]:
        """
        Get information about the template cache.

        Returns:
            Dictionary with cache statistics
        """
        return {
            "cached_templates": len(self._template_cache),
            "template_ids": list(self._template_cache.keys())
        }
