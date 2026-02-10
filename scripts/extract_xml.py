#!/usr/bin/env python3
"""Extract XML from Word document to find syntax errors"""

from pathlib import Path
from docxtpl import DocxTemplate
import re

template_path = Path(__file__).parent.parent / 'app' / 'templates' / 'draft-audit-report-poc.docx'

print(f"Loading template: {template_path}")
template = DocxTemplate(template_path)

# Initialize the template to parse the document
template.init_docx()

# Get the XML
xml = template.get_xml()

# Split into lines
lines = xml.split('\n')

print(f"\nTotal lines: {len(lines)}")
print("\n" + "="*80)
print("Lines 135-145 (around error line 139):")
print("="*80)

for i in range(134, min(145, len(lines))):
    line_num = i + 1
    prefix = ">>> " if line_num == 139 else "    "
    print(f"{prefix}{line_num}: {lines[i][:200]}")

# Also search for common problematic patterns
print("\n" + "="*80)
print("Searching for potential problematic patterns:")
print("="*80)

# Pattern 1: Numbers followed by text without operators
pattern1 = re.findall(r'{%[^}]*?\d+\s+\w+[^}]*?%}', xml)
if pattern1:
    print("\n⚠️  Found numbers with text (might be missing operators):")
    for match in pattern1[:5]:
        print(f"  - {match}")

# Pattern 2: date_format with wrong syntax
pattern2 = re.findall(r'{{\s*date_format[^}]{0,100}}}', xml)
if pattern2:
    print(f"\n🔍 Found {len(pattern2)} date_format calls:")
    for match in pattern2[:10]:
        print(f"  - {match}")

# Pattern 3: Assignment instead of comparison
pattern3 = re.findall(r'{%\s*if[^}]*?=(?!=)[^}]*?%}', xml)
if pattern3:
    print("\n⚠️  Found single = in if statements (should be ==):")
    for match in pattern3[:5]:
        print(f"  - {match}")

# Pattern 4: Look for line 139 content specifically
print("\n" + "="*80)
print("Full content of line 139:")
print("="*80)
if len(lines) > 138:
    print(lines[138])
