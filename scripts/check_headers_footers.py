#!/usr/bin/env python3
"""Check headers and footers for Jinja2 syntax issues"""

from pathlib import Path
from docxtpl import DocxTemplate
import re

template_path = Path(__file__).parent.parent / 'app' / 'templates' / 'draft-audit-report-poc.docx'

print(f"Loading template: {template_path}")
template = DocxTemplate(template_path)

# Get headers and footers
headers_footers = template.get_headers_footers()

print(f"\n" + "="*80)
print("CHECKING HEADERS AND FOOTERS")
print("="*80)

if headers_footers:
    print(f"\nFound {len(headers_footers)} header/footer parts")

    for i, (part, xml) in enumerate(headers_footers, 1):
        print(f"\n--- Part {i}: {part} ---")

        # Find Jinja2 expressions
        expressions = re.findall(r'({%[^}]*%}|{{[^}]*}})', xml)

        if expressions:
            print(f"Found {len(expressions)} Jinja2 expressions:")
            for expr in expressions[:10]:
                clean = re.sub(r'<[^>]+>', '', expr)
                print(f"  - {clean}")

                # Check for problematic patterns
                if re.search(r'\d{4}', clean):
                    # Check if using concatenation
                    if '+' not in clean and "'" in clean:
                        print(f"    ⚠️  Contains 4-digit number in string without concatenation")

                if '<' in clean or '>' in clean:
                    print(f"    ⚠️  Contains < or > character")
        else:
            print("No Jinja2 expressions")

        # Check for years in plain text near Jinja2
        if re.search(r'20[2-5]\d', xml):
            print(f"  Contains year literal (2020-2059)")

else:
    print("\nNo headers/footers found or unable to retrieve them")
