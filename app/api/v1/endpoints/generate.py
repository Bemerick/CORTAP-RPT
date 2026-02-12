"""
Report Generation API Endpoints.

Synchronous report generation endpoint that fetches Riskuity data,
transforms it, generates a Word document, and returns a download URL.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Header, Query
from fastapi.responses import JSONResponse

from app.models.generate_models import (
    GenerateReportRequest,
    GenerateReportResponse,
    ReportMetadata,
    GenerateReportError
)
from app.services.riskuity_client import RiskuityClient
from app.services.data_transformer import DataTransformer
from app.services.document_generator import DocumentGenerator
from app.services.s3_storage import S3Storage
from app.services.validator import JsonValidator
from app.exceptions import (
    RiskuityAPIError,
    ValidationError,
    DocumentGenerationError,
    S3StorageError
)
from app.utils.logging import get_logger
from app.config import settings

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/generate-report-sync",
    response_model=GenerateReportResponse,
    summary="Generate Report (Synchronous)",
    description="""
    Generate CORTAP report synchronously. This endpoint blocks until
    report generation is complete (typically 30-60 seconds), then returns
    the download URL.

    **Authentication:** Requires Riskuity user token in Authorization header.

    **Execution Time:** 30-60 seconds typical

    **Use Cases:**
    - Draft Audit Reports (Triennial Review, SMR)
    - Recipient Information Request (RIR) cover letters

    **Process:**
    1. Validate request and authenticate with Riskuity
    2. Fetch project data and controls (10-20s)
    3. Transform to canonical JSON format (1-2s)
    4. Validate data completeness (1s)
    5. Generate Word document from template (10-20s)
    6. Upload to S3 and generate presigned URL (2-5s)
    7. Return download URL with 24-hour expiry
    """,
    responses={
        200: {
            "description": "Report generated successfully",
            "model": GenerateReportResponse
        },
        400: {
            "description": "Invalid request or data validation failed",
            "model": GenerateReportError
        },
        401: {
            "description": "Authentication failed",
            "model": GenerateReportError
        },
        403: {
            "description": "Insufficient permissions",
            "model": GenerateReportError
        },
        500: {
            "description": "Internal server error",
            "model": GenerateReportError
        },
        502: {
            "description": "Riskuity API error",
            "model": GenerateReportError
        },
        504: {
            "description": "Timeout - generation exceeded 2 minutes",
            "model": GenerateReportError
        }
    },
    tags=["Generation"]
)
async def generate_report_sync(
    request: GenerateReportRequest,
    authorization: str = Header(..., description="Riskuity Bearer token"),
    correlation_id: Optional[str] = Query(None, description="Optional correlation ID for tracing")
) -> GenerateReportResponse:
    """
    Generate CORTAP report synchronously.

    This endpoint performs the complete report generation workflow:
    1. Fetch data from Riskuity using user's token
    2. Transform to canonical JSON format
    3. Validate data against schema and template requirements
    4. Generate Word document
    5. Upload to S3 and return presigned download URL

    Args:
        request: Report generation request with project_id and report_type
        authorization: Riskuity Bearer token from user session
        correlation_id: Optional correlation ID for request tracing

    Returns:
        GenerateReportResponse with download URL and metadata

    Raises:
        HTTPException: On validation, authentication, or generation errors
    """
    start_time = datetime.utcnow()

    # Generate correlation ID if not provided
    if not correlation_id:
        correlation_id = f"gen-sync-{uuid.uuid4().hex[:12]}"

    # Generate report ID
    report_id = f"rpt-{start_time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"

    logger.info(
        f"Starting synchronous report generation",
        extra={
            "report_id": report_id,
            "project_id": request.project_id,
            "report_type": request.report_type,
            "correlation_id": correlation_id
        }
    )

    try:
        # Extract token from Authorization header
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "invalid_authorization_header",
                    "message": "Authorization header must start with 'Bearer '",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "correlation_id": correlation_id
                }
            )

        token = authorization.replace("Bearer ", "").strip()
        if not token:
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "missing_token",
                    "message": "Bearer token is required",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "correlation_id": correlation_id
                }
            )

        # Step 1: Initialize services
        logger.debug(
            "Initializing services",
            extra={"correlation_id": correlation_id}
        )

        riskuity_client = RiskuityClient(
            base_url=settings.riskuity_base_url,
            api_key=token  # Pass user token for authentication
        )
        transformer = DataTransformer()
        validator = JsonValidator()
        s3_storage = S3Storage()

        # Step 2: Fetch project data from Riskuity (10-20s)
        logger.info(
            f"Fetching project data from Riskuity",
            extra={
                "project_id": request.project_id,
                "correlation_id": correlation_id
            }
        )

        try:
            project_data = await riskuity_client.get_project(request.project_id)
            project_controls = await riskuity_client.get_project_controls(request.project_id)
        except RiskuityAPIError as e:
            logger.error(
                f"Riskuity API error: {str(e)}",
                extra={
                    "project_id": request.project_id,
                    "error_code": e.error_code,
                    "correlation_id": correlation_id
                },
                exc_info=True
            )
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "riskuity_api_error",
                    "message": f"Failed to fetch data from Riskuity: {str(e)}",
                    "details": {"error_code": e.error_code},
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "correlation_id": correlation_id
                }
            )

        # Step 3: Transform to canonical JSON (1-2s)
        logger.info(
            "Transforming data to canonical JSON",
            extra={"correlation_id": correlation_id}
        )

        canonical_json = await transformer.transform(
            project=project_data,
            controls=project_controls
        )

        # Step 4: Validate data (1s)
        logger.info(
            "Validating data",
            extra={"correlation_id": correlation_id}
        )

        validation_result = await validator.validate_json_schema(canonical_json)
        if not validation_result.valid:
            logger.warning(
                f"Data validation failed: {len(validation_result.errors)} errors",
                extra={
                    "errors": validation_result.errors[:5],  # First 5 errors
                    "correlation_id": correlation_id
                }
            )
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_data",
                    "message": "Project data validation failed",
                    "details": {
                        "errors": validation_result.errors[:10],  # Return first 10
                        "warnings": validation_result.warnings
                    },
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "correlation_id": correlation_id
                }
            )

        # Step 5: Check completeness for template
        logger.info(
            f"Checking data completeness for template: {request.report_type}",
            extra={"correlation_id": correlation_id}
        )

        completeness = await validator.check_completeness(
            canonical_json,
            template_id=request.report_type
        )

        if not completeness.can_generate:
            logger.warning(
                f"Cannot generate report: missing {len(completeness.missing_critical_fields)} critical fields",
                extra={
                    "missing_fields": completeness.missing_critical_fields,
                    "quality_score": completeness.data_quality_score,
                    "correlation_id": correlation_id
                }
            )
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "missing_required_data",
                    "message": f"Cannot generate report: missing {len(completeness.missing_critical_fields)} critical fields",
                    "details": {
                        "missing_fields": completeness.missing_critical_fields,
                        "template": request.report_type,
                        "quality_score": completeness.data_quality_score
                    },
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "correlation_id": correlation_id
                }
            )

        # Step 6: Generate document (10-20s)
        logger.info(
            "Generating Word document",
            extra={
                "template": request.report_type,
                "correlation_id": correlation_id
            }
        )

        try:
            generator = DocumentGenerator()
            document_bytes = await generator.generate(
                template_id=request.report_type,
                data=canonical_json
            )
        except DocumentGenerationError as e:
            logger.error(
                f"Document generation failed: {str(e)}",
                extra={
                    "template": request.report_type,
                    "error_code": e.error_code,
                    "correlation_id": correlation_id
                },
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "generation_failed",
                    "message": f"Document generation failed: {str(e)}",
                    "details": {"error_code": e.error_code},
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "correlation_id": correlation_id
                }
            )

        # Step 7: Upload to S3 (2-5s)
        logger.info(
            "Uploading document to S3",
            extra={
                "file_size_bytes": len(document_bytes),
                "correlation_id": correlation_id
            }
        )

        filename = f"{report_id}_{request.report_type}.docx"

        try:
            s3_key = await s3_storage.upload_document(
                file_content=document_bytes,
                project_id=str(request.project_id),
                template_id=request.report_type,
                filename=filename
            )
        except S3StorageError as e:
            logger.error(
                f"S3 upload failed: {str(e)}",
                extra={
                    "error_code": e.error_code,
                    "correlation_id": correlation_id
                },
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "upload_failed",
                    "message": f"Failed to upload document: {str(e)}",
                    "details": {"error_code": e.error_code},
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "correlation_id": correlation_id
                }
            )

        # Step 8: Generate presigned URL (24-hour expiry)
        logger.info(
            "Generating presigned download URL",
            extra={
                "s3_key": s3_key,
                "correlation_id": correlation_id
            }
        )

        try:
            download_url = await s3_storage.generate_presigned_url(
                s3_key=s3_key,
                expiration=86400  # 24 hours
            )
        except S3StorageError as e:
            logger.error(
                f"Failed to generate presigned URL: {str(e)}",
                extra={
                    "s3_key": s3_key,
                    "error_code": e.error_code,
                    "correlation_id": correlation_id
                },
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "presigned_url_failed",
                    "message": f"Failed to generate download URL: {str(e)}",
                    "details": {"error_code": e.error_code},
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "correlation_id": correlation_id
                }
            )

        # Calculate generation time
        end_time = datetime.utcnow()
        generation_time_ms = int((end_time - start_time).total_seconds() * 1000)

        logger.info(
            f"Report generation completed successfully",
            extra={
                "report_id": report_id,
                "generation_time_ms": generation_time_ms,
                "file_size_bytes": len(document_bytes),
                "correlation_id": correlation_id
            }
        )

        # Build response
        response = GenerateReportResponse(
            status="completed",
            report_id=report_id,
            project_id=request.project_id,
            report_type=request.report_type,
            download_url=download_url,
            expires_at=(end_time + timedelta(hours=24)).isoformat() + "Z",
            generated_at=end_time.isoformat() + "Z",
            file_size_bytes=len(document_bytes),
            metadata=ReportMetadata(
                recipient_name=canonical_json["project"]["recipient_name"],
                review_type=canonical_json["project"]["review_type"],
                review_areas=len(canonical_json["assessments"]),
                deficiency_count=canonical_json["metadata"]["deficiency_count"],
                generation_time_ms=generation_time_ms
            ),
            correlation_id=correlation_id
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise

    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(
            f"Unexpected error during report generation: {str(e)}",
            extra={
                "report_id": report_id,
                "project_id": request.project_id,
                "correlation_id": correlation_id
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_server_error",
                "message": "An unexpected error occurred during report generation",
                "details": {"report_id": report_id},
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "correlation_id": correlation_id
            }
        )
