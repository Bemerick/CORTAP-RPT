# CORTAP Project Data Schema v1.0

## Overview

This document describes the canonical JSON schema for FTA compliance review project data in the CORTAP-RPT system. This schema serves as the stable contract between the data service layer (Epic 3.5) and all template rendering systems (Epic 4+).

**Schema Version:** 1.0
**Status:** Active
**Created:** 2025-11-19
**JSON Schema File:** `project-data-schema-v1.0.json`
**Example Files:** `project-data-v1.0.json`, `mock-data/project-*.json`

## Schema Purpose

This schema enables:
- **Single source of truth** for project data across all templates
- **Decoupling** of data acquisition from template rendering
- **Validation** of data before template rendering
- **Caching** of normalized data in S3 for performance
- **Parallel development** using static JSON files
- **API contract** between Riskuity integration and CORTAP system

## Schema Structure

The schema is organized into 7 top-level sections:

```json
{
  "project_id": "RSKTY-1337",           // Metadata
  "generated_at": "2023-10-15T14:32:00Z",
  "data_version": "1.0",

  "project": { ... },                   // Recipient & review config
  "contractor": { ... },                // Lead reviewer details
  "fta_program_manager": { ... },       // FTA PM details
  "assessments": [ ... ],               // 23 review areas
  "erf_items": [ ... ],                 // Enhanced Review Focus
  "metadata": { ... }                   // Derived summary data
}
```

---

## Field Reference

### Top-Level Metadata

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `project_id` | string | ✓ | Riskuity project identifier (format: `RSKTY-####`) | `"RSKTY-1337"` |
| `generated_at` | string (ISO 8601) | ✓ | Timestamp when JSON was generated | `"2023-10-15T14:32:00Z"` |
| `data_version` | string | ✓ | Schema version (currently `"1.0"`) | `"1.0"` |

**Validation Rules:**
- `project_id`: Must match pattern `^RSKTY-[0-9]{4}$`
- `generated_at`: Must be valid ISO 8601 datetime with timezone
- `data_version`: Must be `"1.0"` for this schema version

---

### `project` Object

Core recipient and review configuration.

| Field | Type | Required | Description | Example | Default |
|-------|------|----------|-------------|---------|---------|
| `region_number` | integer | ✓ | FTA Region (1-10) | `1` | - |
| `review_type` | string (enum) | ✓ | Type of review | `"Triennial Review"` | - |
| `recipient_name` | string | ✓ | Full legal name | `"Greater New Haven Transit District"` | - |
| `recipient_acronym` | string | ✓ | Common acronym | `"GNHTD"` | - |
| `recipient_city_state` | string | ✓ | Location (City, ST) | `"Hamden, CT"` | - |
| `recipient_id` | string | ✓ | FTA recipient ID | `"1337"` | - |
| `recipient_website` | string, null | - | Website URL | `"www.gnhtd.org"` | `null` |
| `site_visit_dates` | string | ✓ | Human-readable date(s) | `"June 7, 2023"` or `"TBD"` | - |
| `site_visit_start_date` | string (date), null | ✓ | ISO date or null | `"2023-06-07"` or `null` | `null` |
| `site_visit_end_date` | string (date), null | ✓ | ISO date or null | `"2023-06-07"` or `null` | `null` |
| `report_date` | string (date) | ✓ | Report due/published | `"2023-11-30"` | - |
| `exit_conference_format` | string (enum) | ✓ | Conference format | `"virtual"` or `"in-person"` | - |

**Validation Rules:**
- `region_number`: Integer between 1 and 10 inclusive
- `review_type`: One of:
  - `"Triennial Review"`
  - `"State Management Review"`
  - `"Combined Triennial and State Management Review"`
  - `"Special Review"`
  - `"Limited Scope Review"`
- `recipient_city_state`: Must match pattern `^.+, [A-Z]{2}$` (City, STATE)
- `site_visit_start_date`, `site_visit_end_date`: ISO 8601 date format `YYYY-MM-DD` or `null`
- `exit_conference_format`: Either `"virtual"` or `"in-person"`

**Field Mapping to RIR Template:**
| Template Field | JSON Path |
|----------------|-----------|
| `[#]` (Region) | `project.region_number` |
| `[Triennial Review]` | `project.review_type` |
| `[Recipient Name]` | `project.recipient_name` |
| `[Recipient Location]` | `project.recipient_city_state` |
| `[#]` (Recipient ID) | `project.recipient_id` |
| `[URL]` | `project.recipient_website` |
| Site Visit Dates | `project.site_visit_dates` |

---

### `contractor` Object

Lead contractor and reviewer information.

| Field | Type | Required | Description | Example | Default |
|-------|------|----------|-------------|---------|---------|
| `lead_reviewer_name` | string | ✓ | Lead reviewer name | `"Bobby Killebrew"` | - |
| `contractor_name` | string | ✓ | Contracting firm | `"Qi Tech, LLC"` | - |
| `lead_reviewer_phone` | string, null | - | Phone number | `"512-350-9912"` | `null` |
| `lead_reviewer_email` | string, null | - | Email address | `"bobby_killebrew@qitechllc.com"` | `null` |

**Validation Rules:**
- `lead_reviewer_email`: Must be valid email format if not null

**Field Mapping to RIR Template:**
| Template Field | JSON Path |
|----------------|-----------|
| `[Lead Reviewer Name]` | `contractor.lead_reviewer_name` |
| `[Contractor Name]` | `contractor.contractor_name` |
| `[Lead Reviewer Phone #]` | `contractor.lead_reviewer_phone` |
| `[Lead Reviewer Email Address]` | `contractor.lead_reviewer_email` |

---

### `fta_program_manager` Object

FTA Program Manager assigned to the recipient.

| Field | Type | Required | Description | Example | Default |
|-------|------|----------|-------------|---------|---------|
| `fta_program_manager_name` | string | ✓ | PM name | `"Syed T. Ahmed"` | - |
| `fta_program_manager_title` | string, null | - | Job title | `"General Engineer"` | `null` |
| `fta_program_manager_phone` | string, null | - | Phone number | `"617-494-3254"` | `null` |
| `fta_program_manager_email` | string, null | - | Email address | `"syed.ahmed@dot.gov"` | `null` |

**Validation Rules:**
- `fta_program_manager_email`: Must be valid email format if not null

**Field Mapping to RIR Template:**
| Template Field | JSON Path |
|----------------|-----------|
| `[FTA PM for Recipient]` | `fta_program_manager.fta_program_manager_name` |
| `[FTA PM Phone #]` | `fta_program_manager.fta_program_manager_phone` |
| `[FTA PM Email Address]` | `fta_program_manager.fta_program_manager_email` |

---

### `assessments` Array

Array of exactly **23** FTA review areas with findings.

**Array Requirements:**
- Minimum items: 23
- Maximum items: 23
- Order: Not specified (templates should handle any order)

**Assessment Object Structure:**

| Field | Type | Required | Description | Example | Default |
|-------|------|----------|-------------|---------|---------|
| `review_area` | string (enum) | ✓ | Review area name | `"Legal"` | - |
| `finding` | string (enum) | ✓ | Finding code | `"D"`, `"ND"`, or `"NA"` | - |
| `deficiency_code` | string, null | - | Deficiency ID | `"D-2023-001"` or `null` | `null` |
| `description` | string, null | - | Deficiency description | `"..."` or `null` | `null` |
| `corrective_action` | string, null | - | Required action | `"..."` or `null` | `null` |
| `due_date` | string (date), null | - | Action due date | `"2024-03-31"` or `null` | `null` |
| `date_closed` | string (date), null | - | Closed date | `"2024-05-15"` or `null` | `null` |

**`review_area` Enumeration (23 values):**

1. `"Legal"`
2. `"Financial Management and Capacity"`
3. `"Technical Capacity - Award Management"`
4. `"Technical Capacity - Program Management and Subrecipient Oversight"`
5. `"Technical Capacity - Project Management"`
6. `"Transit Asset Management"`
7. `"Satisfactory Continuing Control"`
8. `"Maintenance"`
9. `"Procurement"`
10. `"Disadvantaged Business Enterprise"`
11. `"Title VI"`
12. `"Americans with Disabilities Act (ADA) - General"`
13. `"Americans with Disabilities Act (ADA) - Complementary Paratransit"`
14. `"Equal Employment Opportunity"`
15. `"School Bus"`
16. `"Charter Bus"`
17. `"Drug-Free Workplace Act"`
18. `"Drug and Alcohol Program"`
19. `"Section 5307 Program Requirements"`
20. `"Section 5310 Program Requirements"`
21. `"Section 5311 Program Requirements"`
22. `"Public Transportation Agency Safety Plan (PTASP)"`
23. `"Cybersecurity"`

**`finding` Enumeration:**
- `"D"` - Deficiency found
- `"ND"` - No Deficiency
- `"NA"` - Not Applicable

**Validation Rules:**
- `finding`: Must be one of `"D"`, `"ND"`, `"NA"`
- `deficiency_code`: Must match pattern `^D-[0-9]{4}-[0-9]{3}$` if finding is `"D"`, otherwise must be `null`
- `description`, `corrective_action`, `due_date`: Should be populated if finding is `"D"`, `null` otherwise
- `date_closed`: ISO 8601 date format `YYYY-MM-DD` or `null`

**Business Logic:**
- If `finding == "D"`, then `deficiency_code`, `description`, `corrective_action`, and `due_date` should be populated
- If `finding == "ND"` or `finding == "NA"`, then all deficiency fields should be `null`

---

### `erf_items` Array

Enhanced Review Focus items (optional, may be empty).

**Array Requirements:**
- Minimum items: 0
- Maximum items: Not specified

**ERF Item Object Structure:**

| Field | Type | Required | Description | Example | Default |
|-------|------|----------|-------------|---------|---------|
| `erf_area` | string | ✓ | Focus area | `"Financial Oversight"` | - |
| `focus_description` | string | ✓ | What the focus entails | `"Enhanced review of grant financial reporting"` | - |
| `completion_status` | string (enum) | ✓ | Status | `"In Progress"` or `"Completed"` | - |

**Validation Rules:**
- `completion_status`: Must be either `"In Progress"` or `"Completed"`

---

### `metadata` Object

Derived summary and metadata fields.

| Field | Type | Required | Description | Example | Default |
|-------|------|----------|-------------|---------|---------|
| `has_deficiencies` | boolean | ✓ | Any deficiencies? | `true` or `false` | - |
| `deficiency_count` | integer | ✓ | Total deficiencies | `0`, `1`, `2`, ... | - |
| `deficiency_areas` | array of strings | ✓ | Areas with deficiencies | `["Legal", "TAM"]` or `[]` | - |
| `erf_count` | integer | ✓ | Number of ERF items | `0`, `1`, ... | - |
| `reviewed_subrecipients` | boolean | ✓ | Subrecipient review? | `true` or `false` | - |
| `subrecipient_name` | string, null | ✓ | Subrecipient name | `"Metro Transit"` or `null` | `null` |
| `fiscal_year` | string | ✓ | Fiscal year | `"FY2023"` | - |
| `review_status` | string (enum) | ✓ | Review status | `"Completed"`, `"In Progress"`, `"Draft"` | - |

**Validation Rules:**
- `deficiency_count`: Must be non-negative integer
- `erf_count`: Must be non-negative integer
- `fiscal_year`: Must match pattern `^FY[0-9]{4}$`
- `review_status`: One of `"In Progress"`, `"Completed"`, `"Draft"`

**Derivation Logic:**
- `has_deficiencies`: `true` if any assessment has `finding == "D"`
- `deficiency_count`: Count of assessments with `finding == "D"`
- `deficiency_areas`: List of `review_area` values where `finding == "D"`
- `erf_count`: Length of `erf_items` array

---

## Schema Versioning Strategy

### Current Version: 1.0

**Version Field:** All JSON documents must include `"data_version": "1.0"`

### Versioning Policy

- **Major version** (e.g., 1.0 → 2.0): Breaking changes
  - Removing required fields
  - Changing field types incompatibly
  - Changing enum values
  - Renaming fields

- **Minor version** (e.g., 1.0 → 1.1): Non-breaking changes
  - Adding optional fields
  - Adding new enum values
  - Relaxing validation rules
  - Documentation updates

### Migration Path for Future Versions

When schema changes are needed:

1. **Create new schema file:** `project-data-schema-v{X.Y}.json`
2. **Update transformer:** `services/data_transformer.py` to output new version
3. **Implement migration:** Create `migrations/v{old}_to_v{new}.py` for cached data
4. **Update validators:** Support both old and new versions during transition period
5. **Template compatibility:** Templates must specify minimum schema version required
6. **Deprecation notice:** Mark old version as deprecated for 3 months before removal

### Backward Compatibility

- **Reading:** Data service should be able to read older schema versions
- **Writing:** Data service always writes the latest schema version
- **Validation:** Validator should support multiple schema versions
- **Templates:** Templates should specify minimum required schema version in metadata

### Version Detection

Templates and validators should check the `data_version` field:

```python
data_version = json_data.get("data_version", "1.0")  # Default to 1.0 if missing
if data_version != "1.0":
    raise UnsupportedSchemaVersionError(f"Template requires schema v1.0, got v{data_version}")
```

---

## Usage Examples

### Validating JSON Against Schema

Using `jsonschema` library:

```python
import json
import jsonschema

# Load schema
with open("docs/schemas/project-data-schema-v1.0.json") as f:
    schema = json.load(f)

# Load data
with open("data.json") as f:
    data = json.load(f)

# Validate
try:
    jsonschema.validate(instance=data, schema=schema)
    print("✓ Valid")
except jsonschema.ValidationError as e:
    print(f"✗ Invalid: {e.message}")
```

### Accessing Data in Templates

In Jinja2 templates (python-docxtpl):

```jinja2
Region {{ project.region_number }}
{{ project.review_type }}

Recipient: {{ project.recipient_name }} ({{ project.recipient_acronym }})
Location: {{ project.recipient_city_state }}

{% if metadata.has_deficiencies %}
  DEFICIENCIES FOUND: {{ metadata.deficiency_count }}
  {% for area in metadata.deficiency_areas %}
    - {{ area }}
  {% endfor %}
{% else %}
  No deficiencies identified.
{% endif %}
```

### Querying Deficiencies

```python
# Get all deficiencies
deficiencies = [
    a for a in data["assessments"]
    if a["finding"] == "D"
]

# Get count
count = len(deficiencies)
assert count == data["metadata"]["deficiency_count"]

# Get areas
areas = [d["review_area"] for d in deficiencies]
assert areas == data["metadata"]["deficiency_areas"]
```

---

## Field Mappings

### RIR Template → JSON

See table in `project` section above.

### Riskuity API → JSON

Detailed mapping available in: `docs/riskuity-integration-requirements.md`

Key mappings:
- Riskuity `project.project_id` → `project_id`
- Riskuity `project.region` → `project.region_number`
- Riskuity `assessments[]` → `assessments[]`
- Derived fields calculated from assessments → `metadata`

---

## Related Files

- **JSON Schema:** `project-data-schema-v1.0.json` - Machine-readable validation schema
- **Example:** `project-data-v1.0.json` - Complete example with all fields
- **Mock Data:** `mock-data/project-*.json` - Real extracted data for testing
- **Mock Data README:** `mock-data/README.md` - Documentation of mock data files
- **Requirements:** `../recipient-information-request-requirements.md` - RIR template analysis
- **Requirements:** `../riskuity-integration-requirements.md` - Riskuity field mapping
- **Architecture:** `../architecture.md` - Data service architecture

---

## Changelog

### v1.0 (2025-11-19)
- Initial schema design
- Support for RIR template (15 fields)
- Support for Draft Report template requirements
- 23 standard FTA review areas
- Enhanced Review Focus (ERF) support
- Metadata section with derived fields

---

## Questions & Support

For questions about this schema, refer to:
- **Epic 3.5:** Data Service implementation (docs/epics.md)
- **Story 3.5.1:** Schema design (this document)
- **Architecture:** Data service pattern (docs/architecture.md)
