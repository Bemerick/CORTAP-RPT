#!/usr/bin/env python3
"""
Draft Report Template Validation Script

Purpose: Validate the draft-audit-report-poc.docx template syntax as it's being converted
         to python-docxtpl format with Jinja2 syntax.

Usage:
    # Quick syntax check (just load template):
    python scripts/validate_draft_template.py

    # Full validation with sample data rendering:
    python scripts/validate_draft_template.py --render

    # Test with specific mock JSON file:
    python scripts/validate_draft_template.py --render --data tests/fixtures/mock-data/NTD_FY2023_TR.json

Story: 1.5.5 - Convert Draft Report Template to python-docxtpl Format
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from docxtpl import DocxTemplate
    from jinja2.exceptions import TemplateSyntaxError, UndefinedError
except ImportError as e:
    print(f"❌ Error: Missing required package: {e}")
    print("   Install with: pip install python-docxtpl")
    sys.exit(1)


def format_date(date_str: str) -> str:
    """
    Format ISO date string to 'Month Day, Year' format.

    Args:
        date_str: ISO format date string (YYYY-MM-DD)

    Returns:
        Formatted date string (e.g., "March 28, 2023")
    """
    if not date_str:
        return ""
    try:
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.strftime("%B %d, %Y")
    except ValueError:
        return date_str


def load_mock_data(json_path: Path) -> Dict[str, Any]:
    """
    Load mock JSON data file.

    Args:
        json_path: Path to JSON file

    Returns:
        Dictionary with JSON data
    """
    print(f"📂 Loading mock data: {json_path.name}")

    with open(json_path, 'r') as f:
        data = json.load(f)

    print(f"   ✓ Loaded project: {data['project']['recipient_acronym']} - {data['project']['review_type']}")
    print(f"   ✓ Deficiencies: {data['metadata']['deficiency_count']}")
    print(f"   ✓ Assessments: {len(data['assessments'])} review areas")

    return data


def prepare_context(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare template context with formatted data and custom filters.

    Args:
        data: Raw JSON data

    Returns:
        Template context dictionary
    """
    # Create a copy to avoid modifying original
    context = data.copy()

    # Add date_format filter to the context
    # Note: python-docxtpl will use this when rendering {{ date | date_format }}
    context['date_format'] = format_date

    return context


def validate_template_syntax(template_path: Path) -> tuple[bool, str]:
    """
    Validate that the template loads without syntax errors.

    Args:
        template_path: Path to .docx template file

    Returns:
        Tuple of (success: bool, message: str)
    """
    print(f"\n🔍 Validating template: {template_path.name}")
    print(f"   Path: {template_path}")

    if not template_path.exists():
        return False, f"Template file not found: {template_path}"

    try:
        template = DocxTemplate(template_path)
        print("   ✓ Template loaded successfully")
        print("   ✓ No Jinja2 syntax errors detected")
        return True, "Template syntax is valid"

    except TemplateSyntaxError as e:
        return False, f"Jinja2 Syntax Error:\n{e}"

    except Exception as e:
        return False, f"Template Loading Error:\n{e}"


def validate_template_render(template_path: Path, data: Dict[str, Any], output_path: Path) -> tuple[bool, str]:
    """
    Validate that the template can be rendered with sample data.

    Args:
        template_path: Path to .docx template file
        data: Mock JSON data dictionary
        output_path: Where to save rendered document

    Returns:
        Tuple of (success: bool, message: str)
    """
    print(f"\n📝 Rendering template with sample data...")

    try:
        # Load template
        template = DocxTemplate(template_path)

        # Prepare context with date_format function
        context = data.copy()
        context['date_format'] = format_date

        # Render template
        print("   ⏳ Rendering document...")
        template.render(context)

        # Save output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        template.save(output_path)

        print(f"   ✓ Document rendered successfully")
        print(f"   ✓ Saved to: {output_path}")

        return True, f"Template rendered successfully to {output_path}"

    except UndefinedError as e:
        return False, f"Missing Data Field Error:\n{e}\n\nThis usually means the template references a field that doesn't exist in the JSON data."

    except TemplateSyntaxError as e:
        return False, f"Jinja2 Syntax Error:\n{e}"

    except Exception as e:
        return False, f"Rendering Error:\n{type(e).__name__}: {e}"


def main():
    """Main validation script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate Draft Report template syntax during conversion to python-docxtpl format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick syntax check:
  python scripts/validate_draft_template.py

  # Full validation with default mock data:
  python scripts/validate_draft_template.py --render

  # Test with specific JSON file:
  python scripts/validate_draft_template.py --render --data tests/fixtures/mock-data/GPTD_FY2023_TR.json
        """
    )

    parser.add_argument(
        '--render',
        action='store_true',
        help='Render template with sample data (not just syntax check)'
    )

    parser.add_argument(
        '--data',
        type=Path,
        help='Path to mock JSON data file (default: NTD_FY2023_TR.json)'
    )

    parser.add_argument(
        '--template',
        type=Path,
        default=Path('app/templates/draft-audit-report-poc.docx'),
        help='Path to template file (default: app/templates/draft-audit-report-poc.docx)'
    )

    parser.add_argument(
        '--output',
        type=Path,
        help='Path for rendered output (default: output/validation/Draft_Report_Test.docx)'
    )

    args = parser.parse_args()

    # Resolve paths relative to project root
    project_root = Path(__file__).parent.parent
    template_path = project_root / args.template

    print("=" * 80)
    print("Draft Report Template Validation")
    print("=" * 80)

    # Step 1: Syntax validation (always run)
    success, message = validate_template_syntax(template_path)

    if not success:
        print(f"\n❌ VALIDATION FAILED:\n{message}")
        sys.exit(1)

    print(f"   ✅ {message}")

    # Step 2: Render validation (if requested)
    if args.render:
        # Determine data file
        if args.data:
            data_path = project_root / args.data
        else:
            # Default to NTD (simplest case - 1 deficiency)
            data_path = project_root / 'tests/fixtures/mock-data/NTD_FY2023_TR.json'

        if not data_path.exists():
            print(f"\n❌ Mock data file not found: {data_path}")
            sys.exit(1)

        # Load data
        try:
            data = load_mock_data(data_path)
        except Exception as e:
            print(f"\n❌ Error loading JSON data:\n{e}")
            sys.exit(1)

        # Determine output path
        if args.output:
            output_path = project_root / args.output
        else:
            recipient_acronym = data['project']['recipient_acronym']
            output_path = project_root / f'output/validation/{recipient_acronym}_Draft_Report_Test.docx'

        # Render template
        success, message = validate_template_render(template_path, data, output_path)

        if not success:
            print(f"\n❌ RENDER VALIDATION FAILED:\n{message}")
            print("\nTroubleshooting Tips:")
            print("  • Check that all {{ field }} references match the JSON structure")
            print("  • Ensure {% if %} and {% endif %} blocks are properly closed")
            print("  • Verify table loops use {%r for %} ... {%r endfor %}")
            print("  • Review the conversion guide: docs/draft-report-template-conversion-guide.md")
            sys.exit(1)

        print(f"\n   ✅ {message}")

    # Success!
    print("\n" + "=" * 80)
    print("✅ VALIDATION PASSED")
    print("=" * 80)

    if args.render:
        print("\n💡 Next steps:")
        print("   1. Open the generated document to verify formatting")
        print("   2. Continue template conversion")
        print("   3. Run validation again after each major change")
        print("\n   Test with other mock files:")
        print("      python scripts/validate_draft_template.py --render --data tests/fixtures/mock-data/GPTD_FY2023_TR.json")
        print("      python scripts/validate_draft_template.py --render --data tests/fixtures/mock-data/MEVA_FY2023_TR.json")
    else:
        print("\n💡 Template syntax is valid!")
        print("   To test rendering with sample data:")
        print("      python scripts/validate_draft_template.py --render")

    print()


if __name__ == '__main__':
    main()
