# Draft Report Template - Data Source Mapping

**Purpose:** Identify data sources for all fields in the Draft Report template to determine what needs to be collected, stored in Riskuity, or obtained through other means.

**Audience:** Development Team & Business Team

**Last Updated:** 2025-11-21

---

## Executive Summary

The Draft Report template requires **65+ distinct data fields** organized into 7 major categories:

| Category | Field Count | Current Source | Action Required |
|----------|-------------|----------------|-----------------|
| Project/Review Metadata | 15 | Riskuity | ✅ Available |
| Recipient Information | 10 | Riskuity | ⚠️ Some fields missing |
| FTA Personnel | 4 | Manual/Lookup | 🔴 Need source |
| Regional Officer | 2 | Manual/Lookup | 🔴 Need source |
| Contractor Information | 4 | Manual/Contract | 🔴 Need source |
| Assessment Results | 23 areas × 7 fields | Riskuity | ⚠️ Needs enhancement |
| Operational Details | 15+ | Unknown | 🔴 Need to determine |

**Key Findings:**
- ✅ **30-40% of fields** are likely already in Riskuity (project metadata, recipient basics, assessment findings)
- ⚠️ **20-30% of fields** exist in Riskuity but may need format/structure changes
- 🔴 **30-40% of fields** have unknown sources or require new data collection

---

## Field Inventory by Section

### Section I: Cover Letter

| Field | Description | Template Location | Current Source | Proposed Source | Priority | Notes |
|-------|-------------|-------------------|----------------|-----------------|----------|-------|
| **Regional Office Header** | Full address block for FTA regional office | Letter header | Unknown | **Lookup Table** | HIGH | Need regional office addresses for all 10 FTA regions |
| **Recipient Salutation** | Mr./Ms./Dr. | Letter greeting | Unknown | **Recipient Profile** | MEDIUM | Add to Riskuity recipient record |
| **Recipient Last Name** | Contact person last name | Letter greeting | Riskuity | Riskuity | LOW | Extract from contact name |
| **Recipient Full Address** | Complete mailing address | Letter recipient block | Riskuity (partial) | **Enhance Riskuity** | HIGH | Need street address, not just city/state |
| **Report Date** | Date of report issuance | Letter date line | Riskuity | Riskuity | LOW | Already tracked |
| **Review Type** | Triennial/State Management/Combined | Throughout letter | Riskuity | Riskuity | LOW | Already tracked |
| **Fiscal Year** | FY of review | Throughout letter | Riskuity | Riskuity | LOW | Already tracked |
| **Deficiency Count** | Number of deficiencies found | Letter body | Riskuity (derived) | Riskuity | LOW | Calculate from assessments |
| **Deficiency Areas** | List of areas with deficiencies | Letter body | Riskuity (derived) | Riskuity | LOW | Aggregate from assessments |
| **ERF Count** | Number of Enhanced Review Focus areas | Letter body (conditional) | Unknown | **New Field in Riskuity** | MEDIUM | Need to track ERF designation |
| **ERF Areas** | List of ERF areas | Letter body (conditional) | Unknown | **New Field in Riskuity** | MEDIUM | Need to track which areas are ERF |
| **Has Post-Visit Responses** | Flag: recipient responded after visit | Letter body (conditional) | Unknown | **New Field in Riskuity** | MEDIUM | Track response submission |
| **Report Status** | Draft or Final | Letter body (conditional) | Riskuity | Riskuity | LOW | Workflow status |
| **FTA Program Manager Name** | Name of FTA PM | Closing paragraph | Unknown | **Lookup/Survey** | HIGH | Need FTA staff assignment |
| **FTA Program Manager Title** | Title of FTA PM | Closing paragraph | Unknown | **Lookup/Survey** | HIGH | From FTA staff record |
| **FTA Program Manager Phone** | Phone of FTA PM | Closing paragraph | Unknown | **Lookup/Survey** | HIGH | From FTA staff record |
| **FTA Program Manager Email** | Email of FTA PM | Closing paragraph | Unknown | **Lookup/Survey** | HIGH | From FTA staff record |
| **Contractor Lead Reviewer Name** | Name of lead reviewer | Closing paragraph | Unknown | **Contract/Survey** | HIGH | From contractor assignment |
| **Contractor Lead Reviewer Phone** | Phone of lead reviewer | Closing paragraph | Unknown | **Contract/Survey** | HIGH | From contractor record |
| **Contractor Lead Reviewer Email** | Email of lead reviewer | Closing paragraph | Unknown | **Contract/Survey** | HIGH | From contractor record |
| **Regional Officer Name** | Name of Regional Administrator | Signature block | Unknown | **Lookup Table** | HIGH | By region |
| **Regional Officer Title** | Title (usually "Regional Administrator") | Signature block | Unknown | **Lookup Table** | HIGH | By region |

**Section I Summary:**
- **Total Fields:** 21
- **Riskuity (existing):** 7 (33%)
- **Riskuity (needs enhancement):** 4 (19%)
- **New data needed:** 10 (48%)

---

### Section II: Cover Page & Executive Summary

| Field | Description | Template Location | Current Source | Proposed Source | Priority | Notes |
|-------|-------------|-------------------|----------------|-----------------|----------|-------|
| **Fiscal Year** | FY of review | Cover page | Riskuity | Riskuity | LOW | Duplicate from Section I |
| **Review Type** | TR/SMR/Combined | Cover page | Riskuity | Riskuity | LOW | Duplicate from Section I |
| **Recipient Name** | Full legal name | Cover page | Riskuity | Riskuity | LOW | Duplicate from Section I |
| **Recipient Acronym** | Abbreviation (if any) | Cover page | Riskuity | Riskuity | LOW | May need to add |
| **Recipient City/State** | Location | Cover page | Riskuity | Riskuity | LOW | Duplicate from Section I |
| **Recipient ID** | FTA-assigned ID number | Cover page | Riskuity | Riskuity | LOW | Need to capture |
| **Region Number** | FTA region (1-10) | Cover page | Riskuity | Riskuity | LOW | May need to add |
| **Contractor Name** | Contracting firm name | Cover page | Unknown | **Contract/Survey** | HIGH | From contract |
| **Desk Review Date** | Date of desk review | Cover page dates | Riskuity | **Enhance Riskuity** | MEDIUM | Add to review milestones |
| **Scoping Meeting Date** | Date of scoping meeting | Cover page dates | Riskuity | **Enhance Riskuity** | MEDIUM | Add to review milestones |
| **Site Visit Start Date** | First day of site visit | Cover page dates | Riskuity | Riskuity | LOW | Likely already tracked |
| **Site Visit End Date** | Last day of site visit | Cover page dates | Riskuity | Riskuity | LOW | Likely already tracked |
| **Exit Conference Date** | Date of exit conference | Cover page dates | Riskuity | Riskuity | LOW | Likely already tracked |
| **Exit Conference Format** | Virtual or In-Person | Process section | Unknown | **New Field in Riskuity** | MEDIUM | Track format choice |
| **Report Date** | Date report issued | Cover page dates | Riskuity | Riskuity | LOW | Duplicate from Section I |
| **COVID-19 Context Flag** | Was COVID context included? | Executive summary | Unknown | **New Field in Riskuity** | LOW | Historical context flag |
| **No Repeat Deficiencies Flag** | Are there repeat deficiencies? | Executive summary | Riskuity (derived) | Riskuity | LOW | Compare to prior review |
| **Repeat Deficiency Count** | Number of repeat deficiencies | Executive summary | Riskuity (derived) | Riskuity | LOW | Compare to prior review |
| **Repeat Deficiency Areas** | List of repeat areas | Executive summary | Riskuity (derived) | Riskuity | LOW | Compare to prior review |
| **Previous Review Year** | Year of last review | Executive summary | Riskuity | Riskuity | LOW | Review history |

**Section II Summary:**
- **Total Fields:** 20
- **Riskuity (existing):** 10 (50%)
- **Riskuity (needs enhancement):** 6 (30%)
- **New data needed:** 4 (20%)

---

### Section III: Review Background & Process

| Field | Description | Template Location | Current Source | Proposed Source | Priority | Notes |
|-------|-------------|-------------------|----------------|-----------------|----------|-------|
| **Review Type** | TR/SMR/Combined | Background paragraphs | Riskuity | Riskuity | LOW | Duplicate |
| **Previous Review Year** | Year of last review | Background paragraph | Riskuity | Riskuity | LOW | Duplicate |
| **Process Dates** | Array of 8 milestone dates with descriptions | Process dates table | Riskuity | **Enhance Riskuity** | HIGH | Need structured date tracking |
| **Subrecipients Reviewed (5307)** | List of 5307 subrecipients reviewed | Process paragraph | Unknown | **Survey/Review Notes** | MEDIUM | Not always applicable |
| **Subrecipients Reviewed (5310)** | List of 5310 subrecipients reviewed | Process paragraph | Unknown | **Survey/Review Notes** | MEDIUM | Not always applicable |
| **Subrecipients Reviewed (5311)** | List of 5311 subrecipients reviewed | Process paragraph | Unknown | **Survey/Review Notes** | MEDIUM | Not always applicable |
| **Contractors Reviewed** | List of contractors/lessees reviewed | Process paragraph | Unknown | **Survey/Review Notes** | MEDIUM | Not always applicable |

**Section III Summary:**
- **Total Fields:** 7
- **Riskuity (existing):** 2 (29%)
- **Riskuity (needs enhancement):** 1 (14%)
- **New data needed:** 4 (57%)

---

### Section IV: Recipient Description

| Field | Description | Template Location | Current Source | Proposed Source | Priority | Notes |
|-------|-------------|-------------------|----------------|-----------------|----------|-------|
| **Organization Description** | Narrative description of recipient organization | Organization section | Unknown | **Survey** | HIGH | Free-text organizational overview |
| **Open Awards (Array)** | List of active FTA awards | Awards table | Unknown | **FTA TrAMS** | HIGH | Pull from FTA systems? |
| - Award Number | Grant/award number | Table column | Unknown | **FTA TrAMS** | HIGH | |
| - Award Amount | Dollar amount | Table column | Unknown | **FTA TrAMS** | HIGH | |
| - Year Executed | Year awarded | Table column | Unknown | **FTA TrAMS** | HIGH | |
| - Description | Award purpose/description | Table column | Unknown | **FTA TrAMS** | HIGH | |
| **Supplemental Awards** | Award numbers for supplemental/COVID funds | Paragraph | Unknown | **FTA TrAMS** | MEDIUM | Special funding |
| **First Time Operating Assistance** | Flag: first time receiving operating $ | Paragraph | Unknown | **Survey/FTA Records** | MEDIUM | Historical flag |
| **Projects Completed (Array)** | List of recently completed projects | Bullet list | Unknown | **Survey** | MEDIUM | Narrative list |
| **Projects Ongoing (Array)** | List of current projects | Bullet list | Unknown | **Survey** | MEDIUM | Narrative list |
| **Projects Future (Array)** | List of planned projects | Bullet list | Unknown | **Survey** | LOW | Narrative list |

**Section IV Summary:**
- **Total Fields:** 11 distinct fields (+ 3 arrays with sub-fields)
- **Riskuity (existing):** 0 (0%)
- **Riskuity (needs enhancement):** 0 (0%)
- **New data needed:** 11 (100%)

**Note:** This section is largely narrative and may be best collected via **pre-review survey** or pulled from **FTA TrAMS system** (for awards).

---

### Section V: Results of the Review (23 Assessment Areas)

Each of the 23 assessment areas requires the following fields:

| Field | Description | Template Location | Current Source | Proposed Source | Priority | Notes |
|-------|-------------|-------------------|----------------|-----------------|----------|-------|
| **Review Area** | Name of assessment area (e.g., "Legal") | Section heading | Riskuity | Riskuity | LOW | Fixed list of 23 |
| **Finding** | D (Deficiency), ND (No Deficiency), NA (Not Applicable) | Finding paragraph | Riskuity | Riskuity | HIGH | Core assessment result |
| **Deficiency Code** | FTA deficiency code (e.g., "DBE12-2") | Deficiency details | Riskuity | Riskuity | HIGH | If deficiency exists |
| **Deficiency Description** | Detailed description of deficiency | Deficiency details | Riskuity | Riskuity | HIGH | Free-text field |
| **Corrective Action** | Required corrective action and schedule | Deficiency details | Riskuity | Riskuity | HIGH | Free-text field |
| **Due Date** | Corrective action due date | Deficiency details | Riskuity | Riskuity | HIGH | Date field |
| **Date Closed** | Date deficiency was closed (if applicable) | Deficiency details | Riskuity | Riskuity | MEDIUM | Date field |

**23 Assessment Areas:**
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

**Section V Summary:**
- **Total Fields:** 7 fields × 23 areas = 161 potential data points (but most assessments have ND finding with no details)
- **Typical review:** ~3-5 deficiencies, so ~21-35 actual data points
- **Riskuity (existing):** Likely 100% - this is the core of what Riskuity tracks
- **Enhancements needed:**
  - Ensure all 23 areas are in system
  - Support multiple deficiencies per area
  - Track deficiency codes
  - Track corrective action schedules

---

### Section VI: Attendees

Attendees are organized into 5 categories, each requiring:

| Field | Description | Template Location | Current Source | Proposed Source | Priority | Notes |
|-------|-------------|-------------------|----------------|-----------------|----------|-------|
| **Recipient Attendees** | Array of recipient staff who attended | Attendees table | Unknown | **Survey/Meeting Notes** | MEDIUM | Captured during review |
| - Name | Full name | Table column | Unknown | **Survey** | MEDIUM | |
| - Title | Job title | Table column | Unknown | **Survey** | MEDIUM | |
| - Phone | Phone number | Table column | Unknown | **Survey** | MEDIUM | |
| - Email | Email address | Table column | Unknown | **Survey** | MEDIUM | |
| **Subrecipient Attendees** | Array of subrecipient staff (if applicable) | Attendees table | Unknown | **Survey/Meeting Notes** | LOW | Conditional |
| **Contractor/Lessee Attendees** | Array of contractor staff (if applicable) | Attendees table | Unknown | **Survey/Meeting Notes** | LOW | Conditional |
| **FTA Attendees** | Array of FTA staff who attended | Attendees table | Unknown | **Survey/Meeting Notes** | MEDIUM | From FTA team |
| **Contractor Attendees** | Array of contractor review team | Attendees table | Unknown | **Contract/Meeting Notes** | MEDIUM | From contractor |

**Section VI Summary:**
- **Total Fields:** 5 arrays × 4 sub-fields = 20 field definitions
- **Actual data:** Variable based on attendance (typically 3-5 recipient, 2-3 FTA, 1-2 contractor)
- **Riskuity (existing):** 0%
- **Proposed Source:** **Meeting attendance list** collected during review

---

### Section VII: Appendices

*To be determined - likely contains references to attachments/supporting documents*

**Section VII Summary:**
- **Assessment needed:** Template section not yet analyzed
- **Likely minimal data:** References to external documents

---

## Data Source Recommendations

### 1. Riskuity (Existing) - ~30%
**Fields already tracked in Riskuity:**
- Recipient basic info (name, city/state, ID)
- Review metadata (type, dates, status)
- Assessment results (findings, deficiencies, corrective actions)
- Review history (prior reviews, repeat deficiencies)

**Action:** ✅ Use existing Riskuity fields

---

### 2. Riskuity (Enhancement Needed) - ~25%
**Fields that should be in Riskuity but may need structure changes:**

#### High Priority Additions:
- [ ] **Process milestone dates** (8 structured date fields with descriptions)
- [ ] **ERF tracking** (flag + areas designated as ERF)
- [ ] **Exit conference format** (virtual/in-person flag)
- [ ] **Post-visit response tracking** (flag indicating recipient responded)
- [ ] **Recipient contact details** (salutation, full address including street)
- [ ] **Region number** (1-10, for FTA region)

#### Medium Priority Additions:
- [ ] **Desk review date** (separate from site visit)
- [ ] **Scoping meeting date** (separate from site visit)
- [ ] **Multiple deficiencies per assessment area** (if not already supported)
- [ ] **Deficiency closure dates** (if not already tracked)

**Action:** 🔨 **Enhance Riskuity data model** with above fields

---

### 3. Lookup Tables - ~10%
**Reference data that should be in lookup tables:**

- [ ] **Regional office information** (10 regions)
  - Office address blocks
  - Regional Administrator name and title
  - Regional office phone/email

- [ ] **FTA Program Manager assignments**
  - By recipient or region
  - Name, title, phone, email
  - *Alternative: Could be survey field if assignments vary*

**Action:** 📋 **Create reference/lookup tables** or integrate with FTA staff directory

---

### 4. Contract/Project Data - ~5%
**Fields from contractor/project setup:**

- [ ] **Contractor firm name**
- [ ] **Lead reviewer name**
- [ ] **Lead reviewer contact info** (phone, email)

**Action:** 📑 **Pull from contract records** or collect during project setup

---

### 5. Survey/Recipient Input - ~20%
**Fields best collected from recipient before/during review:**

#### Pre-Review Survey:
- [ ] Organization description (narrative)
- [ ] Projects completed (narrative list)
- [ ] Projects ongoing (narrative list)
- [ ] Projects future (narrative list)
- [ ] Subrecipients/contractors reviewed (if applicable)

#### During Review:
- [ ] Attendees list (all categories)
  - Names, titles, phone, email

**Action:** 📝 **Create pre-review survey** and **meeting attendance form**

---

### 6. FTA TrAMS System - ~10%
**Fields that may be available from FTA systems:**

- [ ] Open awards (award number, amount, year, description)
- [ ] Supplemental awards
- [ ] First-time operating assistance flag

**Action:** 🔌 **Investigate FTA TrAMS API/data export** options

**Alternative:** If API not available, include in pre-review survey

---

## Recommended Implementation Approach

### Phase 1: Core Data (Riskuity Enhancements) - HIGH PRIORITY
**Timeline:** Sprint 1-2

1. Add ERF tracking fields
2. Add process milestone dates structure
3. Add exit conference format flag
4. Add post-visit response tracking
5. Enhance recipient contact details
6. Add region number field
7. Ensure multiple deficiencies per area supported

**Impact:** Enables ~75% of template fields

---

### Phase 2: Reference Data - MEDIUM PRIORITY
**Timeline:** Sprint 2-3

1. Create regional office lookup table
2. Add FTA Program Manager assignments (or decide on survey approach)
3. Create contractor/reviewer data collection process

**Impact:** Enables ~10% of template fields

---

### Phase 3: External Data Collection - MEDIUM PRIORITY
**Timeline:** Sprint 3-4

1. Design pre-review survey (organization description, projects, awards)
2. Create meeting attendance form
3. Determine FTA TrAMS integration approach

**Impact:** Enables remaining ~15% of template fields

---

## Data Collection Workflow

```
Review Scheduled
      ↓
1. System pulls recipient data from Riskuity
      ↓
2. System assigns FTA PM and contractor (lookup/manual)
      ↓
3. Pre-review survey sent to recipient
   - Organization description
   - Projects (completed, ongoing, future)
   - Open awards (if not from TrAMS)
      ↓
4. Desk review / Scoping meeting dates captured
      ↓
5. Site visit conducted
   - Attendance tracked (form)
   - Assessments performed (Riskuity)
      ↓
6. Exit conference
   - Format tracked (virtual/in-person)
   - Date recorded
      ↓
7. Post-visit responses (optional)
   - Flag tracked if received
      ↓
8. Report generated
   - All data merged from Riskuity, surveys, lookups
      ↓
Draft Report Produced
```

---

## Open Questions for Discussion

### Business Team Questions:

1. **FTA TrAMS Integration:** Can we get award data from FTA TrAMS, or should we collect via survey?

2. **FTA Staff Assignments:** Should FTA PM assignments be:
   - Stored in Riskuity (requires maintenance)
   - Lookup by region (assumes consistent assignments)
   - Collected via survey/manual entry per review

3. **Pre-Review Survey Timing:** When should recipients receive the survey?
   - At review scheduling?
   - After RIR (Recipient Information Request)?
   - 30 days before site visit?

4. **Projects Lists (Completed/Ongoing/Future):** Do we need these in Riskuity permanently, or just for report generation?

5. **Attendees Tracking:** Should we create a formal attendance tracking module, or just a simple form/spreadsheet during the review?

### Development Team Questions:

1. **Data Model Changes:** Are the recommended Riskuity enhancements feasible? Any concerns?

2. **API Access:** Can we investigate FTA TrAMS API access for award data?

3. **Survey Tool:** What tool should we use for pre-review surveys?
   - Built into app?
   - External (Google Forms, SurveyMonkey, etc.)?

4. **Lookup Table Maintenance:** Who will maintain regional office data and FTA PM assignments?

5. **Multiple Deficiencies:** Does Riskuity currently support multiple deficiencies per assessment area?

---

## Summary Statistics

| Data Source | Field Count | Percentage | Priority | Implementation |
|-------------|-------------|------------|----------|----------------|
| Riskuity (existing) | ~25 | 30% | ✅ Use as-is | None |
| Riskuity (enhance) | ~20 | 25% | 🔨 High | Phase 1 |
| Lookup tables | ~8 | 10% | 📋 Medium | Phase 2 |
| Contract/project | ~4 | 5% | 📑 Medium | Phase 2 |
| Survey/recipient | ~16 | 20% | 📝 Medium | Phase 3 |
| FTA TrAMS | ~8 | 10% | 🔌 TBD | Phase 3 |
| **TOTAL** | **~81** | **100%** | | |

**Key Insight:**
- **30% ready now** (use existing Riskuity)
- **25% requires Riskuity enhancements** (straightforward additions)
- **45% requires new data collection** (surveys, lookups, integrations)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-21
**Next Steps:** Schedule discussion with business and development teams to finalize data source decisions
