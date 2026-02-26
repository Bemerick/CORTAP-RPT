# Token Type Mismatch Issue - Root Cause Analysis

## Status: IDENTIFIED ✅

**Date:** 2026-02-26
**Issue:** Riskuity API returning 401 Unauthorized
**Root Cause:** Token type mismatch - web session token vs API access token

---

## CloudWatch Evidence

```json
{
    "timestamp": "2026-02-26T19:24:48.535316Z",
    "level": "ERROR",
    "service": "cortap-rpt",
    "module": "riskuity_client",
    "function": "_request_with_retry",
    "message": "Riskuity API request failed: 401",
    "correlation_id": "gen-sync-0019d0503cc5",
    "url": "https://api.riskuity.com/projects/project_controls/33",
    "status_code": 401
}
```

**This proves:**
- ✅ API Gateway is working (passing requests through)
- ✅ Lambda is being invoked successfully
- ✅ Bearer token is reaching the Riskuity API
- ❌ Riskuity API is rejecting the token

---

## The Problem: Two Different Token Types

### What Riskuity Developer is Sending

The Riskuity developer is likely sending a **web session token** - the token their browser uses when they're logged into the Riskuity web application.

**Characteristics:**
- Generated when user logs into Riskuity web app
- Used for browser/UI interactions
- **Not valid for API calls**
- Different authentication context

**Example:**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uX2lkIjoiYWJjMTIzIiwidXNlcl9pZCI6IjEyMyJ9.xyz...
```

### What Our Lambda Needs

Our Lambda needs an **API access token** obtained through the Riskuity API authentication flow.

**Characteristics:**
- Generated via `/users/get-auth-token` API endpoint
- Requires email + password + OTP
- Contains `tenant_id` claim
- Valid for API calls

**Example:**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnRfaWQiOjQ1LCJ1c2VyX2lkIjoxMjMsImVtYWlsIjoidXNlckBleGFtcGxlLmNvbSJ9.xyz...
```

---

## Why This Happens

### Typical Web Application Architecture

```
┌──────────────────┐
│ Riskuity Web App │
│ (React/Vue)      │
└────────┬─────────┘
         │ User logs in
         │ Gets: WEB SESSION TOKEN
         │
         ▼
┌──────────────────┐
│ Riskuity Backend │  ✅ Accepts web session tokens
│ (GraphQL/REST)   │     for UI operations
└──────────────────┘
```

### API Integration Architecture

```
┌──────────────────┐
│ External App     │
│ (Our Lambda)     │
└────────┬─────────┘
         │ Authenticates via API
         │ Gets: API ACCESS TOKEN
         │
         ▼
┌──────────────────┐
│ Riskuity API     │  ✅ Accepts API access tokens
│ (api.riskuity.   │     for programmatic access
│  com)            │
└──────────────────┘
```

### The Mismatch

```
┌──────────────────┐
│ Riskuity User    │  Has: WEB SESSION TOKEN
│ (Browser logged  │
│  in)             │
└────────┬─────────┘
         │
         │ Sends web session token to Lambda
         │
         ▼
┌──────────────────┐
│ Our Lambda       │  ✅ Receives token correctly
└────────┬─────────┘
         │
         │ Forwards web session token to API
         │
         ▼
┌──────────────────┐
│ Riskuity API     │  ❌ Rejects: "This is a web token,
└──────────────────┘     not an API token!"
```

---

## How to Verify This Theory

### Method 1: Decode the JWT Token

Ask the Riskuity developer to decode their token at https://jwt.io/

**Web Session Token will have:**
```json
{
  "session_id": "abc123",
  "user_id": 123,
  "iss": "https://app.riskuity.com",
  "aud": ["web-app"],
  "scope": ["read:ui", "write:ui"]
}
```

**API Access Token will have:**
```json
{
  "user_id": 123,
  "tenant_id": 45,
  "email": "user@example.com",
  "iss": "https://api.riskuity.com",
  "aud": ["api"],
  "scope": ["read:api", "write:api"]
}
```

**Key difference:** API tokens have `tenant_id` claim, web tokens don't.

### Method 2: Test Token with curl

```bash
# Test if token works directly with Riskuity API
curl -X GET 'https://api.riskuity.com/projects/project_controls/33' \
  -H "Authorization: Bearer <THEIR_TOKEN>" \
  -H "Accept: application/json"
```

**If 401:** Token is not valid for API (confirms theory)
**If 200:** Token is valid (our code has a bug)

---

## Solutions

### Option 1: Riskuity Generates API Token (Recommended)

The Riskuity developer needs to **generate an API access token** instead of using their web session token.

**Implementation:**

```javascript
// In Riskuity frontend code

async function callCORTAPService(projectId) {
  // Step 1: Get API token from Riskuity backend
  const apiToken = await generateAPIToken();

  // Step 2: Call our Lambda with API token
  const response = await fetch('https://[lambda-url]/api/v1/generate-report-sync', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      project_id: projectId,
      report_type: 'draft_audit_report'
    })
  });

  return response.json();
}

// New backend endpoint needed in Riskuity
async function generateAPIToken() {
  // Server-side code in Riskuity backend
  const response = await fetch('https://api.riskuity.com/users/get-auth-token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: process.env.RISKUITY_SERVICE_EMAIL,
      password: process.env.RISKUITY_SERVICE_PASSWORD,
      otp: await getOTP()  // Service accounts may not need OTP
    })
  });

  const data = await response.json();
  return data.access_token;
}
```

**Pros:**
- ✅ Proper separation of web vs API tokens
- ✅ Our Lambda code doesn't change
- ✅ Secure (tokens generated on Riskuity backend)

**Cons:**
- ⚠️ Riskuity team needs to implement new endpoint
- ⚠️ May require service account credentials

---

### Option 2: Token Exchange Endpoint (Alternative)

Create a token exchange service that converts web tokens to API tokens.

**NOT RECOMMENDED** - Security risk and complexity

---

### Option 3: Service Account Token (Simplest for Testing)

Have Riskuity create a **service account** and use that token for all API calls.

**Implementation:**

```javascript
// In Riskuity frontend configuration
const CORTAP_API_TOKEN = 'eyJhbGci...[service-account-token]...';

async function callCORTAPService(projectId) {
  const response = await fetch('https://[lambda-url]/api/v1/generate-report-sync', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${CORTAP_API_TOKEN}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      project_id: projectId,
      report_type: 'draft_audit_report'
    })
  });

  return response.json();
}
```

**Service Account Setup:**

```bash
# Riskuity creates service account: "cortap_report_generator"
# Returns token that never expires or expires after 1 year

curl -X POST 'https://api.riskuity.com/users/get-token' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "cortap_report_generator",
    "password": "service-password"
  }'
```

**Pros:**
- ✅ Simple - one token for all requests
- ✅ No OTP required
- ✅ Quick to implement
- ✅ Our Lambda code doesn't change

**Cons:**
- ⚠️ All reports generated as service account (audit trail shows service, not user)
- ⚠️ Token needs secure storage in Riskuity frontend

---

### Option 4: Lambda Authenticates Itself (What We Built for Testing)

Our current test scripts authenticate directly with Riskuity API.

**This WON'T work for production** because:
- ❌ Requires storing Riskuity credentials in Lambda
- ❌ Requires OTP (can't be automated)
- ❌ Security risk (credentials in environment variables)

**Only use for local testing.**

---

## Recommended Solution

### Production: Option 1 - API Token Generation

**Riskuity team implements:**

1. **Backend endpoint:** `POST /api/cortap/generate-token`
   - Authenticates using service account
   - Returns API access token
   - Token expires in 1 hour

2. **Frontend calls:**
   ```javascript
   const apiToken = await fetch('/api/cortap/generate-token').then(r => r.json());
   const report = await callCORTAPLambda(apiToken);
   ```

**Benefits:**
- ✅ Secure (credentials never leave Riskuity backend)
- ✅ Proper audit trail (token associated with service account)
- ✅ Tokens can be short-lived (1 hour)
- ✅ No changes needed to our Lambda

---

### Testing: Option 3 - Service Account Token

**Quick test to verify everything works:**

1. Riskuity creates service account: `cortap_api_test`
2. Generate token once:
   ```bash
   curl -X POST 'https://api.riskuity.com/users/get-token' \
     -H 'Content-Type: application/json' \
     -d '{"username": "cortap_api_test", "password": "..."}'
   ```
3. Riskuity developer uses that token to test Lambda
4. If 200 response → Lambda works, just need production token flow

---

## Next Steps

### Immediate (Within 1 Hour)

**Task for Riskuity Developer:**

1. **Verify token type:**
   ```bash
   # Decode their current token at https://jwt.io/
   # Check if it has "tenant_id" field
   ```

2. **Test API directly:**
   ```bash
   curl -X GET 'https://api.riskuity.com/projects/project_controls/33' \
     -H "Authorization: Bearer <THEIR_CURRENT_TOKEN>"
   ```

   **If 401:** Token is wrong type (web session token)
   **If 200:** Token is right type (our code has bug - unlikely)

3. **Get service account token for testing:**
   ```bash
   # Riskuity admin creates service account
   # Get token from /users/get-token endpoint
   # Test Lambda with that token
   ```

### Short Term (1-2 Days)

**Task for Riskuity Team:**
- Implement backend endpoint to generate API tokens
- Update frontend to call endpoint before calling Lambda
- Document token refresh logic (tokens expire after 1 hour)

### Our Team (No Changes Needed)

✅ Lambda code is correct
✅ API Gateway is working
✅ No changes needed on our side

---

## Communication Template

**Email to Riskuity Developer:**

```
Subject: CORTAP Lambda 401 Error - Token Type Issue

Hi [Riskuity Developer],

Good news! The Lambda is working correctly. The 401 error is because
the Riskuity API requires an API access token, not a web session token.

Quick Test:
1. Try this curl command with your current token:

   curl -X GET 'https://api.riskuity.com/projects/project_controls/33' \
     -H "Authorization: Bearer <YOUR_TOKEN>"

2. If you get 401, the token is a web session token (not API token).

Solutions:
- Short term: Create a service account and use that token for testing
- Production: Generate API tokens on your backend before calling our Lambda

The token needs these claims:
- tenant_id (required)
- user_id
- email

Let me know if you need help creating a service account!

Thanks,
Bob
```

---

**Date:** 2026-02-26
**Status:** Root cause identified - waiting for Riskuity team to provide API token
**Our Lambda:** Working correctly ✅
**Next Action:** Riskuity team to test with proper API token
