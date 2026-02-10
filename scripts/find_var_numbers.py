#!/usr/bin/env python3
"""Find bare numbers in {{ }} variable expressions"""

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
print("FINDING BARE NUMBERS IN VARIABLE EXPRESSIONS {{ }}")
print("="*80)

# Extract all {{ ... }} blocks
var_pattern = r'{{[^}]*}}'
variables = re.findall(var_pattern, xml)

issues = []

for var in variables:
    clean = re.sub(r'<[^>]+>', '', var)

    # Look for 4-digit numbers in various contexts
    if re.search(r'\d{4}', clean):
        # Check if the number appears in a problematic way

        # Pattern 1: String literal with number not using concatenation
        if re.search(r"'[^']*\d{4}[^']*'", clean):
            if '+' not in clean:
                match = re.search(r"'([^']*\d{4}[^']*)'", clean)
                if match:
                    issues.append(('String with 4-digit number (no concatenation)', clean, match.group(1)))

        # Pattern 2: Bare year-like number
        # e.g., {{ project.fiscal_year - 1 }} might have issues if year literal appears
        if re.search(r'\s\d{4}(?:\s|}})', clean):
            # Check if it's part of an operation
            match = re.search(r'(\s)(\d{4})(?:\s|}})', clean)
            if match:
                # If there's no operator before it, it might be problematic
                before_number = clean[:match.start(2)]
                if not any(op in before_number[-5:] for op in ['-', '+', '*', '/', '==', '!=', '>=', '<=', '(', ',']):
                    issues.append(('Bare 4-digit number', clean, match.group(2)))

        # Pattern 3: FY followed by number
        if 'FY' in clean and re.search(r'FY\s*\d{4}', clean):
            issues.append(('FY + year', clean))

print(f"\nChecked {len(variables)} variable expressions")

if issues:
    print(f"\n⚠️  Found {len(issues)} potential issues:\n")
    seen = set()
    for issue in issues:
        if len(issue) == 2:
            issue_type, var = issue
            key = (issue_type, var)
        else:
            issue_type, var, detail = issue
            key = (issue_type, var, detail)

        if key not in seen:
            seen.add(key)
            if len(issue) == 2:
                print(f"• {issue_type}")
                print(f"  {var}")
            else:
                print(f"• {issue_type}")
                print(f"  Detail: {detail}")
                print(f"  {var}")
            print()
else:
    print("\n✓ No bare number issues found in variable expressions")
