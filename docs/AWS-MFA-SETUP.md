# AWS MFA Setup Guide

**Purpose:** Configure AWS CLI to work with Multi-Factor Authentication (MFA)

**Date:** 2025-02-09

---

## What is MFA?

Multi-Factor Authentication adds an extra security layer to your AWS account. When MFA is enabled, you need both:
1. Your AWS credentials (Access Key + Secret Key)
2. A time-based code from an authenticator app (Google Authenticator, Authy, Microsoft Authenticator, etc.)

---

## Quick Start

### Step 1: Get Your MFA Code

Open your authenticator app (Google Authenticator, Authy, etc.) and find the 6-digit code for AWS.

### Step 2: Run the MFA Login Script

```bash
cd /Users/bob.emerick/dev/AI-projects/CORTAP-RPT

# Run the script with your MFA code
./scripts/aws_mfa_login.sh 123456
# Replace 123456 with your actual 6-digit code
```

### Step 3: Use the MFA Session

After successful login, you'll see:

```
✅ Success! MFA Authentication Complete

To use these credentials:
  export AWS_PROFILE=govcloud-mfa
```

Then run:

```bash
export AWS_PROFILE=govcloud-mfa

# Now all AWS commands will use MFA credentials
./scripts/setup_s3_dev_bucket.sh
```

---

## Detailed Instructions

### Understanding the MFA Flow

1. **Base credentials** (Access Key + Secret Key) - These are permanent but have limited permissions
2. **MFA device** - Virtual device in your authenticator app
3. **Temporary credentials** - Full permissions for 12 hours after MFA verification

### What the Script Does

```bash
./scripts/aws_mfa_login.sh [MFA_CODE]
```

The script:
1. ✅ Verifies your base AWS credentials
2. ✅ Detects your MFA device ARN
3. ✅ Requests your MFA code (6 digits)
4. ✅ Exchanges MFA code for temporary session credentials
5. ✅ Stores credentials in a new AWS profile: `govcloud-mfa`
6. ✅ Credentials valid for 12 hours

### Using MFA Credentials

#### Option 1: Set Environment Variable (Recommended)

```bash
export AWS_PROFILE=govcloud-mfa

# Now all commands use MFA credentials
aws s3 ls
./scripts/setup_s3_dev_bucket.sh
pytest tests/integration/test_s3_storage_real.py -v
```

#### Option 2: Specify Profile in Each Command

```bash
aws s3 ls --profile govcloud-mfa
aws s3 mb s3://cortap-documents-dev --profile govcloud-mfa --region us-gov-west-1
```

#### Option 3: Update .env File

```bash
# Add to .env
AWS_PROFILE=govcloud-mfa
```

Then Python scripts and tests will automatically use MFA credentials.

---

## Troubleshooting

### Error: "No MFA device registered"

**Problem:** Your AWS user doesn't have an MFA device set up.

**Solution:** Register MFA device in AWS Console:

1. Go to: https://console.amazonaws-us-gov.com/
2. Click your name (top right) → **Security Credentials**
3. Scroll to **Multi-factor authentication (MFA)**
4. Click **Assign MFA device**
5. Choose **Virtual MFA device**
6. Scan QR code with Google Authenticator/Authy
7. Enter two consecutive MFA codes
8. Click **Assign MFA**

### Error: "Invalid MFA code"

**Causes:**
- Code already used (wait for next code - they refresh every 30 seconds)
- Clock skew (check your computer's time is accurate)
- Typing error

**Solution:**
- Wait for a new code to appear in your authenticator app
- Make sure your system clock is accurate
- Try again with fresh code

### Error: "AccessDenied"

**Problem:** Your base credentials don't have permission to call `sts:GetSessionToken`.

**Solution:** Ask your AWS admin to grant you the `sts:GetSessionToken` permission.

Required IAM policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "sts:GetSessionToken",
    "Resource": "*"
  }]
}
```

### Error: "Session has expired"

**Problem:** Your 12-hour MFA session has expired.

**Solution:** Run the MFA login script again:
```bash
./scripts/aws_mfa_login.sh [NEW_MFA_CODE]
```

### Script can't find jq

**Problem:** The script uses `jq` to parse JSON, but it's not installed.

**Solution:** Install jq:
```bash
# macOS
brew install jq

# Or download from: https://stedolan.github.io/jq/
```

---

## Session Duration

- **Default:** 12 hours (43,200 seconds)
- **Maximum:** 12 hours for IAM users with MFA
- **After expiration:** Run the script again with a new MFA code

---

## Best Practices

### ✅ DO:
- Run MFA login at the start of your work day
- Set `AWS_PROFILE=govcloud-mfa` in your terminal session
- Re-run the script when credentials expire
- Keep your authenticator app accessible

### ❌ DON'T:
- Share your MFA codes
- Screenshot your MFA QR code and store it insecurely
- Disable MFA (it's there for security)

---

## Integration with CORTAP-RPT

### For S3 Bucket Setup

```bash
# Get MFA code from authenticator app
./scripts/aws_mfa_login.sh 123456

# Set profile for this session
export AWS_PROFILE=govcloud-mfa

# Run S3 setup
./scripts/setup_s3_dev_bucket.sh
```

### For Integration Tests

```bash
# Get MFA session
./scripts/aws_mfa_login.sh 123456
export AWS_PROFILE=govcloud-mfa

# Run tests
pytest tests/integration/test_s3_storage_real.py -v -m integration
```

### For Daily Development

```bash
# Morning: Get MFA session
./scripts/aws_mfa_login.sh [TODAY_CODE]
export AWS_PROFILE=govcloud-mfa

# Work all day with full AWS access
# (session lasts 12 hours)
```

---

## Alternative: MFA with Environment Variables

If you prefer not to use AWS profiles, you can export the temporary credentials as environment variables:

```bash
# After running aws_mfa_login.sh, extract credentials:
eval $(aws configure get aws_access_key_id --profile govcloud-mfa | xargs -I {} echo "export AWS_ACCESS_KEY_ID={}")
eval $(aws configure get aws_secret_access_key --profile govcloud-mfa | xargs -I {} echo "export AWS_SECRET_ACCESS_KEY={}")
eval $(aws configure get aws_session_token --profile govcloud-mfa | xargs -I {} echo "export AWS_SESSION_TOKEN={}")
```

---

## How MFA Session Works

```
┌─────────────────────┐
│ Your Computer       │
│                     │
│ Base Credentials:   │
│  Access Key ID      │ ──┐
│  Secret Access Key  │   │
└─────────────────────┘   │
                          │
                          ▼
┌─────────────────────────────────────┐
│ AWS STS (Security Token Service)    │
│                                      │
│ 1. Verify base credentials           │
│ 2. Request MFA code                  │
│ 3. Validate MFA code                 │
│ 4. Generate temp credentials (12hr)  │
│    - Access Key ID (temp)            │
│    - Secret Access Key (temp)        │
│    - Session Token                   │
└─────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────┐
│ Your Computer       │
│                     │
│ MFA Session:        │
│  (12 hours)         │
│  Full AWS Access    │
└─────────────────────┘
```

---

## Quick Reference

```bash
# Get MFA session
./scripts/aws_mfa_login.sh 123456

# Use MFA session
export AWS_PROFILE=govcloud-mfa

# Create S3 bucket
./scripts/setup_s3_dev_bucket.sh

# Run integration tests
pytest tests/integration/test_s3_storage_real.py -v

# Check when session expires
aws configure get aws_session_token --profile govcloud-mfa
# If empty, session expired - run login script again
```

---

## FAQ

**Q: Do I need to enter MFA code every time I run AWS commands?**
A: No! Once you authenticate (run the script), you get 12 hours of access.

**Q: What happens after 12 hours?**
A: Your session expires. Run the script again with a new MFA code.

**Q: Can I increase the session duration beyond 12 hours?**
A: No, 12 hours is the AWS maximum for IAM users with MFA.

**Q: Do I need both base credentials AND MFA credentials?**
A: Base credentials are used to request MFA session. MFA credentials are used for actual AWS operations.

**Q: What if I lose my phone with the authenticator app?**
A: Contact your AWS administrator to reset your MFA device.

---

**Document Owner:** Bob Emerick
**Last Updated:** 2025-02-09
