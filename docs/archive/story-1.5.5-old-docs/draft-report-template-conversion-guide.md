# Draft Audit Report Template - python-docxtpl Conversion Guide

**Story:** 1.5.5 - Convert Draft Report Template to python-docxtpl Format
**Created:** 2025-11-19
**Updated:** 2025-11-19 (with actual conversions completed)
**Source Template:** `docs/requirements/State_RO_Recipient# _Recipient Name_FY25_TRSMR_DraftFinalReport.docx`
**Target Template:** `app/templates/draft-audit-report-poc.docx`
**Status:** Conversion design complete, manual Word editing in progress

---

## Overview

This guide provides step-by-step instructions for converting the Draft Audit Report template to python-docxtpl format using Jinja2 syntax. The conversion maps Word merge fields like `[recipient_name]` to JSON data paths like `{{ project.recipient_name }}`.

**✅ COMPLETED:** Detailed Jinja2 conversions designed for Sections 2, II.1, II.2, and IV (all 23 review areas)
**⏳ IN PROGRESS:** Manual Word editing to implement conversions
**📄 READY TO USE:** See `docs/section-iv-all-23-areas-jinja2.md` for complete Section IV code

**Prerequisites:**
- ✅ Field inventory complete (Story 1.5.1)
- ✅ Pattern mapping complete (Story 1.5.2)
- ✅ Mock JSON files created (Story 1.5.4)

---

## Step 1: Create Template Copy

1. **Copy original template:**
   ```bash
   cp "docs/requirements/State_RO_Recipient# _Recipient Name_FY25_TRSMR_DraftFinalReport.docx" \
      app/templates/draft-audit-report-poc.docx
   ```

2. **Open the copy in Microsoft Word**

3. **Enable "Show all formatting marks"** (¶ button) to see merge fields clearly

---

## Step 2: Basic Merge Field Conversions

### JSON Data Structure Reference

```json
{
  "project_id": "NTD-FY2023-TR-1339",
  "project": {
    "recipient_name": "Norwalk Transit District",
    "recipient_acronym": "NTD",
    "recipient_id": "1339",
    "recipient_city_state": "Norwalk, Connecticut",
    "region_number": 1,
    "review_type": "Triennial Review",
    "fiscal_year": 2023,
    "site_visit_start_date": "2023-03-28",
    "site_visit_end_date": "2023-05-15",
    "exit_conference_date": "2023-05-15",
    "exit_conference_format": "virtual",
    "report_date": "2023-07-11"
  },
  "fta_program_manager": {
    "name": "Peter S. Butler",
    "title": "Regional Administrator",
    "phone": "617-494-2729",
    "email": "peter.butler@dot.gov",
    "region": "Region 1"
  },
  "contractor": {
    "name": "Qi Tech, LLC",
    "lead_reviewer_name": "Gwen Larson",
    "lead_reviewer_phone": "920-746-4595",
    "lead_reviewer_email": "gwen_larson@qitechllc.com"
  },
  "subrecipient": {
    "reviewed": false,
    "name": null
  },
  "metadata": {
    "has_deficiencies": true,
    "deficiency_count": 1,
    "deficiency_areas": "Disadvantaged Business Enterprise",
    "erf_count": 0,
    "erf_areas": ""
  }
}
```

### Field Mapping Table

Use Word's Find & Replace (Ctrl+H) to convert fields systematically:

| Original Field | Jinja2 Replacement | Notes |
|----------------|-------------------|-------|
| `[Recipient name]` | `{{ project.recipient_name }}` | Case-sensitive variations exist |
| `[RECIPIENT NAME]` | `{{ project.recipient_name | upper }}` | All caps version |
| `[recipient name]` | `{{ project.recipient_name }}` | Lowercase version |
| `[Recipient Acronym]` | `{{ project.recipient_acronym }}` | |
| `[Recipient ID]` | `{{ project.recipient_id }}` | |
| `[City, State]` | `{{ project.recipient_city_state }}` | |
| `[Recipient website]` | `{{ project.recipient_website }}` | May be null |
| `[REGION #]` | `{{ project.region_number }}` | Number only |
| `[review_type]` | `{{ project.review_type }}` | **Critical - drives conditionals** |
| `[fiscal_year]` | `{{ project.fiscal_year }}` | Year number (2023) |

### Date Fields

| Original Field | Jinja2 Replacement | Format |
|----------------|-------------------|--------|
| `[site_visit_start_date]` | `{{ project.site_visit_start_date | date_format }}` | March 28, 2023 |
| `[site_visit_end_date]` | `{{ project.site_visit_end_date | date_format }}` | March 28, 2023 |
| `[exit_conference_date]` | `{{ project.exit_conference_date | date_format }}` | March 28, 2023 |
| `[report_date]` | `{{ project.report_date | date_format }}` | July 11, 2023 |

**Note:** Date formatting will be handled by POC script in Story 1.5.6

### FTA Contact Fields

| Original Field | Jinja2 Replacement |
|----------------|-------------------|
| `[FTA PM Name]` | `{{ fta_program_manager.name }}` |
| `[FTA Title]` | `{{ fta_program_manager.title }}` |
| `[phone number]` | `{{ fta_program_manager.phone }}` |
| `[email]` | `{{ fta_program_manager.email }}` |

### Contractor Fields

| Original Field | Jinja2 Replacement |
|----------------|-------------------|
| `[contractor firm]` | `{{ contractor.name }}` |
| `[contractor name]` | `{{ contractor.lead_reviewer_name }}` |
| `[reviewer name]` | `{{ contractor.lead_reviewer_name }}` |
| `[lead reviewer phone]` | `{{ contractor.lead_reviewer_phone }}` |
| `[lead reviewer email]` | `{{ contractor.lead_reviewer_email }}` |

### Derived Fields (Metadata)

| Original Field | Jinja2 Replacement |
|----------------|-------------------|
| `[#]` (deficiency count) | `{{ metadata.deficiency_count }}` |
| `[LIST]` (deficiency areas) | `{{ metadata.deficiency_areas }}` |
| `[ERF count]` | `{{ metadata.erf_count }}` |
| `[ERF areas]` | `{{ metadata.erf_areas }}` |

---

## Step 3: Implement Conditional Logic Patterns

### Pattern 1: Review Type Routing (FR-2.1)

**Template Instructions to Replace:**
```
[For Triennial Reviews, delete the below paragraph...]
[For State Management Reviews, delete the below paragraph...]
```

**Jinja2 Implementation:**

```jinja2
{% if project.review_type == "Triennial Review" %}
    [Triennial Review specific content]
{% elif project.review_type == "State Management Review" %}
    [State Management Review specific content]
{% elif project.review_type == "Combined Triennial and State Management Review" %}
    [Combined review content - usually both paragraphs]
{% endif %}
```

**Locations in Template:**
- Section 1: Background
- Section 2: Review Scope
- Section 3: Review Process
- Multiple other locations (~10+ instances)

**Important:** Use `{%p ... %}` for paragraph-level conditionals to preserve formatting

---

### Pattern 2: Deficiency Detection & Alternative Content (FR-2.2)

**Template Instructions to Replace:**
```
[OR] - marks alternative content based on deficiencies
```

**Jinja2 Implementation:**

**Example 1: Summary paragraph**
```jinja2
{% if metadata.has_deficiencies %}
Deficiencies were found in the following review areas: {{ metadata.deficiency_areas }}.
{% else %}
No deficiencies were found with any of the FTA requirements reviewed.
{% endif %}
```

**Example 2: Closing statement**
```jinja2
{% if metadata.has_deficiencies %}
{{ project.recipient_acronym }} must address the {{ metadata.deficiency_count }}
deficienc{{ 'ies' if metadata.deficiency_count > 1 else 'y' }} identified in this review.
{% else %}
{{ project.recipient_acronym }} demonstrated full compliance with all FTA requirements reviewed.
{% endif %}
```

**Locations:**
- Executive Summary
- Section 4: Review Findings
- Closing Section

---

### Pattern 3: Conditional Section Inclusion (FR-2.3)

**Template Instructions to Replace:**
```
[ADD AS APPLICABLE] - sections that may or may not appear
```

**Jinja2 Implementation:**

**Example: ERF Section**
```jinja2
{% if metadata.erf_count > 0 %}

## Enhanced Review Focus Areas

During the review, {{ metadata.erf_count }} Enhanced Review Focus (ERF) area{{ 's' if metadata.erf_count > 1 else '' }}
{{ 'were' if metadata.erf_count > 1 else 'was' }} identified: {{ metadata.erf_areas }}.

[ERF details table here...]

{% endif %}
```

**Sections to Make Conditional:**
- Enhanced Review Focus (ERF) section
- Subrecipient section
- Repeat deficiencies section (if applicable)

---

### Pattern 4: Conditional Paragraph Selection (FR-2.4)

**Template Instructions to Replace:**
```
[If the Triennial Review included a review of subrecipient(s), include the below paragraph]
```

**Jinja2 Implementation:**

```jinja2
{% if subrecipient.reviewed %}
This review included an assessment of {{ subrecipient.name }}'s compliance with applicable
FTA requirements as a subrecipient of {{ project.recipient_name }}.
{% endif %}
```

**Locations:**
- Section 1: Background
- Section 2: Review Scope

---

### Pattern 5: Exit Conference Format Selection (FR-2.5)

**Template Instructions to Replace:**
```
[Virtual vs in-person exit conference paragraph]
```

**Jinja2 Implementation:**

```jinja2
{% if project.exit_conference_format == "virtual" %}
The exit conference was conducted virtually on {{ project.exit_conference_date | date_format }}.
{% elif project.exit_conference_format == "in-person" %}
The exit conference was held in person at {{ project.recipient_name }}'s offices on
{{ project.exit_conference_date | date_format }}.
{% endif %}
```

**Location:**
- Section 3: Review Process

---

### Pattern 6: Deficiency Table Display (FR-2.6)

**Most Complex Pattern** - 23-row table with conditional content population

**Jinja2 Implementation:**

```jinja2
{% if metadata.has_deficiencies %}

[Table header row]
| Review Area | Finding | Deficiency Code | Description | Corrective Action | Due Date | Status |

{%r for assessment in assessments %}
{% if assessment.finding == "D" %}
{{ assessment.review_area }}	{{ assessment.finding }}	{{ assessment.deficiency_code }}	{{ assessment.description }}	{{ assessment.corrective_action }}	{{ assessment.due_date | date_format if assessment.due_date }}	{{ 'Closed ' + (assessment.date_closed | date_format) if assessment.date_closed else 'Open' }}
{% endif %}
{%r endfor %}

{% endif %}
```

**Important Notes:**
- Use `{%r ... %}` for table row repetition in python-docxtpl
- Only show rows where `assessment.finding == "D"`
- All other assessments (ND, NA) are NOT shown in deficiency table
- Table completely hidden if `has_deficiencies == false`

**Alternative: Full Assessment Table (23 rows)**

If the template shows all 23 areas with findings (not just deficiencies):

```jinja2
{%r for assessment in assessments %}
{{ assessment.review_area }}	{{ assessment.finding }}	{{ assessment.deficiency_code or 'N/A' }}	{{ assessment.description or '' }}	{{ assessment.corrective_action or '' }}	{{ assessment.due_date | date_format if assessment.due_date else '' }}	{{ 'Closed ' + (assessment.date_closed | date_format) if assessment.date_closed else ('Open' if assessment.finding == 'D' else '') }}
{%r endfor %}
```

**Location:**
- Section 4: Deficiency Table

---

### Pattern 7: Dynamic List Population (FR-2.7)

**Template Markers:**
```
[LIST] - comma-separated lists with proper grammar
```

**Jinja2 Implementation:**

Already handled by `metadata.deficiency_areas` and `metadata.erf_areas` which are pre-formatted strings:

```jinja2
{{ metadata.deficiency_areas }}
```

**Output Examples:**
- 1 item: "Legal"
- 2 items: "Legal and Financial Management"
- 3+ items: "Legal, Financial Management, and Procurement"

**Locations:**
- Anywhere lists of deficiency areas are mentioned
- ERF areas lists
- Review scope descriptions

---

### Pattern 8: Dynamic Counts (FR-2.8)

**Template Markers:**
```
[#] - number or "no"
```

**Jinja2 Implementation:**

```jinja2
{{ metadata.deficiency_count if metadata.deficiency_count > 0 else 'no' }}
```

**Examples:**
- `{{ metadata.deficiency_count }}` → "3"
- `{{ metadata.deficiency_count if metadata.deficiency_count > 0 else 'no' }}` → "no" (when count is 0)
- `{{ metadata.erf_count }}` → "2"

**Locations:**
- Executive summary
- Throughout narrative sections

---

### Pattern 9: Grammar Helpers (FR-2.9)

**Jinja2 Implementation:**

**Pluralization:**
```jinja2
{{ metadata.deficiency_count }} deficienc{{ 'ies' if metadata.deficiency_count != 1 else 'y' }}
{{ metadata.erf_count }} area{{ 's' if metadata.erf_count != 1 else '' }}
```

**Subject-verb agreement:**
```jinja2
{{ 'were' if metadata.deficiency_count != 1 else 'was' }} identified
{{ 'are' if metadata.deficiency_count != 1 else 'is' }} required
```

**Article selection:**
```jinja2
{{ 'an' if metadata.deficiency_count == 1 else '' }} Enhanced Review Focus
```

**Locations:**
- Throughout document wherever counts appear

---

## Step 4: Special Considerations

### Document Status Field

The template has a `[Draft/Final]` field that should be hardcoded during POC:

```jinja2
Draft
```

**Note:** In production (Epic 2+), this would be a parameter, but for POC testing, use "Draft"

### COVID-19 Context

If mock JSON includes `metadata.covid19_context: true`, add optional paragraph:

```jinja2
{% if metadata.covid19_context %}
This review was conducted during the COVID-19 public health emergency. FTA granted
administrative relief and flexibilities which were addressed during the review.
{% endif %}
```

### Repeat Deficiencies

```jinja2
{% if metadata.repeat_deficiency_count > 0 %}
Note: {{ metadata.repeat_deficiency_count }} deficienc{{ 'ies' if metadata.repeat_deficiency_count != 1 else 'y' }}
identified in this review {{ 'are' if metadata.repeat_deficiency_count != 1 else 'is' }} repeat findings
from previous reviews.
{% endif %}
```

---

## Step 5: Preservation Checklist

**Verify the following are preserved during conversion:**

- [ ] Header with region number, recipient ID
- [ ] Footer with page numbers
- [ ] All page breaks
- [ ] Table formatting (borders, shading, column widths)
- [ ] Font styles:
  - [ ] Bold headings
  - [ ] Italic emphasis
  - [ ] Red text for template instructions (can be removed)
- [ ] Paragraph spacing and indentation
- [ ] Bullet points and numbered lists
- [ ] Signature blocks at end

---

## Step 6: Testing Strategy

After conversion, test with each of the 5 mock JSON files:

1. **NTD_FY2023_TR.json** - 1 deficiency, no subrecipient, virtual
2. **GPTD_FY2023_TR.json** - 3 deficiencies (2 closed, 1 open), subrecipient, virtual
3. **MEVA_FY2023_TR.json** - 8 deficiencies (1 repeat), no subrecipient, virtual
4. **Nashua_FY2023_TR.json** - 1 deficiency (financial only), clean operational, virtual
5. **DRPA_FY2023_TR.json** - 4 deficiencies (all closed), rail system, virtual

**Expected Variations:**
- Deficiency counts: 1, 3, 4, 8
- Deficiency table rows: 1, 3, 4, 8
- Subrecipient paragraph: Only in GPTD
- Repeat deficiency note: Only in MEVA
- All should show virtual exit conference paragraph

---

## Step 7: Save and Validate

1. **Save template** as `app/templates/draft-audit-report-poc.docx`

2. **Verify file structure:**
   ```bash
   ls -lh app/templates/draft-audit-report-poc.docx
   ```

3. **Test template loads in python-docxtpl** (Story 1.5.6):
   ```python
   from docxtpl import DocxTemplate

   template = DocxTemplate("app/templates/draft-audit-report-poc.docx")
   print("Template loaded successfully!")
   ```

4. **Document any issues or edge cases** for Story 1.5.7 validation

---

## Quick Reference: python-docxtpl Syntax

| Use Case | Syntax | Example |
|----------|--------|---------|
| Simple variable | `{{ variable }}` | `{{ project.recipient_name }}` |
| Nested object | `{{ object.property }}` | `{{ fta_program_manager.title }}` |
| If/else (inline) | `{% if %}...{% endif %}` | `{% if has_deficiencies %}...{% endif %}` |
| If/else (paragraph) | `{%p if %}...{%p endif %}` | `{%p if review_type == "TR" %}...{%p endif %}` |
| For loop (table row) | `{%r for %}...{%r endfor %}` | `{%r for a in assessments %}...{%r endfor %}` |
| Filter (uppercase) | `{{ var | upper }}` | `{{ project.recipient_name | upper }}` |
| Filter (custom) | `{{ var | filter }}` | `{{ project.report_date | date_format }}` |
| Conditional value | `{{ val if cond else other }}` | `{{ count if count > 0 else 'no' }}` |
| Pluralization | `{{ 's' if count != 1 else '' }}` | `deficienc{{ 'ies' if count != 1 else 'y' }}` |

---

## Completion Criteria

**Story 1.5.5 is complete when:**

- [x] Template copied to `app/templates/draft-audit-report-poc.docx`
- [ ] All basic merge fields converted to Jinja2 `{{ }}` syntax
- [ ] All 9 conditional logic patterns implemented
- [ ] All formatting preserved (headers, footers, tables, fonts, spacing)
- [ ] Template loads successfully in python-docxtpl (no syntax errors)
- [ ] Ready for Story 1.5.6 (POC script implementation)

---

---

## Actual Conversions Completed (Session 2025-11-19)

The following sections have detailed Jinja2 conversions ready to implement:

### ✅ Section 2: Summary of Findings
- Review type dynamic insertion
- Fiscal year dynamic
- Repeat deficiencies conditional
- Deficiency detection with alternative content
- ERF conditional section
- Assessment table with all 23 rows

### ✅ Section II.1: Review Background
- Review type conditional paragraphs (Triennial/State Management/Combined)
- Dynamic review type throughout

### ✅ Section II.2: Process
- Review type and fiscal year dynamic
- Subrecipient conditional (with 5307/5310/5311 program sections)
- Exit conference format (virtual vs in-person)
- Process dates table

### ✅ Section IV: Results of the Review (All 23 Areas)
- Complete Jinja2 code for all 23 review areas
- **Ready to copy/paste:** See `docs/section-iv-all-23-areas-jinja2.md`
- Static basic requirements
- Dynamic findings (D/ND/NA)
- Multiple deficiency code handling

### Detailed Conversion Documentation

See these files for complete implementation details:
- **`docs/story-1.5.5-conversion-summary.md`** - Complete summary of all conversions
- **`docs/section-iv-all-23-areas-jinja2.md`** - Ready-to-paste Section IV
- **`docs/draft-report-actual-field-mapping.md`** - Actual field mappings from template
- **`docs/draft-report-conversion-quickstart.md`** - Quick start workflow

---

**Last Updated:** 2025-11-19
**Status:** Conversion design complete - manual Word editing in progress
