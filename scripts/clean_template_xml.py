#!/usr/bin/env python3
"""
Clean Word XML fragmentation in Jinja2 expressions.

Word often breaks Jinja2 expressions across multiple XML runs, causing
syntax errors. This script reassembles broken expressions.
"""

import re
import sys
import zipfile
import shutil
from pathlib import Path


def clean_jinja2_xml(xml_content):
    """Remove Word XML tags from inside Jinja2 expressions."""

    # Pattern to match Jinja2 blocks with embedded XML
    # This matches {{ ... }} and {% ... %} that contain </w:t>

    def clean_expression(match):
        """Clean a single Jinja2 expression of embedded XML."""
        expr = match.group(0)
        opening = match.group(1)  # {{ or {%
        closing = match.group(3)  # }} or %}
        content = match.group(2)

        # Remove all Word XML tags from the content
        # Keep only the actual text content
        cleaned = re.sub(r'<w:t[^>]*>([^<]*)</w:t>', r'\1', content)
        cleaned = re.sub(r'<w:t xml:space="preserve">([^<]*)</w:t>', r'\1', cleaned)
        cleaned = re.sub(r'<[^>]+>', '', cleaned)

        # Collapse multiple spaces
        cleaned = re.sub(r' +', ' ', cleaned)

        return f'{opening}{cleaned}{closing}'

    # Match Jinja2 expressions that contain XML tags
    # Pattern: ({{|{%) ... (}}|%}) where ... contains </w:
    pattern = r'(\{\{|\{%)(.+?</w:.+?)(\}\}|%\})'

    result = re.sub(pattern, clean_expression, xml_content, flags=re.DOTALL)

    return result


def clean_docx_template(input_path, output_path=None):
    """Clean a .docx template file of Word XML fragments in Jinja2."""

    if output_path is None:
        output_path = input_path.replace('.docx', '_cleaned.docx')

    input_path = Path(input_path)
    output_path = Path(output_path)

    # Create temp directory
    temp_dir = Path('temp_docx_clean')
    temp_dir.mkdir(exist_ok=True)

    try:
        # Extract the docx (it's a zip file)
        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Read the main document XML
        doc_xml_path = temp_dir / 'word' / 'document.xml'
        with open(doc_xml_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()

        print(f"Original XML length: {len(xml_content)} characters")

        # Count Jinja2 expressions before cleaning
        before_count = len(re.findall(r'\{\{|\{%', xml_content))
        print(f"Found {before_count} Jinja2 expressions")

        # Clean the XML
        cleaned_xml = clean_jinja2_xml(xml_content)

        # Count after cleaning
        after_count = len(re.findall(r'\{\{|\{%', cleaned_xml))
        print(f"After cleaning: {after_count} Jinja2 expressions")

        # Write back
        with open(doc_xml_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_xml)

        print(f"Cleaned XML length: {len(cleaned_xml)} characters")

        # Repackage as docx
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for file_path in temp_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_dir)
                    zip_out.write(file_path, arcname)

        print(f"\n✅ Cleaned template saved to: {output_path}")

    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python clean_template_xml.py <input.docx> [output.docx]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    clean_docx_template(input_file, output_file)
