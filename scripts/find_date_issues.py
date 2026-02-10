#!/usr/bin/env python3
"""Find date_format syntax issues in template"""

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
print("SEARCHING FOR date_format ISSUES")
print("="*80)

# Find all date_format calls
date_formats = re.findall(r'date_format\([^)]{0,150}\)', xml)

print(f"\nFound {len(date_formats)} date_format() calls:")
for i, match in enumerate(date_formats, 1):
    # Clean up XML tags to make it readable
    clean = re.sub(r'<[^>]+>', '', match)
    print(f"\n{i}. {clean}")

# Look for problematic patterns with date_format
print("\n" + "="*80)
print("CHECKING FOR COMMON ERRORS")
print("="*80)

# Pattern: date_format with a literal number
if re.search(r'date_format\(\s*\d+', xml):
    print("\n⚠️  Found date_format with literal number!")
    matches = re.findall(r'date_format\(\s*\d+[^)]*\)', xml)
    for match in matches:
        clean = re.sub(r'<[^>]+>', '', match)
        print(f"  - {clean}")

# Pattern: date_format with wrong quotes
if re.search(r"date_format\([^)]*'[0-9]{4}", xml):
    print("\n⚠️  Found date_format with year in quotes!")
    matches = re.findall(r"date_format\([^)]*'[0-9]{4}[^)]*\)", xml)
    for match in matches:
        clean = re.sub(r'<[^>]+>', '', match)
        print(f"  - {clean}")

# Pattern: Look for any {{ }} expression with just a number
print("\n" + "="*80)
print("SEARCHING FOR NUMERIC EXPRESSIONS")
print("="*80)

# This would catch things like {{ 2023 }} or {{ project.2023 }}
numeric_exprs = re.findall(r'{{\s*[^}]*?\d{4}[^}]*?}}', xml)
if numeric_exprs:
    print(f"\nFound {len(numeric_exprs)} expressions with 4-digit numbers:")
    for i, match in enumerate(numeric_exprs[:10], 1):
        clean = re.sub(r'<[^>]+>', '', match)
        print(f"{i}. {clean}")

# Look for Section NNNN patterns that might be problematic
print("\n" + "="*80)
print("CHECKING SECTION REFERENCES")
print("="*80)

sections = re.findall(r"'Section \d{4}[^']*'", xml)
print(f"\nFound {len(sections)} Section NNNN references:")
for section in set(sections)[:5]:
    print(f"  - {section}")

print("\n✓ If these all look correct, the issue might be elsewhere in the template")
