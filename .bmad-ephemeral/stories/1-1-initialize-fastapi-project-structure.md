# Story 1.1: Initialize FastAPI Project Structure

Status: review

## Story

As a developer,
I want to set up the FastAPI project with the recommended starter template,
so that we have a production-ready foundation with proper structure and tooling.

## Acceptance Criteria

1. **AC-1**: Project structure matches architecture.md specification

   - FastAPI app with async support configured
   - Pydantic models structure created
   - Environment-based configuration (`.env` support) implemented
   - pytest test structure initialized
   - Docker setup included
   - Git repository initialized with `.gitignore`

2. **AC-2**: Unused scaffolding is removed

   - Remove JWT auth if not needed for MVP
   - Remove SQLAlchemy database models (keep ORM for v2 job queue metadata only)
   - Keep core FastAPI structure

3. **AC-3**: Additional dependencies are installed

   - python-docxtpl 0.20.1
   - boto3 1.40.x
   - httpx (latest)
   - mangum 0.19.0 (Lambda adapter)

4. **AC-4**: Configuration module implemented

   - `app/config.py` using Pydantic Settings with fields: `riskuity_api_key`, `riskuity_base_url`, `s3_bucket_name`, `aws_region`, `log_level`
   - `.env.example` template created

5. **AC-5**: Module structure pattern followed
   - Import ordering: Standard lib → Third-party → Local (alphabetical within each group)
   - All modules follow architecture.md Module Structure Pattern (lines 197-228)

## Tasks / Subtasks

- [x] **Task 1**: Install FastAPI template CLI and create project (AC: #1)

  - [x] Install `fastapi-template-cli`: `pip install fastapi-template-cli`
  - [x] Create project: `fastapi-template new cortap-rpt --orm sqlalchemy --type api`
  - [x] Verify directory structure matches architecture.md Project Structure (lines 73-157)

- [x] **Task 2**: Install additional dependencies (AC: #3)

  - [x] Add docxtpl 0.20.1 to pyproject.toml
  - [x] Add boto3 1.40.x to pyproject.toml
  - [x] Add httpx (latest) to pyproject.toml
  - [x] Add mangum 0.19.0 to pyproject.toml
  - [x] Run `pip install -e ".[dev]"`

- [x] **Task 3**: Remove unused scaffolding (AC: #2)

  - [x] Remove JWT authentication scaffolding (if present)
  - [x] Remove SQLAlchemy database models (keep ORM infrastructure)
  - [x] Clean up unused imports and dependencies
  - [x] Verify core FastAPI structure remains intact

- [x] **Task 4**: Implement configuration module (AC: #4)

  - [x] Create `app/config.py` with Pydantic Settings class
  - [x] Define required fields: `riskuity_api_key`, `riskuity_base_url`, `s3_bucket_name`, `aws_region`, `log_level`
  - [x] Configure `.env` file loading
  - [x] Create `.env.example` template with placeholder values

- [x] **Task 5**: Initialize Git repository (AC: #1)

  - [x] Run `git init`
  - [x] Create `.gitignore` with Python-specific entries
  - [x] Add `.env` to `.gitignore`
  - [x] Create initial commit with base structure

- [x] **Task 6**: Verify project setup (AC: #5)
  - [x] Review module structure matches architecture.md patterns
  - [x] Verify import ordering follows standard lib → third-party → local
  - [x] Test that FastAPI app imports successfully
  - [x] Verify pytest test discovery works: `pytest --collect-only`

## Dev Notes

### Architecture Alignment

**Project Structure** (from architecture.md lines 73-157):

```
cortap-rpt/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app + Lambda handler (Mangum)
│   ├── config.py                    # Environment configuration (Pydantic Settings)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   └── __init__.py
│   │   └── dependencies.py
│   ├── models/
│   │   └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   ├── templates/
│   └── utils/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── lambda/
├── infra/
├── docs/
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── pyproject.toml
└── README.md
```

**Key Technical Decisions** (from architecture.md):

- Python 3.11.14 runtime
- FastAPI 0.121.1 framework
- Pydantic 2.x for data validation
- AWS Lambda deployment target (via Mangum)

**Module Structure Pattern** (architecture.md lines 197-228):

- Import ordering: Standard library → Third-party → Local (alphabetical)
- Docstrings for all modules, classes, and functions
- Type hints for function parameters and return values

### Configuration Fields

Required environment variables (from architecture.md lines 667-673):

- `riskuity_api_key`: API key for Riskuity authentication
- `riskuity_base_url`: Base URL for Riskuity API (default: `https://api.riskuity.com/v1`)
- `s3_bucket_name`: S3 bucket for document storage
- `aws_region`: AWS region (default: `us-east-1`)
- `log_level`: Logging level (default: `INFO`)

### Testing Standards

- Use pytest for all testing
- Follow Test Organization from architecture.md (lines 369-373):
  - `tests/unit/` - Test single functions/classes in isolation (mock all I/O)
  - `tests/integration/` - Test service integrations with mocked external dependencies
  - `tests/e2e/` - Test full API endpoints with TestClient
- Fixtures in `conftest.py` for shared test data and mocks

### Prerequisites

This is the **first story** in Epic 1 - no prerequisites.

### References

- [Source: docs/architecture.md#Project-Structure] - Complete directory layout
- [Source: docs/architecture.md#Project-Initialization] - FastAPI template CLI setup commands
- [Source: docs/architecture.md#Module-Structure-Pattern] - Import ordering and code organization
- [Source: docs/architecture.md#Decision-Summary] - Technology stack versions
- [Source: docs/PRD.md#Epic-1] - Epic overview and business value

## Dev Agent Record

### Context Reference

- `.bmad-ephemeral/stories/1-1-initialize-fastapi-project-structure.context.xml`

### Agent Model Used

claude-sonnet-4-5-20250929 (Sonnet 4.5)

### Debug Log References

No blocking issues encountered. All tasks completed successfully.

### Completion Notes List

**Implementation Summary:**
- Successfully initialized FastAPI project using fastapi-template-cli with SQLAlchemy ORM
- Installed all required dependencies: FastAPI 0.121.1, docxtpl 0.20.1, boto3 1.40.x, httpx, mangum 0.19.0, pytest 9.0.0
- Removed JWT authentication scaffolding (app/users/, app/core/users.py, app/core/security.py, app/models/users.py)
- Kept SQLAlchemy ORM infrastructure in app/database/ for future v2 job queue metadata
- Created simplified app/config.py with Pydantic Settings for environment-based configuration
- Configured 5 required environment variables: riskuity_api_key, riskuity_base_url, s3_bucket_name, aws_region, log_level
- Created .env.example template file
- Updated app/main.py with Mangum Lambda handler
- Configured CORS middleware for Riskuity origin
- Created project structure: app/services/, app/utils/, app/templates/, app/templates/metadata/
- Initialized Git repository with comprehensive .gitignore
- Verified FastAPI app imports successfully
- Verified pytest test discovery works

**Acceptance Criteria Met:**
- ✅ AC-1: Project structure matches architecture.md (lines 73-157)
- ✅ AC-2: Unused scaffolding removed (JWT auth, SQLAlchemy models removed, ORM kept)
- ✅ AC-3: All dependencies installed with correct versions
- ✅ AC-4: Configuration module implemented with all required fields
- ✅ AC-5: Module structure pattern followed (import ordering, docstrings, type hints)

### File List

**NEW:**
- app/config.py
- app/services/__init__.py
- app/utils/__init__.py
- app/templates/ (directory)
- app/templates/metadata/ (directory)
- .env.example

**MODIFIED:**
- app/main.py (added Mangum handler, updated config import, simplified CORS)
- pyproject.toml (added dependencies, updated Python version requirement)
- .gitignore (already includes .env)

**DELETED:**
- app/users/ (directory and all contents)
- app/models/users.py
- app/core/users.py
- app/core/security.py
