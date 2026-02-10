#!/usr/bin/env python3
"""Extract raw XML to file for manual inspection"""

from pathlib import Path
from docxtpl import DocxTemplate

template_path = Path(__file__).parent.parent / 'app' / 'templates' / 'draft-audit-report-poc.docx'
output_path = Path(__file__).parent.parent / 'output' / 'template_xml.txt'

print(f"Loading template: {template_path}")
template = DocxTemplate(template_path)
template.init_docx()

# Get the XML
xml = template.get_xml()

# Write to file
output_path.parent.mkdir(exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(xml)

print(f"XML written to: {output_path}")
print(f"XML length: {len(xml)} characters")

# Also try to parse with Jinja2 to get the exact error
from jinja2 import Environment, TemplateSyntaxError

env = Environment()
try:
    compiled = env.from_string(xml)
    print("✓ Template compiled successfully!")
except TemplateSyntaxError as e:
    print(f"\n❌ Jinja2 Syntax Error:")
    print(f"  Message: {e.message}")
    print(f"  Line: {e.lineno}")

    # Try to extract a chunk of XML around the error
    # Since XML is on one line, use character position estimation
    # Assume roughly 4000 chars per "line" from Jinja2's perspective
    if e.lineno:
        approx_pos = e.lineno * 4000
        start = max(0, approx_pos - 500)
        end = min(len(xml), approx_pos + 500)

        context = xml[start:end]

        print(f"\n  Approximate context (chars {start}-{end}):")
        print(f"  {context[:1000]}")

        # Look for Jinja2 expressions in this region
        import re
        jinja_in_context = re.findall(r'({%[^}]*%}|{{[^}]*}})', context)
        if jinja_in_context:
            print(f"\n  Jinja2 expressions in this area:")
            for expr in jinja_in_context[:10]:
                clean = re.sub(r'<[^>]+>', '', expr)
                print(f"    - {clean}")
