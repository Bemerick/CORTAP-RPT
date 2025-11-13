# CORTAP-RPT - Epic and Story Breakdown

**Project:** CORTAP-RPT
**Created:** 2025-11-12
**Created By:** John (Product Manager)

---

## Epic Overview

This document decomposes the CORTAP-RPT PRD into 7 implementation epics with bite-sized user stories. Each story is designed for completion by a single development agent in one focused session.

**Project Type:** Greenfield - Document Generation Microservice
**Tech Stack:** Python 3.11 + FastAPI + python-docxtpl + AWS Lambda + S3
**Architecture:** docs/architecture.md

---

## Epic 1: Foundation & Template Engine

**Epic Goal:** Establish the FastAPI project foundation and implement core document generation capability with python-docxtpl, enabling basic merge field replacement and Word formatting preservation.

**Business Value:** Creates the technical foundation for all subsequent development and proves that Word formatting can be preserved programmatically.

**Architectural Components:** `app/main.py`, `app/config.py`, `services/document_generator.py`, `utils/grammar.py`, `templates/*.docx`

---

### Story 1.1: Initialize FastAPI Project Structure

As a developer,
I want to set up the FastAPI project with the recommended starter template,
So that we have a production-ready foundation with proper structure and tooling.

**Acceptance Criteria:**

**Given** I have Python 3.11.14 installed
**When** I run the FastAPI template CLI commands from architecture.md
**Then** The project structure matches architecture.md specification

**And** The following are configured:
- FastAPI app with async support
- Pydantic models structure
- Environment-based configuration (`.env` support)
- pytest test structure
- Docker setup
- Git repository initialized with `.gitignore`

**And** Unused scaffolding is removed:
- Remove JWT auth if not needed for MVP
- Remove SQLAlchemy database models (keep ORM for v2 job queue metadata only)
- Keep core FastAPI structure

**And** Additional dependencies are installed:
- python-docxtpl 0.20.1
- boto3 1.40.x
- httpx (latest)
- mangum 0.19.0 (Lambda adapter)

**Prerequisites:** None - this is the first story

**Technical Notes:**
- Follow architecture.md Project Initialization section (lines 7-34)
- Use `fastapi-template-cli` with SQLAlchemy option: `fastapi-template new cortap-rpt --orm sqlalchemy --type api`
- Create `requirements.txt` and `requirements-dev.txt` as specified
- Implement `app/config.py` using Pydantic Settings with fields: `riskuity_api_key`, `riskuity_base_url`, `s3_bucket_name`, `aws_region`, `log_level`
- Create `.env.example` template
- Follow Module Structure Pattern from architecture.md (lines 197-228)

---

### Story 1.2: Implement Structured JSON Logging

As a developer,
I want structured JSON logging for CloudWatch compatibility,
So that we can trace requests and debug issues in production Lambda environment.

**Acceptance Criteria:**

**Given** The FastAPI project is initialized
**When** I implement the logging utility in `app/utils/logging.py`
**Then** The `JSONFormatter` class formats logs as JSON with required fields

**And** All logs include:
- `timestamp` (UTC, ISO format)
- `level` (DEBUG, INFO, WARNING, ERROR)
- `service` ("cortap-rpt")
- `module` (module name)
- `function` (function name)
- `message` (log message)
- `correlation_id` (if available)

**And** The `get_logger(name)` function returns configured logger
**And** Log level is configurable via environment variable
**And** Exception stack traces are included in error logs

**Prerequisites:** Story 1.1 (project structure)

**Technical Notes:**
- Implement exactly as specified in architecture.md Logging Strategy (lines 427-481)
- Use standard library `logging` module with custom `JSONFormatter`
- Never log sensitive data (API keys, PII)
- Example usage: `logger.info("message", extra={"correlation_id": id})`

---

### Story 1.3: Implement Custom Exception Hierarchy

As a developer,
I want a custom exception hierarchy for domain-specific errors,
So that we can provide meaningful error messages and proper HTTP status codes.

**Acceptance Criteria:**

**Given** The project structure is initialized
**When** I create `app/exceptions.py` with custom exceptions
**Then** The following exception classes are defined:

- `CORTAPError` (base) with `message`, `error_code`, `details` attributes
- `RiskuityAPIError` (for Riskuity API failures)
- `DocumentGenerationError` (for document generation failures)
- `ValidationError` (for data validation failures)
- `S3StorageError` (for S3 operation failures)

**And** FastAPI exception handler is registered in `app/main.py`
**And** Handler converts `CORTAPError` to JSON response with:
- `error_code`
- `message`
- `details` dict
- `timestamp` (ISO format)
- `correlation_id`

**And** HTTP status codes map appropriately:
- `ValidationError` → 400 Bad Request
- `RiskuityAPIError` → 502 Bad Gateway or 500
- `DocumentGenerationError` → 500 Internal Server Error
- `S3StorageError` → 500 Internal Server Error

**Prerequisites:** Story 1.1 (project structure)

**Technical Notes:**
- Follow architecture.md Error Handling section (lines 375-425)
- Use `@app.exception_handler(CORTAPError)` decorator
- Never expose internal error details to API consumers (sanitize)
- Always log errors before raising with correlation_id

---

### Story 1.4: POC - Validate python-docxtpl with Draft Audit Report Template

As a developer,
I want to validate that python-docxtpl preserves Word formatting with the real Draft Audit Report template,
So that we confirm the technical approach before full implementation.

**Acceptance Criteria:**

**Given** I have the Draft Audit Report template (.docx file)
**When** I create a POC script using python-docxtpl
**Then** The script successfully:
- Loads the .docx template
- Replaces simple merge fields (e.g., `{{ recipient_name }}`, `{{ review_type }}`)
- Generates output .docx file

**And** The generated document preserves:
- All styles (fonts, colors, sizes)
- Headers and footers
- Page breaks
- Table formatting
- Paragraph formatting

**And** Visual comparison shows no formatting differences
**And** POC results are documented in `docs/poc-validation-report.md`

**Prerequisites:** Story 1.1 (project structure, python-docxtpl installed)

**Technical Notes:**
- This is the Week 1 POC from PRD line 633
- Use python-docxtpl `DocxTemplate` class
- Test with minimal data (3-5 merge fields)
- If formatting is not preserved, document issues and escalate
- Place template in `app/templates/draft-audit-report.docx`
- POC script can be standalone (`scripts/poc_docxtpl.py`) or test file

---

### Story 1.5: Implement DocumentGenerator Service Core

As a developer,
I want a DocumentGenerator service that loads templates and performs basic merge field replacement,
So that we have the foundation for document generation functionality.

**Acceptance Criteria:**

**Given** python-docxtpl POC is validated
**When** I implement `app/services/document_generator.py`
**Then** The `DocumentGenerator` class is created with:
- `__init__(self, template_dir: str)` constructor
- `async def generate(self, template_id: str, context: dict) -> BytesIO` method

**And** The service:
- Loads .docx templates from `app/templates/` directory
- Caches loaded templates in memory for performance
- Uses python-docxtpl to render template with context data
- Returns generated document as `BytesIO` (in-memory, never writes to disk)
- Raises `DocumentGenerationError` on failures

**And** Templates are validated on load:
- Template file exists
- Template is valid .docx format
- Basic Jinja2 syntax is parseable

**And** Unit tests cover:
- Template loading and caching
- Basic merge field replacement
- Error handling for missing templates
- Error handling for invalid context data

**Prerequisites:** Story 1.4 (POC validation complete)

**Technical Notes:**
- Follow Service Layer Pattern from architecture.md (lines 232-252)
- Use `DocxTemplate` from python-docxtpl
- Template caching: `self._template_cache: Dict[str, DocxTemplate] = {}`
- Return `BytesIO` for seamless S3 upload later (Epic 5)
- Log template loading and generation events with correlation_id
- Handle Jinja2 rendering errors gracefully

---

### Story 1.6: Implement Grammar Helper Utilities

As a developer,
I want utility functions for grammar helpers (pluralization, articles),
So that conditional logic can generate grammatically correct text.

**Acceptance Criteria:**

**Given** The project structure is initialized
**When** I implement `app/utils/grammar.py`
**Then** The following functions are available:

- `is_are(count: int) -> str` returns "is" if count==1, else "are"
- `was_were(count: int) -> str` returns "was" if count==1, else "were"
- `a_an(word: str) -> str` returns "an" if word starts with vowel, else "a"
- `format_list(items: List[str]) -> str` returns comma-separated list with "and" before last item

**And** Edge cases are handled:
- Empty lists return empty string
- Single-item lists return just that item
- Zero count uses plural form
- Vowel detection includes 'a', 'e', 'i', 'o', 'u' (case-insensitive)

**And** Examples work correctly:
- `is_are(1)` → "is"
- `is_are(3)` → "are"
- `a_an("apple")` → "an"
- `a_an("banana")` → "a"
- `format_list(["Legal", "Financial", "Procurement"])` → "Legal, Financial, and Procurement"

**And** Unit tests cover all functions with edge cases

**Prerequisites:** Story 1.1 (project structure)

**Technical Notes:**
- These support FR-2.9 Grammar Helpers from PRD (lines 427-432)
- Keep functions simple and pure (no side effects)
- Consider `format_list` with Oxford comma (standard for FTA documents)
- These will be used in conditional logic (Epic 2) and data transformation (Epic 3.5)

---

## Epic 3.5: Project Data Service

**Epic Goal:** Implement a data service layer that fetches project data from Riskuity once, transforms it to a canonical JSON schema, caches it in S3, then serves multiple templates from the cached JSON.

**Business Value:** Enables efficient multi-template generation from a single data fetch, provides audit trail, and decouples template development from Riskuity API availability. This architecture allows parallel development and reduces Riskuity API load.

**Architectural Components:** `services/data_service.py`, `services/riskuity_client.py`, `services/data_transformer.py`, `services/validator.py`, `api/routes/data.py`

**Architectural Pattern:** Data Service Layer with JSON Caching (architecture.md lines 6-16)

**Key Innovation:** Separates data acquisition from template rendering, enabling multiple templates to share cached data and allowing template development with static JSON files.

---

### Story 3.5.1: Design Canonical JSON Schema for Project Data

As a developer,
I want a well-defined JSON schema for CORTAP project data,
So that we have a stable contract between data layer and template layer.

**Acceptance Criteria:**

**Given** Requirements from PRD and RIR template analysis
**When** I design the canonical JSON schema
**Then** The schema includes all required sections:
- `project_id`, `generated_at`, `data_version` (metadata)
- `project` object (recipient info, review config, dates)
- `contractor` object (lead reviewer, firm details)
- `fta_program_manager` object (assigned PM details)
- `assessments` array (23 review areas with findings)
- `erf_items` array (Enhanced Review Focus areas)
- `metadata` object (derived fields: has_deficiencies, counts, etc.)

**And** Schema documentation includes:
- Field name, data type, required/optional status
- Example values for each field
- Default values for optional fields
- Validation rules (e.g., review_type enum values)

**And** Example JSON file created: `docs/schemas/project-data-v1.0.json`

**And** Schema aligns with:
- RIR template fields (15 fields from recipient-information-request-requirements.md)
- Draft Report template fields (50+ fields from PRD)
- Riskuity field mapping (riskuity-integration-requirements.md)

**And** Schema versioning strategy documented:
- Current version: 1.0
- Version field in JSON: `"data_version": "1.0"`
- Migration plan for future schema changes

**Prerequisites:** None - this is the first story in Epic 3.5

**Technical Notes:**
- Follow JSON schema example from architecture.md lines 621-664
- Follow JSON schema from recipient-information-request-requirements.md lines 313-360
- Version: 1.0 (include `data_version` field for future schema evolution)
- Place schema in `docs/schemas/` directory
- This schema will be validated in Story 3.5.6
- Create JSON Schema validation file (optional: use jsonschema.org format)

---

### Story 3.5.2: Implement Riskuity API Client with Retry Logic

As a developer,
I want an async HTTP client for all 4 Riskuity API endpoints with retry logic,
So that we can reliably retrieve CORTAP project data despite network issues.

**Acceptance Criteria:**

**Given** Riskuity API credentials are configured
**When** I implement `RiskuityClient` in `services/riskuity_client.py`
**Then** The class provides:
- `__init__(self, base_url: str, api_key: str, http_client: httpx.AsyncClient)`
- `async def get_project(self, project_id: str) -> dict`
- `async def get_assessments(self, project_id: str) -> List[dict]`
- `async def get_surveys(self, project_id: str) -> List[dict]`
- `async def get_risks_or_erf(self, project_id: str) -> List[dict]`

**And** All methods:
- Use Bearer token authentication (`Authorization: Bearer {api_key}`)
- Include retry logic with exponential backoff (1s, 2s, 4s delays)
- Maximum 3 retries per request
- 10-second timeout per request
- Raise `RiskuityAPIError` on failure after retries
- Log all API calls with correlation_id

**And** Response validation:
- Check HTTP status codes (200 OK expected, handle 404/500/503)
- Validate JSON response structure (not empty, is valid JSON)
- Handle rate limiting (429 status code) with backoff

**And** Unit tests with mocked httpx cover:
- Successful API calls for all 4 endpoints
- Retry on transient failures (500, 503)
- Final failure after max retries
- Timeout handling
- Invalid JSON response
- Rate limiting response

**Prerequisites:** Story 1.3 (custom exceptions), Story 1.2 (logging)

**Technical Notes:**
- Implements FR-3.1 from PRD (lines 436-446)
- Use `httpx.AsyncClient` for async support
- Retry logic from architecture.md Performance section (lines 809-813)
- Endpoints from PRD lines 309-318
- Can use mock Riskuity responses if real API not available yet
- Follow Service Layer Pattern from architecture.md (lines 247-265)
- Consider using `tenacity` library for retry decorator or implement manually
- Mock responses for development: Create `tests/fixtures/riskuity_responses.json`

---

### Story 3.5.3: Implement Data Transformer (Riskuity → JSON)

As a developer,
I want a service that transforms Riskuity API responses to canonical JSON schema,
So that we have clean, validated data ready for template consumption.

**Acceptance Criteria:**

**Given** `RiskuityClient` successfully retrieves project data
**When** I implement `DataTransformer` in `services/data_transformer.py`
**Then** The class provides:
- `__init__(self)` constructor
- `async def transform_to_json(self, project_data: dict, assessments: List[dict], surveys: List[dict], risks: List[dict]) -> dict`

**And** The transformer:
- Maps Riskuity field names to canonical JSON schema fields
- Calculates derived fields:
  - `has_deficiencies = any(a["finding"] == "D" for a in assessments)`
  - `deficiency_count = sum(1 for a in assessments if a["finding"] == "D")`
  - `deficiency_areas = [a["review_area"] for a in assessments if a["finding"] == "D"]`
  - `erf_count = len(erf_items)`
  - `reviewed_subrecipients = subrecipient_name is not None`
- Formats dates to ISO 8601 UTC strings
- Handles missing optional fields gracefully (None or empty string → null in JSON)
- Adds metadata: `generated_at`, `data_version: "1.0"`

**And** Output JSON matches schema from Story 3.5.1

**And** Unit tests cover:
- Complete data transformation (all fields populated)
- Derived field calculations (deficiency detection, counts)
- Missing optional fields (graceful handling)
- Date format conversion (various input formats → ISO 8601)
- Edge cases (no assessments, empty arrays, null values)

**Prerequisites:** Story 3.5.1 (JSON schema), Story 3.5.2 (RiskuityClient)

**Technical Notes:**
- Implements FR-3.2 from PRD (lines 448-459)
- Follow architecture.md Data Transformation Rules (lines 569-576)
- Field mapping requires Riskuity API documentation or mock responses
- Use Python `datetime` module for date handling
- Return dict (plain JSON structure), not Pydantic model
- This is data layer → template layer boundary
- Consider using `format_list()` from grammar helpers for comma-separated lists

---

### Story 3.5.4: Implement S3 Storage for JSON Data Files

As a developer,
I want S3 storage capability for JSON project data files,
So that we can cache Riskuity data and serve multiple templates efficiently.

**Acceptance Criteria:**

**Given** AWS S3 bucket is configured
**When** I extend `S3Storage` service in `services/s3_storage.py`
**Then** The class includes new methods:
- `async def upload_json(self, json_data: dict, project_id: str) -> str` (returns S3 key)
- `async def download_json(self, s3_key: str) -> dict` (returns parsed JSON)
- `async def get_cached_json(self, project_id: str, max_age_seconds: int = 3600) -> Optional[dict]`

**And** Upload logic for JSON:
- Organizes keys as: `projects/{project_id}/data/{timestamp}_project-data.json`
- Timestamp format: ISO 8601 (e.g., `2025-11-13T14:32:00Z`)
- Sets content type: `application/json`
- Uses boto3 `put_object()` with JSON string body
- Adds metadata tags: `project_id`, `data_version`, `generated_at`

**And** Caching logic:
- `get_cached_json()` checks if JSON exists for project_id
- Compares file timestamp to current time
- If file age < max_age_seconds (default 1 hour): Return cached JSON
- If file age >= max_age_seconds or not exists: Return None
- Uses S3 `head_object()` to check existence and get LastModified timestamp

**And** Download logic:
- Downloads JSON file from S3
- Parses JSON string to dict
- Validates JSON structure (basic check: has required top-level keys)
- Raises `S3StorageError` if file not found or invalid JSON

**And** Unit tests with mocked boto3 cover:
- Upload JSON and retrieve
- Cache hit scenario (file age < TTL)
- Cache miss scenario (file age >= TTL or not exists)
- Error handling (S3 errors, invalid JSON)

**Prerequisites:** Story 5.1 (S3Storage base implementation) OR implement new S3Storage class

**Technical Notes:**
- Cache TTL from architecture.md: 1 hour (3600 seconds)
- S3 key naming convention for data files
- Use `boto3.client('s3').head_object()` for metadata retrieval
- JSON storage separate from document storage (different S3 path structure)
- Consider S3 lifecycle policy: auto-delete JSON files > 7 days old
- Make TTL configurable via environment variable `CACHE_TTL_SECONDS`

---

### Story 3.5.5: Implement Caching and TTL Logic

As a developer,
I want intelligent caching that respects TTL and supports force refresh,
So that we balance data freshness with API call efficiency.

**Acceptance Criteria:**

**Given** S3 JSON storage is implemented
**When** I implement cache management in `DataService` class
**Then** The service provides cache control:
- Check cache before fetching from Riskuity
- Respect TTL (default 1 hour, configurable via environment variable)
- Support `force_refresh=True` flag to bypass cache
- Log cache hits and misses with correlation_id

**And** Cache decision logic:
```python
if force_refresh:
    fetch_from_riskuity()
elif cached_json := get_cached_json(project_id, ttl):
    return cached_json  # Cache HIT
else:
    fetch_from_riskuity()  # Cache MISS
```

**And** Cache metadata included in responses:
- `cached: bool` (true if served from cache)
- `cache_age_seconds: int` (age of cached data)
- `expires_at: str` (ISO timestamp when cache expires)

**And** Cache metrics logged:
- Track cache hit rate (log for monitoring)
- Log cache miss reasons (expired, not found, force refresh)

**And** Configuration:
- `CACHE_TTL_SECONDS` environment variable (default: 3600)
- `ENABLE_CACHING` boolean flag (default: true, can disable for testing)

**And** Unit tests cover:
- Cache hit (fresh data exists)
- Cache miss (no data exists)
- Cache miss (data too old)
- Force refresh bypasses cache
- TTL configuration

**Prerequisites:** Story 3.5.4 (S3 JSON storage)

**Technical Notes:**
- Implements caching architecture from architecture.md lines 9-15
- TTL recommendation: 1 hour balances freshness with efficiency
- Cache invalidation: Time-based only in MVP (webhook-based in v2)
- Log cache metrics for future optimization
- Consider adding cache warming (pre-fetch) in v2
- Cache hit rate metric helps optimize TTL value

---

### Story 3.5.6: Implement Data Validation and Completeness Checks

As a developer,
I want comprehensive validation of JSON data against schema and template requirements,
So that we catch missing/invalid data before template generation.

**Acceptance Criteria:**

**Given** Canonical JSON schema is defined
**When** I implement `JsonValidator` in `services/validator.py`
**Then** The class provides:
- `__init__(self, schema_path: str)` constructor
- `async def validate_json_schema(self, json_data: dict) -> ValidationResult`
- `async def check_completeness(self, json_data: dict, template_id: str) -> CompletenessResult`

**And** Schema validation checks:
- All required top-level keys exist (`project`, `assessments`, `metadata`, etc.)
- Data types match schema (strings, integers, dates, arrays)
- Enum values are valid (e.g., review_type in ["Triennial Review", "State Management Review", "Combined..."])
- Arrays are non-empty where required (e.g., assessments should have 23 items)

**And** Completeness checking for templates:
- Load template field requirements (from template metadata YAML)
- Check all CRITICAL fields are present and not null
- Check REQUIRED fields (warn if missing)
- Check CONDITIONAL fields based on context
- Return detailed report: missing_critical, missing_optional, data_quality_score (0-100)

**And** `ValidationResult` Pydantic model includes:
- `valid: bool` (schema valid)
- `errors: List[str]` (schema validation errors)
- `warnings: List[str]` (data quality warnings)

**And** `CompletenessResult` Pydantic model includes:
- `missing_critical_fields: List[str]`
- `missing_optional_fields: List[str]`
- `data_quality_score: int` (0-100, based on field coverage)
- `can_generate: bool` (no critical fields missing)

**And** Unit tests cover:
- Valid JSON passing all checks
- Missing critical field (validation fails)
- Missing optional field (warning only)
- Invalid enum value
- Wrong data type

**Prerequisites:** Story 3.5.1 (JSON schema), Story 4.1 (template metadata)

**Technical Notes:**
- Use `jsonschema` library for schema validation OR implement custom validator
- Completeness checking uses template metadata (field-definitions.yaml)
- Data quality score formula: (fields_present / total_fields) * 100
- This validation happens AFTER Riskuity fetch, BEFORE template rendering
- Validation errors block generation, warnings included in response
- Clear, actionable error messages for users

---

### Story 3.5.7: Implement POST /api/v1/projects/{project_id}/data Endpoint

As a developer,
I want a REST API endpoint to fetch and cache project data,
So that clients can trigger data retrieval independently of document generation.

**Acceptance Criteria:**

**Given** All data service components are implemented
**When** I create `DataService` orchestrator and API endpoint in `api/routes/data.py`
**Then** The `DataService` class provides:
- `__init__(self, riskuity_client: RiskuityClient, transformer: DataTransformer, s3_storage: S3Storage, validator: JsonValidator)`
- `async def fetch_and_cache_project_data(self, project_id: str, force_refresh: bool = False, include_assessments: bool = True, include_erf: bool = True, include_surveys: bool = False) -> DataServiceResponse`

**And** The orchestrator:
- Checks cache first (unless force_refresh=True)
- If cache miss: Calls all 4 Riskuity endpoints in parallel (`asyncio.gather`)
- Transforms responses to canonical JSON
- Validates JSON schema and completeness
- Uploads JSON to S3
- Returns response with S3 path, metadata, validation results

**And** The API endpoint is defined:
```python
@router.post("/projects/{project_id}/data", response_model=DataServiceResponse)
async def fetch_project_data(
    project_id: str,
    request: FetchDataRequest = Body(default=FetchDataRequest()),
    data_service: DataService = Depends(get_data_service)
) -> DataServiceResponse
```

**And** `FetchDataRequest` Pydantic model:
- `force_refresh: bool = False`
- `include_assessments: bool = True`
- `include_erf: bool = True`
- `include_surveys: bool = False`

**And** `DataServiceResponse` Pydantic model:
- `project_id: str`
- `data_file_url: str` (S3 path or pre-signed URL)
- `generated_at: str` (ISO timestamp)
- `data_version: str` ("1.0")
- `expires_at: str` (cache expiration timestamp)
- `cached: bool` (true if served from cache)
- `cache_age_seconds: Optional[int]`
- `completeness: CompletenessResult`

**And** Error handling:
- Riskuity API failure → 502 Bad Gateway
- S3 storage failure → 500 Internal Server Error
- Validation failure (critical fields missing) → 400 Bad Request with details

**And** Integration test validates:
- Successful data fetch and cache
- Cache hit on second request
- Force refresh bypasses cache
- Error scenarios (Riskuity down, S3 failure)

**Prerequisites:** Stories 3.5.2-3.5.6 (all data service components)

**Technical Notes:**
- API contract from architecture.md lines 584-628
- Orchestration pattern: parallel API calls with `asyncio.gather`
- Follow API Route Pattern from architecture.md (lines 277-295)
- Log full flow with correlation_id
- This endpoint can be called independently OR automatically by generate-document endpoint
- Add route to main FastAPI app with prefix `/api/v1`

---

## Epic 4: Recipient Information Request (RIR) Template

**Epic Goal:** Implement the RIR template generation using the data service pattern, validating the end-to-end architecture with a simpler template before tackling the complex Draft Audit Report.

**Business Value:** Provides early stakeholder value with a complete, usable template while validating the data service architecture. RIR is generated early in the review process and serves as proof-of-concept for the full system.

**Architectural Components:** `templates/rir-package.docx`, `services/conditional_logic.py` (RIR-specific), `api/routes/generate.py` (RIR endpoint), `models/template_data.py` (RIRTemplateData)

**Template Characteristics:**
- **Complexity:** LOW (15 fields, 1 conditional pattern)
- **Fields:** Simple merge field replacement
- **Conditional Logic:** Review type selection only (CL-RIR-1)
- **Document Type:** Information request form sent before site visits

**Strategic Value:** RIR validates the complete data service architecture (Epic 3.5) with a simple template, reducing risk before implementing complex Draft Audit Report logic.

---

### Story 4.1: Convert RIR Template to docxtpl Format

As a developer,
I want the RIR Word template converted to use Jinja2 syntax,
So that python-docxtpl can populate it with project data.

**Acceptance Criteria:**

**Given** The source RIR template (.docx file) from docs/requirements
**When** I convert bracket fields to Jinja2 syntax
**Then** All 15 merge fields are converted:

**Cover Page Fields:**
- `[#]` (Region) → `{{ region_number }}`
- Review Type → `{{ review_type }}` (with conditional logic - see Story 4.2)
- `[Recipient Name]` → `{{ recipient_name }}`
- `[Recipient Location]` → `{{ recipient_city_state }}`
- `[#]` (Recipient ID) → `{{ recipient_id }}`
- `[URL]` → `{{ recipient_website|default('N/A') }}`
- Site Visit Dates → `{{ site_visit_dates }}`
- `[Lead Reviewer Name]` → `{{ lead_reviewer_name }}`
- `[Contractor Name]` → `{{ contractor_name }}`
- `[Lead Reviewer Phone #]` → `{{ lead_reviewer_phone }}`
- `[Lead Reviewer Email Address]` → `{{ lead_reviewer_email }}`

**Body Content Fields:**
- `[FTA PM for Recipient]` → `{{ fta_program_manager_name }}`
- `[FTA PM Phone #]` → `{{ fta_program_manager_phone }}`
- `[FTA PM Email Address]` → `{{ fta_program_manager_email }}`

**And** Template saved as: `app/templates/rir-package.docx`

**And** Template metadata created: `app/templates/metadata/rir-field-definitions.yaml`:
```yaml
rir-package:
  name: "Recipient Information Request Package"
  description: "Information request sent to recipients before site visits"
  required_fields:
    - region_number
    - review_type
    - recipient_name
    - recipient_city_state
    - recipient_id
    - lead_reviewer_name
    - contractor_name
    - lead_reviewer_phone
    - lead_reviewer_email
    - fta_program_manager_name
    - fta_program_manager_phone
    - fta_program_manager_email
  optional_fields:
    - recipient_website
    - site_visit_dates
    - due_date
  default_values:
    recipient_website: "N/A"
    site_visit_dates: "TBD"
```

**And** Visual comparison confirms:
- All original Word formatting preserved
- Styles, fonts, headers, footers intact
- No formatting corruption from conversion

**Prerequisites:** Story 1.5 (DocumentGenerator), Story 1.4 (POC validation)

**Technical Notes:**
- Source template: `docs/requirements/RO_State_Recipient_FY2025_RecipientInformationRequestPackage_Final_1.3.25.docx`
- Field inventory from recipient-information-request-requirements.md lines 23-49
- Follow template conversion best practices from Epic 1 POC
- Test with minimal data to ensure rendering works
- Document variables (varFTARegion, varGranteeName, etc.) should be replaced with Jinja2 syntax
- Use Jinja2 `default()` filter for optional fields

---

### Story 4.2: Implement Review Type Conditional Logic (CL-RIR-1)

As a developer,
I want conditional logic for review type selection in RIR template,
So that the correct review type label appears on the cover page.

**Acceptance Criteria:**

**Given** RIR template is converted to docxtpl format
**When** I implement review type conditional in the template
**Then** The template includes Jinja2 conditional:

**Template syntax (line with review type):**
```jinja2
FY 2025 {{ review_type }}
```

**Simple approach:** Just use the variable directly since `review_type` is already the full text.

**Alternative (if multiple review type segments need different handling):**
```jinja2
FY 2025 {% if review_type == "Triennial Review" %}Triennial Review{% elif review_type == "State Management Review" %}State Management Review{% elif review_type == "Combined Triennial and State Management Review" %}Combined Triennial and State Management Review{% endif %}
```

**And** Testing with all 3 review types produces correct output:
- Input: `review_type = "Triennial Review"` → Output: "FY 2025 Triennial Review"
- Input: `review_type = "State Management Review"` → Output: "FY 2025 State Management Review"
- Input: `review_type = "Combined Triennial and State Management Review"` → Output: "FY 2025 Combined Triennial and State Management Review"

**And** Unit test validates conditional logic with all 3 types

**Prerequisites:** Story 4.1 (RIR template conversion)

**Technical Notes:**
- This implements CL-RIR-1 from recipient-information-request-requirements.md lines 82-100
- Reuses same pattern as Draft Audit Report CL-1 (Epic 2 Story 2.2)
- Simple conditional - no complex logic needed
- Validate that Riskuity provides exact enum values (case-sensitive)
- Prefer simple `{{ review_type }}` if no additional logic needed

---

### Story 4.3: Create RIR Data Model and Context Builder

As a developer,
I want a Pydantic model and context builder for RIR template data,
So that we have type-safe data structures and clean separation from Draft Report data.

**Acceptance Criteria:**

**Given** The canonical JSON schema includes all RIR fields
**When** I create `RIRTemplateData` model in `models/template_data.py`
**Then** The Pydantic model includes:
```python
class RIRTemplateData(BaseModel):
    """Data model for Recipient Information Request template."""

    # Project Information
    region_number: int = Field(..., ge=1, le=10, description="FTA Region 1-10")
    review_type: Literal["Triennial Review", "State Management Review", "Combined Triennial and State Management Review"]
    recipient_name: str
    recipient_city_state: str
    recipient_id: str
    recipient_website: Optional[str] = "N/A"

    # Site Visit
    site_visit_dates: str = "TBD"  # Formatted date range or "TBD"

    # Contractor Information
    contractor_name: str
    lead_reviewer_name: str
    lead_reviewer_phone: str
    lead_reviewer_email: EmailStr

    # FTA Program Manager
    fta_program_manager_name: str
    fta_program_manager_phone: str
    fta_program_manager_email: EmailStr

    # Optional
    due_date: Optional[str] = None
```

**And** Context builder class created:
```python
class RIRContextBuilder:
    """Builds Jinja2 context for RIR template from JSON data."""

    @staticmethod
    def build_context(json_data: dict) -> dict:
        """
        Transform canonical JSON to RIR template context.

        Args:
            json_data: Canonical project JSON from data service

        Returns:
            dict: Jinja2 context for RIR template rendering
        """
        # Extract and transform fields
        # Format dates
        # Apply defaults for optional fields
        return context_dict
```

**And** Date formatting logic:
- If both `site_visit_start_date` and `site_visit_end_date` exist: Format as "March 10-14, 2025"
- If dates missing: Use "TBD"

**And** Unit tests cover:
- Model validation (all required fields)
- Invalid enum value (review_type)
- Email validation
- Context building from canonical JSON
- Date formatting

**Prerequisites:** Story 3.5.1 (canonical JSON schema), Story 4.1 (RIR template)

**Technical Notes:**
- Follow Data Validation Pattern from architecture.md (lines 298-321)
- RIRTemplateData is separate from TemplateData (Draft Report model)
- Field mapping from recipient-information-request-requirements.md lines 103-136
- Date formatting helper: `format_date_range(start: str, end: str) -> str`
- Use Pydantic EmailStr for email validation

---

### Story 4.4: Integrate RIR with Data Service (JSON → Template)

As a developer,
I want RIR template generation to consume cached JSON from data service,
So that we validate the end-to-end data service pattern.

**Acceptance Criteria:**

**Given** Data service (Epic 3.5) is complete and RIR template is ready
**When** I extend `DocumentGenerator` to support RIR template
**Then** The generator can:
- Accept template_id = "rir-package"
- Load RIR template from `app/templates/rir-package.docx`
- Build RIR context using `RIRContextBuilder.build_context(json_data)`
- Render template with python-docxtpl
- Return generated document (BytesIO)

**And** Integration flow:
1. Client calls POST `/api/v1/projects/{id}/data` (Epic 3.5.7) → Gets cached JSON
2. Client calls POST `/api/v1/generate-document` with:
   - `template_id = "rir-package"`
   - Optional: `data_source = S3_json_path`
3. DocumentGenerator loads JSON from S3 (or fetches latest cached)
4. RIRContextBuilder transforms JSON to template context
5. Template rendered, uploaded to S3, pre-signed URL returned

**And** Alternative flow (automatic data fetch):
1. Client calls POST `/api/v1/generate-document` with just project_id and template_id
2. System automatically fetches/caches JSON via data service
3. Proceeds with generation

**And** Unit test validates:
- JSON → RIR context transformation
- Template rendering with real JSON data
- All 15 fields populated correctly

**And** Integration test validates:
- End-to-end: Data fetch → JSON cache → RIR generation → S3 upload → Download URL
- Generated document downloads and opens correctly
- All fields populated, formatting preserved

**Prerequisites:** Story 4.3 (RIR data model), Story 3.5.7 (data service endpoint), Story 5.2 (S3 storage integration)

**Technical Notes:**
- This validates the data service architecture end-to-end
- DocumentGenerator should accept optional `json_data` parameter to allow pre-loaded JSON
- If JSON not provided, DocumentGenerator fetches latest cached JSON for project_id
- Log full generation flow with correlation_id
- Template routing: Use template_id to determine which template and context builder to use
- Performance target: < 15 seconds for RIR (simpler than Draft Report)

---

### Story 4.5: Add RIR to Document Generation API

As a developer,
I want RIR template integrated into the main generation API,
So that React app can generate RIR documents alongside other templates.

**Acceptance Criteria:**

**Given** RIR template generation is integrated with data service
**When** POST `/api/v1/generate-document` endpoint receives template_id = "rir-package"
**Then** The endpoint successfully generates RIR document

**And** Request example:
```json
{
  "project_id": "RSKTY-12345",
  "template_id": "rir-package",
  "user_id": "auditor@fta.gov",
  "format": "docx"
}
```

**And** Response includes:
```json
{
  "status": "success",
  "document_id": "uuid",
  "download_url": "https://s3.../rir-package_RSKTY-12345.docx",
  "generated_at": "2025-11-13T14:32:00Z",
  "cached_data_used": true,
  "cache_age_seconds": 1234,
  "warnings": []
}
```

**And** Validation ensures:
- RIR required fields are present (using rir-field-definitions.yaml)
- Returns 400 Bad Request if critical fields missing
- Returns warnings if optional fields missing

**And** GET `/api/v1/templates` returns RIR in template list:
```json
{
  "templates": [
    {
      "id": "rir-package",
      "name": "Recipient Information Request Package",
      "description": "Information request sent to recipients before site visits",
      "required_fields": ["region_number", "review_type", "recipient_name", ...],
      "optional_fields": ["recipient_website", "site_visit_dates"]
    }
  ]
}
```

**And** Integration test validates:
- Successful RIR generation via API (200 OK)
- Download URL works
- Document contains correct data
- Error handling (missing required field → 400)

**Prerequisites:** Story 4.4 (RIR integration), Story 6.2 (generate-document endpoint)

**Technical Notes:**
- Reuses existing `/generate-document` endpoint from Epic 6
- Template routing based on template_id
- RIR uses simpler validation than Draft Report
- Add RIR to template metadata for GET `/templates` endpoint
- Update template registry/factory pattern if implemented
- Ensure consistent error responses across templates

---

### Story 4.6: End-to-End Testing with Real Riskuity Data Structure

As a developer,
I want comprehensive e2e tests for RIR generation using realistic Riskuity data,
So that we validate the complete system works with production-like data.

**Acceptance Criteria:**

**Given** All RIR components are implemented
**When** I create e2e test suite in `tests/e2e/test_rir_generation.py`
**Then** The test suite includes:

**Test 1: Complete RIR Generation Flow**
- Mock Riskuity API responses (realistic data for all 4 endpoints)
- Call POST `/projects/{id}/data` → verify JSON cached
- Call POST `/generate-document` with template_id="rir-package"
- Verify generated .docx file
- Download from S3 and validate content
- Check all 15 fields populated correctly

**Test 2: Cache Hit Scenario**
- First request: Fresh Riskuity fetch
- Second request: Cache hit (no Riskuity call)
- Verify cached data used
- Verify document generation time faster on cache hit

**Test 3: All 3 Review Types**
- Generate RIR for "Triennial Review"
- Generate RIR for "State Management Review"
- Generate RIR for "Combined Triennial and State Management Review"
- Verify correct review type label in each document

**Test 4: Missing Optional Fields**
- Mock Riskuity data with missing recipient_website
- Verify generation succeeds
- Verify "N/A" used as default
- Verify warning in response

**Test 5: Missing Critical Field**
- Mock Riskuity data missing contractor_name
- Verify generation fails with 400 Bad Request
- Verify error message: "Required field missing: contractor_name"

**And** Performance validation:
- Full generation (with cache miss) completes < 15 seconds
- Generation with cache hit completes < 5 seconds

**And** Test data fixtures:
- Create realistic mock Riskuity responses in `tests/fixtures/riskuity_responses/`
- Include edge cases (missing fields, unusual values)

**Prerequisites:** Story 4.5 (RIR API integration), all Epic 4 stories

**Technical Notes:**
- This validates the ENTIRE data service architecture
- Use mocked Riskuity API (not real API) for test reliability
- Mock S3 with LocalStack or moto library
- Validate Word document content using python-docx library
- Performance targets from PRD NFR-1.1 (30-60 seconds for complex docs, faster for simple RIR)
- Consider using `pytest-benchmark` for performance tracking
- This completes Epic 4 and validates architecture before tackling complex Draft Report

---

## Epic 2: Conditional Logic Engine

**Epic Goal:** Implement all 9 conditional logic patterns required for intelligent template rendering, enabling the system to generate contextually appropriate content based on review type, deficiency status, and other data conditions.

**Business Value:** This is the "intelligence" of CORTAP-RPT - the magic that transforms a simple mail-merge into a context-aware document generator. Without this, auditors would still need manual editing.

**Architectural Components:** `services/conditional_logic.py`, `models/template_data.py`

**Critical Success Factor:** 100% accuracy in conditional logic (NFR Success Metric #4 from PRD)

---

### Story 2.1: Define Template Data Models with Pydantic

As a developer,
I want Pydantic models for all template data structures,
So that we have type-safe, validated data for document generation.

**Acceptance Criteria:**

**Given** The project structure is initialized
**When** I create `app/models/template_data.py`
**Then** The following Pydantic models are defined:

**`TemplateData`** (main model):
- Recipient information: `recipient_name`, `recipient_acronym`, `region_number`
- Review configuration: `review_type` (Literal["Triennial Review", "State Management Review", "Combined..."]), `exit_conference_format` (Literal["virtual", "in-person"])
- Assessment data: `assessments: List[AssessmentData]`, `has_deficiencies: bool`, `deficiency_count: int`, `deficiency_areas: List[str]`
- Optional fields: `erf_count`, `erf_areas`, `reviewed_subrecipients`, `subrecipient_name`
- Personnel & dates: `audit_team: List[PersonData]`, `site_visit_dates: DateRange`, `report_date: datetime`

**`AssessmentData`**:
- `review_area: str`
- `finding: Literal["D", "ND", "NA"]`
- `deficiency_code: Optional[str]`
- `description: Optional[str]`
- `corrective_action: Optional[str]`
- `due_date: Optional[datetime]`
- `date_closed: Optional[datetime]`

**`PersonData`**, **`DateRange`** (supporting models)

**And** All datetime fields use timezone-aware UTC
**And** Models include `Field()` descriptions for documentation
**And** Unit tests validate model constraints and field validators

**Prerequisites:** Story 1.1 (project structure)

**Technical Notes:**
- Follow architecture.md Data Architecture (lines 483-549)
- Use Pydantic `BaseModel`, `Field`, `field_validator`
- Follow Data Validation Pattern from architecture.md (lines 283-307)
- These models are used by data transformer (Epic 3) and document generator (Epic 1)

---

### Story 2.2: Implement Review Type Routing (CL-1)

As a developer,
I want conditional logic for review type routing,
So that the correct paragraphs are included based on Triennial/State Management/Combined review types.

**Acceptance Criteria:**

**Given** `TemplateData` includes `review_type` field
**When** I implement `ConditionalLogic.apply_review_type_routing()` in `services/conditional_logic.py`
**Then** The method:
- Takes `template_data: TemplateData` and `template_context: dict` as input
- Adds Jinja2 conditional helpers to context
- Returns enriched context dict

**And** Template can use:
- `{% if review_type == "Triennial Review" %}...{% endif %}`
- `{% if review_type == "State Management Review" %}...{% endif %}`
- `{% if review_type == "Combined Triennial and State Management Review" %}...{% endif %}`

**And** Combined reviews include BOTH Triennial and State Management content
**And** Unit tests cover all 3 review types
**And** Integration test with actual template section validates correct paragraph inclusion

**Prerequisites:** Story 2.1 (TemplateData models), Story 1.5 (DocumentGenerator)

**Technical Notes:**
- This implements FR-2.1 from PRD (lines 365-372)
- Conditional logic reference: PRD Appendix line 689
- Pass `review_type` directly to Jinja2 context
- Document generator will use this context for rendering

---

### Story 2.3: Implement Deficiency Detection & Alternative Content (CL-2)

As a developer,
I want conditional logic for deficiency detection,
So that the system shows appropriate content based on whether deficiencies exist.

**Acceptance Criteria:**

**Given** `TemplateData` includes `has_deficiencies` boolean and `assessments` list
**When** I implement `ConditionalLogic.apply_deficiency_logic()`
**Then** The method:
- Calculates `has_deficiencies = any(a.finding == "D" for a in assessments)`
- Calculates `deficiency_count = sum(1 for a in assessments if a.finding == "D")`
- Generates `deficiency_areas` list (names of review areas with Finding="D")
- Adds these to context

**And** Template can use:
- `{% if has_deficiencies %}Deficiencies were found...{% else %}No deficiencies found...{% endif %}`
- `{{ deficiency_count }}` for displaying count
- `{{ deficiency_areas|format_list }}` for comma-separated list

**And** Unit tests cover:
- No deficiencies scenario (all ND/NA)
- Single deficiency scenario
- Multiple deficiencies scenario
- All 23 review areas scenario

**Prerequisites:** Story 2.1 (models), Story 1.6 (grammar helpers for format_list)

**Technical Notes:**
- Implements FR-2.2 from PRD (lines 374-379)
- Conditional logic reference: PRD line 690
- Use grammar helper `format_list()` for deficiency_areas
- This supports [OR] blocks in templates

---

### Story 2.4: Implement Conditional Section Inclusion (CL-3)

As a developer,
I want conditional logic for section inclusion based on data existence,
So that optional sections (ERF, subrecipients) appear only when applicable.

**Acceptance Criteria:**

**Given** `TemplateData` includes optional fields like `erf_count`, `reviewed_subrecipients`
**When** I implement `ConditionalLogic.apply_section_conditions()`
**Then** The method adds boolean flags to context:
- `show_erf_section = erf_count > 0`
- `show_subrecipient_section = reviewed_subrecipients`

**And** Template can use:
- `{% if show_erf_section %}[ERF section content]{% endif %}`
- `{% if show_subrecipient_section %}[Subrecipient content]{% endif %}`

**And** Entire sections are included/excluded cleanly (no partial content)
**And** Unit tests validate correct inclusion logic

**Prerequisites:** Story 2.1 (models)

**Technical Notes:**
- Implements FR-2.3 from PRD (lines 381-388)
- Conditional logic reference: PRD line 691
- ERF = Enhanced Review Focus (special deep-dive reviews)
- Subrecipients are reviewed if `subrecipient_name` is not None

---

### Story 2.5: Implement Exit Conference Format Selection (CL-5)

As a developer,
I want conditional logic for exit conference format selection,
So that the correct paragraph (virtual vs in-person) is included.

**Acceptance Criteria:**

**Given** `TemplateData` includes `exit_conference_format` field
**When** I implement `ConditionalLogic.apply_exit_conference_logic()`
**Then** The context includes `exit_conference_format` value

**And** Template can use:
- `{% if exit_conference_format == "virtual" %}[Virtual conference paragraph]{% endif %}`
- `{% if exit_conference_format == "in-person" %}[In-person conference paragraph]{% endif %}`

**And** Only ONE paragraph is included (mutually exclusive)
**And** Unit tests cover both formats

**Prerequisites:** Story 2.1 (models)

**Technical Notes:**
- Implements FR-2.5 from PRD (lines 397-400)
- Conditional logic reference: PRD line 693
- Simple pass-through to Jinja2 context
- Validation ensures only "virtual" or "in-person" values

---

### Story 2.6: Implement Deficiency Table Display Logic (CL-6)

As a developer,
I want conditional logic for deficiency table generation,
So that the 23-row table appears only when deficiencies exist and detail columns are populated correctly.

**Acceptance Criteria:**

**Given** `TemplateData` includes `assessments` for all 23 review areas
**When** I implement `ConditionalLogic.generate_deficiency_table()`
**Then** The method:
- Returns `None` if no deficiencies exist (`has_deficiencies == False`)
- Returns table data structure if deficiencies exist

**And** Table structure includes all 23 review areas with:
- `review_area` (name)
- `finding` ("D", "ND", or "NA")
- Detail columns (populated ONLY if finding=="D"):
  - `deficiency_code`
  - `description`
  - `corrective_action`
  - `due_date`
  - `date_closed`

**And** ND/NA rows have empty detail columns
**And** Template can use:
- `{% if deficiency_table %}[render table]{% else %}No deficiencies found.{% endif %}`

**And** Unit tests validate table structure for various scenarios

**Prerequisites:** Story 2.1 (models), Story 2.3 (deficiency detection)

**Technical Notes:**
- Implements FR-2.6 from PRD (lines 402-410)
- Conditional logic reference: PRD line 694
- Table format must match government template exactly
- Return dict/list structure that Jinja2 can iterate over

---

### Story 2.7: Implement Dynamic Count and Grammar Helpers (CL-8, CL-9)

As a developer,
I want conditional logic for dynamic counts and grammar helpers,
So that generated text is grammatically correct.

**Acceptance Criteria:**

**Given** `TemplateData` includes count fields (`erf_count`, `deficiency_count`)
**When** I implement `ConditionalLogic.apply_count_and_grammar()`
**Then** The context includes:
- Count values (`erf_count`, `deficiency_count`)
- Grammar helper functions registered as Jinja2 filters

**And** Template can use:
- `{{ erf_count }}` → displays number or "no" if zero
- `{{ deficiency_count|is_are }}` → "is" or "are"
- `{{ "area"|a_an }}` → "an area"

**And** Jinja2 filters are registered:
- `is_are`
- `was_were`
- `a_an`
- `format_list`

**And** Unit tests validate count display and grammar helper usage

**Prerequisites:** Story 2.1 (models), Story 1.6 (grammar helper functions)

**Technical Notes:**
- Implements FR-2.8 and FR-2.9 from PRD (lines 421-432)
- Conditional logic references: PRD lines 696-697
- Register Python functions as Jinja2 filters
- Example: `template.environment.filters['is_are'] = is_are`

---

### Story 2.8: Implement ConditionalLogic Service Integration

As a developer,
I want a unified ConditionalLogic service that applies all patterns,
So that DocumentGenerator can use a single method to enrich template context.

**Acceptance Criteria:**

**Given** All individual conditional logic methods are implemented
**When** I create `ConditionalLogic` class in `services/conditional_logic.py`
**Then** The class provides:
- `__init__(self)` constructor
- `async def enrich_context(self, template_data: TemplateData) -> dict` method

**And** The `enrich_context` method:
- Calls all conditional logic methods (CL-1 through CL-9)
- Returns complete Jinja2 context dict
- Includes all data, booleans, lists, and helper functions
- Logs the enrichment process with correlation_id

**And** DocumentGenerator is updated to:
- Accept `TemplateData` instead of raw dict
- Use `ConditionalLogic.enrich_context()` before rendering
- Pass enriched context to python-docxtpl

**And** Integration tests validate:
- Complete document generation with all 9 patterns
- Correct content for various data scenarios
- No missing or incorrect conditional sections

**Prerequisites:** Stories 2.2-2.7 (all conditional logic patterns)

**Technical Notes:**
- This unifies all conditional logic into single entry point
- Follow Service Layer Pattern from architecture.md
- Use dependency injection: `DocumentGenerator` receives `ConditionalLogic` in `__init__`
- Comprehensive integration test with realistic CORTAP data

---

## Epic 3: Riskuity API Integration

**Epic Goal:** Implement reliable integration with Riskuity API to retrieve CORTAP project data, transform it to template-ready format, and handle errors gracefully.

**Business Value:** Enables automated data retrieval, eliminating manual data entry and ensuring accuracy.

**Architectural Components:** `services/riskuity_client.py`, `services/data_transformer.py`, `models/request.py`

---

### Story 3.1: Implement Riskuity API Client with Retry Logic

As a developer,
I want an async HTTP client for Riskuity API with retry logic,
So that we can reliably retrieve CORTAP project data despite network issues.

**Acceptance Criteria:**

**Given** Riskuity API credentials are configured
**When** I implement `RiskuityClient` in `services/riskuity_client.py`
**Then** The class provides:
- `__init__(self, base_url: str, api_key: str, http_client: httpx.AsyncClient)`
- `async def get_project(self, project_id: str) -> dict`
- `async def get_assessments(self, project_id: str) -> List[dict]`
- `async def get_surveys(self, project_id: str) -> List[dict]`
- `async def get_risks(self, project_id: str) -> List[dict]`

**And** All methods:
- Use Bearer token authentication (`Authorization: Bearer {api_key}`)
- Include retry logic with exponential backoff (1s, 2s, 4s delays)
- Maximum 3 retries per request
- 10-second timeout per request
- Raise `RiskuityAPIError` on failure after retries

**And** Response validation:
- Check HTTP status codes (200 OK, 404 Not Found, etc.)
- Validate JSON response structure
- Log all API calls with correlation_id

**And** Unit tests with mocked httpx cover:
- Successful API calls
- Retry on transient failures (500, 503)
- Final failure after max retries
- Timeout handling

**Prerequisites:** Story 1.3 (custom exceptions), Story 1.2 (logging)

**Technical Notes:**
- Implements FR-3.1 from PRD (lines 436-446)
- Use `httpx.AsyncClient` for async support
- Retry logic from architecture.md Performance section (lines 692-697)
- Endpoints from PRD lines 309-314
- Use `tenacity` library for retry decorator or implement manually

---

### Story 3.2: Implement Data Transformer Service

As a developer,
I want a service that transforms Riskuity API responses to TemplateData models,
So that document generator receives validated, template-ready data.

**Acceptance Criteria:**

**Given** `RiskuityClient` successfully retrieves project data
**When** I implement `DataTransformer` in `services/data_transformer.py`
**Then** The class provides:
- `__init__(self)` constructor
- `async def transform(self, project_data: dict, assessments: List[dict], surveys: List[dict], risks: List[dict]) -> TemplateData`

**And** The transformer:
- Maps Riskuity field names to TemplateData fields
- Calculates derived fields:
  - `has_deficiencies = any(a["finding"] == "D" for a in assessments)`
  - `deficiency_count`
  - `deficiency_areas` list
  - `reviewed_subrecipients` boolean
- Formats dates to timezone-aware datetime objects (UTC)
- Validates all required fields are present
- Raises `ValidationError` if critical data missing

**And** Unit tests cover:
- Complete data transformation
- Derived field calculations
- Missing optional fields (use defaults)
- Date format conversion

**Prerequisites:** Story 2.1 (TemplateData models), Story 3.1 (RiskuityClient)

**Technical Notes:**
- Implements FR-3.2 from PRD (lines 448-453)
- Follow architecture.md Data Transformation Rules (lines 537-549)
- Field mapping will require Riskuity API documentation
- Handle missing optional fields gracefully (None or default values)

---

### Story 3.3: Implement End-to-End Data Retrieval Flow

As a developer,
I want an orchestration service that coordinates Riskuity data retrieval and transformation,
So that DocumentGenerator can get TemplateData with a single method call.

**Acceptance Criteria:**

**Given** `RiskuityClient` and `DataTransformer` are implemented
**When** I create `DataOrchestrator` service (or extend `DocumentGenerator`)
**Then** A method exists:
- `async def fetch_template_data(self, project_id: str) -> TemplateData`

**And** The method:
- Calls all 4 Riskuity API endpoints in parallel (using `asyncio.gather`)
- Passes responses to `DataTransformer.transform()`
- Returns validated `TemplateData` object
- Logs each step with correlation_id
- Raises appropriate errors (`RiskuityAPIError`, `ValidationError`)

**And** Integration test (with mocked Riskuity API) validates:
- Parallel API calls (faster than sequential)
- Error handling at each step
- Complete TemplateData output

**Prerequisites:** Story 3.1 (RiskuityClient), Story 3.2 (DataTransformer)

**Technical Notes:**
- Implements FR-3 integration from PRD
- Use `asyncio.gather(*[get_project(), get_assessments(), ...])` for parallel calls
- Performance optimization from architecture.md (line 675)
- Consider adding this to `DocumentGenerator` class or separate orchestrator
- Comprehensive error handling for each API call failure

---

## Epic 4: Validation Engine & User Feedback

**Epic Goal:** Implement pre-generation validation to check data completeness and provide clear warnings/errors to users before document generation.

**Business Value:** Prevents generation failures and provides actionable feedback, improving user experience.

**Architectural Components:** `services/validator.py`, `templates/metadata/field-definitions.yaml`

---

### Story 4.1: Create Template Field Metadata Definitions

As a developer,
I want YAML metadata files defining required/optional fields per template,
So that the validator knows which fields are critical vs optional.

**Acceptance Criteria:**

**Given** The project structure is initialized
**When** I create `app/templates/metadata/field-definitions.yaml`
**Then** The file defines for each template:

**Template: draft-audit-report**
- `required_fields`: List of field names that MUST be present (block generation if missing)
  - Example: `recipient_name`, `recipient_acronym`, `review_type`, `region_number`
- `optional_fields`: List of field names that can be missing (warn user, apply defaults)
  - Example: `recipient_phone`, `subrecipient_name`, `contractor_name`
- `conditional_fields`: Fields required only if certain conditions met
  - Example: `erf_count` (required if ERF exists), `deficiency_code` (required if finding=="D")

**And** Metadata includes default values for optional fields:
- `default_value: "N/A"` for most optional fields

**And** YAML structure is documented with comments
**And** Validation schema is testable (load and parse YAML successfully)

**Prerequisites:** Story 1.1 (project structure)

**Technical Notes:**
- Implements FR-3.3 field metadata from PRD (lines 455-462)
- Template field inventory from PRD lines 699-721
- Use YAML for human readability and easy updates
- Place in `app/templates/metadata/` directory
- Load with `pyyaml` library

---

### Story 4.2: Implement Validator Service

As a developer,
I want a Validator service that checks data completeness against template metadata,
So that we can provide warnings/errors before generation.

**Acceptance Criteria:**

**Given** Template field metadata is defined
**When** I implement `Validator` in `services/validator.py`
**Then** The class provides:
- `__init__(self, metadata_path: str)` constructor (loads metadata)
- `async def validate(self, template_id: str, template_data: TemplateData) -> ValidationResult`

**And** `ValidationResult` Pydantic model includes:
- `valid: bool` (overall validity)
- `missing_required: List[str]` (critical fields missing - blocks generation)
- `missing_optional: List[str]` (optional fields missing - warns user)
- `can_proceed: bool` (True if no required fields missing)
- `warnings: List[str]` (user-friendly warning messages)
- `errors: List[str]` (user-friendly error messages)

**And** Validation logic:
- Check all required fields are present and not None
- Check optional fields and note which are missing
- Check conditional fields based on conditions
- Generate clear messages: "Required field [recipient_name] is missing"

**And** Unit tests cover:
- All required fields present (valid=True)
- Missing required field (valid=False, can_proceed=False)
- Missing optional fields (valid=True, can_proceed=True, warnings populated)

**Prerequisites:** Story 4.1 (metadata), Story 2.1 (TemplateData model)

**Technical Notes:**
- Implements FR-3.3 validation from PRD (lines 455-462)
- Implements FR-5.3 validation warnings from PRD (lines 496-501)
- Load metadata YAML once in `__init__`, cache in memory
- Validator used by DocumentGenerator before generation
- Clear, actionable error messages for users

---

### Story 4.3: Integrate Validation into Document Generation Flow

As a developer,
I want validation to run automatically before document generation,
So that users receive warnings/errors before attempting generation.

**Acceptance Criteria:**

**Given** Validator service is implemented
**When** I update `DocumentGenerator.generate()` method
**Then** The method:
- Calls `Validator.validate(template_id, template_data)` first
- If `can_proceed == False`, raises `ValidationError` with missing required fields
- If `can_proceed == True` but warnings exist, includes warnings in response
- Logs validation results with correlation_id

**And** API response includes warnings:
```json
{
  "status": "success",
  "document_id": "uuid",
  "download_url": "...",
  "warnings": ["Optional field [recipient_phone] was missing - used default 'N/A'"]
}
```

**And** Validation errors return 400 Bad Request:
```json
{
  "error_code": "MISSING_REQUIRED_FIELD",
  "message": "Required field missing: [recipient_name]",
  "details": {"missing_fields": ["recipient_name", "review_type"]},
  "can_proceed": false
}
```

**And** Integration tests validate full flow with validation

**Prerequisites:** Story 4.2 (Validator), Story 2.8 (ConditionalLogic integration)

**Technical Notes:**
- Implements FR-5.2 error handling from PRD (lines 487-494)
- Update `GenerateDocumentResponse` model to include `warnings: List[str]`
- Always validate before calling conditional logic enrichment

---

## Epic 5: AWS S3 Storage & Document Management

**Epic Goal:** Implement document upload to AWS S3 with organized naming and pre-signed URL generation for secure downloads.

**Business Value:** Provides secure, scalable document storage with temporary download access.

**Architectural Components:** `services/s3_storage.py`, `infra/template.yaml` (S3 bucket)

---

### Story 5.1: Implement S3Storage Service

As a developer,
I want an S3Storage service for uploading documents and generating pre-signed URLs,
So that generated documents are stored securely and users can download them.

**Acceptance Criteria:**

**Given** AWS credentials and S3 bucket are configured
**When** I implement `S3Storage` in `services/s3_storage.py`
**Then** The class provides:
- `__init__(self, bucket_name: str, region: str, boto3_client: boto3.client)`
- `async def upload_document(self, file_content: BytesIO, project_id: str, template_id: str, filename: str) -> str` (returns S3 key)
- `async def generate_presigned_url(self, s3_key: str, expiration: int = 86400) -> str` (returns download URL)

**And** Upload logic:
- Organizes keys as: `{project_id}/{template_id}/{timestamp}_{filename}.docx`
- Timestamp format: `YYYYMMDD_HHMMSS` (e.g., `20251112_143022`)
- Sets appropriate content type: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Uses boto3 `put_object()` method
- Retries up to 2 times on failure (boto3 built-in retry)
- Raises `S3StorageError` on final failure

**And** Pre-signed URL:
- Default expiration: 24 hours (86400 seconds)
- Uses boto3 `generate_presigned_url()` method
- Returns HTTPS URL

**And** Unit tests with mocked boto3 cover:
- Successful upload and URL generation
- Retry on transient S3 errors
- Error handling

**Prerequisites:** Story 1.3 (custom exceptions), Story 1.1 (boto3 installed)

**Technical Notes:**
- Implements FR-4 from PRD (lines 464-477)
- Follow architecture.md S3 integration (lines 178-182)
- Use `aioboto3` for async boto3 or run in threadpool with `asyncio.to_thread()`
- Naming convention from architecture line 182
- Log all S3 operations with correlation_id

---

### Story 5.2: Integrate S3 Upload into Document Generation Flow

As a developer,
I want S3 upload to happen automatically after document generation,
So that users receive download URLs in the API response.

**Acceptance Criteria:**

**Given** `S3Storage` service is implemented
**When** I update `DocumentGenerator.generate()` method
**Then** The method:
- Generates document (BytesIO)
- Uploads to S3 via `S3Storage.upload_document()`
- Generates pre-signed URL via `S3Storage.generate_presigned_url()`
- Returns `GeneratedDocument` model with:
  - `document_id` (UUID)
  - `download_url` (pre-signed S3 URL)
  - `generated_at` (timestamp)
  - `warnings` (if any from validation)

**And** If S3 upload fails:
- Raises `S3StorageError`
- Document generation is considered failed (no partial success)
- Error is logged with correlation_id

**And** Integration test validates:
- Complete flow: data retrieval → generation → S3 upload → URL
- Generated document is downloadable via pre-signed URL

**Prerequisites:** Story 5.1 (S3Storage), Story 4.3 (validation integration)

**Technical Notes:**
- Document ID: Use `uuid.uuid4()` for unique identifier
- Filename: Construct from template_id and project_id (e.g., `draft-audit-report_RSKTY-12345.docx`)
- S3Storage injected via dependency injection into DocumentGenerator
- Full end-to-end integration test with LocalStack or mocked S3

---

## Epic 6: REST API & React Integration

**Epic Goal:** Implement FastAPI REST endpoints with Pydantic request/response models to provide API for React/Node application integration.

**Business Value:** Enables Riskuity React app to trigger document generation and download documents.

**Architectural Components:** `api/routes/*.py`, `models/request.py`, `models/response.py`, `main.py`

---

### Story 6.1: Implement Pydantic Request and Response Models

As a developer,
I want Pydantic models for all API requests and responses,
So that we have type-safe, validated API contracts.

**Acceptance Criteria:**

**Given** The project structure is initialized
**When** I create `app/models/request.py` and `app/models/response.py`
**Then** The following models are defined:

**Request Models (`request.py`):**
- `GenerateDocumentRequest`:
  - `project_id: str`
  - `template_id: str`
  - `user_id: str`
  - `format: str = "docx"` (default)
  - Validator: `template_id` must be in allowed list

**Response Models (`response.py`):**
- `GenerateDocumentResponse`:
  - `status: str` ("success")
  - `document_id: str` (UUID)
  - `download_url: str`
  - `generated_at: str` (ISO timestamp)
  - `warnings: List[str] = []`

- `TemplateInfo`:
  - `id: str`
  - `name: str`
  - `description: str`
  - `required_fields: List[str]`
  - `optional_fields: List[str]`

- `TemplatesResponse`:
  - `templates: List[TemplateInfo]`

- `ValidationResponse`:
  - `valid: bool`
  - `missing_required: List[str]`
  - `missing_optional: List[str]`
  - `can_proceed: bool`

**And** All models include `Field()` descriptions for OpenAPI docs
**And** Unit tests validate model constraints

**Prerequisites:** Story 1.1 (project structure)

**Technical Notes:**
- Follow API contracts from architecture.md (lines 551-620)
- Follow Pydantic naming convention from architecture.md (lines 330-333)
- Use Pydantic `Field()` with descriptions for auto-generated OpenAPI docs
- Request/response formats from PRD lines 252-283

---

### Story 6.2: Implement POST /api/v1/generate-document Endpoint

As a developer,
I want a REST endpoint to trigger document generation,
So that React app can request documents and receive download URLs.

**Acceptance Criteria:**

**Given** All services are implemented and request/response models exist
**When** I create `app/api/routes/generate.py`
**Then** The endpoint is defined:
```python
@router.post("/generate-document", response_model=GenerateDocumentResponse)
async def generate_document(
    request: GenerateDocumentRequest,
    generator: DocumentGenerator = Depends(get_document_generator)
) -> GenerateDocumentResponse
```

**And** The endpoint:
- Generates correlation_id for request tracing
- Logs request with correlation_id, project_id, template_id, user_id
- Calls `generator.generate_from_project(request.project_id, request.template_id)`
- Returns `GenerateDocumentResponse` with download URL
- Handles all exceptions and converts to appropriate HTTP errors:
  - `ValidationError` → 400 Bad Request
  - `RiskuityAPIError` → 502 Bad Gateway
  - `DocumentGenerationError` → 500 Internal Server Error
  - `S3StorageError` → 500 Internal Server Error

**And** OpenAPI documentation is auto-generated with:
- Endpoint description
- Request/response examples
- Error response examples

**And** Integration test validates:
- Successful generation (200 OK)
- Missing required field error (400)
- API error handling

**Prerequisites:** Story 6.1 (models), Story 5.2 (complete generation flow)

**Technical Notes:**
- Follow API Route Pattern from architecture.md (lines 254-281)
- Endpoint spec from PRD lines 245-283
- Use FastAPI `Depends()` for dependency injection
- Generate correlation_id: `str(uuid.uuid4())`
- Add correlation_id to all logs within request

---

### Story 6.3: Implement GET /api/v1/templates Endpoint

As a developer,
I want an endpoint to list available templates,
So that React app can show template options to users.

**Acceptance Criteria:**

**Given** Template metadata exists
**When** I create endpoint in `app/api/routes/templates.py`
**Then** The endpoint is defined:
```python
@router.get("/templates", response_model=TemplatesResponse)
async def list_templates() -> TemplatesResponse
```

**And** The endpoint:
- Reads template metadata from `app/templates/metadata/field-definitions.yaml`
- Returns list of `TemplateInfo` objects
- Includes template ID, name, description, required fields, optional fields
- Response time < 1 second (NFR-1.2)

**And** Example response:
```json
{
  "templates": [
    {
      "id": "draft-audit-report",
      "name": "Draft Audit Report (FY25)",
      "description": "CORTAP Triennial/State Management Review Draft Report",
      "required_fields": ["recipient_name", "recipient_acronym", "review_type"],
      "optional_fields": ["subrecipient_name", "contractor_name"]
    }
  ]
}
```

**And** Unit test validates response structure

**Prerequisites:** Story 6.1 (models), Story 4.1 (template metadata)

**Technical Notes:**
- Endpoint spec from PRD lines 294-297
- Load metadata once at startup, cache in memory
- Simple, fast endpoint (no external calls)

---

### Story 6.4: Implement GET /api/v1/validate-data Endpoint

As a developer,
I want an endpoint to validate data completeness without generating a document,
So that React app can provide early feedback to users.

**Acceptance Criteria:**

**Given** Validator service is implemented
**When** I create endpoint in `app/api/routes/validate.py`
**Then** The endpoint is defined:
```python
@router.get("/validate-data", response_model=ValidationResponse)
async def validate_data(
    project_id: str = Query(...),
    template_id: str = Query(...),
    validator: Validator = Depends(get_validator),
    data_orchestrator = Depends(get_data_orchestrator)
) -> ValidationResponse
```

**And** The endpoint:
- Fetches template data from Riskuity (via data orchestrator)
- Validates data completeness (via validator)
- Returns validation result (does NOT generate document)
- Response time < 2 seconds (NFR-1.2)

**And** Example response:
```json
{
  "valid": false,
  "missing_required": ["recipient_name"],
  "missing_optional": ["recipient_phone", "subrecipient_name"],
  "can_proceed": false
}
```

**And** Integration test with mocked Riskuity validates response

**Prerequisites:** Story 6.1 (models), Story 4.2 (Validator), Story 3.3 (data orchestrator)

**Technical Notes:**
- Endpoint spec from PRD lines 299-303
- This is a "pre-flight" check before generation
- React app can use this to enable/disable "Generate" button
- Query parameters (not body) for GET request

---

### Story 6.5: Configure FastAPI App with CORS and Lambda Handler

As a developer,
I want FastAPI app configured for Lambda deployment with CORS for React app,
So that the API is accessible from Riskuity frontend and deployable to AWS.

**Acceptance Criteria:**

**Given** All API routes are implemented
**When** I configure `app/main.py`
**Then** The FastAPI app includes:
- CORS middleware configured for Riskuity origin
  - `allow_origins`: `["https://riskuity.com"]` (or from environment variable)
  - `allow_methods`: `["GET", "POST"]`
  - `allow_headers`: `["*"]`
- Exception handlers registered (from Story 1.3)
- All routers included:
  - `app.include_router(generate_router, prefix="/api/v1", tags=["generation"])`
  - `app.include_router(templates_router, prefix="/api/v1", tags=["templates"])`
  - `app.include_router(validate_router, prefix="/api/v1", tags=["validation"])`
- Mangum Lambda handler:
  ```python
  from mangum import Mangum
  handler = Mangum(app, lifespan="off")
  ```

**And** OpenAPI docs available at `/docs` (Swagger UI)
**And** Local development server runs: `uvicorn app.main:app --reload`

**Prerequisites:** All Epic 6 stories (complete API implementation)

**Technical Notes:**
- CORS from architecture.md line 723
- Mangum handler from architecture.md line 715
- API versioning in path: `/api/v1/`
- Set `lifespan="off"` for Lambda (no startup/shutdown events)
- CORS origin should be configurable via environment variable

---

## Epic 7: Testing & AWS Deployment

**Epic Goal:** Implement comprehensive test suite (unit, integration, e2e) and AWS SAM infrastructure for Lambda deployment.

**Business Value:** Ensures code quality, enables confident deployments, and meets NFR-6 maintainability requirements.

**Architectural Components:** `tests/**`, `infra/template.yaml`, `lambda/**`

---

### Story 7.1: Implement Unit Tests for All Services

As a developer,
I want comprehensive unit tests for all service classes,
So that we achieve 70%+ code coverage and can refactor confidently.

**Acceptance Criteria:**

**Given** All service classes are implemented
**When** I create unit tests in `tests/unit/`
**Then** The following test files exist:
- `test_document_generator.py`
- `test_conditional_logic.py`
- `test_riskuity_client.py`
- `test_data_transformer.py`
- `test_validator.py`
- `test_s3_storage.py`
- `test_grammar.py`

**And** Unit tests:
- Mock all I/O operations (API calls, S3, file system)
- Test individual methods in isolation
- Cover happy path and error cases
- Use `pytest` fixtures from `conftest.py`
- Achieve 70%+ code coverage (measured with `pytest-cov`)

**And** Tests are fast (< 10 seconds total for unit tests)
**And** `pytest tests/unit/` runs successfully
**And** Coverage report shows coverage percentage

**Prerequisites:** All service implementation stories

**Technical Notes:**
- Follow Test Organization from architecture.md (lines 369-373)
- Use `pytest` with `pytest-asyncio` for async tests
- Mock with `unittest.mock` or `pytest-mock`
- Coverage target from PRD NFR-6.1 (line 612)
- Run: `pytest tests/unit/ --cov=app --cov-report=term`

---

### Story 7.2: Implement Integration Tests

As a developer,
I want integration tests for service interactions and external dependencies,
So that we validate real API/S3 interactions work correctly.

**Acceptance Criteria:**

**Given** All services are implemented
**When** I create integration tests in `tests/integration/`
**Then** The following test files exist:
- `test_riskuity_client.py` (with mocked Riskuity API responses)
- `test_s3_storage.py` (with LocalStack or mocked S3)
- `test_document_generator.py` (with real python-docxtpl rendering)

**And** Integration tests:
- Test service interactions (e.g., DocumentGenerator + ConditionalLogic + S3Storage)
- Use mocked external services (HTTP mocking, LocalStack for S3)
- Validate end-to-end flows within the service layer
- Use realistic test data (sample CORTAP project data)

**And** Tests run with: `pytest tests/integration/`
**And** Integration tests are slower than unit tests but still reasonable (< 30 seconds)

**Prerequisites:** Story 7.1 (unit tests), all service implementations

**Technical Notes:**
- Follow Test Organization from architecture.md (lines 369-373)
- Use `responses` or `httpx-mock` for HTTP mocking
- Use `moto` or LocalStack for S3 mocking
- Integration tests validate service boundaries
- May require AWS credentials for some tests (use environment variables)

---

### Story 7.3: Implement End-to-End API Tests

As a developer,
I want e2e tests for complete API request/response flows,
So that we validate the entire system works from API to document delivery.

**Acceptance Criteria:**

**Given** All API endpoints are implemented
**When** I create e2e tests in `tests/e2e/`
**Then** The file `test_api_endpoints.py` exists with tests for:
- POST `/api/v1/generate-document` (full generation flow)
- GET `/api/v1/templates`
- GET `/api/v1/validate-data`

**And** E2E tests:
- Use FastAPI `TestClient` to call API endpoints
- Mock Riskuity API and S3 (external dependencies)
- Use real template files and python-docxtpl rendering
- Validate complete request → response flows
- Test error scenarios (400, 500 errors)

**And** Example test:
```python
def test_generate_document_success(test_client, mock_riskuity, mock_s3):
    response = test_client.post("/api/v1/generate-document", json={
        "project_id": "TEST-001",
        "template_id": "draft-audit-report",
        "user_id": "auditor@fta.gov",
        "format": "docx"
    })
    assert response.status_code == 200
    assert "download_url" in response.json()
```

**And** Tests run with: `pytest tests/e2e/`

**Prerequisites:** Story 7.2 (integration tests), Story 6.5 (complete API)

**Technical Notes:**
- Follow Test Organization from architecture.md (lines 369-373)
- Use `TestClient` from `fastapi.testclient`
- E2E tests are slowest but most valuable
- Validate full API contracts match PRD specifications

---

### Story 7.4: Create AWS SAM Infrastructure Template

As a developer,
I want AWS SAM template defining Lambda function, API Gateway, and S3 bucket,
So that we can deploy the complete infrastructure to AWS.

**Acceptance Criteria:**

**Given** The application is ready for deployment
**When** I create `infra/template.yaml`
**Then** The SAM template defines:

**Lambda Function (`CORTAPFunction`):**
- Runtime: `python3.11`
- Handler: `app.main.handler` (Mangum)
- MemorySize: `1024`
- Timeout: `120` (seconds)
- Environment variables:
  - `S3_BUCKET: !Ref DocumentBucket`
  - `RISKUITY_API_KEY: !Ref RiskuityAPISecret` (from Secrets Manager)
  - `RISKUITY_BASE_URL` (from parameter)
  - `LOG_LEVEL: INFO`
- IAM Policies:
  - S3CrudPolicy for DocumentBucket
  - `secretsmanager:GetSecretValue` for RiskuityAPISecret

**API Gateway (`CORTAPApi`):**
- Type: `AWS::Serverless::HttpApi`
- CORS configuration: Allow Riskuity origin
- Integration: Lambda proxy

**S3 Bucket (`DocumentBucket`):**
- Encryption: AES-256
- Lifecycle policy: Delete objects > 90 days old (optional)
- Private access (no public access)

**Secrets Manager (`RiskuityAPISecret`):**
- Secret for Riskuity API key

**And** `infra/samconfig.toml` exists with deployment configuration
**And** SAM template validates: `sam validate`

**Prerequisites:** Story 6.5 (Mangum handler configured)

**Technical Notes:**
- Follow architecture.md Deployment Architecture (lines 703-766)
- SAM template from architecture lines 731-766
- Use CloudFormation intrinsic functions (`!Ref`, `!GetAtt`)
- Parameters for environment-specific values (dev/staging/prod)
- Outputs: API Gateway URL, S3 bucket name

---

### Story 7.5: Create Lambda Deployment Package

As a developer,
I want a Lambda deployment package with all dependencies,
So that the Lambda function has everything needed to run.

**Acceptance Criteria:**

**Given** SAM template is created
**When** I configure Lambda deployment in `lambda/` directory
**Then** The following exists:

**`lambda/requirements.txt`:**
- All production dependencies (FastAPI, python-docxtpl, boto3, mangum, httpx, pydantic, pydantic-settings, pyyaml)
- Pinned versions matching architecture.md

**Lambda Layer (optional):**
- Large dependencies (python-docxtpl, docx) in separate layer for reuse
- Reduces deployment package size
- Faster deployments

**Build process:**
- `sam build` compiles deployment package
- Dependencies installed from `lambda/requirements.txt`
- Application code (`app/`) included
- Templates (`app/templates/*.docx`) included

**And** Local testing works:
- `sam local start-api` starts local API
- `curl http://localhost:3000/api/v1/templates` returns templates

**Prerequisites:** Story 7.4 (SAM template)

**Technical Notes:**
- Lambda deployment from architecture.md lines 713-717
- Use SAM `sam build` to create deployment package
- Lambda layer for dependencies > 50MB (architecture line 716)
- Template files must be included in package
- Test locally with `sam local` before deploying

---

### Story 7.6: Deploy to AWS and Validate

As a developer,
I want to deploy the complete stack to AWS dev environment,
So that we can validate the system works in AWS infrastructure.

**Acceptance Criteria:**

**Given** SAM template and deployment package are ready
**When** I run `sam deploy --guided --config-env dev`
**Then** The deployment:
- Creates CloudFormation stack
- Deploys Lambda function
- Creates API Gateway
- Creates S3 bucket
- Stores Riskuity API secret in Secrets Manager
- Outputs API Gateway URL

**And** Post-deployment validation:
- API Gateway URL is accessible
- GET `/api/v1/templates` returns 200 OK
- CloudWatch Logs show structured JSON logs
- Lambda execution role has correct permissions

**And** Manual test from React app (or curl):
- POST `/api/v1/generate-document` with test data
- Returns download URL
- Document downloads successfully from S3 pre-signed URL
- Generated document has correct formatting

**And** Deployment documentation updated in `README.md`:
- Prerequisites (AWS CLI, SAM CLI, credentials)
- Deployment commands
- Environment variable configuration

**Prerequisites:** Story 7.5 (deployment package), all previous stories complete

**Technical Notes:**
- First deployment to AWS dev environment
- Use `--guided` for initial deploy (prompts for parameters)
- Save config in `samconfig.toml` for future deploys
- Validate with real Riskuity API credentials (if available) or mocked
- Document deployment process in README
- This completes the MVP!

---

## Epic Breakdown Summary

**Total: 9 Epics, 43 Stories** (Updated with Data Service Pattern and RIR Template)

**REVISED EPIC SEQUENCE:**
- **Epic 1: Foundation & Template Engine** - 6 stories ✅ (Weeks 1-2)
- **Epic 3.5: Project Data Service** - 7 stories 🆕 (Week 3)
- **Epic 4: Recipient Information Request Template** - 6 stories 🆕 (Week 4)
- **Epic 2: Conditional Logic Engine** - 8 stories 🔄 DEFERRED (Weeks 5-6)
- **Epic 3: Riskuity API Integration** - ❌ MERGED into Epic 3.5
- **Epic 5: Validation Engine** - 3 stories (renumbered from Epic 4) (Week 7)
- **Epic 6: AWS S3 Storage** - 2 stories (renumbered from Epic 5) (Week 7)
- **Epic 7: REST API & React Integration** - 5 stories (renumbered from Epic 6) (Week 8)
- **Epic 8: Testing & AWS Deployment** - 6 stories (renumbered from Epic 7) (Week 9)

**Estimated Timeline (REVISED):**
- **Epic 1:** 1-2 weeks (foundation + POC validation)
- **Epic 3.5:** 1 week (data service layer - enables parallel development)
- **Epic 4:** 1 week (RIR template - validates architecture with simple template)
- **Epic 2:** 1.5 weeks (complex conditional logic - benefits from Epic 4 lessons)
- **Epic 5:** 0.5 weeks (validation)
- **Epic 6:** 0.5 weeks (S3 storage)
- **Epic 7:** 0.5 weeks (REST API)
- **Epic 8:** 1 week (testing + deployment)

**Total: ~7-8 weeks for MVP** (extended from original 5-6 weeks to include data service architecture and RIR template as architectural validation)

**Key Dependencies (REVISED):**
- ✅ **Epic 1 must complete first** (foundation for all)
- ✅ **Epic 3.5 depends on Epic 1** (needs DocumentGenerator, exceptions, logging)
- ✅ **Epic 4 depends on Epic 3.5** (RIR consumes data service JSON)
- 🔄 **Epic 2 DEFERRED after Epic 4** (learns from RIR implementation, reduces risk)
- **Epic 5-8 sequence unchanged** (same dependencies as before)

**Critical Path Changes:**
- **Old:** Epic 1 → Epic 2 (Conditional Logic) → Epic 3 (Riskuity) → Templates
- **New:** Epic 1 → Epic 3.5 (Data Service) → Epic 4 (RIR) → Epic 2 (Conditional Logic) → Templates

**Rationale for Sequence Change:**
1. **Data Service Pattern** (Epic 3.5) enables multi-template efficiency and parallel development
2. **RIR Template** (Epic 4) validates complete architecture with simpler use case
3. **Conditional Logic** (Epic 2) benefits from architectural lessons learned in Epic 4
4. **Reduced Risk:** Tackle complex Draft Report logic after validating data flow with RIR

**Next Steps:**
1. Review this epic breakdown with stakeholders
2. Run `sprint-planning` workflow to organize stories into sprints
3. Begin implementation with Story 1.1

---

_Generated by BMad Method Epic & Story Decomposition Workflow_
_Date: 2025-11-12_

_Generated by BMad Method Epic & Story Decomposition Workflow_
_Date: 2025-11-12_
