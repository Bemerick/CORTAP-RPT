#!/usr/bin/env python3
"""
Generate RIR Cover Letters from Excel Spreadsheet

This script generates RIR cover letters from the CORTAP Package 4 spreadsheet.
It reads recipient data from the Excel file and generates cover letter documents
using the Jinja2 template.

Usage:
    python scripts/generate_cover_letters_from_excel.py

Input:
    docs/RIR 2026/RIR Cover Letter/CORTAP Package 4 - Reviews - SM Updated 122325.xlsx

Output:
    Generated documents saved to: output/cover-letters-fy2026/
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import re
from docxtpl import DocxTemplate
from xml.sax.saxutils import escape as xml_escape

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


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


def get_regional_administrator(region_code: str) -> str:
    """
    Get regional administrator name based on region code.

    Args:
        region_code: Region code (e.g., "TRO-1")

    Returns:
        Regional administrator name
    """
    # Map region codes to administrators
    # This is a placeholder - update with actual administrator names
    region_map = {
        "TRO-1": "Joanna Reyes-Boyle",
        "TRO-2": "Shantha Muthiah-Maney",
        "TRO-3": "Yvette G. Taylor",
        "TRO-4": "Kelley Brookins",
        "TRO-5": "Linda Gehrke",
        "TRO-6": "Marisol R. Simón",
        "TRO-7": "Linda Gehrke",
        "TRO-8": "Terry Lee Shelton",
        "TRO-9": "Ray Tellis",
        "TRO-10": "Ray Tellis",
    }
    return region_map.get(str(region_code).strip(), "Regional Administrator")


def add_article_to_review_type(review_type: str) -> str:
    """
    Add article (a/an) to review type.

    Args:
        review_type: Review type (e.g., "Triennial Review")

    Returns:
        Review type with article (e.g., "a Triennial Review")
    """
    review_type = str(review_type).strip()

    # Determine article based on first letter
    if review_type[0].lower() in ['a', 'e', 'i', 'o', 'u']:
        return f"an {review_type}"
    return f"a {review_type}"


def get_title_prefix(name: str) -> str:
    """
    Get Mr./Ms. prefix for a name.

    Args:
        name: Person's name

    Returns:
        "Mr." or "Ms." prefix with name
    """
    # Simple heuristic - can be enhanced with a gender lookup
    # For now, default to "Mr./Ms."
    if not name or name.upper() == "TBD":
        return "TBD"
    return f"Mr./Ms. {name}"


def format_date_for_letter(date_value) -> str:
    """
    Format a date value for display in the cover letter.

    Args:
        date_value: Date value from Excel (datetime or string)

    Returns:
        Formatted date string (e.g., "February 27, 2026") or "TBD"
    """
    if pd.isna(date_value):
        return "TBD"

    if isinstance(date_value, datetime):
        return date_value.strftime("%B %d, %Y")

    # Try to parse string dates
    try:
        dt = pd.to_datetime(date_value)
        return dt.strftime("%B %d, %Y")
    except:
        return "TBD"


def escape_xml_chars(text: str) -> str:
    """
    Escape XML special characters in text.

    Args:
        text: Text to escape

    Returns:
        XML-escaped text
    """
    if not text or text == "TBD":
        return text
    return xml_escape(str(text))


def row_to_cover_letter_context(row: pd.Series) -> dict:
    """
    Convert a spreadsheet row to cover letter template context.

    Args:
        row: Pandas Series representing one spreadsheet row

    Returns:
        Context dict for cover letter template
    """
    # Get basic recipient info from Excel columns (escape XML chars)
    recipient_name = escape_xml_chars(str(row.get('Recip Name', '')).strip())
    recipient_acronym = escape_xml_chars(str(row.get('Recipient Accronym', '')).strip())
    address = escape_xml_chars(str(row.get('Recip Address', '')).strip())
    city = escape_xml_chars(str(row.get('Recip City', '')).strip())
    state = str(row.get('Recip State', '')).strip()
    zip_code = str(row.get('Recip Zip', '')).strip()

    # Get review type (already full name in Excel)
    review_type = str(row.get('Review Type', 'Triennial Review')).strip()
    review_type_article = add_article_to_review_type(review_type)

    # Get contractor name from Excel
    contractor_name = str(row.get('Contractor Company', 'Longevity')).strip()
    # If it's just "Longevity", expand to full name
    if contractor_name == "Longevity":
        contractor_name = "Longevity Consulting"

    # Get lead reviewer info
    lead_salutation = str(row.get('Lead Reviewer Salutation', 'Mr./Ms.')).strip()
    lead_name = str(row.get('Lead Reviewer Name', 'TBD')).strip()
    lead_title_name = f"{lead_salutation} {lead_name}" if lead_name != "TBD" else "TBD"

    # Get lead email and phone from Excel (use TBD if not available)
    lead_email_raw = row.get('Lead Reviewer Email')
    lead_email = str(lead_email_raw).strip() if pd.notna(lead_email_raw) and str(lead_email_raw).strip() else "TBD"

    lead_phone_raw = row.get('Lead Reviewer Phone')
    lead_phone = str(lead_phone_raw).strip() if pd.notna(lead_phone_raw) and str(lead_phone_raw).strip() else "TBD"

    # Get Regional Office Rep info
    ro_rep_salutation = str(row.get('RO Rep Salu', 'Mr./Ms.')).strip()
    ro_rep_name = str(row.get('RO Rep Name', 'TBD')).strip()
    ro_rep_title_name = f"{ro_rep_salutation} {ro_rep_name}" if ro_rep_name != "TBD" else "TBD"
    ro_rep_phone = str(row.get('RO Rep Phone', 'TBD')).strip()
    ro_rep_email = str(row.get('RO Rep email', 'TBD')).strip()

    # Get Regional Administrator name
    regional_admin_name = str(row.get('RO Admin Name', 'Regional Administrator')).strip()

    # Get due date from Date column
    letter_date_value = row.get('Date')
    letter_date = format_date_for_letter(letter_date_value)

    # Due date is calculated as letter date + ~45 days (February 27, 2026)
    # For now, use fixed date from original template
    rir_due_date_formatted = "February 27, 2026"

    # Recipient contact info from Excel (escape XML chars)
    recipient_contact_name = escape_xml_chars(str(row.get('Recip AE Name', 'Transit Agency Contact')).strip())
    recipient_contact_title = escape_xml_chars(str(row.get('Recip Title', 'Executive Director')).strip())

    # Build context
    context = {
        'letter_date': letter_date,
        'recipient_contact_name': recipient_contact_name,
        'recipient_contact_title': recipient_contact_title,
        'recipient_name': recipient_name,
        'street_address': address,
        'city': city,
        'state': state,
        'zip_code': zip_code,
        'review_type': review_type,
        'review_type_article': review_type_article,
        'recipient_acronym': recipient_acronym,
        'contractor_name': contractor_name,
        'lead_title_name': lead_title_name,
        'lead_email': lead_email,
        'lead_phone': lead_phone,
        'rir_due_date_formatted': rir_due_date_formatted,
        'ro_rep_title_name': ro_rep_title_name,
        'ro_rep_phone': ro_rep_phone,
        'ro_rep_email': ro_rep_email,
        'regional_admin_name': regional_admin_name,
    }

    return context


def generate_cover_letter_from_row(
    template_path: Path,
    row: pd.Series,
    output_dir: Path,
    row_number: int
) -> tuple[bool, str]:
    """
    Generate a single cover letter document from a spreadsheet row.

    Args:
        template_path: Path to the Jinja2 template file
        row: Pandas Series with recipient data
        output_dir: Directory to save the document
        row_number: Row number for logging

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Get recipient info for naming
        recipient_id = str(row.get('Recipient ID', '')).strip()
        recipient_name = str(row.get('Recip Name', '')).strip()

        # Generate safe filename
        safe_name = sanitize_filename(recipient_name)
        filename = f"CoverLetter_{recipient_id}_{safe_name}_FY2026.docx"
        output_path = output_dir / filename

        # Build context
        context = row_to_cover_letter_context(row)

        # Load template and render
        doc = DocxTemplate(template_path)
        doc.render(context)

        # Save document
        doc.save(output_path)

        file_size = output_path.stat().st_size
        message = f"✓ [{row_number:2d}] {recipient_name[:40]:40s} -> {filename} ({file_size:,} bytes)"
        return True, message

    except Exception as e:
        recipient_name = str(row.get('Recip Name', 'Unknown'))[:40]
        message = f"✗ [{row_number:2d}] {recipient_name:40s} -> Error: {str(e)}"
        return False, message


def main():
    """Main script execution."""
    print("=" * 80)
    print("RIR Cover Letter Generator - Excel Spreadsheet")
    print("=" * 80)

    # Setup paths
    project_root = Path(__file__).parent.parent
    excel_path = project_root / "docs" / "RIR 2026" / "RIR Cover Letter" / "CORTAP Package 4 - Reviews - SM Updated 122325.xlsx"
    template_path = project_root / "app" / "templates" / "rir-cover-letter.docx"

    # Create output directory
    output_dir = project_root / "output" / "cover-letters-fy2026"

    # Verify Excel file exists
    if not excel_path.exists():
        print(f"\n✗ Error: Excel file not found: {excel_path}")
        sys.exit(1)

    # Verify template exists
    if not template_path.exists():
        print(f"\n✗ Error: Template file not found: {template_path}")
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nInput file: {excel_path.name}")
    print(f"Template: {template_path.name}")
    print(f"Output directory: {output_dir}")

    # Read Excel file
    print(f"\nReading Excel file...")
    sheet_name = "RIR Cover Letter 2026 Info"
    try:
        # Read from the RIR Cover Letter 2026 Info sheet
        df = pd.read_excel(excel_path, sheet_name=sheet_name, header=0)

        print(f"  Sheet: {sheet_name}")
        print(f"  Found {len(df)} recipients")

    except Exception as e:
        print(f"\n✗ Error reading Excel file: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Generate documents
    print(f"\n{'=' * 80}")
    print(f"Generating {len(df)} cover letter documents...")
    print(f"{'=' * 80}\n")

    results = []
    messages = []

    for idx, row in df.iterrows():
        success, message = generate_cover_letter_from_row(
            template_path,
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
        print(f"\n✓ All {len(df)} cover letter documents generated successfully!")
        print(f"\nOutput directory: {output_dir}")
    else:
        print(f"\n⚠ Some documents failed to generate:")
        for i, (success, message) in enumerate(zip(results, messages)):
            if not success:
                print(f"  {message}")
        print(f"\nOutput directory: {output_dir}")


if __name__ == "__main__":
    main()
