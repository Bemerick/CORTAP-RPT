# Mock JSON Data for CORTAP-RPT Development

## Overview

This directory contains mock JSON data files created from **actual FTA Recipient Information Request (RIR) forms**. The data has been extracted from real completed reviews to provide realistic test data for developing Epic 3.5 (Data Service) and Epic 4 (RIR Template).

## Data Source

All data extracted from completed RIR forms located in:
`docs/completed_reviews/RIR_forms/`

Template field structure based on:
`docs/requirements/Form_Fields-RO_State_Recipient_FY2025_RecipientInformationRequestPackage_Final_1.3.25.pdf`

## Mock Data Files

### project-001-gnhtd-ct.json
**Source:** `01_CT_1337_GNHTD_2023_TR_RIR.pdf`

**Project Details:**
- **Recipient:** Greater New Haven Transit District (GNHTD)
- **Location:** Hamden, CT
- **Region:** 1
- **Recipient ID:** 1337
- **Review Type:** Triennial Review
- **Contractor:** Qi Tech, LLC
- **Lead Reviewer:** Bobby Killebrew
- **FTA PM:** Syed T. Ahmed (General Engineer)

**Key Characteristics:**
- Has 1 deficiency (Subrecipient Oversight)
- Site visit dates: TBD
- Virtual exit conference

**Use Case:** Test single deficiency scenario

---

### project-002-mvrta-ma.json
**Source:** `01_MA_1374_MVRTA_2023_TR_RIR.pdf`

**Project Details:**
- **Recipient:** Merrimack Valley Regional Transit Authority (MVRTA)
- **Location:** Haverhill, MA
- **Region:** 1
- **Recipient ID:** 1374
- **Review Type:** Triennial Review
- **Contractor:** Qi Tech, LLC
- **Lead Reviewer:** Bobby Killebrew
- **FTA PM:** Syed T. Ahmed (General Engineer)

**Key Characteristics:**
- **No deficiencies** (clean review)
- Site visit dates: June 7, 2023 (specific date)
- All 23 review areas: ND (No Deficiency) or NA (Not Applicable)

**Use Case:** Test clean review scenario with specific site visit date

---

### project-003-hrt-va.json
**Source:** `R3_VA_HRT_FY2023_RecipientInformationRequestPackage 111822.pdf`

**Project Details:**
- **Recipient:** Transportation District Commission of Hampton Roads (HRT)
- **Location:** Hampton, VA
- **Region:** 3
- **Recipient ID:** 1456
- **Review Type:** Triennial Review
- **Contractor:** Calyptus Consulting Group, Inc.
- **Lead Reviewer:** Ellen Harvey
- **FTA PM:** Jason Yucis (Financial Analyst)

**Key Characteristics:**
- Has 2 deficiencies (Financial Management, Transit Asset Management)
- Has 1 ERF (Enhanced Review Focus) item
- Different region (Region 3 vs Region 1)
- Different contractor
- Review status: In Progress

**Use Case:** Test multiple deficiency scenario with ERF items

---

## JSON Schema Structure

All JSON files follow the canonical schema designed for the CORTAP Data Service (Epic 3.5):

```json
{
  "project_id": "RSKTY-XXXX",           // Riskuity project ID
  "generated_at": "ISO 8601 timestamp",
  "data_version": "1.0",

  "project": {
    "region_number": 1-10,              // FTA Region
    "review_type": "Triennial Review | State Management Review | Combined...",
    "recipient_name": "...",
    "recipient_acronym": "...",
    "recipient_city_state": "...",
    "recipient_id": "...",
    "recipient_website": "...",
    "site_visit_dates": "...",
    "site_visit_start_date": "YYYY-MM-DD or null",
    "site_visit_end_date": "YYYY-MM-DD or null",
    "report_date": "YYYY-MM-DD",
    "exit_conference_format": "virtual | in-person"
  },

  "contractor": {
    "lead_reviewer_name": "...",
    "contractor_name": "...",
    "lead_reviewer_phone": "...",
    "lead_reviewer_email": "..."
  },

  "fta_program_manager": {
    "fta_program_manager_name": "...",
    "fta_program_manager_title": "...",
    "fta_program_manager_phone": "...",
    "fta_program_manager_email": "..."
  },

  "assessments": [
    // Array of 23 review areas
    {
      "review_area": "Legal | Financial Management | ...",
      "finding": "D | ND | NA",          // Deficiency, No Deficiency, Not Applicable
      "deficiency_code": "D-YYYY-NNN or null",
      "description": "string or null",
      "corrective_action": "string or null",
      "due_date": "YYYY-MM-DD or null",
      "date_closed": "YYYY-MM-DD or null"
    }
  ],

  "erf_items": [
    // Enhanced Review Focus items (optional)
    {
      "erf_area": "...",
      "focus_description": "...",
      "completion_status": "In Progress | Completed"
    }
  ],

  "metadata": {
    "has_deficiencies": true | false,
    "deficiency_count": 0,
    "deficiency_areas": ["..."],
    "erf_count": 0,
    "reviewed_subrecipients": true | false,
    "subrecipient_name": "string or null",
    "fiscal_year": "FYXXXX",
    "review_status": "Completed | In Progress"
  }
}
```

## Field Mapping to RIR Template

Based on template: `Form_Fields-RO_State_Recipient_FY2025_RecipientInformationRequestPackage_Final_1.3.25.pdf`

| **RIR Template Field** | **JSON Path** |
|------------------------|---------------|
| `[#]` (Region) | `project.region_number` |
| `[Triennial Review]/[State Management Review]/...` | `project.review_type` |
| `[Recipient Name]` | `project.recipient_name` |
| `[Recipient Location]` | `project.recipient_city_state` |
| `[#]` (Recipient ID) | `project.recipient_id` |
| `[URL]` | `project.recipient_website` |
| Site Visit Dates | `project.site_visit_dates` |
| `[Lead Reviewer Name]` | `contractor.lead_reviewer_name` |
| `[Contractor Name]` | `contractor.contractor_name` |
| `[Lead Reviewer Phone #]` | `contractor.lead_reviewer_phone` |
| `[Lead Reviewer Email Address]` | `contractor.lead_reviewer_email` |
| `[FTA PM for Recipient]` | `fta_program_manager.fta_program_manager_name` |
| `[FTA PM Phone #]` | `fta_program_manager.fta_program_manager_phone` |
| `[FTA PM Email Address]` | `fta_program_manager.fta_program_manager_email` |

## Usage for Development

### Epic 3.5: Data Service Development
Use these files to:
1. Test JSON caching to S3 (Story 3.5.4)
2. Test data validation (Story 3.5.6)
3. Test POST `/projects/{id}/data` endpoint (Story 3.5.7)
4. Develop without Riskuity API access

### Epic 4: RIR Template Development
Use these files to:
1. Test RIR template rendering (Story 4.4)
2. Test conditional logic for review types (Story 4.2)
3. Test RIRContextBuilder transformations (Story 4.3)
4. E2E testing (Story 4.6)

### Test Scenarios

**Test 1: Clean Review**
- Use: `project-002-mvrta-ma.json`
- Expected: RIR generates successfully, no deficiency warnings

**Test 2: Single Deficiency**
- Use: `project-001-gnhtd-ct.json`
- Expected: RIR generates with 1 deficiency noted

**Test 3: Multiple Deficiencies + ERF**
- Use: `project-003-hrt-va.json`
- Expected: RIR generates with 2 deficiencies and ERF mention

**Test 4: Different Review Types**
- All files use "Triennial Review"
- Modify `project.review_type` to test other types:
  - "State Management Review"
  - "Combined Triennial and State Management Review"

**Test 5: Date Formatting**
- `project-002-mvrta-ma.json` has specific site visit date
- Others have "TBD"
- Test date formatting logic

## Next Steps

1. **Load into Epic 3.5.1**: Use as example when designing canonical JSON schema
2. **Story 3.5.4 Testing**: Upload these to S3 for cache testing
3. **Story 4.3 Development**: Use to build `RIRContextBuilder.build_context()`
4. **Story 4.6 E2E**: Use all 3 files for comprehensive testing

## Data Freshness

- **Created:** 2025-11-19
- **Source Data:** FY2023 RIR forms (actual completed reviews)
- **Schema Version:** 1.0

## Notes

- All data extracted from real RIR forms to ensure realistic test data
- Sensitive data (full phone numbers, some emails) slightly modified for privacy
- Assessment findings are realistic but simplified for testing
- ERF items added to Virginia project for testing ERF scenarios
