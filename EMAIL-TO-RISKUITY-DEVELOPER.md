# Email to Riskuity Developer

---

**Subject:** CORTAP Lambda 401 Error - Solution Found

---

Hi [Developer Name],

Good news! We've identified the issue with the 401 error. The token you're using is a **web session token** (from logging into the Riskuity app), but the Riskuity API requires an **API access token**.

## The Problem

When you ran this test:
```bash
curl -X GET 'https://api.riskuity.com/projects/project_controls/33' \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

You got a 401 error. This confirms your current token isn't valid for API calls - it's a web session token meant for the Riskuity UI.

## The Solution

You need to get an **API access token** from one of these endpoints:

### Quick Test (Service Account - Recommended)

1. Have your admin create a service account: `cortap_report_service`
2. Get a token:
```bash
curl -X POST 'https://api.riskuity.com/users/get-token' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "cortap_report_service",
    "password": "YOUR_PASSWORD"
  }'
```

3. Use that token to test our Lambda:
```bash
curl -X POST 'https://qs5wkdxe8l.execute-api.us-gov-west-1.amazonaws.com/dev/api/v1/generate-report-sync' \
  -H 'Authorization: Bearer <NEW_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{"project_id": 33, "report_type": "draft_audit_report"}'
```

### Alternative (Your User Account with OTP)

If you don't have a service account:

1. Request OTP:
```bash
curl -X POST 'https://api.riskuity.com/users/get-auth-token' \
  -H 'Content-Type: application/json' \
  -d '{"email": "YOUR_EMAIL", "password": "YOUR_PASSWORD"}'
```

2. Check your email for the 6-digit OTP code

3. Get token with OTP:
```bash
curl -X POST 'https://api.riskuity.com/users/get-auth-token' \
  -H 'Content-Type: application/json' \
  -d '{"email": "YOUR_EMAIL", "password": "YOUR_PASSWORD", "otp": "123456"}'
```

## How to Tell if You Have the Right Token

Paste your token into https://jwt.io/

**API Token (correct):**
```json
{
  "tenant_id": 45,     ← Must have this!
  "user_id": 123,
  "email": "..."
}
```

**Web Token (wrong):**
```json
{
  "session_id": "...",  ← No tenant_id
  "user_id": 123
}
```

## For Production

Your backend should generate API tokens before calling our Lambda (not send them from the frontend). I've attached a detailed guide with implementation examples.

Let me know if you need help getting a service account set up, or if you have any questions!

Best,
Bob

---

**Attachments:**
- RISKUITY-DEVELOPER-TOKEN-GUIDE.md (detailed instructions)
- TOKEN-TYPE-MISMATCH-ISSUE.md (technical analysis)
