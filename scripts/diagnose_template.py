#!/usr/bin/env python3
"""Diagnose Jinja2 syntax issues in Word template."""

import sys
import re
from pathlib import Path
from zipfile import ZipFile

template_path = Path(__file__).parent.parent / "app/templates/draft-audit-report-poc.docx"

print(f"Analyzing template: {template_path}")
print("=" * 80)

# Word documents are zip files - extract and search XML
with ZipFile(template_path, 'r') as zip_file:
    # Check all XML parts
    xml_content = ""
    for xml_file in ['word/document.xml', 'word/header1.xml', 'word/header2.xml', 'word/footer1.xml', 'word/footer2.xml']:
        try:
            xml_content += zip_file.read(xml_file).decode('utf-8', errors='ignore') + "\n"
        except KeyError:
            pass  # File doesn't exist

    # Find all instances of | date_format (filter syntax)
    filter_pattern = re.compile(r'\{\{[^}]*\|\s*date_format[^}]*\}\}')
    matches = filter_pattern.findall(xml_content)

    if matches:
        print(f"\n❌ Found {len(matches)} instances of filter syntax '| date_format':")
        print("-" * 80)
        for i, match in enumerate(matches[:10], 1):  # Show first 10
            # Clean up XML tags for readability
            clean_match = re.sub(r'<[^>]+>', '', match)
            print(f"{i}. {clean_match}")

        if len(matches) > 10:
            print(f"\n... and {len(matches) - 10} more instances")

        print("\n" + "=" * 80)
        print("❌ PROBLEM: Template still contains filter syntax")
        print("\nYou need to change these to function call syntax:")
        print("   ❌ {{ date | date_format }}")
        print("   ✅ {{ date_format(date) }}")
        print("\nIn Word, use Find & Replace:")
        print("   Find: | date_format")
        print("   And wrap date fields with date_format(...)")
    else:
        print("✅ No filter syntax found")

        # Check for date_format function calls
        func_pattern = re.compile(r'date_format\([^)]+\)')
        func_matches = func_pattern.findall(xml_content)

        if func_matches:
            print(f"\n✅ Found {len(func_matches)} function call instances:")
            for i, match in enumerate(func_matches[:5], 1):
                clean_match = re.sub(r'<[^>]+>', '', match)
                print(f"   {i}. {clean_match}")
            print("\n✅ This is the correct syntax!")
        else:
            print("\n⚠️  No date formatting found at all")
            print("    Check if dates are being formatted")

print("\n" + "=" * 80)
