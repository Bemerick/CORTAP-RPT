# Quick Start - AWS GovCloud Deployment

**Deploy CORTAP Report Generation to AWS GovCloud**

---

## Prerequisites (One-Time Setup)

```bash
# Install tools
brew install aws-sam-cli

# Configure AWS GovCloud
aws configure
# Region: us-gov-west-1

# Verify credentials
aws sts get-caller-identity
```

---

## MFA Authentication (Required)

```bash
# Source the MFA login script (sets credentials for 12 hours)
source scripts/aws-mfa-login.sh
# Enter your 6-digit MFA code when prompted
```

---

## Deploy (2 Commands)

```bash
# 1. Build
sam build

# 2. Deploy to dev
sam deploy --config-env dev
```

**Deployment prompts:**
- Stack Name: `cortap-rpt-dev`
- Region: `us-gov-west-1`
- Environment: `dev`
- Log Level: `INFO`
- **Accept all defaults** for other prompts

**Time:** ~5-10 minutes

---

## Get API Endpoint

```bash
aws cloudformation describe-stacks \
  --stack-name cortap-rpt-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
  --output text
```

**Output:** `https://[id].execute-api.us-gov-west-1.amazonaws.com/dev/api/v1/generate-report-sync`

---

## Test

```bash
export API_URL="https://[your-id].execute-api.us-gov-west-1.amazonaws.com/dev/api/v1/generate-report-sync"
export RISKUITY_TOKEN="Bearer [your-token]"

curl -X POST "$API_URL" \
  -H "Authorization: $RISKUITY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"project_id": 33, "report_type": "draft_audit_report"}'
```

**Expected:** JSON response with `download_url`

---

## Update Config

```bash
# 1. Edit config
vi config/project-setup.json

# 2. Rebuild & redeploy
sam build --use-container && sam deploy --profile govcloud
```

---

## Monitor

```bash
# View logs
sam logs --stack-name cortap-rpt-dev --tail

# Or CloudWatch
aws logs tail /aws/lambda/cortap-generate-report-sync-dev --follow
```

---

## Delete

```bash
sam delete --stack-name cortap-rpt-dev
```

---

## Need More Details?

- **Full Guide:** `docs/AWS-DEPLOYMENT-GUIDE.md`
- **Checklist:** `docs/DEPLOYMENT-CHECKLIST.md`
- **Config:** `config/README.md`

---

## Important Notes

- **MFA Required**: Must use `source scripts/aws-mfa-login.sh` before deployment
- **API Gateway**: Uses API Gateway (29s timeout) instead of Function URLs (not available in GovCloud)
- **Timeout**: Lambda has 120s timeout, API Gateway has 29s (document generation takes ~10s)
- **Region**: us-gov-west-1 (AWS GovCloud West)

---

**Status:** ✅ Ready to deploy
**Est. Cost:** ~$1-10/month
**Est. Time:** 5-10 minutes
