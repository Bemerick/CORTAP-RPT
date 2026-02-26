# CloudWatch Logs Investigation Guide

## Purpose
Determine if the Lambda function is being invoked when Riskuity developer makes requests.

**Key Question:** Is API Gateway blocking requests before they reach Lambda, or is Lambda receiving requests and returning errors?

---

## Step 1: Authenticate with AWS

```bash
# Run the MFA login script
./scripts/aws-mfa-login.ksh

# OR manually get session token
aws sts get-session-token \
  --serial-number arn:aws-us-gov:iam::736539455039:mfa/bob.emerick \
  --token-code <your-6-digit-mfa-code> \
  --duration-seconds 43200 \
  --profile govcloud \
  --region us-gov-west-1
```

---

## Step 2: Check Lambda Invocation Logs

### Option A: Recent Invocations (Last 1 Hour)

```bash
# Calculate timestamp for 1 hour ago (in milliseconds)
START_TIME=$(date -u -v-1H +%s)000

# Get recent log events
aws logs filter-log-events \
  --log-group-name /aws/lambda/cortap-generate-report-sync-dev \
  --start-time $START_TIME \
  --profile govcloud-mfa \
  --region us-gov-west-1 \
  --max-items 50
```

### Option B: Search for 401 Errors

```bash
# Search for authentication errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/cortap-generate-report-sync-dev \
  --filter-pattern "401" \
  --start-time $(date -u -v-1H +%s)000 \
  --profile govcloud-mfa \
  --region us-gov-west-1
```

### Option C: Search for START/END Records (Invocation Proof)

```bash
# Every Lambda invocation has START, END, REPORT records
aws logs filter-log-events \
  --log-group-name /aws/lambda/cortap-generate-report-sync-dev \
  --filter-pattern "START RequestId" \
  --start-time $(date -u -v-1H +%s)000 \
  --profile govcloud-mfa \
  --region us-gov-west-1
```

### Option D: Live Tail (While Riskuity Developer Tests)

**Best Option:** Have Riskuity developer make a request while you watch logs in real-time.

**AWS Console Method:**
1. Go to: https://console.amazonaws-us-gov.com/cloudwatch/
2. Navigate to: Logs > Log groups > `/aws/lambda/cortap-generate-report-sync-dev`
3. Click "Search log group"
4. Have developer make request
5. Watch for new log streams appearing

**CLI Method (if your AWS CLI supports it):**
```bash
# Note: 'tail' command may not be available in all AWS CLI versions
aws logs tail /aws/lambda/cortap-generate-report-sync-dev \
  --follow \
  --profile govcloud-mfa \
  --region us-gov-west-1
```

---

## Step 3: Check API Gateway Logs

API Gateway may have its own logs (if enabled):

```bash
# List all log groups
aws logs describe-log-groups \
  --profile govcloud-mfa \
  --region us-gov-west-1 \
  --query 'logGroups[?contains(logGroupName, `API-Gateway`) || contains(logGroupName, `apigateway`)].logGroupName'
```

---

## Step 4: Check Lambda Metrics

Even without logs, metrics show if Lambda was invoked:

```bash
# Get invocation count for last hour
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=cortap-generate-report-sync-dev \
  --start-time $(date -u -v-1H +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum \
  --profile govcloud-mfa \
  --region us-gov-west-1
```

**If Invocations > 0:** Lambda IS being invoked (error is from Lambda or Riskuity)
**If Invocations = 0:** API Gateway is blocking (need to fix API Gateway config)

---

## What to Look For

### ✅ Lambda is Being Invoked (Good News)

**Evidence:**
- You see `START RequestId: xxx-xxx-xxx` in logs
- CloudWatch metrics show Invocations > 0
- You see correlation IDs in logs

**What This Means:**
- API Gateway is passing requests through
- The 401 error is coming from Lambda (easy to fix)
- Likely cause: Lambda can't authenticate with Riskuity API using the provided token

**Next Steps:**
- Verify token format being sent by Riskuity developer
- Check if token is actually valid (test with curl to Riskuity API directly)
- Review Lambda code's token extraction logic

---

### ❌ Lambda is NOT Being Invoked (Bad News)

**Evidence:**
- No START records in logs
- CloudWatch metrics show Invocations = 0
- No correlation IDs appearing
- Logs are completely empty during test requests

**What This Means:**
- **API Gateway is blocking requests before Lambda**
- The 401 error is from API Gateway trying to parse Bearer token as AWS SigV4
- This matches the error message exactly

**Next Steps:**
- Implement one of the solutions from AUTHENTICATION-ANALYSIS.md:
  1. Quick Test: Use custom header (X-Riskuity-Token)
  2. Best Fix: Migrate to HTTP API
  3. Production: Add Lambda Authorizer

---

## Example: Interpreting CloudWatch Logs

### Scenario 1: Lambda Invoked Successfully
```json
{
  "timestamp": "2026-02-26T20:30:15.123Z",
  "message": "START RequestId: abc-123-def RequestVersion: $LATEST"
}
{
  "timestamp": "2026-02-26T20:30:15.456Z",
  "message": "{\"level\":\"INFO\",\"message\":\"Starting synchronous report generation\",\"correlation_id\":\"gen-sync-abc123\"}"
}
{
  "timestamp": "2026-02-26T20:30:16.789Z",
  "message": "END RequestId: abc-123-def"
}
```
✅ **Lambda was invoked** - Now investigate the actual error in the logs

---

### Scenario 2: No Lambda Invocation
```
(No results found)
```
❌ **Lambda was NOT invoked** - API Gateway is blocking

---

## Quick Decision Tree

```
Run: aws logs filter-log-events --log-group-name /aws/lambda/cortap-generate-report-sync-dev --filter-pattern "START" --start-time $(date -u -v-10m +%s)000 --profile govcloud-mfa --region us-gov-west-1

┌─────────────────────────┐
│ Are there any results?  │
└───────┬─────────────────┘
        │
        ├─ YES → Lambda is being invoked
        │        └─> Check logs for actual error
        │           └─> Fix Lambda code or token format
        │
        └─ NO  → API Gateway is blocking
                 └─> Migrate to HTTP API (AUTHENTICATION-ANALYSIS.md Option 2)
                    OR
                 └─> Test with custom header (AUTHENTICATION-ANALYSIS.md Option 3)
```

---

## Commands to Run RIGHT NOW

**While Riskuity developer makes a test request:**

```bash
# Terminal 1: Watch for invocations
watch -n 1 'aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=cortap-generate-report-sync-dev \
  --start-time $(date -u -v-5m +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Sum \
  --profile govcloud-mfa \
  --region us-gov-west-1 \
  --query "Datapoints[*].[Timestamp,Sum]" \
  --output table'

# Terminal 2: Developer makes request
# (Riskuity developer sends POST request)

# Terminal 3: Check if invocation happened
aws logs filter-log-events \
  --log-group-name /aws/lambda/cortap-generate-report-sync-dev \
  --filter-pattern "START" \
  --start-time $(date -u -v-1m +%s)000 \
  --profile govcloud-mfa \
  --region us-gov-west-1
```

---

**Date:** 2026-02-26
**Function:** cortap-generate-report-sync-dev
**Region:** us-gov-west-1
**Account:** 736539455039
