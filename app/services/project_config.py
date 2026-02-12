"""
Project Configuration Service

Loads project-specific setup data from JSON configuration file.
This data supplements what's available from Riskuity API.
"""

import json
from pathlib import Path
from typing import Dict, Optional
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ProjectConfigService:
    """
    Service for loading project setup configuration data.

    Configuration file structure:
    {
        "projects": [
            {
                "project_id": 33,
                "project_info": {...},
                "contractor": {...},
                "fta_program_manager": {...},
                "regional_officer": {...},
                "attendees": [...],
                "subrecipients": {...}
            }
        ]
    }
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize ProjectConfigService.

        Args:
            config_path: Path to project setup JSON configuration file.
                        If None, will use settings.project_config_path
        """
        if config_path is None:
            # Import here to avoid circular dependency
            from app.config import settings
            config_path = settings.project_config_path

        self.config_path = Path(config_path)
        self._config_cache: Optional[Dict] = None

        logger.info(
            f"ProjectConfigService initialized",
            extra={"config_path": str(self.config_path)}
        )

    def _load_config(self) -> Dict:
        """
        Load configuration from JSON file with caching.

        Returns:
            dict: Configuration data
        """
        if self._config_cache is not None:
            return self._config_cache

        if not self.config_path.exists():
            logger.warning(
                f"Project setup config file not found: {self.config_path}",
                extra={"config_path": str(self.config_path)}
            )
            return {"projects": []}

        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)

            self._config_cache = config

            project_count = len(config.get('projects', []))
            logger.info(
                f"Loaded project setup configuration",
                extra={
                    "config_path": str(self.config_path),
                    "project_count": project_count
                }
            )

            return config

        except Exception as e:
            logger.error(
                f"Failed to load project setup configuration: {e}",
                extra={"config_path": str(self.config_path), "error": str(e)},
                exc_info=True
            )
            return {"projects": []}

    def get_project_config(self, project_id: int, correlation_id: Optional[str] = None) -> Optional[Dict]:
        """
        Get configuration for a specific project.

        Args:
            project_id: Riskuity project ID
            correlation_id: Optional correlation ID for logging

        Returns:
            dict: Project configuration or None if not found
        """
        config = self._load_config()
        projects = config.get('projects', [])

        for project in projects:
            if project.get('project_id') == project_id:
                logger.info(
                    f"Found project configuration for project {project_id}",
                    extra={
                        "project_id": project_id,
                        "correlation_id": correlation_id
                    }
                )
                return project

        logger.warning(
            f"No project configuration found for project {project_id}",
            extra={
                "project_id": project_id,
                "correlation_id": correlation_id
            }
        )
        return None

    def get_project_metadata(self, project_id: int, correlation_id: Optional[str] = None) -> Dict:
        """
        Get project metadata for data transformer.

        Returns a dict with all fields needed by the data transformer,
        merging project_info, contractor, fta_program_manager, regional_officer, etc.

        Args:
            project_id: Riskuity project ID
            correlation_id: Optional correlation ID for logging

        Returns:
            dict: Flattened project metadata for data transformer
        """
        project_config = self.get_project_config(project_id, correlation_id)

        if not project_config:
            logger.info(
                f"Using default metadata for project {project_id} (no config found)",
                extra={"project_id": project_id, "correlation_id": correlation_id}
            )
            return self._get_default_metadata(project_id)

        # Flatten configuration into single dict for transformer
        project_info = project_config.get('project_info', {})

        # Get recipient_name from config or derive from recipient_city_state
        recipient_name = project_info.get('recipient_name')
        if not recipient_name:
            # Use city name from recipient_city_state as fallback
            city_state = project_info.get('recipient_city_state', 'Unknown, ST')
            recipient_name = city_state.split(',')[0].strip()

        metadata = {
            "project_id": project_id,
            "project_name": recipient_name,  # For Riskuity compatibility
            "recipient_name": recipient_name,  # Required by transformer
            "recipient_id": str(project_id),  # Map project_id to recipient_id (as string)
            **project_info,
            **self._flatten_contractor(project_config.get('contractor', {})),
            **self._flatten_fta_pm(project_config.get('fta_program_manager', {})),
            "regional_officer": project_config.get('regional_officer', {}),
            "attendees": project_config.get('attendees', []),
            "subrecipients_5307": project_config.get('subrecipients', {}).get('5307', []),
            "subrecipients_5310": project_config.get('subrecipients', {}).get('5310', []),
            "subrecipients_5311": project_config.get('subrecipients', {}).get('5311', []),
        }

        logger.debug(
            f"Built metadata for project {project_id}",
            extra={
                "project_id": project_id,
                "metadata_keys": list(metadata.keys()),
                "correlation_id": correlation_id
            }
        )

        return metadata

    def _flatten_contractor(self, contractor: Dict) -> Dict:
        """Flatten contractor object for transformer compatibility"""
        return {
            "lead_reviewer_name": contractor.get('lead_reviewer_name', 'TBD'),
            "company_name": contractor.get('company_name', 'TBD'),
            "contractor_name": contractor.get('company_name', 'TBD'),  # Alias
            "lead_reviewer_phone": contractor.get('lead_reviewer_phone', 'TBD'),
            "lead_reviewer_email": contractor.get('lead_reviewer_email', 'TBD'),
        }

    def _flatten_fta_pm(self, fta_pm: Dict) -> Dict:
        """Flatten FTA PM object for transformer compatibility"""
        name = fta_pm.get('name', 'TBD')
        return {
            "fta_program_manager_name": name,
            "name": name,  # Alias for completeness check
            "fta_program_manager_title": fta_pm.get('title', 'TBD'),
            "fta_program_manager_phone": fta_pm.get('phone', 'TBD'),
            "fta_program_manager_email": fta_pm.get('email', 'TBD'),
        }

    def _get_default_metadata(self, project_id: int) -> Dict:
        """
        Get default metadata when no configuration is found.

        Returns same "TBD" defaults as before config file existed.
        """
        from datetime import datetime

        return {
            "project_id": project_id,
            "region_number": 1,
            "review_type": "Triennial Review",
            "recipient_city_state": "City, ST",
            "recipient_acronym": "TBD",
            "recipient_website": "",
            "fiscal_year": "FY2026",
            "site_visit_start_date": "",
            "site_visit_end_date": "",
            "site_visit_dates": "TBD",
            "exit_conference_format": "virtual",
            "report_date": datetime.utcnow().strftime("%B %d, %Y"),
            "lead_reviewer_name": "TBD",
            "company_name": "TBD",
            "contractor_name": "TBD",
            "lead_reviewer_phone": "TBD",
            "lead_reviewer_email": "TBD",
            "fta_program_manager_name": "TBD",
            "name": "TBD",
            "fta_program_manager_title": "TBD",
            "fta_program_manager_phone": "TBD",
            "fta_program_manager_email": "TBD",
            "regional_officer": {
                "name": "TBD",
                "title": "Regional Administrator",
                "phone": "TBD",
                "email": "TBD"
            },
            "attendees": [],
            "subrecipients_5307": [],
            "subrecipients_5310": [],
            "subrecipients_5311": [],
        }

    def reload_config(self):
        """Reload configuration from disk (clear cache)"""
        self._config_cache = None
        logger.info("Project configuration cache cleared")
