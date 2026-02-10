#!/usr/bin/env python3
"""Simple template test to diagnose rendering issues."""

import sys
import json
from pathlib import Path
from docxtpl import DocxTemplate

project_root = Path(__file__).parent.parent
template_path = project_root / "app/templates/draft-audit-report-poc.docx"
data_path = project_root / "tests/fixtures/mock-data/NTD_FY2023_TR.json"

print("Testing template rendering...")
print(f"Template: {template_path}")
print(f"Data: {data_path}")
print()

try:
    # Load data
    with open(data_path, 'r') as f:
        data = json.load(f)
    print("✓ Data loaded")

    # Load template
    print("Loading template...")
    template = DocxTemplate(str(template_path))
    print(f"✓ Template loaded: {template}")
    print(f"  Template type: {type(template)}")

    # Try to get jinja env
    print("Getting Jinja environment...")
    try:
        jinja_env = template.get_jinja_env()
        print(f"✓ Jinja env: {jinja_env}")
    except AttributeError as e:
        print(f"✗ Cannot get Jinja env: {e}")
        print(f"  Template attributes: {dir(template)}")
        sys.exit(1)

    # Try to render
    print("Rendering template...")
    template.render(data)
    print("✓ Template rendered")

    # Save
    output_path = project_root / "output/test_simple.docx"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    template.save(str(output_path))
    print(f"✓ Saved to: {output_path}")

    print("\n✅ SUCCESS!")

except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
