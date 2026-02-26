# Section 1: Cover Letter - Conditional Logic Guide

**Purpose:** Handle explicit conditional markers (`[IF APPLICABLE]`, `[OMIT FOR FINAL REPORT LETTER]`) in Section 1

**Important:** This guide ONLY covers conditionals where the original template has explicit markers. We do not add Jinja2 conditionals based on inference - only where the template explicitly calls for them.

---

## Conditional Markers Found in Section 1

The original template has **3 explicit conditional markers** in Section 1:

1. `[IF APPLICABLE]` - Before ERF paragraph (paragraph 12)
2. `[IF APPLICABLE]` - Before corrective action responses (paragraph 14)
3. `[OMIT FOR FINAL REPORT LETTER]` - Before draft review instructions (paragraph 16)

---

## 1. ERF (Enhanced Review Focus) Paragraph

**Location:** After the paragraph listing deficiency areas

**Find this marker:**
```
[IF APPLICABLE]
```

**Followed by this paragraph:**
```
As part of this year's {{ project.review_type }} of {{ project.recipient_acronym }}, the FTA incorporated [an] Enhanced Review Focus (ERF/ERFs) in the [LIST] area/areas. The purpose of an ERF is to conduct a more comprehensive review of underlying operations, policies, procedures, and other data and documentation. Deficiencies resulting from the ERF are presented in the [LIST] area(s) of the report that follows.
```

**Action:**
1. Delete the `[IF APPLICABLE]` marker paragraph
2. Wrap the ERF paragraph with conditional:

```jinja2
{% if metadata.erf_count > 0 %}
As part of this year's {{ project.review_type }} of {{ project.recipient_acronym }}, the FTA incorporated {{ metadata.erf_count }} Enhanced Review Focus (ERF{{ 's' if metadata.erf_count != 1 else '' }}) in the {{ metadata.erf_areas }} area{{ 's' if metadata.erf_count != 1 else '' }}. The purpose of an ERF is to conduct a more comprehensive review of underlying operations, policies, procedures, and other data and documentation. Deficiencies resulting from the ERF are presented in the {{ metadata.erf_areas }} area(s) of the report that follows.
{% endif %}
```

**Required test data fields:**
```json
"metadata": {
  "erf_count": 0,
  "erf_areas": ""
}
```

**Note:** When `erf_count` is 0, this entire paragraph will be omitted from the output.

---

## 2. Corrective Action Responses Paragraph

**Location:** After the ERF paragraph

**Find this marker:**
```
[IF APPLICABLE]
```

**Followed by this paragraph:**
```
After the site visit, {{ project.recipient_acronym }} provided corrective action responses to address/and close deficiencies noted in the [LIST] area(s) of the report that follows.
```

**Action:**
1. Delete the `[IF APPLICABLE]` marker paragraph
2. Wrap the corrective action paragraph with conditional:

```jinja2
{% if metadata.has_post_visit_responses %}
After the site visit, {{ project.recipient_acronym }} provided corrective action responses to address and close deficiencies noted in the {{ metadata.deficiency_areas }} area(s) of the report that follows.
{% endif %}
```

**Required test data fields:**
```json
"metadata": {
  "has_post_visit_responses": false,
  "deficiency_areas": "Disadvantaged Business Enterprise"
}
```

**Note:** This paragraph appears only when the recipient has already provided responses after the site visit but before the report was issued.

---

## 3. Draft Report Review Instructions

**Location:** Near the end of the cover letter

**Find this marker:**
```
[OMIT FOR FINAL REPORT LETTER]
```

**Followed by this paragraph:**
```
Please review this draft report for accuracy and provide your comments to both the reviewer and your FTA Program Manager within ten business days from the date of this letter. A final report that incorporates your comments to the draft report will be provided to you within fourteen business days of your response.
```

**Action:**
1. Delete the `[OMIT FOR FINAL REPORT LETTER]` marker paragraph
2. Wrap the review instructions paragraph with conditional:

```jinja2
{% if project.report_status == "Draft" %}
Please review this draft report for accuracy and provide your comments to both the reviewer and your FTA Program Manager within ten business days from the date of this letter. A final report that incorporates your comments to the draft report will be provided to you within fourteen business days of your response.
{% endif %}
```

**Required test data fields:**
```json
"project": {
  "report_status": "Draft"
}
```

**Note:** When `report_status` is `"Final"`, this entire paragraph will be omitted.

---

## 4. Contact Information and Closing Signature

**Location:** Near the end of Section 1, after the draft review instructions

**Find this paragraph:**
```
Thank you for your cooperation and assistance during this {{ project.review_type }}.  If you need any technical assistance or have any questions, please do not hesitate to contact Mr./Ms. [FTA Program Manager Name], [FTA Title], at [phone number] or by email at [email]@dot.gov, or Mr./Ms. [reviewer name], your reviewer, at [phone number] or by email at [email].
```

**Replace with:**
```jinja2
Thank you for your cooperation and assistance during this {{ project.review_type }}. If you need any technical assistance or have any questions, please do not hesitate to contact {{ fta_program_manager.name }}, {{ fta_program_manager.title }}, at {{ fta_program_manager.phone }} or by email at {{ fta_program_manager.email }}, or {{ contractor.lead_reviewer_name }}, your reviewer, at {{ contractor.lead_reviewer_phone }} or by email at {{ contractor.lead_reviewer_email }}.
```

**Find the signature block:**
```
Sincerely,

[Appropriate Regional Officer]
[Appropriate Regional Officer Titles]
```

**Replace with:**
```jinja2
Sincerely,

{{ regional_officer.name }}
{{ regional_officer.title }}
```

**Required test data fields:**
```json
"fta_program_manager": {
  "name": "Michelle Muhlanger",
  "title": "Deputy Regional Administrator",
  "phone": "617-494-2630",
  "email": "michelle.muhlanger@dot.gov",
  "region": "Region 1"
},
"regional_officer": {
  "name": "Mary Beth Mello",
  "title": "Regional Administrator"
},
"contractor": {
  "name": "Qi Tech, LLC",
  "lead_reviewer_name": "Gwen Larson",
  "lead_reviewer_phone": "920-746-4595",
  "lead_reviewer_email": "gwen_larson@qitechllc.com"
}
```

---

## Complete Section 1 Checklist

After updating Section 1, verify:

**Conditional Logic:**
- [ ] ERF paragraph wrapped with `{% if metadata.erf_count > 0 %}`
- [ ] Corrective action responses wrapped with `{% if metadata.has_post_visit_responses %}`
- [ ] Draft review instructions wrapped with `{% if project.report_status == "Draft" %}`
- [ ] All three `[IF APPLICABLE]` and `[OMIT FOR FINAL REPORT LETTER]` markers deleted

**Basic Field Replacements:**
- [ ] All `[Recipient Acronym]` replaced with `{{ project.recipient_acronym }}`
- [ ] All `[Recipient name]` replaced with `{{ project.recipient_name }}`
- [ ] All date fields using `{{ date_format(...) }}`
- [ ] Regional office header using `{{ project.regional_office_header }}`

**Contact Information and Signature:**
- [ ] `[FTA Program Manager Name]` replaced with `{{ fta_program_manager.name }}`
- [ ] `[FTA Title]` replaced with `{{ fta_program_manager.title }}`
- [ ] FTA `[phone number]` replaced with `{{ fta_program_manager.phone }}`
- [ ] FTA `[email]@dot.gov` replaced with `{{ fta_program_manager.email }}`
- [ ] `[reviewer name]` replaced with `{{ contractor.lead_reviewer_name }}`
- [ ] Reviewer `[phone number]` replaced with `{{ contractor.lead_reviewer_phone }}`
- [ ] Reviewer `[email]` replaced with `{{ contractor.lead_reviewer_email }}`
- [ ] `[Appropriate Regional Officer]` replaced with `{{ regional_officer.name }}`
- [ ] `[Appropriate Regional Officer Titles]` replaced with `{{ regional_officer.title }}`

---

## Test Data Requirements

Make sure your test data includes these fields for Section 1:

```json
{
  "project": {
    "report_status": "Draft",
    "review_type": "Triennial Review",
    "recipient_acronym": "NTD",
    "recipient_name": "Norwalk Transit District"
  },
  "metadata": {
    "erf_count": 0,
    "erf_areas": "",
    "has_post_visit_responses": false,
    "deficiency_areas": "Disadvantaged Business Enterprise"
  },
  "fta_program_manager": {
    "name": "Michelle Muhlanger",
    "title": "Deputy Regional Administrator",
    "phone": "617-494-2630",
    "email": "michelle.muhlanger@dot.gov",
    "region": "Region 1"
  },
  "regional_officer": {
    "name": "Mary Beth Mello",
    "title": "Regional Administrator"
  },
  "contractor": {
    "name": "Qi Tech, LLC",
    "lead_reviewer_name": "Gwen Larson",
    "lead_reviewer_phone": "920-746-4595",
    "lead_reviewer_email": "gwen_larson@qitechllc.com"
  }
}
```

---

## Testing Section 1 Conditionals

After adding the three conditionals, test with different scenarios:

### Test 1: Draft Report, No ERF, No Post-Visit Responses
```bash
# Current NTD test data configuration
python scripts/test_section.py draft-report-working.docx tests/fixtures/mock-data/NTD_FY2023_TR.json
```
**Expected output:**
- ✅ Draft review instructions paragraph appears
- ✅ ERF paragraph is omitted (erf_count = 0)
- ✅ Corrective action responses paragraph is omitted (has_post_visit_responses = false)

### Test 2: Final Report
```bash
# Temporarily change report_status to "Final" in test data
python scripts/test_section.py draft-report-working.docx tests/fixtures/mock-data/NTD_FY2023_TR.json
```
**Expected output:**
- ✅ Draft review instructions paragraph is omitted

### Test 3: With ERF
```bash
# Set erf_count: 1, erf_areas: "Procurement" in test data
python scripts/test_section.py draft-report-working.docx tests/fixtures/mock-data/NTD_FY2023_TR.json
```
**Expected output:**
- ✅ ERF paragraph appears with correct area

### Test 4: With Post-Visit Responses
```bash
# Set has_post_visit_responses: true in test data
python scripts/test_section.py draft-report-working.docx tests/fixtures/mock-data/NTD_FY2023_TR.json
```
**Expected output:**
- ✅ Corrective action responses paragraph appears

---

## Common Jinja2 Patterns (Quick Reference)

### Show/Hide Paragraph
```jinja2
{% if condition %}
[paragraph content]
{% endif %}
```

### Grammar Helper (singular/plural)
```jinja2
{{ count }} area{{ 's' if count != 1 else '' }}
{{ count }} ERF{{ 's' if count != 1 else '' }}
deficienc{{ 'y' if count == 1 else 'ies' }}
```

---

## Important Notes

1. **Only add Jinja2 where markers exist:** Do NOT add conditional logic based on what you think should be conditional. Only convert where the template has explicit markers.

2. **Other sections may have different markers:** When you move to Section 2, 3, etc., look for their specific conditional markers and handle them separately.

3. **Type carefully in Word:** When adding Jinja2 expressions in Word:
   - Turn OFF smart quotes before editing
   - Type Jinja2 code fresh (don't copy/paste)
   - Save and close Word completely before testing
   - Use lowercase for field names (`project.field_name` not `PROJECT.field_name`)

4. **Test after each change:** After adding each conditional, save, close Word, and test immediately.

---

## Next Steps

1. Open `draft-report-working.docx` in Word
2. Find each of the 3 conditional markers
3. Delete the marker paragraph
4. Wrap the following paragraph with the appropriate Jinja2 conditional
5. Save and close Word completely
6. Test: `python scripts/test_section.py draft-report-working.docx`
7. Verify output: `open output/incremental/draft-report-working_test.docx`
8. Move to Section 2 (check for new conditional markers there!)
