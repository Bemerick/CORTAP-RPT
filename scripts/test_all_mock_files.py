#!/usr/bin/env python3
"""
Test template with all mock JSON files and generate separate output for each.

Usage:
    python scripts/test_all_mock_files.py app/templates/draft-report-working.docx
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


def test_with_data_file(template_path, data_path, output_dir):
    """Test template with specific data file."""

    data_file_name = data_path.stem  # e.g., "NTD_FY2023_TR"

    print(f"\n{'='*70}")
    print(f"Testing: {data_file_name}")
    print(f"{'='*70}")

    # Load template
    try:
        template = DocxTemplate(template_path)
        print("✅ Template loaded")
    except Exception as e:
        print(f"❌ Template load failed: {e}")
        return False

    # Load data
    try:
        with open(data_path) as f:
            data = json.load(f)
        print("✅ Data loaded")
    except Exception as e:
        print(f"❌ Data load failed: {e}")
        return False

    # Prepare context
    context = data.copy()
    context['date_format'] = format_date

    # Render
    try:
        template.render(context, autoescape=True)
        print("✅ Template rendered")
    except Exception as e:
        print(f"❌ Render failed: {e}")
        return False

    # Save with unique name based on data file
    output_path = output_dir / f"draft-report-{data_file_name}.docx"
    try:
        template.save(output_path)
        print(f"✅ Output saved: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Save failed: {e}")
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/test_all_mock_files.py <template.docx>")
        print("Example: python scripts/test_all_mock_files.py app/templates/draft-report-working.docx")
        sys.exit(1)

    template_path = Path(sys.argv[1])

    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        sys.exit(1)

    # Find all mock data files
    mock_data_dir = Path('tests/fixtures/mock-data')
    json_files = sorted(mock_data_dir.glob('*.json'))

    if not json_files:
        print(f"❌ No JSON files found in {mock_data_dir}")
        sys.exit(1)

    print(f"\nFound {len(json_files)} mock data files:")
    for f in json_files:
        print(f"  - {f.name}")

    # Create output directory
    output_dir = Path('output/all-mock-tests')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Test each file
    results = {}
    for data_path in json_files:
        success = test_with_data_file(template_path, data_path, output_dir)
        results[data_path.name] = success

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}\n")

    passed = sum(1 for v in results.values() if v)
    failed = len(results) - passed

    for filename, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {filename}")

    print(f"\nTotal: {passed}/{len(results)} passed, {failed} failed")

    if failed == 0:
        print(f"\n🎉 All tests passed! Output files in: {output_dir}")
        print("\nGenerated files:")
        for output_file in sorted(output_dir.glob('*.docx')):
            print(f"  - {output_file.name}")
        sys.exit(0)
    else:
        print(f"\n❌ {failed} test(s) failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
