#!/usr/bin/env python3
"""Try to identify the syntax error by parsing incrementally"""

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
print("ANALYZING JINJA2 SYNTAX")
print("="*80)

# Find all Jinja2 expressions
expressions = []

# Find {{ }} expressions
for match in re.finditer(r'{{[^}]+}}', xml):
    expr = match.group(0)
    # Clean XML tags
    clean = re.sub(r'<[^>]+>', '', expr)
    expressions.append(('variable', clean, match.start()))

# Find {% %} statements
for match in re.finditer(r'{%[^}]+%}', xml):
    expr = match.group(0)
    # Clean XML tags
    clean = re.sub(r'<[^>]+>', '', expr)
    expressions.append(('statement', clean, match.start()))

print(f"\nFound {len(expressions)} Jinja2 expressions")

# Look for problematic patterns
print("\n" + "="*80)
print("CHECKING FOR SYNTAX ERRORS")
print("="*80)

issues = []

for expr_type, expr, pos in expressions:
    # Check for numbers followed by non-operators
    if re.search(r'\d{4}\s+\w+', expr):
        if 'Section' not in expr:  # Section 5307 is OK
            issues.append((expr, "Number followed by text without operator"))

    # Check for 'Section NNNN' used incorrectly
    if re.search(r"Section\s+\d{4}[^'\")}]", expr):
        issues.append((expr, "Section number not in quotes or not properly terminated"))

    # Check for missing closing parentheses
    open_parens = expr.count('(')
    close_parens = expr.count(')')
    if open_parens != close_parens:
        issues.append((expr, f"Mismatched parentheses: {open_parens} open, {close_parens} close"))

    # Check for assignment instead of comparison
    if expr_type == 'statement' and ' if ' in expr:
        # Look for single = not part of ==, !=, <=, >=
        if re.search(r'[^=!<>]=(?!=)', expr):
            issues.append((expr, "Single = in if statement (should be ==)"))

if issues:
    print(f"\n⚠️  Found {len(issues)} potential issues:\n")
    for i, (expr, issue) in enumerate(issues[:20], 1):
        print(f"{i}. {issue}")
        print(f"   Expression: {expr}")
        print()
else:
    print("\n✓ No obvious syntax issues found")

# Try to find expressions with "Section" followed by numbers
print("\n" + "="*80)
print("SECTION NUMBER USAGE")
print("="*80)

section_exprs = [expr for _, expr, _ in expressions if 'Section' in expr and re.search(r'\d{4}', expr)]
print(f"\nFound {len(section_exprs)} expressions with 'Section' and 4-digit numbers:")
for i, expr in enumerate(section_exprs[:10], 1):
    print(f"{i}. {expr}")
