#!/usr/bin/env python3
"""Debug template syntax error by extracting the failing Jinja2 code."""

from docxtpl import DocxTemplate
import json
from datetime import datetime
import sys

def format_date(date_str):
    if not date_str:
        return ''
    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    return dt.strftime('%B %d, %Y')

template_path = 'app/templates/draft-audit-report-poc.docx'
data_path = 'tests/fixtures/mock-data/NTD_FY2023_TR.json'

print(f"Loading template: {template_path}")
template = DocxTemplate(template_path)

print(f"Loading data: {data_path}")
with open(data_path) as f:
    data = json.load(f)

context = data.copy()
context['date_format'] = format_date

print("Attempting to render...")

# Monkey-patch to capture the XML that fails to compile
original_render_xml_part = template.render_xml_part

def debug_render_xml_part(src_xml, *args, **kwargs):
    """Wrapper to capture failing XML."""
    try:
        return original_render_xml_part(src_xml, *args, **kwargs)
    except Exception as e:
        # Save the failing XML
        with open('output/failing_template.txt', 'w', encoding='utf-8') as f:
            f.write(src_xml)
        print(f"\n❌ Template compilation failed!")
        print(f"Saved failing template to: output/failing_template.txt")
        print(f"Error: {e}")

        # Try to parse to get better error info
        from jinja2 import Template, TemplateSyntaxError
        try:
            Template(src_xml)
        except TemplateSyntaxError as te:
            print(f"\nJinja2 Error Details:")
            print(f"  Message: {te.message}")
            print(f"  Line: {te.lineno}")

            # Show context around the error
            if te.source:
                lines = te.source.split('\n')
                if te.lineno and te.lineno <= len(lines):
                    start = max(0, te.lineno - 5)
                    end = min(len(lines), te.lineno + 5)
                    print(f"\n  Context around line {te.lineno}:")
                    for i in range(start, end):
                        marker = ">>>" if i == te.lineno - 1 else "   "
                        line_content = lines[i]
                        if len(line_content) > 200:
                            line_content = line_content[:200] + "..."
                        print(f"  {marker} {i+1:4d}: {line_content}")

        raise

template.render_xml_part = debug_render_xml_part

try:
    template.render(context)
    print("✅ Template rendered successfully!")
except Exception as e:
    print(f"\n❌ Final error: {e}")
    sys.exit(1)
