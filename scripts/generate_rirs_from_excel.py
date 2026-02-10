#!/usr/bin/env python3
"""
Generate RIR Documents from Excel Spreadsheet

This script generates RIR documents from the CORTAP Package 4 spreadsheet.
It reads recipient data from the Excel file, transforms it to the canonical
JSON format, and generates RIR documents using the existing infrastructure.

Usage:
    python scripts/generate_rirs_from_excel.py

Input:
    docs/RIR 2026/CORTAP Package 4 - Reviews - SM Updated_ET_120325.xlsx

Output:
    Generated documents saved to: output/rir-documents-fy2026/
"""

import pandas as pd
import asyncio
from pathlib import Path
from datetime import datetime
import re
from html import escape

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.document_generator import DocumentGenerator
from app.services.context_builder import RIRContextBuilder
from app.utils.logging import get_logger

logger = get_logger(__name__)


def clean_recipient_name(name: str) -> str:
    """
    Remove the prepended recipient ID from the recipient name.

    Args:
        name: Raw recipient name (e.g., "1337 GREATER NEW HAVEN TRANSIT DISTRICT")

    Returns:
        Cleaned name (e.g., "GREATER NEW HAVEN TRANSIT DISTRICT")
    """
    # Remove first 4 characters (recipient ID) and any leading/trailing whitespace
    if len(name) > 4:
        return name[4:].strip()
    return name.strip()


def sanitize_filename(name: str) -> str:
    """
    Sanitize a string for use in a filename.

    Args:
        name: String to sanitize

    Returns:
        Safe filename string
    """
    # Remove or replace invalid filename characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    # Remove multiple underscores
    name = re.sub(r'_+', '_', name)
    # Limit length
    return name[:100]


def extract_region_number(region_code: str) -> int:
    """
    Extract region number from region code.

    Args:
        region_code: Region code (e.g., "TRO-1", "TRO-10")

    Returns:
        Region number as integer
    """
    # Extract number from region code (e.g., "TRO-1" -> 1)
    match = re.search(r'-?(\d+)$', str(region_code))
    if match:
        return int(match.group(1))
    # Default to 1 if can't extract
    return 1


def map_review_type(review_code: str) -> str:
    """
    Map review type code to full name.

    Args:
        review_code: Review code (e.g., "TR")

    Returns:
        Full review type name
    """
    mapping = {
        "TR": "Triennial Review",
        "TRIENNIAL": "Triennial Review",
        "TRIENNIAL REVIEW": "Triennial Review"
    }
    return mapping.get(str(review_code).upper().strip(), "Triennial Review")


def format_phone(phone) -> str:
    """
    Format phone number or return TBD.

    Args:
        phone: Phone number value

    Returns:
        Formatted phone string
    """
    if pd.isna(phone):
        return "TBD"
    phone_str = str(phone).strip()
    if not phone_str or phone_str.upper() == "TBD":
        return "TBD"
    return phone_str


def format_date_for_display(date_value) -> str:
    """
    Format a date value for display in the RIR document.

    Args:
        date_value: Date value from Excel (datetime or string)

    Returns:
        Formatted date string (YYYY-MM-DD) or "TBD"
    """
    if pd.isna(date_value):
        return "TBD"

    if isinstance(date_value, datetime):
        return date_value.strftime("%Y-%m-%d")

    # Try to parse string dates
    try:
        dt = pd.to_datetime(date_value)
        return dt.strftime("%Y-%m-%d")
    except:
        return "TBD"


def row_to_canonical_json(row: pd.Series) -> dict:
    """
    Convert a spreadsheet row to canonical JSON format.

    Args:
        row: Pandas Series representing one spreadsheet row

    Returns:
        Canonical JSON dict for RIR generation
    """
    # Extract recipient name (no longer has ID prefix) and escape XML special characters
    recipient_name = escape(str(row.get('Recipient Name', '')).strip())

    # Format city, state
    city = str(row.get('City', '')).strip()
    state = str(row.get('State', '')).strip()
    recipient_city_state = f"{city}, {state}" if city and state else "N/A"

    # Extract region number
    region_number = extract_region_number(row.get('Region #', 'TRO-1'))

    # Map review type
    review_type = map_review_type(row.get('Type of Review', 'TR'))

    # Format site visit dates
    site_visit_start = format_date_for_display(row.get('FY26 Visit Start'))
    site_visit_end = format_date_for_display(row.get('FY26 Visit End (Complete by Sept 30, 2026)'))

    # Format due date
    due_date = format_date_for_display(row.get('FY26 RIR Due'))

    # Get FTA PM info
    fta_pm_name = str(row.get('FTA PM', '')).strip() or "TBD"
    fta_pm_title = str(row.get('FTA PM Title', '')).strip() or "TBD"
    fta_pm_phone = format_phone(row.get('FTA PM Phone'))
    fta_pm_email = str(row.get('FTA PM Email', '')).strip() or "TBD"

    # Get Lead Reviewer info
    lead_name = str(row.get('Lead', '')).strip() or "TBD"
    lead_email = str(row.get('Lead Email', '')).strip() or "TBD"
    lead_phone = format_phone(row.get('Lead Phone'))

    # Get website from spreadsheet
    website = str(row.get('Website', '')).strip() or "N/A"

    # Build canonical JSON structure
    canonical_json = {
        "project": {
            "region_number": region_number,
            "review_type": review_type,
            "recipient_name": recipient_name,
            "recipient_city_state": recipient_city_state,
            "recipient_id": str(row.get('Recipient ID', '')).strip(),
            "recipient_website": website,
            "site_visit_start_date": site_visit_start,
            "site_visit_end_date": site_visit_end,
            "due_date": due_date
        },
        "contractor": {
            "contractor_name": "Longevity Consulting",
            "lead_reviewer_name": lead_name,
            "lead_reviewer_phone": lead_phone,
            "lead_reviewer_email": lead_email
        },
        "fta_program_manager": {
            "fta_program_manager_name": fta_pm_name,
            "fta_program_manager_title": fta_pm_title,
            "fta_program_manager_phone": fta_pm_phone,
            "fta_program_manager_email": fta_pm_email
        }
    }

    return canonical_json


async def generate_rir_from_row(
    generator: DocumentGenerator,
    row: pd.Series,
    output_dir: Path,
    row_number: int
) -> tuple[bool, str]:
    """
    Generate a single RIR document from a spreadsheet row.

    Args:
        generator: DocumentGenerator instance
        row: Pandas Series with recipient data
        output_dir: Directory to save the document
        row_number: Row number for logging

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Get recipient info for naming
        recipient_id = str(row.get('Recipient ID', '')).strip()
        recipient_name = str(row.get('Recipient Name', '')).strip()

        # Generate safe filename
        safe_name = sanitize_filename(recipient_name)
        filename = f"RIR_{recipient_id}_{safe_name}_FY2026.docx"
        output_path = output_dir / filename

        # Convert to canonical JSON
        json_data = row_to_canonical_json(row)

        # Build RIR context
        context = RIRContextBuilder.build_context(
            json_data,
            correlation_id=f"excel-{recipient_id}"
        )

        # Generate document
        document = await generator.generate(
            template_id="rir-package",
            context=context,
            correlation_id=f"excel-{recipient_id}"
        )

        # Save document
        with open(output_path, 'wb') as f:
            document.seek(0)
            f.write(document.read())

        file_size = output_path.stat().st_size
        message = f"✓ [{row_number:2d}] {recipient_name[:40]:40s} -> {filename} ({file_size:,} bytes)"
        return True, message

    except Exception as e:
        recipient_name = str(row.get('Recipient Name', 'Unknown'))[:40]
        message = f"✗ [{row_number:2d}] {recipient_name:40s} -> Error: {str(e)}"
        logger.error(f"Failed to generate RIR for row {row_number}", exc_info=True)
        return False, message


async def main():
    """Main script execution."""
    print("=" * 80)
    print("RIR Document Generator - Excel Spreadsheet")
    print("=" * 80)

    # Setup paths
    project_root = Path(__file__).parent.parent
    excel_path = project_root / "docs" / "RIR 2026" / "CORTAP Package 4 - Reviews - SM Updated 121025.xlsx"
    excel_sheet = "Package 4 - Longevity"
    template_dir = project_root / "app" / "templates"

    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = project_root / "output" / "rir-documents-fy2026" / timestamp

    # Verify Excel file exists
    if not excel_path.exists():
        print(f"\n✗ Error: Excel file not found: {excel_path}")
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nInput file: {excel_path.name}")
    print(f"Output directory: {output_dir}")

    # Read Excel file
    print(f"\nReading Excel file...")
    print(f"  Sheet: {excel_sheet}")
    try:
        # Read from Package 4 - Longevity sheet, skip first 2 rows (header row is row 3)
        df = pd.read_excel(excel_path, sheet_name=excel_sheet, skiprows=2)

        print(f"  Found {len(df)} recipients")

    except Exception as e:
        print(f"\n✗ Error reading Excel file: {str(e)}")
        sys.exit(1)

    # Initialize DocumentGenerator
    print(f"\nInitializing DocumentGenerator...")
    print(f"  Template directory: {template_dir}")
    generator = DocumentGenerator(template_dir=str(template_dir))

    # Generate documents
    print(f"\n{'=' * 80}")
    print(f"Generating {len(df)} RIR documents...")
    print(f"{'=' * 80}\n")

    results = []
    messages = []

    for idx, row in df.iterrows():
        success, message = await generate_rir_from_row(
            generator,
            row,
            output_dir,
            idx + 1
        )
        results.append(success)
        messages.append(message)
        print(message)

    # Summary
    print(f"\n{'=' * 80}")
    print(f"Generation Summary")
    print(f"{'=' * 80}")
    print(f"Total recipients: {len(df)}")
    print(f"Successful: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")

    if all(results):
        print(f"\n✓ All {len(df)} RIR documents generated successfully!")
        print(f"\nOutput directory: {output_dir}")
    else:
        print(f"\n⚠ Some documents failed to generate:")
        for i, (success, message) in enumerate(zip(results, messages)):
            if not success:
                print(f"  {message}")
        print(f"\nOutput directory: {output_dir}")


if __name__ == "__main__":
    # Run async main
    asyncio.run(main())
