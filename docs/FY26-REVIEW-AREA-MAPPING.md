# FY26 Review Area Mapping - Final Configuration

**Date:** 2026-02-11
**Status:** ✅ Validated against Project 33 (494 controls)

## Summary

- **Total FY26 Review Areas:** 21
- **Mapped from Project 33:** 20 areas
- **Missing from Project 33:** 1 area (Title VI - removed for testing)
- **Excluded from FY26:** 2 areas (DBE, EEO - removed from FY26 program)
- **Mapping Success Rate:** 100% (494/494 controls mapped)

## FY26 Review Areas (21 Total)

| # | Review Area Name | Controls in Project 33 | Status |
|---|------------------|------------------------|--------|
| 1 | Legal | 11 | ✅ Mapped |
| 2 | Financial Management and Capacity | 56 | ✅ Mapped |
| 3 | Technical Capacity - Award Management | 40 | ✅ Mapped |
| 4 | Technical Capacity - Program Management and Subrecipient Oversight | 30 | ✅ Mapped |
| 5 | Technical Capacity - Project Management | 17 | ✅ Mapped |
| 6 | Transit Asset Management | 33 | ✅ Mapped |
| 7 | Satisfactory Continuing Control | 60 | ✅ Mapped |
| 8 | Maintenance | 21 | ✅ Mapped |
| 9 | Procurement | 71 | ✅ Mapped |
| 10 | Title VI | 0 | ⚠️ Not in Project 33 (will add later) |
| 11 | Americans with Disabilities Act (ADA) - General | 4 | ✅ Mapped |
| 12 | Americans with Disabilities Act (ADA) - Complementary Paratransit | 5 | ✅ Mapped |
| 13 | School Bus | 7 | ✅ Mapped |
| 14 | Charter Bus | 11 | ✅ Mapped |
| 15 | Drug-Free Workplace Act | 10 | ✅ Mapped |
| 16 | Drug and Alcohol Program | 18 | ✅ Mapped |
| 17 | Section 5307 Program Requirements | 24 | ✅ Mapped |
| 18 | Section 5310 Program Requirements | 21 | ✅ Mapped |
| 19 | Section 5311 Program Requirements | 33 | ✅ Mapped |
| 20 | Public Transportation Agency Safety Plan (PTASP) | 20 | ✅ Mapped |
| 21 | Cybersecurity | 2 | ✅ Mapped |

**Total Controls:** 494

## Excluded from FY26 (Not in Output JSON)

| Review Area Name | Reason |
|------------------|--------|
| Disadvantaged Business Enterprise | Removed from FY26 CORTAP program |
| Equal Employment Opportunity | Removed from FY26 CORTAP program |

## Riskuity Control Prefix Variations

Some review areas have multiple prefix variations in Riskuity control names:

### Financial Management and Capacity (56 controls)
- `FINANCIAL MANAGEMENT` (55 controls)
- `FINANCIAL MANAGEMENT AND CAPACITY` (1 control)

### Technical Capacity - Award Management (40 controls)
- `TECHNICAL CAPACITY AWARD MANAGEMENT` (35 controls)
- `TECHNICAL CAPACITY – AWARD MANAGEMENT` (5 controls with en-dash)

### Drug-Free Workplace Act (10 controls)
- `DRUG FREE WORKPLACE ACT` (7 controls)
- `DRUG-FREE WORKPLACE ACT` (3 controls with hyphen)

### Public Transportation Agency Safety Plan (20 controls)
- `PUBLIC TRANSPORTATION AGENCY SAFETY PLAN` (14 controls)
- `PTASP` (6 controls)

## Implementation Notes

### Mapping Logic
The mapping is implemented in `src/services/riskuity_control_mapping.py`:

```python
from services.riskuity_control_mapping import map_to_json_review_area

# Extract review area from Riskuity control name
control_name = "LEGAL : L2"
json_area = map_to_json_review_area(control_name)
# Returns: "Legal"
```

### Handling Missing Areas
- **Title VI:** Will be added when Title VI controls are restored to projects
- **DBE, EEO:** Omit entirely from FY26 JSON output (not in schema for FY26)

### Assessment Aggregation Strategy

When transforming 494 individual assessments → 21 consolidated review areas:

1. **Group by Review Area:** Use `map_to_json_review_area()` to group controls
2. **Determine Finding:**
   - If ANY control has a deficiency → `finding: "D"`
   - If all controls compliant → `finding: "ND"`
   - If area not applicable → `finding: "NA"`
3. **Aggregate Comments:** Combine assessment comments from all controls in area
4. **Status Rollup:** Calculate completion percentage across all controls

## Data Sources

- **Riskuity API:** GET `/projects/project_controls/{project_id}?limit=500`
- **Test Project:** Project ID 33 "CORTAP FY26 Assessment Test"
- **FY26 Controls:** `/Users/bob.emerick/dev/AI-projects/CORTAP-Guide/output/LC_Riskuity_CORTAP-FY26_v1.json` (708 controls, 21 families)

## Next Steps

1. ✅ Create mapping configuration (`riskuity_control_mapping.py`)
2. ✅ Validate mapping against project 33 (100% success)
3. ⏳ Implement data transformation in `RiskuityDataService`
4. ⏳ Test aggregation logic (494 assessments → 21 review areas)
5. ⏳ Handle Title VI when added to projects
6. ⏳ Validate output JSON against schema

## Testing Results

**Validation against Project 33:**
- Total controls: 494
- Successfully mapped: 494 (100%)
- Unmapped: 0
- Review areas covered: 20/21 (Title VI excluded from test project)
