#!/usr/bin/env python3
"""Find FY and year patterns that might cause syntax errors"""

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
print("SEARCHING FOR FY + YEAR PATTERNS")
print("="*80)

# Find all Jinja2 expressions with years
patterns_to_check = [
    (r'FY\s*\d{4}', 'FY followed by year'),
    (r'FY\d{4}', 'FY immediately followed by year'),
    (r'fiscal Year[^}]*\d{4}', 'fiscal Year with 4-digit number'),
    (r'Year[^}]*\d{4}', 'Year with 4-digit number'),
]

for pattern, desc in patterns_to_check:
    matches = re.findall(pattern, xml)
    if matches:
        print(f"\n{desc}: Found {len(matches)} instances")
        # Show unique matches
        unique = list(set(matches))[:10]
        for match in unique:
            print(f"  - {match}")

# Look specifically in Jinja2 contexts
print("\n" + "="*80)
print("CHECKING JINJA2 EXPRESSIONS WITH YEARS")
print("="*80)

jinja_exprs = re.findall(r'({%[^}]+%}|{{[^}]+}})', xml)
problem_exprs = []

for expr in jinja_exprs:
    clean = re.sub(r'<[^>]+>', '', expr)

    # Check if contains year-like number
    if re.search(r'\d{4}', clean):
        # Check if it's problematic
        if 'FY' in clean:
            problem_exprs.append((clean, 'Contains FY + year'))
        elif re.search(r"['\"].*\d{4}.*['\"]", clean):
            # Year is in a string, might be OK or might not be
            if '+' not in clean:
                problem_exprs.append((clean, 'Year in string without concatenation'))

if problem_exprs:
    print(f"\nFound {len(problem_exprs)} potentially problematic expressions:")
    for expr, reason in problem_exprs[:15]:
        print(f"\n{reason}:")
        print(f"  {expr}")
else:
    print("\n✓ No problematic year expressions found")
