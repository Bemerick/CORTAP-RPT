# AWS Deployment Guide - CORTAP Report Generation

**Last Updated:** February 12, 2026
**Status:** Ready for deployment
**Environment:** AWS GovCloud

---

## Overview

This guide covers deploying the CORTAP Report Generation Service to AWS using SAM (Serverless Application Model). The deployment includes:

- **Lambda Function** with Function URL (120s timeout)
- **S3 Bucket** for generated documents
- **CloudWatch** logs and alarms
- **IAM Roles** for least-privilege access

---

## Prerequisites

### 1. AWS CLI & SAM CLI

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Install SAM CLI
brew tap aws/tap
brew install aws-sam-cli

# Verify installations
aws --version
sam --version
```

### 2. AWS Credentials

Configure AWS credentials for GovCloud:

```bash
aws configure --profile govcloud
```

Required inputs:
- **AWS Access Key ID**: (from IAM user)
- **AWS Secret Access Key**: (from IAM user)
- **Default region**: `us-gov-west-1`
- **Default output**: `json`

### 3. Python Dependencies

```bash
# Install Python 3.11 (Lambda runtime version)
python3.11 --version

# Install project dependencies
pip install -r requirements.txt
```

---

## Pre-Deployment Checklist

### 1. Update Project Configuration

Edit `config/project-setup.json` with your project data:

```bash
# Option 1: Edit JSON directly
vi config/project-setup.json

# Option 2: Use Excel template
python scripts/manage_project_config.py export
# Edit config/project-setup-template.xlsx in Excel
python scripts/manage_project_config.py import --input config/project-setup-template.xlsx

# Validate configuration
python scripts/manage_project_config.py validate
```

### 2. Update SAM Configuration

Edit `samconfig.toml` if needed (environment, region, etc.):

```toml
[default.deploy.parameters]
stack_name = "cortap-rpt-dev"
region = "us-gov-west-1"
capabilities = "CAPABILITY_IAM"
parameter_overrides = "Environment=dev LogLevel=INFO"
```

### 3. Verify Template Files

Ensure all required files are in place:

```bash
ls -la app/templates/draft_audit_report.docx
ls -la config/project-setup.json
ls -la template.yaml
ls -la requirements.txt
```

---

## Deployment Steps

### Step 1: Build

Build the Lambda deployment package:

```bash
sam build --use-container
```

This will:
- Create `.aws-sam/build/` directory
- Install Python dependencies
- Package application code
- Include `config/` and `app/templates/` directories

**Expected output:**
```
Build Succeeded

Built Artifacts  : .aws-sam/build
Built Template   : .aws-sam/build/template.yaml
```

### Step 2: Deploy (First Time)

For first deployment (guided):

```bash
sam deploy --guided --profile govcloud
```

Answer prompts:
- **Stack Name**: `cortap-rpt-dev`
- **AWS Region**: `us-gov-west-1`
- **Parameter Environment**: `dev`
- **Parameter LogLevel**: `INFO`
- **Parameter RiskuityApiUrl**: `https://api.riskuity.com/v1`
- **Parameter AllowedOrigins**: `https://app.riskuity.com`
- **Confirm changes before deploy**: `Y`
- **Allow SAM CLI IAM role creation**: `Y`
- **Disable rollback**: `N`
- **Save arguments to configuration file**: `Y`

**Deployment time:** ~5-10 minutes

### Step 3: Deploy (Subsequent)

For updates after first deployment:

```bash
sam build && sam deploy --profile govcloud
```

---

## Post-Deployment

### 1. Get Function URL

```bash
aws cloudformation describe-stacks \
  --stack-name cortap-rpt-dev \
  --profile govcloud \
  --query 'Stacks[0].Outputs[?OutputKey==`GenerateReportSyncFunctionUrl`].OutputValue' \
  --output text
```

**Output example:**
```
https://abc123xyz.lambda-url.us-gov-west-1.on.aws/
```

### 2. Get S3 Bucket Name

```bash
aws cloudformation describe-stacks \
  --stack-name cortap-rpt-dev \
  --profile govcloud \
  --query 'Stacks[0].Outputs[?OutputKey==`DocumentsBucket`].OutputValue' \
  --output text
```

### 3. Test the Endpoint

```bash
# Get your Riskuity token
export RISKUITY_TOKEN="your-token-here"

# Test generation
curl -X POST https://your-function-url.lambda-url.us-gov-west-1.on.aws/api/v1/generate-report-sync \
  -H "Authorization: Bearer $RISKUITY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 33,
    "report_type": "draft_audit_report"
  }'
```

**Expected response:**
```json
{
  "report_id": "rpt-20260212-...",
  "status": "completed",
  "s3_key": "generated/33/rpt-20260212-...docx",
  "download_url": "https://...",
  "generated_at": "2026-02-12T20:00:00Z"
}
```

### 4. Monitor Logs

```bash
# Tail logs in real-time
sam logs --stack-name cortap-rpt-dev --tail --profile govcloud

# Or use CloudWatch Insights
aws logs tail /aws/lambda/cortap-generate-report-sync-dev \
  --follow \
  --profile govcloud
```

---

## Configuration Management

### Environment Variables

Set in `template.yaml` or via SAM parameters:

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `dev` | Environment name |
| `LOG_LEVEL` | `INFO` | Logging level |
| `S3_BUCKET_NAME` | Auto-created | S3 bucket for documents |
| `RISKUITY_API_URL` | `https://api.riskuity.com/v1` | Riskuity API endpoint |
| `TEMPLATE_DIR` | `app/templates` | Word templates directory |
| `PROJECT_CONFIG_PATH` | `config/project-setup.json` | Project config file |

### Update Configuration

To update project configuration after deployment:

1. **Update local config:**
   ```bash
   # Edit config/project-setup.json
   vi config/project-setup.json
   ```

2. **Rebuild and redeploy:**
   ```bash
   sam build && sam deploy --profile govcloud
   ```

The configuration file is bundled into the Lambda deployment package, so changes require redeployment.

---

## Troubleshooting

### Build Fails

**Error:** `ModuleNotFoundError` during build

**Solution:** Ensure all dependencies are in `requirements.txt`:
```bash
pip freeze > requirements-dev.txt
# Compare with requirements.txt
```

### Deployment Fails - IAM Permissions

**Error:** `User: arn:aws:iam::... is not authorized to perform: cloudformation:CreateStack`

**Solution:** Your AWS user needs these permissions:
- `CloudFormationFullAccess`
- `IAMFullAccess`
- `AWSLambdaFullAccess`
- `AmazonS3FullAccess`

### Function Timeout

**Error:** `Task timed out after 120.00 seconds`

**Solution:** Increase timeout in `template.yaml`:
```yaml
Timeout: 180  # 3 minutes
```

### S3 Access Denied

**Error:** `AccessDenied: Access Denied`

**Solution:** Verify IAM role has S3 permissions:
```bash
aws iam get-role-policy \
  --role-name cortap-rpt-dev-GenerateReportFunctionRole-... \
  --policy-name S3Access \
  --profile govcloud
```

### Configuration Not Loading

**Error:** `No project configuration found for project X`

**Solution:**
1. Verify config file exists in build:
   ```bash
   ls -la .aws-sam/build/GenerateReportSyncFunction/config/
   ```
2. Check `.samignore` doesn't exclude `config/`
3. Rebuild and redeploy

---

## Monitoring & Alerts

### CloudWatch Alarms

Two alarms are automatically created:

1. **Error Alarm**: Triggers if 5+ errors in 5 minutes
2. **Duration Alarm**: Triggers if average duration > 90s

### View Alarms

```bash
aws cloudwatch describe-alarms \
  --alarm-name-prefix cortap-generate \
  --profile govcloud
```

### Custom Metrics

View generation metrics:

```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=cortap-generate-report-sync-dev \
  --start-time 2026-02-12T00:00:00Z \
  --end-time 2026-02-12T23:59:59Z \
  --period 3600 \
  --statistics Average,Maximum \
  --profile govcloud
```

---

## Cleanup / Teardown

To delete the entire stack:

```bash
sam delete --stack-name cortap-rpt-dev --profile govcloud
```

**Warning:** This will:
- Delete the Lambda function
- Delete the S3 bucket (and all documents)
- Delete CloudWatch logs
- Delete all IAM roles

---

## Cost Estimates

**Monthly costs (dev environment, ~100 reports/month):**

| Service | Usage | Cost |
|---------|-------|------|
| Lambda | 100 invocations × 30s @ 2GB | ~$0.50 |
| S3 Storage | 100 docs × 60KB × 7 days retention | ~$0.01 |
| CloudWatch Logs | 100MB logs | ~$0.50 |
| **Total** | | **~$1.00/month** |

**Production estimates (1000 reports/month):**
- Lambda: ~$5/month
- S3: ~$0.10/month
- CloudWatch: ~$5/month
- **Total: ~$10/month**

---

## Security Considerations

### 1. Function URL Authentication

Currently using `AuthType: NONE` with custom auth in function. To enable AWS IAM auth:

```yaml
FunctionUrlConfig:
  AuthType: AWS_IAM  # Requires signed requests
```

### 2. S3 Bucket Encryption

Enabled by default (AES256). For KMS encryption:

```yaml
BucketEncryption:
  ServerSideEncryptionConfiguration:
    - ServerSideEncryptionByDefault:
        SSEAlgorithm: aws:kms
        KMSMasterKeyID: !Ref MyKMSKey
```

### 3. VPC Configuration

To run Lambda in VPC (for private Riskuity connectivity):

```yaml
VpcConfig:
  SecurityGroupIds:
    - !Ref LambdaSecurityGroup
  SubnetIds:
    - !Ref PrivateSubnet1
    - !Ref PrivateSubnet2
```

---

## Next Steps

1. **Deploy to staging** environment:
   ```bash
   sam deploy --parameter-overrides Environment=staging
   ```

2. **Set up CI/CD pipeline** (GitHub Actions, CodePipeline, etc.)

3. **Configure monitoring dashboard** in CloudWatch

4. **Integrate with Riskuity** frontend

5. **Load production project configurations**

---

## Support

- **AWS SAM Docs**: https://docs.aws.amazon.com/serverless-application-model/
- **Project Issues**: File issues in project repository
- **AWS GovCloud Docs**: https://docs.aws.amazon.com/govcloud-us/

---

**Deployment Status:** ✅ Ready
**Last Tested:** February 12, 2026
**Test Environment:** Local (document generation working)
**Production Status:** Pending AWS deployment
