#!/usr/bin/env python3
"""Find all date-related expressions in template"""

from pathlib import Path
from docxtpl import DocxTemplate
import re

template_path = Path(__file__).parent.parent / 'app' / 'templates' / 'draft-audit-report-poc.docx'

print(f"Loading template: {template_path}")
template = DocxTemplate(template_path)
template.init_docx()

# Get the XML
xml = template.get_xml()

print("\n" + "="*80)
print("SEARCHING FOR DATE FIELDS")
print("="*80)

# Find all expressions with "date" in them
date_fields = [
    'project.report_date',
    'project.scoping_meeting_date',
    'project.site_visit_start_date',
    'project.site_visit_end_date',
    'project.exit_conference_date',
    'assessment.due_date',
    'assessment.date_closed',
    'area.due_date',
    'area.date_closed'
]

for field in date_fields:
    # Search for this field in any {{ }} or {% %} context
    pattern = re.escape(field)
    matches = re.finditer(pattern, xml)

    found = False
    for match in matches:
        if not found:
            print(f"\n✓ Found references to: {field}")
            found = True

        # Get context around the match (200 chars before and after)
        start = max(0, match.start() - 200)
        end = min(len(xml), match.end() + 200)
        context = xml[start:end]

        # Clean up XML tags
        clean = re.sub(r'<[^>]+>', '', context)
        # Highlight the field
        clean = clean.replace(field, f">>>{field}<<<")

        # Truncate if too long
        if len(clean) > 300:
            clean = clean[:300] + "..."

        print(f"  Context: {clean}")

    if not found:
        print(f"\n✗ NOT FOUND: {field}")

print("\n" + "="*80)
print("SEARCHING FOR DATE-RELATED FUNCTION CALLS OR FILTERS")
print("="*80)

# Look for any date formatting
patterns = [
    (r'date_format\([^)]*\)', 'date_format() function calls'),
    (r'\|\s*date_format', 'date_format filter syntax (old style)'),
    (r'\|\s*strftime', 'strftime filter'),
    (r'strftime\(', 'strftime() function'),
]

for pattern, desc in patterns:
    matches = re.findall(pattern, xml)
    if matches:
        print(f"\n✓ Found {desc}:")
        for match in matches[:5]:
            clean = re.sub(r'<[^>]+>', '', match)
            print(f"  - {clean}")
    else:
        print(f"\n✗ NOT found: {desc}")
