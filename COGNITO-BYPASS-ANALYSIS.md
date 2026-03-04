# Cognito MFA Bypass Option Analysis

## Context

A developer suggested that the Lambda function could bypass MFA using AWS CLI and Cognito. Let's evaluate if this is:
1. **Possible** - Can it technically work?
2. **Appropriate** - Should we do it?
3. **Better than alternatives** - Is it the best solution?

---

## Understanding the Architecture

### Riskuity Authentication Stack

According to `docs/RISKUITY-AUTHENTICATION-GUIDE.md:192`:
> AWS Cognito (used by Riskuity) enforces rate limits

**This means:**
- Riskuity uses AWS Cognito for user authentication
- Cognito manages user pools, passwords, and MFA
- The `/users/get-auth-token` endpoint is a wrapper around Cognito API

### Current Flow

```
User → Riskuity API → AWS Cognito
        (/users/get-auth-token)

1. POST {email, password}
   → Cognito: InitiateAuth
   → Response: "EMAIL_OTP required"

2. POST {email, password, otp}
   → Cognito: RespondToAuthChallenge
   → Response: {access_token, id_token, refresh_token}
```

---

## Option: Direct Cognito Integration

### Can We Bypass Riskuity's API?

**YES**, if we:
1. Know the Cognito User Pool ID
2. Know the App Client ID
3. Have user credentials (email + password)
4. Can handle Cognito's MFA challenges

### AWS Cognito SDK Approach

```python
import boto3

# Initialize Cognito client
cognito = boto3.client('cognito-idp', region_name='us-east-1')  # Riskuity region

# Step 1: Initiate auth
response = cognito.initiate_auth(
    AuthFlow='USER_PASSWORD_AUTH',
    AuthParameters={
        'USERNAME': 'user@example.com',
        'PASSWORD': 'password'
    },
    ClientId='RISKUITY_APP_CLIENT_ID'  # Need to discover this
)

# If MFA required
if response['ChallengeName'] == 'CUSTOM_CHALLENGE':
    # Step 2: Handle MFA challenge
    # Still requires OTP from email!
    response = cognito.respond_to_auth_challenge(
        ClientId='RISKUITY_APP_CLIENT_ID',
        ChallengeName='CUSTOM_CHALLENGE',
        Session=response['Session'],
        ChallengeResponses={
            'USERNAME': 'user@example.com',
            'ANSWER': otp_code  # Still need OTP!
        }
    )
```

**Problem:** We still need the OTP code! This doesn't bypass MFA.

---

## Can We Actually Bypass MFA?

### Cognito MFA Types

AWS Cognito supports several MFA methods:

1. **SMS_MFA** - SMS text message
2. **SOFTWARE_TOKEN_MFA** - TOTP (Google Authenticator, etc.)
3. **EMAIL_OTP** - Email verification (what Riskuity uses)

### Bypass Options

#### Option 1: Service Account (No MFA)

**THIS IS THE REAL "BYPASS"**

Cognito allows certain users/app clients to be exempt from MFA:

```python
# Service accounts can be configured without MFA requirement
cognito.admin_initiate_auth(
    UserPoolId='RISKUITY_USER_POOL_ID',
    ClientId='SERVICE_ACCOUNT_CLIENT_ID',  # Different client ID
    AuthFlow='ADMIN_NO_SRP_AUTH',
    AuthParameters={
        'USERNAME': 'cortap_service_account',
        'PASSWORD': 'service_password'
    }
)
# Returns tokens immediately, no MFA challenge
```

**This is what we recommended earlier!**
- Service accounts don't require MFA
- Use `/users/get-token` endpoint (not `/users/get-auth-token`)
- No OTP needed

#### Option 2: Refresh Token (MFA Once)

Once a user authenticates with MFA, they get a **refresh token** that can be used to get new access tokens without MFA:

```python
# Get new access token using refresh token (no MFA)
response = cognito.initiate_auth(
    AuthFlow='REFRESH_TOKEN_AUTH',
    AuthParameters={
        'REFRESH_TOKEN': stored_refresh_token
    },
    ClientId='RISKUITY_APP_CLIENT_ID'
)
# Returns new access token, no MFA required
```

**Problems:**
- Need initial MFA to get refresh token
- Refresh tokens expire (typically 30 days)
- Need to store refresh tokens securely

#### Option 3: AWS IAM Authentication (Doesn't Apply)

Some developers confuse:
- **AWS Cognito** (user authentication for applications)
- **AWS IAM** (AWS resource access)

We're dealing with **Cognito**, not IAM. The AWS CLI MFA bypass refers to IAM, not Cognito.

---

## What the Other Developer Might Be Thinking

### Scenario 1: They Mean Service Accounts

"Bypass MFA using AWS CLI and Cognito" could mean:
- Create a service account in Cognito (via AWS CLI)
- Service account has MFA disabled
- Use service account credentials instead of user credentials

**This is exactly what we recommended!** ✅

### Scenario 2: They Mean Admin SDK

Using `admin_*` Cognito methods that require AWS IAM credentials:

```python
import boto3

# This requires AWS credentials (not Riskuity credentials)
cognito = boto3.client(
    'cognito-idp',
    aws_access_key_id='AWS_KEY',      # Our AWS account
    aws_secret_access_key='AWS_SECRET',
    region_name='us-east-1'
)

# Admin methods bypass MFA
response = cognito.admin_initiate_auth(
    UserPoolId='RISKUITY_USER_POOL_ID',
    ClientId='RISKUITY_CLIENT_ID',
    AuthFlow='ADMIN_NO_SRP_AUTH',
    AuthParameters={
        'USERNAME': 'user@example.com',
        'PASSWORD': 'password'
    }
)
```

**Problems:**
1. ❌ Requires AWS IAM permissions on **Riskuity's** Cognito user pool
2. ❌ We don't have access to Riskuity's AWS account
3. ❌ Security violation (accessing their Cognito pool)
4. ❌ Only works if we had admin permissions

**This won't work unless Riskuity grants us AWS IAM access to their Cognito pool.**

---

## Is This Better Than Our Current Approach?

### Current Recommendation: Service Account

**What we recommended:**
```bash
curl -X POST 'https://api.riskuity.com/users/get-token' \
  -H 'Content-Type: application/json' \
  -d '{"username": "cortap_service", "password": "password"}'
```

**Pros:**
- ✅ No MFA required
- ✅ Works immediately
- ✅ Uses Riskuity's official API
- ✅ No AWS credentials needed
- ✅ Proper audit trail
- ✅ Riskuity controls access

### Direct Cognito Integration

**What the developer might suggest:**
```python
import boto3

cognito = boto3.client('cognito-idp')
response = cognito.admin_initiate_auth(...)
```

**Pros:**
- ✅ Potentially bypass MFA (if we had admin access)

**Cons:**
- ❌ Requires AWS IAM credentials for Riskuity's AWS account
- ❌ Requires admin permissions on their Cognito user pool
- ❌ Violates security boundaries
- ❌ Riskuity unlikely to grant this access
- ❌ More complex than using their API
- ❌ Bypasses Riskuity's access control

**Conclusion:** Direct Cognito is **worse** than service accounts.

---

## What We Should Actually Do

### Clarify with the Developer

**Ask them:**
> "When you mention bypassing MFA with Cognito, do you mean:
>
> A) Creating a service account in Cognito that has MFA disabled?
> B) Using Cognito admin APIs to bypass MFA programmatically?
> C) Using refresh tokens to avoid repeated MFA?
> D) Something else?"

### Most Likely Scenario

They probably mean **Option A** - service accounts, which is exactly what we recommended in `RISKUITY-DEVELOPER-TOKEN-GUIDE.md`.

**Service Account = "MFA Bypass"**
- Service accounts don't have MFA enabled in Cognito
- This is the standard approach for API integrations
- No magical AWS CLI trick needed
- Just need Riskuity to create the account

---

## Technical Deep Dive: Can We Access Riskuity's Cognito?

### What We'd Need

To use Cognito admin APIs, we'd need:

1. **User Pool ID** - Can potentially discover from error messages
2. **App Client ID** - Can potentially discover from network traffic
3. **AWS Region** - Likely us-east-1
4. **AWS IAM Credentials** - ❌ **WE DON'T HAVE THIS**

### Example Discovery

```bash
# Attempt to discover from Riskuity API response headers
curl -v https://api.riskuity.com/users/get-auth-token

# Look for headers like:
# x-amz-cognito-user-pool-id: us-east-1_XYZ123
# x-amz-client-id: 7abc123def456...
```

**But even if we discovered these, we'd still need:**
- AWS credentials with `cognito-idp:AdminInitiateAuth` permission
- Riskuity to grant us IAM role assumption
- **This is a non-starter for security reasons**

---

## Recommendation

### Short Answer: No, Don't Use Direct Cognito Access

**Reasons:**
1. We don't have AWS IAM access to Riskuity's Cognito
2. Riskuity is unlikely to grant this (security violation)
3. Service accounts already solve the problem
4. Using their API is the proper integration method

### What to Tell the Developer

> "Thanks for the suggestion! If you mean using a Cognito service account
> that doesn't require MFA, that's exactly what we recommended - having
> Riskuity create a service account via their `/users/get-token` endpoint.
>
> If you mean using Cognito admin APIs to bypass MFA, that would require
> AWS IAM credentials for Riskuity's AWS account, which they're unlikely
> to provide for security reasons. The service account approach is the
> standard pattern for this."

---

## Action Items

### For Us: ❌ Don't Pursue Cognito Admin API Access

**Why:**
- Security violation
- Won't get access to Riskuity's AWS account
- Service accounts are the proper solution

### For Riskuity: ✅ Create Service Account

**What they need to do:**

1. **In AWS Cognito Console:**
   - Go to their Cognito User Pool
   - Create new user: `cortap_report_service`
   - Set permanent password (no forced change)
   - **Disable MFA requirement for this user**
   - Assign appropriate permissions

2. **Or via AWS CLI:**
```bash
# Riskuity admin runs this
aws cognito-idp admin-create-user \
  --user-pool-id us-east-1_THEIR_POOL_ID \
  --username cortap_report_service \
  --user-attributes Name=email,Value=cortap-service@riskuity.com \
  --message-action SUPPRESS

aws cognito-idp admin-set-user-password \
  --user-pool-id us-east-1_THEIR_POOL_ID \
  --username cortap_report_service \
  --password 'GeneratedPassword123!' \
  --permanent
```

3. **Share credentials with us** (securely)

4. **We test:**
```bash
curl -X POST 'https://api.riskuity.com/users/get-token' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "cortap_report_service",
    "password": "GeneratedPassword123!"
  }'
```

**Result:** API token without MFA! ✅

---

## Summary

### The "Cognito Bypass" They Mentioned

**Is probably:** Service account with MFA disabled ✅
**Is NOT:** Direct Cognito admin API access ❌

### What We Should Do

1. ✅ Stick with our current recommendation (service account)
2. ✅ Clarify with the developer what they meant
3. ❌ Don't pursue Cognito admin API access
4. ✅ Wait for Riskuity to create service account

### The Right Solution

**Service Account via Riskuity's API:**
```bash
# One-time setup by Riskuity
# Creates user in Cognito with MFA disabled

# Then we use it:
curl -X POST 'https://api.riskuity.com/users/get-token' \
  -d '{"username": "cortap_service", "password": "..."}'

# Returns: {access_token: "...", no MFA required}
```

**This IS the Cognito MFA bypass - through service accounts!**

---

**Date:** 2026-02-26
**Conclusion:** Service account = MFA bypass. No need for AWS CLI admin tricks.
**Status:** Our original recommendation was correct ✅
