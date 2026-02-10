# Riskuity Integration Configuration - TODO

**Status:** Epic 3.5 Data Service implementation complete, but requires configuration for project metadata fields not available in Riskuity assessments API.

**Last Updated:** 2026-02-10

---

## Missing Project Metadata Fields

The following fields are required for CORTAP report generation but are **NOT available** in the Riskuity assessments API responses:

### Critical Fields (Report Generation Blockers)

| Field | Required For | Current Status | Proposed Solution |
|-------|-------------|----------------|-------------------|
| `region_number` | RIR Cover Page, Draft Report | ❌ Not in API | Pass from Riskuity button click OR configure per tenant |
| `review_type` | RIR Template Selection, Draft Report | ❌ Not in API | Pass from Riskuity button click OR infer from project |
| `recipient_city_state` | RIR Cover Page | ❌ Not in API | Configure per tenant/recipient |
| `recipient_acronym` | Cover Letter, Draft Report | ❌ Not in API | Configure per tenant/recipient |
| `recipient_website` | RIR Package | ❌ Not in API | Configure per tenant/recipient (optional) |

### Personnel Fields (Required for Reports)

| Field | Required For | Current Status | Proposed Solution |
|-------|-------------|----------------|-------------------|
| `contractor_name` | RIR Cover Page | ❌ Not in API | Configure per tenant (e.g., "Qi Tech, LLC") |
| `lead_reviewer_name` | RIR Cover Page | ❌ Not in API | Pass from Riskuity OR configure |
| `lead_reviewer_phone` | RIR Cover Page | ❌ Not in API | Pass from Riskuity OR configure |
| `lead_reviewer_email` | RIR Cover Page | ❌ Not in API | Pass from Riskuity OR configure |
| `fta_program_manager_name` | RIR Package | ❌ Not in API | Configure per recipient/region |
| `fta_program_manager_title` | RIR Package | ❌ Not in API | Configure per recipient/region |
| `fta_program_manager_phone` | RIR Package | ❌ Not in API | Configure per recipient/region |
| `fta_program_manager_email` | RIR Package | ❌ Not in API | Configure per recipient/region |

### Date Fields

| Field | Required For | Current Status | Proposed Solution |
|-------|-------------|----------------|-------------------|
| `site_visit_start_date` | RIR Cover Page | ❌ Not in API | Pass from Riskuity project OR calculate |
| `site_visit_end_date` | RIR Cover Page | ❌ Not in API | Pass from Riskuity project OR calculate |
| `site_visit_dates` (formatted) | RIR Cover Page | ❌ Not in API | Format from start/end dates |
| `report_date` | Draft Report Header | ❌ Not in API | Use generation date OR pass from Riskuity |
| `exit_conference_format` | Draft Report | ❌ Not in API | Pass from Riskuity OR default to "virtual" |

---

## Proposed Solutions

### Option 1: Extended API Payload from Riskuity (RECOMMENDED)

When Riskuity triggers CORTAP-RPT report generation, pass additional metadata:

```json
POST /api/v1/projects/{project_id}/generate-report
{
  "project_id": 12345,
  "template_type": "draft-report",
  "metadata": {
    "region_number": 5,
    "review_type": "Triennial Review",
    "recipient_name": "Metro Transit",
    "recipient_acronym": "MVRT",
    "recipient_city_state": "Minneapolis, MN",
    "recipient_website": "https://metrotransit.org",
    "site_visit_start_date": "2025-06-15",
    "site_visit_end_date": "2025-06-17",
    "exit_conference_format": "virtual",
    "contractor": {
      "name": "Qi Tech, LLC",
      "lead_reviewer_name": "Bobby Killebrew",
      "lead_reviewer_phone": "512-350-9912",
      "lead_reviewer_email": "bobby@qitech.com"
    },
    "fta_program_manager": {
      "name": "Syed Ahmed",
      "title": "General Engineer",
      "phone": "617-494-3254",
      "email": "syed.ahmed@dot.gov"
    }
  }
}
```

**Pros:**
- ✅ Most flexible - Riskuity controls all data
- ✅ No configuration needed in CORTAP-RPT
- ✅ Data stays in sync with Riskuity

**Cons:**
- ⚠️ Requires Riskuity UI changes to capture these fields
- ⚠️ Requires Riskuity API modifications

---

### Option 2: Tenant Configuration in CORTAP-RPT

Store tenant-specific defaults in CORTAP-RPT configuration (DynamoDB or config file):

```yaml
tenants:
  fta-contractor-a:
    contractor:
      name: "Qi Tech, LLC"
      lead_reviewer_name: "Bobby Killebrew"
      lead_reviewer_phone: "512-350-9912"
      lead_reviewer_email: "bobby@qitech.com"
    default_region: 5

recipients:
  MVRT:
    name: "Metro Transit"
    acronym: "MVRT"
    city_state: "Minneapolis, MN"
    website: "https://metrotransit.org"
    fta_program_manager:
      name: "Syed Ahmed"
      title: "General Engineer"
      phone: "617-494-3254"
      email: "syed.ahmed@dot.gov"
```

**Pros:**
- ✅ Quick to implement
- ✅ No Riskuity changes needed
- ✅ Works immediately

**Cons:**
- ⚠️ Data duplication (same data in Riskuity and CORTAP-RPT)
- ⚠️ Sync issues if data changes
- ⚠️ Maintenance overhead

---

### Option 3: Hybrid Approach (RECOMMENDED FOR MVP)

- **Pass critical fields** from Riskuity (region_number, review_type, dates)
- **Configure static fields** in CORTAP-RPT (contractor info, FTA PM per region)
- **Extract what we can** from assessments (recipient name/ID)

```python
# Riskuity passes minimal required data
POST /api/v1/projects/{project_id}/generate-report
{
  "project_id": 12345,
  "template_type": "draft-report",
  "region_number": 5,
  "review_type": "Triennial Review",
  "site_visit_start_date": "2025-06-15",
  "site_visit_end_date": "2025-06-17"
}

# CORTAP-RPT looks up:
# - Contractor info from tenant config
# - FTA PM from region mapping
# - Recipient details from recipient config or assessments
```

**Pros:**
- ✅ Minimal Riskuity changes
- ✅ Flexible configuration
- ✅ Fast MVP implementation

**Cons:**
- ⚠️ Some configuration needed in CORTAP-RPT

---

## Implementation Status

### ✅ Completed
- RiskuityClient fetches all assessments
- DataTransformer consolidates 644 assessments → 23 review areas
- Placeholder extraction from assessment structure

### ⏳ In Progress
- DataService orchestrator (Epic 3.5.5)

### 🔜 Next Steps
1. **Decide on solution** (Option 1, 2, or 3)
2. **Implement configuration layer** if using Option 2 or 3
3. **Update Riskuity integration contract** if using Option 1
4. **Update DataTransformer** to use configuration/passed metadata

---

## Code References

- `app/services/data_transformer.py:176-220` - `_extract_project_metadata()` method with TODOs
- `app/services/data_transformer.py:388-450` - `_transform_project()`, `_transform_contractor()`, `_transform_fta_pm()` methods
- Lines marked with `# TODO: Configure or extract from project`

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-10 | Documented missing fields | Blocked Epic 3.5 completion pending data source clarification |
| TBD | [Awaiting decision] | Choose Option 1, 2, or 3 above |
