# RIR Template Field Mapping Reference

**Date:** 2025-12-28
**Purpose:** Comprehensive field mapping for RIR documents and RIR cover letters

---

## Table of Contents
1. [RIR Cover Letter Field Mapping](#rir-cover-letter-field-mapping)
2. [RIR Document Field Mapping](#rir-document-field-mapping)
3. [Quick Reference Tables](#quick-reference-tables)

---

## RIR Cover Letter Field Mapping

### Source Information
- **Template File:** `app/templates/rir-cover-letter.docx`
- **Excel File:** `docs/RIR 2026/RIR Cover Letter/CORTAP Package 4 - Reviews - SM Updated 122325.xlsx`
- **Excel Sheet:** `RIR Cover Letter 2026 Info`
- **Generation Script:** `scripts/generate_cover_letters_from_excel.py`
- **Output Directory:** `output/cover-letters-fy2026/`

### Field Mappings

| Jinja2 Template Field | Excel Column | Data Type | Transformation/Notes |
|----------------------|--------------|-----------|----------------------|
| **Address Block (Table)** |
| `{{ recipient_contact_name }}` | Recip AE Name | Text | XML escaped |
| `{{ recipient_contact_title }}` | Recip Title | Text | XML escaped |
| `{{ recipient_name }}` | Recip Name | Text | XML escaped |
| `{{ street_address }}` | Recip Address | Text | XML escaped |
| `{{ city }}` | Recip City | Text | XML escaped |
| `{{ state }}` | Recip State | Text | Direct mapping |
| `{{ zip_code }}` | Recip Zip | Text | Direct mapping |
| **Letter Body** |
| `{{ letter_date }}` | Date | Date | Formatted as "Month DD, YYYY" |
| `{{ review_type }}` | Review Type | Text | Direct (e.g., "Triennial Review") |
| `{{ review_type_article }}` | Review Type | Text | Add "a" or "an" prefix |
| `{{ recipient_acronym }}` | Recipient Accronym | Text | XML escaped |
| `{{ contractor_name }}` | Contractor Company | Text | "Longevity" → "Longevity Consulting" |
| `{{ lead_title_name }}` | Lead Reviewer Salutation + Lead Reviewer Name | Text | Combined (e.g., "Ms. Dana Lucas") |
| `{{ lead_email }}` | Lead Reviewer Email | Text | "TBD" if empty |
| `{{ lead_phone }}` | Lead Reviewer Phone | Text | "TBD" if empty |
| `{{ ro_rep_title_name }}` | RO Rep Salu + RO Rep Name | Text | Combined (e.g., "Mr. Sean McGrath") |
| `{{ ro_rep_phone }}` | RO Rep Phone | Text | Direct mapping |
| `{{ ro_rep_email }}` | RO Rep email | Text | Direct mapping |
| `{{ regional_admin_name }}` | RO Admin Name | Text | Direct mapping |
| `{{ rir_due_date_formatted }}` | *(hardcoded)* | Text | Fixed: "February 27, 2026" |
| **Footer (First Page & Default)** |
| `{{ review_type }}` | Review Type | Text | Direct (e.g., "Triennial Review") |
| `{{ recipient_name }}` | Recip Name | Text | XML escaped |

### Example Data Flow (Cover Letter)

```
Excel Row:
  Recip Name: "Greater New Haven Transit District"
  Recip AE Name: "Mario Marrero"
  Review Type: "Triennial Review"
  Lead Reviewer Salutation: "Ms."
  Lead Reviewer Name: "Dana Lucas"

↓ Script Processing ↓

Template Context:
  recipient_name: "Greater New Haven Transit District"
  recipient_contact_name: "Mario Marrero"
  review_type: "Triennial Review"
  review_type_article: "a Triennial Review"
  lead_title_name: "Ms. Dana Lucas"

↓ Jinja2 Rendering ↓

Generated Document:
  Address: "Mario Marrero\nExecutive Director\nGreater New Haven Transit District..."
  Body: "The FTA is conducting a Triennial Review of your agency..."
  Footer: "FY2026 Triennial Review – Greater New Haven Transit District"
```

---

## RIR Document Field Mapping

### Source Information
- **Template File:** `app/templates/rir-package.docx`
- **Excel File:** `docs/RIR 2026/CORTAP Package 4 - Reviews - SM Updated 121025.xlsx`
- **Excel Sheet:** `Package 4 - Longevity`
- **Generation Script:** `scripts/generate_rirs_from_excel.py`
- **Output Directory:** `output/rir-documents-fy2026/`

### Field Mappings

| Template Field (via RIRContextBuilder) | Excel Column | Data Type | Transformation/Notes |
|---------------------------------------|--------------|-----------|----------------------|
| **Project Information** |
| `region_number` | Region # | Integer | Extract number from code (e.g., "TRO-1" → 1) |
| `review_type` | Type of Review | Text | Map code to full name ("TR" → "Triennial Review") |
| `recipient_name` | Recipient Name | Text | XML escaped |
| `recipient_city_state` | City + State | Text | Combined as "City, ST" |
| `recipient_id` | Recipient ID | Text | Direct mapping |
| `recipient_website` | Website | Text | "N/A" if not available |
| `site_visit_start_date` | FY26 Visit Start | Date | Format as YYYY-MM-DD or "TBD" |
| `site_visit_end_date` | FY26 Visit End (Complete by Sept 30, 2026) | Date | Format as YYYY-MM-DD or "TBD" |
| `due_date` | FY26 RIR Due | Date | Format as YYYY-MM-DD or "TBD" |
| **Contractor Information** |
| `contractor_name` | *(hardcoded)* | Text | Fixed: "Longevity Consulting" |
| `lead_reviewer_name` | Lead | Text | "TBD" if empty |
| `lead_reviewer_phone` | Lead Phone | Text | "TBD" if empty |
| `lead_reviewer_email` | Lead Email | Text | "TBD" if empty |
| **FTA Program Manager Information** |
| `fta_program_manager_name` | FTA PM | Text | "TBD" if empty |
| `fta_program_manager_title` | FTA PM Title | Text | "TBD" if empty |
| `fta_program_manager_phone` | FTA PM Phone | Text | "TBD" if empty |
| `fta_program_manager_email` | FTA PM Email | Text | "TBD" if empty |

### Example Data Flow (RIR Document)

```
Excel Row (Package 4 - Longevity):
  Recipient ID: 1337
  Recipient Name: "GREATER NEW HAVEN TRANSIT DISTRICT"
  City: "Hamden"
  State: "CT"
  Region #: "TRO-1"
  Type of Review: "TR"
  Lead: "Dana Lucas"
  FTA PM: "David Schilling"

↓ Script Processing ↓

Canonical JSON:
  {
    "project": {
      "region_number": 1,
      "review_type": "Triennial Review",
      "recipient_name": "GREATER NEW HAVEN TRANSIT DISTRICT",
      "recipient_city_state": "Hamden, CT",
      "recipient_id": "1337",
      "site_visit_start_date": "2026-04-07",
      ...
    },
    "contractor": {
      "contractor_name": "Longevity Consulting",
      "lead_reviewer_name": "Dana Lucas",
      ...
    },
    "fta_program_manager": {
      "fta_program_manager_name": "David Schilling",
      ...
    }
  }

↓ RIRContextBuilder.build_context() ↓

Template Context (processed and expanded)

↓ DocumentGenerator.generate() ↓

Generated RIR Document
```

---

## Quick Reference Tables

### Data Sources Comparison

| Aspect | RIR Cover Letter | RIR Document |
|--------|------------------|--------------|
| **Excel File** | `CORTAP Package 4 - Reviews - SM Updated 122325.xlsx` | `CORTAP Package 4 - Reviews - SM Updated 121025.xlsx` |
| **Sheet Name** | `RIR Cover Letter 2026 Info` | `Package 4 - Longevity` |
| **Skip Rows** | None (header at row 0) | Skip first 2 rows (header at row 3) |
| **Template** | `rir-cover-letter.docx` | `rir-package.docx` |
| **Output Naming** | `CoverLetter_{ID}_{Name}_FY2026.docx` | `RIR_{ID}_{Name}_FY2026.docx` |
| **Document Type** | Simple Jinja2 (DocxTemplate) | Complex (DocumentGenerator + RIRContextBuilder) |

### Common Fields (Present in Both)

| Field Concept | Cover Letter Column | RIR Document Column |
|--------------|---------------------|---------------------|
| Recipient ID | Recipient ID | Recipient ID |
| Recipient Name | Recip Name | Recipient Name |
| Review Type | Review Type | Type of Review |
| Lead Reviewer | Lead Reviewer Name | Lead |
| Lead Email | Lead Reviewer Email | Lead Email |
| Lead Phone | Lead Reviewer Phone | Lead Phone |
| FTA PM Name | *(via RO Rep Name)* | FTA PM |
| FTA PM Email | *(via RO Rep email)* | FTA PM Email |
| FTA PM Phone | *(via RO Rep Phone)* | FTA PM Phone |

**Note:** The RIR Cover Letter uses "RO Rep" (Regional Office Representative) fields for what the RIR Document calls "FTA PM" (FTA Program Manager). These may refer to the same role but are stored in different column names.

### Unique to RIR Cover Letter

| Field | Excel Column | Notes |
|-------|--------------|-------|
| Recipient Contact Name | Recip AE Name | Agency Executive name |
| Recipient Contact Title | Recip Title | Agency Executive title |
| Regional Administrator | RO Admin Name | Signs the letter |
| Letter Date | Date | Date letter is sent |
| Contractor Company | Contractor Company | Usually "Longevity" |
| Lead Salutation | Lead Reviewer Salutation | Mr./Ms. prefix |
| RO Rep Salutation | RO Rep Salu | Mr./Ms. prefix |

### Unique to RIR Document

| Field | Excel Column | Notes |
|-------|--------------|-------|
| Region Number | Region # | Extracted from code |
| City/State | City + State | Combined field |
| Website | Website | Recipient website |
| Site Visit Start | FY26 Visit Start | Date range start |
| Site Visit End | FY26 Visit End | Date range end |
| RIR Due Date | FY26 RIR Due | Submission deadline |
| FTA PM Title | FTA PM Title | Program Manager title |

### Hardcoded Values

| Template | Field | Hardcoded Value | Notes |
|----------|-------|----------------|-------|
| Both | Contractor Name | "Longevity Consulting" | If Excel shows "Longevity" |
| Cover Letter | RIR Due Date | "February 27, 2026" | Fixed deadline |
| RIR Document | Contractor Name | "Longevity Consulting" | Always this value |
| RIR Document | Website | "N/A" | If not in Excel |

### Default/Fallback Values ("TBD")

The following fields default to "TBD" if not provided in Excel:

**Cover Letter:**
- Lead Reviewer Email
- Lead Reviewer Phone

**RIR Document:**
- Lead Reviewer Name
- Lead Reviewer Email
- Lead Reviewer Phone
- FTA PM Name
- FTA PM Title
- FTA PM Phone
- FTA PM Email
- Site Visit Dates (if invalid)
- Due Date (if invalid)

---

## Data Transformation Rules

### 1. Review Type Mapping (RIR Document Only)

| Excel Value | Output Value |
|-------------|--------------|
| TR | Triennial Review |
| TRIENNIAL | Triennial Review |
| TRIENNIAL REVIEW | Triennial Review |

**Note:** RIR Cover Letter reads the full review type directly from Excel (no mapping needed).

### 2. Review Type with Article (Cover Letter Only)

| Excel Value | Output Value |
|-------------|--------------|
| Triennial Review | a Triennial Review |
| State Management Review | a State Management Review |
| Combined Triennial and State Management Review | a Combined Triennial and State Management Review |

**Rule:** Add "a" or "an" based on first letter (vowel = "an", consonant = "a")

### 3. Region Number Extraction (RIR Document Only)

| Excel Value | Output Value |
|-------------|--------------|
| TRO-1 | 1 |
| TRO-10 | 10 |
| *(invalid)* | 1 (default) |

**Rule:** Extract trailing digits from region code

### 4. Recipient Name Cleanup (RIR Document Only)

| Excel Value | Output Value |
|-------------|--------------|
| 1337 GREATER NEW HAVEN TRANSIT DISTRICT | GREATER NEW HAVEN TRANSIT DISTRICT |

**Rule:** Remove first 4 characters (recipient ID prefix)

**Note:** RIR Cover Letter does not need this - the Excel already has clean names in "Recip Name" column.

### 5. XML Character Escaping (Both)

| Character | Escaped Form |
|-----------|--------------|
| & | &amp; |
| < | &lt; |
| > | &gt; |
| " | &quot; |
| ' | &apos; |

**Applied to:** All text fields that may contain special characters (recipient names, addresses, etc.)

### 6. Date Formatting

**RIR Cover Letter:**
- Input: `2026-01-13 00:00:00` (datetime)
- Output: `January 13, 2026` (formatted string)

**RIR Document:**
- Input: `2026-04-07 00:00:00` (datetime)
- Output: `2026-04-07` (ISO format string)

### 7. Contractor Name Expansion (Both)

| Excel Value | Output Value |
|-------------|--------------|
| Longevity | Longevity Consulting |
| Longevity Consulting | Longevity Consulting |

---

## Excel Sheet Structure Notes

### RIR Cover Letter Sheet Structure
```
Row 0: Header row
  Columns: Region, Region States, Region Address Line 1, ..., Recip Name, ...
Row 1+: Data rows (36 recipients)
```

### RIR Document Sheet Structure
```
Row 0: Merged header row (skipped)
Row 1: Sub-headers (skipped)
Row 2: Actual column headers
  Columns: #, Recipient ID, Recipient, Recipient Name, City, State, ...
Row 3+: Data rows
```

---

## Updating Field Mappings

### To Add a New Field to RIR Cover Letter

1. **Add column to Excel:**
   - Sheet: `RIR Cover Letter 2026 Info`
   - Add column with appropriate header

2. **Update template:**
   - Edit: `app/templates/rir-cover-letter.docx`
   - Add Jinja2 field: `{{ new_field_name }}`

3. **Update script:**
   - Edit: `scripts/generate_cover_letters_from_excel.py`
   - Add to `row_to_cover_letter_context()` function:
     ```python
     new_field = str(row.get('New Excel Column', 'default')).strip()
     context['new_field_name'] = new_field
     ```

4. **Regenerate documents:**
   ```bash
   python3 scripts/generate_cover_letters_from_excel.py
   ```

### To Add a New Field to RIR Document

1. **Add column to Excel:**
   - Sheet: `Package 4 - Longevity`
   - Add column with appropriate header (row 2)

2. **Update canonical JSON:**
   - Edit: `scripts/generate_rirs_from_excel.py`
   - Add to `row_to_canonical_json()` function

3. **Update context builder:**
   - Edit: `app/services/context_builder.py`
   - Add field processing in `RIRContextBuilder.build_context()`

4. **Update template:**
   - Template uses fields via context builder
   - May need to update template sections

5. **Regenerate documents:**
   ```bash
   python3 scripts/generate_rirs_from_excel.py
   ```

---

## Troubleshooting Field Mapping Issues

### Field Not Appearing in Generated Document

**Check:**
1. ✓ Column name in Excel matches exactly (case-sensitive)
2. ✓ Jinja2 field name in template matches context dictionary key
3. ✓ Script is reading from correct Excel sheet
4. ✓ No typos in field names
5. ✓ Data exists in Excel (not empty)

### "TBD" Appearing Instead of Data

**Possible causes:**
1. Excel cell is empty/blank
2. Column name mismatch
3. Script has fallback to "TBD" for that field
4. Data format is invalid (e.g., invalid date)

### XML Parsing Error

**Cause:** Special character not escaped
**Solution:** Ensure field is passed through `escape_xml_chars()` function

### Wrong Excel File Being Read

**Check:**
- RIR Cover Letter: Uses `122325` version of Excel file
- RIR Document: Uses `121025` version of Excel file
- Both read from different sheets

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-28 | 1.0 | Initial field mapping reference created |

---

**Last Updated:** 2025-12-28
**Maintained By:** Development Team
**Related Documentation:**
- `docs/RIR 2026/RIR-Generation-Process.md`
- `docs/RIR 2026/RIR-Cover-Letter-Generation-Process.md`
