#!/usr/bin/env python3
"""Find the exact location of the Jinja2 syntax error"""

from pathlib import Path
from jinja2 import Environment, TemplateSyntaxError
import re

xml_path = Path(__file__).parent.parent / 'output' / 'template_xml.txt'

print(f"Reading XML from: {xml_path}")
with open(xml_path, 'r', encoding='utf-8') as f:
    xml = f.read()

print(f"XML length: {len(xml)} characters\n")

# Try to compile with Jinja2
env = Environment()
try:
    compiled = env.from_string(xml)
    print("✓ Template compiled successfully!")
except TemplateSyntaxError as e:
    print(f"❌ Jinja2 Syntax Error:")
    print(f"  Message: {e.message}")
    print(f"  Line: {e.lineno}")
    print(f"  Name: {e.name}")

    # Try to find the problematic area
    # The XML is mostly on one line, so we need to search by character position
    # Estimate: roughly 7000 chars per "line" from Jinja2's perspective

    if e.lineno:
        # Search for Jinja2 expressions around the estimated position
        estimated_pos = e.lineno * 7000
        start = max(0, estimated_pos - 2000)
        end = min(len(xml), estimated_pos + 2000)

        chunk = xml[start:end]

        print(f"\n  Searching in region: chars {start}-{end}")

        # Find all Jinja2 expressions in this chunk
        expressions = []
        for match in re.finditer(r'(\{\{[^}]*\}\}|{%[^}]*%})', chunk):
            expr_raw = match.group(1)
            expr_clean = re.sub(r'<[^>]+>', '', expr_raw)
            expr_pos = start + match.start()
            expressions.append((expr_pos, expr_raw[:200], expr_clean))

        if expressions:
            print(f"\n  Found {len(expressions)} Jinja2 expressions in this region:")
            for pos, raw, clean in expressions[-10:]:  # Show last 10
                print(f"\n    Position {pos}:")
                print(f"    Clean: {clean}")
                if len(raw) > 150:
                    print(f"    Raw: {raw[:150]}...")
                else:
                    print(f"    Raw: {raw}")

    # Let's also try a different approach: search for common problematic patterns
    print("\n" + "="*80)
    print("SEARCHING FOR PROBLEMATIC PATTERNS")
    print("="*80)

    # Pattern 1: Naked integers in statements
    print("\n1. Checking for naked integers in {% %} statements:")
    for match in re.finditer(r'{%([^}]+)%}', xml):
        stmt = match.group(1)
        stmt_clean = re.sub(r'<[^>]+>', '', stmt)

        # Look for integers that aren't in quotes and aren't part of operators
        # This is tricky - let's look for space + digits + space
        if re.search(r'\s\d+\s|\s\d+$|^\d+\s', stmt_clean):
            # But exclude things like: | length > 0, array[0], etc.
            if not re.search(r'[>\<=\[]|\|\s*\w+', stmt_clean):
                print(f"   Found: {stmt_clean.strip()}")

    # Pattern 2: Check for < or > outside of comparisons
    print("\n2. Checking for < or > characters in expressions:")
    for match in re.finditer(r'(\{\{[^}]*\}\}|{%[^}]*%})', xml):
        expr = match.group(1)
        expr_clean = re.sub(r'<[^>]+>', '', expr)

        # Look for < or > that aren't part of <= or >=
        if '<' in expr_clean or '>' in expr_clean:
            # Check if they're comparison operators
            if not re.search(r'<=|>=|<|>', expr_clean):
                print(f"   Found: {expr_clean[:200]}")
