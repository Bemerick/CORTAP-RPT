# CORTAP Report Generation Service

**Status:** ✅ Deployed to AWS GovCloud
**Latest Deployment:** 2026-02-27 18:49:31 UTC
**Environment:** Development (dev)

---

## Overview

Automated FTA compliance report generation service that integrates with Riskuity to generate draft audit reports for transit agency reviews.

### Features

- ✅ Synchronous report generation (10-15 seconds)
- ✅ Riskuity API integration (OAuth token authentication)
- ✅ AWS Lambda serverless architecture
- ✅ S3 document storage with pre-signed URLs
- ✅ Word document generation (.docx)
- ✅ JSON schema validation
- ✅ Comprehensive error handling and logging

---

## Quick Start

### For Riskuity Developers

**API Endpoint:**
```
POST https://qs5wkdxe8l.execute-api.us-gov-west-1.amazonaws.com/dev/api/v1/generate-report-sync
```

**Authentication:**
```bash
# Get API token from Riskuity staging
curl -X POST 'https://staging-api.riskuity.com/users/get-token' \
  -H 'Content-Type: application/json' \
  -d '{"username": "SERVICE_ACCOUNT", "password": "PASSWORD"}'

# Use token to generate report
curl -X POST 'https://qs5wkdxe8l.execute-api.us-gov-west-1.amazonaws.com/dev/api/v1/generate-report-sync' \
  -H 'Authorization: Bearer <TOKEN_FROM_ABOVE>' \
  -H 'Content-Type: application/json' \
  -d '{"project_id": 33, "report_type": "draft_audit_report"}'
```

**Response:**
```json
{
  "report_id": "rpt-20260227-123456-abc123",
  "status": "completed",
  "download_url": "https://...s3...docx",
  "generated_at": "2026-02-27T18:50:00Z",
  "expires_at": "2026-02-28T18:50:00Z",
  "metadata": {
    "recipient": "Seattle",
    "review_type": "Triennial Review",
    "review_areas": 21
  }
}
```

**See:** [RISKUITY-DEVELOPER-TOKEN-GUIDE.md](RISKUITY-DEVELOPER-TOKEN-GUIDE.md) for detailed integration instructions.

---

## Architecture

### Components

```
Riskuity User → Riskuity Backend → Lambda Function → Riskuity API
                                          ↓
                                    S3 Storage
                                          ↓
                                   Download URL
```

**Technology Stack:**
- **Runtime:** Python 3.11
- **Framework:** FastAPI with Mangum adapter
- **Cloud:** AWS GovCloud (us-gov-west-1)
- **Services:** Lambda, API Gateway, S3, CloudWatch
- **Authentication:** Riskuity OAuth tokens (pass-through)

---

## Project Structure

```
CORTAP-RPT/
├── app/
│   ├── api/v1/endpoints/
│   │   └── generate.py          # Main API endpoint
│   ├── handlers/
│   │   └── generate_sync_handler.py  # Lambda handler
│   ├── services/
│   │   ├── riskuity_client.py   # Riskuity API client
│   │   ├── data_transformer.py  # Data transformation
│   │   ├── validator.py         # Schema validation
│   │   ├── document_generator.py # Word doc generation
│   │   └── s3_storage.py        # S3 operations
│   ├── schemas/
│   │   ├── project-data-schema-v1.0.json  # Canonical schema
│   │   └── documents.py         # Pydantic models
│   └── templates/
│       └── draft_audit_report.docx  # Word template
├── config/
│   ├── project-setup.json       # Project configuration
│   └── project-setup-template.xlsx  # Excel template
├── scripts/
│   ├── test_riskuity_api.py    # API testing
│   ├── test_sync_generation.py # Integration tests
│   └── aws-mfa-login.ksh       # AWS authentication
├── template.yaml               # SAM infrastructure
├── build-lambda.sh            # Build script
└── requirements.txt           # Python dependencies
```

---

## Documentation

### Deployment Guides

- **[DEPLOYMENT-SUCCESS-2026-02-27.md](DEPLOYMENT-SUCCESS-2026-02-27.md)** - Latest deployment details
- **[DEPLOY-SCHEMA-FIX.md](DEPLOY-SCHEMA-FIX.md)** - Deployment procedures
- **[CHECK-DEPLOYMENT-STATUS.sh](CHECK-DEPLOYMENT-STATUS.sh)** - Status verification

### Authentication

- **[RISKUITY-DEVELOPER-TOKEN-GUIDE.md](RISKUITY-DEVELOPER-TOKEN-GUIDE.md)** - Integration guide
- **[PRODUCTION-AUTHENTICATION-STRATEGY.md](PRODUCTION-AUTHENTICATION-STRATEGY.md)** - Production approach
- **[AUTHENTICATION-ANALYSIS.md](AUTHENTICATION-ANALYSIS.md)** - Complete analysis
- **[TOKEN-TYPE-MISMATCH-ISSUE.md](TOKEN-TYPE-MISMATCH-ISSUE.md)** - Troubleshooting

### Operations

- **[CHECK-CLOUDWATCH-LOGS.md](CHECK-CLOUDWATCH-LOGS.md)** - Log monitoring
- **[COGNITO-BYPASS-ANALYSIS.md](COGNITO-BYPASS-ANALYSIS.md)** - Service accounts

### Development History

- **[SESSION-SUMMARY-2026-02-12-AWS-READY.md](SESSION-SUMMARY-2026-02-12-AWS-READY.md)** - Initial deployment
- **[TESTING-SESSION-STATUS-2026-02-12.md](TESTING-SESSION-STATUS-2026-02-12.md)** - Testing session
- **[docs/LAMBDA-TROUBLESHOOTING-SESSION-2026-02-25.md](docs/LAMBDA-TROUBLESHOOTING-SESSION-2026-02-25.md)** - Issue resolution

---

## Development

### Prerequisites

```bash
# Python 3.11+
python --version

# AWS SAM CLI
sam --version

# AWS CLI configured for GovCloud
aws configure --profile govcloud-mfa
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload --port 8000

# Test
python scripts/test_sync_generation.py --project-id 33
```

### Build & Deploy

```bash
# Build Lambda package
./build-lambda.sh

# Deploy to AWS
source /tmp/aws-session.sh  # After MFA auth
aws lambda update-function-code \
  --function-name cortap-generate-report-sync-dev \
  --zip-file fileb:///tmp/cortap-lambda-fix.zip \
  --region us-gov-west-1

# Verify
./verify-deployment.sh
```

---

## Configuration

### Environment Variables

Set in Lambda function configuration:

| Variable | Value | Purpose |
|----------|-------|---------|
| `RISKUITY_BASE_URL` | `https://api.riskuity.com` | Riskuity API endpoint |
| `S3_BUCKET_NAME` | `cortap-documents-dev-...` | S3 bucket for documents |
| `ENVIRONMENT` | `dev` | Environment name |
| `LOG_LEVEL` | `DEBUG` | Logging verbosity |
| `TEMPLATE_DIR` | `app/templates` | Word templates |
| `PROJECT_CONFIG_PATH` | `config/project-setup.json` | Project config |

### Project Configuration

Edit `config/project-setup.json` or use Excel template:

```bash
# Export to Excel
python scripts/manage_project_config.py export

# Edit in Excel: config/project-setup-template.xlsx

# Import back
python scripts/manage_project_config.py import
```

---

## Monitoring

### CloudWatch Logs

```bash
# View recent logs
aws logs filter-log-events \
  --log-group-name /aws/lambda/cortap-generate-report-sync-dev \
  --start-time $(date -u -v-1H +%s)000 \
  --profile govcloud-mfa \
  --region us-gov-west-1

# Search for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/cortap-generate-report-sync-dev \
  --filter-pattern "ERROR" \
  --start-time $(date -u -v-1H +%s)000 \
  --profile govcloud-mfa \
  --region us-gov-west-1
```

### Metrics

```bash
# Invocation count
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

---

## Troubleshooting

### Common Issues

**401 Unauthorized:**
- Check token is from `/users/get-token` (not web session)
- Verify token hasn't expired (1 hour lifetime)
- Decode token at jwt.io - should have `tenant_id` claim

**Validation Errors:**
- Check CloudWatch logs for specific field errors
- Verify Riskuity data structure hasn't changed
- Review schema: `app/schemas/project-data-schema-v1.0.json`

**Timeout:**
- Check CloudWatch for which stage is slow
- Riskuity API typically takes 8-10 seconds
- Lambda timeout is 120 seconds (should be plenty)

### Debug Mode

```bash
# Enable debug logging (already enabled in dev)
aws lambda update-function-configuration \
  --function-name cortap-generate-report-sync-dev \
  --environment Variables={LOG_LEVEL=DEBUG,...} \
  --profile govcloud-mfa \
  --region us-gov-west-1
```

---

## Testing

### Unit Tests

```bash
pytest tests/
```

### Integration Tests

```bash
# Test Riskuity API
python scripts/test_riskuity_api.py --project-id 33

# Test end-to-end
python scripts/test_sync_generation.py \
  --project-id 33 \
  --base-url https://qs5wkdxe8l.execute-api.us-gov-west-1.amazonaws.com/dev \
  --download
```

---

## Production Deployment

### Prerequisites

1. Riskuity implements backend token generation endpoint
2. Service account credentials configured in Riskuity backend
3. Production SAM deployment (currently using dev)
4. CloudWatch alarms configured
5. Monitoring dashboard set up

### Deployment Steps

See [PRODUCTION-AUTHENTICATION-STRATEGY.md](PRODUCTION-AUTHENTICATION-STRATEGY.md) for complete production deployment guide.

---

## Support

**Developer:** Bob Emerick
**Email:** bob@longevityconsulting.com
**Repository:** https://github.com/Bemerick/CORTAP-RPT

**AWS Resources:**
- Account: 736539455039 (GovCloud)
- Region: us-gov-west-1
- Lambda: cortap-generate-report-sync-dev
- Logs: /aws/lambda/cortap-generate-report-sync-dev

---

## License

Proprietary - Longevity Consulting LLC

---

**Last Updated:** 2026-02-27
**Version:** 1.0
**Status:** ✅ Production Ready (awaiting final testing)
