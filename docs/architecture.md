# Architecture

## Executive Summary

CORTAP-RPT is a Python-based document generation microservice that bridges Riskuity (compliance data source) and Microsoft Word (audit report output). The architecture prioritizes formatting preservation, intelligent conditional logic, and integration reliability. This document establishes technical decisions to ensure AI agents implement consistent, maintainable code across all epics.

## Project Initialization

**First Implementation Story: Initialize FastAPI Project**

```bash
# Install fastapi-template-cli
pip install fastapi-template-cli

# Create project with SQLAlchemy (for future job queue metadata if needed)
fastapi-template new cortap-rpt --orm sqlalchemy --type api

# Install additional dependencies for document generation
cd cortap-rpt
pip install python-docxtpl boto3 pydantic-settings
```

**What the Starter Provides:**
- ✅ FastAPI application structure with async support
- ✅ SQLAlchemy ORM setup (optional for MVP, useful for v2 job tracking)
- ✅ JWT authentication scaffolding
- ✅ Docker and docker-compose configuration
- ✅ Automatic OpenAPI/Swagger documentation
- ✅ Pydantic models for data validation
- ✅ Production-ready logging configuration
- ✅ Environment-based configuration management
- ✅ pytest test structure

**Note:** We'll remove unused auth/database scaffolding during Epic 1, keeping only what's needed for document generation API.

## Decision Summary

| Category | Decision | Version | Affects Epics | Rationale |
| -------- | -------- | ------- | ------------- | --------- |
| Runtime | Python | 3.11.14 | All | Excellent performance, stable, full library support, AWS Lambda compatible |
| API Framework | FastAPI | 0.121.1 | Epic 6 | Async support, automatic OpenAPI docs, high performance, v2 async-ready |
| Template Engine | python-docxtpl | 0.20.1 | Epic 1, 2 | Jinja2 support for complex conditional logic, 9 pattern requirements |
| Data Validation | Pydantic | 2.x | All | FastAPI native integration, type safety, request/response validation |
| AWS Compute | Lambda + Mangum | Mangum 0.19.0 | Epic 7 | Serverless, auto-scaling, cost-effective for usage pattern, 15min timeout sufficient |
| AWS Storage | S3 + boto3 | boto3 1.40.x | Epic 5 | Document storage, pre-signed URLs, AWS native integration |
| HTTP Client | httpx | Latest | Epic 3 | Async-capable for Riskuity API calls, modern replacement for requests |
| Testing Framework | pytest | 9.0.0 | Epic 7 | Industry standard, async support, comprehensive plugin ecosystem |
| Deployment | AWS SAM / Lambda | - | Epic 7 | Simplified Lambda deployment, local testing, infrastructure as code |

## Project Structure

```
cortap-rpt/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app + Lambda handler (Mangum)
│   ├── config.py                    # Environment configuration (Pydantic Settings)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── generate.py          # POST /api/v1/generate-document
│   │   │   ├── templates.py         # GET /api/v1/templates
│   │   │   └── validate.py          # GET /api/v1/validate-data
│   │   └── dependencies.py          # FastAPI dependencies (S3 client, etc.)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request.py               # Pydantic request models
│   │   ├── response.py              # Pydantic response models
│   │   └── template_data.py         # Template field data models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document_generator.py    # Core document generation logic
│   │   ├── conditional_logic.py     # 9 conditional logic patterns implementation
│   │   ├── riskuity_client.py       # Riskuity API integration
│   │   ├── data_transformer.py      # API response → template data mapping
│   │   ├── validator.py             # Data completeness validation
│   │   └── s3_storage.py            # S3 upload/download operations
│   ├── templates/
│   │   ├── draft-audit-report.docx  # Word templates with Jinja2 syntax
│   │   ├── cover-letter.docx
│   │   └── metadata/
│   │       └── field-definitions.yaml   # Required vs optional fields per template
│   └── utils/
│       ├── __init__.py
│       ├── grammar.py               # Grammar helper functions (is/are, a/an)
│       └── logging.py               # Structured logging setup
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # pytest fixtures
│   ├── unit/
│   │   ├── test_conditional_logic.py
│   │   ├── test_data_transformer.py
│   │   ├── test_validator.py
│   │   └── test_grammar.py
│   ├── integration/
│   │   ├── test_riskuity_client.py
│   │   ├── test_s3_storage.py
│   │   └── test_document_generator.py
│   └── e2e/
│       └── test_api_endpoints.py
├── lambda/
│   ├── requirements.txt             # Lambda deployment dependencies
│   └── layer/                       # Lambda layer for python-docxtpl + dependencies
├── infra/
│   ├── template.yaml                # AWS SAM template for Lambda + API Gateway + S3
│   └── samconfig.toml               # SAM deployment configuration
├── docs/
│   ├── api-specification.yaml       # OpenAPI spec (auto-generated by FastAPI)
│   └── conditional-logic-rules.md   # Business rules documentation
├── .env.example                     # Environment variable template
├── .gitignore
├── requirements.txt                 # Development dependencies
├── requirements-dev.txt             # Testing/linting dependencies
├── pytest.ini                       # pytest configuration
├── pyproject.toml                   # Python project metadata
└── README.md
```

## Epic to Architecture Mapping

| Epic | Primary Components | Integration Points |
|------|-------------------|-------------------|
| Epic 1: Template Engine & Formatting | `services/document_generator.py`<br>`templates/*.docx`<br>`utils/grammar.py` | python-docxtpl library, Jinja2 template syntax in Word docs |
| Epic 2: Conditional Logic Engine | `services/conditional_logic.py`<br>`models/template_data.py` | Called by document_generator, uses template field metadata |
| Epic 3: Riskuity API Integration | `services/riskuity_client.py`<br>`services/data_transformer.py` | httpx → Riskuity API endpoints, transforms to template_data models |
| Epic 4: Validation Engine | `services/validator.py`<br>`templates/metadata/field-definitions.yaml` | Validates template_data before generation, returns warnings/errors |
| Epic 5: AWS S3 Storage | `services/s3_storage.py`<br>`infra/template.yaml` (S3 bucket) | boto3 → S3, generates pre-signed URLs |
| Epic 6: React/Node Integration | `api/routes/*.py`<br>`main.py` (FastAPI app) | REST API endpoints, Pydantic request/response models |
| Epic 7: Testing & Deployment | `tests/**`<br>`infra/**` (AWS SAM)<br>`lambda/**` | pytest, AWS SAM CLI, Lambda + API Gateway |

## Technology Stack Details

### Core Technologies

**Application Framework:**
- FastAPI 0.121.1 - ASGI web framework with automatic OpenAPI documentation
- Mangum 0.19.0 - ASGI to AWS Lambda adapter
- Pydantic 2.x - Data validation and settings management

**Document Generation:**
- python-docxtpl 0.20.1 - Jinja2-based Word template engine
- Jinja2 (bundled with docxtpl) - Template logic and conditionals

**AWS Integration:**
- boto3 1.40.x - AWS SDK for Python (S3 operations)
- AWS Lambda Python 3.11 runtime
- AWS API Gateway - HTTP API for REST endpoints
- AWS S3 - Document storage with pre-signed URLs

**HTTP & Data:**
- httpx - Async HTTP client for Riskuity API calls
- Pydantic Settings - Environment-based configuration

**Development & Testing:**
- pytest 9.0.0 - Testing framework
- pytest-asyncio - Async test support
- pytest-cov - Code coverage reporting
- black - Code formatting
- ruff - Fast Python linter

**Deployment:**
- AWS SAM - Serverless Application Model for infrastructure as code
- Docker - Local testing and Lambda container images

### Integration Points

**Riskuity API → CORTAP-RPT:**
- Protocol: REST API over HTTPS
- Authentication: Bearer token (API key)
- Data flow: GET project data → Transform to template model → Generate document
- Endpoints consumed:
  - `GET /v1/projects/{project_id}`
  - `GET /v1/projects/{project_id}/assessments`
  - `GET /v1/projects/{project_id}/surveys`
  - `GET /v1/projects/{project_id}/risks`

**CORTAP-RPT → AWS S3:**
- Protocol: boto3 SDK
- Authentication: IAM role (Lambda execution role)
- Data flow: Generate .docx in memory → Upload to S3 → Return pre-signed URL
- Bucket structure: `{bucket}/{project_id}/{template_id}/{timestamp}_{filename}.docx`

**React/Node → CORTAP-RPT API:**
- Protocol: REST API over HTTPS
- Authentication: Shared secret or JWT (configured via environment)
- Endpoints exposed:
  - `POST /api/v1/generate-document` - Main generation endpoint
  - `GET /api/v1/templates` - List available templates
  - `GET /api/v1/validate-data` - Pre-generation validation
- Response format: JSON with download URLs

## Implementation Patterns

These patterns ensure consistent implementation across all AI agents:

### Module Structure Pattern

**ALL Python modules MUST follow this structure:**

```python
"""Module docstring describing purpose."""

# Standard library imports
import json
from datetime import datetime

# Third-party imports
from fastapi import HTTPException
from pydantic import BaseModel

# Local imports
from app.models.request import GenerateDocumentRequest
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ServiceClass:
    """Class docstring."""

    def __init__(self):
        pass

    async def method_name(self, param: str) -> dict:
        """Method docstring with params and return type."""
        pass
```

**Import ordering:** Standard lib → Third-party → Local (alphabetical within each group)

### Service Layer Pattern

**ALL services MUST:**
- Be instantiated as classes with dependency injection
- Use async/await for I/O operations (API calls, S3, file operations)
- Accept dependencies via `__init__` (e.g., S3 client, HTTP client)
- Return Pydantic models or primitives (never raw dicts for complex data)
- Raise custom exceptions (never generic Exception)

**Example:**
```python
class DocumentGenerator:
    def __init__(self, s3_client: S3Storage, validator: Validator):
        self.s3_client = s3_client
        self.validator = validator

    async def generate(self, project_id: str, template_id: str) -> GeneratedDocument:
        """Generate document from template."""
        # Implementation
        pass
```

### API Route Pattern

**ALL FastAPI routes MUST:**
- Use Pydantic models for request/response
- Include docstrings for OpenAPI documentation
- Use dependency injection for services
- Return appropriate HTTP status codes
- Handle exceptions with try/except and convert to HTTPException

**Example:**
```python
@router.post("/generate-document", response_model=GenerateDocumentResponse)
async def generate_document(
    request: GenerateDocumentRequest,
    generator: DocumentGenerator = Depends(get_document_generator)
) -> GenerateDocumentResponse:
    """
    Generate a CORTAP audit report document.

    - **project_id**: Riskuity CORTAP project ID
    - **template_id**: Template identifier (e.g., 'draft-audit-report')
    """
    try:
        result = await generator.generate(request.project_id, request.template_id)
        return result
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.details)
```

### Data Validation Pattern

**ALL data validation MUST:**
- Use Pydantic models with type hints
- Define validators for business logic constraints
- Separate request models, response models, and domain models
- Use Field() for optional fields with defaults

**Example:**
```python
from pydantic import BaseModel, Field, field_validator

class GenerateDocumentRequest(BaseModel):
    project_id: str = Field(..., description="Riskuity project ID")
    template_id: str = Field(..., description="Template identifier")
    user_id: str = Field(..., description="User ID for audit logging")
    format: str = Field(default="docx", description="Output format")

    @field_validator("template_id")
    def validate_template_id(cls, v):
        allowed = ["draft-audit-report", "cover-letter", "rfi-package"]
        if v not in allowed:
            raise ValueError(f"Invalid template_id. Allowed: {allowed}")
        return v
```

## Consistency Rules

### Naming Conventions

**Files and Directories:**
- Python files: `snake_case.py` (e.g., `document_generator.py`)
- Test files: `test_<module_name>.py` (e.g., `test_document_generator.py`)
- Directories: `snake_case/` (e.g., `services/`, `api/routes/`)

**Python Code:**
- Classes: `PascalCase` (e.g., `DocumentGenerator`, `RiskuityClient`)
- Functions/Methods: `snake_case` (e.g., `generate_document`, `fetch_project_data`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- Private methods: `_leading_underscore` (e.g., `_transform_data`)
- Async functions: Always prefix with `async def`, never use sync wrappers

**API Endpoints:**
- Pattern: `/api/v1/resource-name` (kebab-case)
- Examples: `/api/v1/generate-document`, `/api/v1/validate-data`
- Version in path: `/api/v1/` (explicit versioning)

**Pydantic Models:**
- Request models: `<Action><Resource>Request` (e.g., `GenerateDocumentRequest`)
- Response models: `<Action><Resource>Response` (e.g., `GenerateDocumentResponse`)
- Domain models: `<ResourceName>Data` (e.g., `TemplateData`, `ProjectData`)

**Template Fields:**
- Jinja2 variables: `{{ snake_case }}` (e.g., `{{ recipient_name }}`, `{{ review_type }}`)
- Conditional blocks: `{% if condition %}...{% endif %}`
- Loops: `{% for item in items %}...{% endfor %}`

### Code Organization

**Service Dependencies:**
- Services import models, not vice versa
- Services don't import from `api/` layer
- API routes depend on services via dependency injection
- Circular imports are forbidden

**Configuration Management:**
- ALL environment variables in `.env` file (gitignored)
- Use Pydantic Settings for type-safe config
- Config class name: `Settings` in `app/config.py`
- Access config via dependency injection, never global imports

**Example:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    riskuity_api_key: str
    riskuity_base_url: str = "https://api.riskuity.com/v1"
    s3_bucket_name: str
    aws_region: str = "us-east-1"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
```

**Test Organization:**
- `tests/unit/` - Test single functions/classes in isolation (mock all I/O)
- `tests/integration/` - Test service integrations (real AWS/API calls with mocking)
- `tests/e2e/` - Test full API endpoints (TestClient, full stack)
- Fixtures in `conftest.py` - Shared test data and mocks

### Error Handling

**Custom Exception Hierarchy:**
```python
class CORTAPError(Exception):
    """Base exception for all CORTAP-RPT errors."""
    def __init__(self, message: str, error_code: str, details: dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class RiskuityAPIError(CORTAPError):
    """Raised when Riskuity API call fails."""
    pass

class DocumentGenerationError(CORTAPError):
    """Raised when document generation fails."""
    pass

class ValidationError(CORTAPError):
    """Raised when data validation fails."""
    pass

class S3StorageError(CORTAPError):
    """Raised when S3 operations fail."""
    pass
```

**Error Handling Rules:**
- Services raise custom exceptions (never raw Exception or generic errors)
- API routes catch exceptions and convert to HTTPException with appropriate status codes
- Log all errors before raising
- Include correlation_id in error responses for tracking
- Never expose internal errors to API consumers (sanitize messages)

**FastAPI Exception Handler:**
```python
@app.exception_handler(CORTAPError)
async def cortap_error_handler(request: Request, exc: CORTAPError):
    return JSONResponse(
        status_code=400,  # or map error_code to status
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "correlation_id": request.state.correlation_id
        }
    )
```

### Logging Strategy

**Structured JSON Logging for CloudWatch:**

```python
import logging
import json
from datetime import datetime
from typing import Any

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": "cortap-rpt",
            "module": record.module,
            "function": record.funcName,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", None)
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)  # Use env var for level
    return logger
```

**Logging Rules:**
- Log at service boundaries (API entry, external calls, S3 operations)
- Use appropriate levels: DEBUG (detailed), INFO (normal flow), WARNING (degraded), ERROR (failure)
- Include correlation_id in all logs for request tracing
- Never log sensitive data: API keys, tokens, PII (mask if necessary)
- Log before raising exceptions

**Standard Log Messages:**
```python
logger.info("Generating document", extra={
    "correlation_id": correlation_id,
    "project_id": project_id,
    "template_id": template_id
})

logger.error("Riskuity API call failed", extra={
    "correlation_id": correlation_id,
    "endpoint": url,
    "status_code": response.status_code,
    "error": str(error)
})

## Data Architecture

### Core Data Models

**TemplateData** - Complete data model for document generation:
```python
class TemplateData(BaseModel):
    # Recipient Information
    recipient_name: str
    recipient_acronym: str
    region_number: int

    # Review Configuration
    review_type: Literal["Triennial Review", "State Management Review", "Combined Triennial and State Management Review"]
    exit_conference_format: Literal["virtual", "in-person"]

    # Assessment Data
    assessments: List[AssessmentData]  # 23 review areas
    has_deficiencies: bool
    deficiency_count: int
    deficiency_areas: List[str]  # For [LIST] fields

    # Optional Fields
    erf_count: int = 0
    erf_areas: List[str] = []
    reviewed_subrecipients: bool = False
    subrecipient_name: Optional[str] = None

    # Personnel & Dates
    audit_team: List[PersonData]
    site_visit_dates: DateRange
    report_date: datetime
```

**AssessmentData** - Individual review area:
```python
class AssessmentData(BaseModel):
    review_area: str  # e.g., "Legal", "Financial Management"
    finding: Literal["D", "ND", "NA"]  # Deficient, Non-Deficient, Not Applicable
    deficiency_code: Optional[str] = None  # Only if finding == "D"
    description: Optional[str] = None
    corrective_action: Optional[str] = None
    due_date: Optional[datetime] = None
    date_closed: Optional[datetime] = None
```

**Data Flow:**
1. **Riskuity API Response** → `RiskuityProjectData` (raw API model)
2. **Data Transformer** → `TemplateData` (template-ready model)
3. **Validator** → Checks completeness, returns warnings/errors
4. **Document Generator** → Jinja2 context dict from `TemplateData`
5. **python-docxtpl** → Rendered Word document (BytesIO)
6. **S3 Storage** → Uploaded .docx, returns pre-signed URL

### Data Transformation Rules

**Boolean Derivations:**
- `has_deficiencies = any(a.finding == "D" for a in assessments)`
- `reviewed_subrecipients = subrecipient_name is not None`

**List Formatting:**
- `deficiency_areas`: Comma-separated list with "and" before last item
- Example: `["Legal", "Financial Management", "Procurement"]` → `"Legal, Financial Management, and Procurement"`

**Date Formatting:**
- Internal: `datetime` objects with UTC timezone
- Template output: Converted to template-specific format (e.g., `"November 12, 2025"`)

## API Contracts

### POST /api/v1/generate-document

**Request:**
```json
{
  "project_id": "RSKTY-12345",
  "template_id": "draft-audit-report",
  "user_id": "auditor@fta.gov",
  "format": "docx"
}
```

**Success Response (200 OK):**
```json
{
  "status": "success",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "download_url": "https://cortap-docs.s3.amazonaws.com/...",
  "generated_at": "2025-11-12T10:30:00Z",
  "warnings": [
    "Optional field [recipient_phone] was missing - used default 'N/A'"
  ]
}
```

**Error Response (400 Bad Request):**
```json
{
  "error_code": "MISSING_REQUIRED_FIELD",
  "message": "Required field missing: [recipient_name]",
  "details": {
    "missing_fields": ["recipient_name", "review_type"]
  },
  "timestamp": "2025-11-12T10:30:00Z",
  "correlation_id": "req-abc123"
}
```

### GET /api/v1/templates

**Response (200 OK):**
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

### GET /api/v1/validate-data

**Query Parameters:** `?project_id=RSKTY-12345&template_id=draft-audit-report`

**Response (200 OK):**
```json
{
  "valid": false,
  "missing_required": ["recipient_name"],
  "missing_optional": ["recipient_phone", "subrecipient_name"],
  "can_proceed": false
}
```

## Security Architecture

### Authentication & Authorization

**Riskuity API → CORTAP-RPT:**
- No authentication in MVP (Lambda not publicly exposed)
- Future: API Gateway with API Key or JWT validation

**CORTAP-RPT → Riskuity API:**
- Bearer token authentication via `Authorization: Bearer {api_key}`
- API key stored in AWS Secrets Manager (accessed by Lambda)
- Rotated every 90 days (manual process in MVP)

**CORTAP-RPT → AWS S3:**
- IAM role-based authentication (Lambda execution role)
- Least privilege: S3 PutObject, GetObject, ListBucket permissions only
- Bucket policy restricts access to Lambda role

### Data Protection

**In Transit:**
- HTTPS/TLS 1.2+ for all API communication
- API Gateway enforces HTTPS
- Riskuity API uses HTTPS

**At Rest:**
- S3 bucket encryption enabled (AES-256)
- Lambda environment variables encrypted with AWS KMS
- Secrets Manager for API keys (encrypted at rest)

**Sensitive Data Handling:**
- API keys never logged or exposed in responses
- PII data (recipient names, contact info) only in generated documents
- Generated documents stored in private S3 bucket (no public access)
- Pre-signed URLs expire after 24 hours

### Compliance Considerations

**Government Data:**
- FTA audit data is not classified but considered sensitive
- Documents contain official federal compliance records
- S3 storage meets federal data protection standards
- Audit trail via CloudWatch Logs (90-day retention)

## Performance Considerations

### Document Generation Optimization

**Target: 30-60 seconds per document (NFR-1.1)**

**Strategies:**
1. **Template Caching:** Load .docx templates once, cache in memory (Lambda warm start)
2. **Streaming Generation:** Generate document in memory (BytesIO), never write to disk
3. **Async Operations:** Parallel Riskuity API calls for multiple endpoints
4. **S3 Multipart Upload:** Use for documents >5MB (rare, but ready)

**Lambda Configuration:**
- Memory: 1024 MB (balance cost vs performance)
- Timeout: 120 seconds (2x target, allows for retries)
- Ephemeral storage: 512 MB (default, sufficient for in-memory generation)

### Concurrent User Support

**Target: 20 concurrent users (NFR-1.3)**

**Strategies:**
- Lambda auto-scales up to 1000 concurrent executions (AWS default)
- Reserve concurrency: 25 (buffer for 20 users + retries)
- API Gateway throttling: 100 requests/second burst, 50 steady-state

### Retry Logic

**Riskuity API Calls:**
- Exponential backoff: 1s, 2s, 4s delays
- Max retries: 3
- Timeout per request: 10 seconds

**S3 Upload:**
- Boto3 built-in retries (3 attempts)
- Fail entire generation if S3 upload fails

## Deployment Architecture

### AWS Lambda + API Gateway

```
Internet → API Gateway (HTTP API) → Lambda Function → S3 Bucket
                                          ↓
                                     Riskuity API
```

**Lambda Function:**
- Runtime: Python 3.11
- Handler: `app.main.handler` (Mangum wrapper)
- Layers: python-docxtpl + dependencies (separate layer for reuse)
- VPC: Not required (public internet access for Riskuity API)

**API Gateway:**
- Type: HTTP API (simpler, cheaper than REST API)
- Integration: Lambda proxy integration
- Custom domain: TBD (e.g., `cortap-api.fta.gov`)
- CORS: Enabled for Riskuity React app origin

**S3 Bucket:**
- Name: `cortap-documents-{env}` (e.g., `cortap-documents-prod`)
- Versioning: Disabled in MVP (enable in v2)
- Lifecycle policy: Delete documents older than 90 days
- Access: Private (pre-signed URLs only)

### Infrastructure as Code (AWS SAM)

**template.yaml structure:**
```yaml
Resources:
  CORTAPFunction:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: python3.11
      MemorySize: 1024
      Timeout: 120
      Environment:
        Variables:
          S3_BUCKET: !Ref DocumentBucket
      Policies:
        - S3CrudPolicy:
            BucketName: !Ref DocumentBucket
        - Statement:
            Effect: Allow
            Action: secretsmanager:GetSecretValue
            Resource: !Ref RiskuityAPISecret

  CORTAPApi:
    Type: AWS::Serverless::HttpApi
    Properties:
      CorsConfiguration:
        AllowOrigins: ["https://riskuity.com"]

  DocumentBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
```

### Deployment Pipeline

**MVP: Manual deployment via SAM CLI**
```bash
sam build
sam deploy --guided
```

**Future (v2): CI/CD Pipeline**
- GitHub Actions or AWS CodePipeline
- Environments: dev, staging, prod
- Automated tests before deployment

## Development Environment

### Prerequisites

- Python 3.11.14 installed
- AWS CLI configured with credentials
- AWS SAM CLI installed
- Docker (for local Lambda testing)
- Git

### Setup Commands

```bash
# Clone repository
git clone https://github.com/your-org/cortap-rpt.git
cd cortap-rpt

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your Riskuity API credentials

# Run tests
pytest tests/

# Run local API server (for development)
uvicorn app.main:app --reload

# Test with SAM local (simulates Lambda)
sam build
sam local start-api
```

### Local Development Workflow

1. Make code changes in `app/` directory
2. Run unit tests: `pytest tests/unit/`
3. Test API endpoint: `curl http://localhost:8000/api/v1/templates`
4. Run integration tests: `pytest tests/integration/` (requires AWS credentials)
5. Deploy to dev: `sam deploy --config-env dev`

## Architecture Decision Records (ADRs)

### ADR-001: FastAPI over Flask
**Decision:** Use FastAPI instead of Flask
**Rationale:**
- Native async support critical for v2 async job queue
- Automatic OpenAPI documentation reduces manual work
- Pydantic integration provides type safety
- Better performance for concurrent users
**Tradeoffs:** Slightly steeper learning curve, but team expertise in Python mitigates this

### ADR-002: AWS Lambda over ECS/EC2
**Decision:** Deploy as AWS Lambda serverless function
**Rationale:**
- 30-60 second generation time fits within Lambda 15min timeout
- Auto-scaling handles variable load (36-100 documents/year)
- Pay-per-use cost model optimal for low-volume usage
- No server management overhead for small team
**Tradeoffs:** Cold start latency (mitigated by reserved concurrency), 15min hard timeout (acceptable)

### ADR-003: python-docxtpl over docx-mailmerge
**Decision:** Use python-docxtpl as template engine
**Rationale:**
- Native Jinja2 support handles 9 complex conditional logic patterns
- Better suited for nested conditionals and loops
- Active maintenance and community
**Tradeoffs:** Slightly heavier dependency, but functionality is essential

### ADR-004: Synchronous MVP, Async v2
**Decision:** MVP uses synchronous document generation, defer async job queue to v2
**Rationale:**
- 30-60 second generation time acceptable for auditors to wait
- Simplifies MVP architecture (no job queue, no status tracking)
- Validates core functionality before adding complexity
**Tradeoffs:** User must wait during generation, but feedback indicates this is acceptable

### ADR-005: S3 Pre-Signed URLs over Direct Download
**Decision:** Store documents in S3 and return pre-signed URLs
**Rationale:**
- Decouples document storage from Lambda
- Pre-signed URLs provide secure, temporary access
- S3 handles high download bandwidth
- Enables future features (versioning, lifecycle policies)
**Tradeoffs:** Extra S3 API call, but overhead is negligible

### ADR-006: AWS SAM over Terraform
**Decision:** Use AWS SAM for infrastructure as code
**Rationale:**
- Optimized for serverless Lambda deployments
- Simpler syntax for Lambda + API Gateway
- Built-in local testing with `sam local`
- Team already familiar with CloudFormation
**Tradeoffs:** AWS-specific (not multi-cloud), but no multi-cloud requirement exists

---

_Generated by BMAD Decision Architecture Workflow v1.3.2_
_Date: 2025-11-12_
_For: Bob_
