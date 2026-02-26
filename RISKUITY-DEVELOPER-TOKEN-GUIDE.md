# Token Guide for Riskuity Developer

## The Issue ✅ CONFIRMED

Your current token gives a 401 error when calling the Riskuity API directly. This confirms the token is a **web session token**, not an **API access token**.

```bash
# This returns 401
curl -X GET 'https://api.riskuity.com/projects/project_controls/33' \
  -H "Authorization: Bearer <YOUR_CURRENT_TOKEN>"
```

**Why:** The Riskuity API requires an API access token obtained through the authentication endpoints.

---

## Quick Solution: Get an API Token

You have **3 options** to get a valid API token:

---

## Option 1: Service Account Token (RECOMMENDED FOR TESTING)

**Best for:** Quick testing to verify the CORTAP Lambda works

### Step 1: Create Service Account

Ask your Riskuity admin to create a service account:
- Username: `cortap_report_service` (or similar)
- Purpose: Programmatic API access for CORTAP report generation
- Permissions: Read access to projects and controls

### Step 2: Get Token

```bash
curl -X POST 'https://api.riskuity.com/users/get-token' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "cortap_report_service",
    "password": "YOUR_SERVICE_ACCOUNT_PASSWORD"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "status": "SUCCESS"
}
```

### Step 3: Test Token

```bash
# Save the token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Test Riskuity API
curl -X GET 'https://api.riskuity.com/projects/project_controls/33' \
  -H "Authorization: Bearer $TOKEN"

# If 200 response, test CORTAP Lambda
curl -X POST 'https://qs5wkdxe8l.execute-api.us-gov-west-1.amazonaws.com/dev/api/v1/generate-report-sync' \
  -H 'Authorization: Bearer '$TOKEN \
  -H 'Content-Type: application/json' \
  -d '{
    "project_id": 33,
    "report_type": "draft_audit_report"
  }'
```

**✅ If this works:** CORTAP Lambda is fully functional! You just need to implement production token flow.

---

## Option 2: User Account Token with OTP (FOR TESTING)

**Best for:** Testing with your personal account

### Step 1: Trigger OTP Email

```bash
curl -X POST 'https://api.riskuity.com/users/get-auth-token' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "your.email@example.com",
    "password": "YOUR_PASSWORD"
  }'
```

**Response:**
```json
{
  "status": "EMAIL_OTP",
  "delivery": "y***@e***",
  "username": "yourdotemailatelexampledotcom"
}
```

### Step 2: Check Email for OTP

Check your email for a 6-digit OTP code.

### Step 3: Get Token with OTP

```bash
curl -X POST 'https://api.riskuity.com/users/get-auth-token' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "your.email@example.com",
    "password": "YOUR_PASSWORD",
    "otp": "123456"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "status": "SUCCESS"
}
```

### Step 4: Test Token

Use the same test commands from Option 1, Step 3.

**Note:** This token expires after ~1 hour.

---

## Option 3: Backend Token Generation (FOR PRODUCTION)

**Best for:** Production implementation

Your Riskuity backend needs to generate API tokens before calling the CORTAP Lambda.

### Architecture

```
┌─────────────────┐
│ Riskuity User   │
│ (Web Browser)   │
└────────┬────────┘
         │ 1. Click "Generate Report"
         │
         ▼
┌─────────────────┐
│ Riskuity        │  2. Generate API token
│ Backend         │     (using service account)
│ (Node/Python)   │
└────────┬────────┘
         │ 3. Call CORTAP Lambda
         │    Authorization: Bearer <API_TOKEN>
         │
         ▼
┌─────────────────┐
│ CORTAP Lambda   │  4. Generate report
│ (AWS GovCloud)  │
└─────────────────┘
```

### Implementation Example (Node.js)

```javascript
// Riskuity Backend - New Endpoint
app.post('/api/cortap/generate-report', async (req, res) => {
  const { projectId } = req.body;

  try {
    // Step 1: Get API token (service account)
    const tokenResponse = await fetch('https://api.riskuity.com/users/get-token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: process.env.CORTAP_SERVICE_USERNAME,
        password: process.env.CORTAP_SERVICE_PASSWORD
      })
    });

    const { access_token } = await tokenResponse.json();

    // Step 2: Call CORTAP Lambda with API token
    const reportResponse = await fetch(
      'https://qs5wkdxe8l.execute-api.us-gov-west-1.amazonaws.com/dev/api/v1/generate-report-sync',
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${access_token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          project_id: projectId,
          report_type: 'draft_audit_report'
        })
      }
    );

    const report = await reportResponse.json();

    // Step 3: Return download URL to frontend
    res.json({
      download_url: report.download_url,
      report_id: report.report_id
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

### Frontend Code

```javascript
// Riskuity Frontend
async function generateCORTAPReport(projectId) {
  // Call your backend, which handles token generation
  const response = await fetch('/api/cortap/generate-report', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ projectId })
  });

  const { download_url, report_id } = await response.json();

  // Open download URL in new tab
  window.open(download_url, '_blank');
}
```

**Pros:**
- ✅ Secure (credentials never in frontend)
- ✅ Service account credentials stored safely in backend env vars
- ✅ Can implement token caching (1 hour expiry)
- ✅ Proper audit trail

---

## What Token Type Do You Have?

### Decode Your Current Token

Go to https://jwt.io/ and paste your current token.

**Web Session Token looks like:**
```json
{
  "session_id": "abc123",
  "user_id": 123,
  "exp": 1234567890,
  "iss": "https://app.riskuity.com"
}
```
❌ **Missing `tenant_id`** - Won't work with API

**API Access Token looks like:**
```json
{
  "user_id": 123,
  "tenant_id": 45,
  "email": "user@example.com",
  "exp": 1234567890,
  "iss": "https://api.riskuity.com"
}
```
✅ **Has `tenant_id`** - Will work with API

---

## Testing Checklist

### ☐ Step 1: Get API Token

Use Option 1 (service account) or Option 2 (user OTP).

**Verify token:**
```bash
# Should have tenant_id claim
echo "<YOUR_TOKEN>" | base64 -d
```

### ☐ Step 2: Test Riskuity API

```bash
curl -X GET 'https://api.riskuity.com/projects/project_controls/33' \
  -H "Authorization: Bearer <YOUR_NEW_TOKEN>"
```

**Expected:** 200 response with project controls

### ☐ Step 3: Test CORTAP Lambda

```bash
curl -X POST 'https://qs5wkdxe8l.execute-api.us-gov-west-1.amazonaws.com/dev/api/v1/generate-report-sync' \
  -H 'Authorization: Bearer <YOUR_NEW_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{
    "project_id": 33,
    "report_type": "draft_audit_report"
  }'
```

**Expected:** 200 response with download URL

**Response:**
```json
{
  "report_id": "rpt-20260226-123456-abc123",
  "status": "completed",
  "download_url": "https://s3.amazonaws.com/...",
  "generated_at": "2026-02-26T12:34:56Z",
  "expires_at": "2026-02-27T12:34:56Z",
  "metadata": {
    "recipient": "Seattle",
    "review_type": "Triennial Review",
    "generation_time_ms": 10000
  }
}
```

### ☐ Step 4: Download Report

```bash
# Download the generated report
curl -o report.docx "<DOWNLOAD_URL>"

# Verify it's a valid Word document
file report.docx
# Output: report.docx: Microsoft Word 2007+
```

---

## Common Errors

### Error: "Invalid credentials"
**Cause:** Wrong username/password for service account
**Solution:** Verify credentials with Riskuity admin

### Error: "OTP required"
**Cause:** User account requires OTP, not service account
**Solution:** Use `/users/get-auth-token` with OTP or create service account

### Error: "Rate limited"
**Cause:** Too many authentication attempts
**Solution:** Wait 15-30 minutes before retrying

### Error: 401 from Riskuity API
**Cause:** Token is still wrong type or expired
**Solution:**
1. Decode token at jwt.io - verify it has `tenant_id`
2. Check token hasn't expired (`exp` claim)
3. Regenerate token if needed

### Error: 401 from CORTAP Lambda
**Cause:** Token not in correct format
**Solution:** Ensure `Authorization: Bearer <TOKEN>` header (with space after "Bearer")

---

## Quick Reference

### Service Account Token (No OTP)
```bash
curl -X POST 'https://api.riskuity.com/users/get-token' \
  -H 'Content-Type: application/json' \
  -d '{"username": "SERVICE_ACCOUNT", "password": "PASSWORD"}'
```

### User Token (With OTP)
```bash
# Step 1: Trigger OTP
curl -X POST 'https://api.riskuity.com/users/get-auth-token' \
  -H 'Content-Type: application/json' \
  -d '{"email": "EMAIL", "password": "PASSWORD"}'

# Step 2: Submit OTP (check email for code)
curl -X POST 'https://api.riskuity.com/users/get-auth-token' \
  -H 'Content-Type: application/json' \
  -d '{"email": "EMAIL", "password": "PASSWORD", "otp": "123456"}'
```

### Test CORTAP Lambda
```bash
curl -X POST 'https://qs5wkdxe8l.execute-api.us-gov-west-1.amazonaws.com/dev/api/v1/generate-report-sync' \
  -H 'Authorization: Bearer <TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{"project_id": 33, "report_type": "draft_audit_report"}'
```

---

## Need Help?

**Questions?** Contact Bob Emerick (CORTAP team)

**Issues?**
1. Share the error message
2. Share curl command used (WITHOUT the token)
3. Share decoded token claims (without sensitive data)

---

**Date:** 2026-02-26
**Status:** Token issue identified - waiting for proper API token
**Next Step:** Get service account token or user token with OTP
