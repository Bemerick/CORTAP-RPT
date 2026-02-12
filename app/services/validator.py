"""
JSON Data Validator Service for CORTAP-RPT.

Validates canonical JSON data against schema and checks completeness
for template generation requirements.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

import jsonschema
from jsonschema import Draft7Validator
from pydantic import BaseModel, Field

from app.exceptions import ValidationError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ValidationResult(BaseModel):
    """
    Result of JSON schema validation.

    Attributes:
        valid: Whether the JSON is valid according to schema
        errors: List of validation error messages
        warnings: List of data quality warnings
    """
    valid: bool = Field(..., description="Whether JSON is schema-valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Data quality warnings")


class CompletenessResult(BaseModel):
    """
    Result of template completeness checking.

    Attributes:
        missing_critical_fields: Fields required for template generation
        missing_optional_fields: Optional fields that improve quality
        data_quality_score: Percentage of fields present (0-100)
        can_generate: Whether document can be generated despite missing fields
    """
    missing_critical_fields: List[str] = Field(
        default_factory=list,
        description="Critical fields missing (blocks generation)"
    )
    missing_optional_fields: List[str] = Field(
        default_factory=list,
        description="Optional fields missing (reduces quality)"
    )
    data_quality_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Data quality score (0-100)"
    )
    can_generate: bool = Field(
        ...,
        description="Can generate document (no critical fields missing)"
    )


class JsonValidator:
    """
    Validates JSON data against schema and template requirements.

    Provides two validation modes:
    1. Schema validation - Checks JSON structure matches canonical schema
    2. Completeness validation - Checks all required template fields present

    Example:
        >>> validator = JsonValidator()
        >>> result = await validator.validate_json_schema(data)
        >>> if result.valid:
        ...     completeness = await validator.check_completeness(data, "draft-audit-report")
        ...     if completeness.can_generate:
        ...         # Generate document
    """

    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize validator with JSON schema.

        Args:
            schema_path: Path to JSON schema file (defaults to canonical schema)
        """
        if schema_path is None:
            # Default to canonical schema
            schema_path = str(
                Path(__file__).parent.parent.parent / "docs" / "schemas" / "project-data-schema-v1.0.json"
            )

        self.schema_path = schema_path
        self.schema = self._load_schema()
        self.validator = Draft7Validator(self.schema)

        logger.info(
            "JsonValidator initialized",
            extra={"schema_path": schema_path}
        )

    def _load_schema(self) -> Dict:
        """Load JSON schema from file."""
        try:
            with open(self.schema_path, 'r') as f:
                schema = json.load(f)

            logger.debug(f"JSON schema loaded from {self.schema_path}")
            return schema

        except FileNotFoundError:
            logger.error(f"Schema file not found: {self.schema_path}")
            raise ValidationError(
                message=f"Schema file not found: {self.schema_path}",
                error_code="SCHEMA_NOT_FOUND",
                details={"schema_path": self.schema_path}
            )
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in schema file: {str(e)}")
            raise ValidationError(
                message=f"Invalid JSON in schema file: {str(e)}",
                error_code="INVALID_SCHEMA",
                details={"schema_path": self.schema_path, "error": str(e)}
            )

    async def validate_json_schema(self, json_data: Dict) -> ValidationResult:
        """
        Validate JSON data against canonical schema.

        Checks:
        - All required top-level keys present
        - Data types match schema
        - Enum values valid
        - Arrays non-empty where required
        - String patterns match (e.g., dates, region numbers)

        Args:
            json_data: JSON data to validate

        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []

        logger.debug("Starting JSON schema validation")

        try:
            # Validate using jsonschema library
            validation_errors = list(self.validator.iter_errors(json_data))

            if validation_errors:
                for error in validation_errors:
                    # Format error message with path
                    path = ".".join(str(p) for p in error.path) if error.path else "root"
                    error_msg = f"{path}: {error.message}"
                    errors.append(error_msg)

                    logger.warning(
                        "Schema validation error",
                        extra={
                            "path": path,
                            "error": error.message,
                            "validator": error.validator
                        }
                    )

            # Additional custom validations
            self._check_assessments_completeness(json_data, warnings)
            self._check_metadata_quality(json_data, warnings)

            valid = len(errors) == 0

            logger.info(
                "Schema validation complete",
                extra={
                    "valid": valid,
                    "error_count": len(errors),
                    "warning_count": len(warnings)
                }
            )

            return ValidationResult(
                valid=valid,
                errors=errors,
                warnings=warnings
            )

        except Exception as e:
            logger.error(
                f"Unexpected error during validation: {str(e)}",
                exc_info=True
            )
            return ValidationResult(
                valid=False,
                errors=[f"Validation failed: {str(e)}"],
                warnings=[]
            )

    def _check_assessments_completeness(self, json_data: Dict, warnings: List[str]) -> None:
        """Check if assessments array is complete."""
        assessments = json_data.get("assessments", [])

        if len(assessments) == 0:
            warnings.append("assessments: Array is empty - no review areas defined")
        elif len(assessments) < 21:
            warnings.append(
                f"assessments: Only {len(assessments)} review areas (expected 21 for FY26)"
            )

    def _check_metadata_quality(self, json_data: Dict, warnings: List[str]) -> None:
        """Check metadata quality indicators."""
        metadata = json_data.get("metadata", {})

        # Check if deficiency detection ran
        if "has_deficiencies" not in metadata:
            warnings.append("metadata.has_deficiencies: Missing deficiency detection flag")

        # Check for reasonable deficiency counts
        deficiency_count = metadata.get("deficiency_count", 0)
        if deficiency_count > 10:
            warnings.append(
                f"metadata.deficiency_count: High deficiency count ({deficiency_count}) - verify accuracy"
            )

    async def check_completeness(
        self,
        json_data: Dict,
        template_id: str
    ) -> CompletenessResult:
        """
        Check data completeness for specific template requirements.

        This checks whether all required fields for a given template are present
        and not null. Different templates may have different field requirements.

        Args:
            json_data: Validated JSON data
            template_id: Template identifier (e.g., 'draft-audit-report')

        Returns:
            CompletenessResult with missing fields and quality score
        """
        logger.debug(
            f"Checking completeness for template: {template_id}"
        )

        # Define critical and optional fields per template
        # NOTE: In production, this should be loaded from template metadata YAML
        template_requirements = self._get_template_requirements(template_id)

        missing_critical = []
        missing_optional = []

        # Check critical fields
        for field_path in template_requirements["critical"]:
            if not self._field_exists(json_data, field_path):
                missing_critical.append(field_path)

        # Check optional fields
        for field_path in template_requirements["optional"]:
            if not self._field_exists(json_data, field_path):
                missing_optional.append(field_path)

        # Calculate data quality score
        total_fields = len(template_requirements["critical"]) + len(template_requirements["optional"])
        present_fields = total_fields - len(missing_critical) - len(missing_optional)
        quality_score = int((present_fields / total_fields) * 100) if total_fields > 0 else 100

        can_generate = len(missing_critical) == 0

        logger.info(
            "Completeness check complete",
            extra={
                "template_id": template_id,
                "quality_score": quality_score,
                "missing_critical": len(missing_critical),
                "missing_optional": len(missing_optional),
                "can_generate": can_generate
            }
        )

        return CompletenessResult(
            missing_critical_fields=missing_critical,
            missing_optional_fields=missing_optional,
            data_quality_score=quality_score,
            can_generate=can_generate
        )

    def _get_template_requirements(self, template_id: str) -> Dict[str, List[str]]:
        """
        Get field requirements for a specific template.

        NOTE: In production, this should load from template metadata YAML files.
        For MVP, we define requirements inline.
        """
        # Common requirements for all templates
        common_critical = [
            "project.region_number",
            "project.review_type",
            "project.recipient_name",
            "project.recipient_acronym",
            "project.recipient_city_state",
            "project.report_date",
            "contractor.company_name",
            "fta_program_manager.name",
            "assessments",
            "metadata.has_deficiencies"
        ]

        common_optional = [
            "project.recipient_website",
            "project.site_visit_dates",
            "project.exit_conference_format",
            "fta_program_manager.title",
            "fta_program_manager.region"
        ]

        # Template-specific requirements
        if template_id == "draft-audit-report":
            return {
                "critical": common_critical + [
                    "project.exit_conference_format",
                    "metadata.deficiency_count"
                ],
                "optional": common_optional + [
                    "contractor.team_members"
                ]
            }
        elif template_id == "recipient-information-request":
            return {
                "critical": common_critical,
                "optional": common_optional
            }
        else:
            # Unknown template - use common requirements
            logger.warning(
                f"Unknown template_id '{template_id}' - using common requirements"
            )
            return {
                "critical": common_critical,
                "optional": common_optional
            }

    def _field_exists(self, json_data: Dict, field_path: str) -> bool:
        """
        Check if a nested field exists and is not null.

        Args:
            json_data: JSON data to check
            field_path: Dot-notation path (e.g., 'project.recipient_name')

        Returns:
            bool: True if field exists and is not null
        """
        parts = field_path.split('.')
        current = json_data

        for part in parts:
            if not isinstance(current, dict) or part not in current:
                return False
            current = current[part]

        # Field exists, check if it's not null and not empty string
        return current is not None and current != ""
