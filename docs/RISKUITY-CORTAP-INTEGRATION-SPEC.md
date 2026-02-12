# Riskuity ↔ CORTAP-RPT Integration Specification

**Version:** 1.0
**Date:** 2026-02-11
**Status:** Design Review

---

## Overview

This document specifies the integration between Riskuity (source system) and CORTAP-RPT (report generation service) for automated FTA compliance report generation.

### Integration Pattern

**Async Request-Response with Webhook Callback**
- Riskuity triggers report generation via REST API
- CORTAP-RPT responds immediately with job ID
- CORTAP-RPT generates report in background
- CORTAP-RPT notifies Riskuity via webhook when complete
- User downloads report directly from S3 using presigned URL

---

## Architecture Diagram

```
┌─────────────┐                 ┌──────────────┐                ┌─────────┐
│  Riskuity   │                 │  CORTAP-RPT  │                │   S3    │
│   WebApp    │                 │   Service    │                │ Storage │
└──────┬──────┘                 └──────┬───────┘                └────┬────┘
       │                               │                             │
       │ 1. User clicks "Generate"     │                             │
       ├──────────────────────────────>│                             │
       │ POST /api/v1/generate-report  │                             │
       │ Authorization: Bearer <token> │                             │
       │                               │                             │
       │<──────────────────────────────┤                             │
       │ 2. Immediate Response         │                             │
       │ { "job_id": "...",            │                             │
       │   "status": "processing" }    │                             │
       │                               │                             │
       │                               │ 3. Fetch data (user token)  │
       │                               │ 4. Transform to JSON        │
       │                               │ 5. Generate Word doc        │
       │                               │                             │
       │                               ├────────────────────────────>│
       │                               │ 6. Upload DOCX to S3        │
       │                               │<────────────────────────────┤
       │                               │ 7. Get presigned URL        │
       │                               │    (7-day expiry)           │
       │                               │                             │
       │<──────────────────────────────┤                             │
       │ 8. Webhook Callback           │                             │
       │ POST /webhooks/report-complete│                             │
       │ { "download_url": "...",      │                             │
       │   "expires_at": "..." }       │                             │
       │                               │                             │
       │ 9. User clicks "Download"     │                             │
       ├───────────────────────────────┼────────────────────────────>│
       │ GET presigned URL             │                             │
       │<────────────────────────────────────────────────────────────┤
       │ File downloaded               │                             │
```

---

## Authentication Flow

### User Token Pass-Through (Selected Approach)

**Rationale:**
- ✅ User permissions automatically enforced
- ✅ Audit trail shows which user generated each report
- ✅ No need for service account with elevated permissions
- ✅ Token already validated by Riskuity

**Flow:**
1. User authenticates with Riskuity (JWT token issued)
2. User clicks "Generate Report" button
3. Riskuity passes user's JWT token to CORTAP-RPT
4. CORTAP-RPT reuses token for Riskuity API calls
5. User permissions automatically scoped

**Token Properties:**
- **Type:** JWT (Riskuity-issued)
- **Validity:** ~1 hour (typical)
- **Scope:** User's project access permissions
- **Header:** `Authorization: Bearer <token>`

---

## API Specifications

### 1. Generate Report Endpoint (Riskuity → CORTAP-RPT)

**Endpoint:** `POST /api/v1/generate-report`

**Request:**
```http
POST /api/v1/generate-report HTTP/1.1
Host: cortap-rpt.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "project_id": 33,
  "report_type": "draft_audit_report",
  "callback_url": "https://api.riskuity.com/webhooks/report-completed",
  "options": {
    "include_attachments": true,
    "format": "docx"
  }
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `project_id` | integer | Yes | Riskuity project identifier |
| `report_type` | string | Yes | Report template identifier (see Report Types below) |
| `callback_url` | string | Yes | Webhook URL for completion notification |
| `options.include_attachments` | boolean | No | Whether to include evidence attachments (default: false) |
| `options.format` | string | No | Output format: "docx" or "pdf" (default: "docx") |

**Report Types:**
- `draft_audit_report` - Draft Triennial/SMR Report
- `recipient_information_request` - RIR Cover Letter

**Response (Success - 202 Accepted):**
```json
{
  "job_id": "rpt-20260211-160045-a1b2c3d4",
  "status": "processing",
  "estimated_completion": "2026-02-11T16:05:00Z",
  "status_url": "https://cortap-rpt.example.com/api/v1/jobs/rpt-20260211-160045-a1b2c3d4"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `job_id` | string | Unique job identifier for tracking |
| `status` | string | Current status: "processing", "queued" |
| `estimated_completion` | string | ISO 8601 timestamp (estimate) |
| `status_url` | string | URL to poll job status (optional) |

**Error Responses:**

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| 401 | `INVALID_TOKEN` | Missing or invalid Authorization header |
| 403 | `INSUFFICIENT_PERMISSIONS` | User lacks access to project |
| 404 | `PROJECT_NOT_FOUND` | Project ID does not exist |
| 422 | `INVALID_REPORT_TYPE` | Unknown report_type value |
| 500 | `INTERNAL_ERROR` | Server error during job creation |

**Example Error Response:**
```json
{
  "error": "INSUFFICIENT_PERMISSIONS",
  "message": "User does not have access to project 33",
  "details": {
    "user_id": 48,
    "project_id": 33,
    "required_permission": "project.view"
  }
}
```

---

### 2. Webhook Callback Endpoint (CORTAP-RPT → Riskuity)

**Endpoint:** `POST <callback_url>` (provided by Riskuity)

**Implementation Required By:** Riskuity

**Request (Success):**
```http
POST /webhooks/report-completed HTTP/1.1
Host: api.riskuity.com
Content-Type: application/json
X-CORTAP-Signature: sha256=5d7e8c9f...
X-CORTAP-Timestamp: 1707672045

{
  "job_id": "rpt-20260211-160045-a1b2c3d4",
  "status": "completed",
  "project_id": 33,
  "report_type": "draft_audit_report",
  "download_url": "https://cortap-documents-prod.s3.us-gov-west-1.amazonaws.com/reports/project-33/draft_audit_report_20260211.docx?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=...",
  "expires_at": "2026-02-18T16:00:00Z",
  "file_size": 156789,
  "file_name": "CORTAP_Draft_Report_Project33_20260211.docx",
  "metadata": {
    "generated_at": "2026-02-11T16:00:45Z",
    "recipient_name": "CORTAP FY26 Assessment Test",
    "deficiency_count": 1,
    "review_areas": 21
  }
}
```

**Request (Failure):**
```http
POST /webhooks/report-completed HTTP/1.1
Host: api.riskuity.com
Content-Type: application/json
X-CORTAP-Signature: sha256=5d7e8c9f...
X-CORTAP-Timestamp: 1707672045

{
  "job_id": "rpt-20260211-160045-a1b2c3d4",
  "status": "failed",
  "project_id": 33,
  "report_type": "draft_audit_report",
  "error": {
    "code": "DATA_FETCH_ERROR",
    "message": "Failed to fetch project controls from Riskuity API",
    "details": {
      "endpoint": "/projects/project_controls/33",
      "status_code": 404
    }
  }
}
```

**Webhook Security (X-CORTAP-Signature Header):**

To verify webhook authenticity, CORTAP-RPT signs each payload:

```python
# Signature generation (CORTAP-RPT)
import hmac
import hashlib

signature = hmac.new(
    key=WEBHOOK_SECRET.encode(),
    msg=f"{timestamp}.{json.dumps(payload)}".encode(),
    digestmod=hashlib.sha256
).hexdigest()

headers["X-CORTAP-Signature"] = f"sha256={signature}"
headers["X-CORTAP-Timestamp"] = str(timestamp)
```

**Signature verification (Riskuity):**
```python
# Verification (Riskuity webhook endpoint)
import hmac
import hashlib

def verify_webhook_signature(signature_header, timestamp_header, payload):
    expected_signature = hmac.new(
        key=WEBHOOK_SECRET.encode(),
        msg=f"{timestamp_header}.{json.dumps(payload)}".encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    received_signature = signature_header.replace("sha256=", "")

    if not hmac.compare_digest(expected_signature, received_signature):
        raise UnauthorizedError("Invalid webhook signature")

    # Check timestamp to prevent replay attacks
    if time.time() - int(timestamp_header) > 300:  # 5 minutes
        raise UnauthorizedError("Webhook timestamp too old")
```

**Webhook Payload Fields (Success):**

| Field | Type | Description |
|-------|------|-------------|
| `job_id` | string | Original job identifier |
| `status` | string | "completed" or "failed" |
| `project_id` | integer | Riskuity project ID |
| `report_type` | string | Type of report generated |
| `download_url` | string | S3 presigned URL (7-day expiry) |
| `expires_at` | string | ISO 8601 timestamp when URL expires |
| `file_size` | integer | File size in bytes |
| `file_name` | string | Suggested filename for download |
| `metadata` | object | Additional report metadata |

**Expected Response from Riskuity:**
```json
{
  "received": true,
  "job_id": "rpt-20260211-160045-a1b2c3d4"
}
```

**Webhook Retry Logic (CORTAP-RPT):**
- Retry on 5xx errors or network failures
- Exponential backoff: 1s, 2s, 4s, 8s, 16s
- Maximum 5 retries
- After 5 failures, mark job as "callback_failed" and alert operations

---

## File Storage & Delivery

### S3 Bucket Structure

```
s3://cortap-documents-prod/
├── reports/
│   ├── project-33/
│   │   ├── draft_audit_report_20260211.docx
│   │   ├── draft_audit_report_20260210.docx
│   │   └── recipient_information_request_20260211.docx
│   ├── project-34/
│   │   └── ...
└── data/
    ├── project-33/
    │   └── canonical_20260211_160045.json
    └── ...
```

### S3 Presigned URL

**Properties:**
- **Expiration:** 7 days (604,800 seconds)
- **Method:** GET only
- **Content-Type:** `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- **Content-Disposition:** `attachment; filename="CORTAP_Draft_Report_Project33_20260211.docx"`

**Example URL:**
```
https://cortap-documents-prod.s3.us-gov-west-1.amazonaws.com/reports/project-33/draft_audit_report_20260211.docx?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIOSFODNN7EXAMPLE%2F20260211%2Fus-gov-west-1%2Fs3%2Faws4_request&X-Amz-Date=20260211T160045Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=abcd1234...
```

**User Download Flow:**
1. User clicks "Download Report" button in Riskuity
2. Browser navigates directly to presigned S3 URL
3. S3 serves file with correct headers
4. Browser downloads file (no CORTAP-RPT involvement)

### File Retention Policy

**Decision Required:** How long should generated reports remain in S3?

**Options:**
1. **7 days** (matches presigned URL expiry) - Auto-delete when link expires
2. **30 days** - Keep for one month
3. **90 days** - Keep for one quarter
4. **Indefinite** - Archive permanently

**Recommendation:** TBD (awaiting decision)

**Implementation:** S3 Lifecycle Policy
```json
{
  "Rules": [{
    "Id": "DeleteOldReports",
    "Status": "Enabled",
    "Prefix": "reports/",
    "Expiration": {
      "Days": 30
    }
  }]
}
```

---

## Configuration Requirements

### CORTAP-RPT Environment Variables

```bash
# .env (CORTAP-RPT Service)

# S3 Configuration
S3_BUCKET_NAME=cortap-documents-prod
S3_REGION=us-gov-west-1
S3_PRESIGNED_URL_EXPIRATION=604800  # 7 days in seconds

# Webhook Security
WEBHOOK_SIGNATURE_SECRET=<shared_secret_with_riskuity>

# Job Processing
MAX_CONCURRENT_JOBS=5
JOB_TIMEOUT_SECONDS=300  # 5 minutes max per job
```

### Riskuity Environment Variables

```bash
# .env (Riskuity)

# CORTAP-RPT Integration
CORTAP_RPT_API_URL=https://cortap-rpt.example.com
CORTAP_WEBHOOK_SECRET=<same_shared_secret_as_cortap_rpt>
CORTAP_WEBHOOK_ENDPOINT=/webhooks/report-completed
```

### Shared Secret Generation

```bash
# Generate secure shared secret (run once, store in both systems)
openssl rand -hex 32
# Example output: 5d7e8c9f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d
```

---

## Error Handling

### Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `INVALID_TOKEN` | Missing or malformed Authorization header | Check token format and header |
| `EXPIRED_TOKEN` | User token expired during processing | Re-authenticate user |
| `INSUFFICIENT_PERMISSIONS` | User lacks project access | Check user permissions in Riskuity |
| `PROJECT_NOT_FOUND` | Project ID does not exist | Verify project_id |
| `DATA_FETCH_ERROR` | Failed to fetch from Riskuity API | Check Riskuity API status |
| `TRANSFORMATION_ERROR` | Data transformation failed | Review data quality |
| `GENERATION_ERROR` | Report generation failed | Check template compatibility |
| `S3_UPLOAD_ERROR` | Failed to upload to S3 | Check S3 permissions/connectivity |
| `WEBHOOK_DELIVERY_FAILED` | Could not deliver webhook | Check Riskuity webhook endpoint |

### Timeout Handling

**Token Expiration:**
- If user token expires during processing (>1 hour jobs)
- CORTAP-RPT should fail gracefully with `EXPIRED_TOKEN` error
- Riskuity should prompt user to re-trigger report generation

**Job Timeout:**
- Maximum processing time: 5 minutes per job
- After 5 minutes, job marked as `failed` with `JOB_TIMEOUT` error
- Webhook sent with failure notification

---

## Monitoring & Observability

### Metrics (CORTAP-RPT)

**Job Metrics:**
- `cortap.jobs.created` (counter) - Total jobs created
- `cortap.jobs.completed` (counter) - Successfully completed jobs
- `cortap.jobs.failed` (counter) - Failed jobs
- `cortap.jobs.duration` (histogram) - Job processing time
- `cortap.jobs.active` (gauge) - Currently processing jobs

**Webhook Metrics:**
- `cortap.webhooks.sent` (counter) - Webhooks sent
- `cortap.webhooks.failed` (counter) - Webhook delivery failures
- `cortap.webhooks.retries` (counter) - Webhook retry attempts

**S3 Metrics:**
- `cortap.s3.uploads` (counter) - Files uploaded
- `cortap.s3.upload_bytes` (histogram) - File sizes
- `cortap.s3.upload_errors` (counter) - Upload failures

### Logging

**Required Log Fields:**
- `job_id` - Unique job identifier
- `project_id` - Riskuity project ID
- `user_id` - User who triggered (from JWT)
- `correlation_id` - For distributed tracing
- `duration_ms` - Processing time
- `status` - Job status
- `error_code` - If failed

**Example Log Entry:**
```json
{
  "timestamp": "2026-02-11T16:00:45Z",
  "level": "INFO",
  "service": "cortap-rpt",
  "event": "job_completed",
  "job_id": "rpt-20260211-160045-a1b2c3d4",
  "project_id": 33,
  "user_id": 48,
  "correlation_id": "abc-123-def-456",
  "duration_ms": 28456,
  "status": "completed",
  "file_size": 156789,
  "deficiency_count": 1
}
```

---

## Testing Strategy

### Integration Test Scenarios

1. **Happy Path - Successful Report Generation**
   - Riskuity triggers report
   - CORTAP-RPT generates and uploads
   - Webhook delivered successfully
   - User downloads from S3

2. **Authentication Failure**
   - Invalid token → 401 error
   - Expired token → 401 error
   - Insufficient permissions → 403 error

3. **Data Fetch Failure**
   - Riskuity API returns 404
   - Job fails with `DATA_FETCH_ERROR`
   - Webhook notifies failure

4. **Webhook Delivery Failure**
   - Riskuity endpoint returns 500
   - CORTAP-RPT retries with backoff
   - After 5 retries, job marked `callback_failed`

5. **S3 URL Expiration**
   - Generate report
   - Wait 7+ days
   - URL returns 403 Forbidden
   - User must re-generate report

### Mock Implementations

**Riskuity Mock Webhook (for CORTAP-RPT testing):**
```python
# tests/mocks/riskuity_webhook_mock.py
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/webhooks/report-completed")
async def mock_webhook(request: Request):
    """Mock Riskuity webhook for testing."""
    payload = await request.json()

    # Verify signature
    signature = request.headers.get("X-CORTAP-Signature")
    # ... verification logic ...

    # Log received payload
    print(f"Webhook received: {payload['job_id']} - {payload['status']}")

    # Store for test assertions
    test_db.webhooks.append(payload)

    return {"received": True, "job_id": payload["job_id"]}
```

---

## Security Considerations

### 1. Token Security
- ✅ Tokens passed via `Authorization` header (not URL params)
- ✅ HTTPS required for all communication
- ✅ Tokens validated before processing
- ✅ Token permissions checked (user must have project access)

### 2. Webhook Security
- ✅ HMAC signature verification (prevents tampering)
- ✅ Timestamp check (prevents replay attacks)
- ✅ Shared secret stored securely (environment variables)

### 3. S3 Security
- ✅ Presigned URLs expire after 7 days
- ✅ GET-only access (no upload/delete)
- ✅ No public bucket access (presigned URLs only)
- ✅ Bucket policy restricts access to CORTAP-RPT service role

### 4. Data Privacy
- ✅ Reports contain sensitive compliance data
- ✅ Access controlled via presigned URLs
- ✅ No permanent public links
- ✅ Audit logging of all access

---

## Open Questions & Decisions Required

### 1. File Retention Policy ⏳
**Question:** How long should generated reports remain in S3?

**Options:**
- 7 days (matches presigned URL expiry)
- 30 days
- 90 days
- Indefinite

**Impact:** Storage costs, compliance requirements

**Decision:** **PENDING**

---

### 2. Report Regeneration ⏳
**Question:** Can users regenerate reports for the same project?

**Options:**
- A) Always create new file (unique timestamp in filename)
- B) Overwrite previous report (same filename)
- C) Limit regenerations (max X per day)

**Recommendation:** Option A (always create new file)

**Decision:** **PENDING**

---

### 3. User Notifications ✅
**Question:** Who notifies users when report is ready?

**Decision:** **RISKUITY** handles all user notifications (email, in-app, etc.)

**CORTAP-RPT Responsibility:** Only webhook callback to Riskuity

---

### 4. Long-Running Jobs ⏳
**Question:** What if token expires during report generation (jobs >1 hour)?

**Options:**
- A) Fail job with `EXPIRED_TOKEN` error
- B) Implement token refresh mechanism
- C) Use service account as fallback

**Current Approach:** Option A (fail gracefully)

**Future Enhancement:** Consider token refresh if needed

**Decision:** **PENDING REAL-WORLD TESTING**

---

### 5. Batch Report Generation ⏳
**Question:** Should we support generating reports for multiple projects at once?

**Use Case:** User selects 5 projects → generates 5 reports

**Options:**
- A) Client makes 5 separate API calls
- B) New endpoint: `POST /api/v1/generate-reports` (batch)

**Decision:** **DEFERRED** (implement if needed)

---

## Implementation Phases

### Phase 1: Core Integration (This Epic)
- ✅ API endpoint `/api/v1/generate-report`
- ✅ Background job processing
- ✅ S3 upload with presigned URLs
- ✅ Webhook callback implementation
- ✅ Job status tracking

### Phase 2: Riskuity Integration (Riskuity Team)
- ⏳ Webhook endpoint implementation
- ⏳ UI button for "Generate Report"
- ⏳ Download button when report ready
- ⏳ User notification system

### Phase 3: Production Hardening
- ⏳ Monitoring & alerting
- ⏳ Load testing
- ⏳ Error recovery procedures
- ⏳ Documentation for operations

---

## Appendix A: Sample Code

### Riskuity Webhook Implementation

```python
# Example Riskuity webhook endpoint implementation
from fastapi import APIRouter, Request, HTTPException
import hmac
import hashlib
import time

router = APIRouter()

WEBHOOK_SECRET = os.getenv("CORTAP_WEBHOOK_SECRET")

@router.post("/webhooks/report-completed")
async def handle_report_completion(request: Request):
    """
    Receive notification from CORTAP-RPT when report is ready.
    """
    # 1. Verify webhook signature
    signature_header = request.headers.get("X-CORTAP-Signature")
    timestamp_header = request.headers.get("X-CORTAP-Timestamp")

    if not signature_header or not timestamp_header:
        raise HTTPException(status_code=401, detail="Missing signature headers")

    payload = await request.json()

    # 2. Verify signature
    expected_signature = hmac.new(
        key=WEBHOOK_SECRET.encode(),
        msg=f"{timestamp_header}.{json.dumps(payload)}".encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    received_signature = signature_header.replace("sha256=", "")

    if not hmac.compare_digest(expected_signature, received_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 3. Check timestamp (prevent replay attacks)
    if time.time() - int(timestamp_header) > 300:  # 5 minutes
        raise HTTPException(status_code=401, detail="Webhook too old")

    # 4. Process webhook
    job_id = payload["job_id"]
    status = payload["status"]

    if status == "completed":
        # Store download URL in database
        await db.reports.update(
            job_id=job_id,
            status="ready",
            download_url=payload["download_url"],
            expires_at=payload["expires_at"],
            file_size=payload["file_size"],
            file_name=payload["file_name"]
        )

        # Notify user (optional - via email, push notification, etc.)
        project_id = payload["project_id"]
        await notify_user(
            project_id=project_id,
            message=f"Your {payload['report_type']} report is ready for download",
            action_url=f"/projects/{project_id}/reports/{job_id}"
        )

    elif status == "failed":
        # Log error, notify user of failure
        await db.reports.update(
            job_id=job_id,
            status="failed",
            error=payload["error"]
        )

        await notify_user(
            project_id=payload["project_id"],
            message=f"Report generation failed: {payload['error']['message']}",
            is_error=True
        )

    return {"received": True, "job_id": job_id}
```

---

## Appendix B: API Request Examples

### Generate Draft Audit Report

```bash
curl -X POST https://cortap-rpt.example.com/api/v1/generate-report \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 33,
    "report_type": "draft_audit_report",
    "callback_url": "https://api.riskuity.com/webhooks/report-completed"
  }'
```

**Response:**
```json
{
  "job_id": "rpt-20260211-160045-a1b2c3d4",
  "status": "processing",
  "estimated_completion": "2026-02-11T16:05:00Z",
  "status_url": "https://cortap-rpt.example.com/api/v1/jobs/rpt-20260211-160045-a1b2c3d4"
}
```

### Check Job Status (Optional)

```bash
curl https://cortap-rpt.example.com/api/v1/jobs/rpt-20260211-160045-a1b2c3d4 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "job_id": "rpt-20260211-160045-a1b2c3d4",
  "status": "completed",
  "project_id": 33,
  "report_type": "draft_audit_report",
  "created_at": "2026-02-11T16:00:45Z",
  "completed_at": "2026-02-11T16:01:13Z",
  "duration_seconds": 28,
  "download_url": "https://cortap-documents-prod.s3.us-gov-west-1.amazonaws.com/...",
  "expires_at": "2026-02-18T16:00:00Z"
}
```

---

---

# ALTERNATIVE APPROACH: Synchronous Integration

**Version:** 1.1
**Date:** 2026-02-12
**Status:** Proposed (Simpler Implementation)

---

## Overview

This section describes a **synchronous integration approach** as an alternative to the async request-response pattern described above. This approach is simpler to implement and maintain, at the cost of longer user wait times during generation.

### Key Differences from Async Approach

| Aspect | Async (Above) | Synchronous (This Section) |
|--------|---------------|----------------------------|
| **Response Time** | Immediate (< 1s) | Wait for completion (30-60s) |
| **Complexity** | High (background jobs, webhooks, storage) | Low (single request-response) |
| **Infrastructure** | Requires: DynamoDB, SQS/Lambda, webhook handling | Requires: Only Lambda with timeout |
| **User Experience** | Click → job started → notification | Click → loading spinner → download |
| **Error Handling** | Webhook retry, status polling | Immediate error response |
| **Implementation Time** | 3-4 weeks | 1-2 weeks |

### When to Use Synchronous Approach

**✅ Use Synchronous if:**
- Report generation takes < 60 seconds (typical case: 30-45s)
- Simpler architecture is preferred
- Faster time-to-market is critical
- Webhook infrastructure is complex/not desired
- User can wait with loading indicator

**❌ Avoid Synchronous if:**
- Report generation takes > 2 minutes
- Large reports with extensive data (> 1000 assessments)
- Need to support concurrent generation for same user
- API Gateway timeout constraints (29s) cannot be worked around

---

## Synchronous Architecture Diagram

```
┌─────────────┐                 ┌──────────────┐                ┌─────────┐
│  Riskuity   │                 │  CORTAP-RPT  │                │   S3    │
│   WebApp    │                 │   Service    │                │ Storage │
└──────┬──────┘                 └──────┬───────┘                └────┬────┘
       │                               │                             │
       │ 1. User clicks "Generate"     │                             │
       ├──────────────────────────────>│                             │
       │ POST /api/v1/generate-report  │                             │
       │ Authorization: Bearer <token> │                             │
       │                               │                             │
       │     (Wait 30-60 seconds)      │ 2. Fetch data (user token) │
       │                               │ 3. Validate data            │
       │                               │ 4. Generate Word doc        │
       │                               │                             │
       │                               ├────────────────────────────>│
       │                               │ 5. Upload DOCX to S3        │
       │                               │<────────────────────────────┤
       │                               │ 6. Get presigned URL        │
       │                               │    (24-hour expiry)         │
       │                               │                             │
       │<──────────────────────────────┤                             │
       │ 7. Complete Response          │                             │
       │ { "download_url": "...",      │                             │
       │   "report_id": "...",         │                             │
       │   "generated_at": "..." }     │                             │
       │                               │                             │
       │ 8. Browser auto-downloads     │                             │
       ├───────────────────────────────┼────────────────────────────>│
       │ GET presigned URL             │                             │
       │<────────────────────────────────────────────────────────────┤
       │ File downloaded               │                             │
```

**Timeline:**
- **0-2s**: Request validation, auth check
- **2-30s**: Fetch project data from Riskuity
- **30-45s**: Transform data, generate Word document
- **45-50s**: Upload to S3, generate presigned URL
- **50-52s**: Return response with download URL
- **52-55s**: Browser auto-downloads file

---

## API Specification (Synchronous)

### Generate Report Endpoint (Synchronous)

**Endpoint:** `POST /api/v1/generate-report-sync`

**Request:**
```http
POST /api/v1/generate-report-sync HTTP/1.1
Host: cortap-rpt.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "project_id": 33,
  "report_type": "draft_audit_report"
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `project_id` | integer | Yes | Riskuity project identifier |
| `report_type` | string | Yes | `draft_audit_report` or `recipient_information_request` |

**Response (Success - 200 OK):**
```json
{
  "status": "completed",
  "report_id": "rpt-20260212-141530-x7y8z9",
  "project_id": 33,
  "report_type": "draft_audit_report",
  "download_url": "https://s3-govcloud.amazonaws.com/cortap-docs/...",
  "expires_at": "2026-02-13T14:15:00Z",
  "generated_at": "2026-02-12T14:15:30Z",
  "file_size_bytes": 524288,
  "metadata": {
    "recipient_name": "Greater Portland Transit District",
    "review_type": "Triennial Review",
    "review_areas": 21,
    "deficiency_count": 2,
    "generation_time_ms": 48523
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Always "completed" (synchronous) |
| `report_id` | string | Unique report identifier |
| `project_id` | integer | Echo of request project_id |
| `report_type` | string | Echo of request report_type |
| `download_url` | string | Presigned S3 URL (24-hour expiry) |
| `expires_at` | string | ISO 8601 timestamp when URL expires |
| `generated_at` | string | ISO 8601 timestamp when report generated |
| `file_size_bytes` | integer | Size of generated file |
| `metadata` | object | Report metadata for display |

**Error Responses:**

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| 400 | `invalid_project_id` | Project ID not found or invalid |
| 400 | `invalid_report_type` | Report type not supported |
| 400 | `missing_required_data` | Critical data missing for generation |
| 401 | `authentication_failed` | Invalid or expired token |
| 403 | `insufficient_permissions` | User lacks access to project |
| 500 | `generation_failed` | Document generation error |
| 502 | `riskuity_api_error` | Riskuity API unavailable |
| 504 | `timeout` | Generation exceeded timeout (2 min) |

**Error Response Format:**
```json
{
  "error": "missing_required_data",
  "message": "Cannot generate report: missing recipient contact information",
  "details": {
    "missing_fields": ["recipient_contact_name", "recipient_contact_email"],
    "template": "draft_audit_report"
  },
  "timestamp": "2026-02-12T14:15:30Z",
  "correlation_id": "gen-x7y8z9"
}
```

---

## Implementation Details (Synchronous)

### 1. Timeout Considerations

**API Gateway Timeout Limits:**
- API Gateway: **29 seconds max**
- Lambda (standard): **15 minutes max**
- Lambda (with Function URL): **15 minutes max**

**Solution: Use Lambda Function URL (not API Gateway)**

```yaml
# SAM template excerpt
GenerateReportSyncFunction:
  Type: AWS::Serverless::Function
  Properties:
    Handler: app.handlers.generate_report_sync.handler
    Timeout: 120  # 2 minutes
    MemorySize: 2048
    FunctionUrlConfig:
      AuthType: AWS_IAM  # Or NONE with custom auth
      Cors:
        AllowOrigins:
          - https://app.riskuity.com
        AllowMethods:
          - POST
        AllowHeaders:
          - Authorization
          - Content-Type
```

**Why Lambda Function URL:**
- ✅ No 29s API Gateway limit
- ✅ Supports up to 15-minute execution
- ✅ Direct invocation (lower latency)
- ✅ Built-in CORS support
- ✅ Simpler configuration

### 2. Progress Indication (Client-Side)

Since generation is synchronous, provide clear user feedback:

**Riskuity Frontend Example:**
```javascript
async function generateReport(projectId) {
  // Show loading modal
  const modal = showLoadingModal({
    title: "Generating Report",
    message: "Fetching project data from Riskuity...",
    estimatedTime: "30-60 seconds"
  });

  try {
    // Start generation
    const response = await fetch(
      'https://cortap-rpt.example.com/api/v1/generate-report-sync',
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${getUserToken()}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          project_id: projectId,
          report_type: 'draft_audit_report'
        }),
        // Important: Set timeout longer than expected
        signal: AbortSignal.timeout(120000) // 2 min timeout
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message);
    }

    const result = await response.json();

    // Close loading modal
    modal.close();

    // Auto-download or show download link
    if (result.download_url) {
      // Option 1: Auto-download
      window.location.href = result.download_url;

      // Option 2: Show success with download button
      showSuccessModal({
        title: "Report Generated Successfully",
        message: `${result.metadata.recipient_name} - ${result.report_type}`,
        downloadUrl: result.download_url,
        expiresAt: result.expires_at
      });
    }

  } catch (error) {
    modal.close();
    showErrorModal({
      title: "Generation Failed",
      message: error.message,
      retryAction: () => generateReport(projectId)
    });
  }
}
```

### 3. Backend Implementation (Synchronous)

**FastAPI Endpoint:**
```python
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime, timedelta
import uuid

from app.services.riskuity_client import RiskuityClient
from app.services.data_transformer import DataTransformer
from app.services.document_generator import DocumentGenerator
from app.services.s3_storage import S3Storage
from app.services.validator import JsonValidator

router = APIRouter()


class GenerateReportRequest(BaseModel):
    project_id: int
    report_type: str  # "draft_audit_report" or "recipient_information_request"


class ReportMetadata(BaseModel):
    recipient_name: str
    review_type: str
    review_areas: int
    deficiency_count: int
    generation_time_ms: int


class GenerateReportResponse(BaseModel):
    status: str
    report_id: str
    project_id: int
    report_type: str
    download_url: str
    expires_at: str
    generated_at: str
    file_size_bytes: int
    metadata: ReportMetadata


@router.post(
    "/generate-report-sync",
    response_model=GenerateReportResponse,
    summary="Generate Report (Synchronous)",
    description="Generate CORTAP report synchronously. Returns when complete (30-60s)."
)
async def generate_report_sync(
    request: GenerateReportRequest,
    authorization: str = Header(...)
) -> GenerateReportResponse:
    """
    Generate CORTAP report synchronously.

    This endpoint blocks until report generation is complete, then returns
    the download URL. Typical execution time: 30-60 seconds.

    Args:
        request: Report generation request
        authorization: Bearer token from Riskuity

    Returns:
        GenerateReportResponse with download URL

    Raises:
        HTTPException: On validation, generation, or API errors
    """
    start_time = datetime.utcnow()
    report_id = f"rpt-{start_time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"

    # Extract token from Authorization header
    token = authorization.replace("Bearer ", "")

    try:
        # Step 1: Initialize services
        riskuity_client = RiskuityClient(
            base_url="https://api.riskuity.com",
            api_key=token  # Pass user token
        )
        transformer = DataTransformer()
        validator = JsonValidator()
        generator = DocumentGenerator()
        s3_storage = S3Storage()

        # Step 2: Fetch project data from Riskuity (10-20s)
        project_data = await riskuity_client.get_project(request.project_id)
        project_controls = await riskuity_client.get_project_controls(request.project_id)

        # Step 3: Transform to canonical JSON (1-2s)
        canonical_json = await transformer.transform(
            project=project_data,
            controls=project_controls
        )

        # Step 4: Validate data (1s)
        validation_result = await validator.validate_json_schema(canonical_json)
        if not validation_result.valid:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_data",
                    "message": "Project data validation failed",
                    "errors": validation_result.errors
                }
            )

        # Step 5: Check completeness
        completeness = await validator.check_completeness(
            canonical_json,
            template_id=request.report_type
        )
        if not completeness.can_generate:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "missing_required_data",
                    "message": "Cannot generate report: missing critical fields",
                    "missing_fields": completeness.missing_critical_fields
                }
            )

        # Step 6: Generate document (10-20s)
        document_bytes = await generator.generate(
            template_id=request.report_type,
            data=canonical_json
        )

        # Step 7: Upload to S3 (2-5s)
        filename = f"{report_id}_{request.report_type}.docx"
        s3_key = await s3_storage.upload_document(
            file_content=document_bytes,
            project_id=str(request.project_id),
            template_id=request.report_type,
            filename=filename
        )

        # Step 8: Generate presigned URL (24-hour expiry)
        download_url = await s3_storage.generate_presigned_url(
            s3_key=s3_key,
            expiration=86400  # 24 hours
        )

        # Calculate generation time
        generation_time_ms = int(
            (datetime.utcnow() - start_time).total_seconds() * 1000
        )

        # Build response
        return GenerateReportResponse(
            status="completed",
            report_id=report_id,
            project_id=request.project_id,
            report_type=request.report_type,
            download_url=download_url,
            expires_at=(datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z",
            generated_at=datetime.utcnow().isoformat() + "Z",
            file_size_bytes=len(document_bytes),
            metadata=ReportMetadata(
                recipient_name=canonical_json["project"]["recipient_name"],
                review_type=canonical_json["project"]["review_type"],
                review_areas=len(canonical_json["assessments"]),
                deficiency_count=canonical_json["metadata"]["deficiency_count"],
                generation_time_ms=generation_time_ms
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "generation_failed",
                "message": str(e),
                "report_id": report_id
            }
        )
```

### 4. Performance Optimization

**To keep synchronous generation under 60 seconds:**

1. **Cache Riskuity Data** (if token reused):
   ```python
   # Add caching layer
   @functools.lru_cache(maxsize=100)
   async def get_cached_project_data(project_id: int, token: str):
       # Cache for 5 minutes
       pass
   ```

2. **Parallel Data Fetching**:
   ```python
   # Fetch multiple endpoints in parallel
   results = await asyncio.gather(
       riskuity_client.get_project(project_id),
       riskuity_client.get_project_controls(project_id),
       # Other endpoints...
   )
   ```

3. **Pre-warm Lambda Instances**:
   ```yaml
   # SAM template
   ProvisionedConcurrencyConfig:
     ProvisionedConcurrentExecutions: 2  # Keep 2 warm
   ```

4. **Optimize Document Generation**:
   - Keep template in memory
   - Reuse docx template objects
   - Minimize disk I/O

**Typical Performance Profile:**
```
┌─────────────────────────┬──────────┬────────────┐
│ Step                    │ Time (s) │ % of Total │
├─────────────────────────┼──────────┼────────────┤
│ Request validation      │ 0.5      │ 1%         │
│ Fetch Riskuity data     │ 15-25    │ 45%        │
│ Data transformation     │ 2-3      │ 6%         │
│ Data validation         │ 1        │ 2%         │
│ Document generation     │ 10-15    │ 30%        │
│ S3 upload               │ 3-5      │ 10%        │
│ Response preparation    │ 0.5      │ 1%         │
├─────────────────────────┼──────────┼────────────┤
│ TOTAL                   │ 32-50s   │ 100%       │
└─────────────────────────┴──────────┴────────────┘
```

---

## Comparison: Async vs Synchronous

### Async (Original Design)

**Pros:**
- ✅ Immediate response to user (< 1s)
- ✅ No API Gateway timeout concerns
- ✅ Better for long-running operations (> 2 min)
- ✅ Supports queueing and rate limiting
- ✅ Can show real-time progress updates

**Cons:**
- ❌ Complex architecture (DynamoDB, SQS, webhooks)
- ❌ Webhook reliability concerns (retries, failures)
- ❌ User must wait for notification
- ❌ More infrastructure to maintain
- ❌ Longer implementation time (3-4 weeks)

### Synchronous (This Section)

**Pros:**
- ✅ Simpler architecture (just Lambda + S3)
- ✅ Immediate download after generation
- ✅ Easier to debug and monitor
- ✅ No webhook infrastructure needed
- ✅ Faster implementation (1-2 weeks)
- ✅ Better UX for fast reports (< 60s)

**Cons:**
- ❌ User must wait during generation (30-60s)
- ❌ Requires Lambda Function URL (not API Gateway)
- ❌ Risk of timeout for slow operations
- ❌ Single request-response (no queueing)
- ❌ Harder to show granular progress

---

## Recommendation

**For MVP/Phase 1: Use Synchronous Approach**

**Rationale:**
1. ✅ Typical report generation: 30-50 seconds (well under 2-min limit)
2. ✅ Simpler to implement and maintain
3. ✅ Faster time-to-market (1-2 weeks vs 3-4 weeks)
4. ✅ Better user experience (immediate download)
5. ✅ Easier to troubleshoot issues

**For Future/Phase 2: Consider Async if:**
- Report generation consistently exceeds 90 seconds
- Large reports with extensive data become common
- Need to support batch generation
- Require sophisticated progress tracking

**Migration Path:**
- Start with synchronous endpoint: `/api/v1/generate-report-sync`
- Add async endpoint later: `/api/v1/generate-report-async`
- Client chooses based on report size/complexity
- Shared backend logic (just different response handling)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-11 | System Architect | Initial specification (async) |
| 1.1 | 2026-02-12 | System Architect | Added synchronous integration section |

---

## Approval & Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| CORTAP-RPT Architect | | | |
| Riskuity Integration Lead | | | |
| Security Review | | | |
| DevOps Lead | | | |
