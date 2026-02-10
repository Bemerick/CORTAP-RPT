#!/usr/bin/env python3
"""Find bare numbers in Jinja2 contexts"""

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
print("FINDING BARE NUMBERS IN STATEMENT BLOCKS")
print("="*80)

# Extract all {% ... %} blocks
stmt_pattern = r'{%[^}]*%}'
statements = re.findall(stmt_pattern, xml)

issues = []

for stmt in statements:
    clean = re.sub(r'<[^>]+>', '', stmt)

    # Look for patterns that indicate a bare number
    # Pattern 1: == "NUMBER" where NUMBER should be a string
    if re.search(r'==\s*"5\d{3}"', clean):
        issues.append(('Comparing to program section as string', clean))

    # Pattern 2: Space followed by 4-digit number followed by space or %}
    # But exclude cases where the number is clearly in a string or after an operator
    if re.search(r'[^"\'\d]\s+\d{4}(?:\s|%})', clean):
        # Make sure it's not part of a longer number or in a string
        match = re.search(r'([^"\'\d]\s+)(\d{4})(?:\s|%})', clean)
        if match:
            context = match.group(1) + match.group(2)
            # Check if this looks problematic
            if '==' not in context and '!=' not in context and '+' not in context and '-' not in context:
                issues.append(('Bare 4-digit number in statement', clean, match.group(2)))

    # Pattern 3: Literal string with number that might get broken
    # Look for strings like "text 5307" where the number might get split
    if re.search(r"('[^']*5\d{3}[^']*'|\"[^\"]*5\d{3}[^\"]*\")", clean):
        # Check if using concatenation
        if '+' not in clean:
            match = re.search(r"('[^']*5\d{3}[^']*'|\"[^\"]*5\d{3}[^\"]*\")", clean)
            if match:
                issues.append(('String with 5XXX number (no concatenation)', clean, match.group(1)))

print(f"\nChecked {len(statements)} statements")

if issues:
    print(f"\n⚠️  Found {len(issues)} potential issues:\n")
    for issue in issues:
        if len(issue) == 2:
            issue_type, stmt = issue
            print(f"• {issue_type}")
            print(f"  {stmt}")
        else:
            issue_type, stmt, detail = issue
            print(f"• {issue_type}")
            print(f"  Detail: {detail}")
            print(f"  {stmt}")
        print()
else:
    print("\n✓ No bare number issues found in statements")

# Also check for the specific pattern that causes "got 'integer'" error
print("\n" + "="*80)
print("CHECKING FOR SPECIFIC ERROR PATTERNS")
print("="*80)

# The error "got 'integer'" typically means Jinja2 parsed a number token
# where it didn't expect one. Common causes:
# 1. {% set var = STRING 5307 %} - string split by XML
# 2. {% if condition 5307 %} - number appearing after condition
# 3. {% for item in items 5307 %} - number appearing after iterator

problem_patterns = []

for stmt in statements:
    clean = re.sub(r'<[^>]+>', '', stmt)

    # Check if there's a number appearing where it shouldn't
    # Look for: word/symbol SPACE DIGIT SPACE/END
    if re.search(r'\w\s+\d{4}(?:\s|%})', clean):
        if "==" not in clean and "'" not in clean and '"' not in clean:
            match = re.search(r'(\w+)\s+(\d{4})(?:\s|%})', clean)
            if match:
                problem_patterns.append((clean, f'{match.group(1)} followed by {match.group(2)}'))

if problem_patterns:
    print(f"\n⚠️  Found {len(problem_patterns)} patterns that could cause 'got integer' error:\n")
    for stmt, detail in problem_patterns:
        print(f"• {detail}")
        print(f"  {stmt}")
        print()
else:
    print("\n✓ No 'got integer' error patterns found")
