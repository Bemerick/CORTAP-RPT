#!/usr/bin/env python3
"""Quick template test with detailed error output"""

import sys
from pathlib import Path
import json
from docxtpl import DocxTemplate

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

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

# Load template
template_path = Path(__file__).parent.parent / 'app' / 'templates' / 'draft-audit-report-poc.docx'
data_path = Path(__file__).parent.parent / 'tests' / 'fixtures' / 'mock-data' / 'NTD_FY2023_TR.json'

print(f"Loading template: {template_path}")
template = DocxTemplate(template_path)

print(f"Loading data: {data_path}")
with open(data_path) as f:
    data = json.load(f)

print(f"Rendering...")
context = data.copy()
context['date_format'] = format_date

try:
    template.render(context)
    print("✅ Success!")
    output_path = Path(__file__).parent.parent / 'output' / 'quick_test.docx'
    output_path.parent.mkdir(exist_ok=True)
    template.save(output_path)
    print(f"Saved to: {output_path}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
