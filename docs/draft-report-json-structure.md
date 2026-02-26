# Draft Report POC - JSON Data Structure

**Purpose:** Define the JSON structure required for Draft Audit Report template rendering
**Story:** 1.5.5 - Convert Draft Report Template to python-docxtpl Format
**Updated:** 2025-11-19

---

## Complete JSON Schema

```json
{
  "project_id": "NTD-FY2023-TR-1339",
  "generated_at": "2025-11-19T16:00:00Z",
  "data_version": "1.0",

  "project": {
    "recipient_name": "Norwalk Transit District",
    "recipient_acronym": "NTD",
    "recipient_id": "1339",
    "recipient_city_state": "Norwalk, Connecticut",
    "recipient_website": null,
    "region_number": 1,
    "review_type": "Triennial Review",  // or "State Management Review" or "Combined Triennial and State Management Review"
    "fiscal_year": 2023,
    "scoping_meeting_date": "2023-02-24",
    "site_visit_start_date": "2023-03-28",
    "site_visit_end_date": "2023-05-15",
    "exit_conference_date": "2023-05-15",
    "exit_conference_format": "virtual",  // or "in-person"
    "report_date": "2023-07-11"
  },

  "fta_program_manager": {
    "name": "Michelle Muhlanger",
    "title": "Deputy Regional Administrator",
    "phone": "617-494-2630",
    "email": "michelle.muhlanger@dot.gov",
    "region": "Region 1"
  },

  "contractor": {
    "name": "Qi Tech, LLC",
    "lead_reviewer_name": "Gwen Larson",
    "lead_reviewer_phone": "920-746-4595",
    "lead_reviewer_email": "gwen_larson@qitechllc.com"
  },

  "assessments": [
    {
      "review_area": "Legal",  // Must match exact names (23 total areas)
      "finding": "ND",  // "D", "ND", or "NA"
      "deficiency_code": null,  // e.g., "DBE5-1, DBE8-1" (comma-separated for multiple)
      "description": null,  // Full deficiency description
      "corrective_action": null,  // Required corrective actions
      "due_date": null,  // "YYYY-MM-DD" format
      "date_closed": null  // "YYYY-MM-DD" format or null if open
    }
    // ... 22 more assessment objects (one per review area)
  ],

  "erf_items": [],  // Enhanced Review Focus items (optional)

  "subrecipient": {
    "reviewed": false,  // Boolean - was subrecipient reviewed?
    "name": null,  // Subrecipient organization name
    "city_state": null,  // "Portland, Maine"
    "program_section": null  // "5307", "5310", "5311", or null
  },

  "metadata": {
    // Core deficiency tracking
    "has_deficiencies": true,  // Boolean - any "D" findings?
    "deficiency_count": 1,  // Count of "D" findings
    "deficiency_areas": "Disadvantaged Business Enterprise",  // Comma-separated list with "and" before last

    // ERF tracking
    "erf_count": 0,  // Count of Enhanced Review Focus items
    "erf_areas": "",  // Comma-separated ERF areas

    // Context flags
    "covid19_context": true,  // Boolean - review conducted during COVID

    // Repeat deficiencies
    "no_repeat_deficiencies": true,  // Boolean - no repeats from prior review
    "repeat_deficiency_count": 0,  // Count of repeat deficiencies (optional)
    "repeat_deficiency_areas": "",  // Comma-separated repeat areas (optional)

    // Deficiency status (optional but useful)
    "deficiencies_open_count": 1,  // Count of open deficiencies
    "deficiencies_closed_count": 0,  // Count of closed deficiencies

    // Other context flags (optional)
    "first_time_operating_assistance": true  // First time receiving operating funds
  }
}
```

---

## Field Requirements by Section

### Section 2: Summary of Findings

**Required:**
- `project.fiscal_year`
- `project.review_type`
- `project.recipient_acronym`
- `metadata.has_deficiencies`
- `metadata.deficiency_areas`
- `metadata.no_repeat_deficiencies`
- `metadata.erf_count`
- `metadata.erf_areas`
- `assessments[]` (all 23 areas)

**Optional:**
- `metadata.repeat_deficiency_count`
- `metadata.repeat_deficiency_areas`

### Section II.1: Review Background

**Required:**
- `project.review_type`

### Section II.2: Process

**Required:**
- `project.review_type`
- `project.fiscal_year`
- `project.recipient_name`
- `project.recipient_acronym`
- `project.scoping_meeting_date`
- `project.site_visit_start_date`
- `project.exit_conference_date`
- `project.exit_conference_format`
- `project.report_date`
- `subrecipient.reviewed`
- `subrecipient.name`
- `subrecipient.city_state`
- `subrecipient.program_section`

**Optional (for process dates table):**
- `project.rir_transmittal_date`
- `project.rir_response_date`
- `project.agenda_package_date`
- `project.draft_report_date`

### Section IV: Results of the Review

**Required:**
- `project.review_type`
- `project.recipient_acronym`
- `assessments[]` (all 23 areas with):
  - `review_area` (exact name match)
  - `finding` ("D", "ND", or "NA")
  - `deficiency_code` (if finding = "D")
  - `description` (if finding = "D")
  - `corrective_action` (if finding = "D")
  - `due_date` (if finding = "D")
  - `date_closed` (if finding = "D" and closed)

---

## Assessment Review Areas (All 23 - Exact Names)

Must match these names exactly in JSON:

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
11. Title VI
12. Americans with Disabilities Act (ADA) – General
13. ADA – Complementary Paratransit
14. Equal Employment Opportunity
15. School Bus
16. Charter Bus
17. Drug Free Workplace Act
18. Drug and Alcohol Program
19. Section 5307 Program Requirements
20. Section 5310 Program Requirements
21. Section 5311 Program Requirements
22. Public Transportation Agency Safety Plan (PTASP)
23. Cybersecurity

**Note:** Pay attention to:
- En dashes (–) vs hyphens (-)
- Ampersands (&) vs "and"
- Parentheses and acronyms
- Exact capitalization

---

## Changes Made During Story 1.5.5

### Subrecipient Structure Enhanced

**Before:**
```json
{
  "subrecipient": {
    "reviewed": true,
    "name": "Regional Transportation Program, Inc. (RTP)",
    "service": "ADA complementary paratransit (contracted)"
  }
}
```

**After:**
```json
{
  "subrecipient": {
    "reviewed": true,
    "name": "Regional Transportation Program, Inc. (RTP)",
    "city_state": "Portland, Maine",           // ✅ ADDED
    "program_section": "5307",                 // ✅ ADDED
    "service": "ADA complementary paratransit (contracted)"
  }
}
```

**Rationale:** Allows template to generate specific language for Section 5307, 5310, or 5311 subrecipients.

---

## Optional Future Enhancements

These fields are **not required for POC** but could be added in Epic 2:

### 1. Additional Process Dates

```json
{
  "project": {
    "rir_transmittal_date": "2023-12-02",
    "rir_response_date": "2023-02-15",
    "agenda_package_date": "2023-03-06",
    "draft_report_date": "2023-07-28"
  }
}
```

**Use:** Process dates table in Section II.2

### 2. Separate Deficiency Objects

For cases where one review area has multiple distinct deficiencies:

```json
{
  "review_area": "Disadvantaged Business Enterprise (DBE)",
  "finding": "D",
  "deficiencies": [
    {
      "code": "DBE5-1",
      "description": "Uniform reports contain inaccuracies...",
      "corrective_action": "Submit corrected reports by Nov 30, 2023",
      "due_date": "2023-11-30",
      "date_closed": null,
      "repeat": true,
      "repeat_from_year": 2019
    },
    {
      "code": "DBE8-1",
      "description": "Inadequate implementation of race-neutral measures...",
      "corrective_action": "Submit implementation plan by Nov 30, 2023",
      "due_date": "2023-11-30",
      "date_closed": null
    }
  ]
}
```

**Use:** More detailed deficiency tracking, separate corrective actions per deficiency

### 3. Basic Requirements per Assessment

```json
{
  "review_area": "Legal",
  "basic_requirement": "The recipient must promptly notify the FTA of legal matters...",
  "finding": "ND",
  ...
}
```

**Use:** Dynamic basic requirements (currently static in template)

---

## Current Mock Data Status

### All 5 JSON Files Updated ✅

1. **NTD_FY2023_TR.json** - No subrecipient, 1 deficiency
2. **GPTD_FY2023_TR.json** - Has subrecipient (5307, Portland, Maine), 3 deficiencies
3. **MEVA_FY2023_TR.json** - No subrecipient, 8 deficiencies, has repeat deficiency tracking
4. **Nashua_FY2023_TR.json** - No subrecipient, 1 deficiency
5. **DRPA_FY2023_TR.json** - No subrecipient, 4 deficiencies (all closed)

**All files validated:** ✅ Valid JSON syntax

---

## Derived Fields (Metadata)

These fields are **calculated from assessments data**, not manually entered:

```python
# Pseudo-code for deriving metadata
has_deficiencies = any(a.finding == "D" for a in assessments)
deficiency_count = sum(1 for a in assessments if a.finding == "D")

# Deficiency areas with grammar
deficiency_areas = grammar_list([a.review_area for a in assessments if a.finding == "D"])
# Examples:
# 1 area: "Legal"
# 2 areas: "Legal and Procurement"
# 3+ areas: "Legal, Procurement, and Title VI"

no_repeat_deficiencies = not any(
    a.finding == "D" and "repeat" in a.description.lower()
    for a in assessments
)
```

**For POC:** These are pre-calculated and included in JSON. In production (Epic 3.5), these would be calculated by the data service.

---

## Validation

**Schema validation script:** `scripts/validate_draft_template.py`

```bash
# Validate JSON structure
python scripts/validate_draft_template.py --render --data tests/fixtures/mock-data/NTD_FY2023_TR.json
```

**Common validation errors:**
- Missing required fields → UndefinedError
- Wrong assessment area names → Data won't match
- Wrong date format → Filter error

---

**Last Updated:** 2025-11-19
**Status:** Current for Story 1.5.5 POC
