#!/usr/bin/env python3
"""
Analyze the original Word template to identify merge fields and structure.

This helps us understand what needs to be converted to Jinja2.
"""

import zipfile
import re
from pathlib import Path
from xml.etree import ElementTree as ET


def extract_merge_fields(template_path):
    """Extract all merge fields from the Word template."""

    merge_fields = []

    with zipfile.ZipFile(template_path) as z:
        with z.open('word/document.xml') as f:
            xml_content = f.read().decode('utf-8')

    # Word merge fields are in <w:fldSimple> tags or <w:instrText> tags
    # Pattern 1: <w:fldSimple w:instr="MERGEFIELD FieldName" />
    simple_fields = re.findall(r'<w:fldSimple[^>]*w:instr="([^"]*)"', xml_content)

    # Pattern 2: <w:instrText>MERGEFIELD FieldName</w:instrText>
    instr_fields = re.findall(r'<w:instrText[^>]*>([^<]*)</w:instrText>', xml_content)

    # Extract field names from instructions
    all_instructions = simple_fields + instr_fields

    for instr in all_instructions:
        # Extract field name from instruction
        # Common patterns: "MERGEFIELD FieldName", "MERGEFIELD FieldName \\* MERGEFORMAT"
        match = re.search(r'MERGEFIELD\s+(\w+)', instr)
        if match:
            field_name = match.group(1)
            if field_name not in [f['name'] for f in merge_fields]:
                merge_fields.append({
                    'name': field_name,
                    'instruction': instr.strip(),
                    'type': 'merge_field'
                })

    # Also look for plain text placeholders like [[FieldName]]
    text_placeholders = re.findall(r'\[\[([^\]]+)\]\]', xml_content)
    for placeholder in text_placeholders:
        if placeholder not in [f['name'] for f in merge_fields]:
            merge_fields.append({
                'name': placeholder,
                'instruction': f'[[{placeholder}]]',
                'type': 'text_placeholder'
            })

    return merge_fields, xml_content


def identify_sections(xml_content):
    """Identify major sections in the document."""

    # Look for heading styles
    headings = []

    # Pattern: <w:pStyle w:val="Heading1" /> or similar
    for match in re.finditer(r'<w:pStyle w:val="(Heading\d+)"[^>]*/>(.*?)</w:p>', xml_content, re.DOTALL):
        heading_style = match.group(1)
        heading_content_xml = match.group(2)

        # Extract text from the heading
        heading_text = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', heading_content_xml))

        headings.append({
            'level': heading_style,
            'text': heading_text.strip()
        })

    return headings


def count_content(xml_content):
    """Count various content elements."""

    stats = {
        'paragraphs': len(re.findall(r'<w:p[ >]', xml_content)),
        'tables': len(re.findall(r'<w:tbl>', xml_content)),
        'text_runs': len(re.findall(r'<w:t>', xml_content)),
        'images': len(re.findall(r'<w:drawing>', xml_content)),
    }

    return stats


def main():
    template_path = Path('docs/requirements/State_RO_Recipient# _Recipient Name_FY25_TRSMR_DraftFinalReport.docx')

    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        return

    print(f"Analyzing: {template_path}\n")
    print("=" * 80)

    # Extract merge fields
    merge_fields, xml_content = extract_merge_fields(template_path)

    print(f"\n📋 MERGE FIELDS ({len(merge_fields)} found)")
    print("=" * 80)

    if merge_fields:
        # Group by type
        merge_type = [f for f in merge_fields if f['type'] == 'merge_field']
        placeholder_type = [f for f in merge_fields if f['type'] == 'text_placeholder']

        if merge_type:
            print(f"\nWord Merge Fields ({len(merge_type)}):")
            for i, field in enumerate(merge_type, 1):
                print(f"  {i}. {field['name']}")
                print(f"     Instruction: {field['instruction']}")

        if placeholder_type:
            print(f"\nText Placeholders ({len(placeholder_type)}):")
            for i, field in enumerate(placeholder_type, 1):
                print(f"  {i}. [[{field['name']}]]")
    else:
        print("  No merge fields found")

    # Identify sections
    headings = identify_sections(xml_content)

    print(f"\n\n📑 DOCUMENT STRUCTURE ({len(headings)} headings)")
    print("=" * 80)

    current_h1 = None
    section_num = 0

    for heading in headings:
        if heading['level'] == 'Heading1':
            section_num += 1
            current_h1 = heading['text']
            print(f"\n{section_num}. {heading['text']}")
        elif heading['level'] == 'Heading2':
            print(f"   {heading['text']}")
        elif heading['level'] == 'Heading3':
            print(f"      • {heading['text']}")

    # Content statistics
    stats = count_content(xml_content)

    print(f"\n\n📊 CONTENT STATISTICS")
    print("=" * 80)
    print(f"  Paragraphs: {stats['paragraphs']:,}")
    print(f"  Tables: {stats['tables']}")
    print(f"  Text runs: {stats['text_runs']:,}")
    print(f"  Images: {stats['images']}")

    # Save detailed analysis
    output_path = Path('output/original_template_analysis.txt')
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("ORIGINAL TEMPLATE ANALYSIS\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Template: {template_path}\n\n")

        f.write("MERGE FIELDS\n")
        f.write("-" * 80 + "\n")
        for field in merge_fields:
            f.write(f"{field['type']}: {field['name']}\n")
            f.write(f"  Instruction: {field['instruction']}\n\n")

        f.write("\nDOCUMENT STRUCTURE\n")
        f.write("-" * 80 + "\n")
        for heading in headings:
            indent = "  " * (int(heading['level'][-1]) - 1)
            f.write(f"{indent}{heading['text']}\n")

        f.write(f"\nSTATISTICS\n")
        f.write("-" * 80 + "\n")
        for key, value in stats.items():
            f.write(f"{key}: {value}\n")

    print(f"\n✅ Detailed analysis saved to: {output_path}\n")


if __name__ == '__main__':
    main()
