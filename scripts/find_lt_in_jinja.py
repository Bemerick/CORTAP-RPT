#!/usr/bin/env python3
"""Find < or > characters in Jinja2 expressions"""

from pathlib import Path
import re

xml_path = Path(__file__).parent.parent / 'output' / 'template_xml.txt'

print(f"Reading XML from: {xml_path}")
with open(xml_path, 'r', encoding='utf-8') as f:
    xml = f.read()

print("\n" + "="*80)
print("SEARCHING FOR < OR > IN JINJA2 EXPRESSIONS")
print("="*80)

# Find all Jinja2 expressions
expressions = re.findall(r'({%[^}]*%}|{{[^}]*}})', xml)

print(f"\nTotal Jinja2 expressions: {len(expressions)}")

issues = []

for expr in expressions:
    # Clean XML tags
    clean = re.sub(r'<[^>]+>', '', expr)

    # Now check if there are still < or > characters
    if '<' in clean or '>' in clean:
        # Count them
        lt_count = clean.count('<')
        gt_count = clean.count('>')

        # Check if they're part of comparison operators
        has_lte = '<=' in clean
        has_gte = '>=' in clean
        has_lt = '<' in clean and not has_lte
        has_gt = '>' in clean and not has_gte

        # If there are naked < or >, that's the problem
        if has_lt or has_gt:
            issues.append((expr, clean, has_lt, has_gt, has_lte, has_gte))

if issues:
    print(f"\n⚠️  Found {len(issues)} expressions with < or > characters:\n")
    for i, (raw, clean, has_lt, has_gt, has_lte, has_gte) in enumerate(issues, 1):
        print(f"{i}. Expression (first 200 chars):")
        print(f"   Raw: {raw[:200]}")
        print(f"   Clean: {clean}")
        print(f"   Has <: {has_lt}, Has >: {has_gt}, Has <=: {has_lte}, Has >=: {has_gte}")
        print()

        if i >= 20:
            print(f"... and {len(issues) - 20} more")
            break
else:
    print("\n✓ No < or > characters found in Jinja2 expressions")
