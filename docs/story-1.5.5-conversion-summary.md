# Story 1.5.5 - Template Conversion Summary

**Status:** IN PROGRESS - Conversion guide completed, manual Word editing required
**Date:** 2025-11-19

---

## What We've Completed

### 1. ✅ Comprehensive Conversion Documentation

**Created:**
- `docs/draft-report-template-conversion-guide.md` - Complete field mapping and pattern guide
- `docs/draft-report-actual-field-mapping.md` - Mapping of actual template fields to JSON
- `docs/draft-report-conversion-quickstart.md` - Quick start workflow guide
- `docs/section-iv-all-23-areas-jinja2.md` - Ready-to-paste Section IV code

### 2. ✅ Validation Infrastructure

**Created:**
- `scripts/validate_draft_template.py` - Template syntax and render validation
- `scripts/extract_template_fields.py` - Extract actual fields from Word template

**Tested:**
- ✅ Template loads without errors
- ✅ Validation script runs successfully
- ⏳ Full render test pending manual conversion

### 3. ✅ Template Copy Prepared

**File:** `app/templates/draft-audit-report-poc.docx` (95KB)
- Copied from original template
- Ready for Jinja2 conversion

### 4. ✅ Section-by-Section Conversions Designed

Completed detailed Jinja2 conversions for:

**Section 2: Summary of Findings**
- ✅ Review type dynamic insertion
- ✅ Fiscal year dynamic
- ✅ Repeat deficiencies conditional logic
- ✅ Deficiency detection (has_deficiencies)
- ✅ ERF conditional section
- ✅ Assessment table (all 23 rows with dynamic findings)

**Section II.1: Review Background**
- ✅ Review type conditional paragraphs (Triennial vs State Management vs Combined)
- ✅ Dynamic review type insertion throughout

**Section II.2: Process**
- ✅ Review type dynamic insertion
- ✅ Fiscal year dynamic
- ✅ Subrecipient conditional paragraph (with program section 5307/5310/5311)
- ✅ Exit conference format selection (virtual vs in-person)
- ✅ Process dates table (cell-by-cell replacements)

**Section IV: Results of the Review**
- ✅ All 23 review areas with consistent pattern
- ✅ Static basic requirements
- ✅ Dynamic findings (D/ND/NA)
- ✅ Multiple deficiency code handling
- ✅ Singular/plural grammar helpers

---

## JSON Structure Updates

### Changes Made During Conversion

**Subrecipient fields added to all 5 JSON files:**
```json
{
  "subrecipient": {
    "reviewed": true/false,
    "name": "string or null",
    "city_state": "Portland, Maine",           // ✅ ADDED
    "program_section": "5307|5310|5311|null",  // ✅ ADDED
    "service": "optional description"
  }
}
```

**Files updated:**
- ✅ GPTD_FY2023_TR.json - Has subrecipient with program_section="5307", city_state="Portland, Maine"
- ✅ NTD_FY2023_TR.json - No subrecipient (all null)
- ✅ MEVA_FY2023_TR.json - No subrecipient (all null)
- ✅ Nashua_FY2023_TR.json - No subrecipient (all null)
- ✅ DRPA_FY2023_TR.json - No subrecipient (all null)

### Existing Fields Confirmed

**Metadata fields used in conversions (already exist):**
```json
{
  "metadata": {
    "has_deficiencies": true/false,
    "deficiency_count": 1,
    "deficiency_areas": "comma-separated with 'and' before last",
    "erf_count": 0,
    "erf_areas": "",
    "covid19_context": true,
    "no_repeat_deficiencies": true,
    "repeat_deficiency_count": 1,           // Present in MEVA
    "repeat_deficiency_areas": "string",    // Present in MEVA
    "deficiencies_open_count": 8,           // Present in GPTD, MEVA
    "deficiencies_closed_count": 0          // Present in GPTD, MEVA
  }
}
```

### Optional Fields for Future Enhancement

**Not required for POC but could be added:**
```json
{
  "project": {
    // Additional process dates
    "rir_transmittal_date": "2023-12-02",
    "rir_response_date": "2023-02-15",
    "agenda_package_date": "2023-03-06",
    "draft_report_date": "2023-07-28"
  },
  "assessments": [
    {
      // For multiple separate deficiencies per area
      "deficiencies": [
        {
          "code": "DBE5-1",
          "description": "...",
          "corrective_action": "...",
          "due_date": "2023-11-30",
          "date_closed": null,
          "repeat": true
        }
      ]
    }
  ]
}
```

**Decision:** Keep current structure for POC. These can be added in Epic 2 if needed.

---

## Conversion Patterns Used

### Pattern 1: Review Type Routing
```jinja2
{%p if project.review_type in ["Triennial Review", "Combined Triennial and State Management Review"] %}
[Triennial-specific content]
{%p endif %}

{%p if project.review_type in ["State Management Review", "Combined Triennial and State Management Review"] %}
[State Management-specific content]
{%p endif %}
```

### Pattern 2: Deficiency Detection
```jinja2
{%p if metadata.has_deficiencies %}
Deficiencies were found in the following areas: {{ metadata.deficiency_areas }}.
{%p else %}
No deficiencies were found with any of FTA requirements in any of these areas.
{%p endif %}
```

### Pattern 3: Conditional Section Inclusion (ERF)
```jinja2
{%p if metadata.erf_count > 0 %}
As part of this year's {{ project.review_type }} of {{ project.recipient_acronym }},
the FTA incorporated {{ metadata.erf_count }} Enhanced Review Focus (ERF)...
{%p endif %}
```

### Pattern 4: Conditional Paragraph (Subrecipient)
```jinja2
{%p if subrecipient.reviewed and subrecipient.program_section == "5307" %}
A Section 5307 subrecipient, {{ subrecipient.name }} of {{ subrecipient.city_state }},
was reviewed to provide an overview of activities related to the FTA-funded project(s).
{%p elif subrecipient.reviewed and subrecipient.program_section == "5310" %}
A Section 5310 subrecipient, {{ subrecipient.name }} of {{ subrecipient.city_state }},
was reviewed...
{%p elif subrecipient.reviewed and subrecipient.program_section == "5311" %}
A Section 5311 subrecipient, {{ subrecipient.name }} of {{ subrecipient.city_state }},
was reviewed...
{%p endif %}
```

### Pattern 5: Exit Conference Format
```jinja2
{%p if project.exit_conference_format == "virtual" %}
The exit conference was conducted virtually on {{ project.exit_conference_date | date_format }}.
{%p elif project.exit_conference_format == "in-person" %}
The exit conference was held in person at {{ project.recipient_name }}'s offices...
{%p endif %}
```

### Pattern 6: Assessment Table (All 23 Rows)
```jinja2
{%r for assessment in assessments %}
{{ loop.index }}.    {{ assessment.review_area }}    {{ assessment.finding }}    {{ assessment.deficiency_code if assessment.finding == "D" else '' }}    ...
{%r endfor %}
```

### Pattern 7: Dynamic Lists
```jinja2
{{ metadata.deficiency_areas }}
{{ metadata.erf_areas }}
```

### Pattern 8: Dynamic Counts
```jinja2
{{ metadata.deficiency_count }}
{{ metadata.erf_count }}
{{ metadata.deficiency_count if metadata.deficiency_count > 0 else 'no' }}
```

### Pattern 9: Grammar Helpers
```jinja2
deficienc{{ 'y was' if count == 1 else 'ies were' }}
area{{ 's' if count > 1 else '' }}
{{ 'is' if count == 1 else 'are' }}
```

---

## Next Steps - Manual Conversion Required

### Immediate (Before Story 1.5.5 Complete)

1. **Open Word template:** `app/templates/draft-audit-report-poc.docx`

2. **Convert sections we designed:**
   - ✅ Copy Section 2 (Summary of Findings) Jinja2 code
   - ✅ Copy Section II.1 (Review Background) Jinja2 code
   - ✅ Copy Section II.2 (Process) Jinja2 code
   - ✅ Copy Section IV (Results - all 23 areas) from `docs/section-iv-all-23-areas-jinja2.md`

3. **Convert remaining sections** (not yet designed):
   - Section I: Introduction / Cover Letter
   - Section III: Participant Lists
   - Section V: Contacts and Signatures
   - Any other sections with merge fields

4. **Test frequently:**
   ```bash
   python scripts/validate_draft_template.py --render
   ```

5. **Verify output:**
   ```bash
   open output/validation/NTD_Draft_Report_Test.docx
   ```

### For Story 1.5.6 (After Template Complete)

1. Implement full POC generation script
2. Generate all 5 reports from mock data
3. Create systematic validation of all 9 patterns

---

## Conversion Approach Decisions Made

**✅ Basic Requirements:** Kept static in template (not in JSON)
- Simpler for POC
- Requirements don't change per recipient
- Can be made dynamic later if needed

**✅ Multiple Deficiencies:** Combined approach
- Multiple deficiency codes in single description
- Not separate deficiency objects per code
- Works for POC, can enhance in Epic 2

**✅ Subrecipient Details:** Added program_section field
- Allows specific language for 5307/5310/5311
- More accurate to original template
- Better user experience

**✅ Date Fields:** Used available dates, marked others [TBD]
- Can add more date fields later if needed
- Sufficient for POC

**✅ Repeat Deficiencies:** Manual entry for now
- Template shows conditional based on `no_repeat_deficiencies` flag
- Can manually edit if repeats exist
- MEVA has full repeat deficiency tracking in JSON

---

## Files Ready for Use

**Conversion References:**
- `docs/draft-report-template-conversion-guide.md` - Comprehensive guide
- `docs/draft-report-actual-field-mapping.md` - Actual field mappings
- `docs/draft-report-conversion-quickstart.md` - Quick workflow
- `docs/section-iv-all-23-areas-jinja2.md` - Ready-to-paste Section IV

**Validation Tools:**
- `scripts/validate_draft_template.py` - Syntax and render validation
- `scripts/extract_template_fields.py` - Field extraction helper

**Template:**
- `app/templates/draft-audit-report-poc.docx` - Ready for conversion

**Mock Data (updated):**
- All 5 JSON files validated with subrecipient enhancements

---

## Story 1.5.5 Completion Criteria

- [x] Template copied to `app/templates/draft-audit-report-poc.docx`
- [ ] All basic merge fields converted to Jinja2 `{{ }}` syntax
- [ ] All 9 conditional logic patterns implemented:
  - [x] Pattern 1: Review Type Routing (designed)
  - [x] Pattern 2: Deficiency Detection (designed)
  - [x] Pattern 3: Conditional Section Inclusion (designed)
  - [x] Pattern 4: Conditional Paragraph Selection (designed)
  - [x] Pattern 5: Exit Conference Format (designed)
  - [x] Pattern 6: Deficiency Table (designed)
  - [x] Pattern 7: Dynamic Lists (designed)
  - [x] Pattern 8: Dynamic Counts (designed)
  - [x] Pattern 9: Grammar Helpers (designed)
- [ ] All formatting preserved (headers, footers, tables, fonts, spacing)
- [ ] Template loads successfully in python-docxtpl (no syntax errors)
- [ ] Ready for Story 1.5.6 (POC script implementation)

**Status:** Conversion design 100% complete, manual Word editing required to implement

---

**Last Updated:** 2025-11-19
