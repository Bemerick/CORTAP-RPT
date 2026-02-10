#!/usr/bin/env python3
"""
Create a clean Word template with all Jinja2 removed.

This gives us a clean starting point to add Jinja2 section by section.
"""

import zipfile
import shutil
import re
from pathlib import Path


def remove_all_jinja(xml_content):
    """Remove all Jinja2 expressions and statements from XML."""

    print("Scanning for Jinja2 blocks to remove...\n")

    # Count before
    expr_count = len(re.findall(r'\{\{.*?\}\}', xml_content, re.DOTALL))
    stmt_count = len(re.findall(r'\{%.*?%\}', xml_content, re.DOTALL))

    print(f"Found:")
    print(f"  {{ }} expressions: {expr_count}")
    print(f"  {{% %}} statements: {stmt_count}")
    print(f"  Total: {expr_count + stmt_count}\n")

    if expr_count + stmt_count == 0:
        print("✅ No Jinja2 found - already clean!")
        return xml_content

    # Remove all {{ }} expressions
    cleaned = re.sub(r'\{\{.*?\}\}', '[PLACEHOLDER]', xml_content, flags=re.DOTALL)

    # Remove all {% %} statements
    cleaned = re.sub(r'\{%.*?%\}', '', cleaned, flags=re.DOTALL)

    # Verify removal
    remaining_expr = len(re.findall(r'\{\{.*?\}\}', cleaned, re.DOTALL))
    remaining_stmt = len(re.findall(r'\{%.*?%\}', cleaned, re.DOTALL))

    print(f"After removal:")
    print(f"  {{ }} expressions: {remaining_expr}")
    print(f"  {{% %}} statements: {remaining_stmt}\n")

    if remaining_expr + remaining_stmt > 0:
        print(f"⚠️  Warning: {remaining_expr + remaining_stmt} blocks still remain!")
    else:
        print(f"✅ All Jinja2 removed successfully!")

    return cleaned


def create_clean_template(source_path, output_path):
    """Create a clean template from source."""

    source_path = Path(source_path)
    output_path = Path(output_path)

    temp_dir = Path('temp_clean_create')
    temp_dir.mkdir(exist_ok=True)

    try:
        # Extract
        print(f"Extracting: {source_path}\n")
        with zipfile.ZipFile(source_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Read document.xml
        doc_xml = temp_dir / 'word' / 'document.xml'
        with open(doc_xml, 'r', encoding='utf-8') as f:
            xml_content = f.read()

        print(f"Original XML: {len(xml_content):,} characters\n")

        # Remove Jinja2
        cleaned_xml = remove_all_jinja(xml_content)

        # Write back
        with open(doc_xml, 'w', encoding='utf-8') as f:
            f.write(cleaned_xml)

        print(f"\nCleaned XML: {len(cleaned_xml):,} characters")

        # Repackage
        print(f"\nRepackaging to: {output_path}")
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for file_path in temp_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_dir)
                    zip_out.write(file_path, arcname)

        print(f"\n✅ Clean template created: {output_path}")
        print(f"\nNext steps:")
        print(f"  1. Open {output_path} in Word")
        print(f"  2. Turn OFF smart quotes: File → Options → Proofing → AutoCorrect")
        print(f"  3. Add Jinja2 section by section, testing after each")
        print(f"  4. Use: python scripts/test_section.py after each addition")

    finally:
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python create_clean_template.py <source.docx> [output.docx]")
        print("\nCreates a clean Word template with all Jinja2 removed.")
        print("Use this as a starting point to add Jinja2 section by section.")
        sys.exit(1)

    source = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else 'app/templates/draft-audit-report-clean.docx'

    create_clean_template(source, output)
