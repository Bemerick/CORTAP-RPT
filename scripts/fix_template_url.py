#!/usr/bin/env python3
"""
Fix FTA URL in cover letter templates:
1. Make URL clickable (add hyperlink)
2. Move period after URL instead of before

Usage:
    python scripts/fix_template_url.py
"""

from pathlib import Path
from docx import Document
from docx.oxml.shared import OxmlElement
from docx.oxml.ns import qn

def add_hyperlink_to_url(paragraph, url_text: str, display_text: str = None):
    """
    Add a hyperlink to a URL in a paragraph.

    Args:
        paragraph: python-docx Paragraph object
        url_text: The URL to link to
        display_text: Optional display text (defaults to url_text)
    """
    if display_text is None:
        display_text = url_text

    # Search for the URL text in all runs
    for run in paragraph.runs:
        if url_text in run.text:
            # Split the run text around the URL
            parts = run.text.split(url_text, 1)

            # Store reference to the original run element
            original_run_element = run._element

            # Update the current run to have text before URL
            run.text = parts[0]

            # Create hyperlink element
            hyperlink = OxmlElement('w:hyperlink')
            hyperlink.set(qn('w:anchor'), '')

            # Set the hyperlink relationship
            r_id = paragraph.part.relate_to(
                url_text,
                'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',
                is_external=True
            )
            hyperlink.set(qn('r:id'), r_id)

            # Create a new run for the hyperlink
            new_run = OxmlElement('w:r')
            r_pr = OxmlElement('w:rPr')

            # Explicitly set Times New Roman font for the hyperlink
            r_fonts = OxmlElement('w:rFonts')
            r_fonts.set(qn('w:ascii'), 'Times New Roman')
            r_fonts.set(qn('w:hAnsi'), 'Times New Roman')
            r_fonts.set(qn('w:cs'), 'Times New Roman')
            r_pr.append(r_fonts)

            # Set font size to 12pt (24 half-points)
            r_sz = OxmlElement('w:sz')
            r_sz.set(qn('w:val'), '24')
            r_pr.append(r_sz)

            r_sz_cs = OxmlElement('w:szCs')
            r_sz_cs.set(qn('w:val'), '24')
            r_pr.append(r_sz_cs)

            # Add hyperlink color (blue)
            r_color = OxmlElement('w:color')
            r_color.set(qn('w:val'), '0563C1')  # Word hyperlink blue
            r_pr.append(r_color)

            # Add underline
            r_u = OxmlElement('w:u')
            r_u.set(qn('w:val'), 'single')
            r_pr.append(r_u)

            new_run.append(r_pr)

            # Add the URL text with space preservation
            r_text = OxmlElement('w:t')
            r_text.set(qn('xml:space'), 'preserve')
            r_text.text = display_text
            new_run.append(r_text)

            hyperlink.append(new_run)

            # Insert the hyperlink right after the current run
            original_run_element.addnext(hyperlink)

            # Add remaining text if any - insert it right after the hyperlink
            if len(parts) > 1 and parts[1]:
                from copy import deepcopy

                # Create a new run element for the remaining text
                remaining_run = OxmlElement('w:r')

                # Copy run properties from original using deepcopy
                if original_run_element.rPr is not None:
                    remaining_r_pr = deepcopy(original_run_element.rPr)
                    remaining_run.append(remaining_r_pr)

                # Add the remaining text with space preservation
                remaining_text = OxmlElement('w:t')
                remaining_text.set(qn('xml:space'), 'preserve')
                remaining_text.text = parts[1]
                remaining_run.append(remaining_text)

                # Insert right after the hyperlink
                hyperlink.addnext(remaining_run)

            return True

    return False


def fix_fta_url_in_template(template_path: Path) -> bool:
    """
    Fix the FTA URL in a cover letter template:
    1. Move period from before URL to after URL

    The URL is already a hyperlink in the template, so we just need to fix the punctuation.

    Args:
        template_path: Path to the template file

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"\nProcessing: {template_path.name}")

        # Open the template
        doc = Document(template_path)

        # The URL to find
        fta_url = "https://www.transit.dot.gov/regulations-and-guidance/program-oversight/program-oversight"

        # Search all paragraphs for the URL
        url_found = False
        for i, paragraph in enumerate(doc.paragraphs):
            para_text = paragraph.text

            # Look for the pattern "at .  https://..." (note: period before URL)
            if "at ." in para_text and fta_url in para_text:
                print(f"  Found URL in paragraph {i}")

                # The paragraph structure has:
                # - A run with text ending in "at .  "
                # - A hyperlink element with the URL

                # First, find and fix the run that ends with "at .  "
                for run in paragraph.runs:
                    if run.text.endswith("at .  "):
                        original = run.text
                        # Remove the period and extra space
                        run.text = run.text.rstrip()  # Remove trailing spaces
                        if run.text.endswith("."):
                            run.text = run.text[:-1]  # Remove the period
                        run.text = run.text + " "  # Add single space back
                        print(f"  Removed period before URL")
                        print(f"    Before: '{original[-20:]}'")
                        print(f"    After:  '{run.text[-20:]}'")
                        break

                # Now find the hyperlink element and add a period after it
                from docx.oxml.ns import qn
                for elem in paragraph._element:
                    if elem.tag == qn('w:hyperlink'):
                        # Create a new run after the hyperlink with just a period
                        from docx.oxml.shared import OxmlElement
                        period_run = OxmlElement('w:r')
                        period_text = OxmlElement('w:t')
                        period_text.text = "."
                        period_run.append(period_text)

                        # Insert the period run right after the hyperlink
                        elem.addnext(period_run)
                        print(f"  Added period after URL")
                        url_found = True
                        break

                break

        if not url_found:
            print(f"  ⚠ URL not found in template")
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
    print("Fix FTA URL in Cover Letter Templates")
    print("=" * 80)

    # Setup paths
    project_root = Path(__file__).parent.parent
    template_region1 = project_root / "app" / "templates" / "rir-cover-letter-region1.docx"
    template_region3 = project_root / "app" / "templates" / "rir-cover-letter-region3.docx"

    # Process both templates
    results = []

    if template_region1.exists():
        results.append(fix_fta_url_in_template(template_region1))
    else:
        print(f"\n✗ Template not found: {template_region1}")
        results.append(False)

    if template_region3.exists():
        results.append(fix_fta_url_in_template(template_region3))
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
