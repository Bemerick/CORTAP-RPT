## Epic 3.6: Riskuity Integration - Async Report Generation & Webhook Delivery

**Epic Goal:** Implement async report generation endpoint that accepts user tokens from Riskuity, generates reports in background, uploads to S3, and delivers download URLs via webhook callback.

**Business Value:** Enables seamless integration between Riskuity and CORTAP-RPT where users can click a button in Riskuity to trigger report generation and receive download links automatically when complete.

**Architectural Components:**
- `api/routes/reports.py` - Report generation endpoint
- `services/job_manager.py` - Background job orchestration
- `services/webhook_client.py` - Webhook delivery to Riskuity
- `models/job.py` - Job tracking data models  
- Job storage (DynamoDB or in-memory)

**Integration Pattern:** Async Request-Response with Webhook Callback

**Reference:** See `docs/RISKUITY-CORTAP-INTEGRATION-SPEC.md` for complete specification

**Dependencies:** Epic 3.5 (Data Service), Epic 4 or Epic 2 (at least one template)

---

### Story 3.6.1: Implement Generate Report API Endpoint

As a Riskuity integration developer,
I want a REST endpoint to trigger async report generation,
So that Riskuity users can request reports and receive job tracking information.

**Acceptance Criteria:**

**Given** Riskuity has authenticated a user and obtained their JWT token
**When** Riskuity makes a POST request to `/api/v1/generate-report`
**Then** The endpoint:

**Request Handling:**
- Accepts `Authorization: Bearer <user_token>` header
- Validates token format (JWT)
- Extracts user context from token
- Accepts JSON body with:
  - `project_id` (integer, required)
  - `report_type` (string, required: "draft_audit_report" or "recipient_information_request")
  - `callback_url` (string, required: Riskuity webhook URL)
  - `options` (object, optional: `include_attachments`, `format`)

**Response (202 Accepted):**
```json
{
  "job_id": "rpt-20260211-160045-a1b2c3d4",
  "status": "processing",
  "estimated_completion": "2026-02-11T16:05:00Z",
  "status_url": "/api/v1/jobs/rpt-20260211-160045-a1b2c3d4"
}
```

**And** Job record is created with:
- Unique `job_id` (format: `rpt-YYYYMMDD-HHMMSS-{uuid}`)
- Status: `processing`
- Project ID, report type, callback URL
- User context (from token)
- Created timestamp

**And** Background task is queued for report generation

**And** Error handling returns appropriate status codes:
- 400 Bad Request - Missing or invalid fields
- 401 Unauthorized - Invalid/missing token
- 403 Forbidden - User lacks project access
- 404 Not Found - Project doesn't exist
- 422 Unprocessable Entity - Invalid report_type
- 500 Internal Server Error - Server failure

**Prerequisites:** None (first story in epic)

**Technical Notes:**
- Use FastAPI `BackgroundTasks` for async processing
- Implement in `app/api/routes/reports.py`
- Job ID generation: `f"rpt-{datetime.now():%Y%m%d-%H%M%S}-{uuid4().hex[:8]}"`
- Token validation: verify JWT format, extract user_id/tenant_id
- Follow integration spec: `docs/RISKUITY-CORTAP-INTEGRATION-SPEC.md`

**Definition of Done:**
- Endpoint accepts requests and returns 202 with job_id
- Job records created in storage
- Background task queued
- All error codes handled
- Unit tests cover all paths
- Integration test with mock Riskuity request

---

### Story 3.6.2: Implement Background Job Processor

As a system architect,
I want a background job processor that orchestrates report generation workflow,
So that reports can be generated asynchronously without blocking the API.

**Acceptance Criteria:**

**Given** A job has been created by the API endpoint
**When** The background task executes
**Then** The processor:

**Phase 1: Data Fetching**
- Calls `DataService.get_project_data(project_id, user_token=user_token)`
- Uses user's token for Riskuity API authentication
- Handles token expiration errors gracefully
- Logs data fetch duration and success/failure

**Phase 2: Report Generation**
- Calls `ReportGeneratorService.generate_report(report_type, data)`
- Generates Word document (DOCX format)
- Validates output file size > 0
- Logs generation duration

**Phase 3: S3 Upload**
- Uploads to S3 with key: `reports/project-{project_id}/{report_type}_{YYYYMMDD}.docx`
- Sets Content-Type: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Sets Content-Disposition: `attachment; filename="..."`
- Logs upload success and file size

**Phase 4: Presigned URL Generation**
- Generates S3 presigned URL with 7-day expiry (604,800 seconds)
- URL allows GET only
- Logs URL generation

**Phase 5: Job Completion**
- Updates job status to `completed`
- Stores download_url, expires_at, file_size
- Records completed_at timestamp
- Calculates total duration

**And** On any failure:
- Updates job status to `failed`
- Stores error details (code, message, traceback)
- Logs full error context
- Does NOT retry (single attempt only)

**Prerequisites:** Story 3.6.1 (API endpoint), Epic 3.5 (DataService), Epic 4 or 2 (ReportGenerator)

**Technical Notes:**
- Implement in `app/services/job_manager.py`
- Use try/except blocks for each phase
- Log with correlation_id for distributed tracing
- Timeout: 5 minutes maximum per job
- Store job state in DynamoDB or in-memory dict (config-driven)

**Definition of Done:**
- Background processor completes all 5 phases for successful job
- Failed jobs update status with error details
- Comprehensive logging at each phase
- Unit tests mock each service dependency
- Integration test with real S3 upload (localstack OK)

---

### Story 3.6.3: Implement Webhook Notification Client

As an integration developer,
I want a webhook client that notifies Riskuity when reports are complete,
So that users can be informed and download their reports.

**Acceptance Criteria:**

**Given** A report generation job has completed (success or failure)
**When** The webhook client sends notification
**Then** The client:

**Success Webhook Payload:**
```json
{
  "job_id": "rpt-20260211-160045-a1b2c3d4",
  "status": "completed",
  "project_id": 33,
  "report_type": "draft_audit_report",
  "download_url": "https://s3.us-gov-west-1.amazonaws.com/...",
  "expires_at": "2026-02-18T16:00:00Z",
  "file_size": 156789,
  "file_name": "CORTAP_Draft_Report_Project33_20260211.docx",
  "metadata": {
    "generated_at": "2026-02-11T16:00:45Z",
    "recipient_name": "...",
    "deficiency_count": 1,
    "review_areas": 21
  }
}
```

**Failure Webhook Payload:**
```json
{
  "job_id": "rpt-20260211-160045-a1b2c3d4",
  "status": "failed",
  "project_id": 33,
  "report_type": "draft_audit_report",
  "error": {
    "code": "DATA_FETCH_ERROR",
    "message": "Failed to fetch project controls from Riskuity API",
    "details": {...}
  }
}
```

**And** Request includes security headers:
- `X-CORTAP-Signature: sha256=<hmac_signature>`
- `X-CORTAP-Timestamp: <unix_timestamp>`

**And** Signature calculation:
```python
signature = hmac.new(
    key=WEBHOOK_SECRET.encode(),
    msg=f"{timestamp}.{json.dumps(payload)}".encode(),
    digestmod=hashlib.sha256
).hexdigest()
```

**And** Retry logic on failure:
- Retry on 5xx errors or network failures
- Exponential backoff: 1s, 2s, 4s, 8s, 16s
- Maximum 5 retry attempts
- After 5 failures, mark job as `callback_failed`

**And** HTTP request details:
- Method: POST
- Content-Type: application/json
- Timeout: 30 seconds
- Logs each attempt with status code

**Prerequisites:** Story 3.6.2 (job processor)

**Technical Notes:**
- Implement in `app/services/webhook_client.py`
- Use httpx AsyncClient for HTTP requests
- Store WEBHOOK_SECRET in environment variables
- Follow spec: `docs/RISKUITY-CORTAP-INTEGRATION-SPEC.md`
- Log webhook delivery success/failure with correlation_id

**Definition of Done:**
- Webhooks sent for both success and failure cases
- HMAC signature correctly calculated
- Retry logic works with exponential backoff
- Failed deliveries logged and tracked
- Unit tests mock HTTP requests
- Integration test with mock webhook server

---

### Story 3.6.4: Implement Job Status Query Endpoint

As a Riskuity developer,
I want an endpoint to query job status,
So that I can poll for job completion if webhook delivery fails.

**Acceptance Criteria:**

**Given** A job has been created
**When** Riskuity makes a GET request to `/api/v1/jobs/{job_id}`
**Then** The endpoint:

**Response (Job Processing):**
```json
{
  "job_id": "rpt-20260211-160045-a1b2c3d4",
  "status": "processing",
  "project_id": 33,
  "report_type": "draft_audit_report",
  "created_at": "2026-02-11T16:00:45Z",
  "updated_at": "2026-02-11T16:00:45Z"
}
```

**Response (Job Completed):**
```json
{
  "job_id": "rpt-20260211-160045-a1b2c3d4",
  "status": "completed",
  "project_id": 33,
  "report_type": "draft_audit_report",
  "created_at": "2026-02-11T16:00:45Z",
  "completed_at": "2026-02-11T16:01:13Z",
  "duration_seconds": 28,
  "download_url": "https://s3.us-gov-west-1.amazonaws.com/...",
  "expires_at": "2026-02-18T16:00:00Z",
  "file_size": 156789
}
```

**Response (Job Failed):**
```json
{
  "job_id": "rpt-20260211-160045-a1b2c3d4",
  "status": "failed",
  "project_id": 33,
  "report_type": "draft_audit_report",
  "created_at": "2026-02-11T16:00:45Z",
  "failed_at": "2026-02-11T16:01:05Z",
  "error": {
    "code": "DATA_FETCH_ERROR",
    "message": "Failed to fetch project controls"
  }
}
```

**And** Authorization:
- Requires `Authorization: Bearer <token>` header
- Token must belong to user who created the job OR service account
- Returns 403 if user doesn't own the job

**And** Error handling:
- 404 Not Found - Job ID doesn't exist
- 401 Unauthorized - Missing/invalid token
- 403 Forbidden - User doesn't own this job

**Prerequisites:** Story 3.6.1 (job creation)

**Technical Notes:**
- Implement in `app/api/routes/reports.py`
- Query job storage (DynamoDB/in-memory)
- Include correlation_id in logs
- Optional: Implement polling with `Retry-After` header

**Definition of Done:**
- Endpoint returns job status correctly
- Authorization enforced
- All status types handled (processing, completed, failed)
- Error codes correct
- Unit tests cover all cases

---

### Story 3.6.5: Implement Job Storage (DynamoDB)

As a DevOps engineer,
I want persistent job storage in DynamoDB,
So that job state survives Lambda restarts and can be queried later.

**Acceptance Criteria:**

**Given** AWS credentials are configured
**When** I deploy the job storage infrastructure
**Then** A DynamoDB table is created:

**Table Configuration:**
- Table name: `cortap-jobs`
- Partition key: `job_id` (String)
- Sort key: None
- Billing mode: PAY_PER_REQUEST (on-demand)
- TTL attribute: `ttl` (auto-delete old jobs after 30 days)

**Table Attributes:**
- `job_id` - String (PK)
- `status` - String (processing/completed/failed/callback_failed)
- `project_id` - Number
- `report_type` - String
- `callback_url` - String
- `user_id` - String (from token)
- `tenant_id` - String (from token)
- `created_at` - Number (Unix timestamp)
- `updated_at` - Number (Unix timestamp)
- `completed_at` - Number (optional)
- `failed_at` - Number (optional)
- `download_url` - String (optional)
- `expires_at` - String (optional, ISO 8601)
- `file_size` - Number (optional)
- `duration_seconds` - Number (optional)
- `error` - Map (optional: code, message, details)
- `ttl` - Number (Unix timestamp, 30 days from creation)

**And** JobManager class provides methods:
- `create_job(job_data) -> Job`
- `get_job(job_id) -> Optional[Job]`
- `update_job(job_id, updates) -> Job`
- `list_jobs(user_id, limit=10) -> List[Job]`

**And** SAM template updated:
- DynamoDB table resource added
- Lambda execution role has DynamoDB permissions
- Environment variable: `JOBS_TABLE_NAME`

**Prerequisites:** Story 3.6.1 (job models defined)

**Technical Notes:**
- Implement in `app/services/job_storage.py`
- Use boto3 for DynamoDB access
- Follow AWS best practices for DynamoDB queries
- TTL set to `created_at + 30 days`
- Index on `user_id` for listing user's jobs (GSI)

**Definition of Done:**
- DynamoDB table created via SAM template
- JobManager CRUD operations work
- TTL configured for auto-cleanup
- Unit tests mock DynamoDB
- Integration test with LocalStack or real DynamoDB

---

### Story 3.6.6: Add Monitoring & Observability

As a DevOps engineer,
I want comprehensive monitoring for the report generation pipeline,
So that I can track performance, detect failures, and debug issues.

**Acceptance Criteria:**

**Given** The report generation system is deployed
**When** Jobs are processed
**Then** The following metrics are emitted:

**Job Metrics (CloudWatch/Datadog):**
- `cortap.jobs.created` (counter) - Tag: report_type
- `cortap.jobs.completed` (counter) - Tag: report_type
- `cortap.jobs.failed` (counter) - Tag: report_type, error_code
- `cortap.jobs.duration` (histogram) - Tag: report_type
- `cortap.jobs.active` (gauge) - Currently processing

**Webhook Metrics:**
- `cortap.webhooks.sent` (counter)
- `cortap.webhooks.failed` (counter) - Tag: retry_count
- `cortap.webhooks.retry` (counter) - Tag: attempt

**S3 Metrics:**
- `cortap.s3.uploads` (counter) - Tag: report_type
- `cortap.s3.upload_bytes` (histogram)
- `cortap.s3.upload_errors` (counter)

**And** Structured logging includes:
- `job_id` - Unique job identifier
- `project_id` - Riskuity project
- `user_id` - User who triggered
- `correlation_id` - Request tracing
- `duration_ms` - Processing time
- `status` - Job outcome
- `error_code` - If failed

**And** CloudWatch Dashboard shows:
- Job completion rate (success/failure)
- Average job duration
- Webhook delivery success rate
- Active jobs gauge
- Error rate by type

**And** Alarms configured for:
- High failure rate (>10% in 5 minutes)
- Webhook delivery failures (>5 consecutive)
- Long-running jobs (>5 minutes)
- S3 upload errors

**Prerequisites:** Stories 3.6.1-3.6.5 (full pipeline)

**Technical Notes:**
- Use CloudWatch Embedded Metric Format (EMF)
- Log structured JSON to stdout
- Implement in `app/utils/metrics.py`
- Dashboard defined in SAM template or Terraform
- Follow observability best practices

**Definition of Done:**
- All metrics emitted correctly
- Logs include required fields
- CloudWatch dashboard created
- Alarms configured and tested
- Documentation for operations team

---

### Story 3.6.7: Integration Testing with Mock Riskuity

As a QA engineer,
I want end-to-end integration tests simulating Riskuity interaction,
So that I can verify the complete workflow before production deployment.

**Acceptance Criteria:**

**Given** A test environment with mock services
**When** Integration tests execute
**Then** The following scenarios are tested:

**Scenario 1: Happy Path**
1. Mock Riskuity sends generate request with valid token
2. CORTAP-RPT returns 202 with job_id
3. Background job fetches data (mocked Riskuity API)
4. Report generated successfully
5. File uploaded to S3 (LocalStack)
6. Webhook sent to mock endpoint
7. Mock Riskuity receives webhook with download URL
8. Verify signature validation passes
9. Download URL works (S3 presigned URL)

**Scenario 2: Invalid Token**
1. Request with expired/invalid token
2. Returns 401 Unauthorized
3. No job created
4. No webhook sent

**Scenario 3: Data Fetch Failure**
1. Valid request
2. Riskuity API returns 404
3. Job fails with DATA_FETCH_ERROR
4. Webhook sent with error details

**Scenario 4: Webhook Delivery Failure**
1. Job completes successfully
2. Webhook endpoint returns 500
3. Retry logic executes (5 attempts)
4. After retries, job marked `callback_failed`
5. Can still query job status via API

**And** Test fixtures include:
- Mock user JWT tokens
- Mock Riskuity project data
- Mock webhook server (FastAPI)
- LocalStack for S3

**And** Assertions verify:
- Job state transitions correctly
- S3 files uploaded
- Webhook payloads match spec
- HMAC signatures valid
- Error handling works

**Prerequisites:** Stories 3.6.1-3.6.6 (complete pipeline)

**Technical Notes:**
- Use pytest with async support
- Mock Riskuity API with `httpx.MockClient` or FastAPI TestClient
- LocalStack for S3 testing
- Test isolation (clean DynamoDB between tests)
- Implement in `tests/integration/test_report_generation.py`

**Definition of Done:**
- All 4 scenarios pass
- Mock Riskuity webhook server implemented
- Tests run in CI/CD pipeline
- Code coverage >80% for integration code
- Documentation for running tests locally

---

## Epic 3.6 Summary

**Total Stories:** 7
**Estimated Effort:** 7-10 days (1 developer)

**Deliverables:**
- ✅ `/api/v1/generate-report` endpoint (async)
- ✅ Background job processor (5 phases)
- ✅ Webhook notification client (with retry)
- ✅ `/api/v1/jobs/{job_id}` status endpoint
- ✅ DynamoDB job storage
- ✅ CloudWatch metrics & alarms
- ✅ Integration tests with mock Riskuity

**Integration Points:**
- Epic 3.5 (DataService) - Used for fetching project data
- Epic 4 or Epic 2 (ReportGenerator) - Used for generating documents
- Epic 5 (S3Storage) - Used for file upload and presigned URLs

**Success Criteria:**
- Riskuity can trigger report generation with user tokens
- Reports generated asynchronously in <30 seconds
- Webhook delivery success rate >99%
- Download URLs work for 7 days
- Complete observability into job pipeline

**Reference Documentation:**
- `docs/RISKUITY-CORTAP-INTEGRATION-SPEC.md` - Complete integration specification
- `docs/TRANSFORMATION-IMPLEMENTATION-COMPLETE.md` - Data transformation implementation

