"""
Data Transformer - Converts Riskuity API responses to canonical JSON schema.

Transforms data from 4 Riskuity endpoints into the standardized project data schema
used by all document templates, with derived fields and metadata calculation.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from app.exceptions import ValidationError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class DataTransformer:
    """
    Transforms Riskuity API responses to canonical JSON schema (v1.0).

    The canonical schema provides a stable contract between data layer and template layer,
    enabling multiple templates to share the same cached data.

    Schema structure:
    - project_id, generated_at, data_version (metadata)
    - project (recipient info, review config, dates)
    - contractor (lead reviewer, firm details)
    - fta_program_manager (assigned PM details)
    - assessments (23 review areas with findings)
    - erf_items (Enhanced Review Focus areas)
    - metadata (derived fields: has_deficiencies, counts, etc.)

    Example:
        >>> transformer = DataTransformer()
        >>> canonical_json = transformer.transform(
        ...     project_id="RSKTY-12345",
        ...     project_data={...},
        ...     assessments=[...],
        ...     surveys=[...],
        ...     erf_items=[...],
        ...     correlation_id="abc-123"
        ... )
    """

    SCHEMA_VERSION = "1.0"

    # 23 required CORTAP review areas (for validation)
    REQUIRED_REVIEW_AREAS = [
        "Legal",
        "Financial Management and Capacity",
        "Technical Capacity - Award Management",
        "Technical Capacity - Program Management and Subrecipient Oversight",
        "Technical Capacity - Project Management",
        "Transit Asset Management",
        "Satisfactory Continuing Control",
        "Maintenance",
        "Americans with Disabilities Act (ADA)",
        "Drug and Alcohol",
        "Buy America",
        "Disadvantaged Business Enterprise (DBE)",
        "Procurement",
        "Public Transportation Agency Safety Plan (PTASP)",
        "Equal Employment Opportunity (EEO)",
        "Public Participation",
        "Charter Service",
        "School Bus",
        "Labor",
        "Demand Responsive Services",
        "Planning/Service Standards",
        "Security and Emergency Preparedness",
        "Half-Fare"
    ]

    def __init__(self):
        """Initialize DataTransformer."""
        logger.info("DataTransformer initialized", extra={"schema_version": self.SCHEMA_VERSION})

    def transform(
        self,
        project_id: int,
        riskuity_assessments: List[Dict],
        project_metadata: Optional[Dict] = None,
        correlation_id: Optional[str] = None
    ) -> Dict:
        """
        Transform Riskuity assessments (up to 644) to canonical JSON schema with 23 review areas.

        This method:
        1. Extracts project metadata from assessments
        2. Groups 644 control assessments by control_family into 23 CORTAP review areas
        3. Consolidates findings (D/ND/NA) per review area
        4. Calculates derived metadata

        Args:
            project_id: Riskuity project identifier (integer)
            riskuity_assessments: List of 644 assessment objects from Riskuity API
            project_metadata: Optional dict with project-level overrides
            correlation_id: Optional correlation ID for request tracing

        Returns:
            dict: Canonical JSON schema v1.0

        Raises:
            ValidationError: If required data is missing or invalid
        """
        logger.info(
            f"Starting data transformation for project {project_id}",
            extra={
                "project_id": project_id,
                "assessment_count": len(riskuity_assessments),
                "correlation_id": correlation_id
            }
        )

        try:
            # Extract project metadata from first assessment (all have same project info)
            if riskuity_assessments and not project_metadata:
                project_metadata = self._extract_project_metadata(
                    riskuity_assessments[0],
                    correlation_id
                )

            # Build canonical JSON structure
            canonical = {
                "project_id": str(project_id),
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "data_version": self.SCHEMA_VERSION,
                "project": self._transform_project(project_metadata or {}, correlation_id),
                "contractor": self._transform_contractor(project_metadata or {}, correlation_id),
                "fta_program_manager": self._transform_fta_pm(project_metadata or {}, correlation_id),
                "assessments": self._consolidate_assessments_by_review_area(
                    riskuity_assessments,
                    correlation_id
                ),
                "erf_items": [],  # Will be populated from deficient assessments
                "metadata": {}  # Will be populated after assessments
            }

            # Calculate derived metadata fields
            canonical["metadata"] = self._calculate_metadata(
                canonical["assessments"],
                canonical["erf_items"],
                correlation_id
            )

            logger.info(
                f"Data transformation completed for project {project_id}",
                extra={
                    "project_id": project_id,
                    "input_assessments": len(riskuity_assessments),
                    "output_review_areas": len(canonical["assessments"]),
                    "has_deficiencies": canonical["metadata"]["has_deficiencies"],
                    "deficiency_count": canonical["metadata"]["deficiency_count"],
                    "correlation_id": correlation_id
                }
            )

            return canonical

        except Exception as e:
            logger.error(
                f"Data transformation failed for project {project_id}",
                extra={
                    "project_id": project_id,
                    "error": str(e),
                    "correlation_id": correlation_id
                },
                exc_info=True
            )
            raise ValidationError(
                message=f"Failed to transform Riskuity data: {str(e)}",
                error_code="DATA_TRANSFORMATION_ERROR",
                details={"project_id": project_id, "error": str(e)}
            ) from e

    def _extract_project_metadata(self, assessment: Dict, correlation_id: Optional[str]) -> Dict:
        """
        Extract project-level metadata from a Riskuity assessment object.

        Since all assessments belong to the same project, we extract common
        project info from any assessment (typically the first one).

        Args:
            assessment: Single Riskuity assessment object
            correlation_id: Optional correlation ID

        Returns:
            dict: Extracted project metadata
        """
        try:
            project_control = assessment.get("project_control", {})
            project_info = project_control.get("project", {})

            # Extract what we can from the assessment structure
            # Note: Many fields will need to come from external source or be configurable
            metadata = {
                "project_id": project_info.get("id", ""),
                "project_name": project_info.get("name", ""),
                # These fields likely need to come from configuration or another source:
                "region_number": 1,  # TODO: Configure or extract from project
                "review_type": "Triennial Review",  # TODO: Configure
                "recipient_name": project_info.get("name", ""),
                "recipient_city_state": "",  # TODO: Configure
                "recipient_id": project_info.get("id", ""),
                # Add more fields as needed
            }

            logger.debug(
                "Extracted project metadata from assessment",
                extra={"metadata": metadata, "correlation_id": correlation_id}
            )

            return metadata

        except Exception as e:
            logger.warning(
                f"Failed to extract project metadata: {str(e)}",
                extra={"error": str(e), "correlation_id": correlation_id}
            )
            return {}

    def _consolidate_assessments_by_review_area(
        self,
        riskuity_assessments: List[Dict],
        correlation_id: Optional[str]
    ) -> List[Dict]:
        """
        Consolidate 644 Riskuity control assessments into 23 CORTAP review areas.

        Logic:
        1. Group assessments by control_family.name (maps to CORTAP review area)
        2. For each review area, determine overall finding:
           - If ANY control is Deficient (D) → review area is D
           - If ALL controls are Non-Deficient (ND) → review area is ND
           - If ALL controls are Not Applicable (NA) → review area is NA
        3. Aggregate deficiency details from all deficient controls in that area

        Args:
            riskuity_assessments: List of Riskuity assessment objects
            correlation_id: Optional correlation ID

        Returns:
            list: Consolidated assessments (23 review areas in CORTAP format)
        """
        from collections import defaultdict

        # Group assessments by control family (review area)
        review_areas = defaultdict(list)

        for assessment in riskuity_assessments:
            try:
                project_control = assessment.get("project_control", {})
                control_family = project_control.get("control_family", {})
                family_name = control_family.get("name", "Unknown")

                # Get assessment status/finding
                # Map Riskuity status to CORTAP finding codes
                status = assessment.get("status", "Not Started")
                review_status = self._map_status_to_finding(status, assessment)

                review_areas[family_name].append({
                    "assessment": assessment,
                    "finding": review_status,
                    "control_name": project_control.get("control", {}).get("name", ""),
                    "control_id": project_control.get("control", {}).get("id", "")
                })

            except Exception as e:
                logger.warning(
                    f"Failed to process assessment: {str(e)}",
                    extra={"assessment_id": assessment.get("id"), "error": str(e), "correlation_id": correlation_id}
                )
                continue

        # Consolidate each review area
        consolidated = []
        for review_area_name, controls in review_areas.items():
            consolidated_assessment = self._consolidate_review_area(
                review_area_name,
                controls,
                correlation_id
            )
            consolidated.append(consolidated_assessment)

        logger.info(
            f"Consolidated {len(riskuity_assessments)} assessments into {len(consolidated)} review areas",
            extra={
                "input_count": len(riskuity_assessments),
                "output_count": len(consolidated),
                "correlation_id": correlation_id
            }
        )

        return consolidated

    def _map_status_to_finding(self, status: str, assessment: Dict) -> str:
        """
        Map Riskuity assessment status to CORTAP finding code.

        Riskuity statuses: "Not Started", "In Progress", "Complete", etc.
        CORTAP findings: "D" (Deficient), "ND" (Non-Deficient), "NA" (Not Applicable)

        Logic:
        - Check instances[].review_status for actual finding
        - Map status to finding code
        - Default to "ND" if unclear

        Args:
            status: Riskuity assessment status
            assessment: Full assessment object

        Returns:
            str: "D", "ND", or "NA"
        """
        # Check instances for review status
        instances = assessment.get("instances", [])
        if instances:
            review_status = instances[0].get("review_status", "")
            # TODO: Map Riskuity review_status values to D/ND/NA
            # This mapping depends on your Riskuity configuration
            if "deficien" in review_status.lower() or "fail" in review_status.lower():
                return "D"
            elif "not applicable" in review_status.lower() or "n/a" in review_status.lower():
                return "NA"

        # Fallback: map overall status
        if status in ["Complete", "Completed"]:
            return "ND"  # Assume complete = non-deficient unless instance says otherwise
        elif status == "Not Started":
            return "NA"  # Not yet assessed

        return "ND"  # Default to non-deficient

    def _consolidate_review_area(
        self,
        review_area_name: str,
        controls: List[Dict],
        correlation_id: Optional[str]
    ) -> Dict:
        """
        Consolidate multiple control assessments into single review area assessment.

        Args:
            review_area_name: Name of the CORTAP review area
            controls: List of control assessments in this area
            correlation_id: Optional correlation ID

        Returns:
            dict: Consolidated assessment in CORTAP format
        """
        # Determine overall finding for review area
        findings = [c["finding"] for c in controls]
        deficient_controls = [c for c in controls if c["finding"] == "D"]

        # If ANY control is deficient, the review area is deficient
        if deficient_controls:
            overall_finding = "D"
            # Aggregate deficiency details
            deficiency_descriptions = []
            for dc in deficient_controls:
                control_name = dc["control_name"]
                assessment_obj = dc["assessment"]
                desc = assessment_obj.get("description", "")
                comments = assessment_obj.get("comments", "")
                if desc:
                    deficiency_descriptions.append(f"{control_name}: {desc}")
                elif comments:
                    deficiency_descriptions.append(f"{control_name}: {comments}")

            description = "\n".join(deficiency_descriptions) if deficiency_descriptions else "Deficiency found in one or more controls"
        elif all(f == "NA" for f in findings):
            overall_finding = "NA"
            description = None
        else:
            overall_finding = "ND"
            description = None

        return {
            "review_area": review_area_name,
            "finding": overall_finding,
            "deficiency_code": None,  # TODO: Extract if available
            "description": description,
            "corrective_action": None,  # TODO: Extract from CAP POAMs if needed
            "due_date": None,
            "date_closed": None
        }

    def _transform_project(self, project_data: Dict, correlation_id: Optional[str]) -> Dict:
        """
        Transform project metadata and recipient information.

        Required fields: region_number, review_type, recipient_name, recipient_city_state,
                        recipient_id, site_visit_dates, exit_conference_format

        Optional fields: recipient_acronym, recipient_website, report_date
        """
        # Extract required fields
        try:
            project = {
                "region_number": int(project_data["region_number"]),
                "review_type": project_data["review_type"],
                "recipient_name": project_data["recipient_name"],
                "recipient_city_state": project_data["recipient_city_state"],
                "recipient_id": project_data["recipient_id"],
                "site_visit_dates": project_data.get("site_visit_dates", "TBD"),
                "exit_conference_format": project_data.get("exit_conference_format", "virtual"),
            }

            # Add optional fields
            project["recipient_acronym"] = project_data.get("recipient_acronym", "")
            project["recipient_website"] = project_data.get("recipient_website", "")
            project["site_visit_start_date"] = project_data.get("site_visit_start_date", "")
            project["site_visit_end_date"] = project_data.get("site_visit_end_date", "")
            project["report_date"] = project_data.get("report_date", "")

            # Validate review_type
            valid_review_types = [
                "Triennial Review",
                "State Management Review",
                "Combined Triennial and State Management Review"
            ]
            if project["review_type"] not in valid_review_types:
                logger.warning(
                    f"Invalid review_type: {project['review_type']}",
                    extra={
                        "review_type": project["review_type"],
                        "valid_types": valid_review_types,
                        "correlation_id": correlation_id
                    }
                )

            return project

        except KeyError as e:
            raise ValidationError(
                message=f"Missing required project field: {str(e)}",
                error_code="MISSING_PROJECT_FIELD",
                details={"missing_field": str(e)}
            ) from e

    def _transform_contractor(self, project_data: Dict, correlation_id: Optional[str]) -> Dict:
        """
        Transform contractor/lead reviewer information.

        Required fields: lead_reviewer_name, contractor_name, lead_reviewer_phone, lead_reviewer_email
        """
        try:
            return {
                "lead_reviewer_name": project_data["lead_reviewer_name"],
                "contractor_name": project_data["contractor_name"],
                "lead_reviewer_phone": project_data["lead_reviewer_phone"],
                "lead_reviewer_email": project_data["lead_reviewer_email"],
            }
        except KeyError as e:
            raise ValidationError(
                message=f"Missing required contractor field: {str(e)}",
                error_code="MISSING_CONTRACTOR_FIELD",
                details={"missing_field": str(e)}
            ) from e

    def _transform_fta_pm(self, project_data: Dict, correlation_id: Optional[str]) -> Dict:
        """
        Transform FTA Program Manager information.

        Required fields: fta_program_manager_name, fta_program_manager_title,
                        fta_program_manager_phone, fta_program_manager_email
        """
        try:
            return {
                "fta_program_manager_name": project_data["fta_program_manager_name"],
                "fta_program_manager_title": project_data["fta_program_manager_title"],
                "fta_program_manager_phone": project_data["fta_program_manager_phone"],
                "fta_program_manager_email": project_data["fta_program_manager_email"],
            }
        except KeyError as e:
            raise ValidationError(
                message=f"Missing required FTA PM field: {str(e)}",
                error_code="MISSING_FTA_PM_FIELD",
                details={"missing_field": str(e)}
            ) from e

    def _transform_assessments(self, assessments: List[Dict], correlation_id: Optional[str]) -> List[Dict]:
        """
        Transform 23 CORTAP review area assessments.

        Required fields: review_area, finding
        Conditional fields: deficiency_code, description, corrective_action, due_date (if finding = "D")

        Validates that all 23 required review areas are present.
        """
        transformed = []
        review_areas_found = set()

        for assessment in assessments:
            try:
                review_area = assessment["review_area"]
                finding = assessment["finding"]

                # Validate finding value
                if finding not in ["D", "ND", "NA"]:
                    logger.warning(
                        f"Invalid finding value: {finding} for {review_area}",
                        extra={
                            "review_area": review_area,
                            "finding": finding,
                            "correlation_id": correlation_id
                        }
                    )

                transformed_assessment = {
                    "review_area": review_area,
                    "finding": finding,
                    "deficiency_code": assessment.get("deficiency_code"),
                    "description": assessment.get("description"),
                    "corrective_action": assessment.get("corrective_action"),
                    "due_date": assessment.get("due_date"),
                    "date_closed": assessment.get("date_closed"),
                }

                transformed.append(transformed_assessment)
                review_areas_found.add(review_area)

            except KeyError as e:
                logger.warning(
                    f"Assessment missing required field: {str(e)}",
                    extra={
                        "missing_field": str(e),
                        "assessment": assessment,
                        "correlation_id": correlation_id
                    }
                )
                continue

        # Validate all 23 review areas are present
        missing_areas = set(self.REQUIRED_REVIEW_AREAS) - review_areas_found
        if missing_areas:
            logger.warning(
                f"Missing {len(missing_areas)} required review areas",
                extra={
                    "missing_areas": list(missing_areas),
                    "found_count": len(review_areas_found),
                    "correlation_id": correlation_id
                }
            )

        return transformed

    def _transform_erf_items(self, erf_items: List[Dict], correlation_id: Optional[str]) -> List[Dict]:
        """
        Transform Enhanced Review Focus (ERF) items.

        Fields: area, description
        """
        transformed = []

        for item in erf_items:
            transformed_item = {
                "area": item.get("area", ""),
                "description": item.get("description", ""),
            }
            transformed.append(transformed_item)

        return transformed

    def _calculate_metadata(
        self,
        assessments: List[Dict],
        erf_items: List[Dict],
        correlation_id: Optional[str]
    ) -> Dict:
        """
        Calculate derived metadata fields from assessments and ERF data.

        Derived fields:
        - has_deficiencies: boolean
        - deficiency_count: int
        - deficiency_areas: list of review area names with finding = "D"
        - erf_count: int
        - erf_areas: list of ERF area names
        - total_review_areas: int
        """
        # Count deficiencies
        deficient_assessments = [a for a in assessments if a["finding"] == "D"]
        deficiency_count = len(deficient_assessments)
        has_deficiencies = deficiency_count > 0
        deficiency_areas = [a["review_area"] for a in deficient_assessments]

        # ERF counts
        erf_count = len(erf_items)
        erf_areas = [item["area"] for item in erf_items if item["area"]]

        metadata = {
            "has_deficiencies": has_deficiencies,
            "deficiency_count": deficiency_count,
            "deficiency_areas": deficiency_areas,
            "erf_count": erf_count,
            "erf_areas": erf_areas,
            "total_review_areas": len(assessments),
        }

        logger.debug(
            "Metadata calculated",
            extra={
                "metadata": metadata,
                "correlation_id": correlation_id
            }
        )

        return metadata
