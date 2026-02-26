# Authentication Architecture Analysis

## Current Error

**Error Message:**
```json
{
  "detail": "External service error: {\"message\":\"Invalid key=value pair (missing equal-sign) in Authorization header (hashed with SHA-256 and encoded with Base64): '2RqT0sijwVut76+1Vg2t5Q3AItgot3yafHlHlipThlY='.\"}"
}
```

**HTTP Status:** 401 Unauthorized

## Root Cause Analysis

The error message `"Invalid key=value pair (missing equal-sign) in Authorization header"` is **NOT** from Riskuity API. This is an **AWS API Gateway error** that occurs when:

1. AWS API Gateway receives a `Bearer` token in the Authorization header
2. AWS tries to parse it as an AWS Signature V4 header (which uses key=value pairs)
3. The Bearer token doesn't match the expected AWS signature format
4. AWS rejects the request before it even reaches the Lambda function

## Current Architecture

### What We Built (Correct Approach)

```
┌─────────────────┐
│ Riskuity User   │
│ (Authenticated) │
└────────┬────────┘
         │ 1. POST with Bearer token
         │    Authorization: Bearer <riskuity-jwt-token>
         ▼
┌─────────────────┐
│ API Gateway     │  ❌ PROBLEM: Trying to validate token
│ (AWS GovCloud)  │     as AWS Signature V4
└────────┬────────┘
         │ Should pass through to Lambda
         ▼
┌─────────────────┐
│ Lambda Function │
│ - Receives token│  ✅ CORRECT: Uses token for Riskuity API
│ - Calls Riskuity│
│   with token    │
└─────────────────┘
```

### Lambda Code (Working Correctly)

**File:** `app/api/v1/endpoints/generate.py:157-179`

```python
# Extract Bearer token from Authorization header
token = authorization.replace("Bearer ", "").strip()

# Pass token to Riskuity client
riskuity_client = RiskuityClient(
    base_url=settings.riskuity_base_url,
    api_key=token,  # ✅ Uses the passed token
    http_client=http_client
)

# Make Riskuity API call with user's token
project_controls = await riskuity_client.get_project_controls(
    project_id=request.project_id
)
```

**File:** `app/services/riskuity_client.py:100`

```python
headers = {
    "Authorization": f"Bearer {self.api_key}",  # ✅ Passes token to Riskuity
    "Accept": "application/json"
}
```

The Lambda code is **correct**. It:
1. ✅ Receives the Bearer token from the caller
2. ✅ Passes it directly to Riskuity API
3. ✅ Does NOT attempt MFA authentication

## The Problem: API Gateway Configuration

**File:** `template.yaml:175-176`

```yaml
Auth:
  DefaultAuthorizer: NONE
```

This should work, but AWS API Gateway in GovCloud may be interpreting the Authorization header differently.

## Why AWS is Rejecting the Token

AWS API Gateway has **two authentication modes**:

### 1. AWS IAM Authorization (What's Happening Now)
- API Gateway sees the Authorization header
- Assumes it's an AWS Signature V4 (used for AWS service calls)
- Tries to parse: `AWS4-HMAC-SHA256 Credential=..., SignedHeaders=..., Signature=...`
- Fails because it receives: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- Returns 401 error before Lambda is invoked

### 2. Custom/Lambda Authorizer (What We Need)
- API Gateway passes Authorization header through to Lambda
- Lambda handles authentication validation
- Works with any token format (Bearer, JWT, etc.)

## Solutions

### Option 1: Add Lambda Authorizer (Recommended for Production)

**Pros:**
- ✅ Validates Riskuity token at API Gateway layer
- ✅ Returns 401 before invoking Lambda (saves costs)
- ✅ Can cache authorization decisions (5 minutes default)
- ✅ Standard AWS pattern for external auth

**Cons:**
- ⚠️  Requires additional Lambda function (authorizer)
- ⚠️  Additional complexity

**Implementation:**

```yaml
# template.yaml

Resources:
  # Lambda Authorizer Function
  TokenAuthorizerFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub cortap-token-authorizer-${Environment}
      CodeUri: .
      Handler: app.authorizers.token_authorizer.lambda_handler
      Runtime: python3.11
      Environment:
        Variables:
          RISKUITY_BASE_URL: !Ref RiskuityApiUrl

  # API Gateway with Custom Authorizer
  GenerateReportApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: !Ref Environment
      Auth:
        DefaultAuthorizer: RiskuityTokenAuthorizer
        Authorizers:
          RiskuityTokenAuthorizer:
            FunctionArn: !GetAtt TokenAuthorizerFunction.Arn
            FunctionPayloadType: REQUEST  # Pass full request to authorizer
            Identity:
              Headers:
                - Authorization
              ReauthorizeEvery: 300  # Cache for 5 minutes
```

**Authorizer Function:**

```python
# app/authorizers/token_authorizer.py

def lambda_handler(event, context):
    """
    Validate Riskuity Bearer token.

    Returns IAM policy allowing/denying access to API Gateway.
    """
    token = event['headers'].get('authorization', '').replace('Bearer ', '')

    if not token:
        raise Exception('Unauthorized')  # 401

    # Optional: Validate token with Riskuity
    # For now, just check format (JWT structure: xxx.yyy.zzz)
    if token.count('.') != 2:
        raise Exception('Unauthorized')

    # Return IAM policy allowing access
    return {
        'principalId': 'riskuity-user',
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': 'Allow',
                'Resource': event['methodArn']
            }]
        },
        'context': {
            'token': token  # Pass token to Lambda in context
        }
    }
```

### Option 2: Use AWS_IAM with Resource Policy (Workaround)

Allow public access but let Lambda handle auth:

```yaml
GenerateReportApi:
  Type: AWS::Serverless::Api
  Properties:
    StageName: !Ref Environment
    Auth:
      DefaultAuthorizer: NONE
      ResourcePolicy:
        CustomStatements:
          - Effect: Allow
            Principal: '*'
            Action: execute-api:Invoke
            Resource: execute-api:/*/*/*
```

**Status:** This should already work with current `DefaultAuthorizer: NONE`, but GovCloud may have different behavior.

### Option 3: Remove Authorization Header from API Gateway (Quick Test)

Test if Lambda works by having Riskuity pass the token in a **custom header**:

**Riskuity Developer Changes:**
```javascript
// Instead of:
headers: {
  'Authorization': 'Bearer abc123'
}

// Use:
headers: {
  'X-Riskuity-Token': 'abc123'  // Without "Bearer " prefix
}
```

**Lambda Code Changes:**
```python
# app/api/v1/endpoints/generate.py:140-145

# Get token from custom header instead of Authorization
token = request.headers.get('x-riskuity-token')
if not token:
    raise HTTPException(status_code=401, detail="Token required")
```

**Pros:**
- ✅ Quick test to verify Lambda works
- ✅ Bypasses API Gateway auth parsing
- ✅ No infrastructure changes

**Cons:**
- ❌ Non-standard authentication approach
- ❌ Temporary workaround only

### Option 4: Use HTTP API instead of REST API (Best Option)

AWS HTTP APIs have better support for custom auth and Bearer tokens:

```yaml
GenerateReportApi:
  Type: AWS::Serverless::HttpApi  # Changed from Api to HttpApi
  Properties:
    StageName: !Ref Environment
    CorsConfiguration:
      AllowOrigins:
        - !Ref AllowedOrigins
      AllowHeaders:
        - Authorization
        - Content-Type
      AllowMethods:
        - POST
        - OPTIONS
    # HTTP APIs don't parse Authorization headers by default
```

**Pros:**
- ✅ Simpler than REST API
- ✅ Doesn't parse Authorization header as AWS SigV4
- ✅ Lower cost (70% cheaper than REST API)
- ✅ Better performance

**Cons:**
- ⚠️  Different event format (already handled in our Lambda)
- ⚠️  Requires redeployment

## Recommended Solution

### Immediate (Quick Fix): Option 3 - Custom Header Test

Have Riskuity developer test with `X-Riskuity-Token` header to verify Lambda works.

### Short Term (1-2 days): Option 4 - HTTP API Migration

Migrate from REST API to HTTP API for proper Bearer token support.

### Long Term (Production): Option 1 - Lambda Authorizer

Add token validation at API Gateway layer for security and cost optimization.

## Testing the Current Setup

### Check if Lambda is Being Invoked

```bash
# Check CloudWatch logs
aws logs tail /aws/lambda/cortap-generate-report-sync-dev \
  --profile govcloud-mfa \
  --region us-gov-west-1 \
  --follow
```

**If you see logs:** Lambda is being invoked (Option 3 or 4 will work)
**If no logs:** API Gateway is blocking before Lambda (need Option 1, 2, or 4)

### Test with Custom Header (Quick Validation)

```bash
# Have Riskuity developer try this:
curl -X POST https://[api-gateway-url]/dev/api/v1/generate-report-sync \
  -H "Content-Type: application/json" \
  -H "X-Riskuity-Token: [their-token-without-Bearer]" \
  -d '{"project_id": 33, "report_type": "draft_audit_report"}'
```

## Current Code Status

**✅ Lambda Code: CORRECT**
- Properly extracts Bearer token
- Passes token to Riskuity API
- No MFA authentication attempted

**❌ API Gateway: BLOCKING REQUESTS**
- Interpreting Authorization header as AWS SigV4
- Rejecting valid Bearer tokens
- Preventing Lambda invocation

## Next Steps

1. **Immediate:** Ask Riskuity developer to check if requests are reaching Lambda (CloudWatch logs)
2. **Quick Test:** Try custom header (`X-Riskuity-Token`) to verify Lambda works
3. **Fix:** Migrate to HTTP API or implement Lambda Authorizer
4. **Validate:** End-to-end test with actual Riskuity Bearer token

---

**Date:** 2026-02-26
**Status:** Analysis Complete - Awaiting Implementation Decision
