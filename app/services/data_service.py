"""
Data Service - Orchestrates data fetching, transformation, and caching.

This service implements the Data Service Layer pattern, coordinating:
1. RiskuityClient - Fetch assessments from Riskuity API
2. DataTransformer - Transform to canonical JSON schema
3. S3Storage - Cache transformed JSON in S3

The cached JSON serves as the data source for all document templates,
enabling efficient multi-template generation from a single data fetch.
"""

import json
from typing import Dict, Optional
from datetime import datetime

import httpx

from app.services.riskuity_client import RiskuityClient
from app.services.data_transformer import DataTransformer
from app.services.s3_storage import S3Storage
from app.exceptions import ValidationError, RiskuityAPIError, S3StorageError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class DataService:
    """
    Data Service orchestrator for CORTAP project data.

    Responsibilities:
    - Fetch all assessment data from Riskuity (up to 644 assessments)
    - Transform to canonical JSON schema (23 review areas)
    - Cache in S3 for efficient multi-template generation
    - Serve cached data with TTL checks

    Architecture Pattern: Data Service Layer with JSON Caching
    - Separation of concerns (fetch vs. transform vs. render)
    - Multi-template efficiency (one fetch, many templates)
    - Auditability (JSON files serve as audit trail)
    - Parallel development (templates work with static JSON)

    Example:
        >>> async with httpx.AsyncClient() as http_client:
        ...     service = DataService(
        ...         riskuity_base_url="https://api.riskuity.com",
        ...         riskuity_api_key="key",
        ...         http_client=http_client
        ...     )
        ...     data = await service.get_project_data(
        ...         project_id=12345,
        ...         force_refresh=False,
        ...         correlation_id="abc-123"
        ...     )
    """

    def __init__(
        self,
        riskuity_base_url: str,
        riskuity_api_key: str,
        http_client: httpx.AsyncClient,
        s3_storage: Optional[S3Storage] = None,
        cache_ttl_seconds: int = 3600
    ):
        """
        Initialize DataService.

        Args:
            riskuity_base_url: Riskuity API base URL
            riskuity_api_key: Riskuity API key for authentication
            http_client: httpx AsyncClient for HTTP requests
            s3_storage: Optional S3Storage instance (creates new if not provided)
            cache_ttl_seconds: Cache time-to-live in seconds (default: 1 hour)
        """
        self.riskuity_client = RiskuityClient(
            base_url=riskuity_base_url,
            api_key=riskuity_api_key,
            http_client=http_client
        )
        self.transformer = DataTransformer()
        self.s3_storage = s3_storage or S3Storage()
        self.cache_ttl_seconds = cache_ttl_seconds

        logger.info(
            "DataService initialized",
            extra={
                "riskuity_base_url": riskuity_base_url,
                "cache_ttl_seconds": cache_ttl_seconds
            }
        )

    async def get_project_data(
        self,
        project_id: int,
        project_metadata: Optional[Dict] = None,
        force_refresh: bool = False,
        correlation_id: Optional[str] = None
    ) -> Dict:
        """
        Get project data - from cache if available, or fetch fresh from Riskuity.

        Workflow:
        1. Check S3 cache for existing data
        2. If cached and not expired and not force_refresh: return cached
        3. Otherwise: fetch from Riskuity, transform, cache, return

        Args:
            project_id: Riskuity project identifier (integer)
            project_metadata: Optional project metadata to override/supplement extracted data
            force_refresh: If True, bypass cache and fetch fresh data
            correlation_id: Optional correlation ID for request tracing

        Returns:
            dict: Canonical JSON schema (v1.0) with project data

        Raises:
            RiskuityAPIError: If Riskuity API calls fail
            ValidationError: If data transformation fails
            S3StorageError: If S3 operations fail
        """
        logger.info(
            f"DataService.get_project_data called for project {project_id}",
            extra={
                "project_id": project_id,
                "force_refresh": force_refresh,
                "has_metadata_override": project_metadata is not None,
                "correlation_id": correlation_id
            }
        )

        # Step 1: Check cache (unless force_refresh)
        if not force_refresh:
            cached_data = await self._get_cached_data(project_id, correlation_id)
            if cached_data:
                logger.info(
                    f"Returning cached data for project {project_id}",
                    extra={
                        "project_id": project_id,
                        "cache_age_seconds": cached_data.get("_cache_age_seconds"),
                        "correlation_id": correlation_id
                    }
                )
                return cached_data

        # Step 2: Fetch fresh data from Riskuity
        logger.info(
            f"Fetching fresh data from Riskuity for project {project_id}",
            extra={"project_id": project_id, "correlation_id": correlation_id}
        )

        canonical_data = await self.fetch_and_transform(
            project_id=project_id,
            project_metadata=project_metadata,
            correlation_id=correlation_id
        )

        # Step 3: Cache in S3
        await self._cache_data(project_id, canonical_data, correlation_id)

        return canonical_data

    async def fetch_and_transform(
        self,
        project_id: int,
        project_metadata: Optional[Dict] = None,
        correlation_id: Optional[str] = None
    ) -> Dict:
        """
        Fetch all assessments from Riskuity and transform to canonical JSON.

        This method:
        1. Calls RiskuityClient.get_all_assessment_details() (fetches up to 644 assessments)
        2. Calls DataTransformer.transform() (consolidates to 23 review areas)
        3. Returns canonical JSON schema

        Args:
            project_id: Riskuity project identifier
            project_metadata: Optional metadata to pass to transformer
            correlation_id: Optional correlation ID for request tracing

        Returns:
            dict: Canonical JSON schema (v1.0)

        Raises:
            RiskuityAPIError: If API calls fail
            ValidationError: If transformation fails
        """
        logger.info(
            f"Starting fetch and transform for project {project_id}",
            extra={"project_id": project_id, "correlation_id": correlation_id}
        )

        try:
            # Fetch all assessments with full details
            assessments = await self.riskuity_client.get_all_assessment_details(
                project_id=project_id,
                correlation_id=correlation_id,
                max_concurrent=10  # Limit concurrent API requests
            )

            logger.info(
                f"Fetched {len(assessments)} assessments from Riskuity",
                extra={
                    "project_id": project_id,
                    "assessment_count": len(assessments),
                    "correlation_id": correlation_id
                }
            )

            # Transform to canonical JSON schema
            canonical_data = self.transformer.transform(
                project_id=project_id,
                riskuity_assessments=assessments,
                project_metadata=project_metadata,
                correlation_id=correlation_id
            )

            logger.info(
                f"Successfully transformed data for project {project_id}",
                extra={
                    "project_id": project_id,
                    "review_areas": len(canonical_data.get("assessments", [])),
                    "has_deficiencies": canonical_data.get("metadata", {}).get("has_deficiencies"),
                    "correlation_id": correlation_id
                }
            )

            return canonical_data

        except RiskuityAPIError as e:
            logger.error(
                f"Riskuity API error during fetch and transform",
                extra={
                    "project_id": project_id,
                    "error": str(e),
                    "error_code": e.error_code,
                    "correlation_id": correlation_id
                },
                exc_info=True
            )
            raise

        except ValidationError as e:
            logger.error(
                f"Data validation error during transformation",
                extra={
                    "project_id": project_id,
                    "error": str(e),
                    "error_code": e.error_code,
                    "correlation_id": correlation_id
                },
                exc_info=True
            )
            raise

        except Exception as e:
            logger.error(
                f"Unexpected error during fetch and transform",
                extra={
                    "project_id": project_id,
                    "error": str(e),
                    "correlation_id": correlation_id
                },
                exc_info=True
            )
            raise ValidationError(
                message=f"Failed to fetch and transform project data: {str(e)}",
                error_code="DATA_SERVICE_ERROR",
                details={"project_id": project_id, "error": str(e)}
            ) from e

    async def _get_cached_data(
        self,
        project_id: int,
        correlation_id: Optional[str]
    ) -> Optional[Dict]:
        """
        Retrieve cached project data from S3 if available and not expired.

        Args:
            project_id: Riskuity project identifier
            correlation_id: Optional correlation ID

        Returns:
            dict: Cached data if valid, None if not found or expired
        """
        try:
            cached_data = await self.s3_storage.get_json_data(str(project_id))

            if not cached_data:
                logger.debug(
                    f"No cached data found for project {project_id}",
                    extra={"project_id": project_id, "correlation_id": correlation_id}
                )
                return None

            # Check if cache is expired (based on S3Storage's internal TTL)
            # S3Storage.get_json_data() already checks expiration
            # If it returns data, it's not expired

            # Calculate cache age for logging
            generated_at_str = cached_data.get("generated_at")
            if generated_at_str:
                generated_at = datetime.fromisoformat(generated_at_str.replace("Z", "+00:00"))
                cache_age = (datetime.utcnow() - generated_at.replace(tzinfo=None)).total_seconds()
                cached_data["_cache_age_seconds"] = int(cache_age)

            logger.info(
                f"Found valid cached data for project {project_id}",
                extra={
                    "project_id": project_id,
                    "cache_age_seconds": cached_data.get("_cache_age_seconds"),
                    "correlation_id": correlation_id
                }
            )

            return cached_data

        except S3StorageError as e:
            logger.warning(
                f"Error retrieving cached data: {str(e)}",
                extra={
                    "project_id": project_id,
                    "error": str(e),
                    "correlation_id": correlation_id
                }
            )
            return None

        except Exception as e:
            logger.warning(
                f"Unexpected error checking cache: {str(e)}",
                extra={
                    "project_id": project_id,
                    "error": str(e),
                    "correlation_id": correlation_id
                }
            )
            return None

    async def _cache_data(
        self,
        project_id: int,
        data: Dict,
        correlation_id: Optional[str]
    ) -> None:
        """
        Cache project data in S3 as JSON.

        Args:
            project_id: Riskuity project identifier
            data: Canonical JSON data to cache
            correlation_id: Optional correlation ID
        """
        try:
            await self.s3_storage.upload_json_data(
                project_id=str(project_id),
                data=data,
                ttl_seconds=self.cache_ttl_seconds
            )

            logger.info(
                f"Successfully cached data for project {project_id}",
                extra={
                    "project_id": project_id,
                    "ttl_seconds": self.cache_ttl_seconds,
                    "correlation_id": correlation_id
                }
            )

        except S3StorageError as e:
            # Log error but don't fail the request - caching is not critical
            logger.error(
                f"Failed to cache data in S3: {str(e)}",
                extra={
                    "project_id": project_id,
                    "error": str(e),
                    "correlation_id": correlation_id
                },
                exc_info=True
            )

        except Exception as e:
            logger.error(
                f"Unexpected error caching data: {str(e)}",
                extra={
                    "project_id": project_id,
                    "error": str(e),
                    "correlation_id": correlation_id
                },
                exc_info=True
            )

    async def invalidate_cache(self, project_id: int, correlation_id: Optional[str] = None) -> bool:
        """
        Invalidate (delete) cached data for a project.

        Use this when project data changes in Riskuity and cache needs refresh.

        Args:
            project_id: Riskuity project identifier
            correlation_id: Optional correlation ID

        Returns:
            bool: True if deleted, False if not found or error
        """
        try:
            s3_key = f"data/{project_id}_project-data.json"
            result = await self.s3_storage.delete_document(s3_key)

            logger.info(
                f"Cache invalidated for project {project_id}",
                extra={
                    "project_id": project_id,
                    "success": result,
                    "correlation_id": correlation_id
                }
            )

            return result

        except Exception as e:
            logger.error(
                f"Failed to invalidate cache: {str(e)}",
                extra={
                    "project_id": project_id,
                    "error": str(e),
                    "correlation_id": correlation_id
                },
                exc_info=True
            )
            return False
