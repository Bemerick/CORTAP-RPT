# Section 2: Cover Page and Executive Summary - Conversion Guide

**Purpose:** Convert all fields in Section 2 including:
- Cover page (front matter)
- I. Executive Summary paragraphs
- 1. Metric definitions
- 2. Summary of Findings (with table)

**Important:** Many fields are NOT marked with brackets `[]` - they're placeholder text that should be replaced with Jinja2 expressions.

---

## Cover Page Fields to Convert

### 1. Fiscal Year

**Find:**
```
FISCAL YEAR 2025
```

**Replace with:**
```jinja2
FISCAL YEAR {{ project.fiscal_year }}
```

---

### 2. Review Type Heading

**Find:**
```
TRIENNIAL REVIEW/STATE MANAGEMENT REVIEW/COMBINED TRIENNIAL AND STATE MANAGEMENT REVIEW
```

**Replace with:**
```jinja2
{{ project.review_type | upper }}
```

**Note:** The `| upper` filter converts the text to uppercase. The review_type value in data is "Triennial Review", "State Management Review", or "Combined Triennial and State Management Review".

---

### 3. Recipient Information Block

**Find:**
```
Of
Recipient Full Name
Recipient Acronym (If applicable)
Recipient City and State
Recipient ID#
```

**Replace with:**
```jinja2
Of
{{ project.recipient_name }}
{% if project.recipient_acronym %}{{ project.recipient_acronym }}{% endif %}
{{ project.recipient_city_state }}
Recipient ID: {{ project.recipient_id }}
```

**Note:** The acronym line uses a conditional in case some recipients don't have an acronym.

---

### 4. Region Number

**Find:**
```
[REGION #]
```

**Replace with:**
```jinja2
Region {{ project.region_number }}
```

---

### 5. Contractor Name

**Find:**
```
Prepared By:
Contractor Name
```

**Replace with:**
```jinja2
Prepared By:
{{ contractor.name }}
```

---

### 6. Review Dates Block

**Find:**
```
Desk Review Date: [Month] [Day], 2025
Scoping Meeting Date: [Month] [Day], 2025
Site Visit Entrance Conference Date: [Month] [Day], 2025
Site Visit Exit Conference Date: [Month] [Day], 2025
Draft Report Date: [Month] [Day], 2025
Final Report Date: [Month] [Day], 2025
```

**Replace with:**
```jinja2
{% if project.desk_review_date %}Desk Review Date: {{ date_format(project.desk_review_date) }}
{% endif %}Scoping Meeting Date: {{ date_format(project.scoping_meeting_date) }}
Site Visit Entrance Conference Date: {{ date_format(project.site_visit_start_date) }}
Site Visit Exit Conference Date: {{ date_format(project.exit_conference_date) }}
{% if project.report_status == "Draft" %}Draft Report Date: {{ date_format(project.report_date) }}
{% elif project.report_status == "Final" %}Final Report Date: {{ date_format(project.report_date) }}
{% endif %}
```

**Notes:**
- Desk review date is conditional (not all reviews have one)
- Draft/Final report date is conditional based on report_status
- The `date_format()` function formats dates as "Month Day, Year" (e.g., "July 11, 2023")

---

## Complete Section 2 Cover Page Checklist

After updating Section 2, verify:

- [ ] `FISCAL YEAR 2025` replaced with `{{ project.fiscal_year }}`
- [ ] Review type heading replaced with `{{ project.review_type | upper }}`
- [ ] `Recipient Full Name` replaced with `{{ project.recipient_name }}`
- [ ] `Recipient Acronym` wrapped with conditional `{% if project.recipient_acronym %}`
- [ ] `Recipient City and State` replaced with `{{ project.recipient_city_state }}`
- [ ] `Recipient ID#` replaced with `Recipient ID: {{ project.recipient_id }}`
- [ ] `[REGION #]` replaced with `Region {{ project.region_number }}`
- [ ] `Contractor Name` replaced with `{{ contractor.name }}`
- [ ] All date fields using `{{ date_format(...) }}`
- [ ] Desk review date wrapped with conditional (optional field)
- [ ] Draft/Final report date using conditional based on `report_status`

---

## Test Data Requirements

Make sure your test data includes these fields:

```json
{
  "project": {
    "fiscal_year": 2023,
    "review_type": "Triennial Review",
    "recipient_name": "Norwalk Transit District",
    "recipient_acronym": "NTD",
    "recipient_city_state": "Norwalk, Connecticut",
    "recipient_id": "1339",
    "region_number": 1,
    "desk_review_date": "2023-01-15",
    "scoping_meeting_date": "2023-02-24",
    "site_visit_start_date": "2023-03-28",
    "exit_conference_date": "2023-05-15",
    "report_date": "2023-07-11",
    "report_status": "Draft"
  },
  "contractor": {
    "name": "Qi Tech, LLC"
  }
}
```

---

## Testing Section 2 Cover Page

After converting the cover page fields:

```bash
python scripts/test_section.py app/templates/draft-report-working.docx tests/fixtures/mock-data/NTD_FY2023_TR.json
```

**Expected output:**
- ✅ FISCAL YEAR 2023
- ✅ TRIENNIAL REVIEW
- ✅ Norwalk Transit District
- ✅ NTD
- ✅ Norwalk, Connecticut
- ✅ Recipient ID: 1339
- ✅ Region 1
- ✅ Qi Tech, LLC
- ✅ All dates formatted as "Month Day, Year"
- ✅ Only "Draft Report Date" appears (not "Final Report Date")

---

## Important Notes

1. **No brackets on most fields:** Unlike Section 1, most of these fields are not marked with `[]` - they're just placeholder text that looks like field names.

2. **Case sensitivity:** Use exact field names as shown (lowercase with underscores).

3. **Date formatting:** The `date_format()` function is defined in the test script and converts dates like "2023-07-11" to "July 11, 2023".

4. **Review type filter:** The `| upper` filter ensures review type displays in all caps regardless of how it's stored in the data.

5. **Conditional dates:** Desk review and draft/final report dates use conditionals because:
   - Not all reviews have a desk review phase
   - Only draft OR final report date should show, not both

---

---

## I. Executive Summary - Introductory Paragraphs

### First Paragraph

**Find:**
```
This report documents the Federal Transit Administration's (FTA) Triennial Review of the [Recipient full name (Recipient Acronym if applicable)] of [Recipient City and State]. The FTA wants to ensure that awards are administered in accordance with the requirements of Federal public transportation law 49 U.S.C. Chapter 53. The review was performed by [contractor firm] (Contractor).
```

**Replace with:**
```jinja2
This report documents the Federal Transit Administration's (FTA) {{ project.review_type }} of the {{ project.recipient_name }} ({{ project.recipient_acronym }}) of {{ project.recipient_city_state }}. The FTA wants to ensure that awards are administered in accordance with the requirements of Federal public transportation law 49 U.S.C. Chapter 53. The review was performed by {{ contractor.name }}.
```

### COVID-19 Paragraph

**Find:**
```
Due to the Coronavirus 2019 (COVID-19) Public Health Emergency, the FTA expanded the review to address NTD's compliance...
```

**Replace with:**
```jinja2
{% if metadata.covid19_context %}
Due to the Coronavirus 2019 (COVID-19) Public Health Emergency, the FTA expanded the review to address {{ project.recipient_acronym }}'s compliance with the administrative relief and flexibilities that the FTA granted, and the requirements of the COVID-19 Relief funds received through the Coronavirus Aid, Relief, and Economic Security (CARES) Act, Coronavirus Response and Relief Supplemental Appropriations Act (CRRSAA) of 2021, and the American Rescue Plan (ARP) Act of 2021. The FTA also requested the {{ project.recipient_acronym }} share if and/or how it suspended, deviated from, or significantly updated or altered its transit program due to the public health emergency.
{% endif %}
```

**Note:** This entire paragraph is conditional - it only appears if `metadata.covid19_context` is true.

---

## 2. Summary of Findings - Conditional Text

### Repeat Deficiencies

**Find:**
```
There were [no] repeat deficiencies from the FY 2022 Triennial Review.
```

**Replace with:**
```jinja2
{% if metadata.no_repeat_deficiencies %}
There were no repeat deficiencies from the previous {{ project.review_type }}.
{% else %}
There were {{ metadata.repeat_deficiency_count }} repeat deficienc{{ 'y' if metadata.repeat_deficiency_count == 1 else 'ies' }} from the previous {{ project.review_type }} in the following area(s): {{ metadata.repeat_deficiency_areas }}.
{% endif %}
```

### ERF Section (ADD AS APPLICABLE)

**Find:**
```
[ADD AS APPLICABLE] As part of this year's Triennial Review of NTD, the FTA incorporated [#] Enhanced Review Focus (ERF) in the [LIST] area(s)...
```

**Replace with:**
```jinja2
{% if metadata.erf_count > 0 %}
As part of this year's {{ project.review_type }} of {{ project.recipient_acronym }}, the FTA incorporated {{ metadata.erf_count }} Enhanced Review Focus (ERF) in the {{ metadata.erf_areas }} area(s). The purpose of an ERF is to conduct a more comprehensive review of underlying or contributing issues identified during the pre-assessment stage of the {{ project.review_type }}. Deficiencies resulting from the ERF {{ 'is' if metadata.erf_count == 1 else 'are' }} presented in the {{ metadata.erf_areas }} area(s) of this report.
{% endif %}
```

### Deficiency Summary (OR conditional)

**Find:**
```
Deficiencies were found in the areas listed below.
[OR]
No deficiencies were found with any of FTA requirements in any of these areas.
```

**Replace with:**
```jinja2
{% if metadata.has_deficiencies %}
Deficiencies were found in the areas listed below.
{% else %}
No deficiencies were found with any of FTA requirements in any of these areas.
{% endif %}
```

---

## Summary of Findings Table

**IMPORTANT:** Keep the table formatting intact. Replace the 23 hardcoded rows with a Jinja2 loop.

### Table Structure

The table has these columns:
- Review Area
- Finding
- Deficiency Code(s): Code | Description
- Corrective Action(s)
- Response Due Date(s)
- Date Closed

### Converting the Table Rows

**Find the table rows starting with:**
```
1.    Legal    D/ND/NA    [empty cells]
2.    Financial Management and Capacity    D/ND/NA    [empty cells]
...
23.    Cybersecurity    D/ND/NA    [empty cells]
```

**DELETE all 23 hardcoded rows.**

**In their place, add a SINGLE template row with Jinja2 loop:**

```jinja2
{% for assessment in assessments %}
{{ loop.index }}.    {{ assessment.review_area }}    {{ assessment.finding }}    {% if assessment.finding == 'D' %}{{ assessment.deficiency_code }}    {{ assessment.description }}    {{ assessment.corrective_action }}    {{ date_format(assessment.due_date) if assessment.due_date else '' }}    {{ date_format(assessment.date_closed) if assessment.date_closed else '' }}{% endif %}
{% endfor %}
```

**How to do this in Word:**
1. Keep the table header row (Review Area | Finding | Deficiency Code(s)...)
2. Delete all 23 data rows
3. Add ONE new row to the table
4. In the cells of that one row, add the Jinja2 expressions as shown above
5. The loop will generate 23 rows at render time

**Table Cell Mapping:**
- Cell 1: `{{ loop.index }}.    {{ assessment.review_area }}`
- Cell 2: `{{ assessment.finding }}`
- Cell 3 (Code): `{% if assessment.finding == 'D' %}{{ assessment.deficiency_code }}{% endif %}`
- Cell 4 (Description): `{% if assessment.finding == 'D' %}{{ assessment.description }}{% endif %}`
- Cell 5: `{% if assessment.finding == 'D' %}{{ assessment.corrective_action }}{% endif %}`
- Cell 6: `{% if assessment.finding == 'D' and assessment.due_date %}{{ date_format(assessment.due_date) }}{% endif %}`
- Cell 7: `{% if assessment.finding == 'D' and assessment.date_closed %}{{ date_format(assessment.date_closed) }}{% endif %}`

**Note:** Deficiency details only appear when `finding == 'D'`. For ND and NA findings, those cells remain empty.

---

## Complete Section 2 Checklist

### Cover Page:
- [ ] Fiscal year, review type, recipient info converted
- [ ] All dates using `date_format()`
- [ ] Region number and contractor name converted

### Executive Summary:
- [ ] First paragraph fields replaced
- [ ] COVID-19 paragraph wrapped in conditional
- [ ] Repeat deficiencies using conditional
- [ ] ERF section using conditional
- [ ] Deficiency summary using `[OR]` conditional

### Metric Section:
- [ ] No changes needed (definitions only)

### Summary Table:
- [ ] Table header row preserved
- [ ] All 23 hardcoded rows deleted
- [ ] Single template row added with Jinja2 loop
- [ ] Each cell has correct Jinja2 expression
- [ ] Deficiency details conditional on `finding == 'D'`

---

## Test Data Requirements

```json
{
  "assessments": [
    {
      "review_area": "Legal",
      "finding": "ND",
      "deficiency_code": null,
      "description": null,
      "corrective_action": null,
      "due_date": null,
      "date_closed": null
    },
    {
      "review_area": "Disadvantaged Business Enterprise (DBE)",
      "finding": "D",
      "deficiency_code": "DBE12-2",
      "description": "Insufficient documentation of monitoring DBE work...",
      "corrective_action": "By December 31, 2023, NTD must submit...",
      "due_date": "2023-12-31",
      "date_closed": null
    }
  ],
  "metadata": {
    "has_deficiencies": true,
    "deficiency_count": 1,
    "erf_count": 0,
    "erf_areas": "",
    "no_repeat_deficiencies": true,
    "repeat_deficiency_count": 0,
    "repeat_deficiency_areas": "",
    "covid19_context": true
  }
}
```

---

## Next Steps

1. Open `app/templates/draft-report-working.docx` in Word
2. Convert cover page fields
3. Convert Executive Summary paragraphs
4. Handle conditional tags (`[OR]`, `[ADD AS APPLICABLE]`)
5. Convert the table (most complex part!)
6. Save and close Word completely
7. Test: `python scripts/test_section.py app/templates/draft-report-working.docx tests/fixtures/mock-data/NTD_FY2023_TR.json`
8. Verify output: Table has 23 rows populated from assessments array
