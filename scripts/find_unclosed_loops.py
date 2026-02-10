#!/usr/bin/env python3
"""
Find unclosed for loops in Word template.

Usage:
    python scripts/find_unclosed_loops.py app/templates/draft-report-working.docx
"""

import sys
import re
from pathlib import Path
from docxtpl import DocxTemplate
from lxml import etree


def extract_all_text_with_tags(template_path):
    """Extract all text content including Jinja2 tags."""
    template = DocxTemplate(template_path)
    doc_element = template.get_docx()._element

    # Get XML as string
    xml_content = etree.tostring(doc_element, encoding='unicode')

    return xml_content


def find_jinja_tags(xml_content):
    """Find all Jinja2 tags with their positions."""
    # Pattern to match Jinja2 tags (for/endfor)
    pattern = r'\{%\s*(?:p\s+)?(?:tr\s+)?(for|endfor|if|elif|else|endif)\s*[^%]*%\}'

    tags = []
    for match in re.finditer(pattern, xml_content):
        tag = match.group(0)
        position = match.start()

        # Determine tag type
        if 'endfor' in tag:
            tag_type = 'endfor'
        elif 'for' in tag:
            tag_type = 'for'
        elif 'endif' in tag:
            tag_type = 'endif'
        elif 'elif' in tag:
            tag_type = 'elif'
        elif 'else' in tag and 'endelse' not in tag:
            tag_type = 'else'
        elif 'if' in tag and 'endif' not in tag:
            tag_type = 'if'
        else:
            tag_type = 'unknown'

        # Get context (50 chars before and after)
        context_start = max(0, position - 100)
        context_end = min(len(xml_content), position + len(tag) + 100)
        context = xml_content[context_start:context_end]

        tags.append({
            'tag': tag,
            'type': tag_type,
            'position': position,
            'context': context
        })

    return tags


def find_unclosed_loops(tags):
    """Find for loops that don't have matching endfor."""
    loop_stack = []
    unclosed_loops = []

    for i, tag_info in enumerate(tags):
        tag_type = tag_info['type']

        if tag_type == 'for':
            # Opening loop - push to stack
            loop_stack.append({
                'index': i,
                'tag_info': tag_info
            })

        elif tag_type == 'endfor':
            # Closing loop - pop from stack
            if loop_stack:
                loop_stack.pop()
            else:
                # endfor without matching for
                print(f"⚠️  Found endfor without matching for at position {tag_info['position']}")

    # Any remaining items in stack are unclosed
    unclosed_loops = loop_stack

    return unclosed_loops


def find_unclosed_conditionals(tags):
    """Find if statements that don't have matching endif."""
    conditional_stack = []
    unclosed_conditionals = []

    for i, tag_info in enumerate(tags):
        tag_type = tag_info['type']

        if tag_type == 'if':
            # Opening conditional - push to stack
            conditional_stack.append({
                'index': i,
                'tag_info': tag_info
            })

        elif tag_type in ('elif', 'else'):
            # Must be inside an if block
            if not conditional_stack:
                print(f"⚠️  Found {tag_type} without matching if at position {tag_info['position']}")

        elif tag_type == 'endif':
            # Closing conditional - pop from stack
            if conditional_stack:
                conditional_stack.pop()
            else:
                # endif without matching if
                print(f"⚠️  Found endif without matching if at position {tag_info['position']}")

    # Any remaining items in stack are unclosed
    unclosed_conditionals = conditional_stack

    return unclosed_conditionals


def clean_context(context):
    """Clean XML context to show readable text."""
    # Remove XML tags but keep text content
    text = re.sub(r'<[^>]+>', ' ', context)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/find_unclosed_loops.py <template.docx>")
        print("Example: python scripts/find_unclosed_loops.py app/templates/draft-report-working.docx")
        sys.exit(1)

    template_path = sys.argv[1]

    if not Path(template_path).exists():
        print(f"Error: File not found: {template_path}")
        sys.exit(1)

    print(f"Analyzing: {template_path}\n")
    print("=" * 70)

    # Extract XML content
    xml_content = extract_all_text_with_tags(template_path)

    # Find all tags
    tags = find_jinja_tags(xml_content)

    # Count tags
    for_count = sum(1 for t in tags if t['type'] == 'for')
    endfor_count = sum(1 for t in tags if t['type'] == 'endfor')
    if_count = sum(1 for t in tags if t['type'] == 'if')
    endif_count = sum(1 for t in tags if t['type'] == 'endif')

    print(f"Tag counts:")
    print(f"  for:     {for_count}")
    print(f"  endfor:  {endfor_count}")
    print(f"  Balance: {for_count - endfor_count:+d} (should be 0)")
    print()
    print(f"  if:      {if_count}")
    print(f"  endif:   {endif_count}")
    print(f"  Balance: {if_count - endif_count:+d} (should be 0)")
    print()
    print("=" * 70)

    # Find unclosed loops
    unclosed_loops = find_unclosed_loops(tags)

    if unclosed_loops:
        print(f"\n❌ FOUND {len(unclosed_loops)} UNCLOSED FOR LOOP(S):\n")

        for i, loop in enumerate(unclosed_loops, 1):
            tag_info = loop['tag_info']
            context = clean_context(tag_info['context'])

            print(f"Unclosed Loop #{i}:")
            print(f"  Tag: {tag_info['tag']}")
            print(f"  Position: {tag_info['position']}")
            print(f"  Context: ...{context}...")
            print()
    else:
        print("\n✅ All for loops are properly closed!")

    print("=" * 70)

    # Find unclosed conditionals
    unclosed_conditionals = find_unclosed_conditionals(tags)

    if unclosed_conditionals:
        print(f"\n❌ FOUND {len(unclosed_conditionals)} UNCLOSED IF STATEMENT(S):\n")

        for i, conditional in enumerate(unclosed_conditionals, 1):
            tag_info = conditional['tag_info']
            context = clean_context(tag_info['context'])

            print(f"Unclosed Conditional #{i}:")
            print(f"  Tag: {tag_info['tag']}")
            print(f"  Position: {tag_info['position']}")
            print(f"  Context: ...{context}...")
            print()
    else:
        print("\n✅ All if statements are properly closed!")

    print("=" * 70)

    # Overall status
    if unclosed_loops or unclosed_conditionals:
        print("\n🔍 RECOMMENDATION:")
        print("=" * 70)

        if unclosed_loops:
            print(f"\n1. Open the template in Word")
            print(f"2. Search for the first unclosed for loop shown above")
            print(f"3. Add the missing {{%tr endfor %}} or {{% endfor %}} tag")
            print(f"4. Repeat for all {len(unclosed_loops)} unclosed loop(s)")

        if unclosed_conditionals:
            print(f"\n1. Open the template in Word")
            print(f"2. Search for the first unclosed if statement shown above")
            print(f"3. Add the missing {{% endif %}} tag")
            print(f"4. Repeat for all {len(unclosed_conditionals)} unclosed conditional(s)")

        sys.exit(1)
    else:
        print("\n✅ ALL TAGS ARE PROPERLY BALANCED!")
        sys.exit(0)


if __name__ == '__main__':
    main()
