#!/usr/bin/env python3
"""
Find the location of missing {% endif %} tag in Word template.

Usage:
    python scripts/find_missing_endif.py app/templates/draft-report-working.docx
"""

import sys
import re
from pathlib import Path
from docxtpl import DocxTemplate
from lxml import etree


def extract_text_with_tags(element, depth=0):
    """Extract text content including Jinja2 tags with paragraph markers."""
    chunks = []

    # Get text from this element
    if element.text:
        chunks.append(element.text)

    # Process children
    for child in element:
        # Add text from child elements
        chunks.extend(extract_text_with_tags(child, depth + 1))
        if child.tail:
            chunks.append(child.tail)

    return chunks


def get_paragraphs_with_tags(template_path):
    """Extract all paragraphs with their Jinja2 tags."""
    template = DocxTemplate(template_path)
    doc_element = template.get_docx()._element

    paragraphs = []

    # Find all paragraph elements
    for para in doc_element.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        # Extract all text including tags
        text_chunks = extract_text_with_tags(para)
        para_text = ''.join(text_chunks)

        # Only include paragraphs with content
        if para_text.strip():
            paragraphs.append(para_text)

    return paragraphs


def count_tags_in_text(text):
    """Count opening and closing tags in text."""
    if_count = len(re.findall(r'\{%\s*(?:p\s+)?(?:tr\s+)?if\s+', text))
    elif_count = len(re.findall(r'\{%\s*(?:p\s+)?elif\s+', text))
    else_count = len(re.findall(r'\{%\s*(?:p\s+)?else\s*%\}', text))
    endif_count = len(re.findall(r'\{%\s*(?:p\s+)?endif\s*%\}', text))

    for_count = len(re.findall(r'\{%\s*(?:tr\s+)?for\s+', text))
    endfor_count = len(re.findall(r'\{%\s*(?:tr\s+)?endfor\s*%\}', text))

    return {
        'if': if_count,
        'elif': elif_count,
        'else': else_count,
        'endif': endif_count,
        'for': for_count,
        'endfor': endfor_count,
        'if_balance': if_count - endif_count,
        'for_balance': for_count - endfor_count
    }


def find_section_headers(paragraphs):
    """Find paragraph indices that look like section headers."""
    section_indices = []

    for i, para in enumerate(paragraphs):
        # Look for patterns like "I. ", "II. ", "III. ", "1. ", "2. ", etc.
        # Also look for numbered assessment areas like "19.    Section 5307"
        if re.match(r'^(I{1,3}V?|IV|V|VI{1,3}|[0-9]{1,2})\.[\s]+[A-Z]', para):
            section_indices.append(i)

    return section_indices


def analyze_sections(template_path):
    """Analyze template section by section to find unbalanced tags."""
    print(f"Analyzing: {template_path}\n")
    print("=" * 70)

    # Get all paragraphs
    paragraphs = get_paragraphs_with_tags(template_path)
    print(f"Extracted {len(paragraphs)} paragraphs\n")

    # Find section boundaries
    section_indices = find_section_headers(paragraphs)
    print(f"Found {len(section_indices)} section headers\n")

    # Analyze overall document
    all_text = '\n'.join(paragraphs)
    overall_counts = count_tags_in_text(all_text)

    print("OVERALL DOCUMENT COUNTS:")
    print("-" * 70)
    print(f"  if tags:      {overall_counts['if']}")
    print(f"  elif tags:    {overall_counts['elif']}")
    print(f"  else tags:    {overall_counts['else']}")
    print(f"  endif tags:   {overall_counts['endif']}")
    print(f"  Balance:      {overall_counts['if_balance']:+d} (should be 0)")
    print()
    print(f"  for tags:     {overall_counts['for']}")
    print(f"  endfor tags:  {overall_counts['endfor']}")
    print(f"  Balance:      {overall_counts['for_balance']:+d} (should be 0)")
    print()

    if overall_counts['if_balance'] == 0 and overall_counts['for_balance'] == 0:
        print("✅ All tags are balanced!")
        return True

    print("=" * 70)
    print("ANALYZING SECTIONS...")
    print("=" * 70)
    print()

    # Add document end as final boundary
    section_indices.append(len(paragraphs))

    # Analyze each section
    problems = []
    cumulative_if_balance = 0
    cumulative_for_balance = 0

    for i in range(len(section_indices) - 1):
        start_idx = section_indices[i]
        end_idx = section_indices[i + 1]

        section_header = paragraphs[start_idx][:60] + "..." if len(paragraphs[start_idx]) > 60 else paragraphs[start_idx]
        section_text = '\n'.join(paragraphs[start_idx:end_idx])

        counts = count_tags_in_text(section_text)
        cumulative_if_balance += counts['if_balance']
        cumulative_for_balance += counts['for_balance']

        # Check if this section has unbalanced tags
        has_problem = counts['if_balance'] != 0 or counts['for_balance'] != 0

        if has_problem:
            problems.append({
                'index': i,
                'start': start_idx,
                'end': end_idx,
                'header': section_header,
                'counts': counts
            })

        status = "❌" if has_problem else "✅"
        print(f"{status} Section {i+1} (para {start_idx}-{end_idx}):")
        print(f"   {section_header}")
        print(f"   if/endif: {counts['if']}/{counts['endif']} (balance: {counts['if_balance']:+d})")
        print(f"   for/endfor: {counts['for']}/{counts['endfor']} (balance: {counts['for_balance']:+d})")
        print(f"   Cumulative if balance: {cumulative_if_balance:+d}")
        print()

    print("=" * 70)
    print("PROBLEM SECTIONS:")
    print("=" * 70)

    if not problems:
        print("No unbalanced sections found (this shouldn't happen!)")
        return False

    for problem in problems:
        print(f"\n❌ Section {problem['index'] + 1}:")
        print(f"   Header: {problem['header']}")
        print(f"   Paragraphs: {problem['start']}-{problem['end']}")
        print(f"   Missing endif tags: {problem['counts']['if_balance']}")
        print(f"   Missing endfor tags: {problem['counts']['for_balance']}")

        # Show last few paragraphs of this section
        section_paras = paragraphs[problem['start']:problem['end']]
        print(f"\n   Last 5 paragraphs of this section:")
        for j, para in enumerate(section_paras[-5:], start=len(section_paras)-5):
            para_display = para[:100] + "..." if len(para) > 100 else para
            para_display = para_display.replace('\n', ' ')
            print(f"      [{j}] {para_display}")

    print("\n" + "=" * 70)
    print("RECOMMENDATION:")
    print("=" * 70)

    first_problem = problems[0]
    print(f"\n👉 Check Section {first_problem['index'] + 1}:")
    print(f"   {first_problem['header']}")
    print(f"\n   This section is missing {first_problem['counts']['if_balance']} endif tag(s)")
    print(f"\n   Look at the END of this section and check if you forgot to close")
    print(f"   an if/elif/else block.\n")

    return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/find_missing_endif.py <template.docx>")
        print("Example: python scripts/find_missing_endif.py app/templates/draft-report-working.docx")
        sys.exit(1)

    template_path = sys.argv[1]

    if not Path(template_path).exists():
        print(f"Error: File not found: {template_path}")
        sys.exit(1)

    try:
        success = analyze_sections(template_path)
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
