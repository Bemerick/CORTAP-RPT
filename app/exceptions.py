"""
Custom exception hierarchy for CORTAP-RPT domain-specific errors.

All exceptions inherit from CORTAPError and include:
- message: Human-readable error message
- error_code: Machine-readable error code
- details: Additional context (dict)
"""

from typing import Dict, Optional


class CORTAPError(Exception):
    """
    Base exception for all CORTAP-RPT errors.

    Attributes:
        message: Human-readable error message
        error_code: Machine-readable error code (e.g., "TEMPLATE_NOT_FOUND")
        details: Additional context as a dictionary
    """

    def __init__(
        self,
        message: str,
        error_code: str,
        details: Optional[Dict] = None
    ):
        """
        Initialize CORTAP error.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Optional dictionary with additional context
        """
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message='{self.message}', "
            f"error_code='{self.error_code}', "
            f"details={self.details})"
        )


class RiskuityAPIError(CORTAPError):
    """
    Raised when Riskuity API call fails.

    Examples:
        - Network timeout
        - 500 Internal Server Error from Riskuity
        - Invalid API response format
        - Rate limiting (429)
    """

    def __init__(
        self,
        message: str,
        error_code: str = "RISKUITY_API_ERROR",
        details: Optional[Dict] = None
    ):
        super().__init__(message, error_code, details)


class DocumentGenerationError(CORTAPError):
    """
    Raised when document generation fails.

    Examples:
        - Template file not found
        - Invalid template syntax
        - Jinja2 rendering error
        - Missing required context data
    """

    def __init__(
        self,
        message: str,
        error_code: str = "DOCUMENT_GENERATION_ERROR",
        details: Optional[Dict] = None
    ):
        super().__init__(message, error_code, details)


class ValidationError(CORTAPError):
    """
    Raised when data validation fails.

    Examples:
        - Missing required fields
        - Invalid data types
        - Schema validation failure
        - Business rule violation
    """

    def __init__(
        self,
        message: str,
        error_code: str = "VALIDATION_ERROR",
        details: Optional[Dict] = None
    ):
        super().__init__(message, error_code, details)


class S3StorageError(CORTAPError):
    """
    Raised when S3 operations fail.

    Examples:
        - Bucket not found
        - Permission denied
        - Upload/download failure
        - Invalid S3 path
    """

    def __init__(
        self,
        message: str,
        error_code: str = "S3_STORAGE_ERROR",
        details: Optional[Dict] = None
    ):
        super().__init__(message, error_code, details)
