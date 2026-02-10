#!/usr/bin/env python3
"""Simplest possible render test"""

import sys
from pathlib import Path
import json
from docxtpl import DocxTemplate
from jinja2 import Environment

# Load template
template_path = Path(__file__).parent.parent / 'app' / 'templates' / 'draft-audit-report-poc.docx'
data_path = Path(__file__).parent.parent / 'tests' / 'fixtures' / 'mock-data' / 'NTD_FY2023_TR.json'

print(f"Loading template: {template_path}")
template = DocxTemplate(template_path)

print(f"Loading data: {data_path}")
with open(data_path) as f:
    data = json.load(f)

def format_date(date_str):
    """Format date string"""
    from datetime import datetime
    if not date_str:
        return ''
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%B %d, %Y')
    except:
        return date_str

context = data.copy()
context['date_format'] = format_date

print(f"\nAttempting to render...")
try:
    # Try to build the XML which triggers Jinja2 compilation
    env = Environment()
    template.render(context)
    print("✅ Success!")

except Exception as e:
    print(f"❌ Error: {e}")

    # Get more details
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()

    # Try to get the problematic section
    print("\nAttempting to identify problematic area...")

    # Get the XML and try to compile it with Jinja2
    template2 = DocxTemplate(template_path)
    xml = template2.get_xml()

    print(f"XML length: {len(xml)}")

    # Try compiling with Jinja2 directly
    try:
        env.from_string(xml)
    except Exception as e2:
        print(f"\nJinja2 compilation error: {e2}")

        # See if we can extract context
        if hasattr(e2, 'lineno'):
            print(f"Error at Jinja2 line: {e2.lineno}")
