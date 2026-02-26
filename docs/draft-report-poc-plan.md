# Draft Audit Report - POC Plan

**Created:** 2025-11-19
**Purpose:** Validate conditional logic patterns with Draft Audit Report template using mock JSON data extracted from prior year reports

---

## Objective

Prove that python-docxtpl can handle all 9 conditional logic patterns for the Draft Audit Report template using realistic data from prior year reports.

**Success Criteria:**
- Extract 2-3 example data sets from prior year Final Reports
- Create mock JSON files representing those real reviews
- Generate Word documents that match the original formatting and conditional logic
- Validate all 9 conditional logic patterns work correctly

---

## Phase 1: Template Analysis & Form Field Extraction

### Step 1.1: Identify All Merge Fields

**Source:** `State_RO_Recipient# _Recipient Name_FY25_TRSMR_DraftFinalReport.docx`

**Method:**
1. Open Word document
2. Use Find & Replace to search for `[` characters (merge field markers)
3. Document each merge field with:
   - Field name
   - Location in document (page, section)
   - Field type (text, date, number, list)
   - Required vs optional
   - Conditional logic pattern (which of the 9 patterns)

**Output:** Create spreadsheet or markdown table

**Example Format:**
```markdown
| Field Name | Section | Type | Required | Conditional Pattern | Example Value |
|------------|---------|------|----------|---------------------|---------------|
| [recipient_name] | Header | Text | Critical | None | "Massachusetts Bay Transportation Authority" |
| [review_type] | Section 1 | Enum | Critical | FR-2.1 Review Type Routing | "Triennial Review" |
| [has_deficiencies] | Section 4 | Boolean | Derived | FR-2.2 Deficiency Detection | true |
| [deficiency_count] | Section 4 | Number | Derived | FR-2.8 Dynamic Counts | 3 |
```

---

### Step 1.2: Map Conditional Logic Patterns to Template

**For each of the 9 conditional logic patterns, document specific examples from the template:**

#### Pattern 1: Review Type Routing (FR-2.1)
**Template Instructions:**
- Find paragraphs with: `[For Triennial Reviews, delete the below paragraph...]`
- Find paragraphs with: `[For State Management Reviews, delete the below paragraph...]`

**Jinja2 Translation:**
```jinja2
{% if review_type == "Triennial Review" %}
  Paragraph A content...
{% elif review_type == "State Management Review" %}
  Paragraph B content...
{% elif review_type == "Combined Triennial and State Management Review" %}
  Paragraph A content...
  Paragraph B content...
{% endif %}
```

**Fields Required:**
- `review_type` (enum: "Triennial Review" | "State Management Review" | "Combined Triennial and State Management Review")

---

#### Pattern 2: Deficiency Detection & Alternative Content (FR-2.2)
**Template Instructions:**
- Find `[OR]` blocks with deficiency-specific content

**Jinja2 Translation:**
```jinja2
{% if has_deficiencies %}
Deficiencies were found in the following review areas: {{ deficiency_areas }}.
{% else %}
No deficiencies were found with any of the FTA requirements reviewed.
{% endif %}
```

**Fields Required:**
- `has_deficiencies` (boolean) - Derived from assessments
- `deficiency_areas` (string) - Comma-separated list

---

#### Pattern 3: Conditional Section Inclusion (FR-2.3)
**Template Instructions:**
- Find sections marked `[ADD AS APPLICABLE]`
- Examples:
  - ERF section
  - Subrecipient section

**Jinja2 Translation:**
```jinja2
{% if erf_count > 0 %}
## Enhanced Review Focus Areas

During the review, {{ erf_count }} Enhanced Review Focus (ERF) area{{ 's' if erf_count > 1 else '' }}
{{ 'were' if erf_count > 1 else 'was' }} identified: {{ erf_areas }}.

[ERF details table...]
{% endif %}
```

**Fields Required:**
- `erf_count` (number)
- `erf_areas` (string) - Comma-separated list
- `erf_items` (array of objects) - For table population

---

#### Pattern 4: Conditional Paragraph Selection (FR-2.4)
**Template Instructions:**
- `[If the Triennial Review included a review of subrecipient(s), include the below paragraph]`

**Jinja2 Translation:**
```jinja2
{% if reviewed_subrecipients %}
This review included an assessment of {{ subrecipient_name }}'s compliance with
applicable FTA requirements as a subrecipient of {{ recipient_name }}.
{% endif %}
```

**Fields Required:**
- `reviewed_subrecipients` (boolean)
- `subrecipient_name` (string) - Optional

---

#### Pattern 5: Exit Conference Format Selection (FR-2.5)
**Template Instructions:**
- Virtual vs in-person exit conference paragraph

**Jinja2 Translation:**
```jinja2
{% if exit_conference_format == "virtual" %}
The exit conference was conducted virtually on {{ exit_conference_date }}.
{% elif exit_conference_format == "in-person" %}
The exit conference was held in person at {{ recipient_name }}'s offices on {{ exit_conference_date }}.
{% endif %}
```

**Fields Required:**
- `exit_conference_format` (enum: "virtual" | "in-person")
- `exit_conference_date` (date)

---

#### Pattern 6: Deficiency Table Display (FR-2.6)
**Template Instructions:**
- Show 23-row table ONLY if deficiencies exist
- Populate detail columns ONLY for rows with Finding = D

**Jinja2 Translation:**
```jinja2
{% if has_deficiencies %}
## Review Area Findings

| Review Area | Finding | Deficiency Code | Description | Corrective Action | Due Date | Date Closed |
|-------------|---------|-----------------|-------------|-------------------|----------|-------------|
{% for assessment in assessments %}
| {{ assessment.review_area }} | {{ assessment.finding }} | {% if assessment.finding == 'D' %}{{ assessment.deficiency_code }}{% endif %} | {% if assessment.finding == 'D' %}{{ assessment.description }}{% endif %} | {% if assessment.finding == 'D' %}{{ assessment.corrective_action }}{% endif %} | {% if assessment.finding == 'D' %}{{ assessment.due_date }}{% endif %} | {% if assessment.finding == 'D' %}{{ assessment.date_closed }}{% endif %} |
{% endfor %}
{% else %}
No deficiencies were identified during this review.
{% endif %}
```

**Fields Required:**
- `has_deficiencies` (boolean) - Derived
- `assessments` (array of 23 objects):
  ```json
  {
    "review_area": "Legal",
    "finding": "D",  // or "ND" or "NA"
    "deficiency_code": "L-001",  // Only if finding == "D"
    "description": "...",
    "corrective_action": "...",
    "due_date": "2025-06-30",
    "date_closed": null
  }
  ```

---

#### Pattern 7: Dynamic List Population (FR-2.7)
**Template Instructions:**
- `[LIST]` placeholders for deficiency areas, ERF areas, etc.

**Jinja2 Translation:**
```jinja2
{{ deficiency_areas }}  {# "Legal, Financial Management, and Procurement" #}
```

**Fields Required:**
- `deficiency_areas` (string) - Pre-formatted with "and" before last item
- `erf_areas` (string) - Pre-formatted

**Helper Function Needed:**
```python
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

---

#### Pattern 8: Dynamic Counts (FR-2.8)
**Template Instructions:**
- `[#]` placeholders for counts
- `[no]` for zero counts

**Jinja2 Translation:**
```jinja2
{{ erf_count if erf_count > 0 else 'no' }} Enhanced Review Focus area{{ 's' if erf_count != 1 else '' }}
{{ deficiency_count if deficiency_count > 0 else 'no' }} deficienc{{ 'ies' if deficiency_count != 1 else 'y' }}
```

**Fields Required:**
- `erf_count` (number)
- `deficiency_count` (number)
- All other counts

---

#### Pattern 9: Grammar Helpers (FR-2.9)
**Template Instructions:**
- `[is/are]`, `[was/were]`, `[a/an]`

**Jinja2 Translation:**
```jinja2
{{ 'is' if deficiency_count == 1 else 'are' }}
{{ 'was' if erf_count == 1 else 'were' }}
{{ 'an' if review_area[0].lower() in 'aeiou' else 'a' }} {{ review_area }}
```

**Helper Functions Needed:**
```python
def is_are(count: int) -> str:
    return "is" if count == 1 else "are"

def was_were(count: int) -> str:
    return "was" if count == 1 else "were"

def a_an(word: str) -> str:
    return "an" if word[0].lower() in 'aeiou' else "a"
```

---

## Phase 2: Extract Example Data from Prior Year Reports

### Step 2.1: Identify Source Reports

**Goal:** Find 2-3 completed FY24 or FY23 Final Reports with diverse characteristics

**Ideal Examples:**
1. **Report A:** Triennial Review, NO deficiencies, NO ERF, virtual exit conference
2. **Report B:** State Management Review, 3 deficiencies, 2 ERFs, in-person exit conference
3. **Report C:** Combined Review, 1 deficiency, subrecipient reviewed, virtual exit conference

**Sources:**
- Ask FTA team for anonymized example reports
- Use completed reviews from Riskuity (if available)
- Manual extraction from PDF/Word files

---

### Step 2.2: Data Extraction Template

**For each example report, extract the following data into a structured format:**

```markdown
# Example Report: [Recipient Name] - FY[Year] [Review Type]

## Project Metadata
- Recipient Name: [e.g., "Massachusetts Bay Transportation Authority"]
- Recipient Acronym: [e.g., "MBTA"]
- Recipient ID: [e.g., "1057"]
- Region Number: [e.g., 1]
- Review Type: [Triennial Review | State Management Review | Combined]
- Site Visit Dates: [Start] to [End]
- Exit Conference Date: [Date]
- Exit Conference Format: [virtual | in-person]
- Report Date: [Date]

## Audit Team
- FTA Program Manager: [Name], [Phone], [Email]
- Contractor Lead: [Name], [Firm], [Phone], [Email]

## Review Areas (23 total)
1. Legal: [D | ND | NA]
   - Deficiency Code: [if D]
   - Description: [if D]
   - Corrective Action: [if D]
   - Due Date: [if D]
2. Financial Management: [D | ND | NA]
   ...
[Continue for all 23 review areas]

## Enhanced Review Focus (ERF)
- ERF Count: [0-N]
- ERF Areas: [if > 0, list areas]
- ERF Details: [if > 0, details for each]

## Subrecipients
- Reviewed Subrecipients: [Yes | No]
- Subrecipient Name: [if Yes]

## Derived Fields
- Has Deficiencies: [true | false]
- Deficiency Count: [0-N]
- Deficiency Areas: [comma-separated list]
```

---

### Step 2.3: Create Mock JSON Files

**Location:** `/Users/bob.emerick/dev/AI-projects/CORTAP-RPT/tests/fixtures/mock-data/`

**File Naming:** `{recipient_acronym}_FY{year}_{review_type_abbrev}.json`

**Example:**
- `MBTA_FY24_TR.json` (Triennial Review, no deficiencies)
- `DART_FY24_SMR.json` (State Management Review, 3 deficiencies)
- `SEPTA_FY24_COMBINED.json` (Combined, 1 deficiency, subrecipient)

**JSON Schema Structure:**

```json
{
  "project_id": "RSKTY-001",
  "generated_at": "2025-11-19T10:00:00Z",
  "data_version": "1.0",

  "project": {
    "recipient_name": "Massachusetts Bay Transportation Authority",
    "recipient_acronym": "MBTA",
    "recipient_id": "1057",
    "recipient_city_state": "Boston, MA",
    "recipient_website": "https://www.mbta.com",
    "region_number": 1,
    "review_type": "Triennial Review",
    "site_visit_start_date": "2024-03-15",
    "site_visit_end_date": "2024-03-19",
    "exit_conference_date": "2024-03-19",
    "exit_conference_format": "virtual",
    "report_date": "2024-05-15"
  },

  "fta_program_manager": {
    "name": "John Smith",
    "phone": "(202) 555-0123",
    "email": "john.smith@dot.gov"
  },

  "contractor": {
    "name": "Milligan & Company",
    "lead_reviewer_name": "Scott W. Schilt",
    "lead_reviewer_phone": "215-496-9100 ext 183",
    "lead_reviewer_email": "sschilt@milligancpa.com"
  },

  "assessments": [
    {
      "review_area": "Legal",
      "finding": "ND",
      "deficiency_code": null,
      "description": null,
      "corrective_action": null,
      "due_date": null,
      "date_closed": null
    },
    {
      "review_area": "Financial Management",
      "finding": "ND",
      "deficiency_code": null,
      "description": null,
      "corrective_action": null,
      "due_date": null,
      "date_closed": null
    },
    {
      "review_area": "Procurement",
      "finding": "D",
      "deficiency_code": "P-001",
      "description": "Inadequate procurement procedures for purchases over $250,000.",
      "corrective_action": "Update procurement manual to align with FTA requirements.",
      "due_date": "2024-08-31",
      "date_closed": null
    }
    // ... continue for all 23 review areas
  ],

  "erf_items": [
    {
      "area": "Technical Capacity",
      "description": "Staffing levels below recommended thresholds for maintenance operations."
    },
    {
      "area": "Maintenance",
      "description": "Deferred maintenance backlog exceeds industry standards."
    }
  ],

  "subrecipient": {
    "reviewed": false,
    "name": null
  },

  "metadata": {
    "has_deficiencies": true,
    "deficiency_count": 1,
    "deficiency_areas": "Procurement",
    "erf_count": 2,
    "erf_areas": "Technical Capacity and Maintenance"
  }
}
```

---

## Phase 3: Template Conversion to python-docxtpl

### Step 3.1: Convert Word Template Merge Fields

**Process:**
1. Open `State_RO_Recipient# _Recipient Name_FY25_TRSMR_DraftFinalReport.docx`
2. Find all `[field_name]` merge fields
3. Replace with Jinja2 syntax: `{{ field_name }}`
4. Save as `draft-audit-report.docx` in `/app/templates/`

**Example Conversions:**
- `[recipient_name]` → `{{ project.recipient_name }}`
- `[review_type]` → `{{ project.review_type }}`
- `[#]` → `{{ metadata.deficiency_count }}`

---

### Step 3.2: Add Conditional Logic

**For each of the 9 patterns identified in Phase 1, add Jinja2 conditionals:**

**Example: Pattern 2 (Deficiency Detection)**

**Original Template Text:**
```
[OR: If deficiencies found:]
Deficiencies were found in the following review areas: [LIST].

[OR: If no deficiencies:]
No deficiencies were found with any of the FTA requirements reviewed.
```

**Converted to Jinja2:**
```jinja2
{% if metadata.has_deficiencies %}
Deficiencies were found in the following review areas: {{ metadata.deficiency_areas }}.
{% else %}
No deficiencies were found with any of the FTA requirements reviewed.
{% endif %}
```

---

### Step 3.3: Add Table Logic (Pattern 6)

**Original:** 23-row deficiency table (always visible in template)

**Converted:**
```jinja2
{% if metadata.has_deficiencies %}

| Review Area | Finding | Deficiency Code | Description | Corrective Action | Due Date | Date Closed |
|-------------|---------|-----------------|-------------|-------------------|----------|-------------|
{% for assessment in assessments %}
| {{ assessment.review_area }} | {{ assessment.finding }} | {% if assessment.finding == 'D' %}{{ assessment.deficiency_code }}{% endif %} | {% if assessment.finding == 'D' %}{{ assessment.description }}{% endif %} | {% if assessment.finding == 'D' %}{{ assessment.corrective_action }}{% endif %} | {% if assessment.finding == 'D' %}{{ assessment.due_date }}{% endif %} | {% if assessment.finding == 'D' %}{{ assessment.date_closed }}{% endif %} |
{% endfor %}

{% endif %}
```

**Note:** python-docxtpl supports table rendering. May need to use Word table syntax instead of markdown.

---

## Phase 4: POC Implementation & Testing

### Step 4.1: Create POC Script

**Location:** `scripts/poc_draft_report.py`

**Purpose:** Load mock JSON, render template, generate Word document

```python
#!/usr/bin/env python3
"""
POC Script: Draft Audit Report Generation from Mock JSON

Tests all 9 conditional logic patterns with realistic data.
"""

import json
from pathlib import Path
from docxtpl import DocxTemplate
from datetime import datetime

def load_mock_data(json_file: Path) -> dict:
    """Load mock JSON data from file"""
    with open(json_file, 'r') as f:
        return json.load(f)

def format_date(date_str: str) -> str:
    """Convert ISO date to readable format"""
    dt = datetime.fromisoformat(date_str)
    return dt.strftime("%B %d, %Y")  # "March 15, 2024"

def generate_draft_report(mock_data_file: str, output_file: str):
    """Generate Draft Audit Report from mock JSON data"""

    # Load template
    template = DocxTemplate('app/templates/draft-audit-report.docx')

    # Load mock data
    data = load_mock_data(Path(mock_data_file))

    # Format dates for template
    data['project']['site_visit_dates_formatted'] = f"{format_date(data['project']['site_visit_start_date'])} to {format_date(data['project']['site_visit_end_date'])}"
    data['project']['report_date_formatted'] = format_date(data['project']['report_date'])

    # Render template
    template.render(data)

    # Save output
    template.save(output_file)
    print(f"✅ Generated: {output_file}")

if __name__ == "__main__":
    # Test with multiple mock data files
    test_cases = [
        ("tests/fixtures/mock-data/MBTA_FY24_TR.json", "output/MBTA_Draft_Report.docx"),
        ("tests/fixtures/mock-data/DART_FY24_SMR.json", "output/DART_Draft_Report.docx"),
        ("tests/fixtures/mock-data/SEPTA_FY24_COMBINED.json", "output/SEPTA_Draft_Report.docx")
    ]

    for mock_file, output_file in test_cases:
        print(f"\nGenerating from {mock_file}...")
        generate_draft_report(mock_file, output_file)

    print("\n✅ POC Complete! Review generated documents in output/ directory")
```

---

### Step 4.2: Validation Checklist

**For each generated document, validate:**

#### Formatting Preservation
- [ ] Headers and footers match original template
- [ ] Page breaks in correct locations
- [ ] Table formatting preserved
- [ ] Font styles (bold, italic, colors) correct
- [ ] Paragraph spacing matches original

#### Pattern 1: Review Type Routing
- [ ] Correct paragraphs included based on review_type
- [ ] Combined reviews show BOTH Triennial and State Management paragraphs

#### Pattern 2: Deficiency Detection
- [ ] Documents with deficiencies show deficiency content
- [ ] Documents without deficiencies show "no deficiencies" content
- [ ] [OR] blocks display correct alternative

#### Pattern 3: Conditional Section Inclusion
- [ ] ERF section appears ONLY when erf_count > 0
- [ ] Subrecipient section appears ONLY when reviewed = true
- [ ] Sections completely omitted when not applicable

#### Pattern 4: Conditional Paragraph Selection
- [ ] Subrecipient paragraph appears only if reviewed_subrecipients = true

#### Pattern 5: Exit Conference Format
- [ ] Virtual exit conference uses virtual paragraph
- [ ] In-person exit conference uses in-person paragraph

#### Pattern 6: Deficiency Table
- [ ] Table appears ONLY if has_deficiencies = true
- [ ] All 23 review areas listed
- [ ] Detail columns populated ONLY for rows with Finding = D
- [ ] ND/NA rows have blank detail columns

#### Pattern 7: Dynamic Lists
- [ ] Deficiency areas list formatted correctly (commas, "and" before last)
- [ ] ERF areas list formatted correctly

#### Pattern 8: Dynamic Counts
- [ ] Counts display numbers when > 0
- [ ] "no" displays when count = 0
- [ ] Pluralization correct (1 deficiency vs 2 deficiencies)

#### Pattern 9: Grammar Helpers
- [ ] is/are correct based on count
- [ ] was/were correct based on count
- [ ] a/an correct based on following word

---

## Phase 5: Documentation & Next Steps

### Step 5.1: Document POC Results

**Create:** `docs/poc-validation-report.md`

**Include:**
- Summary of POC approach
- Mock data sources (which prior year reports used)
- Validation results (all 9 patterns tested)
- Screenshots comparing generated vs original documents
- Issues encountered and resolutions
- Recommendations for Epic 2 implementation

---

### Step 5.2: Extract Lessons for Epic 2

**Questions to Answer:**
1. Does python-docxtpl handle all 9 patterns correctly?
2. Are there Word formatting edge cases we need to handle?
3. What helper functions are needed (format_list, is_are, etc.)?
4. How should we structure the template data model?
5. Which patterns need custom Jinja2 filters?

**Deliverable:** Update Epic 2 stories with specific technical notes from POC

---

## Next Steps

### Immediate Actions (This Week)
1. ✅ Extract form fields from Draft Audit Report template
2. ✅ Map all 9 conditional logic patterns to specific template locations
3. ✅ Identify 2-3 prior year reports for data extraction
4. ✅ Create mock JSON files with realistic data
5. ✅ Convert template to python-docxtpl format
6. ✅ Run POC script and validate output
7. ✅ Document results and lessons learned

### Follow-Up (Next Week)
1. Share POC results with stakeholders
2. Update Epic 2 stories based on POC findings
3. Begin Epic 1 implementation with validated approach
4. Use mock JSON files as test fixtures for Epic 3.5 (Data Service)

---

**Last Updated:** 2025-11-19
