# Riskuity Integration - Implementation Plan

**Date:** 2026-02-11
**Status:** Design Approved, Ready for Implementation

---

## Summary

Complete plan for implementing async report generation integration between Riskuity and CORTAP-RPT, including webhook delivery of download URLs.

---

## Key Decisions Made

### 1. Authentication Approach ✅
**Decision:** User Token Pass-Through (Option 1)

**Rationale:**
- User permissions automatically enforced
- Audit trail shows which user generated each report
- No service account with elevated permissions needed
- Token already validated by Riskuity

**Implementation:**
- Riskuity passes user's JWT token in `Authorization` header
- CORTAP-RPT reuses token for Riskuity API calls
- User can only generate reports for projects they can access

---

### 2. File Delivery Architecture ✅
**Decision:** S3 Presigned URLs with Webhook Callback

**Flow:**
1. User clicks "Generate Report" in Riskuity
2. Riskuity calls CORTAP-RPT API with user token
3. CORTAP-RPT returns job_id immediately (async)
4. Background job generates report and uploads to S3
5. CORTAP-RPT sends webhook to Riskuity with presigned URL
6. Riskuity stores URL and notifies user
7. User downloads directly from S3 (7-day expiry)

**Benefits:**
- Scalable (no CORTAP-RPT involvement in downloads)
- Secure (presigned URLs expire, signed webhooks)
- Fast user experience (async processing)

---

### 3. User Notifications ✅
**Decision:** Riskuity Handles All Notifications

**CORTAP-RPT Responsibility:**
- Only webhook callback to Riskuity

**Riskuity Responsibility:**
- Email notifications
- In-app notifications
- UI updates (show download button)

---

## Documentation Created

### 1. Integration Specification
**File:** `docs/RISKUITY-CORTAP-INTEGRATION-SPEC.md`

**Contents:**
- Complete API specifications (request/response formats)
- Authentication flow details
- Webhook payload schemas
- Security implementation (HMAC signatures)
- Error handling and retry logic
- Configuration requirements
- Monitoring & observability
- Open questions and decisions

**Status:** ✅ Complete

---

### 2. Epic & Stories
**File:** `docs/epics-integration-addon.md`

**Epic 3.6:** Riskuity Integration - Async Report Generation & Webhook Delivery

**Stories (7 total):**
1. **Story 3.6.1:** Generate Report API Endpoint
2. **Story 3.6.2:** Background Job Processor
3. **Story 3.6.3:** Webhook Notification Client
4. **Story 3.6.4:** Job Status Query Endpoint
5. **Story 3.6.5:** Job Storage (DynamoDB)
6. **Story 3.6.6:** Monitoring & Observability
7. **Story 3.6.7:** Integration Testing with Mock Riskuity

**Estimated Effort:** 7-10 days (1 developer)

**Status:** ✅ Complete, ready for implementation

---

## Open Questions & Next Steps

### Open Questions (Pending Decision)

#### 1. File Retention Policy ⏳
**Question:** How long should generated reports remain in S3?

**Options:**
- 7 days (matches presigned URL expiry)
- 30 days
- 90 days
- Indefinite

**Impact:** Storage costs, compliance requirements

**Action:** Get decision from stakeholders

---

#### 2. Report Regeneration ⏳
**Question:** Can users regenerate reports for the same project?

**Options:**
- A) Always create new file (unique timestamp in filename)
- B) Overwrite previous report (same filename)
- C) Limit regenerations (max X per day)

**Recommendation:** Option A (always create new file)

**Action:** Confirm with product owner

---

#### 3. Long-Running Jobs ⏳
**Question:** What if user token expires during report generation (jobs >1 hour)?

**Current Approach:** Fail gracefully with `EXPIRED_TOKEN` error

**Future Enhancement:** Token refresh mechanism if needed

**Action:** Monitor in production, implement refresh if necessary

---

### Next Steps

#### For CORTAP-RPT Team:

1. **Complete Epic 3.5 Remaining Stories** (if not done)
   - Story 3.5.4: S3 Storage for JSON Data Files
   - Story 3.5.5: Caching and TTL Logic
   - Story 3.5.6: JSON Schema Validation

2. **Implement Epic 3.6 Stories** (7 stories)
   - Start with Story 3.6.1 (API endpoint)
   - Then Story 3.6.5 (DynamoDB storage)
   - Then Stories 3.6.2-3.6.4 (job processing pipeline)
   - Finally Stories 3.6.6-3.6.7 (monitoring & testing)

3. **Test with Mock Riskuity**
   - Use integration tests to validate end-to-end flow
   - Verify webhook delivery and signature validation
   - Test S3 presigned URL generation

---

#### For Riskuity Team:

1. **Implement Webhook Endpoint**
   - `POST /webhooks/report-completed`
   - HMAC signature verification
   - Store download URLs in database
   - Handle success/failure cases

2. **Add "Generate Report" Button**
   - UI button in project view
   - Calls CORTAP-RPT `/api/v1/generate-report`
   - Pass user's JWT token in Authorization header
   - Store returned job_id

3. **Display Download Button**
   - When webhook received with status="completed"
   - Show "Download Report" button with presigned URL
   - Display expiry date
   - Handle expired URLs gracefully

4. **User Notifications**
   - Email when report is ready
   - In-app notification
   - Error notifications if generation fails

---

#### Coordination Between Teams:

1. **Shared Secret Generation**
   ```bash
   # Run once, store in both systems
   openssl rand -hex 32
   ```
   - Store in CORTAP-RPT: `WEBHOOK_SIGNATURE_SECRET`
   - Store in Riskuity: `CORTAP_WEBHOOK_SECRET`

2. **Environment Configuration**
   - CORTAP-RPT: Set `S3_BUCKET_NAME`, `S3_REGION`
   - Riskuity: Set `CORTAP_RPT_API_URL`

3. **Integration Testing**
   - CORTAP-RPT: Mock Riskuity webhook endpoint
   - Riskuity: Test with CORTAP-RPT dev environment
   - Joint testing session before production

---

## Implementation Timeline

### Week 1: Foundation
- ✅ Integration spec documented
- ✅ Epic 3.6 stories created
- ⏳ Generate shared secret
- ⏳ Set up dev environments

### Week 2: Core Implementation (CORTAP-RPT)
- Story 3.6.1: API endpoint
- Story 3.6.5: DynamoDB storage
- Story 3.6.2: Job processor

### Week 3: Integration & Testing
- Story 3.6.3: Webhook client
- Story 3.6.4: Status endpoint
- Story 3.6.6: Monitoring
- Story 3.6.7: Integration tests

### Week 4: Riskuity Integration
- Riskuity webhook endpoint
- Riskuity UI updates
- Joint integration testing

### Week 5: Production Deployment
- Deploy to production
- Monitor metrics
- Iterate based on real usage

---

## Success Criteria

### Technical Metrics:
- [ ] Report generation completes in <30 seconds (95th percentile)
- [ ] Webhook delivery success rate >99%
- [ ] S3 presigned URLs work for full 7-day period
- [ ] No data leakage between users/tenants
- [ ] All integration tests passing

### Business Metrics:
- [ ] Users can generate reports from Riskuity UI
- [ ] Download links delivered within 1 minute
- [ ] Zero manual intervention required
- [ ] Comprehensive error messages for failures
- [ ] Audit trail for all report generations

---

## Risk Mitigation

### Risk 1: Token Expiration During Processing
**Mitigation:**
- Monitor job durations
- Implement timeout at 5 minutes
- Fail gracefully with clear error message
- Future: Add token refresh if needed

### Risk 2: Webhook Delivery Failure
**Mitigation:**
- Retry logic with exponential backoff (5 attempts)
- Job status query endpoint as fallback
- Alert operations if >5 consecutive failures
- Monitor webhook success rate

### Risk 3: S3 URL Expiration Without Download
**Mitigation:**
- 7-day expiry gives ample time
- User can regenerate report if needed
- Log downloads to track usage patterns
- Future: Email reminder before expiry

---

## References

- **Integration Spec:** `docs/RISKUITY-CORTAP-INTEGRATION-SPEC.md`
- **Epic Stories:** `docs/epics-integration-addon.md`
- **Transformation Implementation:** `docs/TRANSFORMATION-IMPLEMENTATION-COMPLETE.md`
- **Current Epics:** `docs/epics.md`

---

## Approval Sign-Off

| Role | Name | Date | Approved |
|------|------|------|----------|
| Product Owner | | | ⏳ |
| CORTAP-RPT Tech Lead | | | ⏳ |
| Riskuity Tech Lead | | | ⏳ |
| DevOps Lead | | | ⏳ |
| Security Review | | | ⏳ |

---

**Next Action:** Begin implementing Story 3.6.1 (Generate Report API Endpoint)
