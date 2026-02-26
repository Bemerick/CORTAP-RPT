# Draft Report Template Conversion - Quick Start Guide

**Story:** 1.5.5 - Convert Draft Report Template to python-docxtpl Format
**Time Estimate:** 2-4 hours (depending on template complexity)
**Status:** Ready to start conversion

---

## Prerequisites ✅

- [x] Field inventory complete (`docs/draft-report-field-inventory.md`)
- [x] Conversion guide complete (`docs/draft-report-template-conversion-guide.md`)
- [x] Mock JSON files created (5 files in `tests/fixtures/mock-data/`)
- [x] Template copied to `app/templates/draft-audit-report-poc.docx`
- [x] Validation script ready (`scripts/validate_draft_template.py`)

---

## Conversion Workflow

### Step 1: Open Template in Word

```bash
# Open the template for editing
open app/templates/draft-audit-report-poc.docx
```

**Important:** Enable "Show all formatting marks" (¶ button) to see merge fields clearly

---

### Step 2: Convert Section-by-Section

Follow this recommended order:

1. **Header/Footer fields** (simple text replacements)
2. **Basic project metadata** (recipient, dates, etc.)
3. **FTA and contractor contact info**
4. **Pattern 7 & 8** (lists and counts - easiest patterns)
5. **Pattern 5** (exit conference - simple if/else)
6. **Pattern 2** (deficiency detection - common pattern)
7. **Pattern 1** (review type routing - appears in ~10 locations)
8. **Pattern 4** (subrecipient - conditional paragraph)
9. **Pattern 3** (conditional sections - ERF, etc.)
10. **Pattern 6** (deficiency table - most complex)
11. **Pattern 9** (grammar helpers - throughout)

---

### Step 3: Test Frequently with Validation Script

**After each major change, run validation:**

```bash
# Quick syntax check (runs in ~1 second)
python scripts/validate_draft_template.py

# Full render test with sample data
python scripts/validate_draft_template.py --render

# Test with different mock data files
python scripts/validate_draft_template.py --render --data tests/fixtures/mock-data/GPTD_FY2023_TR.json
python scripts/validate_draft_template.py --render --data tests/fixtures/mock-data/MEVA_FY2023_TR.json
```

**Recommended testing frequency:**
- After converting all basic fields → Quick syntax check
- After implementing each pattern → Quick syntax check
- After completing 3-4 patterns → Full render test
- Before final save → Full render test with all 5 mock files

---

## Common Find & Replace Operations

Use Word's Find & Replace (Ctrl+H or Cmd+H) for bulk conversions:

### Basic Fields (Safe to do in bulk)

| Find | Replace With | Notes |
|------|--------------|-------|
| `[Recipient name]` | `{{ project.recipient_name }}` | Case-sensitive |
| `[Recipient Acronym]` | `{{ project.recipient_acronym }}` | |
| `[Recipient ID]` | `{{ project.recipient_id }}` | |
| `[City, State]` | `{{ project.recipient_city_state }}` | |
| `[REGION #]` | `{{ project.region_number }}` | |
| `[fiscal_year]` | `{{ project.fiscal_year }}` | |

**⚠️ Do NOT use Find & Replace for:**
- `[review_type]` - requires conditional logic in many places
- `[#]` - context-dependent (could be deficiency count, ERF count, etc.)
- `[LIST]` - context-dependent
- `[OR]` - marks conditional blocks, not a field

---

## Validation Script Output Examples

### ✅ Success (Syntax Check)

```
================================================================================
Draft Report Template Validation
================================================================================

🔍 Validating template: draft-audit-report-poc.docx
   Path: /Users/bob.emerick/dev/AI-projects/CORTAP-RPT/app/templates/draft-audit-report-poc.docx
   ✓ Template loaded successfully
   ✓ No Jinja2 syntax errors detected
   ✅ Template syntax is valid

================================================================================
✅ VALIDATION PASSED
================================================================================
```

### ✅ Success (Full Render)

```
🔍 Validating template: draft-audit-report-poc.docx
   ✓ Template loaded successfully
   ✓ No Jinja2 syntax errors detected
   ✅ Template syntax is valid

📂 Loading mock data: NTD_FY2023_TR.json
   ✓ Loaded project: NTD - Triennial Review
   ✓ Deficiencies: 1
   ✓ Assessments: 23 review areas

📝 Rendering template with sample data...
   ⏳ Rendering document...
   ✓ Document rendered successfully
   ✓ Saved to: /Users/bob.emerick/dev/AI-projects/CORTAP-RPT/output/validation/NTD_Draft_Report_Test.docx

   ✅ Template rendered successfully to output/validation/NTD_Draft_Report_Test.docx

================================================================================
✅ VALIDATION PASSED
================================================================================
```

### ❌ Syntax Error Example

```
❌ VALIDATION FAILED:
Jinja2 Syntax Error:
unexpected 'endif'

This means you have an {% endif %} without a matching {% if %}
```

### ❌ Missing Field Error Example

```
❌ RENDER VALIDATION FAILED:
Missing Data Field Error:
'dict object' has no attribute 'recipient_website'

This usually means the template references a field that doesn't exist in the JSON data.
```

---

## Testing with All 5 Mock Files

Once conversion is complete, validate with all scenarios:

```bash
# Test 1: NTD - 1 deficiency, simple case
python scripts/validate_draft_template.py --render --data tests/fixtures/mock-data/NTD_FY2023_TR.json

# Test 2: GPTD - 3 deficiencies, subrecipient, mix of open/closed
python scripts/validate_draft_template.py --render --data tests/fixtures/mock-data/GPTD_FY2023_TR.json

# Test 3: MEVA - 8 deficiencies, repeat deficiency
python scripts/validate_draft_template.py --render --data tests/fixtures/mock-data/MEVA_FY2023_TR.json

# Test 4: Nashua - 1 deficiency, clean operational review
python scripts/validate_draft_template.py --render --data tests/fixtures/mock-data/Nashua_FY2023_TR.json

# Test 5: DRPA - 4 deficiencies all closed, rail system
python scripts/validate_draft_template.py --render --data tests/fixtures/mock-data/DRPA_FY2023_TR.json
```

**Expected outputs:** `output/validation/{ACRONYM}_Draft_Report_Test.docx` for each

---

## Troubleshooting Common Issues

### Issue: Template won't load

**Possible causes:**
- Word file is corrupted
- Unclosed Jinja2 tags

**Solution:**
```bash
# Restore from original and start over
cp "docs/requirements/State_RO_Recipient# _Recipient Name_FY25_TRSMR_DraftFinalReport.docx" \
   app/templates/draft-audit-report-poc.docx
```

### Issue: Syntax errors with {% if %}

**Common mistakes:**
- Missing `{% endif %}`
- Using `{%p if %}` but closing with `{% endif %}` (must match: `{%p endif %}`)
- Using `{%r if %}` instead of `{%r for %}` in tables

**Solution:** Every opening tag needs matching close tag:
- `{% if %}` → `{% endif %}`
- `{%p if %}` → `{%p endif %}`
- `{%r for %}` → `{%r endfor %}`

### Issue: "Missing Data Field" errors

**Cause:** Template references `{{ field }}` that doesn't exist in JSON

**Solution:** Check JSON structure in mock files and verify path:
```bash
# See available fields
cat tests/fixtures/mock-data/NTD_FY2023_TR.json | jq 'keys'
cat tests/fixtures/mock-data/NTD_FY2023_TR.json | jq '.project | keys'
cat tests/fixtures/mock-data/NTD_FY2023_TR.json | jq '.metadata | keys'
```

### Issue: Table rows not repeating

**Cause:** Using `{% for %}` instead of `{%r for %}` in table

**Solution:** Table row loops MUST use `{%r ... %}` syntax:
```jinja2
{%r for assessment in assessments %}
{{ assessment.review_area }}   {{ assessment.finding }}
{%r endfor %}
```

### Issue: Date formatting not working

**Cause:** Filter not applied or date field is null

**Solution:** Check that:
1. Date filter is used: `{{ project.report_date | date_format }}`
2. Field exists in JSON: `cat tests/fixtures/mock-data/NTD_FY2023_TR.json | jq '.project.report_date'`
3. Handle nulls: `{{ project.report_date | date_format if project.report_date else 'TBD' }}`

---

## Completion Checklist

Story 1.5.5 is complete when:

- [ ] All basic merge fields converted to `{{ }}` syntax
- [ ] All 9 conditional patterns implemented:
  - [ ] Pattern 1: Review Type Routing
  - [ ] Pattern 2: Deficiency Detection
  - [ ] Pattern 3: Conditional Section Inclusion
  - [ ] Pattern 4: Conditional Paragraph Selection
  - [ ] Pattern 5: Exit Conference Format
  - [ ] Pattern 6: Deficiency Table
  - [ ] Pattern 7: Dynamic Lists
  - [ ] Pattern 8: Dynamic Counts
  - [ ] Pattern 9: Grammar Helpers
- [ ] Validation passes: `python scripts/validate_draft_template.py`
- [ ] All 5 mock files render successfully
- [ ] Generated documents reviewed for:
  - [ ] Correct data population
  - [ ] Preserved formatting (fonts, spacing, tables)
  - [ ] Correct conditional logic (right paragraphs appear/disappear)
  - [ ] Headers and footers intact
  - [ ] Page breaks preserved

---

## Next Steps After Completion

Once Story 1.5.5 is complete:

1. **Story 1.5.6:** Implement full POC generation script
2. **Story 1.5.7:** Validate all 9 conditional logic patterns systematically
3. **Story 1.5.8:** Document POC results and lessons learned

---

## Quick Reference

### Template File
```
app/templates/draft-audit-report-poc.docx
```

### Validation Commands
```bash
# Syntax check
python scripts/validate_draft_template.py

# Render test
python scripts/validate_draft_template.py --render

# Specific mock file
python scripts/validate_draft_template.py --render --data tests/fixtures/mock-data/MEVA_FY2023_TR.json
```

### Reference Docs
- **Conversion guide:** `docs/draft-report-template-conversion-guide.md`
- **Field inventory:** `docs/draft-report-field-inventory.md`
- **POC plan:** `docs/draft-report-poc-plan.md`
- **Mock JSON:** `tests/fixtures/mock-data/*.json`

### Output Location
```
output/validation/{ACRONYM}_Draft_Report_Test.docx
```

---

**Ready to start? Open the template and begin with simple field conversions!**

```bash
open app/templates/draft-audit-report-poc.docx
```

**Last Updated:** 2025-11-19
