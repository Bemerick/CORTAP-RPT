#!/usr/bin/env python3
"""
Check Jinja2 syntax in Word template for unmatched tags.

Usage:
    python scripts/check_jinja_syntax.py app/templates/draft-report-working.docx
"""

import sys
import re
from pathlib import Path
from docxtpl import DocxTemplate
from collections import deque


def extract_jinja_tags(xml_content):
    """Extract all Jinja2 tags from XML content."""
    # Pattern to match Jinja2 tags
    pattern = r'\{%\s*(p\s+)?(tr\s+)?(if|elif|else|endif|for|endfor|set|endset)\s*[^%]*%\}'

    tags = []
    for match in re.finditer(pattern, xml_content):
        tag = match.group(0)
        position = match.start()
        tags.append({
            'tag': tag,
            'position': position,
            'line': xml_content[:position].count('\n') + 1
        })

    return tags


def parse_tag_type(tag):
    """Parse a Jinja2 tag to determine its type."""
    tag = tag.strip()

    # Check for paragraph tags
    is_paragraph = '{%p ' in tag or '{% p ' in tag

    # Check for table row tags
    is_table_row = '{%tr ' in tag or '{% tr ' in tag

    # Determine tag type
    if 'if' in tag and 'endif' not in tag and 'elif' not in tag:
        tag_type = 'if'
    elif 'elif' in tag:
        tag_type = 'elif'
    elif 'else' in tag and 'endelse' not in tag:
        tag_type = 'else'
    elif 'endif' in tag:
        tag_type = 'endif'
    elif 'for' in tag and 'endfor' not in tag:
        tag_type = 'for'
    elif 'endfor' in tag:
        tag_type = 'endfor'
    elif 'set' in tag and 'endset' not in tag:
        tag_type = 'set'
    elif 'endset' in tag:
        tag_type = 'endset'
    else:
        tag_type = 'unknown'

    return {
        'type': tag_type,
        'is_paragraph': is_paragraph,
        'is_table_row': is_table_row,
        'tag': tag
    }


def check_matching_tags(tags):
    """Check if all opening tags have matching closing tags."""
    stack = []
    errors = []

    for i, tag_info in enumerate(tags):
        parsed = parse_tag_type(tag_info['tag'])
        tag_type = parsed['type']

        if tag_type == 'if':
            # Opening tag
            stack.append({
                'type': 'if',
                'index': i,
                'tag_info': tag_info,
                'parsed': parsed
            })

        elif tag_type == 'for':
            # Opening tag
            stack.append({
                'type': 'for',
                'index': i,
                'tag_info': tag_info,
                'parsed': parsed
            })

        elif tag_type == 'set':
            # Set is usually standalone, but could be block-level
            # For now, treat as standalone
            pass

        elif tag_type in ('elif', 'else'):
            # Must be inside an if block
            if not stack or stack[-1]['type'] != 'if':
                errors.append({
                    'type': 'orphan_elif_else',
                    'tag': tag_info['tag'],
                    'line': tag_info['line'],
                    'message': f"{tag_type} without matching if"
                })

        elif tag_type == 'endif':
            # Closing tag for if
            if not stack:
                errors.append({
                    'type': 'orphan_endif',
                    'tag': tag_info['tag'],
                    'line': tag_info['line'],
                    'message': "endif without matching if"
                })
            elif stack[-1]['type'] != 'if':
                errors.append({
                    'type': 'mismatched_endif',
                    'tag': tag_info['tag'],
                    'line': tag_info['line'],
                    'expected': stack[-1]['type'],
                    'message': f"endif found but expected end{stack[-1]['type']}"
                })
            else:
                # Check if paragraph/table row types match
                opening = stack.pop()
                if opening['parsed']['is_paragraph'] != parsed['is_paragraph']:
                    opening_type = '{%p' if opening['parsed']['is_paragraph'] else '{%'
                    closing_type = '{%p' if parsed['is_paragraph'] else '{%'
                    errors.append({
                        'type': 'mismatched_paragraph_tag',
                        'opening_tag': opening['tag_info']['tag'],
                        'opening_line': opening['tag_info']['line'],
                        'closing_tag': tag_info['tag'],
                        'closing_line': tag_info['line'],
                        'message': f"if block opened with {opening_type} but closed with {closing_type}"
                    })

                if opening['parsed']['is_table_row'] != parsed['is_table_row']:
                    opening_type = '{%tr' if opening['parsed']['is_table_row'] else '{%'
                    closing_type = '{%tr' if parsed['is_table_row'] else '{%'
                    errors.append({
                        'type': 'mismatched_table_tag',
                        'opening_tag': opening['tag_info']['tag'],
                        'opening_line': opening['tag_info']['line'],
                        'closing_tag': tag_info['tag'],
                        'closing_line': tag_info['line'],
                        'message': f"for loop opened with {opening_type} but closed with {closing_type}"
                    })

        elif tag_type == 'endfor':
            # Closing tag for for
            if not stack:
                errors.append({
                    'type': 'orphan_endfor',
                    'tag': tag_info['tag'],
                    'line': tag_info['line'],
                    'message': "endfor without matching for"
                })
            elif stack[-1]['type'] != 'for':
                errors.append({
                    'type': 'mismatched_endfor',
                    'tag': tag_info['tag'],
                    'line': tag_info['line'],
                    'expected': stack[-1]['type'],
                    'message': f"endfor found but expected end{stack[-1]['type']}"
                })
            else:
                # Check if paragraph/table row types match
                opening = stack.pop()
                if opening['parsed']['is_table_row'] != parsed['is_table_row']:
                    opening_type = '{%tr' if opening['parsed']['is_table_row'] else '{%'
                    closing_type = '{%tr' if parsed['is_table_row'] else '{%'
                    errors.append({
                        'type': 'mismatched_table_tag',
                        'opening_tag': opening['tag_info']['tag'],
                        'opening_line': opening['tag_info']['line'],
                        'closing_tag': tag_info['tag'],
                        'closing_line': tag_info['line'],
                        'message': f"for loop opened with {opening_type} but closed with {closing_type}"
                    })

    # Check for unclosed tags
    for remaining in stack:
        errors.append({
            'type': 'unclosed_tag',
            'tag': remaining['tag_info']['tag'],
            'line': remaining['tag_info']['line'],
            'message': f"Unclosed {remaining['type']} tag (missing end{remaining['type']})"
        })

    return errors


def check_template(template_path):
    """Check a Word template for Jinja2 syntax errors."""
    print(f"Checking: {template_path}\n")

    try:
        # Load template
        template = DocxTemplate(template_path)
        print("✅ Template loaded successfully")

        # Get XML content from document part
        from lxml import etree
        xml_content = etree.tostring(template.get_docx()._element, encoding='unicode')

        # Extract tags
        tags = extract_jinja_tags(xml_content)
        print(f"Found {len(tags)} Jinja2 tags\n")

        # Check for matching tags
        errors = check_matching_tags(tags)

        if not errors:
            print("=" * 70)
            print("✅ NO SYNTAX ERRORS FOUND!")
            print("=" * 70)
            return True
        else:
            print("=" * 70)
            print(f"❌ FOUND {len(errors)} SYNTAX ERROR(S)")
            print("=" * 70)
            print()

            for i, error in enumerate(errors, 1):
                print(f"Error #{i}: {error['type'].upper()}")
                print(f"  Line: {error.get('line', 'Unknown')}")
                print(f"  Message: {error['message']}")
                print(f"  Tag: {error.get('tag', 'N/A')}")

                if 'opening_tag' in error:
                    print(f"  Opening tag (line {error['opening_line']}): {error['opening_tag']}")
                    print(f"  Closing tag (line {error['closing_line']}): {error['closing_tag']}")

                print()

            print("=" * 70)
            print("SUMMARY:")
            print("=" * 70)

            # Group errors by type
            error_types = {}
            for error in errors:
                error_type = error['type']
                if error_type not in error_types:
                    error_types[error_type] = []
                error_types[error_type].append(error)

            for error_type, type_errors in error_types.items():
                print(f"  {error_type}: {len(type_errors)} error(s)")

            print()
            print("Most likely issue:")
            if any(e['type'] == 'unclosed_tag' for e in errors):
                unclosed = [e for e in errors if e['type'] == 'unclosed_tag']
                print(f"  ⚠️  You have {len(unclosed)} unclosed tag(s)")
                print(f"  First unclosed tag: {unclosed[0]['tag']} at line {unclosed[0]['line']}")
            elif any(e['type'] == 'mismatched_paragraph_tag' for e in errors):
                print("  ⚠️  You have mismatched {% if %} and {%p if %} tags")
                print("  Make sure opening and closing tags match:")
                print("    {% if %} must close with {% endif %}")
                print("    {%p if %} must close with {%p endif %}")

            return False

    except Exception as e:
        print(f"❌ Error loading template: {e}")
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/check_jinja_syntax.py <template.docx>")
        print("Example: python scripts/check_jinja_syntax.py app/templates/draft-report-working.docx")
        sys.exit(1)

    template_path = sys.argv[1]

    if not Path(template_path).exists():
        print(f"Error: File not found: {template_path}")
        sys.exit(1)

    success = check_template(template_path)

    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
