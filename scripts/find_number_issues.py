#!/usr/bin/env python3
"""Find all places where numbers might cause syntax errors"""

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
print("SEARCHING FOR PROBLEMATIC NUMBER PATTERNS")
print("="*80)

# Find all Jinja2 statements ({% %})
stmt_pattern = r'{%[^}]+%}'
statements = re.findall(stmt_pattern, xml)

print(f"\nFound {len(statements)} statements")

# Clean and check each
issues = []
for stmt in statements:
    clean = re.sub(r'<[^>]+>', '', stmt)

    # Pattern 1: '5307' style string with number that might get broken
    if re.search(r"'[^']*\d{4}[^']*'", clean):
        # Check if it's using concatenation
        if '+' not in clean:
            match = re.search(r"'([^']*\d{4}[^']*)'", clean)
            if match:
                issues.append(('String with 4-digit number (not concatenated)', clean, match.group(1)))

    # Pattern 2: Bare numbers in comparisons
    if re.search(r'==\s*\d+\s', clean) or re.search(r'\s\d+\s*==', clean):
        match = re.search(r'(==\s*\d+|\d+\s*==)', clean)
        if match:
            # This is usually OK, but flag it
            pass  # Actually this is fine

    # Pattern 3: Numbers in set statements
    if 'set ' in clean and re.search(r"=\s*\d{4}", clean):
        match = re.search(r"(set\s+\w+\s*=\s*\d{4})", clean)
        if match:
            issues.append(('Setting variable to bare 4-digit number', clean, match.group(1)))

    # Pattern 4: FY2023 style strings
    if re.search(r"'[^']*FY\s*\d{4}[^']*'", clean):
        match = re.search(r"'([^']*FY\s*\d{4}[^']*)'", clean)
        if match:
            if '+' not in clean:
                issues.append(('FY + year string (not concatenated)', clean, match.group(1)))

if issues:
    print(f"\n⚠️  Found {len(issues)} potential issues:\n")
    for issue_type, stmt, detail in issues:
        print(f"• {issue_type}")
        print(f"  Detail: {detail}")
        print(f"  Full: {stmt}")
        print()
else:
    print("\n✓ No problematic number patterns found in statements")

# Also check variable expressions {{ }}
print("\n" + "="*80)
print("CHECKING VARIABLE EXPRESSIONS")
print("="*80)

var_pattern = r'{{[^}]+}}'
variables = re.findall(var_pattern, xml)

print(f"\nFound {len(variables)} variable expressions")

var_issues = []
for var in variables:
    clean = re.sub(r'<[^>]+>', '', var)

    # Check for strings with years/numbers
    if re.search(r"'[^']*\d{4}[^']*'", clean):
        if '+' not in clean:
            match = re.search(r"'([^']*\d{4}[^']*)'", clean)
            if match:
                var_issues.append(('String with 4-digit number', clean, match.group(1)))

if var_issues:
    print(f"\n⚠️  Found {len(var_issues)} potential issues in variable expressions:\n")
    for issue_type, var, detail in var_issues[:20]:
        print(f"• {issue_type}")
        print(f"  Detail: {detail}")
        print(f"  Full: {var}")
        print()
else:
    print("\n✓ No problematic number patterns found in variable expressions")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"\nTotal potential issues: {len(issues) + len(var_issues)}")
if issues or var_issues:
    print("\nRecommendation: Use string concatenation for all strings containing 4-digit numbers:")
    print("  Instead of: 'Text 2023 more'")
    print("  Use: 'Text ' + '2023' + ' more'")
