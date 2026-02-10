#!/usr/bin/env python3
"""
Merge split '==' operators in selectattr statements.

After fixing smart quotes, we still have: <w:t>'=</w:t>...<w:t>='</w:t>
This needs to become: <w:t>'=='</w:t> (and remove the second tag)
"""

import zipfile
import shutil
import re
from pathlib import Path


def merge_split_equals(xml_content):
    """Merge '= and =' tags into '==' tags."""

    # Pattern: <w:t>'=</w:t></w:r>...<w:r ...><w:t>='</w:t>
    # Replace with: <w:t>'=='</w:t></w:r> (remove everything after)

    # More precise pattern - matches the exact structure Word creates
    pattern = r"(<w:t>)'=(</w:t></w:r>)<w:proofErr[^/]*/?>(<w:r [^>]+>)(<w:rPr>.*?</w:rPr>)?(<w:t>)='(</w:t>)"

    def replacer(match):
        """Replace with merged version."""
        # Keep first tag start, change content to '==', keep first tag close
        return match.group(1) + "'==" + match.group(6)

    original_count = len(re.findall(r"<w:t>'=</w:t>", xml_content))
    print(f"Found {original_count} instances of <w:t>'=</w:t>")

    fixed = re.sub(pattern, replacer, xml_content, flags=re.DOTALL)

    fixed_count = len(re.findall(r"<w:t>'=</w:t>", fixed))
    print(f"After merge: {fixed_count} instances remaining")
    print(f"Fixed: {original_count - fixed_count} instances")

    return fixed


def fix_template(input_path, output_path=None):
    """Merge split == operators in Word template."""

    input_path = Path(input_path)

    if output_path is None:
        # Overwrite original (backup should already exist from previous step)
        output_path = input_path

    temp_dir = Path('temp_merge')
    temp_dir.mkdir(exist_ok=True)

    try:
        # Extract
        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Fix document.xml
        doc_xml = temp_dir / 'word' / 'document.xml'
        with open(doc_xml, 'r', encoding='utf-8') as f:
            xml_content = f.read()

        print(f"Original XML: {len(xml_content):,} characters\n")

        # Fix
        fixed_xml = merge_split_equals(xml_content)

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
        print("Usage: python merge_split_equals.py <template.docx> [output.docx]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    fix_template(input_file, output_file)
