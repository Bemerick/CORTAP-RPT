#!/usr/bin/env python3
"""
Quick test of template after adding a section.

Tests both syntax validity and rendering with test data.
"""

import sys
from pathlib import Path
import json
from docxtpl import DocxTemplate
from datetime import datetime


def format_date(date_str):
    """Format date string."""
    if not date_str:
        return ''
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%B %d, %Y')
    except:
        return date_str


def test_template(template_path, data_path=None):
    """Test template syntax and rendering."""

    template_path = Path(template_path)

    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        return False

    # Default test data
    if data_path is None:
        data_path = Path('tests/fixtures/mock-data/NTD_FY2023_TR.json')

    print(f"Testing: {template_path}")
    print(f"Data: {data_path}\n")

    # Load template
    try:
        template = DocxTemplate(template_path)
        print("✅ Template loads successfully")
    except Exception as e:
        print(f"❌ Template load failed: {e}")
        return False

    # Load data
    try:
        with open(data_path) as f:
            data = json.load(f)
        print("✅ Test data loaded")
    except Exception as e:
        print(f"❌ Data load failed: {e}")
        return False

    # Prepare context
    context = data.copy()
    context['date_format'] = format_date

    # Try to render
    try:
        template.render(context, autoescape=True)
        print("✅ Template renders successfully")
    except Exception as e:
        print(f"❌ Render failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Save output
    output_dir = Path('output/incremental')
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{template_path.stem}_test.docx"
    template.save(output_path)
    print(f"✅ Output saved: {output_path}\n")

    print("=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nYou can now:")
    print("  1. Open the output to verify formatting")
    print(f"     open {output_path}")
    print("  2. Add the next section to your template")
    print("  3. Run this test again\n")

    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        # Default to the working template
        template_path = 'app/templates/draft-audit-report-poc.docx'
    else:
        template_path = sys.argv[1]

    data_path = sys.argv[2] if len(sys.argv) > 2 else None

    success = test_template(template_path, data_path)
    sys.exit(0 if success else 1)
