# Lambda Function Troubleshooting Session - February 25, 2026

## Overview

This document captures the complete troubleshooting process for resolving a 502 Bad Gateway error with the CORTAP-RPT Lambda function deployed to AWS GovCloud. The session successfully identified and fixed 7 distinct issues, resulting in a fully functional report generation service.

## Initial Problem

**Reported Issue**: Riskuity developer receiving "502 Bad Gateway - Internal Server Error" when calling the Lambda service endpoint.

**API Endpoint**: `https://qs5wkdxe8l.execute-api.us-gov-west-1.amazonaws.com/dev/api/v1/generate-report-sync`

**Lambda Function**: `cortap-generate-report-sync-dev` (AWS GovCloud us-gov-west-1)

## Issues Discovered and Fixed

### Issue #1: API Gateway Event Format Detection
**File**: `app/handlers/generate_sync_handler.py:52`

**Problem**: Lambda handler only checked for `requestContext.http` field, which exists in HTTP API v2 format but not in REST API Gateway format.

**Error**: Handler treated REST API events as direct invocations, returning 400 "missing_project_id" errors.

**Fix**:
```python
# BEFORE (only HTTP API v2)
if "requestContext" in event and "http" in event.get("requestContext", {}):

# AFTER (supports both REST API and HTTP API v2)
if "httpMethod" in event or ("requestContext" in event and "http" in event.get("requestContext", {})):
```

**Discovery Method**: Created `test_lambda_locally.py` to simulate REST API Gateway events and test handler locally.

---

### Issue #2: Missing Python Dependency
**File**: `requirements.txt:17`

**Problem**: Pydantic requires `email-validator` for email field validation, but it wasn't in requirements.txt.

**Error**:
```
RuntimeError: Unable to import module 'app.handlers.generate_sync_handler':
email-validator is not installed, run `pip install pydantic[email]`
```

**Fix**: Added to requirements.txt:
```python
email-validator==2.1.0  # Required by Pydantic for email validation
```

**Discovery Method**: Direct Lambda invocation via AWS CLI revealed import error.

---

### Issue #3: Incorrect Riskuity API URL
**File**: `template.yaml:45`

**Problem**: Default Riskuity URL was set to `https://app.riskuity.com/v1` (web app URL) instead of `https://api.riskuity.com` (API URL).

**Error**: 404 responses from Riskuity API for valid project requests.

**CloudWatch Log**:
```json
{"url": "https://api.riskuity.com/v1/projects/project_controls/33", "status_code": 404}
```

**Fix**:
```yaml
# BEFORE
RiskuityApiUrl:
  Type: String
  Default: https://app.riskuity.com/v1

# AFTER
RiskuityApiUrl:
  Type: String
  Default: https://api.riskuity.com
```

**Discovery Method**: CloudWatch logs showed URL being called with `/v1` prefix.

---

### Issue #4: Environment Variable Name Mismatch
**Lambda Environment**: `RISKUITY_API_URL`
**Code Expected**: `RISKUITY_BASE_URL`

**Problem**: Pydantic Settings converts field name `riskuity_base_url` to `RISKUITY_BASE_URL` when reading environment variables, but Lambda had `RISKUITY_API_URL`.

**Fix**: Updated Lambda environment variable via AWS CLI:
```bash
aws lambda update-function-configuration \
  --function-name cortap-generate-report-sync-dev \
  --environment "Variables={
    RISKUITY_BASE_URL=https://api.riskuity.com,
    PROJECT_CONFIG_PATH=config/project-setup.json,
    ENVIRONMENT=dev,
    S3_BUCKET_NAME=cortap-documents-dev-736539455039,
    LOG_LEVEL=DEBUG,
    TEMPLATE_DIR=app/templates
  }" \
  --profile govcloud-mfa \
  --region us-gov-west-1
```

**Discovery Method**: Checked Lambda configuration and compared with Pydantic field names in `app/config.py`.

---

### Issue #5: Missing Schema File in Lambda Package
**File**: `docs/schemas/project-data-schema-v1.0.json`

**Problem**: The `build-lambda.sh` script excludes `docs/` directory to reduce package size, but the JSON schema validator needed the schema file.

**Error**:
```
FileNotFoundError: [Errno 2] No such file or directory:
'/var/task/docs/schemas/project-data-schema-v1.0.json'
```

**Solution**:
1. Created `app/schemas/` directory
2. Copied schema file to `app/schemas/project-data-schema-v1.0.json`
3. Updated validator to load from new location

**Files Modified**:
- `app/services/validator.py:92-93`
```python
# BEFORE
schema_path = str(
    Path(__file__).parent.parent.parent / "docs" / "schemas" / "project-data-schema-v1.0.json"
)

# AFTER
schema_path = str(
    Path(__file__).parent.parent / "schemas" / "project-data-schema-v1.0.json"
)
```

**Discovery Method**: CloudWatch logs showed successful generation up to validation, then file not found error.

---

### Issue #6: Parameter Name Mismatch
**File**: `app/api/v1/endpoints/generate.py:470-472`

**Problem**: Code called S3 storage method with `expiration` parameter, but method signature expects `expires_in`.

**Error**:
```
TypeError: S3Storage.generate_presigned_url() got an unexpected keyword argument 'expiration'
```

**Fix**:
```python
# BEFORE
download_url = await s3_storage.generate_presigned_url(
    s3_key=s3_key,
    expiration=86400  # 24 hours
)

# AFTER
download_url = await s3_storage.generate_presigned_url(
    s3_key=s3_key,
    expires_in=86400  # 24 hours
)
```

**Discovery Method**: CloudWatch logs after fixing schema issue.

---

### Issue #7: Incorrect Async/Await Usage
**File**: `app/api/v1/endpoints/generate.py:470`

**Problem**: Used `await` on `generate_presigned_url()` which is a synchronous function (not `async def`).

**Error**:
```
TypeError: object str can't be used in 'await' expression
```

**CloudWatch Log**:
```json
{
  "level": "ERROR",
  "message": "Unexpected error during report generation: object str can't be used in 'await' expression",
  "exception": "File '/var/task/app/api/v1/endpoints/generate.py', line 470, in generate_report_sync\n    download_url = await s3_storage.generate_presigned_url(\nTypeError: object str can't be used in 'await' expression"
}
```

**Fix**:
```python
# BEFORE
download_url = await s3_storage.generate_presigned_url(
    s3_key=s3_key,
    expires_in=86400
)

# AFTER (removed await)
download_url = s3_storage.generate_presigned_url(
    s3_key=s3_key,
    expires_in=86400
)
```

**Interesting Note**: Despite this error, the Lambda was still successfully generating documents and uploading them to S3! The error occurred when trying to construct the API response, so documents were created but the API returned 500 errors.

**Discovery Method**: Searched CloudWatch logs for "Unexpected error" after noticing documents were appearing in S3 despite 500 errors.

---

## AWS GovCloud Authentication Process

### Prerequisites
- AWS CLI installed and configured
- MFA device set up for AWS GovCloud account
- Profile configured in `~/.aws/config` and `~/.aws/credentials`

### Authentication Script
Located at: `scripts/aws-mfa-login.ksh`

### Step-by-Step Authentication

1. **Run the MFA login script**:
```bash
./scripts/aws-mfa-login.ksh
```

2. **When prompted, retrieve MFA code**:
   - Open your MFA app (Google Authenticator, Authy, etc.)
   - Find the code for AWS GovCloud
   - Enter the 6-digit code

3. **Script creates temporary session**:
   - Creates/updates `govcloud-mfa` profile
   - Valid for 12 hours (43200 seconds)
   - Stores temporary credentials in `~/.aws/credentials`

4. **Verify authentication**:
```bash
aws sts get-caller-identity --profile govcloud-mfa --region us-gov-west-1
```

Expected output:
```json
{
    "UserId": "AIDAXXXXXXXXXXXXXXXXX",
    "Account": "736539455039",
    "Arn": "arn:aws-us-gov:iam::736539455039:user/bob.emerick"
}
```

### Common Issues

**Issue**: "Invalid MFA code"
- **Cause**: Code was used before email arrived or expired
- **Solution**: Wait for new code in MFA app, run script again

**Issue**: "The security token included in the request is expired"
- **Cause**: Session expired (after 12 hours)
- **Solution**: Re-run authentication script

---

## Riskuity API Authentication Process

### Prerequisites
- Riskuity account credentials
- Email access for OTP codes
- `.env` file with credentials

### Environment Setup

Create `.env` file:
```bash
RISKUITY_USERNAME=your.email@example.com
RISKUITY_PASSWORD=your_password
```

### Two-Step Authentication Flow

#### Step 1: Initial Authentication Request
```python
import httpx

base_url = "https://api.riskuity.com"
url = f"{base_url}/users/get-auth-token"
payload = {
    "email": "bob.emerick@longevityconsulting.com",
    "password": "your_password"
}

response = await client.post(url, json=payload)
token_data = response.json()
```

**Response**:
```json
{
  "status": "EMAIL_OTP",
  "session": "AYABeG...[session token]...",
  "username": "bob.emerick@longevityconsulting.com_48"
}
```

#### Step 2: OTP Challenge
1. Check email for OTP code (6 digits)
2. Submit OTP with session token:

```python
mfa_url = f"{base_url}/users/respond_to_mfa_challenge"
mfa_payload = {
    "username": token_data["username"],  # Transformed username
    "session": token_data["session"],
    "mfa_code": "123456",  # From email
    "email": "bob.emerick@longevityconsulting.com",
    "challenge_type": "EMAIL_OTP"
}

response = await client.post(mfa_url, json=mfa_payload)
auth_data = response.json()
```

**Success Response**:
```json
{
  "access_token": "eyJra...[JWT token]...",
  "refresh_token": "eyJra...[refresh token]...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

### OTP Timing Issue

**Problem**: If OTP code is provided to script before email arrives, authentication fails.

**Workflow**:
1. Script sends credentials (Step 1) → Triggers OTP email
2. User receives OTP email (takes a few seconds)
3. Script immediately tries to use old/expired OTP (Step 2) → **FAILS**

**Solution**: Run script interactively without `--mfa-code` parameter:
```bash
# WRONG (timing issue)
python3 scripts/test_riskuity_api.py --username user@example.com --mfa-code 123456

# CORRECT (interactive)
python3 scripts/test_riskuity_api.py --username user@example.com
# Script sends request, waits for OTP email
# User checks email, gets fresh code
# User enters code when prompted
```

### Token Caching

The test script caches tokens in `~/.cache/riskuity/tokens.json`:
- Access token valid for 1 hour
- Refresh token for extended sessions
- Automatically reuses valid tokens
- Only prompts for OTP when token expires

---

## Lambda Deployment Process

### Build Script
**Location**: `build-lambda.sh`

**Purpose**:
- Moves large directories (`output/`, `docs/`) to `/tmp` to reduce package size
- Builds Lambda package with SAM CLI
- Restores moved directories
- Final package size: 79MB (well within 250MB limit)

### Build Command
```bash
bash build-lambda.sh
```

**Output**:
```
Moving large directories out of the way...
Cleaning previous build...
Building Lambda package...
Build Succeeded
Restoring directories...
Build complete!
 79M    .aws-sam/build/GenerateReportSyncFunction
```

### Package Size Breakdown
```
19MB - botocore (AWS SDK)
13MB - uvloop (async event loop)
11MB - lxml (XML processing for python-docx)
5.1MB - pydantic_core
5.1MB - app (our code)
2.8MB - yaml
1.7MB - docx
1.6MB - pydantic
... (remaining dependencies)
```

### Deployment Methods

#### Method 1: Direct Lambda Code Update (Fastest)
```bash
cd .aws-sam/build/GenerateReportSyncFunction
zip -r /tmp/cortap-lambda.zip . -q
aws lambda update-function-code \
  --function-name cortap-generate-report-sync-dev \
  --zip-file fileb:///tmp/cortap-lambda.zip \
  --profile govcloud-mfa \
  --region us-gov-west-1
rm -f /tmp/cortap-lambda.zip
```

**Use When**: Code-only changes (no infrastructure updates)

#### Method 2: Full SAM Deployment
```bash
sam deploy \
  --profile govcloud-mfa \
  --region us-gov-west-1 \
  --no-confirm-changeset
```

**Use When**: Infrastructure changes (IAM roles, API Gateway, environment variables, etc.)

### Verify Deployment
```bash
# Check function status
aws lambda get-function \
  --function-name cortap-generate-report-sync-dev \
  --profile govcloud-mfa \
  --region us-gov-west-1 \
  --query 'Configuration.LastUpdateStatus' \
  --output text

# Expected: "Successful"
```

---

## Testing the Lambda Function

### Local Testing (Before Deployment)

#### Test 1: Lambda Handler with Mock Event
**File**: `scripts/test_lambda_locally.py`

```bash
python3 scripts/test_lambda_locally.py
```

**Purpose**: Test event detection logic without deploying

**Mock Event Structure** (REST API):
```python
event = {
    "httpMethod": "POST",
    "path": "/api/v1/generate-report-sync",
    "headers": {
        "Authorization": "Bearer token",
        "Content-Type": "application/json"
    },
    "body": '{"project_id": 33, "report_type": "draft_audit_report"}',
    "requestContext": {
        "accountId": "123456789012",
        "apiId": "test",
        "protocol": "HTTP/1.1",
        "httpMethod": "POST",
        "path": "/dev/api/v1/generate-report-sync",
        "stage": "dev"
    }
}
```

#### Test 2: Riskuity API Integration
**File**: `scripts/test_riskuity_api.py`

```bash
# List available projects
python3 scripts/test_riskuity_api.py \
  --username bob.emerick@longevityconsulting.com \
  --list-projects

# Get project controls
python3 scripts/test_riskuity_api.py \
  --username bob.emerick@longevityconsulting.com \
  --project-id 33
```

---

### Remote Testing (AWS Lambda)

#### Test 1: Direct Lambda Invocation
```bash
# Create test event
cat > /tmp/test-event.json << 'EOF'
{
  "httpMethod": "POST",
  "path": "/api/v1/generate-report-sync",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer test-token"
  },
  "body": "{\"project_id\": 33, \"report_type\": \"draft_audit_report\"}"
}
EOF

# Invoke Lambda
aws lambda invoke \
  --function-name cortap-generate-report-sync-dev \
  --payload file:///tmp/test-event.json \
  --profile govcloud-mfa \
  --region us-gov-west-1 \
  /tmp/lambda-response.json

# View response
cat /tmp/lambda-response.json | jq
```

#### Test 2: End-to-End API Test
**File**: `scripts/test_sync_generation.py`

```bash
# Basic test
python3 scripts/test_sync_generation.py \
  --project-id 33 \
  --base-url https://qs5wkdxe8l.execute-api.us-gov-west-1.amazonaws.com/dev

# Test with download
python3 scripts/test_sync_generation.py \
  --project-id 33 \
  --base-url https://qs5wkdxe8l.execute-api.us-gov-west-1.amazonaws.com/dev \
  --download \
  --output output/test_generation
```

**Test Flow**:
1. Authenticates with Riskuity (uses cached token if valid)
2. Calls Lambda API endpoint
3. Waits for generation (30-60 seconds)
4. Validates response
5. Optionally downloads generated document

**Successful Output**:
```
================================================================================
Testing Synchronous Report Generation
================================================================================
Project ID: 33
Report Type: draft_audit_report
Endpoint: https://qs5wkdxe8l.execute-api.us-gov-west-1.amazonaws.com/dev/api/v1/generate-report-sync
================================================================================

⏳ Starting generation (this will take 30-60 seconds)...
   Please wait...

⏱️  Request completed in 13.4 seconds

✅ Generation Successful!

────────────────────────────────────────────────────────────────────────────────
Report Details:
────────────────────────────────────────────────────────────────────────────────
  Report ID:       rpt-20260225-154609-9875de7b
  Project ID:      33
  Report Type:     draft_audit_report
  Status:          completed
  Generated At:    2026-02-25T15:46:19.528303Z
  Expires At:      2026-02-26T15:46:19.528303Z
  File Size:       61,114 bytes (59.7 KB)
  Correlation ID:  gen-sync-f2db91b9ff25

────────────────────────────────────────────────────────────────────────────────
Metadata:
────────────────────────────────────────────────────────────────────────────────
  Recipient:       Seattle
  Review Type:     Triennial Review
  Review Areas:    21
  Deficiencies:    1
  Generation Time: 9,960 ms (10.0s)

────────────────────────────────────────────────────────────────────────────────
Performance Breakdown:
────────────────────────────────────────────────────────────────────────────────
  Total Request:   13.4s (100%)
  Backend Work:    10.0s (74%)
  Network/Overhead: 3.5s (26%)
```

---

## CloudWatch Logs Analysis

### Accessing Logs
```bash
# Tail logs in real-time
aws logs tail /aws/lambda/cortap-generate-report-sync-dev \
  --profile govcloud-mfa \
  --region us-gov-west-1 \
  --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/cortap-generate-report-sync-dev \
  --filter-pattern "ERROR" \
  --profile govcloud-mfa \
  --region us-gov-west-1 \
  --start-time 1772033635713 \
  --max-items 10
```

### Key Log Patterns

#### Successful Generation Flow
```json
{"level": "INFO", "message": "Starting synchronous report generation", "correlation_id": "gen-sync-xxx"}
{"level": "INFO", "message": "Fetching project controls from Riskuity", "project_id": 33}
{"level": "INFO", "message": "Successfully fetched 494 of 494 project controls"}
{"level": "INFO", "message": "Transforming data to canonical JSON"}
{"level": "INFO", "message": "Completeness check complete", "quality_score": 86, "can_generate": true}
{"level": "INFO", "message": "Generating document from template"}
{"level": "INFO", "message": "Document uploaded to S3"}
{"level": "INFO", "message": "Pre-signed URL generated"}
{"level": "INFO", "message": "Report generation completed successfully"}
```

#### Error Indicators
```json
{"level": "ERROR", "message": "Unexpected error during report generation"}
{"level": "ERROR", "message": "Failed to generate presigned URL"}
{"level": "ERROR", "message": "Riskuity API error"}
```

### Using Correlation IDs

Each request has a unique correlation ID: `gen-sync-xxxxxxxxxx`

**Search by correlation ID**:
```bash
aws logs filter-log-events \
  --log-group-name /aws/lambda/cortap-generate-report-sync-dev \
  --filter-pattern "gen-sync-f2db91b9ff25" \
  --profile govcloud-mfa \
  --region us-gov-west-1
```

---

## Verifying S3 Documents

### List Generated Documents
```bash
aws s3 ls s3://cortap-documents-dev-736539455039/documents/33/ \
  --profile govcloud-mfa \
  --region us-gov-west-1 \
  --recursive
```

**Output**:
```
2026-02-25 10:46:20      61114 documents/33/rpt-20260225-154609-9875de7b_draft_audit_report.docx
```

### Download and Verify Document
```bash
# Download
aws s3 cp \
  s3://cortap-documents-dev-736539455039/documents/33/rpt-20260225-154609-9875de7b_draft_audit_report.docx \
  /tmp/test-report.docx \
  --profile govcloud-mfa \
  --region us-gov-west-1

# Verify file type
file /tmp/test-report.docx
# Output: /tmp/test-report.docx: Microsoft OOXML

# Check file size
ls -lh /tmp/test-report.docx
# Output: -rw-r--r--  1 user  staff    60K Feb 25 10:46 /tmp/test-report.docx
```

### Open Document (macOS)
```bash
open /tmp/test-report.docx
```

---

## Troubleshooting Checklist

### Pre-Deployment Checks
- [ ] `.env` file contains valid Riskuity credentials
- [ ] AWS GovCloud authentication is current (within 12 hours)
- [ ] `build-lambda.sh` runs successfully
- [ ] Schema file exists at `app/schemas/project-data-schema-v1.0.json`
- [ ] All dependencies in `requirements.txt` are valid

### Post-Deployment Checks
- [ ] Lambda function status is "Successful"
- [ ] Environment variables are set correctly
- [ ] CloudWatch log group exists and is accessible
- [ ] S3 bucket exists and Lambda has write permissions
- [ ] API Gateway endpoint is accessible

### Testing Checklist
- [ ] Can authenticate with Riskuity API
- [ ] Can fetch project controls from Riskuity
- [ ] Lambda responds to test invocation
- [ ] API endpoint returns 200 status
- [ ] Documents appear in S3 bucket
- [ ] Download URLs work and documents are valid
- [ ] CloudWatch logs show no errors

---

## Common Error Patterns

### 502 Bad Gateway
**Causes**:
- Lambda handler cannot detect event format
- Lambda import failure
- Runtime exception before response

**Investigation**:
1. Check CloudWatch logs for import errors
2. Test handler locally with mock events
3. Verify all dependencies are installed

### 500 Internal Server Error
**Causes**:
- Uncaught exception in handler code
- Invalid response format
- Timeout (but document still generated)

**Investigation**:
1. Search CloudWatch for "ERROR" logs
2. Check correlation ID for request flow
3. Verify S3 to see if document was created despite error

### 404 Not Found
**Causes**:
- Wrong Riskuity API URL
- Invalid project ID
- Missing API endpoint

**Investigation**:
1. Check CloudWatch for URL being called
2. Verify Riskuity base URL configuration
3. Test Riskuity API directly

### TimeoutError
**Causes**:
- Document generation takes too long
- Network issues with Riskuity API
- S3 upload delays

**Current Timeout**: 120 seconds (2 minutes)

**Solution**: Increase timeout in `template.yaml`:
```yaml
Globals:
  Function:
    Timeout: 180  # 3 minutes
```

---

## Performance Metrics

### Typical Generation Times
- **Riskuity API fetch**: 9 seconds (494 controls)
- **Data transformation**: <1 second
- **Document generation**: ~1 second
- **S3 upload**: <1 second
- **Total backend**: ~10 seconds
- **Total request**: 13-15 seconds (with network overhead)

### Lambda Resources
- **Memory**: 2048 MB
- **Timeout**: 120 seconds
- **Package Size**: 79 MB (unzipped)
- **Runtime**: Python 3.11
- **Architecture**: x86_64

### Document Sizes
- **Draft Audit Report**: ~60 KB (61,114 bytes)
- **Varies by**: Number of review areas, deficiencies, attachments

---

## Success Criteria

### ✅ All Systems Operational
- Lambda returns 200 status code
- Response contains valid download URL
- Document exists in S3
- Document is valid Microsoft Word format
- Generation time < 30 seconds
- No errors in CloudWatch logs (warnings OK)
- Presigned URL is accessible
- Download URL expires in 24 hours

---

## Next Steps for Riskuity Team

1. **Integration**: Update Riskuity application to call Lambda endpoint
2. **Error Handling**: Implement retry logic for transient failures
3. **Monitoring**: Set up alerts for Lambda errors and slow requests
4. **Testing**: Test with various project IDs and report types
5. **Documentation**: Update internal docs with API endpoint details

---

## Files Modified During Session

### Application Code
1. `app/handlers/generate_sync_handler.py` - Event detection fix
2. `app/api/v1/endpoints/generate.py` - Parameter fixes, async/await fix
3. `app/services/validator.py` - Schema path update
4. `requirements.txt` - Added email-validator

### Infrastructure
5. `template.yaml` - Riskuity URL fix
6. Lambda environment variables - Name and value fixes

### Build System
7. `build-lambda.sh` - Simplified (schema now in app/)

### New Files
8. `app/schemas/project-data-schema-v1.0.json` - Moved from docs/

### Test Scripts
9. `scripts/test_sync_generation.py` - Auth URL fix
10. `scripts/test_riskuity_api.py` - Debug logging added

---

## Key Learnings

1. **API Gateway has multiple event formats** - Always check for both REST API and HTTP API v2 patterns
2. **Pydantic dependencies are not always explicit** - email-validator required but not auto-installed
3. **Environment variable naming matters** - Pydantic converts snake_case to UPPER_CASE
4. **Build scripts can exclude needed files** - Schema files should be in app/ directory
5. **Async/await errors can be subtle** - Document generation succeeded but response failed
6. **CloudWatch logs are essential** - Correlation IDs make debugging much easier
7. **OTP timing is critical** - Interactive authentication prevents timing issues

---

## Contact Information

**Project**: CORTAP-RPT Report Generation Service
**AWS Account**: 736539455039 (GovCloud)
**Region**: us-gov-west-1
**Environment**: dev

**API Endpoint**: `https://qs5wkdxe8l.execute-api.us-gov-west-1.amazonaws.com/dev`

**S3 Bucket**: `cortap-documents-dev-736539455039`

**Lambda Function**: `cortap-generate-report-sync-dev`

**CloudWatch Log Group**: `/aws/lambda/cortap-generate-report-sync-dev`

---

## Document Version

**Date**: February 25, 2026
**Session Duration**: ~4 hours
**Final Status**: ✅ All issues resolved, service fully operational
**Test Result**: 200 OK, 13.4s generation time, valid document delivered
