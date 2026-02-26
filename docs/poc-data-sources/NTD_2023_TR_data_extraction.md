# Data Extraction: Norwalk Transit District (NTD) FY2023 Triennial Review

**Source:** `NTD 2023 TR Final Report.pdf`
**Extracted:** 2025-11-19
**Purpose:** Mock JSON data for Epic 1.5 POC

---

## Project Metadata

| Field | Value |
|-------|-------|
| Recipient Name | Norwalk Transit District |
| Recipient Acronym | NTD |
| Recipient ID | 1339 |
| City, State | Norwalk, Connecticut |
| Region Number | 1 |
| Review Type | Triennial Review |
| Fiscal Year | 2023 |

---

## Review Dates & Events

| Field | Value |
|-------|-------|
| Scoping Meeting Date | February 24 & 27, 2023 |
| Site Visit Start Date (Entrance Conference) | March 28, 2023 |
| Site Visit End Date (Exit Conference) | May 15, 2023 |
| Exit Conference Format | virtual |
| Final Report Date | July 11, 2023 |

---

## FTA Contact Information

| Field | Value |
|-------|-------|
| FTA Title | Deputy Regional Administrator |
| FTA Name | Michelle Muhlanger |
| Phone | 617-494-2630 |
| Email | michelle.muhlanger@dot.gov |
| Region | Region 1 (I) |

---

## Contractor Information

| Field | Value |
|-------|-------|
| Contractor Firm | Qi Tech, LLC |
| Reviewer Name | Gwen Larson |
| Phone | 920-746-4595 |
| Email | gwen_larson@qitechllc.com |

---

## Assessment Results (23 Review Areas)

| # | Review Area | Finding | Deficiency Code | Description | Corrective Action | Due Date |
|---|-------------|---------|-----------------|-------------|-------------------|----------|
| 1 | Legal | ND | | | | |
| 2 | Financial Management and Capacity | ND | | | | |
| 3 | Technical Capacity – Award Management | ND | | | | |
| 4 | Technical Capacity – Program Management & Subrecipient Oversight | NA | | | | |
| 5 | Technical Capacity – Project Management | ND | | | | |
| 6 | Transit Asset Management | ND | | | | |
| 7 | Satisfactory Continuing Control | ND | | | | |
| 8 | Maintenance | ND | | | | |
| 9 | Procurement | ND | | | | |
| 10 | Disadvantaged Business Enterprise (DBE) | D | DBE12-2 | Insufficient documentation of monitoring DBE work | NTD must submit to the FTA Office of Civil Rights (TCR) evidence that it has implemented its DBE monitoring process to ensure that DBEs are actually performing the stated work. | December 31, 2023 |
| 11 | Title VI | ND | | | | |
| 12 | Americans with Disabilities Act (ADA) – General | ND | | | | |
| 13 | ADA – Complementary Paratransit | ND | | | | |
| 14 | Equal Employment Opportunity | ND | | | | |
| 15 | School Bus | ND | | | | |
| 16 | Charter Bus | ND | | | | |
| 17 | Drug Free Workplace Act | ND | | | | |
| 18 | Drug and Alcohol Program | ND | | | | |
| 19 | Section 5307 Program Requirements | ND | | | | |
| 20 | Section 5310 Program Requirements | NA | | | | |
| 21 | Section 5311 Program Requirements | NA | | | | |
| 22 | Public Transportation Agency Safety Plan (PTASP) | ND | | | | |
| 23 | Cybersecurity | ND | | | | |

**Finding Legend:** D = Deficient, ND = Not Deficient, NA = Not Applicable

---

## Deficiency Summary

**Total Deficiencies:** 1

**Deficiency Details:**

### Deficiency 1: DBE12-2
- **Review Area:** Disadvantaged Business Enterprise (DBE)
- **Code:** DBE12-2
- **Description:** Insufficient documentation of monitoring DBE work. Per 49 CFR 26.37(b), a recipient's DBE program must include a monitoring and enforcement mechanism to ensure that work committed to DBEs at contract award is actually performed by the DBEs to which the work was committed. This mechanism must include a written certification that the recipient reviewed contracting records and monitored work sites for this purpose. NTD implemented a project during the review period to replace the fuel tank, construct a new fuel island, and to make service lane improvements, which included work completed by a DBE. However, since the DBE Liaison Officer was out on an extended medical leave during this project's completion, it was not monitored for DBE participation, as stated in the recipient's DBE program plan.
- **Corrective Action:** By December 31, 2023, NTD must submit to the FTA Office of Civil Rights (TCR) evidence that it has implemented its DBE monitoring process to ensure that DBEs are actually performing the stated work.
- **Due Date:** December 31, 2023

---

## Enhanced Review Focus (ERF)

**ERF Count:** 0 (No ERF mentioned in report)

---

## Subrecipient Information

**Reviewed Subrecipients:** No (Section 4: Technical Capacity - Program Management & Subrecipient Oversight marked as NA)

---

## Derived Fields (for JSON)

| Field | Value | Calculation |
|-------|-------|-------------|
| has_deficiencies | true | 1 deficiency found |
| deficiency_count | 1 | Count of "D" findings |
| deficiency_areas | "Disadvantaged Business Enterprise" | List of review areas with "D" finding |
| erf_count | 0 | No ERF mentioned |
| erf_areas | "" | No ERF areas |
| reviewed_subrecipients | false | Subrecipient oversight marked NA |

---

## Additional Notes

- **COVID-19 Context:** Review was conducted virtually due to COVID-19 Public Health Emergency
- **First-time Operating Assistance:** NTD received operating assistance for the first time using COVID-19 relief funds (CARES Act)
- **No Repeat Deficiencies:** There were no repeat deficiencies from the FY 2019 Triennial Review
- **Review Period:** Concentrated on procedures since 2019 Triennial Review, extended to earlier periods as needed

---

## Recipient Description (Background Info)

- **Established:** 1974 (began operation in 1978)
- **Service Area Population:** 119,309 (Norwalk and Westport primary); 957,419 (Stamford/Norwalk UZA)
- **Fleet Size:** 39 directly operated vehicles (fixed-route), 35 cutaway buses (paratransit), 13 contractor vehicles
- **Routes:** 11 bus routes (8 Saturday, 2 Sunday), 4 Metro North shuttles, microtransit (Wheels 2U)
- **Fares:** $1.75 adult, $0.85 reduced (seniors/disabled), $3.50 ADA paratransit

---

**POC Use Case:** This report represents a **Triennial Review with 1 deficiency** - good for testing Pattern 2 (Deficiency Detection), Pattern 6 (Deficiency Table with mostly ND rows), and Pattern 8 (Dynamic Counts with small numbers).
