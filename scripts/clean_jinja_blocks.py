#!/usr/bin/env python3
"""
Clean Word XML from inside Jinja2 blocks.

Word fragments Jinja2 expressions by inserting XML tags. This script:
1. Finds all {{ }} and {% %} blocks
2. Extracts the text content (removing all XML)
3. Rebuilds clean Jinja2 expressions
"""

import zipfile
import shutil
import re
from pathlib import Path


def extract_text_from_xml(xml_fragment):
    """Extract plain text from XML fragment, removing all tags."""

    # Extract all <w:t> tag contents
    text_parts = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', xml_fragment)

    # Also check for xml:space="preserve" variants
    preserve_parts = re.findall(r'<w:t xml:space="preserve">([^<]*)</w:t>', xml_fragment)

    # Combine all text
    all_text = ''.join(text_parts)

    return all_text


def clean_jinja_block(match):
    """Clean a single Jinja2 block of embedded XML."""

    full_match = match.group(0)
    opening = match.group(1)  # {{ or {%
    content = match.group(2)   # everything in between
    closing = match.group(3)   # }} or %}

    # Check if there's XML inside
    if '<' not in content:
        # No XML, return as-is
        return full_match

    # Extract text from XML
    clean_content = extract_text_from_xml(content)

    # If extraction failed, try simple tag stripping
    if not clean_content:
        clean_content = re.sub(r'<[^>]+>', '', content)

    # Clean up the content
    clean_content = clean_content.strip()

    # Add space after opening delimiter for statements
    # {% if ... %} needs the space
    if opening == '{%':
        clean_content = ' ' + clean_content + ' '

    # Rebuild the block
    return f"{opening}{clean_content}{closing}"


def clean_jinja_in_xml(xml_content):
    """Clean all Jinja2 blocks in XML content."""

    print("Scanning for Jinja2 blocks with embedded XML...\n")

    # Pattern to match {{ ... }} with any content including XML
    # Use non-greedy matching and handle multiline
    expr_pattern = r'(\{\{)(.*?)(\}\})'
    stmt_pattern = r'(\{%)(.*?)(%\})'

    # Count before
    expr_matches = re.findall(expr_pattern, xml_content, re.DOTALL)
    stmt_matches = re.findall(stmt_pattern, xml_content, re.DOTALL)

    expr_with_xml = sum(1 for _, content, _ in expr_matches if '<' in content)
    stmt_with_xml = sum(1 for _, content, _ in stmt_matches if '<' in content)

    print(f"Found {len(expr_matches)} {{ }} expressions ({expr_with_xml} with XML)")
    print(f"Found {len(stmt_matches)} {{% %}} statements ({stmt_with_xml} with XML)")
    print(f"Total blocks with XML: {expr_with_xml + stmt_with_xml}\n")

    if expr_with_xml + stmt_with_xml == 0:
        print("✅ No XML found in Jinja2 blocks!")
        return xml_content

    # Clean expressions
    print("Cleaning {{ }} expressions...")
    cleaned = re.sub(expr_pattern, clean_jinja_block, xml_content, flags=re.DOTALL)

    # Clean statements
    print("Cleaning {% %} statements...")
    cleaned = re.sub(stmt_pattern, clean_jinja_block, cleaned, flags=re.DOTALL)

    # Verify
    expr_matches_after = re.findall(expr_pattern, cleaned, re.DOTALL)
    stmt_matches_after = re.findall(stmt_pattern, cleaned, re.DOTALL)

    expr_with_xml_after = sum(1 for _, content, _ in expr_matches_after if '<' in content)
    stmt_with_xml_after = sum(1 for _, content, _ in stmt_matches_after if '<' in content)

    print(f"\nAfter cleaning:")
    print(f"  {{ }} with XML: {expr_with_xml} → {expr_with_xml_after}")
    print(f"  {{% %}} with XML: {stmt_with_xml} → {stmt_with_xml_after}")

    size_reduction = len(xml_content) - len(cleaned)
    print(f"  Size reduction: {size_reduction:,} chars ({size_reduction/len(xml_content)*100:.1f}%)")

    return cleaned


def clean_template(input_path, output_path=None):
    """Clean Jinja2 blocks in Word template."""

    input_path = Path(input_path)

    if output_path is None:
        # Create backup
        backup_path = input_path.with_stem(input_path.stem + '_before_clean')
        shutil.copy2(input_path, backup_path)
        print(f"✅ Backup created: {backup_path}\n")
        output_path = input_path
    else:
        output_path = Path(output_path)

    temp_dir = Path('temp_clean_jinja')
    temp_dir.mkdir(exist_ok=True)

    try:
        # Extract
        print(f"Extracting: {input_path}")
        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Read document.xml
        doc_xml = temp_dir / 'word' / 'document.xml'
        with open(doc_xml, 'r', encoding='utf-8') as f:
            xml_content = f.read()

        print(f"Original XML: {len(xml_content):,} characters\n")

        # Clean
        cleaned_xml = clean_jinja_in_xml(xml_content)

        # Write back
        with open(doc_xml, 'w', encoding='utf-8') as f:
            f.write(cleaned_xml)

        print(f"\nFinal XML: {len(cleaned_xml):,} characters")

        # Repackage
        print(f"\nRepackaging to: {output_path}")
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for file_path in temp_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_dir)
                    zip_out.write(file_path, arcname)

        print(f"\n✅ Cleaned template saved!")

    finally:
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python clean_jinja_blocks.py <template.docx> [output.docx]")
        print("\nRemoves Word XML tags from inside Jinja2 expressions and statements.")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    clean_template(input_file, output_file)
