# Riskuity API Authentication Guide

**Last Updated:** 2025-02-10

---

## Overview

Riskuity API uses a two-step authentication process for user accounts with email OTP verification.

---

## Authentication Endpoints

### User Accounts (Email OTP)
**Endpoint:** `POST /users/get-auth-token`

### Service Accounts (No OTP)
**Endpoint:** `POST /users/get-token`

---

## User Authentication Flow (Two-Step)

### Step 1: Initial Authentication

**Request:**
```bash
curl -X POST 'https://api.riskuity.com/users/get-auth-token' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "email": "user@example.com",
    "password": "your-password"
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

**Status Codes:**
- `EMAIL_OTP` - Email verification required (check your email for OTP code)
- Other statuses TBD

---

### Step 2: OTP Verification

After receiving the OTP code via email, submit it along with your credentials:

**Request:**
```bash
curl -X POST 'https://api.riskuity.com/users/get-auth-token' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{
    "email": "user@example.com",
    "password": "your-password",
    "otp": "123456"
  }'
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "status": "SUCCESS"
}
```

---

## JWT Token Structure

The access token is a JWT (JSON Web Token) that contains:

```json
{
  "user_id": 123,
  "tenant_id": 45,
  "email": "user@example.com",
  "is_superuser": false,
  "exp": 1234567890
}
```

**Key Fields:**
- `tenant_id` - Your organization's tenant identifier (required for API calls)
- `user_id` - Your user identifier
- `email` - Your email address
- `exp` - Token expiration timestamp

**Decode at:** https://jwt.io/

---

## Service Account Authentication (CI/CD)

Service accounts use a different endpoint without OTP:

**Request:**
```bash
curl -X POST 'https://api.riskuity.com/users/get-token' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "fedrisk_api_ci",
    "password": "service-account-password"
  }'
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "status": "SUCCESS"
}
```

**Note:** Service accounts typically have `tenant_id: 0` and no project data.

---

## Using the Test Script

### Prerequisites
```bash
pip install httpx python-dotenv
```

### User Account (with OTP)

**Step 1: Trigger OTP Email**
```bash
python3 scripts/test_riskuity_api.py \
  --username your.email@example.com \
  --password 'your-password' \
  --list-projects
```

**Output:**
```
⚠️  OTP required! Check your b***@e*** for the verification code.
   Run again with: --mfa-code YOUR_CODE
```

**Step 2: Authenticate with OTP**
Check your email for the 6-digit OTP code, then:

```bash
python3 scripts/test_riskuity_api.py \
  --username your.email@example.com \
  --password 'your-password' \
  --mfa-code 123456 \
  --list-projects
```

**Expected Output:**
```
✅ Authentication successful!

📋 Token Information:
   User ID: 123
   Tenant ID: 45
   Email: your.email@example.com
   Is Superuser: false

✅ Successfully fetched projects!
   Count: 5
```

### Service Account (No OTP)

```bash
export RISKUITY_USERNAME="fedrisk_api_ci"
export RISKUITY_PASSWORD="your-password"

python3 scripts/test_riskuity_api.py --list-projects
```

---

## Rate Limiting

AWS Cognito (used by Riskuity) enforces rate limits:

- **Limit:** ~5 failed attempts
- **Lockout Duration:** 15-30 minutes
- **Error Message:** `"Attempt limit exceeded, please try after some time"`

**Best Practice:** Wait 30 minutes after hitting rate limit before retrying.

---

## Common Issues

### Issue: "string indices must be integers, not 'str'"
**Cause:** Using wrong endpoint or wrong field names
**Solution:** Use `/users/get-auth-token` with `email` field (not `username`)

### Issue: "Method Not Allowed" (405)
**Cause:** Missing trailing slash or wrong HTTP method
**Solution:** Ensure endpoint has correct format

### Issue: "field required" (422)
**Cause:** Missing required fields in request body
**Solution:** Check that all required fields are present:
- Step 1: `email`, `password`
- Step 2: `email`, `password`, `otp`

### Issue: Rate Limited (401)
**Cause:** Too many authentication attempts
**Solution:** Wait 30 minutes before retrying

---

## API Integration Example

```python
import httpx
import json

async def authenticate(email: str, password: str, otp: str = None):
    """Authenticate with Riskuity API."""
    url = "https://api.riskuity.com/users/get-auth-token"

    # Step 1: Initial auth
    payload = {"email": email, "password": password}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        data = response.json()

        if data.get("status") == "EMAIL_OTP":
            if not otp:
                raise Exception("OTP required - check your email")

            # Step 2: Submit OTP
            payload["otp"] = otp
            response = await client.post(url, json=payload)
            data = response.json()

        return data.get("access_token")
```

---

## Next Steps

1. ✅ Authentication working with two-step OTP flow
2. 🔜 Test with real tenant data (after rate limit resets)
3. 🔜 Implement project listing with `/projects/tenant/`
4. 🔜 Implement assessment fetching with `/projects/project_controls/{id}/`
5. 🔜 Update `RiskuityClient` service with correct authentication flow

---

**Documentation Status:** ✅ Complete
**Testing Status:** ⚠️ Waiting for rate limit to reset
**Production Ready:** 🔜 After successful testing with real tenant data
