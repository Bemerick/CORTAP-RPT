"""
Document generation API endpoints.

Provides REST endpoints for generating documents from templates
and listing available templates.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict
import yaml

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from app.schemas.documents import (
    GenerateDocumentRequest,
    GenerateDocumentResponse,
    TemplatesListResponse,
    TemplateInfo,
)
from app.services.document_generator import DocumentGenerator
from app.services.s3_storage import S3Storage
from app.services.context_builder import RIRContextBuilder
from app.exceptions import DocumentGenerationError, ValidationError, CORTAPError
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Initialize services (singleton pattern)
# In production, this would be dependency-injected
_document_generator = None
_s3_storage = None


def get_s3_storage() -> S3Storage:
    """
    Get or create S3Storage instance.

    Returns:
        S3Storage: Singleton S3Storage instance
    """
    global _s3_storage
    if _s3_storage is None:
        _s3_storage = S3Storage()
    return _s3_storage


def get_document_generator() -> DocumentGenerator:
    """
    Get or create DocumentGenerator instance with S3 integration.

    Returns:
        DocumentGenerator: Singleton document generator instance
    """
    global _document_generator
    if _document_generator is None:
        # Path from this file: app/api/v1/endpoints/documents.py
        # Up 4 levels: endpoints -> v1 -> api -> app -> project_root
        # Then app/templates
        project_root = Path(__file__).parent.parent.parent.parent.parent
        template_dir = project_root / "app" / "templates"

        # Initialize with S3Storage
        s3_storage = get_s3_storage()
        _document_generator = DocumentGenerator(str(template_dir), s3_storage=s3_storage)
    return _document_generator


def load_template_metadata(template_id: str) -> Dict:
    """
    Load template metadata from YAML file.

    Args:
        template_id: Template identifier (e.g., "rir-package")

    Returns:
        dict: Template metadata

    Raises:
        HTTPException: If metadata file not found
    """
    # Path from this file: app/api/v1/endpoints/documents.py
    # Up 4 levels: endpoints -> v1 -> api -> app -> project_root
    # Then app/templates/metadata
    project_root = Path(__file__).parent.parent.parent.parent.parent
    metadata_dir = project_root / "app" / "templates" / "metadata"
    metadata_file = metadata_dir / f"{template_id}-field-definitions.yaml"

    logger.info(f"Looking for metadata file: {metadata_file}")

    if not metadata_file.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Template metadata not found: {template_id} at {metadata_file}"
        )

    with open(metadata_file, 'r') as f:
        metadata = yaml.safe_load(f)

    return metadata.get(template_id, {})


@router.post(
    "/generate-document",
    response_model=GenerateDocumentResponse,
    summary="Generate document from template",
    description="""
    Generate a document from a specified template using project data.

    **Process:**
    1. Validate request (project_id, template_id, user_id)
    2. Fetch project data (from cache or Riskuity API)
    3. Transform data to template context
    4. Render template with context
    5. Upload to S3 (future - currently returns in-memory)
    6. Return pre-signed download URL

    **Supported Templates:**
    - `rir-package`: Recipient Information Request Package

    **Future Templates:**
    - `draft-audit-report`: Draft Audit Report (Epic 1.5)
    - `final-audit-report`: Final Audit Report (Epic 2)
    """,
    responses={
        200: {
            "description": "Document generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "document_id": "550e8400-e29b-41d4-a716-446655440000",
                        "s3_key": "documents/RSKTY-12345/rir-package_20250210_143200.docx",
                        "download_url": "https://s3-us-gov-west-1.amazonaws.com/cortap-documents-dev/documents/RSKTY-12345/rir-package_20250210_143200.docx?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=...",
                        "generated_at": "2025-12-03T14:32:00Z",
                        "cached_data_used": False,
                        "warnings": []
                    }
                }
            }
        },
        400: {
            "description": "Invalid request or missing required fields",
            "content": {
                "application/json": {
                    "example": {
                        "error_code": "VALIDATION_ERROR",
                        "message": "Missing required field: contractor_name",
                        "details": {"missing_field": "contractor_name"}
                    }
                }
            }
        },
        404: {
            "description": "Template not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Template not found: invalid-template"
                    }
                }
            }
        },
        500: {
            "description": "Document generation failed",
            "content": {
                "application/json": {
                    "example": {
                        "error_code": "GENERATION_ERROR",
                        "message": "Template rendering failed",
                        "details": {}
                    }
                }
            }
        }
    },
    tags=["Documents"]
)
async def generate_document(
    request: GenerateDocumentRequest,
    http_request: Request
) -> GenerateDocumentResponse:
    """
    Generate document from template with project data.

    Args:
        request: Document generation request
        http_request: FastAPI request object for correlation_id

    Returns:
        GenerateDocumentResponse: Document generation result with download URL

    Raises:
        HTTPException: If template not found or generation fails
    """
    # Generate correlation ID for request tracing
    correlation_id = str(uuid.uuid4())

    logger.info(
        f"Document generation requested: {request.template_id} for project {request.project_id}",
        extra={
            "correlation_id": correlation_id,
            "project_id": request.project_id,
            "template_id": request.template_id,
            "user_id": request.user_id
        }
    )

    try:
        # TODO: Story 3.5.7 - Fetch project data from data service
        # For now, we'll use mock data for Story 4.5 demonstration
        # In production, this would call: data_service.get_project_data(request.project_id)

        # Load mock JSON data (temporary for Story 4.5)
        # This will be replaced with actual data service in Epic 3.5
        mock_json_data = {
            "project": {
                "region_number": 5,
                "review_type": "Triennial Review",
                "recipient_name": "Metro Transit",
                "recipient_city_state": "Minneapolis, MN",
                "recipient_id": "MN-2023-001",
                "recipient_website": "https://metrotransit.org",
                "site_visit_dates": "June 15-17, 2025",
                "site_visit_start_date": "2025-06-15",
                "site_visit_end_date": "2025-06-17"
            },
            "contractor": {
                "contractor_name": "Qi Tech, LLC",
                "lead_reviewer_name": "Jane Smith",
                "lead_reviewer_phone": "612-555-1234",
                "lead_reviewer_email": "jane.smith@qitech.com"
            },
            "fta_program_manager": {
                "fta_program_manager_name": "John Doe",
                "fta_program_manager_title": "General Engineer",
                "fta_program_manager_phone": "202-555-5678",
                "fta_program_manager_email": "john.doe@dot.gov"
            }
        }

        # Route to appropriate context builder based on template_id
        if request.template_id == "rir-package":
            context = RIRContextBuilder.build_context(mock_json_data, correlation_id)
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Template not supported: {request.template_id}. Currently only 'rir-package' is supported."
            )

        # Generate document and upload to S3
        generator = get_document_generator()
        s3_key, presigned_url = await generator.generate_and_upload(
            template_id=request.template_id,
            context=context,
            project_id=request.project_id,
            correlation_id=correlation_id
        )

        # Generate document ID and timestamp
        document_id = str(uuid.uuid4())
        generated_at = datetime.utcnow().isoformat() + "Z"

        logger.info(
            f"Document generated and uploaded successfully: {request.template_id}",
            extra={
                "correlation_id": correlation_id,
                "document_id": document_id,
                "s3_key": s3_key,
                "project_id": request.project_id
            }
        )

        return GenerateDocumentResponse(
            status="success",
            document_id=document_id,
            s3_key=s3_key,
            download_url=presigned_url,
            generated_at=generated_at,
            cached_data_used=False,  # TODO: Track cache hits in Epic 3.5
            cache_age_seconds=None,
            warnings=[]
        )

    except ValidationError as e:
        logger.error(
            f"Validation error during document generation",
            extra={
                "correlation_id": correlation_id,
                "error": str(e)
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": e.error_code,
                "message": e.message,
                "details": e.details
            }
        )

    except DocumentGenerationError as e:
        logger.error(
            f"Document generation error",
            extra={
                "correlation_id": correlation_id,
                "error": str(e)
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": e.error_code,
                "message": e.message,
                "details": e.details
            }
        )

    except Exception as e:
        logger.error(
            f"Unexpected error during document generation",
            extra={
                "correlation_id": correlation_id,
                "error": str(e)
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during document generation",
                "details": {"error": str(e)}
            }
        )


@router.get(
    "/templates",
    response_model=TemplatesListResponse,
    summary="List available document templates",
    description="""
    Get list of all available document templates with their metadata.

    Returns template IDs, names, descriptions, and required/optional fields
    for each available template.

    **Use this endpoint to:**
    - Discover available templates
    - Get required fields for a template
    - Build dynamic UI forms in React app
    """,
    responses={
        200: {
            "description": "List of available templates",
            "content": {
                "application/json": {
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
            }
        }
    },
    tags=["Documents"]
)
async def list_templates() -> TemplatesListResponse:
    """
    Get list of all available document templates.

    Returns:
        TemplatesListResponse: List of template metadata

    Raises:
        HTTPException: If template metadata cannot be loaded
    """
    logger.info("Templates list requested")

    try:
        # Load RIR template metadata
        rir_metadata = load_template_metadata("rir-package")

        templates = [
            TemplateInfo(
                id="rir-package",
                name=rir_metadata.get("name", "Recipient Information Request Package"),
                description=rir_metadata.get("description", "Information request sent to recipients before site visits"),
                required_fields=rir_metadata.get("required_fields", []),
                optional_fields=rir_metadata.get("optional_fields", [])
            )
        ]

        # TODO: Add more templates as they're implemented
        # - draft-audit-report (Epic 1.5)
        # - final-audit-report (Epic 2)

        logger.info(f"Returning {len(templates)} templates")

        return TemplatesListResponse(templates=templates)

    except Exception as e:
        logger.error(
            f"Error loading template metadata",
            extra={"error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "METADATA_LOAD_ERROR",
                "message": "Failed to load template metadata",
                "details": {"error": str(e)}
            }
        )
