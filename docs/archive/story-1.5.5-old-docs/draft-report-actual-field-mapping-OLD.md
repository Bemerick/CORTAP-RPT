# Draft Report Template - Actual Field Mapping

**Based on:** Actual merge fields extracted from template
**Created:** 2025-11-19

This document maps the **actual fields found in the template** to the JSON data structure.

---

## Direct Merge Field Replacements

These fields exist in the template and can be directly replaced:

| Template Field | Replace With | JSON Path |
|---------------|--------------|-----------|
| `[Recipient name]` | `{{ project.recipient_name }}` | project.recipient_name |
| `[Recipient Acronym]` | `{{ project.recipient_acronym }}` | project.recipient_acronym |
| `[Recipient full name (Recipient Acronym if applicable)]` | `{{ project.recipient_name }} ({{ project.recipient_acronym }})` | Combined |
| `[City, State]` | `{{ project.recipient_city_state }}` | project.recipient_city_state |
| `[Recipient City and State]` | `{{ project.recipient_city_state }}` | project.recipient_city_state |
| `[REGION #]` | `{{ project.region_number }}` | project.region_number |
| `[FTA Program Manager Name]` | `{{ fta_program_manager.name }}` | fta_program_manager.name |
| `[FTA Title]` | `{{ fta_program_manager.title }}` | fta_program_manager.title |
| `[phone number]` | `{{ fta_program_manager.phone }}` | fta_program_manager.phone |
| `[email]` | `{{ fta_program_manager.email }}` | fta_program_manager.email |
| `[Last Name]` | `{{ fta_program_manager.name.split()[-1] }}` | Derived from name |
| `[reviewer name]` | `{{ contractor.lead_reviewer_name }}` | contractor.lead_reviewer_name |
| `[#]` | `{{ metadata.deficiency_count }}` | metadata.deficiency_count |
| `[no]` | `{{ 'no' if metadata.deficiency_count == 0 else metadata.deficiency_count }}` | Conditional |
| `[LIST]` | `{{ metadata.deficiency_areas }}` | metadata.deficiency_areas |
| `[XX-2020-000-00]` | `{{ project_id }}` or `{{ project.recipient_id }}` | project_id |

---

## Instructional Fields (Marked with [contractor firm] etc.)

These appear in the "instructional text" list but should be actual merge fields:

| Template Field | Replace With | JSON Path | Note |
|---------------|--------------|-----------|------|
| `[contractor firm]` | `{{ contractor.name }}` | contractor.name | Appears in instructions but should be field |
| `[contractor name]` | `{{ contractor.lead_reviewer_name }}` | contractor.lead_reviewer_name | Same as reviewer name |

---

## Enum/Choice Fields (Replace Multiple Options with Conditional)

### Review Type Field

**Template has THREE separate placeholders:**
- `[Triennial Review]`
- `[State Management Review]`
- `[Combined Triennial and State Management Review]`

**Also this variant:**
- `[Triennial Review/State Management Review/Combined Triennial and State Management Review]`

**Replace ALL of these with:**
```jinja2
{{ project.review_type }}
```

This will output: "Triennial Review" or "State Management Review" or "Combined Triennial and State Management Review"

---

## Date Fields

The template uses `[Month]`, `[Day]`, `[Year]` as separate fields.

### Option 1: Use report_date for all
```jinja2
[Month] → {{ project.report_date | date_format }}
[Day] → {{ project.report_date | date_format }}
[Year] → {{ project.fiscal_year }}
```

**Problem:** This assumes Month and Day always refer to report date, which may not be true.

### Option 2: Context-dependent (recommended)

Look at where each date field appears and map to the appropriate JSON field:

**For site visit dates:**
```jinja2
{{ project.site_visit_start_date | date_format }} to {{ project.site_visit_end_date | date_format }}
```

**For exit conference date:**
```jinja2
{{ project.exit_conference_date | date_format }}
```

**For report date (title page, header):**
```jinja2
{{ project.report_date | date_format }}
```

---

## Document Status Fields

| Template Field | Replace With | Note |
|---------------|--------------|------|
| `[Draft/Final]` | `Draft` | Hardcode to "Draft" for POC |
| `[draft/final]` | `draft` | Hardcode to "draft" for POC |
| `[DRAFT/FINAL]` | `DRAFT` | Hardcode to "DRAFT" for POC |

**Note:** In production (Epic 2+), these would be parameters, but for POC use hardcoded "Draft" values.

---

## Grammar Helper Fields

| Template Field | Replace With | Note |
|---------------|--------------|------|
| `[is/are]` | `{{ 'is' if metadata.deficiency_count == 1 else 'are' }}` | Subject-verb agreement |
| `[is/is not]` | `{{ 'is' if metadata.has_deficiencies else 'is not' }}` | Conditional verb |
| `[an]` | Context-dependent | Usually for article before count |

**Example usage:**
```
{{ metadata.deficiency_count }} deficienc{{ 'y' if metadata.deficiency_count == 1 else 'ies' }}
{{ 'was' if metadata.deficiency_count == 1 else 'were' }} identified
```

---

## Subrecipient Fields

| Template Field | Replace With | JSON Path |
|---------------|--------------|-----------|
| `[subrecipient name]` | `{{ subrecipient.name }}` | subrecipient.name |
| `[subrecipient City/County]` | *Not in JSON* | May need to add or derive |
| `[Subrecipients]` | *Conditional section* | Only show if subrecipient.reviewed == true |

**Conditional paragraph for subrecipient:**
```jinja2
{% if subrecipient.reviewed %}
This review included an assessment of {{ subrecipient.name }}'s compliance with
applicable FTA requirements as a subrecipient of {{ project.recipient_name }}.
{% endif %}
```

---

## Instructional Text → Conditional Logic

### 1. Review Type Instructions

**Template text:**
```
[For Triennial Reviews, delete the below paragraph; for State Management Reviews,
delete the above paragraph; for Combined Reviews, include both paragraphs]
```

**Convert to:**
```jinja2
{%p if project.review_type == "Triennial Review" %}
[Triennial-specific content]
{%p endif %}

{%p if project.review_type == "State Management Review" %}
[State Management-specific content]
{%p endif %}

{%p if project.review_type == "Combined Triennial and State Management Review" %}
[Triennial-specific content]

[State Management-specific content]
{%p endif %}
```

**Note:** Use `{%p ... %}` for paragraph-level conditionals to preserve formatting.

### 2. Exit Conference Format

**Template text:**
```
[If exit conference is conducted virtually, include the below paragraph]
[If exit conference is conducted in-person, include the below paragraph]
```

**Convert to:**
```jinja2
{%p if project.exit_conference_format == "virtual" %}
The exit conference was conducted virtually on {{ project.exit_conference_date | date_format }}.
{%p elif project.exit_conference_format == "in-person" %}
The exit conference was held in person at {{ project.recipient_name }}'s offices on
{{ project.exit_conference_date | date_format }}.
{%p endif %}
```

### 3. Subrecipient Review

**Template text:**
```
[If the Triennial Review, State Management Review or Combined Triennial and State
Management Review included a review of Section 5307, Section 5310, or Section 5311
subrecipient(s) or contractor(s), include the below paragraph]
```

**Convert to:**
```jinja2
{%p if subrecipient.reviewed %}
This review included an assessment of {{ subrecipient.name }}'s compliance with
applicable FTA requirements as a subrecipient of {{ project.recipient_name }}.
{%p endif %}
```

### 4. Deficiency Content (OR blocks)

**Template text:**
```
[OR] - marks alternative content
```

**Convert to:**
```jinja2
{%p if metadata.has_deficiencies %}
Deficiencies were found in the following review areas: {{ metadata.deficiency_areas }}.
{%p else %}
No deficiencies were found with any of the FTA requirements reviewed.
{%p endif %}
```

### 5. Add As Applicable Sections

**Template text:**
```
[ADD AS APPLICABLE]
```

**Examples:**
- ERF section: `{% if metadata.erf_count > 0 %}...{% endif %}`
- Repeat deficiencies: `{% if metadata.repeat_deficiency_count > 0 %}...{% endif %}`

---

## Fields NOT in Template (Need to Add)

These JSON fields don't have template placeholders. Decide if/where to add them:

| JSON Field | Suggested Use | Where to Add |
|-----------|---------------|--------------|
| `project.recipient_id` | May want in header or filename | Header area? |
| `project.fiscal_year` | Year of review | Title, various date contexts |
| `project.scoping_meeting_date` | Meeting date | Section 3: Review Process |
| `project.recipient_website` | Optional URL | Section 1: Background? |
| Various assessment details | Deficiency table | Create/enhance deficiency table |

**Decision:** Review the original template to see if these are implied or if you need to add them based on your requirements.

---

## Special Cases

### 1. Deficiency Table

**Not in extracted fields list** because it's likely a formatted table without bracket fields.

**What to do:** Find the deficiency/assessment table and convert to:

```jinja2
{%r for assessment in assessments %}
{%r if assessment.finding == "D" %}
{{ assessment.review_area }}	{{ assessment.deficiency_code }}	{{ assessment.description }}	{{ assessment.corrective_action }}	{{ assessment.due_date | date_format if assessment.due_date else '' }}	{{ 'Closed ' + (assessment.date_closed | date_format) if assessment.date_closed else 'Open' }}
{%r endif %}
{%r endfor %}
```

### 2. Fields in Header/Footer

Check header and footer for fields like:
- `[REGION #]`
- `[Recipient name]`
- `[Draft/Final]`

These should be in headers/footers - convert them there.

---

## Conversion Workflow

1. **Start with direct replacements** (30 fields listed above)
   - Use Find & Replace in Word
   - Test frequently with validation script

2. **Convert enum/choice fields** (review type)
   - Find all instances of `[Triennial Review]`, etc.
   - Replace with `{{ project.review_type }}`

3. **Remove and convert instructional text**
   - Delete `[For Triennial Reviews, delete...]` instructions
   - Wrap content in `{%p if %}` conditionals

4. **Add missing fields** if needed
   - recipient_id, fiscal_year, dates
   - Based on your requirements

5. **Verify with validation script**
   ```bash
   python scripts/validate_draft_template.py --render
   ```

---

## Quick Reference: Most Common Conversions

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
[Draft/Final]                 → Draft
```

**For instructions:**
```
[For Triennial Reviews, delete...] → {%p if project.review_type == "Triennial Review" %}
[If exit conference is virtual...] → {%p if project.exit_conference_format == "virtual" %}
[OR]                               → {%p if %}...{%p else %}...{%p endif %}
```

---

**Last Updated:** 2025-11-19
