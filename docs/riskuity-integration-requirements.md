# Riskuity Integration Requirements

**Document:** CORTAP-RPT → Riskuity Integration Specification
**Author:** Mary (Business Analyst)
**Date:** 2025-11-12
**Version:** 1.0
**Purpose:** Define data contract, required changes, and dependencies between CORTAP-RPT and Riskuity systems

---

## Executive Summary

CORTAP-RPT requires specific data from Riskuity to generate intelligent audit reports with conditional logic. This document specifies:

1. **What data CORTAP-RPT needs** from Riskuity API responses
2. **What changes are required** in Riskuity (new fields, UI updates, data capture)
3. **Dependencies and blockers** - which CORTAP-RPT features cannot be implemented until Riskuity changes are complete

**Critical Finding:** Several conditional logic patterns depend on fields that may not currently exist in Riskuity. These must be identified and added before CORTAP-RPT can function fully.

---

## 1. Data Contract Specification

### 1.1 Required API Endpoints

CORTAP-RPT will consume these Riskuity endpoints:

| Endpoint | Purpose | Required Fields | Status |
|----------|---------|----------------|--------|
| `GET /v1/projects/{project_id}` | Project metadata & recipient info | See section 1.2 | ❓ Unknown |
| `GET /v1/projects/{project_id}/assessments` | 23 review area findings | See section 1.3 | ❓ Unknown |
| `GET /v1/projects/{project_id}/surveys` | Survey responses | See section 1.4 | ❓ Unknown |
| `GET /v1/projects/{project_id}/risks` | Risk/ERF data | See section 1.5 | ❓ Unknown |

**Status Legend:**
- ✅ Confirmed exists in current Riskuity API
- ⚠️ Exists but may need modification
- ❌ Does not exist, must be added
- ❓ Unknown, needs verification

---

### 1.2 Project Endpoint Fields

**Endpoint:** `GET /v1/projects/{project_id}`

This endpoint provides project configuration and recipient information.

| Field Name | Data Type | Required? | Conditional Logic | Riskuity Status | Notes |
|------------|-----------|-----------|-------------------|-----------------|-------|
| `recipient_name` | string | ✅ Critical | N/A | ❓ Unknown | Legal name of transit agency |
| `recipient_acronym` | string | ✅ Critical | N/A | ❓ Unknown | Short name (e.g., "MBTA") |
| `region_number` | integer | ✅ Critical | N/A | ❓ Unknown | FTA Region 1-10 |
| `review_type` | enum | ✅ Critical | **CL-1** | ❓ Unknown | **MUST be exact:** "Triennial Review" \| "State Management Review" \| "Combined Triennial and State Management Review" |
| `exit_conference_format` | enum | ✅ Required | **CL-5** | ❓ Unknown | "virtual" \| "in-person" |
| `site_visit_start_date` | date (ISO 8601) | ✅ Required | N/A | ❓ Unknown | Start of on-site visit |
| `site_visit_end_date` | date (ISO 8601) | ✅ Required | N/A | ❓ Unknown | End of on-site visit |
| `report_date` | date (ISO 8601) | ✅ Required | N/A | ❓ Unknown | Date of report issuance |
| `recipient_contact_name` | string | ⚠️ Optional | N/A | ❓ Unknown | Primary contact |
| `recipient_phone` | string | ⚠️ Optional | N/A | ❓ Unknown | Format: (XXX) XXX-XXXX |
| `recipient_email` | email | ⚠️ Optional | N/A | ❓ Unknown | |
| `subrecipient_name` | string | ⚠️ Optional | **CL-4** | ❓ Unknown | If subrecipients reviewed |
| `contractor_name` | string | ⚠️ Optional | N/A | ❓ Unknown | If contractor used |
| `contractor_firm` | string | ⚠️ Optional | N/A | ❓ Unknown | Contractor company |
| `reviewed_subrecipients` | boolean | ⚠️ Optional | **CL-4** | ❓ Unknown | **OR** derive from subrecipient_name != null? |

**Critical Questions:**
1. Does `review_type` currently exist as a structured field?
2. If yes, what are the EXACT stored values? (case-sensitive, spacing)
3. Does `exit_conference_format` exist? If not, where should it be captured?
4. Is `reviewed_subrecipients` a boolean flag or derived from subrecipient data?

---

### 1.3 Assessments Endpoint Fields

**Endpoint:** `GET /v1/projects/{project_id}/assessments`

Returns findings for all 23 CORTAP review areas.

| Field Name | Data Type | Required? | Conditional Logic | Riskuity Status | Notes |
|------------|-----------|-----------|-------------------|-----------------|-------|
| `assessments` | array | ✅ Critical | Multiple | ❓ Unknown | Array of 23 review areas |
| `assessments[].review_area` | string | ✅ Critical | **CL-7** | ❓ Unknown | E.g., "Legal", "Financial Management" |
| `assessments[].finding` | enum | ✅ Critical | **CL-2, CL-6** | ❓ Unknown | **MUST be:** "D" (Deficient) \| "ND" (Non-Deficient) \| "NA" (Not Applicable) |
| `assessments[].deficiency_code` | string | ⚠️ Conditional | **CL-6** | ❓ Unknown | Required only if finding = "D" |
| `assessments[].description` | text | ⚠️ Conditional | **CL-6** | ❓ Unknown | Deficiency description (if finding = "D") |
| `assessments[].corrective_action` | text | ⚠️ Conditional | **CL-6** | ❓ Unknown | Required action (if finding = "D") |
| `assessments[].due_date` | date | ⚠️ Conditional | **CL-6** | ❓ Unknown | Correction deadline (if finding = "D") |
| `assessments[].date_closed` | date | ⚠️ Conditional | **CL-6** | ❓ Unknown | Resolution date (if finding = "D" and closed) |

**Derived Fields (calculated by CORTAP-RPT):**
- `has_deficiencies` = any(assessment.finding == "D")
- `deficiency_count` = count(assessment.finding == "D")
- `deficiency_areas` = list(assessment.review_area where finding == "D")

**Critical Questions:**
1. Are findings stored as "D", "ND", "NA" or different values?
2. Are deficiency details (code, description, corrective action) required fields in Riskuity UI when finding = "D"?
3. Does Riskuity enforce that all 23 review areas are assessed?

---

### 1.4 Surveys Endpoint Fields

**Endpoint:** `GET /v1/projects/{project_id}/surveys`

Survey response data (usage TBD based on template requirements).

| Field Name | Data Type | Required? | Conditional Logic | Riskuity Status | Notes |
|------------|-----------|-----------|-------------------|-----------------|-------|
| `surveys` | array | ⚠️ Optional | TBD | ❓ Unknown | Survey responses |
| `surveys[].question_id` | string | ⚠️ Optional | TBD | ❓ Unknown | |
| `surveys[].response` | string | ⚠️ Optional | TBD | ❓ Unknown | |

**Status:** Low priority for MVP. May be used for future templates.

---

### 1.5 Risks/ERF Endpoint Fields

**Endpoint:** `GET /v1/projects/{project_id}/risks`

Enhanced Review Focus (ERF) data.

| Field Name | Data Type | Required? | Conditional Logic | Riskuity Status | Notes |
|------------|-----------|-----------|-------------------|-----------------|-------|
| `erf_items` | array | ⚠️ Optional | **CL-3, CL-8** | ❓ Unknown | ERF deep-dive areas |
| `erf_items[].area` | string | ⚠️ Optional | **CL-3, CL-7** | ❓ Unknown | Review area under ERF |
| `erf_items[].description` | text | ⚠️ Optional | **CL-3** | ❓ Unknown | Rationale for ERF |

**Derived Fields:**
- `erf_count` = count(erf_items)
- `erf_areas` = list(erf_items[].area)
- `show_erf_section` = erf_count > 0

**Critical Questions:**
1. Does Riskuity have a concept of "Enhanced Review Focus"?
2. If yes, how is it stored (separate table, flag on assessments, risk register)?
3. If no, should ERF be added to Riskuity data model?

---

### 1.6 Audit Team & Personnel Data

**Source:** Likely from `GET /v1/projects/{project_id}` or separate endpoint

| Field Name | Data Type | Required? | Conditional Logic | Riskuity Status | Notes |
|------------|-----------|-----------|-------------------|-----------------|-------|
| `audit_team` | array | ✅ Required | N/A | ❓ Unknown | Team members |
| `audit_team[].first_name` | string | ✅ Required | N/A | ❓ Unknown | |
| `audit_team[].last_name` | string | ✅ Required | N/A | ❓ Unknown | |
| `audit_team[].title` | string | ✅ Required | N/A | ❓ Unknown | FTA official title |
| `audit_team[].phone` | string | ⚠️ Optional | N/A | ❓ Unknown | |
| `audit_team[].email` | email | ⚠️ Optional | N/A | ❓ Unknown | |

**Critical Questions:**
1. Where is audit team data stored in Riskuity?
2. Is it project-specific or pulled from user profiles?
3. Can multiple team members be assigned to a project?

---

## 2. Conditional Logic → Riskuity Field Mapping

This table maps each of the 9 conditional logic patterns to required Riskuity fields.

| CL-ID | Pattern | Riskuity Field(s) Required | Field Type | Current Status | Blocker? |
|-------|---------|---------------------------|------------|----------------|----------|
| **CL-1** | Review Type Routing | `review_type` | enum (3 values) | ❓ Unknown | ✅ YES - blocks all type-specific content |
| **CL-2** | Deficiency Detection | `assessments[].finding` | enum (D/ND/NA) | ❓ Unknown | ✅ YES - blocks deficiency logic |
| **CL-3** | Conditional Sections | `erf_items`, `reviewed_subrecipients` | array, boolean | ❓ Unknown | ⚠️ PARTIAL - ERF section only |
| **CL-4** | Conditional Paragraphs | `reviewed_subrecipients`, `subrecipient_name` | boolean, string | ❓ Unknown | ⚠️ PARTIAL - subrecipient paragraphs only |
| **CL-5** | Exit Format Selection | `exit_conference_format` | enum (2 values) | ❓ Unknown | ⚠️ PARTIAL - affects one paragraph |
| **CL-6** | Deficiency Table | `assessments[]` (all fields) | complex object | ❓ Unknown | ✅ YES - blocks entire table |
| **CL-7** | Dynamic Lists | `assessments[].review_area`, `erf_items[].area` | arrays | ❓ Unknown | ⚠️ PARTIAL - list formatting |
| **CL-8** | Dynamic Counts | `erf_count` (derived from erf_items) | integer | ❓ Unknown | ⚠️ PARTIAL - count display |
| **CL-9** | Grammar Helpers | (uses counts from other fields) | N/A | N/A | ❌ NO - pure logic |

**Blocker Legend:**
- ✅ YES - Without this field, major functionality is blocked
- ⚠️ PARTIAL - Affects specific sections/features only
- ❌ NO - No external dependency

---

## 3. Required Riskuity Changes

### 3.1 Assumed MISSING Fields (High Priority Verification)

These fields are **likely missing** from current Riskuity and **must be added**:

| Field | Where to Add | UI Component | Default Value | Priority |
|-------|-------------|--------------|---------------|----------|
| `review_type` | Project profile | Dropdown (3 options) | (none - must select) | 🔴 CRITICAL |
| `exit_conference_format` | Project profile | Radio button (2 options) | "virtual" | 🟠 HIGH |
| `reviewed_subrecipients` | Project profile | Checkbox | false | 🟡 MEDIUM |
| `erf_items` | Risk/assessment module | Multi-select or table | [] (empty array) | 🟡 MEDIUM |

**Dropdown Values (EXACT - case-sensitive):**

`review_type`:
- "Triennial Review"
- "State Management Review"
- "Combined Triennial and State Management Review"

`exit_conference_format`:
- "virtual"
- "in-person"

### 3.2 Riskuity UI Changes Required

**Project Profile / Review Configuration Screen:**

```
┌─────────────────────────────────────────────────┐
│ CORTAP Review Configuration                     │
├─────────────────────────────────────────────────┤
│                                                  │
│ Review Type: * [Dropdown]                       │
│   ○ Triennial Review                            │
│   ○ State Management Review                     │
│   ○ Combined Triennial and State Management     │
│                                                  │
│ Exit Conference Format: * [Radio]               │
│   ○ Virtual     ○ In-Person                     │
│                                                  │
│ Subrecipients Reviewed: [Checkbox]              │
│   If checked, display:                          │
│   Subrecipient Name: [Text field]               │
│                                                  │
│ Enhanced Review Focus (ERF):                    │
│   [+ Add ERF Area]                              │
│   [Table: Area | Description | Actions]         │
│                                                  │
└─────────────────────────────────────────────────┘
```

### 3.3 Riskuity Database Schema Changes

**Estimated changes** (to be confirmed with Riskuity team):

**`projects` table:**
```sql
ALTER TABLE projects ADD COLUMN review_type VARCHAR(100);
ALTER TABLE projects ADD COLUMN exit_conference_format VARCHAR(20);
ALTER TABLE projects ADD COLUMN reviewed_subrecipients BOOLEAN DEFAULT false;
ALTER TABLE projects ADD COLUMN subrecipient_name VARCHAR(255);
```

**`erf_items` table (new):**
```sql
CREATE TABLE erf_items (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id),
  review_area VARCHAR(100) NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 3.4 Riskuity API Response Schema Changes

**Updated `GET /v1/projects/{project_id}` response:**

```json
{
  "id": "RSKTY-12345",
  "recipient_name": "Massachusetts Bay Transportation Authority",
  "recipient_acronym": "MBTA",
  "region_number": 1,

  // NEW FIELDS (to be added):
  "review_type": "Triennial Review",
  "exit_conference_format": "virtual",
  "reviewed_subrecipients": true,
  "subrecipient_name": "Cape Cod Regional Transit Authority",

  // Existing fields:
  "site_visit_start_date": "2025-03-10",
  "site_visit_end_date": "2025-03-14",
  "report_date": "2025-04-15",
  "audit_team": [...]
}
```

**New or Updated `GET /v1/projects/{project_id}/erf` response:**

```json
{
  "project_id": "RSKTY-12345",
  "erf_items": [
    {
      "area": "Procurement",
      "description": "Multiple sole-source contracts without proper justification"
    },
    {
      "area": "ADA Compliance",
      "description": "Accessibility complaints backlog exceeding 90 days"
    }
  ]
}
```

---

## 4. Dependency Tracking Matrix

### 4.1 Feature Dependency Map

This matrix shows which CORTAP-RPT features are **blocked** by which Riskuity changes.

| CORTAP-RPT Feature | Depends On | Riskuity Status | Workaround Possible? | Impact if Missing |
|--------------------|------------|-----------------|----------------------|-------------------|
| **Review Type Content Selection** | `review_type` field | ❓ Unknown | ❌ NO | CRITICAL - All type-specific paragraphs incorrect |
| **Deficiency Detection** | `assessments[].finding` values | ❓ Unknown | ⚠️ Partial (mock data) | CRITICAL - Core feature broken |
| **Deficiency Table Generation** | All `assessments[]` fields | ❓ Unknown | ⚠️ Partial (mock data) | HIGH - Table incomplete or wrong |
| **Exit Conference Paragraph** | `exit_conference_format` field | ❓ Unknown | ✅ YES (default to "virtual") | LOW - One paragraph affected |
| **ERF Section** | `erf_items` array | ❓ Unknown | ✅ YES (omit section) | MEDIUM - Section missing but not broken |
| **Subrecipient Paragraphs** | `reviewed_subrecipients` flag | ❓ Unknown | ✅ YES (omit paragraphs) | MEDIUM - Paragraphs missing but not broken |

**Risk Assessment:**
- 🔴 **2 CRITICAL blockers**: `review_type`, `assessments[].finding`
- 🟠 **1 HIGH blocker**: Complete assessment field set
- 🟡 **3 MEDIUM dependencies**: ERF, subrecipients, format

### 4.2 Implementation Phases & Dependencies

**Phase 1: MVP Core (Weeks 1-3)**

| Story | Riskuity Dependency | Status | Blocker Level |
|-------|-------------------|--------|---------------|
| 1.1: Project Setup | None | ✅ READY | None |
| 1.2: Logging | None | ✅ READY | None |
| 1.3: Exceptions | None | ✅ READY | None |
| 1.4: POC Template | None | ✅ READY | None (can use mock data) |
| 1.5: DocumentGenerator | None | ✅ READY | None |
| 1.6: Grammar Helpers | None | ✅ READY | None |

**Phase 2: Conditional Logic (Weeks 4-5)**

| Story | Riskuity Dependency | Status | Blocker Level |
|-------|-------------------|--------|---------------|
| 2.1: Template Data Models | Field definitions | ⚠️ AT RISK | HIGH (need exact field names/types) |
| 2.2: Review Type Routing (CL-1) | `review_type` field | 🔴 BLOCKED | CRITICAL |
| 2.3: Deficiency Detection (CL-2) | `assessments[].finding` | 🔴 BLOCKED | CRITICAL |
| 2.4: Conditional Sections (CL-3) | `erf_items`, `reviewed_subrecipients` | ⚠️ AT RISK | MEDIUM |
| 2.5: Exit Format (CL-5) | `exit_conference_format` | ⚠️ AT RISK | LOW |
| 2.6: Deficiency Table (CL-6) | All assessment fields | 🔴 BLOCKED | HIGH |
| 2.7: Counts & Grammar (CL-8, CL-9) | Derived from other fields | ⚠️ AT RISK | MEDIUM |
| 2.8: Logic Integration | All above | 🔴 BLOCKED | CRITICAL |

**Phase 3: Riskuity Integration (Week 6)**

| Story | Riskuity Dependency | Status | Blocker Level |
|-------|-------------------|--------|---------------|
| 3.1: Riskuity API Client | API access, endpoints exist | 🔴 BLOCKED | CRITICAL |
| 3.2: Data Transformer | Field mapping verified | 🔴 BLOCKED | CRITICAL |
| 3.3: Data Orchestration | All endpoints working | 🔴 BLOCKED | CRITICAL |

**KEY FINDING:** **Epic 2 and Epic 3 cannot be fully completed without Riskuity field verification and changes.**

### 4.3 Risk Mitigation Strategies

**If Riskuity changes are delayed:**

| Scenario | Mitigation | Trade-off |
|----------|-----------|-----------|
| `review_type` missing | Hard-code to "Triennial Review" for testing | No multi-type support |
| `exit_conference_format` missing | Default to "virtual" | Wrong paragraph in some cases |
| `erf_items` missing | Omit ERF section entirely | Missing functionality |
| Assessment fields incomplete | Use mock/test data | Cannot test with real Riskuity |
| API access delayed | Build with mock API responses | Integration testing blocked |

**Recommended Approach:**
1. **Immediate:** Send questions to Riskuity team (see Section 5)
2. **Week 1-2:** Build with mock data, document exact requirements
3. **Week 3:** Validate mock data structure with Riskuity
4. **Week 4+:** Integrate with real Riskuity API once fields confirmed/added

---

## 5. Questions for Riskuity Team

### 5.1 CRITICAL Priority Questions

**Must be answered before Epic 2 (Conditional Logic) implementation:**

1. **Review Type Field:**
   - Q: Does Riskuity currently capture "Review Type" (Triennial/State Management/Combined)?
   - Q: If yes, what is the exact field name and possible values?
   - Q: If no, can this be added as a dropdown in the project profile?
   - Q: What is the expected timeline for adding this field?

2. **Assessment Findings:**
   - Q: What are the EXACT values stored for assessment findings? (D/ND/NA or different?)
   - Q: Are all 23 CORTAP review areas guaranteed to be present in the assessments endpoint?
   - Q: If a finding is "D" (Deficient), are deficiency_code, description, and corrective_action required fields?

3. **Exit Conference Format:**
   - Q: Does Riskuity capture whether the exit conference was virtual or in-person?
   - Q: If no, can this be added as a simple radio button (virtual/in-person)?
   - Q: Where would this be captured in the Riskuity UI?

### 5.2 HIGH Priority Questions

**Needed for complete MVP functionality:**

4. **Enhanced Review Focus (ERF):**
   - Q: Does Riskuity have a concept of "Enhanced Review Focus" areas?
   - Q: If yes, how is ERF data stored and accessed via API?
   - Q: If no, should ERF be tracked in Riskuity or handled externally?

5. **Subrecipient Review:**
   - Q: How does Riskuity indicate that subrecipients were reviewed?
   - Q: Is there a `reviewed_subrecipients` boolean flag?
   - Q: Or should CORTAP-RPT infer this from `subrecipient_name` != null?

6. **API Response Schema:**
   - Q: Can you provide sample JSON responses for all 4 endpoints (projects, assessments, surveys, risks)?
   - Q: Are there API documentation (Swagger/OpenAPI) specs available?

### 5.3 MEDIUM Priority Questions

**Important for data quality and user experience:**

7. **Audit Team Personnel:**
   - Q: Where is audit team information stored in Riskuity?
   - Q: Is it part of the project endpoint or a separate endpoint?
   - Q: Can multiple team members be assigned to a project?

8. **Date Fields:**
   - Q: What date format does Riskuity use in API responses (ISO 8601, Unix timestamp, etc.)?
   - Q: Are all dates stored in UTC or local timezone?

9. **Field Validation:**
   - Q: Are required fields enforced in Riskuity UI (cannot submit without them)?
   - Q: What happens if optional fields are missing (null, empty string, omitted)?

10. **Data Completeness:**
    - Q: At what point in the CORTAP review workflow is data considered "complete" for report generation?
    - Q: Should CORTAP-RPT validate data completeness or assume Riskuity enforces it?

### 5.4 Integration Logistics Questions

11. **API Access:**
    - Q: What is the process for obtaining API credentials for development/testing?
    - Q: Is there a sandbox/test environment available?
    - Q: What are the rate limits for the Riskuity API?

12. **Change Management:**
    - Q: If new fields need to be added to Riskuity, what is the typical timeline?
    - Q: Would schema changes require Riskuity API versioning (v2)?
    - Q: Can we coordinate a joint testing phase once Riskuity changes are deployed?

---

## 6. Next Steps & Action Items

### Immediate Actions (This Week)

- [ ] **Send Questions to Riskuity Team** (Section 5) - Priority: CRITICAL
  - Assign to: Bob (Product Owner)
  - Deadline: End of Week
  - Deliverable: Documented responses from Riskuity

- [ ] **Request Sample API Responses** - Priority: HIGH
  - Obtain real or representative JSON responses for all 4 endpoints
  - Use for data model validation and mock data creation

- [ ] **Schedule Riskuity Integration Meeting** - Priority: HIGH
  - Attendees: CORTAP-RPT team + Riskuity technical lead
  - Agenda: Review integration requirements, discuss timeline for changes

### Short-Term Actions (Weeks 1-2)

- [ ] **Create Mock Riskuity API Responses** - Priority: HIGH
  - Based on best-guess field structure
  - Use for CORTAP-RPT development until real API available
  - Document all assumptions made

- [ ] **Validate Data Models** - Priority: HIGH
  - Once Riskuity responds, update `app/models/template_data.py`
  - Ensure field names, types, and constraints match exactly

- [ ] **Update Epic 2 Stories** - Priority: MEDIUM
  - Add Riskuity dependency notes to affected stories
  - Update acceptance criteria with actual field names

### Medium-Term Actions (Weeks 3-4)

- [ ] **Riskuity Field Addition (if needed)** - Priority: CRITICAL
  - Coordinate with Riskuity team to add missing fields
  - Agree on field names, types, UI placement, default values

- [ ] **API Integration Testing** - Priority: HIGH
  - Test with real Riskuity sandbox environment
  - Validate data transformation logic

- [ ] **Document Integration Contract** - Priority: MEDIUM
  - Formalize API contract between systems
  - Include versioning strategy for future changes

---

## 7. Open Issues & Assumptions

### Current Assumptions (TO BE VALIDATED)

| Assumption | Risk Level | Validation Method |
|-----------|------------|-------------------|
| Riskuity API uses JSON REST format | LOW | Verify with API docs |
| All 4 endpoints exist and are accessible | MEDIUM | Test API access |
| `review_type` field does NOT currently exist | HIGH | Confirm with Riskuity team |
| Assessment findings use "D"/"ND"/"NA" values | HIGH | Check actual values in database |
| ERF data is NOT currently tracked in Riskuity | MEDIUM | Confirm current ERF workflow |
| Audit team is part of project endpoint | MEDIUM | Review API response structure |
| Dates are in ISO 8601 format | LOW | Verify API response samples |

### Unresolved Questions

1. **Data Ownership:** Who is responsible for data quality? (Riskuity validates vs CORTAP-RPT validates)
2. **Error Handling:** What should CORTAP-RPT do if required fields are missing from Riskuity?
3. **Versioning:** How will API changes be communicated and handled?
4. **Performance:** What are Riskuity API performance characteristics (latency, rate limits)?

---

## 8. Appendix: Full Field Inventory

### 8.1 Complete Field List by Endpoint

**GET /v1/projects/{project_id}** (estimated 30+ fields)

**Core Project Info:**
- id, recipient_name, recipient_acronym, region_number

**Review Configuration (NEW - to be added):**
- review_type, exit_conference_format, reviewed_subrecipients, subrecipient_name

**Dates:**
- site_visit_start_date, site_visit_end_date, report_date

**Contact Info:**
- recipient_contact_name, recipient_phone, recipient_email

**Optional:**
- contractor_name, contractor_firm

**GET /v1/projects/{project_id}/assessments** (23 review areas)

**Per Assessment:**
- review_area, finding, deficiency_code, description, corrective_action, due_date, date_closed

**GET /v1/projects/{project_id}/risks (ERF data)**

**ERF Items:**
- erf_items[].area, erf_items[].description

**GET /v1/projects/{project_id}/surveys** (usage TBD)

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-12 | Mary (Business Analyst) | Initial version - comprehensive integration requirements |

---

**END OF DOCUMENT**
