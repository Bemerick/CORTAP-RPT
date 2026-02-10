#!/usr/bin/env python3
"""
Fix document properties that exceed Word's limits.

Word has a 255 character limit on certain properties like Comments.
This script clears or truncates properties that exceed limits.
"""

import zipfile
import shutil
from pathlib import Path


def fix_properties(template_path):
    """Clear document properties that might cause issues."""

    template_path = Path(template_path)

    # Create backup
    backup_path = template_path.with_stem(template_path.stem + '_before_prop_fix')
    shutil.copy2(template_path, backup_path)
    print(f"✅ Backup created: {backup_path}")

    temp_dir = Path('temp_prop_fix')
    temp_dir.mkdir(exist_ok=True)

    try:
        # Extract
        with zipfile.ZipFile(template_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Modify core properties
        core_props_path = temp_dir / 'docProps' / 'core.xml'

        if core_props_path.exists():
            with open(core_props_path, 'r', encoding='utf-8') as f:
                props_xml = f.read()

            print(f"\nOriginal properties file: {len(props_xml)} chars")

            # Clear the description (comments) field
            import re
            props_xml = re.sub(
                r'<dc:description>.*?</dc:description>',
                '<dc:description></dc:description>',
                props_xml,
                flags=re.DOTALL
            )

            # Also clear subject if too long
            props_xml = re.sub(
                r'<dc:subject>.*?</dc:subject>',
                '<dc:subject></dc:subject>',
                props_xml,
                flags=re.DOTALL
            )

            with open(core_props_path, 'w', encoding='utf-8') as f:
                f.write(props_xml)

            print(f"Modified properties file: {len(props_xml)} chars")
            print("✅ Cleared description and subject fields")

        # Repackage
        with zipfile.ZipFile(template_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for file_path in temp_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_dir)
                    zip_out.write(file_path, arcname)

        print(f"\n✅ Fixed template saved: {template_path}")

    finally:
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python fix_document_properties.py <template.docx>")
        sys.exit(1)

    template = sys.argv[1]
    fix_properties(template)
