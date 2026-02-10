#!/usr/bin/env python3
"""
Test template sections individually to isolate errors.

Breaks the template into logical sections and tests each one.
"""

import zipfile
import re
from jinja2 import Environment, TemplateSyntaxError


def extract_sections(xml_content):
    """Extract logical sections based on headings or structure."""

    # Find all paragraphs with heading styles
    # These typically mark major sections
    heading_pattern = r'<w:pStyle w:val="Heading\d+"[^>]*/>.*?</w:p>'

    # Or split by major Jinja2 control structures
    # Look for {% if metadata.has_deficiencies %}, etc.

    # For now, let's split by every N characters to manageable chunks
    # and also try to split at logical Jinja2 boundaries

    sections = []
    chunk_size = 50000  # ~50KB chunks

    pos = 0
    section_num = 1

    while pos < len(xml_content):
        # Find next good split point (after a complete Jinja2 block)
        end_pos = min(pos + chunk_size, len(xml_content))

        # Try to find a {% endif %} or {% endfor %} near the end
        search_start = max(pos, end_pos - 1000)
        search_end = min(len(xml_content), end_pos + 1000)

        # Look for complete block endings
        chunk = xml_content[search_start:search_end]
        endings = list(re.finditer(r'{%\s*end(if|for)\s*%}', chunk))

        if endings:
            # Use the last complete ending
            last_ending = endings[-1]
            actual_end = search_start + last_ending.end()
        else:
            actual_end = end_pos

        section_content = xml_content[pos:actual_end]
        sections.append({
            'num': section_num,
            'start': pos,
            'end': actual_end,
            'size': actual_end - pos,
            'content': section_content
        })

        pos = actual_end
        section_num += 1

    return sections


def test_section(section, env):
    """Test if a section can be parsed by Jinja2."""

    # Wrap in minimal XML structure
    test_xml = f'''<w:body xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
{section['content']}
</w:body>'''

    try:
        env.parse(test_xml)
        return True, None
    except TemplateSyntaxError as e:
        return False, e.message
    except Exception as e:
        return False, str(e)


def find_jinja_blocks_in_section(content):
    """Count Jinja2 blocks in a section."""

    if_count = len(re.findall(r'{%\s*if\s', content))
    elif_count = len(re.findall(r'{%\s*elif\s', content))
    endif_count = len(re.findall(r'{%\s*endif\s*%}', content))
    for_count = len(re.findall(r'{%\s*for\s', content))
    endfor_count = len(re.findall(r'{%\s*endfor\s*%}', content))
    expr_count = len(re.findall(r'{{.*?}}', content))

    return {
        'if': if_count,
        'elif': elif_count,
        'endif': endif_count,
        'for': for_count,
        'endfor': endfor_count,
        'expressions': expr_count,
        'total_blocks': if_count + elif_count + endif_count + for_count + endfor_count + expr_count
    }


def main():
    template_path = 'app/templates/draft-audit-report-poc.docx'

    print(f"Loading template: {template_path}\n")

    # Extract document.xml
    with zipfile.ZipFile(template_path) as z:
        with z.open('word/document.xml') as f:
            xml_content = f.read().decode('utf-8')

    print(f"Template size: {len(xml_content):,} characters\n")

    # Extract sections
    print("Breaking template into sections...\n")
    sections = extract_sections(xml_content)

    print(f"Created {len(sections)} sections\n")
    print("=" * 80)

    # Test each section
    env = Environment()
    failed_sections = []

    for section in sections:
        blocks = find_jinja_blocks_in_section(section['content'])

        print(f"\nSection {section['num']}:")
        print(f"  Position: {section['start']:,} - {section['end']:,}")
        print(f"  Size: {section['size']:,} chars")
        print(f"  Jinja2 blocks: {blocks['total_blocks']}")
        print(f"    - if: {blocks['if']}, elif: {blocks['elif']}, endif: {blocks['endif']}")
        print(f"    - for: {blocks['for']}, endfor: {blocks['endfor']}")
        print(f"    - expressions: {blocks['expressions']}")

        # Test it
        success, error = test_section(section, env)

        if success:
            print(f"  ✅ PASS")
        else:
            print(f"  ❌ FAIL: {error}")
            failed_sections.append((section, error))

    print("\n" + "=" * 80)
    print(f"\nSummary:")
    print(f"  Total sections: {len(sections)}")
    print(f"  Passed: {len(sections) - len(failed_sections)}")
    print(f"  Failed: {len(failed_sections)}")

    if failed_sections:
        print(f"\nFailed sections:")
        for section, error in failed_sections:
            print(f"  - Section {section['num']} (pos {section['start']:,}-{section['end']:,}): {error}")

            # Save failed section for inspection
            output_path = f"output/failed_section_{section['num']}.xml"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(section['content'])
            print(f"    Saved to: {output_path}")
    else:
        print(f"\n✅ All sections pass individually!")
        print(f"\nThis means the error occurs from section interactions.")
        print(f"Try testing cumulative sections (1, 1+2, 1+2+3, etc.)")


if __name__ == '__main__':
    main()
