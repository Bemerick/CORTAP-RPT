# RIR Template Conversion Guide

**Story:** 4.1 - Convert RIR Template to docxtpl Format
**Status:** In Progress
**Date:** 2025-11-19

---

## Overview

This guide documents the conversion of the FTA Recipient Information Request (RIR) template from bracketed placeholder format to Jinja2 template syntax for use with python-docxtpl.

**Source Template:**
- File: `docs/requirements/RO_State_Recipient_FY2025_RecipientInformationRequestPackage_Final_1.3.25.docx`
- Size: 255KB
- Format: Microsoft Word (.docx)

**Destination Template:**
- File: `app/templates/rir-package.docx`
- Format: Microsoft Word (.docx) with Jinja2 placeholders
- Metadata: `app/templates/metadata/rir-field-definitions.yaml`

---

## Conversion Steps

### Step 1: Open the Template

1. Open `app/templates/rir-package.docx` in Microsoft Word
2. Enable "Show/Hide ¶" to see all formatting marks
3. Use Find & Replace (Ctrl+H / Cmd+H) for bulk conversions

### Step 2: Convert Bracketed Fields to Jinja2

Replace the following **16 fields** using Find & Replace:

#### Cover Page Fields (11 fields)

| Original Bracket | Jinja2 Placeholder | Location | Notes |
|------------------|-------------------|----------|-------|
| `[#]` (Region) | `{{ region_number }}` | Cover page, top | First [#] on page |
| `[Triennial Review]` | `{{ review_type }}` | Cover page, title | Keep "FY 2025" prefix |
| `[Recipient Name]` | `{{ recipient_name }}` | Cover page | Full legal name |
| `[Recipient Location]` | `{{ recipient_city_state }}` | Cover page | City, ST format |
| `[#]` (Recipient ID) | `{{ recipient_id }}` | Cover page | Second [#] on page |
| `[URL]` | `{{ recipient_website\|default('N/A') }}` | Cover page | Use default filter |
| Site Visit Dates field | `{{ site_visit_dates }}` | Cover page | May say "TBD" |
| `[Lead Reviewer Name]` | `{{ lead_reviewer_name }}` | Cover page | Contractor contact |
| `[Contractor Name]` | `{{ contractor_name }}` | Cover page | Firm name |
| `[Lead Reviewer Phone #]` | `{{ lead_reviewer_phone }}` | Cover page | Phone number |
| `[Lead Reviewer Email Address]` | `{{ lead_reviewer_email }}` | Cover page | Email address |

#### Body Content Fields (4 fields)

| Original Bracket | Jinja2 Placeholder | Location | Notes |
|------------------|-------------------|----------|-------|
| `[FTA PM for Recipient]` | `{{ fta_program_manager_name }}` | Body | FTA Program Manager name |
| `[FTA PM Title]` | `{{ fta_program_manager_title }}` | Body | FTA PM job title |
| `[FTA PM Phone #]` | `{{ fta_program_manager_phone }}` | Body | FTA PM phone |
| `[FTA PM Email Address]` | `{{ fta_program_manager_email }}` | Body | FTA PM email |

#### Due Date Field (1 field)

| Original Bracket | Jinja2 Placeholder | Location | Notes |
|------------------|-------------------|----------|-------|
| Due date placeholder | `{{ due_date\|default('TBD') }}` | Body | Response deadline |

---

## Find & Replace Instructions

Use Word's Find & Replace with "Match case" enabled:

### 1. Region Number (Cover Page)
**Find:** `[#]` (first occurrence only)
**Replace:** `{{ region_number }}`
**Note:** There are two `[#]` placeholders - replace them individually!

### 2. Review Type
**Find:** `[Triennial Review]`
**Replace:** `{{ review_type }}`
**Note:** Do NOT remove "FY 2025" text before this field

### 3. Recipient Name
**Find:** `[Recipient Name]`
**Replace:** `{{ recipient_name }}`

### 4. Recipient Location
**Find:** `[Recipient Location]`
**Replace:** `{{ recipient_city_state }}`

### 5. Recipient ID (Cover Page)
**Find:** `[#]` (second occurrence)
**Replace:** `{{ recipient_id }}`

### 6. Recipient Website
**Find:** `[URL]`
**Replace:** `{{ recipient_website|default('N/A') }}`
**Note:** Include the `|default('N/A')` filter!

### 7. Lead Reviewer Name
**Find:** `[Lead Reviewer Name]`
**Replace:** `{{ lead_reviewer_name }}`

### 8. Contractor Name
**Find:** `[Contractor Name]`
**Replace:** `{{ contractor_name }}`

### 9. Lead Reviewer Phone
**Find:** `[Lead Reviewer Phone #]`
**Replace:** `{{ lead_reviewer_phone }}`

### 10. Lead Reviewer Email
**Find:** `[Lead Reviewer Email Address]`
**Replace:** `{{ lead_reviewer_email }}`

### 11. FTA Program Manager Name
**Find:** `[FTA PM for Recipient]`
**Replace:** `{{ fta_program_manager_name }}`

### 12. FTA Program Manager Title
**Find:** `[FTA PM Title]`
**Replace:** `{{ fta_program_manager_title }}`

### 13. FTA Program Manager Phone
**Find:** `[FTA PM Phone #]`
**Replace:** `{{ fta_program_manager_phone }}`

### 14. FTA Program Manager Email
**Find:** `[FTA PM Email Address]`
**Replace:** `{{ fta_program_manager_email }}`

### 15. Site Visit Dates
**Find:** Site visit dates placeholder (varies by template)
**Replace:** `{{ site_visit_dates }}`

### 16. Due Date
**Find:** Due date placeholder (varies by template)
**Replace:** `{{ due_date|default('TBD') }}`

---

## Validation Checklist

After conversion, verify:

- [ ] All 16 bracketed fields replaced with Jinja2 syntax
- [ ] No remaining `[...]` brackets in template
- [ ] All `{{ ... }}` placeholders use correct variable names
- [ ] Optional fields use `|default()` filter
- [ ] No formatting corruption (styles, fonts, headers, footers intact)
- [ ] "FY 2025" text preserved before review type
- [ ] Document can be opened without errors

---

## Testing the Converted Template

After conversion, test with DocumentGenerator:

```python
from app.services.document_generator import DocumentGenerator

generator = DocumentGenerator(template_dir="app/templates")

# Test context with all required fields
context = {
    "region_number": 1,
    "review_type": "Triennial Review",
    "recipient_name": "Greater New Haven Transit District",
    "recipient_city_state": "Hamden, CT",
    "recipient_id": "1337",
    "recipient_website": "www.gnhtd.org",
    "site_visit_dates": "TBD",
    "lead_reviewer_name": "Bobby Killebrew",
    "contractor_name": "Qi Tech, LLC",
    "lead_reviewer_phone": "512-350-9912",
    "lead_reviewer_email": "bobby_killebrew@qitechllc.com",
    "fta_program_manager_name": "Syed T. Ahmed",
    "fta_program_manager_title": "General Engineer",
    "fta_program_manager_phone": "617-494-3254",
    "fta_program_manager_email": "syed.ahmed@dot.gov",
    "due_date": "2024-03-31"
}

# Generate document
output = await generator.generate("rir-package", context)

# Save for visual inspection
with open("test-rir-output.docx", "wb") as f:
    f.write(output.read())
```

---

## Common Issues

### Issue 1: Jinja2 Syntax Errors
**Symptom:** Template rendering fails with TemplateError
**Fix:** Check for typos in `{{ ... }}` placeholders - must match metadata YAML exactly

### Issue 2: Missing Default Values
**Symptom:** KeyError or "variable undefined" errors
**Fix:** Optional fields must use `|default()` filter

### Issue 3: Formatting Corruption
**Symptom:** Fonts, styles, or layout broken after conversion
**Fix:** Use Find & Replace cautiously, don't manually retype fields

### Issue 4: Multiple Replacements
**Symptom:** Wrong field replaced (e.g., both `[#]` replaced with same variable)
**Fix:** Replace one occurrence at a time for ambiguous brackets

---

## Reference

**Related Files:**
- Template metadata: `app/templates/metadata/rir-field-definitions.yaml`
- JSON schema: `docs/schemas/project-data-schema-v1.0.json`
- Mock data: `docs/schemas/mock-data/project-*.json`
- Requirements: `docs/recipient-information-request-requirements.md`

**Story Details:**
- Epic 4, Story 4.1 in `docs/epics.md` (lines 697-771)
- Acceptance criteria: 16 fields converted, metadata created, formatting preserved

**Next Steps:**
- Story 4.2: Implement review type conditional logic
- Story 4.3: Create RIR data model and context builder
- Story 4.4: Integrate with mock JSON files
