# Riskuity Control Prefix → JSON Review Area Mapping

**Project:** CORTAP FY26 Assessment Test (ID: 33)
**Date:** 2026-02-11
**Total Riskuity Controls:** 494
**Total JSON Review Areas:** 23

## Mapping Table

| Riskuity Control Prefix | Count | JSON Review Area | Status |
|-------------------------|-------|------------------|--------|
| LEGAL | 11 | Legal | ✅ Mapped |
| FINANCIAL MANAGEMENT | 55 | Financial Management and Capacity | ✅ Mapped |
| FINANCIAL MANAGEMENT AND CAPACITY | 1 | Financial Management and Capacity | ✅ Mapped |
| TECHNICAL CAPACITY – AWARD MANAGEMENT | 35 | Technical Capacity - Award Management | ✅ Mapped |
| TECHNICAL CAPACITY – PROGRAM MANAGEMENT | 30 | Technical Capacity - Program Management and Subrecipient Oversight | ✅ Mapped |
| TECHNICAL CAPACITY – PROJECT MANAGEMENT | 17 | Technical Capacity - Project Management | ✅ Mapped |
| TRANSIT ASSET MANAGEMENT | 33 | Transit Asset Management | ✅ Mapped |
| SATISFACTORY CONTINUING CONTROL | 60 | Satisfactory Continuing Control | ✅ Mapped |
| MAINTENANCE | 21 | Maintenance | ✅ Mapped |
| PROCUREMENT | 71 | Procurement | ✅ Mapped |
| ADA GENERAL | 4 | Americans with Disabilities Act (ADA) - General | ✅ Mapped |
| ADA COMPLEMENTARY PARATRANSIT | 5 | Americans with Disabilities Act (ADA) - Complementary Paratransit | ✅ Mapped |
| SCHOOL BUS | 7 | School Bus | ✅ Mapped |
| CHARTER BUS | 11 | Charter Bus | ✅ Mapped |
| DRUG FREE WORKPLACE ACT | 7 | Drug-Free Workplace Act | ✅ Mapped |
| DRUG AND ALCOHOL PROGRAM | 18 | Drug and Alcohol Program | ✅ Mapped |
| PUBLIC TRANSPORTATION AGENCY SAFETY PLAN | 14 | Public Transportation Agency Safety Plan (PTASP) | ✅ Mapped |
| PTASP | 6 | Public Transportation Agency Safety Plan (PTASP) | ✅ Mapped |
| CYBERSECURITY | 2 | Cybersecurity | ✅ Mapped |

**Total Mapped:** 408 controls (19 categories)
**Unmapped Controls:** 86 controls (need investigation)

## JSON Review Areas NOT Found in Riskuity Data

These review areas exist in the JSON schema but have no corresponding controls in project 33:

1. **Disadvantaged Business Enterprise** - No controls
2. **Title VI** - No controls
3. **Equal Employment Opportunity** - No controls
4. **Section 5307 Program Requirements** - No controls
5. **Section 5310 Program Requirements** - No controls
6. **Section 5311 Program Requirements** - No controls

**Note:** These areas may not be applicable to FY26 reviews, or they may be handled differently in Riskuity.

## Implementation Notes

### Mapping Logic

```python
# Pseudo-code for mapping
def map_riskuity_to_json(control_name: str) -> str:
    # Extract prefix before colon
    prefix = extract_prefix(control_name)  # e.g., "LEGAL" from "LEGAL : L2"

    # Normalize and map
    mapping = {
        "LEGAL": "Legal",
        "FINANCIAL MANAGEMENT": "Financial Management and Capacity",
        "FINANCIAL MANAGEMENT AND CAPACITY": "Financial Management and Capacity",
        "TECHNICAL CAPACITY – AWARD MANAGEMENT": "Technical Capacity - Award Management",
        "TECHNICAL CAPACITY AWARD MANAGEMENT": "Technical Capacity - Award Management",
        "TECHNICAL CAPACITY – PROGRAM MANAGEMENT": "Technical Capacity - Program Management and Subrecipient Oversight",
        "TECHNICAL CAPACITY PROGRAM MANAGEMENT": "Technical Capacity - Program Management and Subrecipient Oversight",
        "TECHNICAL CAPACITY – PROJECT MANAGEMENT": "Technical Capacity - Project Management",
        "TECHNICAL CAPACITY PROJECT MANAGEMENT": "Technical Capacity - Project Management",
        "TRANSIT ASSET MANAGEMENT": "Transit Asset Management",
        "SATISFACTORY CONTINUING CONTROL": "Satisfactory Continuing Control",
        "MAINTENANCE": "Maintenance",
        "PROCUREMENT": "Procurement",
        "ADA GENERAL": "Americans with Disabilities Act (ADA) - General",
        "ADA COMPLEMENTARY PARATRANSIT": "Americans with Disabilities Act (ADA) - Complementary Paratransit",
        "SCHOOL BUS": "School Bus",
        "CHARTER BUS": "Charter Bus",
        "DRUG FREE WORKPLACE ACT": "Drug-Free Workplace Act",
        "DRUG AND ALCOHOL PROGRAM": "Drug and Alcohol Program",
        "PUBLIC TRANSPORTATION AGENCY SAFETY PLAN": "Public Transportation Agency Safety Plan (PTASP)",
        "PTASP": "Public Transportation Agency Safety Plan (PTASP)",
        "CYBERSECURITY": "Cybersecurity",
    }

    return mapping.get(prefix.upper().strip())
```

### Handling Unmapped Controls (86 controls)

Options:
1. Manually review the 86 controls without clear prefixes
2. Map them to "N/A" or skip them
3. Create a catch-all review area
4. Investigate control names to find patterns

### Handling Missing JSON Areas

For the 6 review areas with no Riskuity controls:
- Set `finding: "NA"` (Not Applicable)
- Leave deficiency fields as null
- Document why they're not applicable

## Next Steps

1. ✅ Create mapping table
2. ⏳ Investigate 86 unmapped controls
3. ⏳ Implement mapping function in RiskuityDataService
4. ⏳ Handle 6 missing review areas (DBE, Title VI, EEO, Section programs)
5. ⏳ Test transformation with project 33 data
6. ⏳ Validate output JSON against schema
