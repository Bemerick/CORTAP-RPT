"""
Context builders for transforming canonical JSON data to template contexts.

Provides builders for different template types that extract and transform
data from the canonical JSON schema into template-ready dictionaries.
"""

from datetime import datetime
from typing import Dict, Optional
from pydantic import ValidationError

from app.models.template_data import RIRTemplateData
from app.exceptions import ValidationError as CORTAPValidationError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class RIRContextBuilder:
    """
    Builds Jinja2 context for RIR template from canonical JSON data.

    Transforms the canonical project JSON schema into the specific
    context required for the Recipient Information Request template.
    """

    @staticmethod
    def format_date_range(start_date: Optional[str], end_date: Optional[str]) -> str:
        """
        Format date range for display.

        Args:
            start_date: ISO 8601 date string (YYYY-MM-DD) or None
            end_date: ISO 8601 date string (YYYY-MM-DD) or None

        Returns:
            Formatted date range string (e.g., "March 10-14, 2025") or "TBD"

        Examples:
            >>> RIRContextBuilder.format_date_range("2025-03-10", "2025-03-14")
            "March 10-14, 2025"
            >>> RIRContextBuilder.format_date_range("2025-03-10", "2025-03-10")
            "March 10, 2025"
            >>> RIRContextBuilder.format_date_range(None, None)
            "TBD"
        """
        if not start_date or not end_date:
            return "TBD"

        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)

            # Same day visit
            if start == end:
                return start.strftime("%B %d, %Y")

            # Same month range
            if start.month == end.month and start.year == end.year:
                return f"{start.strftime('%B')} {start.day}-{end.day}, {start.year}"

            # Different months, same year
            if start.year == end.year:
                return f"{start.strftime('%B %d')} - {end.strftime('%B %d, %Y')}"

            # Different years
            return f"{start.strftime('%B %d, %Y')} - {end.strftime('%B %d, %Y')}"

        except (ValueError, AttributeError) as e:
            logger.warning(
                f"Invalid date format in date range: {start_date} to {end_date}",
                extra={"error": str(e)}
            )
            return "TBD"

    @staticmethod
    def build_context(
        json_data: dict,
        correlation_id: Optional[str] = None
    ) -> Dict:
        """
        Transform canonical JSON to RIR template context.

        Args:
            json_data: Canonical project JSON from data service (v1.0 schema)
            correlation_id: Optional correlation ID for logging

        Returns:
            dict: Jinja2 context for RIR template rendering

        Raises:
            ValidationError: If required fields are missing or invalid

        Example:
            >>> json_data = {
            ...     "project": {"region_number": 1, "review_type": "Triennial Review", ...},
            ...     "contractor": {"lead_reviewer_name": "John Doe", ...},
            ...     "fta_program_manager": {"fta_program_manager_name": "Jane Smith", ...}
            ... }
            >>> context = RIRContextBuilder.build_context(json_data)
            >>> context["region_number"]
            1
        """
        logger.info(
            "Building RIR template context from canonical JSON",
            extra={"correlation_id": correlation_id}
        )

        try:
            # Extract sections from canonical JSON
            project = json_data.get("project", {})
            contractor = json_data.get("contractor", {})
            fta_pm = json_data.get("fta_program_manager", {})

            # Format site visit dates
            site_visit_dates = project.get("site_visit_dates", "TBD")

            # If site_visit_dates is already a formatted string, use it
            # Otherwise, try to format from start/end dates
            if site_visit_dates == "TBD" or not site_visit_dates:
                start_date = project.get("site_visit_start_date")
                end_date = project.get("site_visit_end_date")
                if start_date and end_date:
                    site_visit_dates = RIRContextBuilder.format_date_range(start_date, end_date)
                else:
                    site_visit_dates = "TBD"

            # Build RIRTemplateData model for validation
            rir_data = RIRTemplateData(
                # Project Information
                region_number=project.get("region_number"),
                review_type=project.get("review_type"),
                recipient_name=project.get("recipient_name"),
                recipient_city_state=project.get("recipient_city_state"),
                recipient_id=project.get("recipient_id"),
                recipient_website=project.get("recipient_website", "N/A"),

                # Site Visit
                site_visit_dates=site_visit_dates,

                # Contractor Information
                contractor_name=contractor.get("contractor_name"),
                lead_reviewer_name=contractor.get("lead_reviewer_name"),
                lead_reviewer_phone=contractor.get("lead_reviewer_phone"),
                lead_reviewer_email=contractor.get("lead_reviewer_email"),

                # FTA Program Manager
                fta_program_manager_name=fta_pm.get("fta_program_manager_name"),
                fta_program_manager_title=fta_pm.get("fta_program_manager_title"),
                fta_program_manager_phone=fta_pm.get("fta_program_manager_phone"),
                fta_program_manager_email=fta_pm.get("fta_program_manager_email"),

                # Optional
                due_date=project.get("due_date")
            )

            # Convert to template context
            context = rir_data.to_template_context()

            logger.info(
                "RIR template context built successfully",
                extra={
                    "correlation_id": correlation_id,
                    "recipient_name": context.get("recipient_name"),
                    "review_type": context.get("review_type")
                }
            )

            return context

        except ValidationError as e:
            logger.error(
                "Validation error building RIR context",
                extra={
                    "correlation_id": correlation_id,
                    "errors": e.errors()
                },
                exc_info=True
            )
            raise CORTAPValidationError(
                message=f"Invalid data for RIR template: {str(e)}",
                error_code="RIR_CONTEXT_VALIDATION_ERROR",
                details={"validation_errors": e.errors()}
            ) from e
        except KeyError as e:
            logger.error(
                "Missing required field in JSON data",
                extra={
                    "correlation_id": correlation_id,
                    "missing_field": str(e)
                },
                exc_info=True
            )
            raise CORTAPValidationError(
                message=f"Missing required field in JSON data: {str(e)}",
                error_code="RIR_CONTEXT_MISSING_FIELD",
                details={"missing_field": str(e)}
            ) from e
        except Exception as e:
            logger.error(
                "Unexpected error building RIR context",
                extra={
                    "correlation_id": correlation_id,
                    "error": str(e)
                },
                exc_info=True
            )
            raise CORTAPValidationError(
                message=f"Failed to build RIR context: {str(e)}",
                error_code="RIR_CONTEXT_BUILD_ERROR",
                details={"error": str(e), "error_type": type(e).__name__}
            ) from e
