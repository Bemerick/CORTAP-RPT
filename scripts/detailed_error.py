#!/usr/bin/env python3
"""Find the exact error location with context"""

from pathlib import Path
from docxtpl import DocxTemplate
from jinja2 import Environment, TemplateSyntaxError
import re

template_path = Path(__file__).parent.parent / 'app' / 'templates' / 'draft-audit-report-poc.docx'

print(f"Loading template: {template_path}")
template = DocxTemplate(template_path)
template.init_docx()

# Get the XML
xml = template.get_xml()

print(f"XML length: {len(xml)}\n")

# Try to compile with Jinja2
env = Environment()
try:
    compiled = env.from_string(xml)
    print("✅ Template compiled successfully!")
except TemplateSyntaxError as e:
    print(f"❌ Jinja2 Syntax Error:")
    print(f"  Message: {e.message}")
    print(f"  Line: {e.lineno}")

    # Split XML into logical segments (by Jinja2 expressions)
    segments = re.split(r'(\{[%{][^}]*[}%]\})', xml)

    # Find segment that has issues - look around the estimated position
    # Jinja2 line numbers in XML don't correspond to actual lines
    # Try compiling progressively
    print("\nTrying to find the problematic expression...")

    # Find all Jinja2 expressions
    expressions = list(re.finditer(r'(\{[%{][^}]*[}%]\})', xml))

    print(f"Found {len(expressions)} total Jinja2 expressions")
    print("\nChecking each expression individually...")

    for i, match in enumerate(expressions):
        expr_raw = match.group(1)
        expr_clean = re.sub(r'<[^>]+>', '', expr_raw)

        # Check if this expression has issues
        # Look for patterns that might cause "got integer" error
        if re.search(r'\s\d+\s|\s\d+[%}]', expr_clean):
            # Check if the digit is part of a valid expression
            if not re.search(r'["\'].*\d+.*["\']|==|!=', expr_clean):
                print(f"\n⚠️  Expression #{i+1} (position {match.start()}):")
                print(f"   Clean: {expr_clean}")

                # Show context
                ctx_start = max(0, match.start() - 200)
                ctx_end = min(len(xml), match.end() + 200)
                context = xml[ctx_start:ctx_end]
                context_clean = re.sub(r'<[^>]+>', '', context)
                print(f"   Context: ...{context_clean[:300]}...")
