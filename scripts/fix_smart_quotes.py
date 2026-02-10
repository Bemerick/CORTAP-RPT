#!/usr/bin/env python3
"""
Fix Word's smart quotes in Jinja2 expressions.

Word converts ASCII quotes to Unicode "smart quotes":
  ' (U+0027) → ' (U+2018) left single quote
  ' (U+0027) → ' (U+2019) right single quote
  " (U+0022) → " (U+201C) left double quote
  " (U+0022) → " (U+201D) right double quote

Jinja2 doesn't recognize smart quotes, causing syntax errors.
This script converts all smart quotes back to ASCII quotes.
"""

import zipfile
import shutil
from pathlib import Path


def fix_smart_quotes(xml_content):
    """Replace Unicode smart quotes with ASCII quotes."""

    original_len = len(xml_content)

    # Count before
    left_single = xml_content.count('\u2018')
    right_single = xml_content.count('\u2019')
    left_double = xml_content.count('\u201C')
    right_double = xml_content.count('\u201D')

    print("Smart quotes found:")
    print(f"  Left single (\u2018):  {left_single}")
    print(f"  Right single (\u2019): {right_single}")
    print(f"  Left double (\u201C): {left_double}")
    print(f"  Right double (\u201D): {right_double}")
    print(f"  Total: {left_single + right_single + left_double + right_double}")

    # Replace smart quotes with ASCII
    fixed = xml_content
    fixed = fixed.replace('\u2018', "'")  # ' → '
    fixed = fixed.replace('\u2019', "'")  # ' → '
    fixed = fixed.replace('\u201C', '"')  # " → "
    fixed = fixed.replace('\u201D', '"')  # " → "

    # Also fix any en-dashes or em-dashes in expressions
    fixed = fixed.replace('\u2013', '-')  # – → -
    fixed = fixed.replace('\u2014', '-')  # — → -

    print(f"\nReplaced {original_len - len(fixed)} characters")

    return fixed


def fix_template(input_path, output_path=None):
    """Fix smart quotes in Word template."""

    input_path = Path(input_path)

    if output_path is None:
        # Overwrite original and create backup
        backup_path = input_path.with_stem(input_path.stem + '_backup')
        shutil.copy2(input_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
        output_path = input_path
    else:
        output_path = Path(output_path)

    temp_dir = Path('temp_fix_quotes')
    temp_dir.mkdir(exist_ok=True)

    try:
        # Extract
        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Fix document.xml
        doc_xml = temp_dir / 'word' / 'document.xml'
        with open(doc_xml, 'r', encoding='utf-8') as f:
            xml_content = f.read()

        print(f"\nOriginal XML: {len(xml_content):,} characters\n")

        # Fix
        fixed_xml = fix_smart_quotes(xml_content)

        print(f"\nFixed XML: {len(fixed_xml):,} characters")

        # Write back
        with open(doc_xml, 'w', encoding='utf-8') as f:
            f.write(fixed_xml)

        # Repackage
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for file_path in temp_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_dir)
                    zip_out.write(file_path, arcname)

        print(f"\n✅ Fixed template saved to: {output_path}")

    finally:
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python fix_smart_quotes.py <template.docx> [output.docx]")
        print("\nFixes Unicode smart quotes in Jinja2 expressions.")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    fix_template(input_file, output_file)
