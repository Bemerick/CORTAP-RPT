# Project Setup Configuration

This directory contains project-specific setup data that supplements information from the Riskuity API.

## Overview

The configuration system allows you to manage 32 project setup fields that are not currently available from Riskuity:

- **Project Info**: Region, review type, fiscal year, site visit dates, etc. (11 fields)
- **Contractor**: Lead reviewer details (4 fields)
- **FTA Program Manager**: Assigned PM details (4 fields)
- **Regional Officer**: Regional Administrator details (4 fields)
- **Attendees**: Site visit attendees (optional list)
- **Subrecipients**: Section 5307/5310/5311 subrecipients (optional lists)

## Files

- **`project-setup-schema.json`** - JSON schema definition for validation
- **`project-setup.json`** - Active configuration file (edit this or use Excel)
- **`project-setup-template.xlsx`** - Excel template for easy editing

## Workflow

### Option 1: Edit JSON Directly

```bash
# Edit config/project-setup.json in your text editor
# Validate your changes
python scripts/manage_project_config.py validate --config config/project-setup.json
```

### Option 2: Edit via Excel (Recommended)

```bash
# 1. Export current JSON to Excel
python scripts/manage_project_config.py export \
  --input config/project-setup.json \
  --output config/project-setup-template.xlsx

# 2. Open config/project-setup-template.xlsx in Excel and edit

# 3. Import Excel back to JSON
python scripts/manage_project_config.py import \
  --input config/project-setup-template.xlsx \
  --output config/project-setup.json

# 4. Validate the result
python scripts/manage_project_config.py validate --config config/project-setup.json
```

## Excel Template Structure

The Excel file has 7 sheets:

1. **Instructions** - How to use the template
2. **Project_Info** - Basic project and review information
3. **Contractors** - Lead reviewer and company details
4. **FTA_PM** - FTA Program Manager information
5. **Regional_Officer** - Regional Administrator information
6. **Attendees** - Site visit attendees (multiple rows per project)
7. **Subrecipients** - Subrecipient agencies by program type

## Field Requirements

### Required Fields (HIGH Priority)

These fields **must** be provided for each project:

**Project Info:**
- `region_number` (1-10)
- `review_type` ("Triennial Review", "State Management Review", or "Combined...")
- `recipient_city_state` (format: "City, ST")
- `fiscal_year` (format: "FY####")
- `site_visit_start_date` (YYYY-MM-DD)
- `site_visit_end_date` (YYYY-MM-DD)
- `site_visit_dates` (human-readable, e.g., "March 15-19, 2026")
- `exit_conference_format` ("virtual" or "in-person")

**Contractor:**
- `lead_reviewer_name`
- `company_name`
- `lead_reviewer_phone`
- `lead_reviewer_email`

**FTA Program Manager:**
- `name`
- `title`
- `phone`
- `email`

**Regional Officer:**
- `name`
- `title`
- `phone`
- `email`

### Optional Fields (MEDIUM Priority)

- `recipient_acronym` - Short name (e.g., "METRO")
- `recipient_website` - Agency URL
- `report_date` - Report date (defaults to today if not specified)

### Optional Collections (LOW Priority)

- `attendees` - List of site visit attendees
- `subrecipients.5307` - Section 5307 subrecipients
- `subrecipients.5310` - Section 5310 subrecipients
- `subrecipients.5311` - Section 5311 subrecipients

## How It Works

1. **Data Transformer** loads configuration on startup
2. When generating a report, it looks up the project by ID
3. If found, uses configuration values; otherwise falls back to Riskuity or defaults
4. Configuration values **override** Riskuity data

## Example: Adding a New Project

### Via JSON:

```json
{
  "projects": [
    {
      "project_id": 42,
      "project_info": {
        "region_number": 5,
        "review_type": "Triennial Review",
        "recipient_city_state": "Minneapolis, MN",
        "recipient_acronym": "Metro Transit",
        "fiscal_year": "FY2026",
        "site_visit_start_date": "2026-05-10",
        "site_visit_end_date": "2026-05-14",
        "site_visit_dates": "May 10-14, 2026",
        "exit_conference_format": "in-person"
      },
      "contractor": {
        "lead_reviewer_name": "Jane Smith",
        "company_name": "ABC Consulting",
        "lead_reviewer_phone": "(612) 555-1234",
        "lead_reviewer_email": "jsmith@abc.com"
      },
      "fta_program_manager": {
        "name": "John Doe",
        "title": "Transportation Program Specialist",
        "phone": "(816) 329-3920",
        "email": "john.doe@dot.gov"
      },
      "regional_officer": {
        "name": "Sarah Johnson",
        "title": "Regional Administrator",
        "phone": "(816) 329-3900",
        "email": "sarah.johnson@dot.gov"
      },
      "attendees": [],
      "subrecipients": {
        "5307": [],
        "5310": [],
        "5311": []
      }
    }
  ]
}
```

### Via Excel:

1. Export to Excel: `python scripts/manage_project_config.py export`
2. Open `config/project-setup-template.xlsx`
3. Add a new row in each sheet with `project_id = 42`
4. Fill in the required fields
5. Import: `python scripts/manage_project_config.py import --input config/project-setup-template.xlsx`

## Validation

The configuration is validated against the JSON schema:

```bash
python scripts/manage_project_config.py validate --config config/project-setup.json
```

Common validation errors:
- Missing required fields
- Invalid `region_number` (must be 1-10)
- Invalid `review_type` (must match enum values)
- Invalid date formats (must be YYYY-MM-DD)
- Invalid `recipient_city_state` format (must be "City, ST")

## Integration with Report Generation

When you call the report generation endpoint:

```bash
POST /api/v1/generate-report-sync
{
  "project_id": 33,
  "report_type": "draft_audit_report"
}
```

The system will:
1. Look up project 33 in `config/project-setup.json`
2. If found, use those values for contractor, FTA PM, regional officer, etc.
3. If not found, fall back to Riskuity data or "TBD" defaults
4. Generate the report with the merged data

## Future Enhancement

Eventually, these fields should be stored directly in Riskuity, and this configuration system can be deprecated. See `docs/missing-data-fields-from-riskuity.md` for the full field inventory and Riskuity integration recommendations.

## Troubleshooting

### "No project configuration found for project X"

This is just a warning. The system will use Riskuity data or defaults. To fix:
1. Add the project to `config/project-setup.json`
2. Or export to Excel, add the project, and re-import

### "ProjectConfigService: config file not found"

The `config/project-setup.json` file doesn't exist. Create it:

```bash
cp config/project-setup.json.example config/project-setup.json
```

Or create a new one:

```json
{
  "projects": []
}
```

### Validation fails after Excel import

Check for:
- Extra spaces in fields
- Invalid date formats (must be YYYY-MM-DD)
- Missing required fields
- Invalid enum values (review_type, exit_conference_format)

Run validation to see specific errors:

```bash
python scripts/manage_project_config.py validate
```
