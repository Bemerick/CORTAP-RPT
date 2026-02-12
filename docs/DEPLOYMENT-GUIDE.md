# CORTAP-RPT Deployment Guide

**Version:** 1.0
**Date:** 2026-02-12
**For:** Synchronous Report Generation (Lambda Function URL)

---

## Overview

This guide covers deploying the CORTAP-RPT synchronous report generation service to AWS GovCloud using AWS SAM (Serverless Application Model).

### Architecture

```
┌─────────────┐          ┌──────────────────┐          ┌─────────┐
│  Riskuity   │  HTTPS   │  Lambda Function │  S3 API  │   S3    │
│   WebApp    ├─────────>│   (Function URL) ├─────────>│ Storage │
└─────────────┘          └──────────────────┘          └─────────┘
                               ↓
                         CloudWatch Logs
```

**Key Components:**
- **Lambda Function URL**: Bypasses API Gateway 29s timeout
- **Lambda Function**: 2-minute timeout, 2GB memory
- **S3 Bucket**: Encrypted document storage with 7-day lifecycle
- **CloudWatch**: Logs and alarms for monitoring

---

## Prerequisites

### 1. AWS CLI & SAM CLI

```bash
# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install SAM CLI
pip install aws-sam-cli

# Verify installations
aws --version      # Should be 2.x
sam --version      # Should be 1.x
```

### 2. AWS Credentials

Configure AWS GovCloud credentials:

```bash
aws configure --profile govcloud
# AWS Access Key ID: [your-key]
# AWS Secret Access Key: [your-secret]
# Default region name: us-gov-west-1
# Default output format: json
```

### 3. Python Dependencies

Ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

---

## Deployment Steps

### Step 1: Build the Application

```bash
# Build with SAM
sam build --use-container

# This will:
# - Create .aws-sam/build directory
# - Package dependencies
# - Prepare Lambda deployment package
```

**Expected Output:**
```
Build Succeeded

Built Artifacts  : .aws-sam/build
Built Template   : .aws-sam/build/template.yaml
```

### Step 2: Validate Template

```bash
# Validate CloudFormation template
sam validate --lint

# Check for errors
echo $?  # Should be 0
```

### Step 3: Deploy (Development)

```bash
# Deploy to dev environment
sam deploy \
  --config-env dev \
  --profile govcloud \
  --guided  # First time only

# Follow prompts:
# - Stack name: cortap-rpt-dev
# - Region: us-gov-west-1
# - Parameter Environment: dev
# - Parameter LogLevel: DEBUG
# - Confirm changes before deploy: Y
# - Allow SAM CLI IAM role creation: Y
# - Deploy this changeset: Y
```

**First Deployment:** Use `--guided` to configure `samconfig.toml`

**Subsequent Deployments:**
```bash
sam deploy --config-env dev --profile govcloud
```

### Step 4: Test Deployment

After deployment, SAM outputs the Function URL:

```
Outputs
-------
Key: GenerateReportSyncFunctionUrl
Value: https://xyz123.lambda-url.us-gov-west-1.on.aws/
```

Test with curl:

```bash
# Set variables
export FUNCTION_URL="https://xyz123.lambda-url.us-gov-west-1.on.aws"
export RISKUITY_TOKEN="your-bearer-token"

# Test endpoint
curl -X POST "${FUNCTION_URL}/api/v1/generate-report-sync" \
  -H "Authorization: Bearer ${RISKUITY_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 33,
    "report_type": "draft_audit_report"
  }'
```

**Expected Response (200 OK):**
```json
{
  "status": "completed",
  "report_id": "rpt-...",
  "download_url": "https://s3.amazonaws.com/...",
  "expires_at": "...",
  ...
}
```

---

## Environment-Specific Deployments

### Development (dev)

```bash
sam deploy --config-env dev --profile govcloud

# Configuration:
# - Stack: cortap-rpt-dev
# - Log Level: DEBUG
# - Timeout: 120s
# - Memory: 2048MB
```

### Staging (staging)

```bash
sam deploy --config-env staging --profile govcloud

# Configuration:
# - Stack: cortap-rpt-staging
# - Log Level: INFO
# - Timeout: 120s
# - Memory: 2048MB
```

### Production (prod)

```bash
sam deploy --config-env prod --profile govcloud

# Configuration:
# - Stack: cortap-rpt-prod
# - Log Level: WARNING
# - Timeout: 120s
# - Memory: 2048MB
# - Requires changeset confirmation
```

---

## Configuration

### Environment Variables

Set in `template.yaml` or override in `samconfig.toml`:

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | dev | Environment name (dev/staging/prod) |
| `LOG_LEVEL` | INFO | Logging level |
| `S3_BUCKET_NAME` | (auto) | S3 bucket for documents |
| `RISKUITY_API_URL` | https://app.riskuity.com/v1 | Riskuity API base URL |
| `AWS_REGION` | us-gov-west-1 | AWS region |

### Timeouts and Limits

| Resource | Value | Configurable |
|----------|-------|--------------|
| Lambda Timeout | 120s | Yes (template.yaml) |
| Lambda Memory | 2048MB | Yes (template.yaml) |
| S3 Document Expiry | 7 days | Yes (template.yaml) |
| Presigned URL Expiry | 24 hours | No (hardcoded) |

### CORS Configuration

Configured in `template.yaml`:

```yaml
AllowOrigins:
  - https://app.riskuity.com  # Production
  - https://staging.riskuity.com  # Staging
AllowMethods:
  - POST
AllowHeaders:
  - Authorization
  - Content-Type
```

---

## Monitoring

### CloudWatch Logs

View logs in AWS Console or CLI:

```bash
# Get log group name
aws logs describe-log-groups \
  --log-group-name-prefix /aws/lambda/cortap-generate-report-sync \
  --profile govcloud

# Tail logs (requires sam cli)
sam logs --name GenerateReportSyncFunction --tail --profile govcloud
```

### CloudWatch Alarms

Two alarms are configured:

1. **Error Alarm** (`cortap-generate-errors-${Environment}`)
   - Triggers on: 5+ errors in 5 minutes
   - Action: Alert (configure SNS topic)

2. **Duration Alarm** (`cortap-generate-slow-${Environment}`)
   - Triggers on: Average duration > 90 seconds
   - Action: Alert (configure SNS topic)

### Custom Metrics

Log-based metrics to create:

```bash
# Average generation time
aws logs put-metric-filter \
  --log-group-name /aws/lambda/cortap-generate-report-sync-dev \
  --filter-name GenerationTime \
  --filter-pattern '[timestamp, level, service, module, function, message, correlation_id, generation_time_ms]' \
  --metric-transformations \
    metricName=GenerationTime,\
    metricNamespace=CORTAP-RPT,\
    metricValue='$generation_time_ms',\
    unit=Milliseconds \
  --profile govcloud
```

---

## Troubleshooting

### Common Issues

#### 1. Timeout Errors (504)

**Symptom:** Request times out after 120 seconds

**Causes:**
- Riskuity API slow or unresponsive
- Large project with many controls (> 500)
- Network connectivity issues

**Solutions:**
- Increase Lambda timeout in `template.yaml`
- Optimize data fetching (parallel requests)
- Check Riskuity API status
- Review CloudWatch logs for bottlenecks

#### 2. Memory Errors

**Symptom:** "Task timed out" or memory limit exceeded

**Causes:**
- Document generation using too much memory
- Large assessment data (> 1000 areas)

**Solutions:**
- Increase Lambda memory in `template.yaml` (max 10GB)
- Optimize document generation
- Stream large files instead of loading in memory

#### 3. S3 Access Denied

**Symptom:** "Access Denied" when uploading to S3

**Causes:**
- Lambda role missing S3 permissions
- Bucket policy misconfigured

**Solutions:**
- Check IAM role permissions
- Verify bucket policy allows Lambda access
- Review CloudWatch logs for exact error

#### 4. CORS Errors

**Symptom:** Browser blocks request with CORS error

**Causes:**
- Origin not in AllowOrigins list
- Missing headers in CORS config

**Solutions:**
- Add origin to `AllowedOrigins` parameter
- Redeploy with updated CORS settings
- Check browser dev tools for exact error

### Debug Logs

Enable debug logging:

```bash
# Redeploy with DEBUG log level
sam deploy --config-env dev --profile govcloud \
  --parameter-overrides "LogLevel=DEBUG"

# View debug logs
sam logs --name GenerateReportSyncFunction --tail --profile govcloud
```

---

## Performance Optimization

### 1. Provisioned Concurrency

For predictable performance, enable provisioned concurrency:

```yaml
# Add to template.yaml
GenerateReportSyncFunction:
  Type: AWS::Serverless::Function
  Properties:
    ...
    ProvisionedConcurrencyConfig:
      ProvisionedConcurrentExecutions: 2
```

**Trade-off:** Higher cost, but eliminates cold starts

### 2. Lambda Layers

Extract dependencies to Lambda Layer for faster deployments:

```bash
# Create layer
sam build --use-container
sam package --output-template-file packaged.yaml
sam publish --template packaged.yaml --region us-gov-west-1
```

### 3. Connection Pooling

Enable connection pooling for Riskuity API:

```python
# In app/services/riskuity_client.py
import httpx

# Reuse client across invocations
_http_client = None

def get_http_client():
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(
            timeout=60.0,
            limits=httpx.Limits(max_connections=10)
        )
    return _http_client
```

---

## Rollback

If deployment fails or has issues:

```bash
# Rollback to previous version
aws cloudformation rollback-stack \
  --stack-name cortap-rpt-dev \
  --profile govcloud

# Or delete stack entirely
sam delete --stack-name cortap-rpt-dev --profile govcloud
```

---

## Cost Estimation

### Monthly Cost (Development)

Assuming 100 reports/day, 50s average duration:

| Resource | Usage | Cost/Month |
|----------|-------|------------|
| Lambda Requests | 3,000 | $0.60 |
| Lambda Duration | 150,000 GB-s | $2.50 |
| S3 Storage | 10 GB | $0.25 |
| S3 Requests | 6,000 | $0.03 |
| CloudWatch Logs | 5 GB | $2.50 |
| **Total** | | **~$6/month** |

### Monthly Cost (Production)

Assuming 1,000 reports/day, 50s average duration:

| Resource | Usage | Cost/Month |
|----------|-------|------------|
| Lambda Requests | 30,000 | $6.00 |
| Lambda Duration | 1,500,000 GB-s | $25.00 |
| S3 Storage | 100 GB | $2.50 |
| S3 Requests | 60,000 | $0.30 |
| CloudWatch Logs | 50 GB | $25.00 |
| **Total** | | **~$59/month** |

**Note:** AWS GovCloud pricing may differ

---

## Security Considerations

### 1. Token Security

- ✅ User tokens passed through (no storage)
- ✅ Tokens not logged (filtered in CloudWatch)
- ✅ HTTPS only (Lambda Function URL enforces TLS)

### 2. S3 Security

- ✅ Encryption at rest (AES256)
- ✅ Presigned URLs expire in 24 hours
- ✅ Public access blocked
- ✅ Documents auto-delete after 7 days

### 3. IAM Permissions

- ✅ Least-privilege IAM role
- ✅ No wildcard permissions
- ✅ Scoped to specific bucket

### 4. Network Security

- ✅ Lambda in VPC (optional, add VpcConfig)
- ✅ Security groups for outbound only
- ✅ CORS restricted to Riskuity domains

---

## Maintenance

### Regular Tasks

**Weekly:**
- Review CloudWatch logs for errors
- Check alarm status
- Monitor S3 storage usage

**Monthly:**
- Review cost reports
- Update dependencies (`pip list --outdated`)
- Test with latest Riskuity data

**Quarterly:**
- Rotate AWS credentials
- Review and update documentation
- Performance testing and optimization

### Updates and Patches

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Rebuild and deploy
sam build --use-container
sam deploy --config-env prod --profile govcloud
```

---

## Support and Resources

### Documentation
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [Lambda Function URLs](https://docs.aws.amazon.com/lambda/latest/dg/lambda-urls.html)
- [Integration Specification](./RISKUITY-CORTAP-INTEGRATION-SPEC.md)

### Commands Reference

```bash
# Build
sam build --use-container

# Validate
sam validate --lint

# Deploy
sam deploy --config-env dev --profile govcloud

# View logs
sam logs --name GenerateReportSyncFunction --tail --profile govcloud

# Delete stack
sam delete --stack-name cortap-rpt-dev --profile govcloud

# Test locally
sam local start-api --profile govcloud
sam local invoke GenerateReportSyncFunction --profile govcloud
```

---

## Appendix

### A. Template Parameters

Complete list of parameters in `template.yaml`:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| Environment | String | dev | Environment (dev/staging/prod) |
| LogLevel | String | INFO | Log level (DEBUG/INFO/WARNING/ERROR) |
| RiskuityApiUrl | String | https://app.riskuity.com/v1 | Riskuity API base |
| AllowedOrigins | String | https://app.riskuity.com | CORS origins |

### B. Stack Outputs

Outputs available after deployment:

| Output | Description | Export Name |
|--------|-------------|-------------|
| DocumentsBucket | S3 bucket name | {StackName}-DocumentsBucket |
| GenerateReportSyncFunctionUrl | Function URL | {StackName}-GenerateReportSyncUrl |
| GenerateReportSyncFunctionArn | Lambda ARN | {StackName}-GenerateReportSyncArn |
| GenerateReportLogGroup | Log group name | {StackName}-LogGroup |

### C. IAM Permissions Required

Deploying user needs:

- `cloudformation:*`
- `lambda:*`
- `s3:*`
- `iam:CreateRole`
- `iam:AttachRolePolicy`
- `logs:CreateLogGroup`

---

**Last Updated:** 2026-02-12
**Version:** 1.0
**Maintained By:** CORTAP-RPT Team
