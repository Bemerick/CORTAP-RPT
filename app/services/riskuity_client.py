"""
Riskuity API Client - Async HTTP client for Riskuity compliance data.

Provides async methods to fetch CORTAP project data from 4 Riskuity API endpoints
with automatic retry logic, exponential backoff, and comprehensive error handling.
"""

import asyncio
from typing import List, Dict, Optional
from datetime import datetime

import httpx

from app.exceptions import RiskuityAPIError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class RiskuityClient:
    """
    Async HTTP client for Riskuity API with retry logic.

    Features:
    - 4 API endpoints: project, assessments, surveys, risks/ERF
    - Exponential backoff retry (1s, 2s, 4s)
    - Maximum 3 retries per request
    - 10-second timeout per request
    - Bearer token authentication
    - Rate limiting handling (429 status)
    - Comprehensive logging with correlation_id

    Example:
        >>> async with httpx.AsyncClient() as http_client:
        ...     client = RiskuityClient(
        ...         base_url="https://api.riskuity.com/api/v1",
        ...         api_key="your-api-key",
        ...         http_client=http_client
        ...     )
        ...     project = await client.get_project("RSKTY-12345", correlation_id="abc-123")
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        http_client: httpx.AsyncClient,
        max_retries: int = 3,
        timeout: float = 10.0
    ):
        """
        Initialize Riskuity API client.

        Args:
            base_url: Riskuity API base URL (e.g., "https://api.riskuity.com/api/v1")
            api_key: Riskuity API key for Bearer authentication
            http_client: httpx AsyncClient instance for HTTP requests
            max_retries: Maximum retry attempts (default: 3)
            timeout: Request timeout in seconds (default: 10.0)
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.http_client = http_client
        self.max_retries = max_retries
        self.timeout = timeout

        logger.info(
            "RiskuityClient initialized",
            extra={
                "base_url": self.base_url,
                "max_retries": self.max_retries,
                "timeout": self.timeout
            }
        )

    async def _request_with_retry(
        self,
        method: str,
        endpoint: str,
        correlation_id: Optional[str] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """
        Make HTTP request with exponential backoff retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path (without base_url)
            correlation_id: Optional correlation ID for request tracing
            params: Optional query parameters (for GET requests)

        Returns:
            dict: Parsed JSON response

        Raises:
            RiskuityAPIError: If request fails after all retries
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }

        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(
                    f"Riskuity API request attempt {attempt}/{self.max_retries}",
                    extra={
                        "method": method,
                        "url": url,
                        "attempt": attempt,
                        "correlation_id": correlation_id
                    }
                )

                response = await self.http_client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    timeout=self.timeout
                )

                # Handle rate limiting (429)
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 2 ** attempt))
                    logger.warning(
                        f"Rate limited by Riskuity API, retrying after {retry_after}s",
                        extra={
                            "url": url,
                            "attempt": attempt,
                            "retry_after": retry_after,
                            "correlation_id": correlation_id
                        }
                    )
                    await asyncio.sleep(retry_after)
                    continue

                # Handle transient errors (500, 503)
                if response.status_code in [500, 503]:
                    if attempt < self.max_retries:
                        backoff_delay = 2 ** (attempt - 1)  # 1s, 2s, 4s
                        logger.warning(
                            f"Transient error {response.status_code}, retrying after {backoff_delay}s",
                            extra={
                                "url": url,
                                "status_code": response.status_code,
                                "attempt": attempt,
                                "backoff_delay": backoff_delay,
                                "correlation_id": correlation_id
                            }
                        )
                        await asyncio.sleep(backoff_delay)
                        continue
                    else:
                        raise RiskuityAPIError(
                            message=f"Riskuity API returned {response.status_code} after {self.max_retries} retries",
                            error_code="RISKUITY_SERVER_ERROR",
                            details={
                                "url": url,
                                "status_code": response.status_code,
                                "attempts": attempt
                            }
                        )

                # Handle other error status codes
                if response.status_code >= 400:
                    error_message = f"Riskuity API error: {response.status_code}"
                    try:
                        error_body = response.json()
                        error_message = error_body.get("message", error_message)
                    except:
                        pass

                    logger.error(
                        f"Riskuity API request failed: {response.status_code}",
                        extra={
                            "url": url,
                            "status_code": response.status_code,
                            "correlation_id": correlation_id
                        }
                    )

                    raise RiskuityAPIError(
                        message=error_message,
                        error_code=f"RISKUITY_HTTP_{response.status_code}",
                        details={
                            "url": url,
                            "status_code": response.status_code
                        }
                    )

                # Success - parse JSON response
                try:
                    data = response.json()
                except Exception as e:
                    logger.error(
                        "Failed to parse Riskuity API response as JSON",
                        extra={
                            "url": url,
                            "error": str(e),
                            "correlation_id": correlation_id
                        },
                        exc_info=True
                    )
                    raise RiskuityAPIError(
                        message="Invalid JSON response from Riskuity API",
                        error_code="RISKUITY_INVALID_JSON",
                        details={"url": url, "error": str(e)}
                    )

                logger.info(
                    f"Riskuity API request successful",
                    extra={
                        "url": url,
                        "status_code": response.status_code,
                        "attempt": attempt,
                        "correlation_id": correlation_id
                    }
                )

                return data

            except httpx.TimeoutException as e:
                if attempt < self.max_retries:
                    backoff_delay = 2 ** (attempt - 1)
                    logger.warning(
                        f"Request timeout, retrying after {backoff_delay}s",
                        extra={
                            "url": url,
                            "attempt": attempt,
                            "backoff_delay": backoff_delay,
                            "correlation_id": correlation_id
                        }
                    )
                    await asyncio.sleep(backoff_delay)
                    continue
                else:
                    logger.error(
                        f"Request timeout after {self.max_retries} retries",
                        extra={
                            "url": url,
                            "attempts": attempt,
                            "correlation_id": correlation_id
                        },
                        exc_info=True
                    )
                    raise RiskuityAPIError(
                        message=f"Riskuity API request timed out after {self.max_retries} retries",
                        error_code="RISKUITY_TIMEOUT",
                        details={"url": url, "timeout": self.timeout, "attempts": attempt}
                    ) from e

            except httpx.RequestError as e:
                if attempt < self.max_retries:
                    backoff_delay = 2 ** (attempt - 1)
                    logger.warning(
                        f"Request error: {str(e)}, retrying after {backoff_delay}s",
                        extra={
                            "url": url,
                            "error": str(e),
                            "attempt": attempt,
                            "backoff_delay": backoff_delay,
                            "correlation_id": correlation_id
                        }
                    )
                    await asyncio.sleep(backoff_delay)
                    continue
                else:
                    logger.error(
                        f"Request failed after {self.max_retries} retries",
                        extra={
                            "url": url,
                            "error": str(e),
                            "attempts": attempt,
                            "correlation_id": correlation_id
                        },
                        exc_info=True
                    )
                    raise RiskuityAPIError(
                        message=f"Failed to connect to Riskuity API: {str(e)}",
                        error_code="RISKUITY_CONNECTION_ERROR",
                        details={"url": url, "error": str(e), "attempts": attempt}
                    ) from e

        # Should never reach here, but just in case
        raise RiskuityAPIError(
            message="Unexpected error in retry loop",
            error_code="RISKUITY_UNEXPECTED_ERROR",
            details={"url": url}
        )

    async def get_assessment_by_id(self, assessment_id: int, correlation_id: Optional[str] = None) -> Dict:
        """
        Fetch detailed data for a specific assessment.

        Actual Riskuity API Endpoint: GET /assessments/{id}

        Use this to get full details for each assessment, including all fields
        needed for report generation (findings, corrective actions, etc.)

        Args:
            assessment_id: Riskuity assessment identifier (integer)
            correlation_id: Optional correlation ID for request tracing

        Returns:
            dict: Complete assessment data

        Raises:
            RiskuityAPIError: If API request fails

        Example response:
            {
                "id": 123,
                "name": "Legal Compliance",
                "status": "complete",
                "finding": "D",
                "deficiency_description": "...",
                "corrective_action": "...",
                ...
            }
        """
        endpoint = f"/assessments/{assessment_id}"
        logger.info(
            f"Fetching assessment {assessment_id} from Riskuity",
            extra={"assessment_id": assessment_id, "correlation_id": correlation_id}
        )
        return await self._request_with_retry("GET", endpoint, correlation_id)

    async def get_assessments(self, project_id: int, correlation_id: Optional[str] = None) -> List[Dict]:
        """
        Fetch assessment findings for project.

        Actual Riskuity API Endpoint: GET /assessments/?project_id={project_id}

        Args:
            project_id: Riskuity project identifier (integer)
            correlation_id: Optional correlation ID for request tracing

        Returns:
            list: Array of assessment findings

        Raises:
            RiskuityAPIError: If API request fails

        Example response:
            [
                {
                    "id": 123,
                    "name": "Legal Compliance",
                    "status": "complete",
                    ...
                },
                ...
            ]
        """
        endpoint = f"/assessments/?project_id={project_id}"
        logger.info(
            f"Fetching assessments from Riskuity",
            extra={"project_id": project_id, "correlation_id": correlation_id}
        )
        data = await self._request_with_retry("GET", endpoint, correlation_id)
        # API returns list of assessments
        if isinstance(data, list):
            return data
        # Might be wrapped in a response object
        if isinstance(data, dict) and "assessments" in data:
            return data["assessments"]
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return data if isinstance(data, list) else []

    async def get_all_assessment_details(
        self,
        project_id: int,
        correlation_id: Optional[str] = None,
        max_concurrent: int = 10
    ) -> List[Dict]:
        """
        Fetch all assessments for a project with full details.

        This is a convenience method that:
        1. Calls GET /assessments/?project_id={id} to get list of assessment IDs
        2. Calls GET /assessments/{id} for each assessment to get full details
        3. Returns array of complete assessment data

        For projects with 644 assessments, this will make 645 API calls total.
        Requests are made concurrently (max_concurrent at a time) for performance.

        Args:
            project_id: Riskuity project identifier (integer)
            correlation_id: Optional correlation ID for request tracing
            max_concurrent: Maximum concurrent API requests (default: 10)

        Returns:
            list: Array of complete assessment data for all project assessments

        Raises:
            RiskuityAPIError: If API requests fail
        """
        logger.info(
            f"Fetching all assessment details for project {project_id}",
            extra={"project_id": project_id, "max_concurrent": max_concurrent, "correlation_id": correlation_id}
        )

        # Step 1: Get list of assessments
        assessments_summary = await self.get_assessments(project_id, correlation_id)
        assessment_ids = [a.get("id") for a in assessments_summary if a.get("id")]

        logger.info(
            f"Found {len(assessment_ids)} assessments for project {project_id}",
            extra={"project_id": project_id, "assessment_count": len(assessment_ids), "correlation_id": correlation_id}
        )

        # Step 2: Fetch full details for each assessment (with concurrency limit)
        detailed_assessments = []

        # Process in batches to limit concurrent requests
        for i in range(0, len(assessment_ids), max_concurrent):
            batch = assessment_ids[i:i + max_concurrent]
            batch_tasks = [
                self.get_assessment_by_id(assessment_id, correlation_id)
                for assessment_id in batch
            ]

            # Wait for batch to complete
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            # Filter out any errors and collect successful results
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(
                        f"Failed to fetch assessment detail",
                        extra={"error": str(result), "correlation_id": correlation_id}
                    )
                else:
                    detailed_assessments.append(result)

        logger.info(
            f"Successfully fetched {len(detailed_assessments)}/{len(assessment_ids)} assessment details",
            extra={
                "project_id": project_id,
                "successful": len(detailed_assessments),
                "total": len(assessment_ids),
                "correlation_id": correlation_id
            }
        )

        return detailed_assessments

    async def get_project_controls(
        self,
        project_id: int,
        limit: int = 1000,
        offset: int = 0,
        correlation_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Fetch project controls (with embedded assessments) for a project.

        **This is the recommended endpoint for FY26 CORTAP projects.**

        Actual Riskuity API Endpoint: GET /projects/project_controls/{project_id}?limit={limit}&offset={offset}

        Returns paginated list of project_control objects, each containing:
        - control: Control definition with name, description
        - assessment: Embedded assessment data (status, comments, findings)
        - project: Project information
        - control_status, control_phase, etc.

        For FY26 projects, this typically returns 494-708 controls with assessments.

        Args:
            project_id: Riskuity project identifier (integer)
            limit: Maximum number of controls to return (default: 1000, covers most projects)
            offset: Pagination offset (default: 0)
            correlation_id: Optional correlation ID for request tracing

        Returns:
            list: Array of project_control objects with embedded assessments

        Raises:
            RiskuityAPIError: If API request fails

        Example response structure:
            {
                "items": [
                    {
                        "id": "4311",
                        "control": {
                            "id": "4870",
                            "name": "LEGAL : L2",
                            "description": "...",
                        },
                        "assessment": {
                            "id": "4572",
                            "status": "Complete",
                            "comments": "...",
                        },
                        "project": {...},
                        ...
                    },
                    ...
                ],
                "total": 494,
                "offset": 0,
                "limit": 1000
            }
        """
        endpoint = f"/projects/project_controls/{project_id}"
        params = {"limit": limit, "offset": offset}

        logger.info(
            f"Fetching project controls from Riskuity",
            extra={
                "project_id": project_id,
                "limit": limit,
                "offset": offset,
                "correlation_id": correlation_id
            }
        )

        data = await self._request_with_retry("GET", endpoint, correlation_id, params)

        # Extract items from paginated response
        if isinstance(data, dict):
            items = data.get("items", [])
            total = data.get("total", len(items))

            logger.info(
                f"Successfully fetched {len(items)} of {total} project controls",
                extra={
                    "project_id": project_id,
                    "returned": len(items),
                    "total": total,
                    "correlation_id": correlation_id
                }
            )

            return items
        elif isinstance(data, list):
            # In case API returns list directly
            return data
        else:
            logger.warning(
                f"Unexpected response format from project_controls endpoint",
                extra={"data_type": type(data), "correlation_id": correlation_id}
            )
            return []
