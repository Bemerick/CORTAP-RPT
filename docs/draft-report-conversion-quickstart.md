# Draft Report Template Conversion - Quick Start Guide

**Story:** 1.5.5 - Convert Draft Report Template to python-docxtpl Format
**Last Updated:** 2025-11-21
**Status:** In Progress (~80% complete)

> **Full details:** See `docs/draft-report-actual-field-mapping.md` for comprehensive conversion guide

---

## Quick Reference

### Files

```
Working Template:  app/templates/draft-report-working.docx
Test Data:        tests/fixtures/mock-data/NTD_FY2023_TR.json
Test Script:      scripts/test_section.py
Output:           output/incremental/draft-report-working_test.docx
```

### Essential Commands

```bash
# Test conversion
python scripts/test_section.py app/templates/draft-report-working.docx tests/fixtures/mock-data/NTD_FY2023_TR.json

# View output
open output/incremental/draft-report-working_test.docx

# Fix smart quotes (if needed)
python scripts/fix_smart_quotes.py app/templates/draft-report-working.docx
```

---

## Workflow

### 1. Before You Start

- [ ] Turn OFF smart quotes in Word (Word → Preferences → AutoCorrect → uncheck "straight quotes" with "smart quotes")
- [ ] Restart Word
- [ ] Make a backup copy of template

### 2. Conversion Approach

**Work section by section:**
1. Open template in Word
2. Convert 2-3 fields
3. **Save and close Word completely** (Cmd+Q on Mac)
4. Test with script
5. Verify output
6. Repeat

**Never:**
- Copy/paste Jinja2 code
- Keep Word open while testing
- Convert entire template at once

### 3. After Each Section

```bash
python scripts/test_section.py app/templates/draft-report-working.docx tests/fixtures/mock-data/NTD_FY2023_TR.json
open output/incremental/draft-report-working_test.docx
```

---

## Common Patterns

### Basic Fields

```
[Recipient name]     → {{ project.recipient_name }}
[Recipient Acronym]  → {{ project.recipient_acronym }}
[REGION #]           → {{ project.region_number }}
[Triennial Review]   → {{ project.review_type }}
```

### Conditionals

```jinja2
{% if metadata.has_deficiencies %}
Deficiencies were found.
{% else %}
No deficiencies were found.
{% endif %}
```

### Tables (Critical!)

**Use `{%tr %}` for row loops:**

```
Header Row
{%tr for item in list %}
{{ item.field1 }} | {{ item.field2 }}
{%tr endfor %}
```

**NOT** `{% for %}` (that creates weird wrapping)

### Assessment Areas (Section IV)

```jinja2
{% set area_assessments = assessments|selectattr("review_area", "equalto", "Legal")|list %}
{% set deficiencies = area_assessments|selectattr("finding", "equalto", "D")|list %}

{% if deficiencies|length == 0 %}
Finding: No deficiencies were found with the FTA requirements for Legal.
{% else %}
Finding: {{ deficiencies|length }} {% if deficiencies|length == 1 %}deficiency was{% else %}deficiencies were{% endif %} found with the FTA requirements for Legal.

{% for deficiency in deficiencies %}
Deficiency Description: {{ deficiency.description }}

Corrective Action(s) and Schedule: {{ deficiency.corrective_action }}
{% if not loop.last %}

{% endif %}
{% endfor %}
{% endif %}
```

---

## Section Status

| Section | Status | Notes |
|---------|--------|-------|
| I. Cover Letter | ✅ Complete | All conditionals implemented |
| II. Cover Page & Executive Summary | ✅ Complete | Table with 23 assessments |
| III. Review Background & Process | ✅ Complete | Process dates table |
| IV. Recipient Description | ✅ Complete | Awards, projects tables |
| V. Results (23 areas) | 🔄 43% (10/23) | Areas 1-10 complete, 11-23 pending |
| VI. Attendees | ✅ Complete | All sections with conditionals |
| VII. Appendices | ⏳ Not started | TBD |

---

## Critical Lessons

### 1. Smart Quotes Kill Jinja2
Turn them OFF in Word before editing or use cleanup script after

### 2. Always Type, Never Paste
Pasting brings XML fragments that break rendering

### 3. Close Word Before Testing
Word locks the file - must close completely (Cmd+Q)

### 4. Use {%tr %} in Tables
Regular {% for %} doesn't work in tables - use {%tr for %}...{%tr endfor %}

### 5. Test After Every 2-3 Changes
Don't wait - test frequently to catch errors early

### 6. Case Matters
Use lowercase: `project.field_name` (not `PROJECT.field_name`)

---

## Troubleshooting

### Template won't load
- Check for unclosed {% if %} or {% for %} tags
- Run smart quotes cleanup script
- Restore from backup and retry

### Syntax error: "unexpected endif"
- Missing opening {% if %} tag
- Mismatched {%p if %} with {% endif %} (must use {%p endif %})

### Table rows not repeating
- Using {% for %} instead of {%tr for %}
- Solution: Change to {%tr for %}...{%tr endfor %}

### Fields showing as blank
- Field doesn't exist in JSON
- Case mismatch (PROJECT vs project)
- Check JSON structure: `cat tests/fixtures/mock-data/NTD_FY2023_TR.json | jq '.project'`

---

## Next Steps to Complete Story 1.5.5

### 1. Finish Section V Assessment Areas 11-23

Use same pattern as areas 1-10. Areas 19, 20, 21, 23 need NA conditionals:

```jinja2
{% set na_items = area_assessments|selectattr("finding", "equalto", "NA")|list %}

{% if na_items %}
Finding: This section only applies to recipients that receive Section [5307/5310/5311] funds directly from the FTA; therefore, the related requirements are not applicable.
{% elif deficiencies|length == 0 %}
...
```

### 2. Convert Section VII (if needed)

Check if there are any fields to convert or if it's all static text.

### 3. Final Testing

Test with all 5 mock files:

```bash
for file in tests/fixtures/mock-data/*.json; do
    echo "Testing with $file"
    python scripts/test_section.py app/templates/draft-report-working.docx "$file"
done
```

### 4. Final Cleanup

```bash
python scripts/fix_smart_quotes.py app/templates/draft-report-working.docx
python scripts/merge_split_equals.py app/templates/draft-report-working.docx
```

### 5. Promote to Production

```bash
cp app/templates/draft-report-working.docx app/templates/draft-audit-report-poc.docx
```

---

## Completion Checklist

- [ ] All 7 sections converted
- [ ] All 23 assessment areas in Section V complete
- [ ] Tests pass with all 5 mock JSON files
- [ ] Smart quotes cleaned up
- [ ] Formatting preserved (fonts, tables, spacing)
- [ ] Headers/footers intact
- [ ] Template promoted to `draft-audit-report-poc.docx`

---

**For detailed field mappings, conditional patterns, and lessons learned, see:**
`docs/draft-report-actual-field-mapping.md`

**Last Updated:** 2025-11-21
