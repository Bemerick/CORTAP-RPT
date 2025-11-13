# Recipient Information Request (RIR) - Template Requirements

**Document:** CORTAP-RPT RIR Template Specification
**Author:** Mary (Business Analyst)
**Date:** 2025-11-13
**Version:** 1.0
**Template Source:** `docs/requirements/RO_State_Recipient_FY2025_RecipientInformationRequestPackage_Final_1.3.25.docx`

---

## Executive Summary

The **Recipient Information Request (RIR) Package** is the second document template for CORTAP-RPT implementation. Unlike the Draft Audit Report (which has extensive conditional logic), the RIR is primarily a **static document with simple field substitution**—making it an ideal candidate for early implementation and validation of the data architecture.

**Key Characteristics:**
- **Template Complexity:** LOW (mostly static text, minimal conditional logic)
- **Field Count:** 15 merge fields
- **Conditional Logic:** MINIMAL (review type selection only)
- **Document Type:** Information request form sent to recipients before site visits
- **Generation Timing:** Early in review process (pre-site visit)

---

## Template Field Inventory

### Cover Page Fields

| Bracket Field | Purpose | Example Value | Required? | Riskuity Source |
|---------------|---------|---------------|-----------|-----------------|
| **`[#]` (Region)** | FTA Region number | "4" (Region 4) | ✅ Critical | `projects.region_number` |
| **Review Type** | Type of review | "Triennial Review" | ✅ Critical | `projects.review_type` |
| **`[Recipient Name]`** | Transit agency legal name | "Massachusetts Bay Transportation Authority" | ✅ Critical | `projects.recipient_name` |
| **`[Recipient Location]`** | City, State | "Boston, MA" | ✅ Critical | `projects.recipient_city_state` |
| **`[#]` (Recipient ID)** | Riskuity recipient ID | "1057" | ✅ Critical | `projects.recipient_id` |
| **`[URL]`** | Recipient website | "https://www.mbta.com" | ⚠️ Optional | `projects.recipient_website` |
| **Site Visit Dates** | TBD or actual dates | "March 10-14, 2025" | ⚠️ Optional | `projects.site_visit_start_date` + `site_visit_end_date` |
| **`[Lead Reviewer Name]`** | Contractor lead reviewer | "Scott W. Schilt" | ✅ Critical | `projects.lead_reviewer_name` |
| **`[Contractor Name]`** | Contractor firm name | "Milligan & Company" | ✅ Critical | `projects.contractor_name` |
| **`[Lead Reviewer Phone #]`** | Contact phone | "215-496-9100 ext 183" | ✅ Critical | `projects.lead_reviewer_phone` |
| **`[Lead Reviewer Email Address]`** | Contact email | "sschilt@milligancpa.com" | ✅ Critical | `projects.lead_reviewer_email` |

### Body Content Fields

| Bracket Field | Purpose | Example Value | Required? | Riskuity Source |
|---------------|---------|---------------|-----------|-----------------|
| **`[FTA PM for Recipient]`** | FTA Program Manager name | "John Smith" | ✅ Critical | `projects.fta_program_manager_name` |
| **`[FTA PM Phone #]`** | FTA PM phone | "(202) 555-0123" | ✅ Critical | `projects.fta_program_manager_phone` |
| **`[FTA PM Email Address]`** | FTA PM email | "john.smith@dot.gov" | ✅ Critical | `projects.fta_program_manager_email` |

**Total Fields:** 15 unique merge fields

---

## Document Variables (from Word Template)

The HTML shows these document variables are embedded in the template:

| Variable Name | Maps To Bracket Field | Notes |
|---------------|----------------------|-------|
| `varFTARegion` | `[#]` (Region) | Integer 1-10 |
| `varGranteeName` | `[Recipient Name]` | Full legal name |
| `varGranteeCityState` | `[Recipient Location]` | Format: "City, ST" |
| `varRecipientID` | `[#]` (Recipient ID) | Numeric ID |
| `varReviewerName` | `[Lead Reviewer Name]` | Contractor lead |
| `varContractorName` | `[Contractor Name]` | Firm name |
| `varReviewerPhone` | `[Lead Reviewer Phone #]` | Phone with ext |
| `varReviewerEmail` | `[Lead Reviewer Email Address]` | Email |
| `varFTAProgramManagerName` | `[FTA PM for Recipient]` | FTA PM name |
| `varFTAProgramManagerPhone` | `[FTA PM Phone #]` | FTA PM phone |
| `varFTAProgramManagerEmail` | `[FTA PM Email Address]` | FTA PM email |
| `varSiteVisitDates` | Site Visit Dates | Date range or "TBD" |
| `varDueDate` | Due Date (in body) | Response deadline |
| `varPriorDeficiencies` | Prior Deficiencies (in body) | Historical context |
| `varContractorCityState` | Contractor location | City, ST |
| `varFTACityState` | FTA office location | City, ST |

**Note:** Some variables (like `varPriorDeficiencies`, `varDueDate`) are referenced but may not be visible on cover page—likely used in body content.

---

## Conditional Logic Requirements

### CL-RIR-1: Review Type Selection

**Pattern:** Mutually exclusive text selection based on review type

**Template Text (Line 9449):**
```
FY 2025 [Triennial Review]/[State Management Review]/[Combined Triennial and State Management Review]
```

**Logic:**
- If `review_type == "Triennial Review"` → Display: "FY 2025 Triennial Review"
- If `review_type == "State Management Review"` → Display: "FY 2025 State Management Review"
- If `review_type == "Combined Triennial and State Management Review"` → Display: "FY 2025 Combined Triennial and State Management Review"

**Implementation:** Same as Draft Audit Report CL-1 (Review Type Routing)

**Priority:** 🔴 CRITICAL (depends on `projects.review_type` field in Riskuity)

---

## Riskuity Field Mapping

### Required New Fields (Not Yet Documented)

These fields are needed for RIR but were NOT in the Draft Audit Report requirements:

| Field Name | Data Type | Purpose | Priority | Riskuity Status |
|------------|-----------|---------|----------|-----------------|
| `recipient_website` | URL | Recipient's public website | ⚠️ Optional | ❓ Unknown |
| `lead_reviewer_name` | string | Contractor lead reviewer | ✅ Critical | ❓ Unknown - LIKELY MISSING |
| `lead_reviewer_phone` | string | Reviewer phone | ✅ Critical | ❓ Unknown - LIKELY MISSING |
| `lead_reviewer_email` | email | Reviewer email | ✅ Critical | ❓ Unknown - LIKELY MISSING |
| `contractor_name` | string | Contractor firm name | ✅ Critical | ❓ Unknown - LIKELY MISSING |
| `contractor_city_state` | string | Contractor location | ⚠️ Optional | ❓ Unknown |
| `fta_program_manager_name` | string | Assigned FTA PM | ✅ Critical | ❓ Unknown - LIKELY MISSING |
| `fta_program_manager_phone` | string | FTA PM phone | ✅ Critical | ❓ Unknown - LIKELY MISSING |
| `fta_program_manager_email` | email | FTA PM email | ✅ Critical | ❓ Unknown - LIKELY MISSING |
| `fta_office_city_state` | string | Regional office location | ⚠️ Optional | ❓ Unknown |
| `due_date` | date | RIR response deadline | ⚠️ Optional | ❓ Unknown |
| `prior_deficiencies` | text | Historical deficiency context | ⚠️ Optional | ❓ Unknown |

### Fields Shared with Draft Audit Report

| Field Name | Status | Notes |
|------------|--------|-------|
| `region_number` | ✅ Already documented | Region 1-10 |
| `review_type` | ✅ Already documented | 🔴 CRITICAL blocker if missing |
| `recipient_name` | ✅ Already documented | |
| `recipient_acronym` | NOT used in RIR | Used in other templates |
| `recipient_city_state` | NEW for RIR | Different from separate city/state fields |
| `recipient_id` | ✅ Already documented | |
| `site_visit_start_date` | ✅ Already documented | |
| `site_visit_end_date` | ✅ Already documented | |

---

## Critical Questions for Riskuity Team (RIR-Specific)

**These are IN ADDITION to the questions in the main Riskuity Integration Requirements document.**

### CRITICAL Priority

13. **Contractor/Reviewer Information:**
    - Does Riskuity capture contractor and lead reviewer details for each project?
    - If yes, where is this stored (project profile, separate contractor table)?
    - Fields needed: contractor_name, lead_reviewer_name, lead_reviewer_phone, lead_reviewer_email
    - **OR** should this be managed externally (contractor assignment system)?

14. **FTA Program Manager Assignment:**
    - Does Riskuity track which FTA Program Manager is assigned to each project?
    - If yes, where is this stored (user assignment, project field)?
    - Fields needed: fta_pm_name, fta_pm_phone, fta_pm_email
    - **OR** is this pulled from another FTA system?

### HIGH Priority

15. **Recipient Website:**
    - Does Riskuity capture recipient website URLs?
    - If no, should this be added to recipient profile?
    - Default behavior if missing: Omit field or display "N/A"?

16. **RIR Due Date:**
    - How is the RIR response due date determined (business rule or manual entry)?
    - Should CORTAP-RPT calculate this (e.g., site visit date - 30 days)?
    - Or does Riskuity store this explicitly?

17. **Prior Deficiencies Context:**
    - Should RIR include summary of prior deficiencies from previous reviews?
    - If yes, how far back (previous review only, or last 3 years)?
    - Or is this optional contextual text entered manually?

---

## Architectural Proposal: Data Service Pattern

### Current Architecture (Draft Audit Report Approach)

**Flow:**
```
Riskuity API → CORTAP-RPT → Template Engine → Document
     ↓             ↓               ↓
  (4 endpoints) (Transform)  (python-docxtpl)
```

**Characteristics:**
- Real-time API calls during document generation
- Data transformation happens in memory
- No intermediate storage
- Tightly coupled to template engine

### Proposed Architecture: Data Service → JSON → Template

**Flow:**
```
Riskuity API → Data Service → JSON File → Template Engine → Document
     ↓              ↓            ↓              ↓
(4 endpoints)  (Transform)  (Persist)   (python-docxtpl)
```

**Characteristics:**
- Data fetch and transformation separated from template rendering
- JSON file serves as "contract" between data layer and template layer
- JSON can be cached, versioned, audited
- Enables multiple templates to share same data
- Allows template generation without re-fetching Riskuity data

---

### Architectural Analysis: Pros & Cons

#### ✅ ADVANTAGES of Data Service Pattern

**1. Separation of Concerns**
- **Data Layer:** Responsible only for fetching and transforming Riskuity data
- **Template Layer:** Responsible only for rendering JSON to Word documents
- **Result:** Easier to test, maintain, and debug each layer independently

**2. Multi-Template Efficiency**
- **Problem:** RIR, Draft Report, Cover Letter, Notification Letter all need same project data
- **Solution:** Fetch Riskuity data ONCE → Generate multiple documents from same JSON
- **Benefit:** Reduces API calls to Riskuity (performance, rate limit avoidance)

**3. Data Caching & Reuse**
- **Scenario:** Auditor generates RIR, then realizes they need to regenerate with correction
- **Without JSON:** Re-fetch all data from Riskuity (slow, wasteful)
- **With JSON:** Reuse cached JSON file (fast, efficient)

**4. Auditability & Version Control**
- **Benefit:** JSON file provides exact snapshot of data used for document generation
- **Use Case:** "What data was used to generate this document 6 months ago?"
- **Result:** JSON file serves as audit trail

**5. Development & Testing**
- **Benefit:** Developers can work on templates using static JSON files (no Riskuity API needed)
- **Use Case:** Template developers can iterate without waiting for Riskuity API access
- **Result:** Parallel development (data team + template team)

**6. Validation & Quality Gates**
- **Benefit:** Data completeness validation happens BEFORE template rendering
- **Use Case:** Validate JSON schema, check for required fields, enforce business rules
- **Result:** Better error handling, clearer error messages to users

#### ❌ DISADVANTAGES of Data Service Pattern

**1. Increased Complexity**
- **Trade-off:** Adds another layer (data service) and artifact (JSON file)
- **Impact:** More code to write, test, and maintain
- **Mitigation:** Clear interfaces, good documentation

**2. Storage Requirements**
- **Trade-off:** JSON files must be stored (S3, filesystem, database)
- **Impact:** Additional infrastructure, cleanup policies needed
- **Mitigation:** Store in S3 with lifecycle policies (auto-delete after 30 days)

**3. Stale Data Risk**
- **Trade-off:** JSON may be outdated if Riskuity data changes between fetch and render
- **Impact:** Generated document may not reflect latest Riskuity data
- **Mitigation:** Time-to-live (TTL) on JSON files, timestamp validation

**4. Initial Development Overhead**
- **Trade-off:** More upfront work to build data service layer
- **Impact:** Slower initial delivery
- **Mitigation:** Pays off quickly when adding 2nd, 3rd, 4th templates

---

### Recommendation: Adopt Data Service Pattern

**Verdict:** ✅ **STRONGLY RECOMMENDED** for CORTAP-RPT

**Rationale:**

**1. Multiple Templates Are Coming**
- You already have 4-5 document templates planned
- Data Service pattern prevents redundant API calls
- Efficiency gains compound with each new template

**2. RIR is Perfect Proof-of-Concept**
- Simple template (15 fields, minimal logic)
- Low risk, high learning value
- Can validate architecture before complex templates

**3. Riskuity Integration Uncertainty**
- We don't yet know Riskuity's rate limits or performance
- JSON caching provides buffer against slow/unreliable API
- Reduces blast radius if Riskuity API has issues

**4. Future Features Unlock**
- **Batch Generation:** "Generate all documents for this project" (RIR + Draft + Cover Letter) from single data fetch
- **Preview Mode:** Show user data completeness BEFORE generating document
- **Data Validation:** Catch missing fields early, provide clear error messages
- **Audit Trail:** "Show me the data that was used for this document"

---

### Proposed Implementation Approach

#### Phase 1: Build Data Service (Epic 3.5)

**New Story: "3.5: Implement Project Data Service"**

**Acceptance Criteria:**
- AC-1: Data service fetches all project data from 4 Riskuity endpoints
- AC-2: Data transformer converts Riskuity responses to canonical JSON schema
- AC-3: JSON schema validated (all required fields present, data types correct)
- AC-4: JSON file stored in S3 with project_id and timestamp in filename
- AC-5: Data service returns S3 path to JSON file
- AC-6: Retry logic and error handling for Riskuity API failures

**JSON Schema Example:**
```json
{
  "project_id": "RSKTY-12345",
  "generated_at": "2025-03-15T14:32:00Z",
  "data_version": "1.0",
  "project": {
    "recipient_name": "Massachusetts Bay Transportation Authority",
    "recipient_acronym": "MBTA",
    "recipient_id": "1057",
    "recipient_city_state": "Boston, MA",
    "recipient_website": "https://www.mbta.com",
    "region_number": 1,
    "review_type": "Triennial Review",
    "site_visit_start_date": "2025-03-10",
    "site_visit_end_date": "2025-03-14",
    "report_date": "2025-04-15"
  },
  "contractor": {
    "name": "Milligan & Company",
    "city_state": "Philadelphia, PA",
    "lead_reviewer_name": "Scott W. Schilt",
    "lead_reviewer_phone": "215-496-9100 ext 183",
    "lead_reviewer_email": "sschilt@milligancpa.com"
  },
  "fta_program_manager": {
    "name": "John Smith",
    "phone": "(202) 555-0123",
    "email": "john.smith@dot.gov",
    "office_city_state": "Washington, DC"
  },
  "assessments": [
    {
      "review_area": "Legal",
      "finding": "ND",
      "deficiency_code": null,
      "description": null
    },
    ...
  ],
  "erf_items": [],
  "metadata": {
    "has_deficiencies": false,
    "deficiency_count": 0,
    "erf_count": 0,
    "data_completeness": "100%"
  }
}
```

#### Phase 2: Update Template Engine to Consume JSON

**Update Story 1.5: DocumentGenerator**

**Changes:**
- Add parameter: `data_source` (accepts Riskuity API or S3 JSON path)
- If JSON path provided: Load JSON from S3
- If Riskuity API: Fall back to direct API calls (backward compatibility)
- Template receives same data structure either way

#### Phase 3: Implement RIR Template (Epic 4)

**New Epic: "Epic 4: Recipient Information Request Template"**

**Stories:**
- 4.1: Implement RIR template with docxtpl
- 4.2: Add review type conditional logic (CL-RIR-1)
- 4.3: Integrate RIR with data service
- 4.4: End-to-end testing (data fetch → JSON → RIR generation)

---

### API Endpoint Design for Data Service

**New Endpoint:**
```
POST /api/v1/projects/{project_id}/data
```

**Purpose:** Fetch and cache all project data from Riskuity

**Request Body:**
```json
{
  "force_refresh": false,  // Optional: bypass cache, fetch fresh data
  "include_assessments": true,
  "include_erf": true,
  "include_surveys": false
}
```

**Response:**
```json
{
  "project_id": "RSKTY-12345",
  "data_file_url": "s3://cortap-rpt-data/RSKTY-12345/2025-03-15T14:32:00_project-data.json",
  "generated_at": "2025-03-15T14:32:00Z",
  "data_version": "1.0",
  "expires_at": "2025-03-15T15:32:00Z",  // 1-hour TTL
  "completeness": {
    "missing_critical_fields": [],
    "missing_optional_fields": ["recipient_website", "erf_items"],
    "data_quality_score": 95
  }
}
```

**Flow:**
1. Client calls `/projects/{id}/data`
2. Data service checks if cached JSON exists and is fresh (< 1 hour old)
3. If cached: Return S3 path immediately
4. If not cached: Fetch from Riskuity, transform, save to S3, return path
5. Client uses S3 path to generate any template(s)

---

## Comparison: RIR vs Draft Audit Report

| Characteristic | Draft Audit Report | Recipient Information Request |
|----------------|-------------------|-------------------------------|
| **Template Complexity** | HIGH | LOW |
| **Field Count** | 50+ | 15 |
| **Conditional Logic Patterns** | 9 complex patterns | 1 simple pattern |
| **Tables** | 23-row deficiency table | None |
| **Dynamic Content** | Extensive | Minimal |
| **Implementation Priority** | MEDIUM (complex logic) | HIGH (quick win) |
| **Riskuity Dependency** | HIGH (many fields) | MEDIUM (fewer fields) |
| **Testing Complexity** | HIGH | LOW |
| **Development Effort** | 5-7 days | 1-2 days |

**Strategic Recommendation:** Implement RIR FIRST as proof-of-concept, then tackle Draft Audit Report.

---

## Implementation Roadmap

### Recommended Sequence (Revised)

**Epic 1: Foundation & Template Engine** ✅ (Already started)
- 1.1: Project Setup
- 1.2: Logging
- 1.3: Exceptions
- 1.4: POC Template Validation
- 1.5: DocumentGenerator
- 1.6: Grammar Helpers

**Epic 3.5: Project Data Service** 🆕 (NEW - Insert before Epic 2)
- 3.5.1: Design JSON schema for project data
- 3.5.2: Implement Riskuity API client (fetch from 4 endpoints)
- 3.5.3: Implement data transformer (Riskuity → JSON)
- 3.5.4: Implement S3 storage for JSON files
- 3.5.5: Add caching and TTL logic
- 3.5.6: Add data validation and completeness checks
- 3.5.7: Create `/projects/{id}/data` API endpoint

**Epic 4: RIR Template** 🆕 (NEW - Simpler than Epic 2)
- 4.1: Convert RIR template to docxtpl format
- 4.2: Implement review type conditional logic (CL-RIR-1)
- 4.3: Create RIR template data model (15 fields)
- 4.4: Integrate RIR with data service (JSON → template)
- 4.5: Add RIR generation endpoint
- 4.6: End-to-end testing with real Riskuity data

**Epic 2: Conditional Logic** (DEFERRED - tackle after RIR proves pattern)
- 2.1-2.8: All complex conditional logic for Draft Audit Report

**Epic 3: Riskuity Integration** (MERGED into Epic 3.5)
- No longer needed as separate epic

**Rationale:**
- RIR is simpler → faster win, validates architecture
- Data service unlocks both RIR and Draft Report
- Learn from RIR implementation before tackling complex Draft Report logic

---

## Success Criteria

**RIR Template is considered COMPLETE when:**

1. ✅ All 15 merge fields populated correctly from Riskuity data
2. ✅ Review type conditional logic works (3 variations)
3. ✅ Generated document preserves Word formatting exactly
4. ✅ Data service successfully fetches and caches project data
5. ✅ JSON schema validated and complete
6. ✅ End-to-end generation takes < 30 seconds
7. ✅ Auditor can generate RIR from Riskuity UI with one click

---

## Next Steps

**Immediate Actions:**

1. **Add RIR-specific questions to Riskuity inquiry** (Questions 13-17 above)
2. **Review proposed data service architecture with team**
3. **Decide: Adopt data service pattern? (Recommendation: YES)**
4. **Update PRD to include RIR template and data service epic**
5. **Revise epic sequencing: Epic 3.5 (Data Service) → Epic 4 (RIR) → Epic 2 (Conditional Logic)**

**Design Decisions Needed:**

- **JSON Schema Design:** Finalize structure based on Riskuity API responses
- **Caching Strategy:** TTL duration (1 hour? 24 hours? Configurable?)
- **Storage Location:** S3 bucket structure, lifecycle policies
- **Error Handling:** What happens if Riskuity data incomplete? Fail generation or use defaults?

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-13 | Mary (Business Analyst) | Initial analysis of RIR template + data service architecture proposal |

---

**END OF DOCUMENT**
