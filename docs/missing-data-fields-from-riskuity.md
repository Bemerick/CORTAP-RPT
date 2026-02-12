# Missing Data Fields from Riskuity

**Generated:** February 12, 2026
**Purpose:** Document all fields that require default values or programmatic population due to missing data from Riskuity API

This document lists fields that need to be stored in Riskuity's project setup data or another configuration source to enable complete report generation without hardcoded "TBD" values.

---

## 1. Project/Recipient Information

**Location:** `app/services/data_transformer.py:197-217, 476-484, 482`

| Field | Current Default | Type | Priority | Notes |
|-------|----------------|------|----------|-------|
| `region_number` | `1` | int | **HIGH** | FTA region number (1-10) |
| `review_type` | `"Triennial Review"` | string | **HIGH** | Valid: "Triennial Review", "State Management Review", "Combined Triennial and State Management Review" |
| `recipient_acronym` | `"TBD"` | string | MEDIUM | Short name/acronym for recipient |
| `recipient_city_state` | `"City, ST"` | string | **HIGH** | Format: "City, State" |
| `fiscal_year` | `"FY2026"` | string | **HIGH** | Format: "FY####" |
| `report_date` | `datetime.utcnow()` | string | MEDIUM | Currently auto-generated as today's date; Format: "Month DD, YYYY" |
| `site_visit_dates` | `"TBD"` | string | **HIGH** | Human-readable date range |
| `site_visit_start_date` | `""` | string | **HIGH** | ISO format or human-readable |
| `site_visit_end_date` | `""` | string | **HIGH** | ISO format or human-readable |
| `exit_conference_format` | `"virtual"` | string | **HIGH** | "virtual" or "in-person" |
| `recipient_website` | `""` | string | MEDIUM | Optional URL |

**Total: 11 fields**

---

## 2. Contractor/Lead Reviewer Information

**Location:** `app/services/data_transformer.py:206-210, 519-526`

| Field | Current Default | Type | Priority | Notes |
|-------|----------------|------|----------|-------|
| `lead_reviewer_name` | `"TBD"` | string | **HIGH** | Full name of lead reviewer |
| `contractor_name` / `company_name` | `"TBD"` | string | **HIGH** | Required by schema and completeness check |
| `lead_reviewer_phone` | `"TBD"` | string | **HIGH** | Phone number |
| `lead_reviewer_email` | `"TBD"` | string | **HIGH** | Email address |

**Total: 4 fields**

---

## 3. FTA Program Manager Information

**Location:** `app/services/data_transformer.py:212-216, 542-549`

| Field | Current Default | Type | Priority | Notes |
|-------|----------------|------|----------|-------|
| `fta_program_manager_name` / `name` | `"TBD"` | string | **HIGH** | Full name (required by completeness check) |
| `fta_program_manager_title` | `"TBD"` | string | **HIGH** | Job title |
| `fta_program_manager_phone` | `"TBD"` | string | **HIGH** | Phone number |
| `fta_program_manager_email` | `"TBD"` | string | **HIGH** | Email address |

**Total: 4 fields**

---

## 4. Regional Officer Information

**Location:** `app/services/document_generator.py:261-266`

| Field | Current Default | Type | Priority | Notes |
|-------|----------------|------|----------|-------|
| `regional_officer.name` | `"TBD"` | string | **HIGH** | Full name of regional administrator |
| `regional_officer.title` | `"Regional Administrator"` | string | **HIGH** | Job title |
| `regional_officer.phone` | `"TBD"` | string | **HIGH** | Phone number |
| `regional_officer.email` | `"TBD"` | string | **HIGH** | Email address |

**Total: 4 fields**

---

## 5. Optional Lists/Collections

**Location:** `app/services/document_generator.py:267-271`

| Field | Current Default | Type | Priority | Notes |
|-------|----------------|------|----------|-------|
| `attendees` | `[]` | array | MEDIUM | List of site visit attendees |
| `contractors` | `[]` | array | MEDIUM | List of contractor personnel (plural form) |
| `subrecipients_5307` | `[]` | array | LOW | Section 5307 subrecipients |
| `subrecipients_5310` | `[]` | array | LOW | Section 5310 subrecipients |
| `subrecipients_5311` | `[]` | array | LOW | Section 5311 subrecipients |

**Total: 5 fields**

---

## 6. Assessment/Deficiency Fields

**Location:** `app/services/data_transformer.py:452-457`

| Field | Current Default | Type | Priority | Notes |
|-------|----------------|------|----------|-------|
| `deficiency_code` | `None` | string | LOW | TODO: Extract if available from Riskuity |
| `corrective_action` | `None` | string | LOW | TODO: Extract from CAP POAMs if needed |
| `due_date` | `None` | string | LOW | Due date for corrective action |
| `date_closed` | `None` | string | LOW | Date deficiency was closed |

**Total: 4 fields**

---

## Summary by Priority

### HIGH Priority (28 fields)
**Required for complete report generation**

- **Project Info (8):** region_number, review_type, recipient_city_state, fiscal_year, site_visit_dates, site_visit_start_date, site_visit_end_date, exit_conference_format
- **Contractor (4):** lead_reviewer_name, company_name, lead_reviewer_phone, lead_reviewer_email
- **FTA PM (4):** fta_program_manager_name, fta_program_manager_title, fta_program_manager_phone, fta_program_manager_email
- **Regional Officer (4):** name, title, phone, email

### MEDIUM Priority (4 fields)
**Enhance report quality**

- recipient_acronym, recipient_website, report_date, attendees

### LOW Priority (9 fields)
**Future enhancements**

- contractors (list), subrecipients (3 lists), deficiency fields (4)

---

## Total: 32 Fields

---

## Recommendations

### Immediate Action
Store **HIGH priority fields (28)** in Riskuity project setup/configuration area:

1. **Project Configuration** - Create custom fields or use existing project metadata fields
2. **Team Assignment** - Link contractor and FTA PM to project with contact details
3. **Review Schedule** - Store site visit dates and exit conference format
4. **Regional Info** - Associate regional officer based on project region

### Future Enhancement
- Add **MEDIUM priority fields** for better report quality
- Investigate extracting **deficiency details** from existing Riskuity CAP/POAM data

### Alternative Solutions
1. **Configuration File** - Store defaults in YAML/JSON config per region/review type
2. **Survey/Form** - Collect missing data via pre-review setup form in Riskuity
3. **User Input** - Prompt for required fields during report generation (not ideal for automation)

---

## Code Locations

- **Data Transformer:** `/app/services/data_transformer.py`
  - Lines 197-217: Project metadata extraction with defaults
  - Lines 459-510: Project transformation
  - Lines 512-532: Contractor transformation
  - Lines 534-555: FTA PM transformation

- **Document Generator:** `/app/services/document_generator.py`
  - Lines 260-272: Default values for optional template variables
  - Lines 76-101: Date format filter (handles missing dates)
