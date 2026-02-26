# RIR Cover Letter Generation from Excel Spreadsheet

**Date:** 2025-12-28
**Purpose:** Generate FY2026 RIR Cover Letters in bulk from recipient tracking spreadsheet

---

## Overview

This process generates Recipient Information Request (RIR) cover letters from the CORTAP Package 4 tracking spreadsheet. It automates the creation of customized cover letters for multiple recipients using the Jinja2 template infrastructure.

---

## Files Involved

### Input Files
- **Spreadsheet:** `docs/RIR 2026/RIR Cover Letter/CORTAP Package 4 - Reviews - SM Updated 122325.xlsx`
- **Sheet Name:** `RIR Cover Letter 2026 Info`
- **Template:** `app/templates/rir-cover-letter.docx` (Jinja2 template)

### Scripts
- **Generation Script:** `scripts/generate_cover_letters_from_excel.py`

### Output
- **Directory:** `output/cover-letters-fy2026/`
- **Naming Convention:** `CoverLetter_{RecipientID}_{RecipientName}_FY2026.docx`

---

## Field Mapping

The script maps Excel columns to cover letter template fields as follows:

| Template Field | Excel Column | Transformation |
|----------------|--------------|----------------|
| `recipient_name` | Recip Name | Direct mapping with XML escaping |
| `recipient_contact_name` | Recip AE Name | Direct mapping with XML escaping |
| `recipient_contact_title` | Recip Title | Direct mapping with XML escaping |
| `recipient_acronym` | Recipient Accronym | Direct mapping with XML escaping |
| `street_address` | Recip Address | Direct mapping with XML escaping |
| `city` | Recip City | Direct mapping with XML escaping |
| `state` | Recip State | Direct mapping |
| `zip_code` | Recip Zip | Direct mapping |
| `review_type` | Review Type | Direct mapping (e.g., "Triennial Review") |
| `review_type_article` | Review Type | Add "a" or "an" prefix (e.g., "a Triennial Review") |
| `contractor_name` | Contractor Company | "Longevity" → "Longevity Consulting" |
| `lead_title_name` | Lead Reviewer Salutation + Lead Reviewer Name | Combined (e.g., "Ms. Dana Lucas") |
| `lead_email` | *(not in Excel)* | Fixed: "TBD" |
| `lead_phone` | *(not in Excel)* | Fixed: "TBD" |
| `ro_rep_title_name` | RO Rep Salu + RO Rep Name | Combined (e.g., "Mr. Sean McGrath") |
| `ro_rep_phone` | RO Rep Phone | Direct mapping |
| `ro_rep_email` | RO Rep email | Direct mapping |
| `regional_admin_name` | RO Admin Name | Direct mapping |
| `letter_date` | Date | Format as "Month DD, YYYY" |
| `rir_due_date_formatted` | *(fixed)* | Fixed: "February 27, 2026" |

---

## Data Transformations

### Review Type with Article
```python
# Input:  "Triennial Review"
# Output: "a Triennial Review"
# Method: Add "a" or "an" based on first letter
```

### Contractor Name Expansion
```python
# Input:  "Longevity"
# Output: "Longevity Consulting"
```

### XML Character Escaping
```python
# Input:  "Delaware River & Bay Authority"
# Output: "Delaware River &amp; Bay Authority"
# Method: Escape XML special characters (&, <, >, etc.)
```

### Date Formatting
```python
# Input:  2026-01-13 00:00:00
# Output: "January 13, 2026"
```

### Filename Sanitization
- Invalid characters removed: `< > : " / \ | ? *`
- Spaces converted to underscores
- Multiple underscores collapsed to single
- Truncated to 100 characters max

---

## Running the Process

### Prerequisites
1. Excel spreadsheet must be in place with correct sheet name: `RIR Cover Letter 2026 Info`
2. Cover letter template must be ready: `app/templates/rir-cover-letter.docx`
3. Python environment with required dependencies (pandas, openpyxl, docxtpl)

### Command
```bash
python3 scripts/generate_cover_letters_from_excel.py
```

### Expected Output
```
================================================================================
RIR Cover Letter Generator - Excel Spreadsheet
================================================================================

Input file: CORTAP Package 4 - Reviews - SM Updated 122325.xlsx
Template: rir-cover-letter.docx
Output directory: /path/to/output/cover-letters-fy2026

Reading Excel file...
  Sheet: RIR Cover Letter 2026 Info
  Found 36 recipients

================================================================================
Generating 36 cover letter documents...
================================================================================

✓ [ 1] Greater New Haven Transit District       -> CoverLetter_1337_Greater_New_Haven_Transit_District_FY2026.docx (28,755 bytes)
✓ [ 2] Norwalk Transit District                 -> CoverLetter_1339_Norwalk_Transit_District_FY2026.docx (28,741 bytes)
...
✓ [36] Susquehanna Regional Transportation Auth -> CoverLetter_7422_Susquehanna_Regional_Transportation_Authority_FY2026.docx (28,773 bytes)

================================================================================
Generation Summary
================================================================================
Total recipients: 36
Successful: 36
Failed: 0

✓ All 36 cover letter documents generated successfully!

Output directory: /path/to/output/cover-letters-fy2026
```

---

## Template Fields

### Address Block (Table)
- `{{ recipient_contact_name }}`
- `{{ recipient_contact_title }}`
- `{{ recipient_name }}`
- `{{ street_address }}`
- `{{ city }}, {{ state }} {{ zip_code }}`

### Letter Body
- `{{ letter_date }}` - Letter date
- `{{ review_type }}` - Review type without article
- `{{ review_type_article }}` - Review type with "a" or "an"
- `{{ recipient_acronym }}` - Agency acronym
- `{{ contractor_name }}` - Contractor company name
- `{{ lead_title_name }}` - Lead reviewer with salutation
- `{{ lead_email }}` - Lead reviewer email
- `{{ lead_phone }}` - Lead reviewer phone
- `{{ ro_rep_title_name }}` - Regional office rep with salutation
- `{{ ro_rep_phone }}` - Regional office rep phone
- `{{ ro_rep_email }}` - Regional office rep email
- `{{ regional_admin_name }}` - Regional administrator name
- `{{ rir_due_date_formatted }}` - RIR due date

### Footer
- `FY2026 {{ review_type }} – {{ recipient_name }}`

---

## Updating the Template

If you need to update the cover letter template content:

1. **Edit the template:** Open `app/templates/rir-cover-letter.docx` in Microsoft Word
2. **Make changes:** Update dates, text, or formatting as needed
3. **Preserve Jinja2 fields:** Keep all `{{ field_name }}` placeholders intact
4. **Save the template:** Save and close the Word document
5. **Clean old output (optional):** Delete files in `output/cover-letters-fy2026/`
6. **Regenerate:** Run the script again to regenerate all documents with the updated template

**Important:** Do not modify the Jinja2 field names (text inside `{{ }}`) unless you also update the script.

---

## Updating the Spreadsheet

If the Excel spreadsheet is updated with new recipients or changed data:

1. **Update Excel:** Modify the spreadsheet
2. **Save Excel:** Ensure the file is saved
3. **Regenerate:** Run the script - it will regenerate ALL documents (not just changed ones)

**Important:** The script reads the entire spreadsheet and generates documents for all rows. There is no incremental update mode.

---

## Troubleshooting

### Issue: Excel file not found
```
✗ Error: Excel file not found: /path/to/CORTAP Package 4 - Reviews - SM Updated 122325.xlsx
```
**Solution:** Verify the Excel file exists at `docs/RIR 2026/RIR Cover Letter/` with exact filename.

### Issue: Sheet not found
```
✗ Error: Worksheet named 'RIR Cover Letter 2026 Info' not found
```
**Solution:** Verify the sheet name in the Excel file matches exactly: `RIR Cover Letter 2026 Info`

### Issue: Template not found
```
✗ Error: Template file not found: rir-cover-letter.docx
```
**Solution:** Verify `app/templates/rir-cover-letter.docx` exists and is a valid Word document.

### Issue: XML parsing error
```
✗ Error: xmlParseEntityRef: no name
```
**Solution:** This indicates a special character wasn't properly escaped. The script automatically escapes XML characters (&, <, >, etc.), but if this error occurs, check the data for unusual characters.

### Issue: Permission denied writing output
```
PermissionError: [Errno 13] Permission denied: 'output/cover-letters-fy2026/...'
```
**Solution:** Close any open Word documents in the output directory and try again.

### Issue: Footer not rendering
If the footer shows placeholder text instead of actual values:
1. Verify the template was created using the provided scripts
2. Ensure `docxtpl` is processing the footer correctly
3. Regenerate the template using the source document

---

## Script Details

### Key Functions

#### `escape_xml_chars(text: str) -> str`
Escapes XML special characters (&, <, >, etc.) to prevent parsing errors.

#### `add_article_to_review_type(review_type: str) -> str`
Adds "a" or "an" article before review type based on first letter.

#### `format_date_for_letter(date_value) -> str`
Formats date values as "Month DD, YYYY" (e.g., "January 13, 2026").

#### `row_to_cover_letter_context(row: pd.Series) -> dict`
Transforms an Excel row into the template context dictionary.

#### `generate_cover_letter_from_row(template_path, row, output_dir, row_number) -> tuple`
Generates a single cover letter document from one spreadsheet row.

### Data Flow
```
Excel Spreadsheet (RIR Cover Letter 2026 Info sheet)
    ↓ pandas.read_excel()
Pandas DataFrame (rows)
    ↓ row_to_cover_letter_context()
Jinja2 Template Context (dict)
    ↓ DocxTemplate.render()
Generated Word Document (.docx)
    ↓ save to file
Output Directory
```

---

## Configuration Settings

### Hardcoded Values
- **Contractor Name:** "Longevity Consulting" (if "Longevity" in Excel)
- **Lead Email:** "TBD" (not in spreadsheet)
- **Lead Phone:** "TBD" (not in spreadsheet)
- **RIR Due Date:** "February 27, 2026"

### Excel Structure Assumptions
- **Sheet Name:** "RIR Cover Letter 2026 Info"
- **Header Row:** Row 1 (0-indexed row 0)
- **Data Starts:** Row 2 (0-indexed row 1)

### Output Settings
- **Directory:** `output/cover-letters-fy2026/`
- **Format:** Microsoft Word (.docx)
- **Encoding:** UTF-8

---

## Maintenance Notes

### When to Update This Process

1. **New Template Fields Added:** Update `row_to_cover_letter_context()` function
2. **Excel Structure Changes:** Update column names in script
3. **Different Contractor:** Update contractor name mapping in script
4. **New Review Types:** No changes needed - review types come directly from Excel
5. **Different Output Directory:** Modify `output_dir` path in script
6. **Lead Email/Phone Available:** Update script to read from new Excel columns

### Related Documentation
- **RIR Document Generation:** `docs/RIR 2026/RIR-Generation-Process.md`
- **Project Data Schema:** `docs/schemas/project-data-schema-v1.0.json`

---

## Success Criteria

A successful run should produce:
- ✓ 36 documents generated (or match row count in Excel)
- ✓ All documents ~29 KB in size
- ✓ No error messages in output
- ✓ All filenames follow naming convention
- ✓ Documents can be opened in Microsoft Word without errors
- ✓ Footer shows correct recipient name and review type (not placeholder text)
- ✓ All Jinja2 fields replaced with actual data

---

## Future Enhancements

Potential improvements for this process:

1. **Lead Contact Information:** Add lead email and phone to Excel spreadsheet
2. **Dynamic Due Date:** Calculate due date based on letter date + offset days
3. **Incremental Updates:** Only regenerate documents for changed rows
4. **Validation Report:** Generate CSV report of all field values used
5. **Template Preview:** Generate sample document first for review
6. **Email Integration:** Automatically email cover letters to recipients
7. **Parallel Processing:** Generate multiple documents concurrently
8. **Error Recovery:** Skip failed documents and continue processing

---

**Last Updated:** 2025-12-28
**Script Version:** 1.0
**Generated Documents:** 36
**Success Rate:** 100%
