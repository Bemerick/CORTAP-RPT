# Riskuity Data Mapping Analysis
**Project: CORTAP FY26 Assessment Test (ID: 33)**
**Date: 2026-02-11**

## Summary

Successfully retrieved 494 project controls with assessments from Riskuity API for test project 33.

## API Endpoint

**Working Endpoint:**
```
GET https://api.riskuity.com/projects/project_controls/{project_id}?limit=500&offset=0
```

**Response Structure:**
```json
{
  "items": [...],
  "total": 494,
  "offset": 0,
  "limit": 500
}
```

## Data Structure

### Project Control Object
Each project control contains:
- `id`: Project control ID
- `control`: Control definition with name, description
- `assessment`: Assessment data (status, comments, etc.)
- `control_family`: Family grouping (currently null for all)
- `control_status`: Status information
- Other metadata fields

### Assessment Object (embedded in project_control)
```json
{
  "id": "4572",
  "name": "Assess Control 'LEGAL : L2' on Project 'CORTAP FY26 Assessment Test'",
  "status": "Complete",  // or "Not Started"
  "description": "...",
  "comments": "Tested L2 - Failed",
  "is_assessment_confirmed": "No",
  "project_control": {"id": "4311"}
}
```

## Control Distribution

### By Review Area (Control Name Prefix)
19 review area categories identified:

| Review Area | Count |
|-------------|-------|
| PROCUREMENT | 71 |
| SATISFACTORY CONTINUING CONTROL | 60 |
| FINANCIAL MANAGEMENT | 55 |
| TECHNICAL CAPACITY – AWARD MANAGEMENT | 35 |
| TRANSIT ASSET MANAGEMENT | 33 |
| TECHNICAL CAPACITY – PROGRAM MANAGEMENT | 30 |
| MAINTENANCE | 21 |
| DRUG AND ALCOHOL PROGRAM | 18 |
| TECHNICAL CAPACITY – PROJECT MANAGEMENT | 17 |
| PUBLIC TRANSPORTATION AGENCY SAFETY PLAN | 14 |
| CHARTER BUS | 11 |
| LEGAL | 11 |
| DRUG FREE WORKPLACE ACT | 7 |
| SCHOOL BUS | 7 |
| PTASP | 6 |
| ADA COMPLEMENTARY PARATRANSIT | 5 |
| ADA GENERAL | 4 |
| CYBERSECURITY | 2 |
| FINANCIAL MANAGEMENT AND CAPACITY | 1 |

**Total with prefix:** 408 controls
**Total controls:** 494 controls
**Missing prefix:** 86 controls (need investigation)

### By Assessment Status
- **Not Started:** 492 assessments
- **Complete:** 2 assessments

## Mapping Strategy: Riskuity → JSON

### Challenge
- **Source:** 494 individual assessments (one per control)
- **Target:** 23 consolidated review areas in JSON

### Proposed Mapping Approach

1. **Group by Control Name Prefix**
   - Extract prefix from `control.name` (e.g., "LEGAL" from "LEGAL : L2")
   - Map multiple controls to single review area

2. **Consolidate Status**
   - If ANY control is "Complete" → review area shows progress
   - Aggregate completion percentage across all controls in area

3. **Combine Comments/Findings**
   - Collect all assessment comments for controls in area
   - Filter out empty/null comments
   - Present as list of findings per review area

4. **Review Area Mapping**
   Need to map 19 Riskuity categories → 23 JSON review areas:
   - Some may be 1:1 (e.g., "PROCUREMENT" → "Procurement")
   - Some may need to be split or combined
   - Need to handle 86 controls without prefix

## Next Steps

1. ✅ Verify API endpoint and authentication
2. ✅ Fetch all 494 project controls
3. ✅ Analyze control distribution and naming patterns
4. ⏳ Create mapping table: Riskuity prefix → JSON review area name
5. ⏳ Implement transformation logic in RiskuityDataService
6. ⏳ Test with project 33 data
7. ⏳ Validate against expected 23 review areas in JSON template

## Questions to Resolve

1. What are the 23 review area names in our JSON template?
2. How do we map the 19 Riskuity categories to those 23 areas?
3. How should we handle the 86 controls without a clear prefix?
4. What fields from assessment should be included in JSON output?
