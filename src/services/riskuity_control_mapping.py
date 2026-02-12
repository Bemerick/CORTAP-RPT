"""
Mapping configuration for Riskuity control prefixes to JSON review area names.

This module provides the canonical mapping between:
- Riskuity control name prefixes (extracted from control.name field)
- JSON schema review area names (used in project-data-schema-v1.0.json)

Based on analysis of CORTAP FY26 Assessment Test project (ID: 33).
"""

from typing import Dict, Optional
import re


# Canonical mapping from Riskuity control prefixes to JSON review area names
# Based on actual control names from Riskuity API
RISKUITY_PREFIX_TO_JSON_AREA: Dict[str, str] = {
    # Legal (11 controls)
    "LEGAL": "Legal",

    # Financial Management (56 controls total: 55 + 1)
    "FINANCIAL MANAGEMENT": "Financial Management and Capacity",
    "FINANCIAL MANAGEMENT AND CAPACITY": "Financial Management and Capacity",

    # Technical Capacity - Award Management (40 controls total: 35 + 5)
    "TECHNICAL CAPACITY AWARD MANAGEMENT": "Technical Capacity - Award Management",
    "TECHNICAL CAPACITY – AWARD MANAGEMENT": "Technical Capacity - Award Management",  # Note: en-dash variant

    # Technical Capacity - Program Management (30 controls)
    "TECHNICAL CAPACITY PROGRAM MANAGEMENT": "Technical Capacity - Program Management and Subrecipient Oversight",
    "TECHNICAL CAPACITY – PROGRAM MANAGEMENT": "Technical Capacity - Program Management and Subrecipient Oversight",

    # Technical Capacity - Project Management (17 controls)
    "TECHNICAL CAPACITY PROJECT MANAGEMENT": "Technical Capacity - Project Management",
    "TECHNICAL CAPACITY – PROJECT MANAGEMENT": "Technical Capacity - Project Management",

    # Transit Asset Management (33 controls)
    "TRANSIT ASSET MANAGEMENT": "Transit Asset Management",

    # Satisfactory Continuing Control (60 controls)
    "SATISFACTORY CONTINUING CONTROL": "Satisfactory Continuing Control",

    # Maintenance (21 controls)
    "MAINTENANCE": "Maintenance",

    # Procurement (71 controls)
    "PROCUREMENT": "Procurement",

    # Title VI (not in current project 33, but exists in FY26)
    # Will be added later when Title VI controls are added to projects
    # "TITLE VI": "Title VI",

    # ADA - General (4 controls)
    "ADA GENERAL": "Americans with Disabilities Act (ADA) - General",

    # ADA - Complementary Paratransit (5 controls)
    "ADA COMPLEMENTARY PARATRANSIT": "Americans with Disabilities Act (ADA) - Complementary Paratransit",

    # School Bus (7 controls)
    "SCHOOL BUS": "School Bus",

    # Charter Bus (11 controls)
    "CHARTER BUS": "Charter Bus",

    # Drug-Free Workplace Act (10 controls total: 7 + 3)
    "DRUG FREE WORKPLACE ACT": "Drug-Free Workplace Act",
    "DRUG-FREE WORKPLACE ACT": "Drug-Free Workplace Act",  # Hyphenated variant

    # Drug and Alcohol Program (18 controls)
    "DRUG AND ALCOHOL PROGRAM": "Drug and Alcohol Program",

    # Section 5307 Program Requirements (24 controls)
    "SECTION 5307 PROGRAM REQUIREMENTS": "Section 5307 Program Requirements",

    # Section 5310 Program Requirements (21 controls)
    "SECTION 5310 PROGRAM REQUIREMENTS": "Section 5310 Program Requirements",

    # Section 5311 Program Requirements (33 controls)
    "SECTION 5311 PROGRAM REQUIREMENTS": "Section 5311 Program Requirements",

    # Public Transportation Agency Safety Plan (20 controls total: 14 + 6)
    "PUBLIC TRANSPORTATION AGENCY SAFETY PLAN": "Public Transportation Agency Safety Plan (PTASP)",
    "PTASP": "Public Transportation Agency Safety Plan (PTASP)",

    # Cybersecurity (2 controls)
    "CYBERSECURITY": "Cybersecurity",
}


# Review areas that exist in JSON schema but are NOT in FY26 CORTAP
# These will be marked as "NA" (Not Applicable) in the output
EXCLUDED_FY26_AREAS = [
    "Disadvantaged Business Enterprise",  # Removed from FY26
    "Equal Employment Opportunity",        # Removed from FY26
]


# Review areas that exist in FY26 but may not be in specific projects
# These should be marked as "NA" if no controls are found
OPTIONAL_AREAS = [
    "Title VI",  # Exists in FY26 (39 controls) but removed from project 33 for testing
]


def extract_control_prefix(control_name: str) -> Optional[str]:
    """
    Extract the review area prefix from a Riskuity control name.

    Args:
        control_name: Full control name (e.g., "LEGAL : L2")

    Returns:
        Normalized prefix (e.g., "LEGAL") or None if no match

    Examples:
        >>> extract_control_prefix("LEGAL : L2")
        "LEGAL"
        >>> extract_control_prefix("FINANCIAL MANAGEMENT : F4")
        "FINANCIAL MANAGEMENT"
        >>> extract_control_prefix("TECHNICAL CAPACITY – AWARD MANAGEMENT : TC-AM5")
        "TECHNICAL CAPACITY – AWARD MANAGEMENT"
    """
    if not control_name:
        return None

    # Match everything before the colon (handles en-dash and hyphen)
    match = re.match(r'^(.+?)\s*:', control_name)
    if match:
        prefix = match.group(1).strip()
        # Normalize whitespace
        prefix = re.sub(r'\s+', ' ', prefix)
        return prefix

    return None


def map_to_json_review_area(control_name: str) -> Optional[str]:
    """
    Map a Riskuity control name to its JSON review area name.

    Args:
        control_name: Full control name from Riskuity (e.g., "LEGAL : L2")

    Returns:
        JSON review area name or None if unmapped

    Examples:
        >>> map_to_json_review_area("LEGAL : L2")
        "Legal"
        >>> map_to_json_review_area("PROCUREMENT : P12")
        "Procurement"
        >>> map_to_json_review_area("TECHNICAL CAPACITY – AWARD MANAGEMENT : TC-AM5")
        "Technical Capacity - Award Management"
    """
    prefix = extract_control_prefix(control_name)
    if not prefix:
        return None

    return RISKUITY_PREFIX_TO_JSON_AREA.get(prefix)


def get_all_json_review_areas() -> list[str]:
    """
    Get all unique JSON review area names in canonical order.

    This includes areas from FY26 but excludes DBE and EEO (removed from FY26).
    Title VI is included but may be marked as "NA" if not in the project.

    Returns:
        List of 21 FY26 review area names
    """
    # Get unique values from mapping
    mapped_areas = set(RISKUITY_PREFIX_TO_JSON_AREA.values())

    # Add Title VI (exists in FY26 but may not be in all projects)
    mapped_areas.add("Title VI")

    # Sort alphabetically for consistency
    return sorted(mapped_areas)


def get_unmapped_areas() -> list[str]:
    """
    Get review areas that are excluded from FY26.

    These should be omitted from FY26 reports entirely.

    Returns:
        List of excluded review area names (DBE, EEO)
    """
    return EXCLUDED_FY26_AREAS.copy()


if __name__ == "__main__":
    # Test the mapping
    test_controls = [
        "LEGAL : L2",
        "FINANCIAL MANAGEMENT : F4",
        "TECHNICAL CAPACITY – AWARD MANAGEMENT : TC-AM5",
        "PROCUREMENT : P12",
        "DRUG-FREE WORKPLACE ACT : DFWA1",
        "SECTION 5307 PROGRAM REQUIREMENTS : 5307:1-A",
        "PTASP : PTASP1",
    ]

    print("Testing control name mapping:")
    print("=" * 80)
    for control_name in test_controls:
        prefix = extract_control_prefix(control_name)
        json_area = map_to_json_review_area(control_name)
        print(f"{control_name:60} -> {json_area}")

    print(f"\nTotal JSON review areas: {len(get_all_json_review_areas())}")
    print(f"Excluded from FY26: {', '.join(get_unmapped_areas())}")
