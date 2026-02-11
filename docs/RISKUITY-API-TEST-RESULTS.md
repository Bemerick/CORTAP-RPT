# Riskuity API Test Results

**Date:** 2025-02-10
**Test Account:** `fedrisk_api_ci` (user_id: 0, tenant_id: 0)

---

## ✅ Working Endpoints

### 1. Authentication
**Endpoint:** `POST /users/get-token`
**Status:** ✅ **Working perfectly**

**Request:**
```json
{
  "username": "fedrisk_api_ci",
  "password": "R15ku1tyPa551234!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "status": "SUCCESS"
}
```

**Token Payload:**
- `user_id`: 0
- `email`: "cicd@riskuity.com"
- `tenant_id`: 0
- `is_superuser`: true

---

### 2. List Projects (Tenant-Scoped)
**Endpoint:** `GET /projects/tenant/`
**Status:** ✅ **Working** (returns empty list for test tenant)

**Request:**
```bash
curl -X GET 'https://api.riskuity.com/projects/tenant/' \
  -H 'Authorization: Bearer {token}' \
  -H 'Accept: application/json'
```

**Response (200 OK):**
```json
[]
```

**Notes:**
- Returns 0 projects for the `fedrisk_api_ci` test account
- This is expected - the CI/CD account has no projects
- Endpoint works correctly

---

## ❌ Non-Working / Unclear Endpoints

### 1. GET /projects/
**Status:** ❌ **404 "Invalid value in Parameter"**

**Attempts Made:**
```bash
# Attempt 1: With query params from docs
GET /projects/?offset=0&limit=10&sort_by=name&get_role=false
# Result: 404 {"detail":"Invalid value in Parameter"}

# Attempt 2: Minimal params
GET /projects/?offset=0&limit=10
# Result: 404 {"detail":"Invalid value in Parameter"}

# Attempt 3: No params
GET /projects/
# Result: 404 {"detail":"Invalid value in Parameter"}
```

**Possible Issues:**
1. May require additional parameters not documented
2. May require specific tenant/user context
3. Documentation screenshot shows this endpoint exists, but parameter requirements unclear

---

### 2. GET /assessments/
**Status:** ❌ **500 Internal Server Error**

**Request:**
```bash
GET /assessments/
# Result: 500 (no error details)
```

**Notes:**
- Returns 500 error (server-side issue)
- Endpoint exists but may require project_id parameter
- Need clarification on required parameters

---

### 3. GET /projects/project_controls/{project_id}/
**Status:** ⚠️ **Not tested** (no valid project_id available)

**Next Steps:**
- Need a valid project_id from a real tenant to test
- This endpoint is critical for fetching control assessments

---

## 📋 Summary

### Working ✅
1. **Authentication** - `POST /users/get-token` - Full success
2. **List Tenant Projects** - `GET /projects/tenant/` - Works (returns [])

### Needs Clarification ⚠️
1. **GET /projects/** - 404 "Invalid value in Parameter"
   - Query parameter requirements unclear
   - May need additional context/permissions

2. **GET /assessments/** - 500 Internal Server Error
   - Likely requires project_id parameter
   - Need endpoint structure clarification

3. **GET /projects/project_controls/{project_id}/** - Not tested
   - Need valid project_id with data

---

## 🔧 Recommendations

### For Riskuity Team

1. **Provide test project ID** with actual assessment data
   - The `fedrisk_api_ci` account has 0 projects
   - Need a project with control assessments to test full data flow

2. **Clarify /projects/ endpoint requirements**
   - What are the valid values for `sort_by`?
   - Is `get_role` required? What format (boolean/string)?
   - Any additional required parameters?

3. **Provide API documentation**
   - OpenAPI/Swagger spec would be ideal
   - Or detailed endpoint documentation with:
     - Required vs optional parameters
     - Valid parameter values
     - Example requests/responses

4. **Confirm endpoint structure for assessments**
   - Is it `/assessments/?project_id={id}` or
   - `/projects/project_controls/{project_id}/` or
   - Something else?

### For CORTAP-RPT Implementation

1. **Use `/projects/tenant/` for listing projects**
   - This endpoint works and is properly scoped to the tenant

2. **Authentication is production-ready**
   - Current implementation in `RiskuityClient` should work

3. **Wait for clarification on:**
   - Project controls/assessments endpoint structure
   - Required metadata fields for document generation

---

## 📊 Test Commands

### CI/CD Account (No MFA - No Data)
```bash
python3 scripts/test_riskuity_api.py --list-projects
```

### User Account (With MFA - Real Data)
```bash
# List all projects
python3 scripts/test_riskuity_api.py \
  --username your.email@dot.gov \
  --mfa-code 123456 \
  --list-projects

# Test specific project
python3 scripts/test_riskuity_api.py \
  --username your.email@dot.gov \
  --mfa-code 123456 \
  --project-id 42
```

**Note:** User accounts require MFA. Get the 6-digit code from your authenticator app.

---

## 🔑 Important Update from Riskuity Team

**Date:** 2025-02-10

The `fedrisk_api_ci` account is a CI/CD account with `tenant_id: 0` and no associated data.

**To test with real data:**
1. Use your personal Riskuity account (email)
2. Provide MFA code (6 digits from authenticator app)
3. The JWT token will contain your `tenant_id` and `user_id`
4. Use https://jwt.io/ to decode and inspect JWT tokens

**Reference:** The token that a user gets from the API has the tenant and user ID embedded in the JWT payload.

---

**Test Results Generated:** 2025-02-10
**Tester:** Claude Code (AI Assistant)
**Status:** Authentication working, MFA support added, ready for testing with user account
