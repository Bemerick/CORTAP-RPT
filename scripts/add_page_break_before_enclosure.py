#!/usr/bin/env python3
"""
Add a page break before the "Enclosure" paragraph in cover letter templates.

Usage:
    python scripts/add_page_break_before_enclosure.py
"""

from pathlib import Path
from docx import Document
from docx.oxml.shared import OxmlElement
from docx.oxml.ns import qn


def add_page_break_before_paragraph(paragraph):
    """
    Add a page break before a paragraph.

    Args:
        paragraph: python-docx Paragraph object
    """
    # Get the paragraph properties element
    p_pr = paragraph._element.get_or_add_pPr()

    # Add a page break before
    page_break = OxmlElement('w:pageBreakBefore')
    page_break.set(qn('w:val'), 'true')
    p_pr.append(page_break)


def add_page_break_before_enclosure(template_path: Path) -> bool:
    """
    Add a page break before the "Enclosure" paragraph.

    Args:
        template_path: Path to the template file

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"\nProcessing: {template_path.name}")

        # Open the template
        doc = Document(template_path)

        # Find the "Enclosure" paragraph
        enclosure_found = False
        for i, paragraph in enumerate(doc.paragraphs):
            if paragraph.text.strip() == "Enclosure":
                print(f"  Found 'Enclosure' at paragraph {i}")

                # Add page break before this paragraph
                add_page_break_before_paragraph(paragraph)
                print(f"  ✓ Added page break before 'Enclosure'")

                enclosure_found = True
                break

        if not enclosure_found:
            print(f"  ⚠ 'Enclosure' paragraph not found")
            return False

        # Save the modified template
        doc.save(template_path)
        print(f"  ✓ Template saved")

        return True

    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main script execution."""
    print("=" * 80)
    print("Add Page Break Before 'Enclosure' in Cover Letter Templates")
    print("=" * 80)

    # Setup paths
    project_root = Path(__file__).parent.parent
    template_region1 = project_root / "app" / "templates" / "rir-cover-letter-region1.docx"
    template_region3 = project_root / "app" / "templates" / "rir-cover-letter-region3.docx"

    # Process both templates
    results = []

    if template_region1.exists():
        results.append(add_page_break_before_enclosure(template_region1))
    else:
        print(f"\n✗ Template not found: {template_region1}")
        results.append(False)

    if template_region3.exists():
        results.append(add_page_break_before_enclosure(template_region3))
    else:
        print(f"\n✗ Template not found: {template_region3}")
        results.append(False)

    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)

    if all(results):
        print("✓ Both templates updated successfully!")
    else:
        print("✗ Some templates failed to update")

    return all(results)


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
