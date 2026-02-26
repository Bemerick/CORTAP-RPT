# Draft Report Template - Comprehensive Field Mapping & Conversion Guide

**Story:** 1.5.5 - Convert Draft Report Template to python-docxtpl Format
**Status:** In Progress (Sections 1-4, 6 complete; Section 5 partial; Section 7 pending)
**Last Updated:** 2025-11-21

This is the authoritative guide for converting the Draft Audit Report Word template to Jinja2 format for use with python-docxtpl.

---

## Table of Contents

1. [Overview](#overview)
2. [Direct Field Replacements](#direct-field-replacements)
3. [Conditional Logic Patterns](#conditional-logic-patterns)
4. [Table Conversion Syntax](#table-conversion-syntax)
5. [Section-by-Section Guide](#section-by-section-guide)
6. [Critical Lessons Learned](#critical-lessons-learned)
7. [Testing & Validation](#testing--validation)

---

## Overview

### Conversion Approach

**Method:** Incremental conversion from clean original template
- Work section by section (1-7)
- Test after each section completes
- Preserve ALL original formatting

### Template File Locations

```
Original: docs/requirements/State_RO_Recipient#_Recipient Name_FY25_TRSMR_DraftFinalReport.docx
Working:  app/templates/draft-report-working.docx
Final:    app/templates/draft-audit-report-poc.docx
```

### Test Script

```bash
python scripts/test_section.py app/templates/draft-report-working.docx tests/fixtures/mock-data/NTD_FY2023_TR.json
```

---

##

 Direct Field Replacements

### Basic Project Fields

| Template Field | Replace With | JSON Path |
|---------------|--------------|-----------|
| `[Recipient name]` | `{{ project.recipient_name }}` | project.recipient_name |
| `[Recipient Acronym]` | `{{ project.recipient_acronym }}` | project.recipient_acronym |
| `[City, State]` | `{{ project.recipient_city_state }}` | project.recipient_city_state |
| `[Recipient ID]` | `{{ project.recipient_id }}` | project.recipient_id |
| `[REGION #]` | `{{ project.region_number }}` | project.region_number |
| `[fiscal_year]` | `{{ project.fiscal_year }}` | project.fiscal_year |

### Review Type Fields

**Replace ALL of these with `{{ project.review_type }}`:**
- `[Triennial Review]`
- `[State Management Review]`
- `[Combined Triennial and State Management Review]`
- `[Triennial Review/State Management Review/Combined Triennial and State Management Review]`

### Contact Information Fields

| Template Field | Replace With | JSON Path |
|---------------|--------------|-----------|
| `[FTA Program Manager Name]` | `{{ fta_program_manager.name }}` | fta_program_manager.name |
| `[FTA Title]` | `{{ fta_program_manager.title }}` | fta_program_manager.title |
| `[phone number]` (FTA) | `{{ fta_program_manager.phone }}` | fta_program_manager.phone |
| `[email]` (FTA) | `{{ fta_program_manager.email }}` | fta_program_manager.email |
| `[reviewer name]` | `{{ contractor.lead_reviewer_name }}` | contractor.lead_reviewer_name |
| `[phone number]` (Reviewer) | `{{ contractor.lead_reviewer_phone }}` | contractor.lead_reviewer_phone |
| `[email]` (Reviewer) | `{{ contractor.lead_reviewer_email }}` | contractor.lead_reviewer_email |
| `[contractor firm]` / `[Contractor Name]` | `{{ contractor.name }}` | contractor.name |
| `[Appropriate Regional Officer]` | `{{ regional_officer.name }}` | regional_officer.name |
| `[Appropriate Regional Officer Titles]` | `{{ regional_officer.title }}` | regional_officer.title |

### Deficiency Fields

| Template Field | Replace With | JSON Path |
|---------------|--------------|-----------|
| `[#]` | `{{ metadata.deficiency_count }}` | metadata.deficiency_count |
| `[LIST]` | `{{ metadata.deficiency_areas }}` | metadata.deficiency_areas |
| `[no]` | `{{ 'no' if metadata.deficiency_count == 0 else metadata.deficiency_count }}` | Conditional |

---

## Conditional Logic Patterns

### Pattern 1: Review Type Routing

**Template Instructions:**
```
[For Triennial Reviews, delete the below paragraph; for State Management Reviews,
delete the above paragraph; for Combined Reviews, include both paragraphs]
```

**Convert to:**
```jinja2
{% if project.review_type == "Triennial Review" %}
[Triennial-specific content]
{% endif %}

{% if project.review_type == "State Management Review" %}
[State Management-specific content]
{% endif %}

{% if project.review_type == "Combined Triennial and State Management Review" %}
[Triennial-specific content]

[State Management-specific content]
{% endif %}
```

### Pattern 2: Deficiency Detection

**Template has `[OR]` marker between alternatives:**

**Convert to:**
```jinja2
{% if metadata.has_deficiencies %}
Deficiencies were found in the following areas: {{ metadata.deficiency_areas }}.
{% else %}
No deficiencies were found with any of the FTA requirements reviewed.
{% endif %}
```

### Pattern 3: Conditional Section Inclusion

**Template has `[IF APPLICABLE]` or `[ADD AS APPLICABLE]` markers:**

**ERF Example:**
```jinja2
{% if metadata.erf_count > 0 %}
As part of this year's {{ project.review_type }} of {{ project.recipient_acronym }}, the FTA incorporated {{ metadata.erf_count }} Enhanced Review Focus (ERF{{ 's' if metadata.erf_count != 1 else '' }}) in the {{ metadata.erf_areas }} area{{ 's' if metadata.erf_count != 1 else '' }}.
{% endif %}
```

**Post-Visit Responses Example:**
```jinja2
{% if metadata.has_post_visit_responses %}
After the site visit, {{ project.recipient_acronym }} provided corrective action responses to address and close deficiencies.
{% endif %}
```

### Pattern 4: Exit Conference Format

**Template has `[If exit conference is conducted virtually/in-person]`:**

```jinja2
{% if project.exit_conference_format == "virtual" %}
Upon completion of the site visit, the reviewers and the FTA regional office staff discussed preliminary findings with the recipient, subsequently presented and provided the findings formally at the exit conference, conducted virtually.
{% elif project.exit_conference_format == "in-person" %}
Upon completion of the site visit, the reviewers and the FTA regional office staff provided a summary of preliminary findings to the recipient at the exit conference.
{% endif %}
```

### Pattern 5: Draft vs Final Report

**Template has `[OMIT FOR FINAL REPORT LETTER]`:**

```jinja2
{% if project.report_status == "Draft" %}
Please review this draft report for accuracy and provide your comments within ten business days.
{% endif %}
```

### Pattern 6: Grammar Helpers

**Subject-verb agreement:**
```jinja2
{{ metadata.deficiency_count }} deficienc{{ 'y' if metadata.deficiency_count == 1 else 'ies' }}
{{ 'was' if metadata.deficiency_count == 1 else 'were' }} identified
```

---

## Table Conversion Syntax

### Critical Rule: Use `{%tr %}` for Table Row Loops

**CORRECT (creates multiple rows):**
```
Header Row: Name | Title | Phone | Email
{%tr for person in attendees %}
{{ person.name }} | {{ person.title }} | {{ person.phone }} | {{ person.email }}
{%tr endfor %}
```

**INCORRECT (creates weird wrapping):**
```
{% for person in attendees %}{{ person.name }} | {{ person.title }}...{% endfor %}
```

### Table Conditional Sections

**For conditional rows, use regular `{% if %}` (not `{%tr if %}`):**

```
{% if attendees.subrecipients %}
{%tr %}
[Subrecipients] (header row)
{%tr endfor %}
{%tr for person in attendees.subrecipients %}
{{ person.name }} | {{ person.title }} | {{ person.phone }} | {{ person.email }}
{%tr endfor %}
{% endif %}
```

### Process Dates Table Example

```
Header Row: Process Date | Process
{%tr for date in project.process_dates %}
{{ date.date }} | {{ date.process }}
{%tr endfor %}
```

### Awards Table Example

```
Header Row: Award Number | Award Amount | Year | Description
{%tr for award in project.awards %}
{{ award.award_number }} | {{ award.award_amount }} | {{ award.year_executed }} | {{ award.description }}
{%tr endfor %}
```

### Assessment Findings Pattern (Section IV)

Each of the 23 assessment areas follows this pattern:

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

**For areas with NA option (5307, 5310, 5311, Cybersecurity):**

```jinja2
{% set area_assessments = assessments|selectattr("review_area", "equalto", "Section 5307 Program Requirements")|list %}
{% set deficiencies = area_assessments|selectattr("finding", "equalto", "D")|list %}
{% set na_items = area_assessments|selectattr("finding", "equalto", "NA")|list %}

{% if na_items %}
Finding: This section only applies to recipients that receive Section 5307 funds directly from the FTA; therefore, the related requirements are not applicable.
{% elif deficiencies|length == 0 %}
Finding: No deficiencies were found with the FTA requirements for Section 5307 Program Requirements.
{% else %}
Finding: {{ deficiencies|length }} {% if deficiencies|length == 1 %}deficiency was{% else %}deficiencies were{% endif %} found with the FTA requirements for Section 5307 Program Requirements.

{% for deficiency in deficiencies %}
Deficiency Description: {{ deficiency.description }}

Corrective Action(s) and Schedule: {{ deficiency.corrective_action %}
{% if not loop.last %}

{% endif %}
{% endfor %}
{% endif %}
```

---

## Section-by-Section Guide

### Section I: Cover Letter

**Completed:** ✅

**Key Conversions:**
- Regional office header: `{{ project.regional_office_header }}`
- Recipient salutation: `{{ project.recipient_salutation }} {{ project.recipient_last_name }}`
- All date references
- Contact information paragraph
- Signature block

**Conditionals:**
- ERF paragraph: `{% if metadata.erf_count > 0 %}`
- Post-visit responses: `{% if metadata.has_post_visit_responses %}`
- Draft instructions: `{% if project.report_status == "Draft" %}`

### Section II: Cover Page & Executive Summary

**Completed:** ✅

**Cover Page Fields:**
- Fiscal year: `{{ project.fiscal_year }}`
- Review type: `{{ project.review_type | upper }}`
- Recipient info block (name, acronym, city/state, ID)
- Region number
- Contractor name
- All review dates

**Executive Summary:**
- Intro paragraphs with recipient and contractor info
- COVID-19 context paragraph: `{% if metadata.covid19_context %}`
- Repeat deficiencies: `{% if metadata.no_repeat_deficiencies %}`
- ERF section: `{% if metadata.erf_count > 0 %}`
- Deficiency summary: `{% if metadata.has_deficiencies %}`
- Summary of Findings table (23 rows loop through assessments)

### Section III: Review Background and Process

**Completed:** ✅

**Background:**
- Triennial Review paragraph: `{% if project.review_type == "Triennial Review" %}`
- State Management Review paragraph: `{% if project.review_type == "State Management Review" %}`
- Previous review year: `{{ project.previous_review_year }}`

**Process:**
- COVID-19 expansion paragraph
- FY and review type references
- Subrecipient/contractor review: Conditionals for 5307, 5310, 5311, contractors
- Exit conference format: `{% if project.exit_conference_format == "virtual" %}`
- Process dates table with `{%tr for date in project.process_dates %}`

### Section IV: Recipient Description

**Completed:** ✅

**Organization:**
- Organization description: `{{ project.organization_description }}`

**Awards and Projects:**
- Open awards table: `{%tr for award in project.awards %}`
- Supplemental awards and first-time assistance conditional
- Completed projects list: `{% for project_item in project.projects_completed %}`
- Ongoing projects list: `{% for project_item in project.projects_ongoing %}`
- Future projects list: `{% for project_item in project.projects_future %}`

### Section V: Results of the Review (23 Assessment Areas)

**Status:** 🔄 10 of 23 complete

**Pattern for each area:**
- Keep "Basic Requirement" text as static
- Convert "Finding" paragraphs using the assessment findings pattern above
- Loop through deficiencies if any exist
- Show deficiency description and corrective action for each

**Completed Areas (1-10):**
1. Legal
2. Financial Management and Capacity
3. Technical Capacity – Award Management
4. Technical Capacity – Program Management & Subrecipient Oversight
5. Technical Capacity – Project Management
6. Transit Asset Management
7. Satisfactory Continuing Control
8. Maintenance
9. Procurement
10. Disadvantaged Business Enterprise (DBE)

**Pending Areas (11-23):**
11. Title VI
12. Americans with Disabilities Act (ADA) – General
13. ADA – Complementary Paratransit
14. Equal Employment Opportunity
15. School Bus
16. Charter Bus
17. Drug Free Workplace Act
18. Drug and Alcohol Program
19. Section 5307 Program Requirements (has NA option)
20. Section 5310 Program Requirements (has NA option)
21. Section 5311 Program Requirements (has NA option)
22. Public Transportation Agency Safety Plan (PTASP)
23. Cybersecurity (has NA option)

### Section VI: Attendees

**Completed:** ✅

**Table Structure:**
- Header row: Name | Title | Phone Number | E-mail Address
- Recipient section: Loop through `attendees.recipient`
- Subrecipients section: Conditional `{% if attendees.subrecipients %}` then loop
- Contractors/Lessees section: Conditional `{% if attendees.contractors_lessees %}` then loop
- FTA section: Loop through `attendees.fta`
- Contractor section: Loop through `attendees.contractor`

**Pattern:**
```
[Section Header]
{%tr for person in attendees.section %}
{{ person.name }} | {{ person.title }} | {{ person.phone }} | {{ person.email }}
{%tr endfor %}
```

### Section VII: Appendices

**Status:** ⏳ Not started

---

## Critical Lessons Learned

### 1. Smart Quotes Are Deadly

**Problem:** Word auto-converts straight quotes to smart quotes, breaking Jinja2 syntax.

**Solution:**
1. **Before editing:** Turn OFF smart quotes in Word:
   - Word → Preferences → AutoCorrect → AutoFormat As You Type
   - UNCHECK: "Straight quotes" with "smart quotes"
   - Restart Word

2. **After editing:** Run cleanup script:
   ```bash
   python scripts/fix_smart_quotes.py app/templates/draft-report-working.docx
   ```

### 2. Always Type Fresh, Never Paste

**Problem:** Copying Jinja2 code from other sources brings hidden XML fragments that break rendering.

**Solution:**
- Always TYPE Jinja2 expressions directly in Word
- Never copy/paste from other documents or text editors
- If you must reference, look at example and type it yourself

### 3. Close Word Completely Before Testing

**Problem:** Word locks the file, preventing test script from reading it.

**Solution:**
- Save changes in Word
- Close Word application completely (Cmd+Q on Mac, not just close window)
- Then run test script

### 4. Case Sensitivity Matters

**Problem:** `PROJECT.field_name` doesn't work.

**Solution:**
- Always use lowercase: `project.field_name`
- Applies to all data structures: `fta_program_manager`, `contractor`, `metadata`, `assessments`

### 5. Table Row Syntax is Different

**Problem:** Using `{% for %}` in tables creates single-row wrapping.

**Solution:**
- Use `{%tr for %}...{%tr endfor %}` to repeat entire rows
- Use regular `{% if %}...{% endif %}` for conditional sections (NOT `{%tr if %}`)

### 6. Test After Every 2-3 Changes

**Problem:** Making many changes before testing makes errors hard to debug.

**Solution:**
- Convert 2-3 fields
- Save and close Word
- Run test script
- Verify output
- Continue

### 7. Incremental Approach Works Best

**Problem:** Trying to convert entire template at once is overwhelming and error-prone.

**Solution:**
- Work section by section (I, II, III, etc.)
- Complete one section fully before moving to next
- Test section after completion
- Document what works

### 8. XML Fragmentation Requires Fresh Typing

**Problem:** Sometimes Jinja2 expressions get split across multiple XML elements inside Word.

**Solution:**
- If expression doesn't render, delete entire expression and retype fresh
- Don't try to edit partially - delete and start over
- This is especially common after copy/paste

---

## Testing & Validation

### Test Data Location

```
tests/fixtures/mock-data/NTD_FY2023_TR.json
```

### Test Script

```bash
# Basic test
python scripts/test_section.py app/templates/draft-report-working.docx tests/fixtures/mock-data/NTD_FY2023_TR.json

# View output
open output/incremental/draft-report-working_test.docx
```

### Test Data Requirements

Your test JSON must include these top-level structures:

```json
{
  "project_id": "...",
  "project": { /* recipient, dates, review info */ },
  "fta_program_manager": { /* name, title, phone, email */ },
  "regional_officer": { /* name, title */ },
  "contractor": { /* name, lead_reviewer_name, phone, email */ },
  "assessments": [ /* 23 assessment objects */ ],
  "erf_items": [],
  "attendees": {
    "recipient": [],
    "subrecipients": [],
    "contractors_lessees": [],
    "fta": [],
    "contractor": []
  },
  "metadata": { /* counts, flags, lists */ }
}
```

### Validation Checklist

After each section conversion:

- [ ] Template loads without errors
- [ ] All fields populate correctly
- [ ] Conditionals show/hide content as expected
- [ ] Tables render with correct number of rows
- [ ] Formatting preserved (fonts, spacing, colors)
- [ ] Headers and footers intact
- [ ] Page breaks preserved

---

## Quick Reference

### Most Common Field Conversions

```
[Recipient name]              → {{ project.recipient_name }}
[Recipient Acronym]           → {{ project.recipient_acronym }}
[City, State]                 → {{ project.recipient_city_state }}
[REGION #]                    → {{ project.region_number }}
[Triennial Review]            → {{ project.review_type }}
[#]                           → {{ metadata.deficiency_count }}
[LIST]                        → {{ metadata.deficiency_areas }}
[FTA Program Manager Name]    → {{ fta_program_manager.name }}
[reviewer name]               → {{ contractor.lead_reviewer_name }}
```

### Most Common Conditionals

```jinja2
{% if metadata.has_deficiencies %}...{% endif %}
{% if metadata.erf_count > 0 %}...{% endif %}
{% if metadata.has_post_visit_responses %}...{% endif %}
{% if project.report_status == "Draft" %}...{% endif %}
{% if project.exit_conference_format == "virtual" %}...{% endif %}
{% if project.review_type == "Triennial Review" %}...{% endif %}
```

### Table Row Loop

```jinja2
{%tr for item in list %}
{{ item.field1 }} | {{ item.field2 }} | {{ item.field3 }}
{%tr endfor %}
```

---

## Next Steps

### To Complete Story 1.5.5:

1. **Finish Section V (Results)** - Convert remaining 13 assessment areas (11-23)
   - Use the same pattern as areas 1-10
   - Add NA conditionals for areas 19, 20, 21, 23
   - Test after every 3-4 areas

2. **Convert Section VII (Appendices)** - Determine if there are fields to convert
   - May be mostly static text
   - Check for any conditional content

3. **Final Testing** - Test with all 5 mock JSON files:
   ```bash
   python scripts/test_section.py app/templates/draft-report-working.docx tests/fixtures/mock-data/NTD_FY2023_TR.json
   python scripts/test_section.py app/templates/draft-report-working.docx tests/fixtures/mock-data/GPTD_FY2023_TR.json
   python scripts/test_section.py app/templates/draft-report-working.docx tests/fixtures/mock-data/MEVA_FY2023_TR.json
   python scripts/test_section.py app/templates/draft-report-working.docx tests/fixtures/mock-data/Nashua_FY2023_TR.json
   python scripts/test_section.py app/templates/draft-report-working.docx tests/fixtures/mock-data/DRPA_FY2023_TR.json
   ```

4. **Final Cleanup**:
   ```bash
   python scripts/fix_smart_quotes.py app/templates/draft-report-working.docx
   python scripts/merge_split_equals.py app/templates/draft-report-working.docx
   ```

5. **Promote to Production**:
   ```bash
   cp app/templates/draft-report-working.docx app/templates/draft-audit-report-poc.docx
   ```

---

**Last Updated:** 2025-11-21
**Story Status:** In Progress (~80% complete)
**Next Milestone:** Complete Section V assessment areas 11-23
