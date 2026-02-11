# Email to Riskuity Team - Authentication Flow Clarification

---

**Subject:** Need Help with User Authentication Flow (OTP/JWT Token)

---

**To:** Riskuity API Support Team

**From:** Bob Emerick (bob.emerick@longevityconsulting.com)

**Date:** 2025-02-10

---

## Issue Summary

We're successfully implementing the CORTAP-RPT integration with the Riskuity API and need clarification on the complete user authentication flow to obtain a JWT access token with our `tenant_id`.

---

## Current Progress ✅

We've successfully implemented the first two steps of authentication:

### Step 1: Initial Authentication
```bash
curl -X POST 'https://api.riskuity.com/users/get-auth-token' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "email": "bob.emerick@longevityconsulting.com",
    "password": "********"
  }'
```

**Response (200 OK):**
```json
{
  "status": "EMAIL_OTP",
  "delivery": "b***@l***",
  "username": "bobdotemerick@longevityconsultingdotcom"
}
```
✅ **Working** - OTP email received successfully

---

### Step 2: OTP Verification
```bash
curl -X POST 'https://api.riskuity.com/users/get-auth-token' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "email": "bob.emerick@longevityconsulting.com",
    "password": "********",
    "otp": "123456"
  }'
```

**Response (200 OK):**
```json
{
  "status": "EMAIL_OTP",
  "session": "AYABeB2VS_4y3d7F9mgCa4hFjRQAHQABAAdTZXJ2aWNl...[truncated]",
  "delivery": "b***@l***",
  "username": "bobdotemerick@longevityconsultingdotcom"
}
```
✅ **Working** - OTP verified, session token received

---

## Problem ❌

After Step 2, we receive a `session` token, but the response still shows `"status": "EMAIL_OTP"` and **does not contain an `access_token` or JWT token**.

We've tried:

### Step 3 Attempt: Session Exchange
```bash
curl -X POST 'https://api.riskuity.com/users/get-auth-token' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "email": "bob.emerick@longevityconsulting.com",
    "password": "********",
    "session": "AYABeB2VS_4y3d7F9mgCa4hFjRQ..."
  }'
```

**Response:** Still returns `"status": "EMAIL_OTP"` with a new session token, but **no access_token**.

---

## What We Need 🙏

### 1. Complete Authentication Flow Documentation

Could you please provide the **complete step-by-step flow** to obtain a JWT access token for a user account with OTP enabled?

Specifically:
- What endpoint should we call after receiving the `session` token in Step 2?
- What payload/headers are required?
- What field name contains the final JWT access token?

### 2. Working Example

A complete working `curl` example showing all steps from email/password → OTP → final JWT token would be extremely helpful.

### 3. Expected Response Format

What does the final successful authentication response look like? We're expecting:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "status": "SUCCESS"
}
```

Is this correct?

---

## Context & Background

Per your earlier guidance, we understand that:
- ✅ The JWT token contains `tenant_id` and `user_id` in the payload
- ✅ We can use the token with endpoints like `GET /projects/tenant/` to retrieve our projects
- ✅ The CI/CD account (`fedrisk_api_ci`) has `tenant_id: 0` with no data (working as expected)
- ✅ We need to authenticate with my user account to get a real `tenant_id` for testing

We've successfully tested the `/users/get-token` endpoint with the CI/CD account, and the JWT token works perfectly. We just need to understand the complete flow for user accounts with OTP.

---

## Testing Script

We've built a comprehensive test script that handles:
- Two-step OTP authentication
- JWT token decoding
- Project listing from `/projects/tenant/`

Once we understand the complete authentication flow, we'll be ready to test the full integration with real project data.

---

## Current Implementation Status

- ✅ Epic 5.2: S3 Integration (54 tests passing)
- ✅ Epic 3.5: Riskuity Data Service (code complete)
- ⚠️ Epic 3.5: Testing with real Riskuity data (blocked on authentication flow)

---

## Request

Could you please:

1. **Document the complete authentication flow** for user accounts with OTP
2. **Provide a working curl example** showing all steps
3. **Confirm the response format** for the final JWT token
4. Alternatively, if easier: **Provide a test JWT token** with a real `tenant_id` that we can use for development/testing

---

## Additional Notes

We've encountered AWS Cognito rate limiting during testing (expected security behavior), so we're being careful with authentication attempts. Any guidance to help us get it right on the first try would be appreciated!

---

## Thank You

Thanks for your help with this integration. The API documentation and support have been excellent so far, and we're excited to complete this integration.

Please let me know if you need any additional information or if there's a better way to reach the API support team.

**Best regards,**

**Bob Emerick**
Senior Consultant
Longevity Consulting
bob.emerick@longevityconsulting.com

---

**CC:** CORTAP Development Team

---

## Attachments

- Test script: `scripts/test_riskuity_api.py`
- API test results: `docs/RISKUITY-API-TEST-RESULTS.md`
- Authentication guide: `docs/RISKUITY-AUTHENTICATION-GUIDE.md`

---

**Status:** Awaiting Riskuity team response
**Priority:** High - Blocking Epic 3.5 testing
**Expected Response Time:** 1-2 business days
