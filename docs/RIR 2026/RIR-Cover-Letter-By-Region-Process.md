# RIR Cover Letter Generation by Region

**Date:** 2026-01-05
**Purpose:** Generate FY2026 RIR Cover Letters with region-specific templates and Recipient POC information

---

## Overview

This process generates Recipient Information Request (RIR) cover letters from the CORTAP Package 4 tracking spreadsheet, using region-specific templates for Region 1 and Region 3. It supports 1-3 Recipient Points of Contact (POCs) in the cc: line.

---

## Files Involved

### Input Files
- **Spreadsheet:** `docs/RIR 2026/RIR Cover Letter/CORTAP Package 4 - Reviews - SM Updated 123025.xlsx`
- **Sheet Name:** `RIR Cover Letter 2026 Info`
- **Templates:**
  - Region 1: `app/templates/rir-cover-letter-region1.docx`
  - Region 3: `app/templates/rir-cover-letter-region3.docx`

### Scripts
- **Generation Script:** `scripts/generate_cover_letters_by_region.py`

### Output
- **Directory Structure:**
  - Region 1: `output/cover-letters-fy2026/{timestamp}/region1/`
  - Region 3: `output/cover-letters-fy2026/{timestamp}/region3/`
- **Timestamp Format:** `YYYYMMDD_HHMMSS` (e.g., `20260105_125655`)
- **Naming Convention:** `CoverLetter_{RecipientID}_{RecipientName}_FY2026.docx`

---

## What's New (Compared to Previous Process)

### 1. Updated Excel File
- **New file:** `CORTAP Package 4 - Reviews - SM Updated 123025.xlsx`
- **Column name changes:**
  - `Recip Name` → `Recipient Name`
  - `Recip AE Name` → `Recipient Accountable Executive Name`
  - `Recip Title` → `Recipient Accountable Executive Title`
  - `Recip Address` → `Recipient Address`
  - `Recip City` → `Recipient City`
  - `Recip State` → `Recipient State`
  - `Recip Zip` → `Recipient Zip`
  - `RO Rep Salu` → `Regional Office Representative Salutation`
  - `RO Rep Name` → `Regional Office Representative Name`
  - `RO Rep Phone` → `Regional Office Representative Phone`
  - `RO Rep email` → `Regional Office Representative email`
  - `RO Admin Name` → `Regional Office Administrator Name`

### 2. New Recipient POC Fields (12 columns)
- **POC 1:**
  - `Recipient POC 1 Name Salutation` (Mr./Ms.)
  - `Recipient POC 1 Name`
  - `Recipient POC 1 email`
  - `Recipient POC 1 Phone`
- **POC 2:**
  - `Recipient POC 2 Name Salutation`
  - `Recipient POC 2 Name`
  - `Recipient POC 2 email`
  - `Recipient POC 2 Phone`
- **POC 3:**
  - `Recipient POC 3 Name Salutation`
  - `Recipient POC 3 Name`
  - `Recipient POC 3 email`
  - `Recipient POC 3 Phone`

### 3. Region-Specific Templates
- **Region 1 (REGION I):** 16 recipients
  - Template: `rir-cover-letter-region1.docx`
  - Can be customized with Region 1-specific headers/content
- **Region 3 (REGION III):** 20 recipients
  - Template: `rir-cover-letter-region3.docx`
  - Can be customized with Region 3-specific headers/content

### 4. Dynamic cc: Line
- **Old format:** `{{ recipient_contact_name }}, {{ recipient_name }}`
- **New format:** `{{ recipient_poc_cc_line }}`
  - Dynamically builds cc: line from 1-3 POCs
  - Each POC on separate line with organization name

### 5. Clickable Email Links
- Email addresses in the last paragraph are now clickable hyperlinks
- **Implementation:** Post-processing with `python-docx` after template rendering
  - Renders template with plain text emails first
  - Reopens document and adds hyperlinks via XML element construction
  - Preserves Times New Roman font and document formatting
- Applies to: `{{ lead_email }}` and `{{ ro_rep_email }}`
- Allows recipients to click and open email client directly

### 6. FTA Website URL Hyperlink
- FTA website URL is now clickable in the template
- URL: `https://www.transit.dot.gov/regulations-and-guidance/program-oversight/program-oversight`
- Hyperlink already exists in template (manually added)
- Proper punctuation: period appears after URL, not before

### 7. Template Customizations
- **Region 1 Template:**
  - Header with FTA logo/branding (~220KB file size)
  - Updated footer content
  - Improved address table spacing
- **Region 3 Template:**
  - Updated footer content
  - Improved address table spacing
- **Backup Files:** Template backups created as `.backup-20260106.docx`
  - Examples:
    - 1 POC:
      ```
      Mr. Glen McGough, Greater New Haven Transit District
      ```
    - 2 POCs:
      ```
      Ms. Lisa Rivers, Connecticut Department of Transportation
      Mr. Rich Jankovich, Connecticut Department of Transportation
      ```
    - 3 POCs:
      ```
      Mr. John Doe, Transit Agency Name
      Ms. Jane Smith, Transit Agency Name
      Mr. Bob Jones, Transit Agency Name
      ```

---

## Output Organization

### Timestamped Directory Structure

Cover letters are organized into timestamped directories with region subdirectories:

```
output/cover-letters-fy2026/
└── 20260105_125655/              # Timestamp when generation started
    ├── region1/                  # 16 Region 1 cover letters
    │   ├── CoverLetter_1337_Greater_New_Haven_Transit_District_FY2026.docx
    │   ├── CoverLetter_1339_Norwalk_Transit_District_FY2026.docx
    │   └── ...
    └── region3/                  # 20 Region 3 cover letters
        ├── CoverLetter_7363_Delaware_River_&_Bay_Authority_FY2026.docx
        ├── CoverLetter_1396_Delaware_Department_of_Transportation_FY2026.docx
        └── ...
```

**Benefits:**
- Separate document sets for each region
- Historical tracking via timestamps
- Parallel distribution to regional offices
- Clear audit trail of generation runs
- Easy to regenerate without overwriting previous runs

---

## Field Mapping

### Address Block (Table)
| Jinja2 Template Field | Excel Column | Notes |
|----------------------|--------------|-------|
| `{{ recipient_contact_name }}` | Recipient Accountable Executive Name | XML escaped |
| `{{ recipient_contact_title }}` | Recipient Accountable Executive Title | XML escaped |
| `{{ recipient_name }}` | Recipient Name | XML escaped |
| `{{ street_address }}` | Recipient Address | XML escaped |
| `{{ city }}` | Recipient City | XML escaped |
| `{{ state }}` | Recipient State | Direct mapping |
| `{{ zip_code }}` | Recipient Zip | Direct mapping |

### Letter Body
| Jinja2 Template Field | Excel Column | Notes |
|----------------------|--------------|-------|
| `{{ letter_date }}` | Date | Formatted as "Month DD, YYYY" |
| `{{ review_type }}` | Review Type | Direct (e.g., "Triennial Review") |
| `{{ review_type_article }}` | Review Type | Add "a" or "an" prefix |
| `{{ recipient_acronym }}` | Recipient Accronym | XML escaped |
| `{{ contractor_name }}` | Contractor Company | "Longevity" → "Longevity Consulting" |
| `{{ lead_title_name }}` | Lead Reviewer Salutation + Lead Reviewer Name | Combined |
| `{{ lead_email }}` | Lead Reviewer Email | "TBD" if empty |
| `{{ lead_phone }}` | Lead Reviewer Phone | "TBD" if empty |
| `{{ ro_rep_title_name }}` | Regional Office Representative Salutation + Regional Office Representative Name | Combined |
| `{{ ro_rep_phone }}` | Regional Office Representative Phone | Direct mapping |
| `{{ ro_rep_email }}` | Regional Office Representative email | Direct mapping |
| `{{ regional_admin_name }}` | Regional Office Administrator Name | Direct mapping |
| `{{ rir_due_date_formatted }}` | *(hardcoded)* | Fixed: "February 27, 2026" |

### cc: Line (NEW)
| Jinja2 Template Field | Source | Notes |
|----------------------|--------|-------|
| `{{ recipient_poc_cc_line }}` | POC 1, POC 2, POC 3 + Recipient Name | Dynamically built |

**POC cc: Line Logic:**
1. Check for Recipient POC 1 Name - if present, add `{Salutation} {Name}, {Recipient Name}` on first line
2. Check for Recipient POC 2 Name - if present, add `{Salutation} {Name}, {Recipient Name}` on second line
3. Check for Recipient POC 3 Name - if present, add `{Salutation} {Name}, {Recipient Name}` on third line
4. Join all lines with newline + 4 spaces (to align with "cc:    ")

### Footer (First Page & Default)
| Jinja2 Template Field | Excel Column | Notes |
|----------------------|--------------|-------|
| `{{ review_type }}` | Review Type | Direct mapping |
| `{{ recipient_name }}` | Recipient Name | XML escaped |

---

## Running the Process

### Prerequisites
1. Excel spreadsheet must be in place: `CORTAP Package 4 - Reviews - SM Updated 123025.xlsx`
2. Region-specific templates must exist:
   - `app/templates/rir-cover-letter-region1.docx`
   - `app/templates/rir-cover-letter-region3.docx`
3. Python environment with required dependencies (pandas, openpyxl, docxtpl)

### Command
```bash
python3 scripts/generate_cover_letters_by_region.py
```

### Expected Output
```
================================================================================
RIR Cover Letter Generator - By Region
================================================================================

Input file: CORTAP Package 4 - Reviews - SM Updated 123025.xlsx
Template Region 1: rir-cover-letter-region1.docx
Template Region 3: rir-cover-letter-region3.docx
Output directories:
  Region 1: /path/to/output/cover-letters-fy2026/20260105_125655/region1
  Region 3: /path/to/output/cover-letters-fy2026/20260105_125655/region3

Reading Excel file...
  Sheet: RIR Cover Letter 2026 Info
  Found 36 recipients

  Region I: 16 recipients
  Region III: 20 recipients

================================================================================
Generating 16 Region 1 cover letters...
================================================================================

✓ [ 1] Greater New Haven Transit District       -> CoverLetter_1337_...
...
✓ [16] City of Nashua                           -> CoverLetter_2413_...

================================================================================
Generating 20 Region 3 cover letters...
================================================================================

✓ [ 1] Delaware River & Bay Authority           -> CoverLetter_7363_...
...
✓ [20] Susquehanna Regional Transportation Auth -> CoverLetter_7422_...

================================================================================
Generation Summary
================================================================================
Region I:
  Total: 16
  Successful: 16
  Failed: 0

Region III:
  Total: 20
  Successful: 20
  Failed: 0

Overall:
  Total: 36
  Successful: 36
  Failed: 0

✓ All 36 cover letter documents generated successfully!

Output directories:
  Region 1: /path/to/output/cover-letters-fy2026/20260105_125655/region1
  Region 3: /path/to/output/cover-letters-fy2026/20260105_125655/region3
```

---

## Customizing Region-Specific Templates

The two templates are initially identical. To customize them:

1. **Open template in Word:**
   - Region 1: `app/templates/rir-cover-letter-region1.docx`
   - Region 3: `app/templates/rir-cover-letter-region3.docx`

2. **Customize region-specific content:**
   - Update header/footer with region-specific information
   - Modify regional office contact information
   - Adjust any region-specific language or requirements
   - **Important:** Keep all Jinja2 fields intact (`{{ field_name }}`)

3. **Save and regenerate:**
   - Save the modified template(s)
   - Run: `python3 scripts/generate_cover_letters_by_region.py`

---

## Example Cover Letter Sections

### cc: Line Examples

**Single POC:**
```
cc:	Mr. Glen McGough, Greater New Haven Transit District
	Mr. Sean McGrath, FTA
	Ms. Dana Lucas, Longevity Consulting
```

**Two POCs:**
```
cc:	Ms. Lisa Rivers, Connecticut Department of Transportation
    Mr. Rich Jankovich, Connecticut Department of Transportation
	Mr. Sean McGrath, FTA
	Ms. Dana Lucas, Longevity Consulting
```

**Three POCs:**
```
cc:	Mr. John Doe, Transit Agency Name
    Ms. Jane Smith, Transit Agency Name
    Mr. Bob Jones, Transit Agency Name
	Mr. Sean McGrath, FTA
	Ms. Dana Lucas, Longevity Consulting
```

---

## Troubleshooting

### Issue: POC not appearing in cc: line
**Cause:** POC Name column is empty in Excel
**Solution:** Populate the `Recipient POC # Name` column in Excel

### Issue: Wrong template used for region
**Cause:** Region value in Excel doesn't match exactly
**Solution:** Ensure Region column contains exactly "REGION I" or "REGION III"

### Issue: Template not found
```
✗ Error: Region 1 template file not found
```
**Solution:** Verify template files exist:
- `app/templates/rir-cover-letter-region1.docx`
- `app/templates/rir-cover-letter-region3.docx`

### Issue: Column name not found
```
KeyError: 'Recip Name'
```
**Solution:** Verify you're using the new Excel file (123025 version) with updated column names

---

## Comparison: Old vs New Process

| Aspect | Old Process | New Process |
|--------|-------------|-------------|
| **Excel File** | `122325.xlsx` | `123025.xlsx` |
| **Column Names** | Short names (`Recip Name`) | Full names (`Recipient Name`) |
| **POC Fields** | None | 12 new POC columns |
| **cc: Line** | Static: contact name + recipient | Dynamic: 1-3 POCs + recipient |
| **Templates** | Single template | Region-specific templates |
| **Output Structure** | Single directory | Separate directories by region |
| **Script** | `generate_cover_letters_from_excel.py` | `generate_cover_letters_by_region.py` |
| **Regions Supported** | All in one | Region 1 and Region 3 separately |

---

## Maintenance Notes

### When to Update This Process

1. **New POC columns added:** Update `build_poc_cc_line()` function
2. **New region added:** Add new template and update script logic
3. **Excel column names change:** Update `row_to_cover_letter_context()` function
4. **New required fields:** Update field mapping and template

### Related Documentation
- **Field Mapping Reference:** `docs/RIR 2026/Field-Mapping-Reference.md`
- **Original Process:** `docs/RIR 2026/RIR-Cover-Letter-Generation-Process.md`

---

## Success Criteria

A successful run should produce:
- ✓ Timestamped parent directory created (format: `YYYYMMDD_HHMMSS`)
- ✓ 16 Region 1 documents generated in timestamped region1 subdirectory
- ✓ 20 Region 3 documents generated in timestamped region3 subdirectory
- ✓ Region 1 documents ~220 KB in size (with header logo)
- ✓ Region 3 documents ~30 KB in size
- ✓ No error messages in output
- ✓ All filenames follow naming convention: `CoverLetter_{ID}_{Name}_FY2026.docx`
- ✓ Documents can be opened in Microsoft Word without errors
- ✓ Header displays correctly (logo in Region 1, standard in Region 3)
- ✓ Footer shows correct recipient name and review type
- ✓ Address table spacing is properly formatted
- ✓ All Jinja2 fields replaced with actual data
- ✓ cc: line shows correct number of POCs (1-3)
- ✓ Each POC on separate line with organization name
- ✓ POC names formatted with salutation (Mr./Ms.)
- ✓ **Email addresses are clickable mailto: hyperlinks** (lead_email and ro_rep_email, Times New Roman font)
- ✓ **FTA website URL is clickable hyperlink** with period after URL
- ✓ "Enclosure" paragraph appears on page 1

---

## Latest Production Output

**Location:** `output/cover-letters-fy2026/20260107_105943/`
- Region 1: 16 documents (~220KB each with logo)
- Region 3: 20 documents (~30KB each)

**Template Backups:** `app/templates/rir-cover-letter-region*.backup-20260106.docx`

**Utility Scripts:**
- `scripts/fix_template_url.py` - Fix FTA URL punctuation
- `scripts/fix_cover_letter_phone_field.py` - Fix phone field in templates
- `scripts/add_page_break_before_enclosure.py` - Add page break before Enclosure
- `scripts/remove_page_break_before_enclosure.py` - Remove page break before Enclosure

---

**Last Updated:** 2026-01-07 12:15 PST
**Script Version:** 1.5 (All fixes complete: hyperlinks + phone fields + zip codes + review types)
**Generated Documents:** 36 (16 Region 1 + 20 Region 3)
**Success Rate:** 100%
**Output Structure:** Timestamped directories with region subdirectories
**cc: Line Format:** Each POC on separate line with organization name
**Email Links:** Clickable mailto: hyperlinks (post-processed via python-docx)
**FTA URL:** Clickable hyperlink with proper punctuation
**Phone Fields:** Correct phone numbers (RO rep and lead reviewer)
**Zip Codes:** 5-digit format with leading zeros
**Review Types:** Mapped from short codes (TR, SMR, Combined) to full names
**Template Features:** Logo header (Region 1), updated footer, improved spacing
**Status:** ✅ Production-Ready
