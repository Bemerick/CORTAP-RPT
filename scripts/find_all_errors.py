#!/usr/bin/env python3
"""Find all potential Jinja2 syntax errors"""

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
print("COMPREHENSIVE SYNTAX ERROR SEARCH")
print("="*80)

# Find all Jinja2 expressions
expressions = []

# Find {{ }} expressions
for match in re.finditer(r'{{[^}]+}}', xml):
    expr = match.group(0)
    clean = re.sub(r'<[^>]+>', '', expr)
    expressions.append(('var', clean, match.start()))

# Find {% %} statements
for match in re.finditer(r'{%[^}]+%}', xml):
    expr = match.group(0)
    clean = re.sub(r'<[^>]+>', '', expr)
    expressions.append(('stmt', clean, match.start()))

print(f"\nTotal expressions: {len(expressions)}")

issues = []

print("\n" + "="*80)
print("CHECKING FOR COMMON SYNTAX ERRORS")
print("="*80)

for expr_type, expr, pos in expressions:
    # 1. Check for bare numbers (not in strings)
    # Look for spaces followed by digit(s) followed by space or end
    if re.search(r'\s\d{4}(?!\d)', expr):
        # Exclude if it's clearly in a string or part of a longer number
        if "'" not in expr[expr.find(re.search(r'\s\d{4}(?!\d)', expr).group(0).strip()):]:
            # Check if the number appears outside quotes
            parts = expr.split("'")
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Outside quotes
                    if re.search(r'\s\d{4}(?!\d)', part):
                        issues.append((expr, f"Possible bare number outside quotes: {re.search(r'\d{4}', part).group(0)}"))
                        break

    # 2. Unbalanced quotes
    single_quotes = expr.count("'")
    if single_quotes % 2 != 0:
        issues.append((expr, f"Unbalanced single quotes: {single_quotes} quotes"))

    double_quotes = expr.count('"')
    if double_quotes % 2 != 0:
        issues.append((expr, f"Unbalanced double quotes: {double_quotes} quotes"))

    # 3. Missing operators between values
    if re.search(r"'\s+\d+\s+", expr):
        issues.append((expr, "String followed by number without operator"))

    if re.search(r"\d+\s+'", expr):
        issues.append((expr, "Number followed by string without operator"))

    # 4. Function call with missing parentheses
    if re.search(r'date_format\s+[^(]', expr):
        issues.append((expr, "date_format without parentheses"))

    # 5. Check for misplaced operators
    if re.search(r'==\s*$', expr):
        issues.append((expr, "== operator at end of expression"))

if issues:
    print(f"\n⚠️  Found {len(issues)} potential issues:\n")
    for i, (expr, issue) in enumerate(issues, 1):
        print(f"{i}. {issue}")
        print(f"   {expr}")
        print()
else:
    print("\n✓ No syntax issues detected by automated checks")

print("\n" + "="*80)
print("CHECKING SPECIFIC PATTERNS")
print("="*80)

# Look for any expression with year-like numbers
year_exprs = [expr for _, expr, _ in expressions if re.search(r'\b20\d{2}\b', expr)]
if year_exprs:
    print(f"\nFound {len(year_exprs)} expressions with year-like numbers:")
    for expr in year_exprs[:10]:
        print(f"  - {expr}")

# Look for expressions with FY
fy_exprs = [expr for _, expr, _ in expressions if 'FY' in expr]
if fy_exprs:
    print(f"\nFound {len(fy_exprs)} expressions with 'FY':")
    for expr in fy_exprs[:10]:
        print(f"  - {expr}")

# Look for numeric literals
numeric_exprs = [expr for _, expr, _ in expressions if re.search(r'\s\d+\s', expr) and '+' not in expr]
if numeric_exprs:
    print(f"\nFound {len(numeric_exprs)} expressions with numeric literals:")
    for expr in numeric_exprs[:20]:
        print(f"  - {expr}")
