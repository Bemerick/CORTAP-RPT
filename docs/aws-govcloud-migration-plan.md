# AWS GovCloud Migration & API Strategy

**Project:** CORTAP-RPT Final Report Generation Service
**Target:** AWS GovCloud Lambda with API Gateway
**Priority:** Final Report (Draft Audit Report) Generation
**Date:** 2025-02-09
**Status:** Planning Phase

---

## Executive Summary

This document outlines the strategy to migrate CORTAP-RPT from a local FastAPI service to AWS GovCloud Lambda, enabling it to be called as an external API service by other applications. The focus is on **Final Report generation** (Draft Audit Report template with 9 conditional logic patterns).

**Key Objectives:**
1. Deploy CORTAP-RPT as a serverless Lambda function in AWS GovCloud
2. Expose API endpoints via API Gateway for external consumption
3. Integrate with Riskuity API to fetch real project data
4. Store generated documents in S3 GovCloud with secure access
5. Enable external applications to trigger report generation

---

## Current State Assessment

### What's Working ✅
- **Draft Report POC Complete** (Epic 1.5)
  - Template: `draft-report-working.docx`
  - All 9 conditional logic patterns implemented and tested
  - 5 mock JSON scenarios validated
  - Document generation working locally

- **RIR Production System** (Epic 4)
  - RIR template conversion complete
  - Excel-based generation workflow (36 FY2026 documents)
  - API endpoints operational with mock data

- **Core Infrastructure** (Epic 1)
  - FastAPI application structure
  - Structured JSON logging
  - Custom exception hierarchy
  - Document generator service
  - Lambda handler ready (Mangum configured)

### What's Needed 🔨
- **AWS Deployment** (Epic 7 - partial)
  - AWS SAM template for GovCloud
  - Lambda packaging and deployment
  - IAM roles and permissions

- **S3 Integration** (Epic 5)
  - S3 storage service implementation
  - Pre-signed URL generation
  - Document upload/download

- **Riskuity Integration** (Epic 3.5)
  - Riskuity API client with retry logic
  - Data transformer (Riskuity → JSON schema)
  - Data caching in S3
  - POST `/api/v1/projects/{id}/data` endpoint

- **API Hardening** (Epic 6 - partial)
  - API authentication (API keys)
  - Request/response validation
  - External API documentation
  - CORS configuration

---

## Target Architecture

### High-Level Architecture

```
┌─────────────────────┐
│  External App       │
│  (Riskuity UI, etc) │
└──────────┬──────────┘
           │ HTTPS + API Key
           ↓
┌──────────────────────────────────┐
│  API Gateway (AWS GovCloud)      │
│  - API Key Validation            │
│  - Rate Limiting                 │
│  - CORS Headers                  │
└──────────┬───────────────────────┘
           │
           ↓
┌──────────────────────────────────┐
│  Lambda Function                 │
│  - FastAPI + Mangum              │
│  - Document Generator            │
│  - Riskuity Client               │
│  - S3 Storage Service            │
└──────┬─────────────┬─────────────┘
       │             │
       │             ↓
       │   ┌─────────────────────┐
       │   │  S3 Bucket          │
       │   │  - Documents (.docx)│
       │   │  - JSON Data Cache  │
       │   │  - Encryption at rest│
       │   └─────────────────────┘
       │
       ↓
┌─────────────────────┐
│  Riskuity API       │
│  - Project Data     │
│  - Assessments      │
│  - Surveys, Risks   │
└─────────────────────┘
```

### API Endpoints for External Consumption

#### 1. POST `/api/v1/projects/{project_id}/data`
**Purpose:** Fetch and cache project data from Riskuity

**Request:**
```json
{
  "force_refresh": false,
  "include_assessments": true,
  "include_erf": true,
  "include_surveys": false
}
```

**Response:**
```json
{
  "project_id": "RSKTY-12345",
  "data_file_id": "RSKTY-12345_2025-02-09",
  "data_quality_score": 95,
  "missing_critical_fields": [],
  "missing_optional_fields": ["contractor_phone"],
  "ready_for_generation": true,
  "warnings": []
}
```

#### 2. POST `/api/v1/generate-document`
**Purpose:** Generate Final Report (or other templates)

**Request:**
```json
{
  "project_id": "RSKTY-12345",
  "template_id": "draft-audit-report",
  "user_id": "auditor@fta.gov",
  "format": "docx"
}
```

**Response:**
```json
{
  "status": "success",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "download_url": "https://cortap-docs-govcloud.s3.amazonaws.com/...",
  "filename": "MBTA_Draft_Audit_Report_2025-02-09.docx",
  "expires_at": "2025-02-10T10:30:00Z",
  "generated_at": "2025-02-09T10:30:00Z",
  "warnings": []
}
```

#### 3. GET `/api/v1/templates`
**Purpose:** List available templates

**Response:**
```json
{
  "templates": [
    {
      "id": "draft-audit-report",
      "name": "Draft Audit Report (FY25)",
      "description": "CORTAP Triennial/State Management Review Draft Report",
      "required_fields": ["recipient_name", "recipient_acronym", "review_type"]
    },
    {
      "id": "rir-package",
      "name": "Recipient Information Request Package",
      "description": "RIR package for CORTAP reviews"
    }
  ]
}
```

#### 4. GET `/api/v1/documents/{document_id}/url`
**Purpose:** Refresh expired download URL

**Response:**
```json
{
  "download_url": "https://cortap-docs-govcloud.s3.amazonaws.com/...",
  "expires_at": "2025-02-10T10:30:00Z"
}
```

### Authentication Strategy

**API Key-Based Authentication:**
- API Gateway validates `x-api-key` header
- Each external application receives unique API key
- Keys stored in AWS Secrets Manager
- Rate limiting per API key (100 req/min)

**Future Multi-Tenant Enhancement:**
- Lambda authorizer for advanced tenant isolation
- DynamoDB tenant configuration table
- Tenant-specific S3 prefixes
- (Defer to v2 if not immediately needed)

---

## Implementation Roadmap

### Phase 1: AWS Infrastructure Setup (Week 1)
**Epic 7 (Partial) + Epic 5**

**Goals:**
- Deploy Lambda to GovCloud
- Configure S3 storage
- Set up API Gateway

**Tasks:**
1. **Create AWS SAM Template** (`infra/template.yaml`)
   - Lambda function definition
   - API Gateway HTTP API
   - S3 bucket with encryption
   - IAM roles and policies
   - CloudWatch Logs

2. **Implement S3 Storage Service** (Story 5.1)
   - `app/services/s3_storage.py`
   - Upload documents to S3
   - Generate pre-signed URLs (24hr expiration)
   - Handle encryption at rest

3. **Lambda Packaging**
   - Create `requirements.txt` for Lambda layer
   - Include python-docxtpl + dependencies
   - Optimize package size (<50MB unzipped)

4. **Deploy to GovCloud**
   - `sam build`
   - `sam deploy --guided` (GovCloud region)
   - Test Lambda invocation
   - Validate S3 access

**Deliverables:**
- ✅ Lambda function deployed in GovCloud
- ✅ S3 bucket configured with encryption
- ✅ API Gateway endpoint accessible
- ✅ S3 storage service working

**IAM Permissions Required:**
```yaml
LambdaExecutionRole:
  Policies:
    - S3FullAccess (scoped to cortap-* buckets)
    - CloudWatchLogsWriteAccess
    - SecretsManagerReadAccess (for Riskuity API keys)
```

---

### Phase 2: Riskuity Data Service (Week 2)
**Epic 3.5**

**Goals:**
- Integrate with Riskuity API
- Transform data to canonical JSON
- Cache in S3

**Tasks:**
1. **Implement Riskuity API Client** (Story 3.5.2)
   - `app/services/riskuity_client.py`
   - Fetch from 4 endpoints:
     - GET `/v1/projects/{project_id}`
     - GET `/v1/projects/{project_id}/assessments`
     - GET `/v1/projects/{project_id}/surveys`
     - GET `/v1/projects/{project_id}/risks`
   - Retry logic with exponential backoff (3 retries)
   - Timeout handling (10s per request)

2. **Implement Data Transformer** (Story 3.5.3)
   - `app/services/data_transformer.py`
   - Transform Riskuity API → Canonical JSON schema
   - Calculate derived fields:
     - `has_deficiencies = any(assessment.finding == "D")`
     - `deficiency_count`, `erf_count`
     - `deficiency_areas` list

3. **S3 Data Caching** (Story 3.5.4)
   - Store JSON files: `{bucket}/data/{project_id}_project-data.json`
   - TTL: 1 hour (configurable)
   - Check cache before API call

4. **Data Validation Service** (Story 3.5.6)
   - Validate completeness against template requirements
   - Check required vs optional fields
   - Return data quality score

5. **API Endpoint** (Story 3.5.7)
   - POST `/api/v1/projects/{project_id}/data`
   - Orchestrate: fetch → transform → cache → validate
   - Return data quality report

**Deliverables:**
- ✅ Riskuity API client with error handling
- ✅ Data transformer (Riskuity → JSON)
- ✅ JSON data caching in S3
- ✅ POST `/data` endpoint working

**Riskuity API Configuration:**
```python
# app/config.py
class Settings(BaseSettings):
    riskuity_api_key: str  # From Secrets Manager
    riskuity_base_url: str = "https://api.riskuity.com/v1"
    riskuity_timeout: int = 10
    riskuity_max_retries: int = 3
```

---

### Phase 3: Final Report API Integration (Week 3)
**Epic 2 (Conditional Logic) + Epic 6 (API)**

**Goals:**
- Integrate Draft Report template with live data
- Expose generation API
- End-to-end testing

**Tasks:**
1. **Finalize Conditional Logic** (Epic 2 - if needed)
   - Review Epic 1.5 POC implementation
   - Ensure all 9 patterns work with Riskuity data
   - Test with real API data structure

2. **API Request/Response Models** (Story 6.1)
   - Pydantic models for all endpoints
   - Field validation
   - Error response schemas

3. **Generate Document Endpoint** (Story 6.2)
   - POST `/api/v1/generate-document`
   - Load cached JSON from S3
   - Generate document (python-docxtpl)
   - Upload to S3
   - Return pre-signed URL

4. **CORS Configuration** (Story 6.5)
   - Allow external applications
   - Configure allowed origins in API Gateway

5. **End-to-End Testing**
   - Test full flow: Riskuity → JSON → Document → S3
   - Validate 5 different project scenarios
   - Performance testing (30-60s target)

**Deliverables:**
- ✅ POST `/generate-document` working with Riskuity data
- ✅ All API endpoints documented (OpenAPI/Swagger)
- ✅ E2E tests passing
- ✅ External API ready for consumption

---

### Phase 4: External API Documentation & Handoff (Week 4)
**Documentation + Testing**

**Goals:**
- Document API for external developers
- Provide integration examples
- Load testing and performance validation

**Tasks:**
1. **API Documentation**
   - OpenAPI 3.0 specification
   - Authentication guide
   - Request/response examples
   - Error codes and handling

2. **Integration Guide**
   - Quick start guide
   - Code examples (JavaScript, Python)
   - Common use cases
   - Troubleshooting

3. **Performance & Load Testing**
   - Test concurrent requests (20 users)
   - Measure document generation time
   - Validate S3 pre-signed URL expiration
   - Monitor CloudWatch metrics

4. **Security Review**
   - API key rotation process
   - Data encryption validation (at rest and in transit)
   - Compliance check (FedRAMP, FISMA if applicable)

**Deliverables:**
- ✅ API documentation published
- ✅ Integration examples
- ✅ Load test results
- ✅ Security review complete

---

## AWS SAM Template Structure

### `/infra/template.yaml`

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: CORTAP-RPT Final Report Generation Service

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues: [dev, staging, prod]

  RiskuityAPIKeySecretArn:
    Type: String
    Description: ARN of Secrets Manager secret containing Riskuity API key

Globals:
  Function:
    Timeout: 120
    MemorySize: 1024
    Runtime: python3.11
    Environment:
      Variables:
        ENVIRONMENT: !Ref Environment
        S3_BUCKET_NAME: !Ref DocumentBucket
        RISKUITY_API_KEY_SECRET: !Ref RiskuityAPIKeySecretArn

Resources:
  # Lambda Function
  CORTAPFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub cortap-rpt-${Environment}
      CodeUri: ../
      Handler: app.main.handler
      Layers:
        - !Ref PythonDependenciesLayer
      Policies:
        - S3CrudPolicy:
            BucketName: !Ref DocumentBucket
        - Statement:
            Effect: Allow
            Action:
              - secretsmanager:GetSecretValue
            Resource: !Ref RiskuityAPIKeySecretArn
      Events:
        ApiEvent:
          Type: HttpApi
          Properties:
            ApiId: !Ref CORTAPApi
            Path: /{proxy+}
            Method: ANY

  # Lambda Layer for Dependencies
  PythonDependenciesLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: cortap-dependencies
      ContentUri: ../lambda/layer/
      CompatibleRuntimes:
        - python3.11

  # API Gateway HTTP API
  CORTAPApi:
    Type: AWS::Serverless::HttpApi
    Properties:
      StageName: !Ref Environment
      CorsConfiguration:
        AllowOrigins:
          - https://riskuity.com
          - https://*.riskuity.com
        AllowMethods:
          - GET
          - POST
        AllowHeaders:
          - x-api-key
          - content-type
      Auth:
        ApiKeyRequired: true

  # S3 Bucket for Documents
  DocumentBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub cortap-documents-${Environment}
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      LifecycleConfiguration:
        Rules:
          - Id: DeleteOldDocuments
            Status: Enabled
            ExpirationInDays: 90
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

  # CloudWatch Log Group
  CORTAPLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub /aws/lambda/cortap-rpt-${Environment}
      RetentionInDays: 90

Outputs:
  ApiEndpoint:
    Description: API Gateway endpoint URL
    Value: !Sub https://${CORTAPApi}.execute-api.${AWS::Region}.amazonaws.com/${Environment}

  S3BucketName:
    Description: S3 bucket for documents
    Value: !Ref DocumentBucket

  LambdaFunctionArn:
    Description: Lambda function ARN
    Value: !GetAtt CORTAPFunction.Arn
```

---

## Epic Story Mapping

### Phase 1: AWS Infrastructure
- ✅ **Story 5.1:** Implement S3Storage service
- ✅ **Story 5.2:** Integrate S3 upload into document generation
- ✅ **Story 7.4:** Create AWS SAM infrastructure template
- ✅ **Story 7.5:** Create Lambda deployment package
- ✅ **Story 7.6:** Deploy to AWS GovCloud and validate

### Phase 2: Riskuity Integration
- ✅ **Story 3.5.2:** Implement Riskuity API client with retry logic
- ✅ **Story 3.5.3:** Implement data transformer (Riskuity → JSON)
- ✅ **Story 3.5.4:** Implement S3 storage for JSON data files
- ✅ **Story 3.5.5:** Implement caching and TTL logic
- ✅ **Story 3.5.6:** Implement data validation and completeness checks
- ✅ **Story 3.5.7:** Implement POST `/api/v1/projects/{id}/data` endpoint

### Phase 3: API Integration
- ✅ **Story 6.1:** Implement Pydantic request/response models
- ✅ **Story 6.2:** Implement POST `/api/v1/generate-document` endpoint
- ✅ **Story 6.3:** Implement GET `/api/v1/templates` endpoint
- ✅ **Story 6.4:** Implement GET `/api/v1/validate-data` endpoint
- ✅ **Story 6.5:** Configure CORS and Lambda handler

### Phase 4: Testing & Documentation
- ✅ **Story 7.1:** Implement unit tests for all services
- ✅ **Story 7.2:** Implement integration tests
- ✅ **Story 7.3:** Implement E2E API tests
- 📝 **Ad-hoc:** Create external API documentation

---

## Configuration & Environment Variables

### Local Development (`.env`)
```bash
ENVIRONMENT=dev
PROJECT_NAME=CORTAP-RPT
LOG_LEVEL=INFO

# Riskuity API
RISKUITY_API_KEY=your-dev-api-key
RISKUITY_BASE_URL=https://api.riskuity.com/v1
RISKUITY_TIMEOUT=10
RISKUITY_MAX_RETRIES=3

# AWS (for local SAM testing)
AWS_REGION=us-gov-west-1
S3_BUCKET_NAME=cortap-documents-dev

# CORS
CORS_ORIGINS=http://localhost:3000,https://dev.riskuity.com
```

### AWS GovCloud (Secrets Manager + Lambda Environment)
```yaml
# Stored in AWS Secrets Manager
riskuity_api_key: "prod-api-key-from-riskuity"

# Lambda Environment Variables (via SAM template)
ENVIRONMENT: prod
S3_BUCKET_NAME: cortap-documents-prod
AWS_REGION: us-gov-west-1
RISKUITY_BASE_URL: https://api.riskuity.com/v1
RISKUITY_TIMEOUT: 10
RISKUITY_MAX_RETRIES: 3
```

---

## IAM Roles & Permissions

### Lambda Execution Role

**Required Permissions:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws-us-gov:s3:::cortap-documents-*",
        "arn:aws-us-gov:s3:::cortap-documents-*/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws-us-gov:logs:*:*:log-group:/aws/lambda/cortap-rpt-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws-us-gov:secretsmanager:*:*:secret:riskuity-api-key-*"
    }
  ]
}
```

### API Gateway Execution Role
- Invoke Lambda function
- CloudWatch logging

---

## Testing Strategy

### Unit Tests
- S3Storage service (mocked boto3)
- RiskuityClient (mocked httpx)
- DataTransformer (sample API responses)
- ConditionalLogic patterns

### Integration Tests
- S3 upload/download (real S3 bucket in dev)
- Riskuity API calls (dev API key)
- Document generation (real templates)

### End-to-End Tests
- API Gateway → Lambda → S3 full flow
- External API consumption simulation
- Performance benchmarks (30-60s target)

### Load Testing
- 20 concurrent users
- 100 documents/hour sustained
- API Gateway rate limiting validation

---

## Success Criteria

### Technical Success
- ✅ Lambda function deploys successfully to GovCloud
- ✅ API Gateway accessible with API key authentication
- ✅ S3 storage working with pre-signed URLs
- ✅ Riskuity API integration complete
- ✅ Document generation time: 30-60 seconds
- ✅ All 9 conditional logic patterns working with real data
- ✅ 100% of test scenarios passing

### Business Success
- ✅ External applications can call API successfully
- ✅ Final Reports generated match manual template formatting
- ✅ Auditors can download generated documents
- ✅ Data sourced from Riskuity (no manual JSON files)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Lambda cold start latency (2-5s) | User experience | Reserve concurrency + keep warm |
| Riskuity API downtime | Service unavailable | Retry logic, cache data in S3 |
| S3 pre-signed URL expiration | Download failures | Implement URL refresh endpoint |
| IAM permission issues in GovCloud | Deployment blocked | Test permissions in dev first |
| Document generation timeout (>120s) | Lambda timeout | Optimize template rendering, increase timeout to 180s if needed |
| Large document size (>50MB) | Lambda ephemeral storage limit | Use S3 streaming, multipart upload |

---

## Next Immediate Actions

1. **Create AWS SAM template** (`infra/template.yaml`) - Phase 1
2. **Implement S3Storage service** (`app/services/s3_storage.py`) - Epic 5.1
3. **Deploy to GovCloud dev environment** - Test Lambda + S3
4. **Implement Riskuity API client** - Epic 3.5.2
5. **Test end-to-end with 1 real project** - Validate integration

**Estimated Timeline:** 4 weeks to production-ready external API

---

**Document Owner:** Bob Emerick
**Last Updated:** 2025-02-09
**Status:** Ready for Implementation
