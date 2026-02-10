#!/usr/bin/env python3
"""Check for malformed statement blocks"""

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
print("EXTRACTING ALL STATEMENT BLOCKS")
print("="*80)

# Find all {% ... %} blocks
pattern = r'{%[^}]*%}'
matches = list(re.finditer(pattern, xml))

print(f"\nFound {len(matches)} statement blocks")

# Check each one
issues = []
for i, match in enumerate(matches, 1):
    stmt = match.group(0)
    clean = re.sub(r'<[^>]+>', '', stmt)

    # Check if statement ends properly
    if not clean.strip().endswith('%}'):
        issues.append((i, 'Statement does not end with %}', clean, stmt[:200]))
        continue

    # Check for incomplete statements
    if clean.count('{%') != clean.count('%}'):
        issues.append((i, 'Unbalanced {%/%}', clean, stmt[:200]))
        continue

    # Check for specific problematic patterns
    # Pattern: Something followed by a bare number before %}
    if re.search(r'\s\d{4}\s*%}', clean):
        issues.append((i, 'Bare 4-digit number before %}', clean, stmt[:300]))

    # Pattern: String that might be broken 'text 1234'
    if re.search(r"'\w+\s+\d{4}", clean):
        # Check if it's part of a concatenation
        if '+' not in clean:
            issues.append((i, 'String with space + number (might be broken)', clean, stmt[:300]))

if issues:
    print(f"\n⚠️  Found {len(issues)} potential issues:\n")
    for num, issue_type, clean, raw in issues:
        print(f"#{num}: {issue_type}")
        print(f"  Clean: {clean}")
        print(f"  Raw (first 200 chars): {raw}")
        print()
else:
    print("\n✓ All statement blocks appear well-formed")

# Try a different approach - look for all instances of 4-digit numbers
# outside of proper contexts
print("\n" + "="*80)
print("SEARCHING FOR 4-DIGIT NUMBERS IN JINJA2 CONTEXTS")
print("="*80)

# Extract just the Jinja2 parts
jinja_parts = []
for match in re.finditer(r'({%.*?%}|{{.*?}})', xml):
    jinja_parts.append(match.group(1))

# Clean them
cleaned_jinja = []
for part in jinja_parts:
    clean = re.sub(r'<[^>]+>', '', part)
    cleaned_jinja.append(clean)

# Find all with 4-digit numbers
with_numbers = [j for j in cleaned_jinja if re.search(r'\d{4}', j)]

print(f"\nFound {len(with_numbers)} Jinja2 expressions containing 4-digit numbers:")
for i, expr in enumerate(with_numbers[:30], 1):
    print(f"{i}. {expr}")
