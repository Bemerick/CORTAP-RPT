#!/usr/bin/env python3
"""
Fix broken == operators in selectattr statements.

Word splits '==' into two separate <w:t> tags: '<w:t>'=</w:t>' and '<w:t>='</w:t>'.
This script merges them back into '<w:t>'=='</w:t>'.
"""

import zipfile
import shutil
import re
from pathlib import Path


def fix_broken_equals(xml_content):
    """Fix broken == operators that are split across <w:t> tags."""

    # Pattern: <w:t>'=</w:t> followed by XML garbage, then <w:t>='</w:t>
    # Replace with: <w:t>'=='</w:t> and remove the second tag

    # This matches: <w:t>'=</w:t></w:r>...<w:r ...><w:t>='</w:t>
    # And replaces with: <w:t>'=='</w:t>

    pattern = r"(<w:t>)'=(</w:t></w:r>)(<w:proofErr[^>]*/>)?(<w:r [^>]*>)(<w:rPr>.*?</w:rPr>)?(<w:t>)='(</w:t>)"

    def replacer(match):
        """Replace broken == with fixed version."""
        # Keep just the first <w:t> tag with '==' inside
        return match.group(1) + "'==" + match.group(7)

    fixed = re.sub(pattern, replacer, xml_content, flags=re.DOTALL)

    changes = xml_content.count("<w:t>'=</w:t>")
    print(f"Fixed {changes} broken == operators")

    return fixed


def fix_template(input_path, output_path=None):
    """Fix broken selectattr == operators in Word template."""

    if output_path is None:
        # Create backup
        backup_path = str(input_path).replace('.docx', '_backup.docx')
        shutil.copy2(input_path, backup_path)
        print(f"Backup created: {backup_path}")
        output_path = input_path

    input_path = Path(input_path)
    output_path = Path(output_path)
    temp_dir = Path('temp_fix')

    try:
        # Extract
        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Read document XML
        doc_xml = temp_dir / 'word' / 'document.xml'
        with open(doc_xml, 'r', encoding='utf-8') as f:
            xml_content = f.read()

        print(f"Original XML: {len(xml_content)} chars")
        broken_count = xml_content.count("<w:t>'=</w:t>")
        print(f"Broken == operators: {broken_count}")

        # Fix
        fixed_xml = fix_broken_equals(xml_content)

        print(f"Fixed XML: {len(fixed_xml)} chars")
        remaining = fixed_xml.count("<w:t>'=</w:t>")
        print(f"Remaining broken ==: {remaining}")

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
        print("Usage: python fix_selectattr.py <template.docx> [output.docx]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    fix_template(input_file, output_file)
