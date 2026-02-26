# Draft Audit Report - Form Field Inventory

**Created:** 2025-11-19
**Source:** `State_RO_Recipient# _Recipient Name_FY25_TRSMR_DraftFinalReport.docx`
**Purpose:** Comprehensive catalog of all merge fields and conditional logic patterns for Epic 1.5 POC

---

## Summary Statistics

- **Total Unique Merge Fields:** ~65-75 (estimated)
- **Conditional Logic Patterns:** 9 (FR-2.1 through FR-2.9)
- **Review Areas:** 23 (for deficiency table)
- **Document Length:** 24 pages, ~5,248 words

---

## Field Inventory by Category

### 1. Project Metadata Fields

| Field Name | Type | Required | Example Value | Section | Pattern |
|------------|------|----------|---------------|---------|---------|
| `[Recipient name]` | Text | Critical | "Massachusetts Bay Transportation Authority" | Header, multiple | None |
| `[Recipient Acronym]` | Text | Critical | "MBTA" | Throughout | None |
| `[Recipient ID]` | Text | Critical | "1057" | Header | None |
| `[City, State]` | Text | Critical | "Boston, MA" | Multiple | None |
| `[Recipient website]` | URL | Optional | "https://www.mbta.com" | ? | None |
| `[review_type]` | Enum | Critical | "Triennial Review" \| "State Management Review" \| "Combined Triennial and State Management Review" | Throughout | FR-2.1 |
| `[XX-2020-000-00]` | Text | Critical | Project/Award ID | ? | None |

**Notes:**
- `review_type` is the **most critical field** - drives conditional routing throughout document (Pattern FR-2.1)
- Appears in ~10+ locations

---

### 2. Review Dates & Events

| Field Name | Type | Required | Example Value | Section | Pattern |
|------------|------|----------|---------------|---------|---------|
| `[Month]` | Text | Critical | "March" | Multiple dates | None |
| `[Day]` | Text | Critical | "15" | Multiple dates | None |
| `[Year]` | Text | Critical | "2024" | Multiple dates | None |
| `[site_visit_start_date]` | Date | Critical | "March 15, 2024" | Section 1 | None |
| `[site_visit_end_date]` | Date | Critical | "March 19, 2024" | Section 1 | None |
| `[exit_conference_date]` | Date | Critical | "March 19, 2024" | Section 1 | FR-2.5 |
| `[exit_conference_format]` | Enum | Critical | "virtual" \| "in-person" | Section 1 | FR-2.5 |
| `[report_date]` | Date | Critical | "May 15, 2024" | Cover | None |

**Notes:**
- `exit_conference_format` drives conditional paragraph selection (Pattern FR-2.5)

---

### 3. Document Status Fields

| Field Name | Type | Required | Example Value | Section | Pattern |
|------------|------|----------|---------------|---------|---------|
| `[Draft/Final]` | Text | Critical | "Draft" or "Final" | Header | None |
| `[draft/final]` | Text | Critical | "draft" or "final" (lowercase) | Multiple | None |
| `[DRAFT/FINAL]` | Text | Critical | "DRAFT" or "FINAL" (uppercase) | Multiple | None |

**Notes:**
- Three variations (capitalization) used in different contexts

---

### 4. FTA Contact Information

| Field Name | Type | Required | Example Value | Section | Pattern |
|------------|------|----------|---------------|---------|---------|
| `[FTA Title]` | Text | Critical | "Regional Administrator" | Section X | None |
| `[phone number]` | Text | Critical | "(202) 555-0123" | Multiple | None |
| `[email]` | Email | Critical | "john.smith@dot.gov" | Multiple | None |
| `[REGION #]` | Number | Critical | "1" | Header | None |
| `[Appropriate Regional Officer Titles]` | Text | Critical | ? | ? | None |
| `[Last Name]` | Text | Critical | "Smith" | Signature | None |

---

### 5. Contractor/Reviewer Information

| Field Name | Type | Required | Example Value | Section | Pattern |
|------------|------|----------|---------------|---------|---------|
| `[contractor name]` | Text | Critical | "Scott W. Schilt" | Signature | None |
| `[contractor firm]` | Text | Critical | "Milligan & Company" | Signature | None |
| `[reviewer name]` | Text | Critical | "Scott W. Schilt" | Multiple | None |

---

### 6. Assessment Data - Deficiencies

| Field Name | Type | Required | Example Value | Section | Pattern |
|------------|------|----------|---------------|---------|---------|
| `[has_deficiencies]` | Boolean | Derived | true/false | Multiple | FR-2.2, FR-2.6 |
| `[#]` (deficiency count) | Number | Derived | 3 or "no" | Multiple | FR-2.8 |
| `[no]` | Text | Derived | "no" (when count=0) | Multiple | FR-2.8 |
| `[LIST]` (deficiency areas) | String | Derived | "Legal, Financial Management, and Procurement" | Multiple | FR-2.7 |
| `[OR]` | Conditional | Marker | (not a field - marks alternative content) | Multiple | FR-2.2 |

**Notes:**
- `has_deficiencies` drives major conditional block (Pattern FR-2.2)
- `[#]` used for counts - displays number or "no" (Pattern FR-2.8)
- `[LIST]` used for comma-separated lists with "and" before last item (Pattern FR-2.7)
- `[OR]` marks alternative content blocks (show one or the other)

---

### 7. Enhanced Review Focus (ERF) Fields

| Field Name | Type | Required | Example Value | Section | Pattern |
|------------|------|----------|---------------|---------|---------|
| `[erf_count]` | Number | Derived | 2 | ERF Section | FR-2.3, FR-2.8 |
| `[LIST]` (ERF areas) | String | Derived | "Technical Capacity and Maintenance" | ERF Section | FR-2.7 |
| `[ADD AS APPLICABLE]` | Marker | Conditional | (marker for conditional section) | ERF Section | FR-2.3 |

**Notes:**
- Entire ERF section is conditional (Pattern FR-2.3)
- Only included if `erf_count > 0`

---

### 8. Subrecipient Fields

| Field Name | Type | Required | Example Value | Section | Pattern |
|------------|------|----------|---------------|---------|---------|
| `[reviewed_subrecipients]` | Boolean | Derived | true/false | Multiple | FR-2.4 |
| `[Subrecipients]` | Text | Optional | "City Transit Authority" | Subrecipient Section | None |
| `[subrecipient City/County]` | Text | Optional | "Cambridge, MA" | Subrecipient Section | None |
| `[Contractors/Lessees]` | Text | Optional | ? | ? | None |
| `[IF APPLICABLE]` | Marker | Conditional | (marker for conditional content) | Multiple | FR-2.3, FR-2.4 |

**Notes:**
- `reviewed_subrecipients` drives conditional paragraph (Pattern FR-2.4)
- Subrecipient section only appears if subrecipient was reviewed

---

### 9. Grammar Helper Placeholders

| Field Name | Type | Required | Example Value | Section | Pattern |
|------------|------|----------|---------------|---------|---------|
| `[is/are]` | Grammar | Derived | "is" or "are" | Multiple | FR-2.9 |
| `[was/were]` | Grammar | Derived | "was" or "were" | Multiple | FR-2.9 |
| `[an]` | Grammar | Derived | "a" or "an" | Multiple | FR-2.9 |
| `[Include the number (#)]` | Instruction | Marker | (instruction to include count) | ? | FR-2.8 |

**Notes:**
- Grammar helpers ensure correct pluralization
- `is/are`: depends on count (1 = "is", else "are")
- `was/were`: past tense version
- `a/an`: depends on first letter of following word (vowel = "an")

---

### 10. Deficiency Table Fields (23 Review Areas)

**Array Structure:** `assessments[]`

For each of 23 review areas:

| Field Name | Type | Required | Example Value | Pattern |
|------------|------|----------|---------------|---------|
| `review_area` | Text | Critical | "Legal" | None |
| `finding` | Enum | Critical | "D" \| "ND" \| "NA" | FR-2.6 |
| `deficiency_code` | Text | Conditional | "L-001" (only if finding="D") | FR-2.6 |
| `description` | Text | Conditional | "Inadequate procurement procedures..." | FR-2.6 |
| `corrective_action` | Text | Conditional | "Update procurement manual..." | FR-2.6 |
| `due_date` | Date | Conditional | "2024-08-31" | FR-2.6 |
| `date_closed` | Date | Conditional | null or "2024-09-15" | FR-2.6 |

**23 Review Areas:**
1. Legal
2. Financial Management
3. Procurement
4. Disadvantaged Business Enterprise (DBE)
5. Maintenance
6. Americans with Disabilities Act (ADA)
7. Equal Employment Opportunity (EEO)
8. Planning
9. Programming
10. Private Sector Participation
11. School Bus
12. Charter Bus
13. Drug and Alcohol
14. Buy America
15. Technical Capacity
16. Public Transportation Agency Safety Plan (PTASP)
17. Security
18. Rolling Stock
19. Facilities
20. Real Property
21. Project Management Oversight (PMO)
22. Construction (Rail Fixed Guideway / Bus Rapid Transit)
23. Other (State-specific requirements)

**Table Display Logic (Pattern FR-2.6):**
- Table appears ONLY if `has_deficiencies = true`
- ALL 23 rows always shown in table
- Detail columns (deficiency_code, description, corrective_action, due_date, date_closed) populated ONLY for rows where `finding = "D"`
- Rows with `finding = "ND"` or `"NA"` show finding status but have blank detail columns

---

## Conditional Logic Pattern Reference

### Pattern 1: Review Type Routing (FR-2.1)

**Occurrences:** ~10+ locations throughout document

**Logic:**
```jinja2
{% if review_type == "Triennial Review" %}
  [Triennial-specific content]
{% elif review_type == "State Management Review" %}
  [SMR-specific content]
{% elif review_type == "Combined Triennial and State Management Review" %}
  [Both Triennial AND SMR content]
{% endif %}
```

**Template Markers:**
- `[Triennial Review]/[State Management Review]/[Combined...]`
- Instructions: "For Triennial Reviews, delete the below paragraph..."
- Instructions: "For State Management Reviews, include..."

**Example Locations:**
- Section 1: Review scope description
- Section 2: Review methodology
- Multiple paragraphs explaining review focus

---

### Pattern 2: Deficiency Detection & Alternative Content (FR-2.2)

**Occurrences:** Multiple `[OR]` blocks

**Logic:**
```jinja2
{% if has_deficiencies %}
  Deficiencies were found in the following review areas: {{ deficiency_areas }}.
{% else %}
  No deficiencies were found with any of the FTA requirements reviewed.
{% endif %}
```

**Template Markers:**
- `[OR]` - marks alternative content blocks
- Instructions with two alternatives (show one or the other)

**Example:**
```
[OR: If deficiencies exist:]
Deficiencies were identified in [#] review area[s]: [LIST].

[OR: If no deficiencies:]
No deficiencies were found during this review.
```

---

### Pattern 3: Conditional Section Inclusion (FR-2.3)

**Occurrences:** ERF section, Subrecipient section

**Logic:**
```jinja2
{% if erf_count > 0 %}
## Enhanced Review Focus Areas

During the review, {{ erf_count }} Enhanced Review Focus (ERF) area{{ 's' if erf_count > 1 else '' }}
{{ 'were' if erf_count > 1 else 'was' }} identified: {{ erf_areas }}.

[ERF details...]
{% endif %}
```

**Template Markers:**
- `[ADD AS APPLICABLE]`
- `[IF APPLICABLE]`
- Entire sections that may or may not appear

**Sections:**
- ERF section (if `erf_count > 0`)
- Subrecipient section (if `reviewed_subrecipients = true`)

---

### Pattern 4: Conditional Paragraph Selection (FR-2.4)

**Occurrences:** Multiple single paragraphs that conditionally appear

**Logic:**
```jinja2
{% if reviewed_subrecipients %}
This review included an assessment of {{ subrecipient_name }}'s compliance with
applicable FTA requirements as a subrecipient of {{ recipient_name }}.
{% endif %}
```

**Template Markers:**
- `[IF APPLICABLE]`
- Instructions: "If the Triennial Review included a review of subrecipient(s), include the below paragraph"

---

### Pattern 5: Exit Conference Format Selection (FR-2.5)

**Occurrences:** 1 (exit conference paragraph)

**Logic:**
```jinja2
{% if exit_conference_format == "virtual" %}
The exit conference was conducted virtually on {{ exit_conference_date }}.
{% elif exit_conference_format == "in-person" %}
The exit conference was held in person at {{ recipient_name }}'s offices on {{ exit_conference_date }}.
{% endif %}
```

**Template Markers:**
- Two mutually exclusive paragraphs
- One for virtual, one for in-person

---

### Pattern 6: Deficiency Table Display (FR-2.6)

**Occurrences:** 1 (main deficiency table)

**Logic:**
```jinja2
{% if has_deficiencies %}

| Review Area | Finding | Deficiency Code | Description | Corrective Action | Due Date | Date Closed |
|-------------|---------|-----------------|-------------|-------------------|----------|-------------|
{% for assessment in assessments %}
| {{ assessment.review_area }} | {{ assessment.finding }} | {% if assessment.finding == 'D' %}{{ assessment.deficiency_code }}{% endif %} | {% if assessment.finding == 'D' %}{{ assessment.description }}{% endif %} | {% if assessment.finding == 'D' %}{{ assessment.corrective_action }}{% endif %} | {% if assessment.finding == 'D' %}{{ assessment.due_date }}{% endif %} | {% if assessment.finding == 'D' %}{{ assessment.date_closed }}{% endif %} |
{% endfor %}

{% else %}
No deficiencies were identified during this review.
{% endif %}
```

**Table Structure:**
- 23 rows (one per review area)
- 7 columns
- Detail columns populated ONLY for "D" findings
- ND/NA rows show only review area name and finding status

---

### Pattern 7: Dynamic List Population (FR-2.7)

**Occurrences:** Multiple `[LIST]` markers

**Logic:**
```python
# Helper function needed:
def format_list(items: List[str]) -> str:
    if len(items) == 0:
        return ""
    elif len(items) == 1:
        return items[0]
    elif len(items) == 2:
        return f"{items[0]} and {items[1]}"
    else:
        return ", ".join(items[:-1]) + f", and {items[-1]}"
```

**Template Usage:**
```jinja2
{{ deficiency_areas }}  {# "Legal, Financial Management, and Procurement" #}
{{ erf_areas }}  {# "Technical Capacity and Maintenance" #}
```

**Lists Needed:**
- `deficiency_areas`: comma-separated list of review areas with deficiencies
- `erf_areas`: comma-separated list of ERF focus areas
- Potentially others (repeat deficiencies, etc.)

---

### Pattern 8: Dynamic Counts (FR-2.8)

**Occurrences:** Multiple `[#]` and `[no]` markers

**Logic:**
```jinja2
{{ erf_count if erf_count > 0 else 'no' }} Enhanced Review Focus area{{ 's' if erf_count != 1 else '' }}
{{ deficiency_count if deficiency_count > 0 else 'no' }} deficienc{{ 'ies' if deficiency_count != 1 else 'y' }}
```

**Counts Needed:**
- `deficiency_count`: number of review areas with "D" finding
- `erf_count`: number of ERF items
- Others as discovered

**Display Rules:**
- If count > 0: Show number ("3 deficiencies")
- If count = 0: Show "no" ("no deficiencies")
- Handle pluralization

---

### Pattern 9: Grammar Helpers (FR-2.9)

**Occurrences:** Multiple `[is/are]`, `[was/were]`, `[an]` markers

**Helper Functions:**
```python
def is_are(count: int) -> str:
    return "is" if count == 1 else "are"

def was_were(count: int) -> str:
    return "was" if count == 1 else "were"

def a_an(word: str) -> str:
    return "an" if word[0].lower() in 'aeiou' else "a"
```

**Template Usage:**
```jinja2
{{ deficiency_count }} deficienc{{ 'y' if deficiency_count == 1 else 'ies' }} {{ is_are(deficiency_count) }} present
{{ erf_count }} area{{ 's' if erf_count != 1 else '' }} {{ was_were(erf_count) }} identified
{{ a_an(review_area) }} {{ review_area }} deficiency
```

---

## Derived Fields (Calculated from Source Data)

These fields are NOT in the template but must be calculated from assessment data:

| Field Name | Calculation | Example |
|------------|-------------|---------|
| `has_deficiencies` | `any(assessment.finding == "D" for assessment in assessments)` | true |
| `deficiency_count` | `sum(1 for assessment in assessments if assessment.finding == "D")` | 3 |
| `deficiency_areas` | `format_list([a.review_area for a in assessments if a.finding == "D"])` | "Legal, Financial Management, and Procurement" |
| `erf_count` | `len(erf_items)` | 2 |
| `erf_areas` | `format_list([erf.area for erf in erf_items])` | "Technical Capacity and Maintenance" |
| `reviewed_subrecipients` | `subrecipient.reviewed == true` | true |

---

## Next Steps (Story 1.5.2)

For each conditional pattern identified above:
1. Find ALL specific template locations (page, section, paragraph)
2. Extract exact template instruction text (red text, comments)
3. Create Jinja2 code snippet for conversion
4. Define test scenarios for each pattern

**Immediate Actions:**
1. ✅ Field inventory created (this document)
2. 📝 Next: Map patterns to specific template sections (Story 1.5.2)
3. 📝 Request 2-3 prior year Final Reports from FTA (Story 1.5.3)

---

**Last Updated:** 2025-11-19
**Status:** Draft - Story 1.5.1 in progress
