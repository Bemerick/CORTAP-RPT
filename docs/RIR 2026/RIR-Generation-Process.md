# RIR Document Generation by Region from Excel Spreadsheet

**Date:** 2026-01-05
**Purpose:** Generate FY2026 RIR documents in bulk from recipient tracking spreadsheet, organized by region

---

## Overview

This process generates Recipient Information Request (RIR) documents from the CORTAP Package 4 tracking spreadsheet, creating separate outputs for Region 1 (TRO-1) and Region 3 (TRO-3). It automates the creation of customized RIR documents for multiple recipients using the existing RIR template infrastructure.

---

## Files Involved

### Input Files

- **Spreadsheet:** `docs/RIR 2026/RIR Cover Letter/CORTAP Package 4 - Reviews - SM Updated 123025.xlsx`
- **Sheet Name:** `Package 4 - Longevity`
- **Template:** `app/templates/rir-package.docx` (Jinja2 template)

### Scripts

- **Generation Script:** `scripts/generate_rirs_by_region.py`
- **Supporting Services:**
  - `app/services/document_generator.py` - Document generation engine
  - `app/services/context_builder.py` - RIRContextBuilder for data transformation

### Output

- **Directory Structure:**
  - Region 1: `output/rir-documents-fy2026/{timestamp}/region1/`
  - Region 3: `output/rir-documents-fy2026/{timestamp}/region3/`
- **Naming Convention:** `RIR_{RecipientID}_{RecipientName}_FY2026.docx`

---

## Field Mapping

The script maps Excel columns to RIR template fields as follows:

| RIR Template Field          | Excel Column                      | Transformation                               |
| --------------------------- | --------------------------------- | -------------------------------------------- |
| `recipient_id`              | Recipient ID                      | Direct mapping                               |
| `recipient_name`            | Recipient                         | Remove first 4 chars (prepended ID)          |
| `recipient_city_state`      | City + State                      | Combine as "City, ST"                        |
| `region_number`             | Region #                          | Extract number from code (e.g., "TRO-1" → 1) |
| `review_type`               | Type of Review                    | Mapped: TR→Triennial Review, SMR→State Management Review, Combined→Combined Triennial and State Management Review |
| `lead_reviewer_name`        | Lead                              | Direct mapping or "TBD"                      |
| `lead_reviewer_email`       | Lead Email                        | Direct mapping or "TBD"                      |
| `lead_reviewer_phone`       | Lead Phone                        | Direct mapping or "TBD"                      |
| `contractor_name`           | _(not in Excel)_                  | Fixed: "Longevity Consulting"                |
| `fta_program_manager_name`  | FTA PM                            | Direct mapping or "TBD"                      |
| `fta_program_manager_title` | FTA PM Title                      | Direct mapping or "TBD"                      |
| `fta_program_manager_phone` | FTA PM Phone                      | Direct mapping or "TBD"                      |
| `fta_program_manager_email` | FTA PM Email                      | Direct mapping or "TBD"                      |
| `site_visit_dates`          | FY26 Visit Start + FY26 Visit End | Format as date range (YYYY-MM-DD)            |
| `due_date`                  | FY26 RIR Due                      | Format as YYYY-MM-DD or "TBD"                |
| `recipient_website`         | _(not in Excel)_                  | Fixed: "N/A"                                 |

---

## Region-Based Processing

### Region Identification

The script filters recipients by region using the `Region #` column (Column I):

| Region Code | Region Name | Document Count |
|-------------|-------------|----------------|
| TRO-1       | Region 1    | 16 recipients  |
| TRO-3       | Region 3    | 20 recipients  |

### Output Organization

Documents are organized into timestamped directories with region subdirectories:

```
output/rir-documents-fy2026/
└── 20260105_110236/              # Timestamp when generation started
    ├── region1/                  # 16 Region 1 documents
    │   ├── RIR_1337_Greater_New_Haven_Transit_District_FY2026.docx
    │   ├── RIR_1339_Norwalk_Transit_District_FY2026.docx
    │   └── ...
    └── region3/                  # 20 Region 3 documents
        ├── RIR_7363_Delaware_River_&_Bay_Authority_FY2026.docx
        ├── RIR_1396_Delaware_Department_of_Transportation_FY2026.docx
        └── ...
```

**Benefits:**
- Separate document sets for each region
- Historical tracking via timestamps
- Parallel distribution to regional offices
- Clear audit trail of generation runs

---

## Data Transformations

### Recipient Name Cleanup

```python
# Input:  "Greater New Haven Transit District" (already clean in new Excel)
# Output: "Greater New Haven Transit District"
# Note: No cleanup needed - Excel has clean names
```

### Region Number Extraction

```python
# Input:  "TRO-1"
# Output: 1
# Method: Extract trailing number from region code
```

### Review Type Mapping

```python
# Input:  "TR"
# Output: "Triennial Review"
```

### Filename Sanitization

- Invalid characters removed: `< > : " / \ | ? *`
- Spaces converted to underscores
- Multiple underscores collapsed to single
- Truncated to 100 characters max

---

## Running the Process

### Prerequisites

1. Excel spreadsheet must be in place: `docs/RIR 2026/RIR Cover Letter/CORTAP Package 4 - Reviews - SM Updated 123025.xlsx`
2. RIR template must be ready: `app/templates/rir-package.docx`
3. Python environment with required dependencies (pandas, openpyxl, docxtpl)

### Command

```bash
python3 scripts/generate_rirs_by_region.py
```

### Expected Output

```
================================================================================
RIR Document Generator - By Region
================================================================================

Input file: CORTAP Package 4 - Reviews - SM Updated 123025.xlsx
Sheet: Package 4 - Longevity
Output directories:
  Region 1: /path/to/output/rir-documents-fy2026/20260105_110236/region1
  Region 3: /path/to/output/rir-documents-fy2026/20260105_110236/region3

Reading Excel file...
  Found 36 recipients

  Region 1 (TRO-1): 16 recipients
  Region 3 (TRO-3): 20 recipients

Initializing DocumentGenerator...
  Template directory: /path/to/app/templates

================================================================================
Generating 16 Region 1 RIR documents...
================================================================================

✓ [ 1] Greater New Haven Transit District       -> RIR_1337_Greater_New_Haven_Transit_District_FY2026.docx (241,818 bytes)
✓ [ 2] Norwalk Transit District                 -> RIR_1339_Norwalk_Transit_District_FY2026.docx (241,772 bytes)
...
✓ [16] City of Nashua                           -> RIR_2413_City_of_Nashua_FY2026.docx (241,760 bytes)

================================================================================
Generating 20 Region 3 RIR documents...
================================================================================

✓ [ 1] Delaware River & Bay Authority           -> RIR_7363_Delaware_River_&_Bay_Authority_FY2026.docx (241,859 bytes)
✓ [ 2] Delaware Department of Transportation    -> RIR_1396_Delaware_Department_of_Transportation_FY2026.docx (241,817 bytes)
...
✓ [20] Susquehanna Regional Transportation Auth -> RIR_7422_Susquehanna_Regional_Transportation_Authority_FY2026.docx (241,885 bytes)

================================================================================
Generation Summary
================================================================================
Region 1 (TRO-1):
  Total: 16
  Successful: 16
  Failed: 0

Region 3 (TRO-3):
  Total: 20
  Successful: 20
  Failed: 0

Overall:
  Total: 36
  Successful: 36
  Failed: 0

✓ All 36 RIR documents generated successfully!

Output directories:
  Region 1: /path/to/output/rir-documents-fy2026/20260105_110236/region1
  Region 3: /path/to/output/rir-documents-fy2026/20260105_110236/region3
```

---

## Updating the Template

If you need to update the RIR template dates or content:

1. **Edit the template:** Open `app/templates/rir-package.docx` in Microsoft Word
2. **Make changes:** Update dates, text, or formatting as needed
3. **Save the template:** Save and close the Word document
4. **Clean old output (optional):** Delete files in `output/rir-documents-fy2026/`
5. **Regenerate:** Run the script again to regenerate all documents with the updated template

**Note:** The DocumentGenerator caches templates. If you update the template while the script is running, restart the script to pick up changes.

---

## Updating the Spreadsheet

If the Excel spreadsheet is updated with new recipients or changed data:

1. **Update Excel:** Modify `docs/RIR 2026/RIR Cover Letter/CORTAP Package 4 - Reviews - SM Updated 123025.xlsx`
2. **Save Excel:** Ensure the file is saved
3. **Regenerate:** Run the script - it will regenerate ALL documents (not just changed ones)

**Important:** The script reads the entire spreadsheet and generates documents for all rows. There is no incremental update mode.

---

## Troubleshooting

### Issue: Excel file not found

```
✗ Error: Excel file not found: /path/to/CORTAP Package 4 - Reviews - SM Updated_ET_120325.xlsx
```

**Solution:** Verify the Excel file exists at `docs/RIR 2026/` with exact filename.

### Issue: Template not found

```
ERROR: Template file not found: rir-package.docx
```

**Solution:** Verify `app/templates/rir-package.docx` exists and is a valid Word document.

### Issue: Missing data in Excel

```
✗ [12] RECIPIENT NAME -> Error: Missing required field in JSON data: 'recipient_id'
```

**Solution:** Check that the Excel row has all required fields populated (Recipient ID, Recipient, City, State, Lead, FTA PM, etc.).

### Issue: Invalid dates

```
WARNING: Invalid date format in date range: None to None
```

**Solution:** The script will use "TBD" for invalid/missing dates. This is expected behavior if site visit dates aren't set yet.

### Issue: Permission denied writing output

```
PermissionError: [Errno 13] Permission denied: 'output/rir-documents-fy2026/RIR_1337_...'
```

**Solution:** Close any open Word documents in the output directory and try again.

---

## Script Details

### Key Functions

#### `clean_recipient_name(name: str) -> str`

Removes the 4-digit recipient ID prefix from recipient names.

#### `extract_region_number(region_code: str) -> int`

Extracts the numeric region from codes like "TRO-1" → 1.

#### `map_review_type(review_code: str) -> str`

Maps review type codes to full names: "TR" → "Triennial Review".

#### `row_to_canonical_json(row: pd.Series) -> dict`

Transforms an Excel row into the canonical JSON format expected by RIRContextBuilder.

#### `generate_rir_from_row(generator, row, output_dir, row_number) -> tuple`

Generates a single RIR document from one spreadsheet row.

### Data Flow

```
Excel Spreadsheet
    ↓ pandas.read_excel()
Pandas DataFrame (rows)
    ↓ row_to_canonical_json()
Canonical JSON (per project schema)
    ↓ RIRContextBuilder.build_context()
Jinja2 Template Context
    ↓ DocumentGenerator.generate()
Generated Word Document (.docx)
    ↓ save to file
Output Directory
```

---

## Configuration Settings

### Hardcoded Values

- **Contractor Name:** "Longevity Consulting"
- **Recipient Website:** "N/A" (not in spreadsheet)
- **Default Review Type:** "Triennial Review"
- **Default Region:** 1 (if extraction fails)

### Excel Structure Assumptions

- **Header Row:** Row 2 (0-indexed row 1)
- **Data Starts:** Row 3 (0-indexed row 2)
- **Merged Header Row:** Row 1 (skipped)

### Output Settings

- **Directory Structure:** `output/rir-documents-fy2026/{timestamp}/region{1|3}/`
- **Timestamp Format:** `YYYYMMDD_HHMMSS` (e.g., `20260105_110236`)
- **Region Filtering:** Column I (`Region #`) - `TRO-1` for Region 1, `TRO-3` for Region 3
- **Format:** Microsoft Word (.docx)
- **Encoding:** UTF-8

---

## Maintenance Notes

### When to Update This Process

1. **New RIR Fields Added:** Update field mapping table and `row_to_canonical_json()` function
2. **Excel Structure Changes:** Update skiprows parameter in `pd.read_excel()` calls
3. **Different Contractor:** Update hardcoded contractor name in script
4. **New Review Types:** Add to `map_review_type()` mapping dictionary
5. **Different Output Directory:** Modify `output_dir` path in script

### Related Documentation

- **RIR Cover Letter Generation:** `docs/RIR 2026/RIR-Cover-Letter-By-Region-Process.md`
- **Field Mapping Reference:** `docs/RIR 2026/Field-Mapping-Reference.md`
- **RIR Template Conversion:** `docs/rir-template-conversion-guide.md`
- **Project Data Schema:** `docs/schemas/project-data-schema-v1.0.json`
- **RIR Requirements:** `docs/recipient-information-request-requirements.md`
- **Epic Documentation:** `docs/epics.md` (Epic 4 - RIR Template)

---

## Success Criteria

A successful run should produce:

- ✓ 16 Region 1 documents generated in timestamped region1 subdirectory
- ✓ 20 Region 3 documents generated in timestamped region3 subdirectory
- ✓ All documents ~242 KB in size
- ✓ No error messages in output
- ✓ All filenames follow naming convention: `RIR_{ID}_{Name}_FY2026.docx`
- ✓ Documents can be opened in Microsoft Word without errors
- ✓ Timestamped parent directory created (format: `YYYYMMDD_HHMMSS`)
- ✓ **Email addresses are clickable hyperlinks** (lead reviewer and FTA PM) with Times New Roman font
- ✓ **Recipient website URLs are clickable hyperlinks** on page 1
- ✓ **Review types correctly mapped** from short codes (TR, SMR, Combined) to full names

---

## Comparison: Old vs New Process

| Aspect | Old Process | New Process |
|--------|-------------|-------------|
| **Script** | `generate_rirs_from_excel.py` | `generate_rirs_by_region.py` |
| **Excel File** | `121025.xlsx` | `123025.xlsx` |
| **Output Structure** | Single directory | Timestamped with region subdirectories |
| **Region Support** | All in one | Separate Region 1 and Region 3 |
| **Directory Naming** | `output/rir-documents-fy2026/` | `output/rir-documents-fy2026/{timestamp}/region{1\|3}/` |
| **Region Filtering** | None | Based on `Region #` column (TRO-1, TRO-3) |
| **Distribution** | Manual sorting needed | Pre-sorted by region |
| **Audit Trail** | Single generation | Timestamped generations |

**Migration Note:** The old script (`generate_rirs_from_excel.py`) is still available but references an older Excel file. The new region-based script is recommended for all new generations.

---

## Future Enhancements

Potential improvements for this process:

1. **Incremental Updates:** Only regenerate documents for changed rows
2. **Validation Report:** Generate CSV report of all field values used
3. **Template Preview:** Generate sample document first for review
4. **Email Integration:** Automatically email RIRs to recipients
5. **Contractor Detection:** Auto-detect contractor from email domains
6. **Website Lookup:** Attempt to find recipient websites automatically
7. **Parallel Processing:** Generate multiple documents concurrently
8. **Error Recovery:** Skip failed documents and continue processing

---

## Latest Production Output

**Location:** `output/rir-documents-fy2026/20260107_120656/`
- Region 1: 16 documents (~242KB each)
- Region 3: 20 documents (~242KB each)

**Key Features:**
- ✅ Clickable email hyperlinks (post-processed with python-docx)
- ✅ Clickable website hyperlinks
- ✅ Review type mapping (TR/SMR/Combined → full names)
- ✅ Times New Roman font preserved in all hyperlinks

---

**Last Updated:** 2026-01-07
**Script Version:** 2.1 (Region-based + hyperlinks + review type mapping)
**Status:** ✅ Production-Ready
**Generated Documents:** 36 (16 Region 1 + 20 Region 3)
**Success Rate:** 100%
**Output Structure:** Timestamped directories with region subdirectories
