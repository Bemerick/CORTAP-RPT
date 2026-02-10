#!/usr/bin/env python3
"""Find years or numbers adjacent to Jinja2 expressions"""

from pathlib import Path
import re

xml_path = Path(__file__).parent.parent / 'output' / 'template_xml.txt'

print(f"Reading XML from: {xml_path}")
with open(xml_path, 'r', encoding='utf-8') as f:
    xml = f.read()

print("\n" + "="*80)
print("SEARCHING FOR YEARS ADJACENT TO JINJA2")
print("="*80)

# Find all Jinja2 expressions and surrounding context
pattern = r'.{0,50}(\{\{[^}]*\}\}|{%[^}]*%}).{0,50}'
matches = re.finditer(pattern, xml)

issues = []

for match in matches:
    context = match.group(0)
    expr = match.group(1)

    # Clean XML tags to see what text would actually appear
    clean = re.sub(r'<[^>]+>', '', context)

    # Look for 4-digit numbers (especially years) near the expression
    if re.search(r'\d{4}', clean):
        # Check if there's a year right before {{
        if re.search(r'20[0-9]{2}\s*\{\{|FY\s*20[0-9]{2}\s*\{\{|[^0-9]20[0-9]{2}\s*{%', clean):
            issues.append((clean, context[:200]))

if issues:
    print(f"\n⚠️  Found {len(issues)} potential year adjacency issues:\n")
    for i, (clean, raw) in enumerate(issues[:20], 1):
        print(f"{i}. Clean text: {clean}")
        print(f"   Raw XML (first 200 chars): {raw}")
        print()
else:
    print("\n✓ No year adjacency issues found")

# Also search for bare integers in statements
print("\n" + "="*80)
print("SEARCHING FOR BARE INTEGERS IN JINJA2 STATEMENTS")
print("="*80)

statement_pattern = r'{%([^}]+)%}'
statements = re.findall(statement_pattern, xml)

bare_int_issues = []

for stmt in statements:
    # Clean XML tags
    clean = re.sub(r'<[^>]+>', '', stmt)

    # Look for 4-digit numbers that aren't in quotes
    if re.search(r'[^"\']20[0-9]{2}[^"\']|[^"\'][0-9]{4}[^"\']', clean):
        # Check if it's actually bare (not in a string)
        if '"' not in clean or "'" not in clean or not re.search(r'["\'][^"\']*[0-9]{4}[^"\']*["\']', clean):
            bare_int_issues.append(clean)

if bare_int_issues:
    print(f"\n⚠️  Found {len(bare_int_issues)} statements with potential bare integers:\n")
    for i, stmt in enumerate(bare_int_issues[:20], 1):
        print(f"{i}. {stmt}")
else:
    print("\n✓ No bare integers in statements")
