#!/usr/bin/env python3
"""Get detailed Jinja2 error information"""

from pathlib import Path
from docxtpl import DocxTemplate
from jinja2 import Environment, TemplateSyntaxError

template_path = Path(__file__).parent.parent / 'app' / 'templates' / 'draft-audit-report-poc.docx'

print(f"Loading template: {template_path}")
template = DocxTemplate(template_path)
template.init_docx()

# Get the XML
xml = template.get_xml()

print(f"\nXML length: {len(xml)} characters")

# Try to compile with Jinja2 directly
print("\nAttempting to compile XML as Jinja2 template...")

env = Environment()
try:
    compiled = env.from_string(xml)
    print("✓ Template compiled successfully!")
except TemplateSyntaxError as e:
    print(f"\n❌ Jinja2 Syntax Error:")
    print(f"  Message: {e.message}")
    print(f"  Line: {e.lineno}")
    print(f"  Name: {e.name}")

    # Try to extract context around the error
    lines = xml.split('\n') if '\n' in xml else [xml]

    if len(lines) == 1:
        # XML is all on one line, need to find by character position
        print(f"\n  (XML is on a single line)")

        # Try to find the error by looking at the error context
        if hasattr(e, 'source'):
            print(f"\n  Error source available")

        # Extract all Jinja2 tokens to find which one is line 139
        import re
        tokens = []
        for match in re.finditer(r'({%.*?%}|{{.*?}})', xml):
            tokens.append((match.start(), match.end(), match.group(0)))

        print(f"\n  Found {len(tokens)} Jinja2 tokens")

        # Line 139 in the Jinja2 parser likely refers to the 139th token or thereabouts
        if len(tokens) >= 139:
            print(f"\n  Token around position 139:")
            for i in range(max(0, 136), min(len(tokens), 142)):
                clean = re.sub(r'<[^>]+>', '', tokens[i][2])
                marker = ">>> " if i == 138 else "    "
                print(f"{marker}{i+1}: {clean[:150]}")
    else:
        # Multi-line XML
        print(f"\n  Context around line {e.lineno}:")
        start = max(0, e.lineno - 3)
        end = min(len(lines), e.lineno + 3)
        for i in range(start, end):
            marker = ">>> " if i == e.lineno - 1 else "    "
            print(f"{marker}{i+1}: {lines[i][:200]}")
