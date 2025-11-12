# CORTAP-RPT - Product Requirements Document

**Author:** Bob
**Date:** 2025-11-12
**Version:** 1.0

---

## Executive Summary

CORTAP-RPT is a document generation system that automates the creation of FTA (Federal Transit Administration) CORTAP audit reports by pulling data from the Riskuity compliance management system and populating Microsoft Word templates with intelligent conditional logic.

**The Problem:** Currently, 20+ FTA auditors manually create complex, formatted audit reports for 36+ CORTAP reviews annually. This manual process is time-consuming, error-prone, and takes valuable time away from their core work: conducting thorough compliance audits. Each report requires meticulous formatting, conditional content selection based on review type, and accurate data population across multiple templates.

**The Solution:** CORTAP-RPT serves as a bridge between Riskuity (the data source) and polished Word documents (the deliverables). When an auditor completes a CORTAP review in Riskuity, they can generate publication-ready documents with a single click. The system handles all the complex formatting, conditional logic, and data transformation automatically.

**The Impact:** Auditors shift their focus from document formatting to audit quality. What previously took hours of careful manual work now takes seconds, while ensuring consistency and accuracy across all generated reports.

### What Makes This Special

**Auditor Liberation:** This system removes the burden of document creation and formatting from auditors, allowing them to focus entirely on their expertise—conducting thorough, high-quality compliance audits. The magic moment is when an auditor clicks "Generate Document" and receives a perfectly formatted, professionally polished report ready for review, without touching Word.

### ⚠️ Critical Integration Dependency

**CORTAP-RPT relies heavily on data from Riskuity.** Several required fields (review type, exit conference format, ERF tracking) may not currently exist in Riskuity and will need to be added. **See "Riskuity Integration Requirements" section** for complete field inventory, required changes, and critical questions that must be answered before Epic 2 development begins.

---

## Project Classification

**Technical Type:** Backend Service / Document Generation API
**Domain:** Government Compliance & Audit Reporting
**Complexity:** Moderate (Domain-specific business rules, complex conditional logic)

CORTAP-RPT is a **document generation microservice** that transforms structured compliance data into formatted Word documents. It sits between Riskuity (the compliance management platform) and end users (auditors), providing an intelligent templating layer.

**Key Technical Characteristics:**
- **Integration-heavy:** Pulls data from Riskuity API, generates documents, stores in AWS S3
- **Business logic-rich:** Complex conditional content rules based on review type, findings, and project configuration
- **Template-driven:** Word document templates with merge fields and conditional sections
- **Asynchronous processing:** Background job queue for document generation (v2)

### Domain Context

**Federal Transit Administration (FTA) Compliance Reviews**

CORTAP reviews are comprehensive compliance audits conducted by the FTA to assess transit agencies' adherence to federal requirements across 23 review areas (Legal, Financial Management, Procurement, ADA compliance, Safety Plans, etc.).

**Domain-Specific Considerations:**
- **Review Types:** Three distinct types (Triennial Review, State Management Review, Combined) with different regulatory frameworks and reporting requirements
- **Standardized Templates:** Government-mandated report formats that must preserve exact formatting and structure
- **Compliance Rigor:** Reports are official federal documents used for regulatory enforcement and funding decisions
- **Audit Workflow:** Multi-phase process (pre-assessment → desk review → scoping → site visit → findings → report → corrective action)
- **Deficiency Tracking:** Binary compliance assessment (Deficient vs Non-Deficient) with formal corrective action requirements
- **ERF (Enhanced Review Focus):** Special deep-dive reviews triggered by pre-assessment concerns

---

## Success Criteria

**Primary Success Metrics:**

1. **Auditor Time Savings:** Reduce document creation time from hours to minutes per report
   - Target: 90%+ time reduction for document generation
   - Measured by: Before/after time studies with auditors

2. **Document Quality & Consistency:** Zero formatting errors or inconsistencies in generated documents
   - Target: 100% of generated documents require no manual formatting fixes
   - Measured by: Audit manager review feedback

3. **Adoption Rate:** Auditors prefer the system over manual document creation
   - Target: 80%+ of CORTAP reports generated via CORTAP-RPT within 6 months
   - Measured by: Usage analytics (documents generated vs total reviews)

4. **Conditional Logic Accuracy:** Correct content selection based on review type and findings
   - Target: 100% accuracy in conditional content (no incorrect sections included/excluded)
   - Measured by: QA review of sample documents

5. **Template Preservation:** Word formatting matches original templates exactly
   - Target: Styles, headers, footers, page breaks preserved perfectly
   - Measured by: Visual comparison and auditor acceptance

**Secondary Success Metrics:**

6. **Proof of Concept Validation (Week 1):** Python libraries successfully preserve Word formatting with conditional logic
   - Target: Draft Audit Report template generates correctly with test data
   - Measured by: POC demo acceptance

7. **Scale Readiness:** System handles 36+ reviews for FY26 without performance degradation
   - Target: Support concurrent document generation by 20 auditors
   - Measured by: Load testing and production usage

### Business Metrics

**Operational Efficiency:**
- **Hours saved annually:** 36 reviews × 3 templates × 2-4 hours per template = 216-432 hours saved per fiscal year
- **Error reduction:** Eliminate manual data entry errors and formatting inconsistencies
- **Scalability:** Enable audit program growth (50-100+ reviews) without proportional staff increase

**Quality Improvements:**
- **Consistency:** All reports follow standardized format without variation
- **Compliance:** Reduce risk of missing required sections or using wrong templates
- **Speed to delivery:** Faster turnaround from site visit to draft report delivery

---

## Product Scope

### MVP - Minimum Viable Product

**Timeline:** 3 weeks POC → Production deployment for FY26 reviews

**Core Capabilities:**

1. **Single Document Generation (Synchronous)**
   - User selects CORTAP project from Riskuity
   - User selects template(s) to generate (Draft Audit Report as POC starting point)
   - User clicks "Generate Document"
   - System processes in foreground (user waits with progress indicator)
   - Generated document stored in AWS S3
   - Immediate download available

2. **Riskuity API Integration**
   - Pull complete assessment data for selected CORTAP project
   - Retrieve: Assessments, Surveys, Risks data
   - Authentication via API keys
   - Single endpoint call per data type

3. **Intelligent Template Engine**
   - Python-based document generation (python-docxtpl or docx-mailmerge - determined in Week 1 POC)
   - Preserve complex Word formatting (styles, headers, footers, page breaks)
   - Support for conditional sections and dynamic lists
   - Grammar helpers (is/are, a/an pluralization)

4. **Conditional Logic Engine** (Critical MVP Feature)
   - **Review Type Routing:** Select correct paragraphs based on Triennial/State Management/Combined
   - **Deficiency Detection:** Show/hide content blocks based on presence of deficiencies
   - **Alternative Content ([OR] blocks):** Display correct alternative based on data
   - **Conditional Sections ([ADD AS APPLICABLE]):** Include sections only when data exists (ERF, subrecipients)
   - **Table Display Logic:** Show deficiency table only if deficiencies exist
   - **Dynamic Lists ([LIST]):** Populate variable-length comma-separated lists

5. **Data Validation & User Feedback**
   - Pre-generation validation: Check for required vs optional fields
   - Warning messages for missing critical data
   - User choice: Proceed anyway, Cancel, or Review data
   - Clear error messages for generation failures

6. **Template Support**
   - **Primary:** Draft Audit Report (FY25_TRSMR_DraftFinalReport)
   - **Additional templates:** Cover Letter, Recipient Information Request Package (post-POC)
   - Template field metadata (required vs optional fields)

7. **AWS S3 Storage**
   - Automatic upload of generated documents
   - Download link generation
   - Simple storage structure (no versioning in MVP)

8. **React/Node Integration**
   - API endpoint: POST /generate-document
   - Parameters: project_id, template_id, user_id
   - Returns: download URL
   - Embedded "Generate Document" button in Riskuity UI

**MVP Explicitly Excludes:**
- Asynchronous job queue (v2)
- Batch document generation
- Document versioning
- Audit trails
- Access controls
- Template management UI
- PDF export
- Email notifications

### Growth Features (Post-MVP)

**Phase 2 Enhancements:**

1. **Asynchronous Job Processing**
   - Background job queue (Celery/Redis or AWS SQS)
   - Job status tracking (pending → processing → complete → failed)
   - Notification when complete (email or in-app)
   - Job history and retry logic

2. **Batch Document Generation**
   - Generate multiple templates for one project at once
   - Generate documents for multiple projects
   - Progress tracking for batch operations

3. **Additional Template Support**
   - All remaining CORTAP templates
   - Template versioning support
   - Template management interface

4. **Enhanced User Experience**
   - Document preview before final generation
   - Edit generated document metadata
   - Regenerate with corrections

5. **Audit Manager Workflow**
   - Review queue for generated documents
   - Approval workflow before finalization
   - Comment/feedback capability

### Vision (Future)

**Long-term Capabilities:**

1. **Multi-Format Output**
   - PDF generation alongside Word
   - HTML/web preview
   - Editable vs final formats

2. **Intelligence & Automation**
   - AI-suggested findings based on historical patterns
   - Auto-complete common deficiency descriptions
   - Anomaly detection in assessment data

3. **Analytics & Insights**
   - Cross-year trend analysis
   - Recipient performance tracking
   - Common deficiency patterns
   - Report generation efficiency metrics

4. **Template Studio**
   - Visual template editor
   - Drag-and-drop field mapping
   - Test mode with sample data
   - Template validation

5. **Multi-Fiscal-Year Support**
   - FY27, FY28+ template variants
   - Framework evolution tracking
   - Historical comparison

6. **Extensibility**
   - Support for other audit types beyond CORTAP
   - Plugin architecture for custom business rules
   - API for third-party integrations

---

## Backend Service / Document Generation API - Specific Requirements

### API Specification

**CORTAP-RPT exposes a REST API for document generation:**

**Primary Endpoint:**

```
POST /api/v1/generate-document
```

**Request Body:**
```json
{
  "project_id": "string",          // Riskuity CORTAP project ID
  "template_id": "string",         // Template identifier (e.g., "draft-audit-report")
  "user_id": "string",             // Auditor user ID
  "format": "docx"                 // Output format (MVP: docx only)
}
```

**Response (Synchronous - MVP):**
```json
{
  "status": "success",
  "document_id": "uuid",
  "download_url": "https://s3.amazonaws.com/...",
  "generated_at": "2025-11-12T10:30:00Z",
  "warnings": [
    "Optional field [recipient_phone] was missing - used default 'N/A'"
  ]
}
```

**Error Response:**
```json
{
  "status": "error",
  "error_code": "MISSING_REQUIRED_FIELD",
  "message": "Required field missing: [recipient_name]",
  "missing_fields": ["recipient_name", "review_type"],
  "can_proceed": false
}
```

**Status Codes:**
- `200 OK` - Document generated successfully
- `202 Accepted` - Job queued (async mode - v2)
- `400 Bad Request` - Missing required parameters or invalid data
- `401 Unauthorized` - Invalid API credentials
- `500 Internal Server Error` - Generation failure

**Additional Endpoints (MVP):**

```
GET /api/v1/templates
```
Returns list of available templates

```
GET /api/v1/validate-data
POST body: { project_id, template_id }
```
Validates data completeness without generating document

**Riskuity API Integration:**

CORTAP-RPT consumes the following Riskuity endpoints:

```
GET https://api.riskuity.com/v1/projects/{project_id}
GET https://api.riskuity.com/v1/projects/{project_id}/assessments
GET https://api.riskuity.com/v1/projects/{project_id}/surveys
GET https://api.riskuity.com/v1/projects/{project_id}/risks
```

### Authentication & Authorization

**Riskuity API Authentication:**
- Method: API Key-based authentication
- Header: `Authorization: Bearer {api_key}`
- Keys managed in environment configuration
- No user-level permissions (system-to-system)

**CORTAP-RPT API Authentication (from React/Node app):**
- Method: Shared secret or JWT (TBD during architecture)
- No user authentication in MVP
- All requests trusted from Riskuity application
- User ID passed for audit logging only

**MVP Simplifications:**
- No role-based access control
- No per-user permissions
- No document-level access restrictions
- Riskuity handles all authorization logic

---

## Functional Requirements

### FR-1: Document Generation Engine

**FR-1.1: Template Processing**
- System SHALL load Microsoft Word templates (.docx format) from configured storage location
- System SHALL preserve all original formatting: styles, fonts, colors, headers, footers, page breaks, table formatting
- System SHALL support templates up to 50 pages with complex formatting
- **Acceptance:** Generated document visually identical to manually populated template

**FR-1.2: Merge Field Population**
- System SHALL identify and replace all merge fields in format `[field_name]`
- System SHALL handle 50+ unique merge fields per template
- System SHALL apply smart defaults for missing optional fields ("N/A", "Not Applicable")
- System SHALL warn user if required fields are missing
- **Acceptance:** All merge fields correctly replaced with data or appropriate defaults

**FR-1.3: Template Library Management**
- System SHALL support multiple templates: Draft Audit Report, Cover Letter, RFI Package
- System SHALL allow template selection during generation request
- Templates stored in S3 and cached locally for performance
- **Acceptance:** User can select from available templates, system uses correct template

### FR-2: Conditional Logic Engine

This is the heart of CORTAP-RPT's intelligence. The system must implement 9 distinct conditional logic patterns.

**⚠️ Riskuity Dependency:** Each conditional logic pattern requires specific fields from Riskuity API. See "Riskuity Integration Requirements → Conditional Logic → Riskuity Field Dependencies" for complete field mapping and blocker analysis.

**FR-2.1: Review Type Routing**
- System SHALL accept `review_type` parameter with values: "Triennial Review" | "State Management Review" | "Combined Triennial and State Management Review"
- System SHALL select appropriate content based on review type throughout document
- For instructions like `[For Triennial Reviews, delete the below paragraph...]`, system SHALL:
  - Include paragraph A if review_type = "Triennial Review"
  - Include paragraph B if review_type = "State Management Review"
  - Include BOTH paragraphs if review_type = "Combined..."
- **Acceptance:** Correct paragraphs included/excluded based on review type across entire document

**FR-2.2: Deficiency Detection & Alternative Content**
- System SHALL analyze assessment data to determine if any deficiencies exist (Finding = D)
- For `[OR]` blocks, system SHALL display ONE alternative:
  - Block A: "Deficiencies were found in the areas listed below" (if hasDeficiencies = true)
  - Block B: "No deficiencies were found with any of FTA requirements" (if hasDeficiencies = false)
- **Acceptance:** Correct alternative content displayed based on deficiency presence

**FR-2.3: Conditional Section Inclusion**
- For sections marked `[ADD AS APPLICABLE]`, system SHALL:
  - Include entire section if triggering data exists
  - Omit entire section if triggering data does not exist
- Examples:
  - ERF section: Include if erf_count > 0
  - Subrecipient section: Include if reviewed_subrecipients = true
- **Acceptance:** Conditional sections appear only when data warrants inclusion

**FR-2.4: Conditional Paragraph Selection**
- For instructions like `[If the Triennial Review included a review of subrecipient(s), include the below paragraph]`, system SHALL:
  - Evaluate condition based on data (reviewed_subrecipients flag)
  - Include paragraph if condition true
  - Omit paragraph if condition false
- **Acceptance:** Paragraphs conditionally included based on data-driven rules

**FR-2.5: Exit Conference Format Selection**
- System SHALL accept `exit_conference_format` parameter: "virtual" | "in-person"
- System SHALL include ONE of two mutually exclusive paragraphs based on format
- **Acceptance:** Correct exit conference paragraph selected

**FR-2.6: Deficiency Table Display**
- System SHALL show deficiency table ONLY if any review area has Finding = D
- If no deficiencies (all ND/NA): Hide table, show alternative text
- If deficiencies exist:
  - Display table with ALL 23 review areas
  - For each row: Show Review Area name and Finding status (D/ND/NA)
  - Populate detail columns (Deficiency Code, Description, Corrective Actions, Due Dates, Date Closed) ONLY for rows with Finding = D
  - Leave detail columns blank for ND/NA rows
- **Acceptance:** Table appears only when deficiencies exist; detail columns populated correctly

**FR-2.7: Dynamic List Population**
- System SHALL populate `[LIST]` placeholders with comma-separated values
- List types:
  - Deficiency areas: "Legal, Financial Management, Procurement"
  - ERF areas: "Technical Capacity, Maintenance"
  - Repeat deficiency areas
- System SHALL format lists appropriately (commas, "and" before last item)
- **Acceptance:** Lists correctly formatted and contextually appropriate

**FR-2.8: Dynamic Counts**
- System SHALL replace `[#]` with actual count
- Examples: `[#]` ERFs → "3 ERFs" or `[no]` → "no repeat deficiencies"
- System SHALL show count if > 0, show "no" if = 0
- **Acceptance:** Counts accurate and grammatically correct

**FR-2.9: Grammar Helpers**
- System SHALL apply pluralization rules:
  - `[is/are]`: "is" if count=1, "are" if count≠1
  - `[was/were]`: Same logic
  - `[an]`: "an" before vowels, "a" before consonants
- **Acceptance:** Grammar always correct based on context

### FR-3: Riskuity API Integration

**FR-3.1: Data Retrieval**
- System SHALL authenticate to Riskuity API using API keys
- System SHALL retrieve complete CORTAP project data:
  - Project configuration (review_type, recipient info, dates)
  - Assessment data for all 23 review areas
  - Survey responses
  - Risk data
  - ERF data
  - Subrecipient/contractor data
- System SHALL handle API errors gracefully (retries, timeouts)
- **Acceptance:** All required data successfully retrieved from Riskuity

**FR-3.2: Data Transformation**
- System SHALL transform Riskuity API responses into template data model
- System SHALL map API field names to template merge field names
- System SHALL calculate derived fields (deficiency_count, hasDeficiencies boolean)
- System SHALL aggregate data for lists (deficiency_areas array → comma-separated string)
- **Acceptance:** API data correctly transformed for template engine

**FR-3.3: Data Completeness Validation**
- System SHALL maintain metadata of required vs optional fields per template
- System SHALL validate data completeness before generation
- System SHALL categorize missing fields:
  - **Critical:** Block generation, show error
  - **Optional:** Warn user, allow proceed with defaults
- System SHALL return list of missing fields with severity
- **Acceptance:** User informed of missing data before generation proceeds

### FR-4: AWS S3 Storage Integration

**FR-4.1: Document Upload**
- System SHALL upload generated documents to configured S3 bucket
- System SHALL use organized naming convention: `{project_id}/{template_id}/{timestamp}_{document_name}.docx`
- System SHALL set appropriate S3 permissions for access
- System SHALL handle upload failures with retry logic
- **Acceptance:** Generated documents reliably stored in S3

**FR-4.2: Download URL Generation**
- System SHALL generate pre-signed S3 URLs for document download
- URLs SHALL be valid for configurable duration (default: 24 hours)
- System SHALL return download URL in API response
- **Acceptance:** Users can download generated documents via provided URL

### FR-5: User Interaction & Feedback

**FR-5.1: Progress Indication**
- System SHALL display progress indicator during synchronous generation (MVP)
- System SHALL provide estimated time remaining
- System SHALL allow user to wait during processing (no timeout)
- **Acceptance:** User sees clear feedback that system is working

**FR-5.2: Error Handling & User Communication**
- System SHALL provide clear, actionable error messages
- Error types:
  - Missing required data: "Required field [recipient_name] is missing. Please update project in Riskuity."
  - API failures: "Unable to retrieve data from Riskuity. Please try again."
  - Generation failures: "Document generation failed. Error: [specific issue]"
- System SHALL offer user choices where appropriate: Proceed/Cancel/Review
- **Acceptance:** Users understand what went wrong and how to fix it

**FR-5.3: Validation Warnings**
- System SHALL warn user before generation if optional fields missing
- System SHALL list all missing optional fields
- System SHALL explain how defaults will be applied
- User can choose: Proceed with defaults, Cancel to fix data, Review data
- **Acceptance:** User informed and empowered to make decision

### FR-6: React/Node Integration

**FR-6.1: Embedded UI Component**
- React/Node app SHALL display "Generate Document" button in Riskuity project view
- Button SHALL be contextually aware (enabled only when project has required data)
- Click SHALL trigger template selection modal
- **Acceptance:** Auditors can initiate document generation from Riskuity UI

**FR-6.2: API Communication**
- React app SHALL call CORTAP-RPT API with project context
- React app SHALL handle API responses (success, error, warnings)
- React app SHALL provide download link to user upon success
- **Acceptance:** Seamless integration between Riskuity and CORTAP-RPT

---

## Non-Functional Requirements

### Performance

**NFR-1.1: Document Generation Speed**
- System SHALL generate documents within 30 seconds for standard reports (up to 25 pages)
- System SHALL generate documents within 60 seconds for complex reports (25-50 pages)
- Synchronous generation acceptable in MVP given these timeframes
- **Rationale:** Auditors can wait 30-60 seconds; faster than manual process (hours)

**NFR-1.2: API Response Time**
- Data validation endpoint SHALL respond within 2 seconds
- Template list endpoint SHALL respond within 1 second
- **Rationale:** Interactive UI requires responsive feedback

**NFR-1.3: Concurrent User Support**
- System SHALL support 20 concurrent document generation requests (1 per auditor)
- System SHALL handle 5 concurrent generations without performance degradation in MVP
- **Rationale:** Unlikely more than 5 auditors generate documents simultaneously

### Reliability

**NFR-2.1: Availability**
- System SHALL target 95% uptime during business hours (9am-5pm ET, weekdays)
- Planned maintenance windows acceptable with 24-hour notice
- **Rationale:** MVP timeline; not mission-critical uptime requirement

**NFR-2.2: Data Integrity**
- System SHALL NOT modify source data in Riskuity
- System SHALL generate identical documents given identical input data (deterministic)
- System SHALL verify S3 upload success before returning success response
- **Rationale:** Reports are official federal documents; accuracy critical

**NFR-2.3: Error Recovery**
- System SHALL retry Riskuity API calls up to 3 times on failure
- System SHALL retry S3 uploads up to 2 times on failure
- System SHALL log all generation attempts (success and failure)
- **Rationale:** Network issues should not cause permanent failures

### Security

**NFR-3.1: Data Protection**
- System SHALL use HTTPS for all API communication
- System SHALL encrypt Riskuity API keys in configuration
- System SHALL use AWS S3 encryption at rest for stored documents
- **Rationale:** Government compliance data requires basic security

**NFR-3.2: Access Control (Deferred to Riskuity)**
- Riskuity handles user authentication and authorization
- CORTAP-RPT trusts all requests from Riskuity application
- No document-level access control in MVP
- **Rationale:** Simplified MVP; Riskuity is trusted system

**NFR-3.3: Audit Logging**
- System SHALL log: user_id, project_id, template_id, timestamp, outcome for each generation
- Logs stored for 90 days minimum
- **Rationale:** Basic accountability; useful for troubleshooting

### Scalability

**NFR-4.1: Volume Capacity**
- System SHALL support 36 CORTAP reviews × 3 templates = 108 documents for FY26
- System SHALL support growth to 100 reviews (300 documents) in FY27
- **Rationale:** Known current volume with reasonable growth projection

**NFR-4.2: Template Scalability**
- System architecture SHALL support adding new templates without code changes
- Template configuration SHALL be data-driven
- **Rationale:** Additional templates needed post-MVP

**NFR-4.3: Future Async Support**
- Architecture SHALL accommodate async job queue in v2 without major refactor
- Design with async patterns in mind even if MVP is synchronous
- **Rationale:** Known v2 requirement; plan ahead

### Integration

**NFR-5.1: Riskuity API Compatibility**
- System SHALL use Riskuity API v1 endpoints (documented at https://api.riskuity.com/docs)
- System SHALL handle API schema changes gracefully (fail with clear error, not crash)
- System SHALL validate API responses before processing
- **Rationale:** External dependency; must handle changes

**NFR-5.2: AWS Dependency**
- System SHALL deploy to AWS infrastructure
- System SHALL use AWS S3 for document storage
- System SHALL be deployable as AWS Lambda, ECS container, or EC2 instance (TBD in architecture)
- **Rationale:** Existing infrastructure; cost-effective

### Maintainability

**NFR-6.1: Code Quality**
- Python code SHALL follow PEP 8 style guidelines
- System SHALL include comprehensive unit tests (70%+ coverage)
- System SHALL include integration tests for Riskuity API and S3
- **Rationale:** Team maintains code; quality standards important

**NFR-6.2: Documentation**
- System SHALL include API documentation (OpenAPI/Swagger)
- System SHALL include deployment documentation
- System SHALL document conditional logic rules and template field mappings
- **Rationale:** Knowledge transfer; long-term maintenance

**NFR-6.3: Configuration Management**
- All environment-specific configuration SHALL be externalized (environment variables)
- No hardcoded credentials or URLs
- **Rationale:** Deploy to dev/staging/prod environments

---

## Implementation Planning

### POC Phase Breakdown (3 Weeks)

**Week 1: Template Library Validation** ⚡ CRITICAL
- Test python-docxtpl vs docx-mailmerge with Draft Audit Report template
- Validate formatting preservation with varying data scenarios
- Implement basic conditional logic (review type routing)
- **Decision Point:** Python approach validated OR pivot to .NET

**Week 2: Core Engine Development**
- Riskuity API integration and data transformation
- Complete conditional logic engine (all 9 patterns)
- Data validation engine
- S3 storage integration

**Week 3: Integration & Testing**
- React/Node API integration
- End-to-end testing with real Riskuity data
- User acceptance testing with auditors
- Deployment to AWS

### Epic Breakdown Required

Requirements will be decomposed into epics and bite-sized stories optimized for 200k context development sessions.

**Anticipated Epic Structure:**
1. **Epic 1:** Template Engine & Formatting Preservation
2. **Epic 2:** Conditional Logic Engine (9 patterns)
3. **Epic 3:** Riskuity API Integration & Data Transform
4. **Epic 4:** Validation Engine & User Feedback
5. **Epic 5:** AWS S3 Storage & Document Management
6. **Epic 6:** React/Node Integration
7. **Epic 7:** Testing & Deployment

**Next Step:** Run `workflow create-epics-and-stories` to create the detailed implementation breakdown.

---

## References

**Source Documents:**
- Brainstorming Session: `docs/bmm-brainstorming-session-2025-11-12.md`
- Template Analysis: Draft Audit Report (`docs/requirements/State_RO_Recipient#_Recipient Name_FY25_TRSMR_DraftFinalReport.docx`)
- Riskuity API Documentation: https://api.riskuity.com/docs

**Key Decisions from Discovery:**
- Build vs Buy: Build with Python (team expertise, cost-effective)
- Template Library: python-docxtpl (preferred) or docx-mailmerge (to be validated in Week 1)
- Data Source: Riskuity API only (Excel files eliminated for simplification)
- MVP Pattern: Synchronous generation (async job queue deferred to v2)

---

## Riskuity Integration Requirements

### Critical Integration Dependency

**CORTAP-RPT cannot function without accurate, complete data from Riskuity.** This section defines the explicit data contract between systems, identifies required Riskuity changes, and documents dependencies that could block CORTAP-RPT development.

**Key Finding:** Several conditional logic patterns depend on fields that may not currently exist in Riskuity. These must be verified and added before CORTAP-RPT can implement full functionality.

---

### Riskuity API Data Contract

CORTAP-RPT consumes four Riskuity API endpoints. The following tables specify required fields, their purpose, and current verification status.

#### Endpoint 1: Project Metadata

**`GET /v1/projects/{project_id}`**

Provides project configuration, recipient information, and review parameters.

| Field Name | Data Type | Required? | Used For | Verification Status |
|------------|-----------|-----------|----------|---------------------|
| `recipient_name` | string | ✅ Critical | Template merge field | ❓ Unknown |
| `recipient_acronym` | string | ✅ Critical | Template merge field | ❓ Unknown |
| `region_number` | integer (1-10) | ✅ Critical | Template merge field | ❓ Unknown |
| **`review_type`** | enum | ✅ Critical | **CL-1: Review Type Routing** | ❓ Unknown - LIKELY MISSING |
| **`exit_conference_format`** | enum | ✅ Required | **CL-5: Exit Format Selection** | ❓ Unknown - LIKELY MISSING |
| `site_visit_start_date` | date (ISO 8601) | ✅ Required | Template merge field | ❓ Unknown |
| `site_visit_end_date` | date (ISO 8601) | ✅ Required | Template merge field | ❓ Unknown |
| `report_date` | date (ISO 8601) | ✅ Required | Template merge field | ❓ Unknown |
| `recipient_contact_name` | string | ⚠️ Optional | Template merge field | ❓ Unknown |
| `recipient_phone` | string | ⚠️ Optional | Template merge field | ❓ Unknown |
| `recipient_email` | email | ⚠️ Optional | Template merge field | ❓ Unknown |
| **`reviewed_subrecipients`** | boolean | ⚠️ Optional | **CL-4: Conditional Paragraphs** | ❓ Unknown - LIKELY MISSING |
| `subrecipient_name` | string | ⚠️ Optional | Template merge field, CL-4 | ❓ Unknown |
| `contractor_name` | string | ⚠️ Optional | Template merge field | ❓ Unknown |
| `contractor_firm` | string | ⚠️ Optional | Template merge field | ❓ Unknown |
| `audit_team` | array | ✅ Required | Team member list | ❓ Unknown |

**Critical Field Requirements:**

**`review_type`** - MUST be one of these EXACT values (case-sensitive):
- `"Triennial Review"`
- `"State Management Review"`
- `"Combined Triennial and State Management Review"`

**`exit_conference_format`** - MUST be one of:
- `"virtual"`
- `"in-person"`

**`reviewed_subrecipients`** - Boolean flag OR derived from `subrecipient_name != null`

---

#### Endpoint 2: Assessment Findings

**`GET /v1/projects/{project_id}/assessments`**

Returns findings for all 23 CORTAP review areas. This is the MOST CRITICAL endpoint for conditional logic.

| Field Name | Data Type | Required? | Used For | Verification Status |
|------------|-----------|-----------|----------|---------------------|
| `assessments` | array (23 items) | ✅ Critical | All deficiency logic | ❓ Unknown |
| `assessments[].review_area` | string | ✅ Critical | CL-7: Dynamic Lists | ❓ Unknown |
| **`assessments[].finding`** | enum | ✅ Critical | **CL-2, CL-6: Deficiency Logic** | ❓ Unknown - VERIFY VALUES |
| `assessments[].deficiency_code` | string | ⚠️ Conditional | CL-6: Deficiency Table | ❓ Unknown |
| `assessments[].description` | text | ⚠️ Conditional | CL-6: Deficiency Table | ❓ Unknown |
| `assessments[].corrective_action` | text | ⚠️ Conditional | CL-6: Deficiency Table | ❓ Unknown |
| `assessments[].due_date` | date | ⚠️ Conditional | CL-6: Deficiency Table | ❓ Unknown |
| `assessments[].date_closed` | date | ⚠️ Conditional | CL-6: Deficiency Table | ❓ Unknown |

**Critical Field Requirements:**

**`assessments[].finding`** - MUST be one of these EXACT values:
- `"D"` (Deficient)
- `"ND"` (Non-Deficient)
- `"NA"` (Not Applicable)

**Note:** Deficiency detail fields (code, description, corrective_action, due_date, date_closed) are ONLY required when `finding = "D"`.

**Derived Fields** (calculated by CORTAP-RPT from assessments data):
- `has_deficiencies` = any(assessment.finding == "D")
- `deficiency_count` = count(assessment.finding == "D")
- `deficiency_areas` = list of review_area names where finding == "D"

---

#### Endpoint 3: Enhanced Review Focus (ERF)

**`GET /v1/projects/{project_id}/risks`** OR **`GET /v1/projects/{project_id}/erf`**

Enhanced Review Focus areas requiring deep-dive investigation.

| Field Name | Data Type | Required? | Used For | Verification Status |
|------------|-----------|-----------|----------|---------------------|
| **`erf_items`** | array | ⚠️ Optional | **CL-3, CL-8: ERF Section** | ❓ Unknown - MAY NOT EXIST |
| `erf_items[].area` | string | ⚠️ Optional | CL-3, CL-7: Lists | ❓ Unknown |
| `erf_items[].description` | text | ⚠️ Optional | CL-3: ERF details | ❓ Unknown |

**Derived Fields:**
- `erf_count` = count(erf_items)
- `erf_areas` = list of erf_items[].area
- `show_erf_section` = erf_count > 0

**Critical Question:** Does Riskuity currently track ERF data? If not, should it be added or managed externally?

---

#### Endpoint 4: Surveys (Low Priority for MVP)

**`GET /v1/projects/{project_id}/surveys`**

Survey response data. Usage TBD based on template requirements.

| Field Name | Data Type | Required? | Used For | Verification Status |
|------------|-----------|-----------|----------|---------------------|
| `surveys` | array | ⚠️ Optional | Future templates | ❓ Unknown |

**Status:** Low priority for MVP. May be used for future template enhancements.

---

### Required Riskuity Changes

The following changes are **likely required** in Riskuity before CORTAP-RPT can function fully:

#### 1. New Fields in Project Profile

**Fields to Add:**

| Field | UI Component | Location | Default Value | Priority |
|-------|-------------|----------|---------------|----------|
| `review_type` | Dropdown (3 options) | Project Configuration | (none - must select) | 🔴 CRITICAL |
| `exit_conference_format` | Radio buttons (2 options) | Project Configuration | "virtual" | 🟠 HIGH |
| `reviewed_subrecipients` | Checkbox | Project Configuration | false | 🟡 MEDIUM |

**Proposed UI Layout:**

```
┌─────────────────────────────────────────────────┐
│ CORTAP Review Configuration                     │
├─────────────────────────────────────────────────┤
│                                                  │
│ Review Type: * [Required Dropdown]              │
│   • Triennial Review                            │
│   • State Management Review                     │
│   • Combined Triennial and State Management     │
│                                                  │
│ Exit Conference Format: * [Required]            │
│   ○ Virtual     ○ In-Person                     │
│                                                  │
│ ☐ Subrecipients Reviewed                        │
│   If checked:                                   │
│   Subrecipient Name: [Text field]               │
│                                                  │
└─────────────────────────────────────────────────┘
```

#### 2. Enhanced Review Focus (ERF) Tracking

**If ERF is NOT currently tracked in Riskuity:**

Add ERF tracking capability:
- New table/module for ERF items
- Link ERF items to review areas
- Capture ERF rationale/description
- Expose via API endpoint

**Alternative:** Track ERF externally if Riskuity roadmap doesn't support this.

#### 3. Assessment Data Completeness

**Ensure:**
- All 23 review areas are present in assessments endpoint
- When `finding = "D"`, deficiency details are captured in Riskuity UI
- Riskuity enforces required fields for deficiencies

---

### Conditional Logic → Riskuity Field Dependencies

This table maps each conditional logic pattern to required Riskuity fields.

| CL-ID | Pattern | Riskuity Field(s) Required | Blocker Level | Impact if Missing |
|-------|---------|---------------------------|---------------|-------------------|
| **CL-1** | Review Type Routing | `review_type` | 🔴 CRITICAL | ALL type-specific content incorrect |
| **CL-2** | Deficiency Detection | `assessments[].finding` | 🔴 CRITICAL | Core deficiency logic broken |
| **CL-3** | Conditional Sections | `erf_items`, `reviewed_subrecipients` | 🟡 MEDIUM | ERF/subrecipient sections missing |
| **CL-4** | Conditional Paragraphs | `reviewed_subrecipients` | 🟡 MEDIUM | Subrecipient paragraphs missing |
| **CL-5** | Exit Format Selection | `exit_conference_format` | 🟡 MEDIUM | One paragraph affected |
| **CL-6** | Deficiency Table | All `assessments[]` fields | 🔴 CRITICAL | Entire 23-row table broken |
| **CL-7** | Dynamic Lists | `assessments[].review_area`, `erf_items[].area` | 🟠 HIGH | List formatting affected |
| **CL-8** | Dynamic Counts | Derived from other fields | 🟡 MEDIUM | Count display affected |
| **CL-9** | Grammar Helpers | Uses counts from other fields | ❌ None | Pure logic, no dependency |

**Blocker Summary:**
- 🔴 **3 CRITICAL blockers** - Without these, major functionality is broken
- 🟠 **1 HIGH blocker** - Affects important features
- 🟡 **4 MEDIUM blockers** - Specific sections/features only
- ❌ **1 No dependency** - Pure logic

---

### Implementation Phase Dependencies

**Phase 1: Foundation (Epic 1) - Weeks 1-3**
- ✅ **NO Riskuity dependencies** - Can proceed immediately
- Stories 1.1-1.6 can be completed with mock data

**Phase 2: Conditional Logic (Epic 2) - Weeks 4-5**
- 🔴 **BLOCKED** without Riskuity field verification
- 6 out of 8 stories depend on Riskuity fields
- **Can use mock data** if real API not ready, but must match exact schema

**Phase 3: Riskuity Integration (Epic 3) - Week 6**
- 🔴 **FULLY BLOCKED** without API access and confirmed field schema
- All 3 stories require working Riskuity API

**Risk:** If Riskuity changes are delayed, Epic 2 and Epic 3 timelines slip.

---

### Critical Questions for Riskuity Team

**These questions MUST be answered before Epic 2 implementation begins:**

#### CRITICAL Priority (Answer First)

1. **Review Type Field:**
   - Does Riskuity currently capture "Review Type" (Triennial/State Management/Combined)?
   - If yes, what is the exact field name and possible values?
   - If no, can this be added as a dropdown in the project profile? Timeline?

2. **Assessment Findings:**
   - What are the EXACT values stored for assessment findings? ("D"/"ND"/"NA" or different?)
   - Are all 23 CORTAP review areas guaranteed to be present in the assessments endpoint?
   - If finding = "D", are deficiency details (code, description, corrective_action) required fields in Riskuity UI?

3. **Exit Conference Format:**
   - Does Riskuity capture whether the exit conference was virtual or in-person?
   - If no, can this be added as a radio button (virtual/in-person)? Where in the UI?

#### HIGH Priority

4. **Enhanced Review Focus (ERF):**
   - Does Riskuity have a concept of "Enhanced Review Focus" areas?
   - If yes, how is ERF data stored and accessed via API?
   - If no, should ERF be tracked in Riskuity or handled externally?

5. **Subrecipient Review:**
   - How does Riskuity indicate that subrecipients were reviewed?
   - Is there a `reviewed_subrecipients` boolean flag?
   - Or should CORTAP-RPT infer this from `subrecipient_name != null`?

6. **API Response Schema:**
   - Can you provide sample JSON responses for all 4 endpoints?
   - Are there API documentation (Swagger/OpenAPI) specs available?

#### MEDIUM Priority

7. **Audit Team Personnel:**
   - Where is audit team information stored? (project endpoint or separate?)
   - Can multiple team members be assigned to a project?

8. **Date Fields:**
   - What date format does Riskuity use in API responses (ISO 8601, Unix timestamp)?
   - Are dates stored in UTC or local timezone?

9. **Field Validation:**
   - Are required fields enforced in Riskuity UI?
   - What happens if optional fields are missing (null, empty string, omitted)?

10. **Data Completeness:**
    - At what point in the workflow is data "complete" for report generation?
    - Should CORTAP-RPT validate data completeness or assume Riskuity enforces it?

#### Integration Logistics

11. **API Access:**
    - What is the process for obtaining API credentials for dev/test?
    - Is there a sandbox/test environment available?
    - What are the rate limits?

12. **Change Management:**
    - If new fields need to be added to Riskuity, what is the typical timeline?
    - Would schema changes require API versioning (v2)?
    - Can we coordinate joint testing once Riskuity changes are deployed?

---

### Risk Mitigation Strategies

**If Riskuity changes are delayed:**

| Scenario | Mitigation | Trade-off |
|----------|-----------|-----------|
| `review_type` missing | Hard-code to "Triennial Review" for testing | No multi-type support, blocks CL-1 |
| `exit_conference_format` missing | Default to "virtual" | Wrong paragraph in some cases |
| `erf_items` missing | Omit ERF section entirely | Missing functionality |
| Assessment fields incomplete | Use mock/test data that matches documented schema | Cannot test with real Riskuity |
| API access delayed | Build with mock API responses | Integration testing blocked |

**Recommended Development Approach:**
1. **Week 1-2:** Build Epic 1 (Foundation) with mock data
2. **Week 3:** Receive Riskuity field confirmation, update mock data
3. **Week 4-5:** Build Epic 2 (Conditional Logic) with validated mock data
4. **Week 6+:** Integrate with real Riskuity API

**Critical Path:** Riskuity field verification must complete by end of Week 2 to avoid Epic 2 delays.

---

### Open Issues & Assumptions

**Current Assumptions (TO BE VALIDATED):**

| Assumption | Risk Level | Validation Method |
|-----------|------------|-------------------|
| Riskuity API uses JSON REST format | LOW | Verify with API docs |
| All 4 endpoints exist and are accessible | MEDIUM | Test API access |
| `review_type` field does NOT currently exist | HIGH | ⚠️ **Confirm with Riskuity team** |
| Assessment findings use "D"/"ND"/"NA" values | HIGH | ⚠️ **Check actual database values** |
| ERF data is NOT currently tracked | MEDIUM | ⚠️ **Confirm current ERF workflow** |
| Dates are in ISO 8601 format | LOW | Verify API response samples |

**Unresolved Questions:**
1. Who is responsible for data quality validation? (Riskuity enforces vs CORTAP-RPT validates)
2. What should CORTAP-RPT do if required fields are missing from Riskuity API?
3. How will API schema changes be communicated and versioned?
4. What are Riskuity API performance characteristics (latency, rate limits)?

---

## Appendix: Conditional Logic Rule Reference

**Complete Business Rules for Template Processing:**

| Rule ID | Pattern | Trigger | Action | Example |
|---------|---------|---------|--------|---------|
| CL-1 | Review Type Routing | `review_type` parameter | Include/exclude paragraphs based on type | `[For Triennial Reviews, delete...]` |
| CL-2 | Deficiency Detection | Any Finding = D | Show/hide alternative content | `[OR]` blocks |
| CL-3 | Conditional Sections | Data existence check | Include/omit entire sections | `[ADD AS APPLICABLE]` |
| CL-4 | Conditional Paragraphs | Boolean data flags | Include/omit specific paragraphs | `[If subrecipients reviewed...]` |
| CL-5 | Exit Format Selection | `exit_conference_format` | Select one of two paragraphs | virtual vs in-person |
| CL-6 | Table Display | hasDeficiencies boolean | Show table or alternative text | 23-row deficiency table |
| CL-7 | Dynamic Lists | Array data | Comma-separated formatting | `[LIST]` areas |
| CL-8 | Dynamic Counts | Numeric data | Count or "no" | `[#]` or `[no]` |
| CL-9 | Grammar Helpers | Numeric context | Pluralization rules | `[is/are]`, `[a/an]` |

**Template Field Inventory:**

**Critical (Block generation if missing):**
- `[recipient_name]`
- `[recipient_acronym]`
- `[review_type]` - Triennial | State Management | Combined
- `[region_number]`

**Required (Warn if missing, allow proceed):**
- Date fields: `[Month]`, `[Day]` for all dates
- Personnel: `[Last Name]`, `[FTA Title]`
- Contact: `[phone number]`, `[email]`

**Optional (Default to "N/A" if missing):**
- `[subrecipient_name]`
- `[contractor_name]`
- `[contractor_firm]`

**Conditional (Only required if condition met):**
- `[erf_count]` - Required if ERF exists
- `[exit_conference_format]` - Required for format selection
- Deficiency details - Required if Finding = D

---

## Next Steps

**CRITICAL - Immediate Actions (This Week):**
1. 🔴 **Send Questions to Riskuity Team** - Review "Critical Questions for Riskuity Team" section above and obtain answers before Epic 2 begins
2. 🔴 **Request Riskuity API Access** - Obtain credentials, documentation, and sample API responses
3. 🔴 **Schedule Riskuity Integration Meeting** - Discuss required field additions, timeline, and change management process

**Short-Term Actions (Weeks 1-2):**
4. ✅ **Epic & Story Breakdown** - Run: `workflow create-epics-and-stories`
5. ✅ **Architecture Design** - Run: `workflow create-architecture` (recommended before coding)
6. ⏭️ **Create Mock Riskuity API Responses** - Based on documented field requirements until real API available

**WARNING:** Epic 2 (Conditional Logic) and Epic 3 (Riskuity Integration) are BLOCKED until Riskuity field verification is complete. See "Riskuity Integration Requirements" section for details.
4. ⏭️ **Development** - Start Week 1 POC with template library validation

**Workflow Sequence:**
- PRD (Complete) → Epics & Stories → Architecture → Sprint Planning → Development

---

_This PRD captures the essence of CORTAP-RPT: **Liberating auditors from document formatting so they can focus on audit quality.**_

_The magic moment: An auditor clicks "Generate Document" and receives a perfectly formatted, professionally polished report ready for review—transforming hours of tedious work into seconds of satisfaction._

_Created through collaborative discovery between Bob and AI Business Analyst Mary on 2025-11-12._
