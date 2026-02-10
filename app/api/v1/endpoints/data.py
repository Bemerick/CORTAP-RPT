"""
Project Data API endpoints.

Provides REST endpoints for fetching, caching, and managing CORTAP project data
from Riskuity. Implements the Data Service Layer pattern.
"""

import uuid
from typing import Optional
from datetime import datetime

import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.services.data_service import DataService
from app.services.s3_storage import S3Storage
from app.exceptions import RiskuityAPIError, ValidationError, S3StorageError, CORTAPError
from app.utils.logging import get_logger
from app.config import settings

logger = get_logger(__name__)

router = APIRouter()

# Singleton instances (in production, use dependency injection)
_http_client = None
_data_service = None


def get_http_client() -> httpx.AsyncClient:
    """
    Get or create httpx AsyncClient instance.

    Returns:
        httpx.AsyncClient: Singleton HTTP client for Riskuity API
    """
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=30.0)
    return _http_client


def get_data_service() -> DataService:
    """
    Get or create DataService instance.

    Returns:
        DataService: Singleton DataService instance
    """
    global _data_service
    if _data_service is None:
        # Get Riskuity configuration from environment
        riskuity_base_url = settings.RISKUITY_API_BASE_URL
        riskuity_api_key = settings.RISKUITY_API_KEY

        _data_service = DataService(
            riskuity_base_url=riskuity_base_url,
            riskuity_api_key=riskuity_api_key,
            http_client=get_http_client(),
            s3_storage=S3Storage(),
            cache_ttl_seconds=3600  # 1 hour cache
        )

    return _data_service


@router.get(
    "/projects/{project_id}/data",
    summary="Get Project Data",
    description="""
    Fetch project data from Riskuity and return in canonical JSON format.

    This endpoint:
    1. Checks S3 cache for existing data (unless force_refresh=true)
    2. If not cached: Fetches all assessments from Riskuity (up to 644)
    3. Transforms to canonical JSON schema (23 CORTAP review areas)
    4. Caches in S3 for future requests
    5. Returns canonical JSON

    The canonical JSON can be used by all document templates (RIR, Draft Report, Cover Letter).

    **Cache Behavior:**
    - Default TTL: 1 hour
    - Use `force_refresh=true` to bypass cache
    - Cache is automatically invalidated on POST /projects/{project_id}/data

    **Performance:**
    - Cached response: < 1 second
    - Fresh fetch: 30-60 seconds (644 API calls to Riskuity)
    """,
    responses={
        200: {
            "description": "Project data retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "project_id": "12345",
                        "generated_at": "2026-02-10T16:30:00Z",
                        "data_version": "1.0",
                        "project": {
                            "region_number": 5,
                            "review_type": "Triennial Review",
                            "recipient_name": "Metro Transit",
                            "recipient_id": "12345"
                        },
                        "assessments": [
                            {
                                "review_area": "Legal",
                                "finding": "ND",
                                "deficiency_code": None,
                                "description": None
                            }
                        ],
                        "metadata": {
                            "has_deficiencies": False,
                            "deficiency_count": 0,
                            "total_review_areas": 23
                        },
                        "_cache_age_seconds": 300
                    }
                }
            }
        },
        404: {
            "description": "Project not found in Riskuity"
        },
        500: {
            "description": "Riskuity API error or transformation error"
        }
    }
)
async def get_project_data(
    project_id: int,
    force_refresh: bool = Query(False, description="Bypass cache and fetch fresh data"),
    correlation_id: Optional[str] = Query(None, description="Optional correlation ID for tracing")
):
    """
    Get project data from Riskuity with caching.

    Args:
        project_id: Riskuity project identifier (integer)
        force_refresh: If true, bypass cache and fetch fresh data
        correlation_id: Optional correlation ID for request tracing

    Returns:
        JSONResponse: Canonical JSON schema with project data
    """
    # Generate correlation ID if not provided
    if not correlation_id:
        correlation_id = f"get-data-{uuid.uuid4()}"

    logger.info(
        f"GET /projects/{project_id}/data",
        extra={
            "project_id": project_id,
            "force_refresh": force_refresh,
            "correlation_id": correlation_id,
            "endpoint": "get_project_data"
        }
    )

    try:
        data_service = get_data_service()

        # Fetch project data (from cache or Riskuity)
        project_data = await data_service.get_project_data(
            project_id=project_id,
            project_metadata=None,  # TODO: Support metadata overrides via query params
            force_refresh=force_refresh,
            correlation_id=correlation_id
        )

        logger.info(
            f"Successfully retrieved project data for {project_id}",
            extra={
                "project_id": project_id,
                "review_areas": len(project_data.get("assessments", [])),
                "from_cache": not force_refresh and "_cache_age_seconds" in project_data,
                "correlation_id": correlation_id
            }
        )

        return JSONResponse(
            status_code=200,
            content=project_data
        )

    except RiskuityAPIError as e:
        logger.error(
            f"Riskuity API error for project {project_id}",
            extra={
                "project_id": project_id,
                "error": str(e),
                "error_code": e.error_code,
                "correlation_id": correlation_id
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "riskuity_api_error",
                "message": str(e),
                "error_code": e.error_code,
                "details": e.details,
                "correlation_id": correlation_id
            }
        )

    except ValidationError as e:
        logger.error(
            f"Data validation error for project {project_id}",
            extra={
                "project_id": project_id,
                "error": str(e),
                "error_code": e.error_code,
                "correlation_id": correlation_id
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "validation_error",
                "message": str(e),
                "error_code": e.error_code,
                "details": e.details,
                "correlation_id": correlation_id
            }
        )

    except Exception as e:
        logger.error(
            f"Unexpected error fetching project data for {project_id}",
            extra={
                "project_id": project_id,
                "error": str(e),
                "correlation_id": correlation_id
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_server_error",
                "message": "An unexpected error occurred",
                "correlation_id": correlation_id
            }
        )


@router.post(
    "/projects/{project_id}/data",
    summary="Refresh Project Data",
    description="""
    Force refresh of project data from Riskuity and update cache.

    This endpoint:
    1. Invalidates existing cache
    2. Fetches fresh data from Riskuity
    3. Transforms to canonical JSON
    4. Updates cache
    5. Returns refreshed data

    Use this endpoint when:
    - Project data has changed in Riskuity
    - Cache needs immediate update
    - Testing/debugging data transformations

    **Note:** This operation can take 30-60 seconds for large projects (644 assessments).
    """,
    responses={
        200: {
            "description": "Project data refreshed successfully"
        },
        500: {
            "description": "Riskuity API error or transformation error"
        }
    }
)
async def refresh_project_data(
    project_id: int,
    correlation_id: Optional[str] = Query(None, description="Optional correlation ID for tracing")
):
    """
    Force refresh project data from Riskuity.

    Args:
        project_id: Riskuity project identifier
        correlation_id: Optional correlation ID for tracing

    Returns:
        JSONResponse: Refreshed canonical JSON schema
    """
    # Generate correlation ID if not provided
    if not correlation_id:
        correlation_id = f"refresh-{uuid.uuid4()}"

    logger.info(
        f"POST /projects/{project_id}/data (refresh)",
        extra={
            "project_id": project_id,
            "correlation_id": correlation_id,
            "endpoint": "refresh_project_data"
        }
    )

    try:
        data_service = get_data_service()

        # Invalidate cache first
        await data_service.invalidate_cache(project_id, correlation_id)

        # Fetch fresh data (force_refresh=True)
        project_data = await data_service.get_project_data(
            project_id=project_id,
            force_refresh=True,
            correlation_id=correlation_id
        )

        logger.info(
            f"Successfully refreshed project data for {project_id}",
            extra={
                "project_id": project_id,
                "review_areas": len(project_data.get("assessments", [])),
                "correlation_id": correlation_id
            }
        )

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": f"Project data refreshed for project {project_id}",
                "data": project_data,
                "correlation_id": correlation_id
            }
        )

    except Exception as e:
        logger.error(
            f"Error refreshing project data for {project_id}",
            extra={
                "project_id": project_id,
                "error": str(e),
                "correlation_id": correlation_id
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "refresh_failed",
                "message": str(e),
                "correlation_id": correlation_id
            }
        )


@router.delete(
    "/projects/{project_id}/data",
    summary="Invalidate Project Data Cache",
    description="""
    Invalidate (delete) cached project data from S3.

    Use this to clear the cache without fetching new data.
    Next GET request will fetch fresh data from Riskuity.
    """,
    responses={
        200: {
            "description": "Cache invalidated successfully"
        },
        404: {
            "description": "No cached data found"
        }
    }
)
async def invalidate_project_cache(
    project_id: int,
    correlation_id: Optional[str] = Query(None, description="Optional correlation ID for tracing")
):
    """
    Invalidate cached project data.

    Args:
        project_id: Riskuity project identifier
        correlation_id: Optional correlation ID for tracing

    Returns:
        JSONResponse: Status of cache invalidation
    """
    if not correlation_id:
        correlation_id = f"invalidate-{uuid.uuid4()}"

    logger.info(
        f"DELETE /projects/{project_id}/data",
        extra={
            "project_id": project_id,
            "correlation_id": correlation_id,
            "endpoint": "invalidate_project_cache"
        }
    )

    try:
        data_service = get_data_service()
        success = await data_service.invalidate_cache(project_id, correlation_id)

        if success:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": f"Cache invalidated for project {project_id}",
                    "correlation_id": correlation_id
                }
            )
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "not_found",
                    "message": f"No cached data found for project {project_id}",
                    "correlation_id": correlation_id
                }
            )

    except Exception as e:
        logger.error(
            f"Error invalidating cache for project {project_id}",
            extra={
                "project_id": project_id,
                "error": str(e),
                "correlation_id": correlation_id
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "invalidation_failed",
                "message": str(e),
                "correlation_id": correlation_id
            }
        )
