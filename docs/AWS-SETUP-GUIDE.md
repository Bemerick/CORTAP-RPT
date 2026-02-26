# AWS GovCloud Setup Guide

**Purpose:** Set up AWS GovCloud environment for CORTAP-RPT development and testing

**Date:** 2025-02-09

---

## Prerequisites

1. **AWS GovCloud Account Access**
   - Account ID
   - IAM user with appropriate permissions

2. **AWS CLI Installed**
   ```bash
   aws --version
   # Should show: aws-cli/2.x.x or higher
   ```

3. **Required IAM Permissions**
   Your IAM user needs:
   - `s3:CreateBucket`
   - `s3:PutObject`
   - `s3:GetObject`
   - `s3:DeleteObject`
   - `s3:ListBucket`
   - `s3:PutBucketEncryption`
   - `s3:PutBucketPublicAccessBlock`
   - `s3:PutBucketLifecycleConfiguration`
   - `s3:PutBucketVersioning`

---

## Step 1: Configure AWS Credentials

### Option A: AWS CLI Configure (Recommended)

```bash
aws configure --profile govcloud

# Prompts:
AWS Access Key ID [None]: YOUR_ACCESS_KEY
AWS Secret Access Key [None]: YOUR_SECRET_KEY
Default region name [None]: us-gov-west-1
Default output format [None]: json
```

### Option B: Environment Variables

```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-gov-west-1
```

### Option C: AWS Credentials File

Edit `~/.aws/credentials`:
```ini
[govcloud]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

Edit `~/.aws/config`:
```ini
[profile govcloud]
region = us-gov-west-1
output = json
```

### Verify Credentials

```bash
aws sts get-caller-identity --region us-gov-west-1

# Expected output:
{
    "UserId": "AIDAXXXXXXXXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws-us-gov:iam::123456789012:user/yourname"
}
```

---

## Step 2: Create S3 Dev Bucket

### Automated Setup (Recommended)

```bash
# Make script executable
chmod +x scripts/setup_s3_dev_bucket.sh

# Run the setup script
./scripts/setup_s3_dev_bucket.sh
```

The script will:
1. ✅ Verify AWS credentials
2. ✅ Create bucket: `cortap-documents-dev`
3. ✅ Enable AES-256 encryption
4. ✅ Block public access
5. ✅ Set lifecycle policy (90-day auto-delete)
6. ✅ Enable versioning
7. ✅ Test upload/download
8. ✅ Test pre-signed URLs

### Manual Setup (Alternative)

If you prefer to run commands manually:

```bash
# 1. Create bucket
aws s3 mb s3://cortap-documents-dev --region us-gov-west-1

# 2. Enable encryption
aws s3api put-bucket-encryption \
  --bucket cortap-documents-dev \
  --region us-gov-west-1 \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# 3. Block public access
aws s3api put-public-access-block \
  --bucket cortap-documents-dev \
  --region us-gov-west-1 \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# 4. Set lifecycle policy
aws s3api put-bucket-lifecycle-configuration \
  --bucket cortap-documents-dev \
  --region us-gov-west-1 \
  --lifecycle-configuration '{
    "Rules": [{
      "Id": "DeleteOldDocuments",
      "Status": "Enabled",
      "Expiration": {"Days": 90},
      "Filter": {"Prefix": ""}
    }]
  }'

# 5. Enable versioning
aws s3api put-bucket-versioning \
  --bucket cortap-documents-dev \
  --region us-gov-west-1 \
  --versioning-configuration Status=Enabled
```

---

## Step 3: Update Environment Configuration

Update your `.env` file:

```bash
# Copy example if not exists
cp .env.example .env

# Edit .env
nano .env
```

Required settings:
```bash
# AWS Configuration
AWS_REGION=us-gov-west-1
S3_BUCKET_NAME=cortap-documents-dev

# If using profile-based credentials
AWS_PROFILE=govcloud

# If using access keys directly (not recommended for production)
# AWS_ACCESS_KEY_ID=your-key
# AWS_SECRET_ACCESS_KEY=your-secret
```

---

## Step 4: Install Python Dependencies

Ensure boto3 is installed:

```bash
pip3 install boto3 requests
```

Or install all project dependencies:

```bash
pip3 install -r requirements.txt
```

---

## Step 5: Run Integration Tests

### Run All Integration Tests

```bash
# Run integration tests against real S3
pytest tests/integration/test_s3_storage_real.py -v -m integration
```

### Run Specific Test Classes

```bash
# Test document operations only
pytest tests/integration/test_s3_storage_real.py::TestRealS3DocumentOperations -v

# Test JSON caching only
pytest tests/integration/test_s3_storage_real.py::TestRealS3JsonCaching -v

# Test full workflow
pytest tests/integration/test_s3_storage_real.py::TestRealS3FullWorkflow -v
```

### Expected Output

```
tests/integration/test_s3_storage_real.py::TestRealS3DocumentOperations::test_upload_and_retrieve_document PASSED
tests/integration/test_s3_storage_real.py::TestRealS3DocumentOperations::test_presigned_url_download PASSED
tests/integration/test_s3_storage_real.py::TestRealS3DocumentOperations::test_document_deletion PASSED
tests/integration/test_s3_storage_real.py::TestRealS3JsonCaching::test_upload_and_retrieve_json PASSED
tests/integration/test_s3_storage_real.py::TestRealS3FullWorkflow::test_complete_document_generation_workflow PASSED
...

============================== 14 passed in 5.23s ===============================
```

---

## Step 6: Manual S3 Testing (Optional)

### Test Upload

```bash
echo "test content" > test.txt
aws s3 cp test.txt s3://cortap-documents-dev/test.txt --region us-gov-west-1
```

### Test Download

```bash
aws s3 cp s3://cortap-documents-dev/test.txt downloaded.txt --region us-gov-west-1
cat downloaded.txt
```

### Test Pre-signed URL

```bash
# Generate URL
aws s3 presign s3://cortap-documents-dev/test.txt --region us-gov-west-1 --expires-in 300

# Download using URL
curl -o downloaded2.txt "https://cortap-documents-dev.s3.us-gov-west-1.amazonaws.com/..."
```

### List Bucket Contents

```bash
aws s3 ls s3://cortap-documents-dev/ --region us-gov-west-1 --recursive
```

### Cleanup Test Files

```bash
aws s3 rm s3://cortap-documents-dev/test.txt --region us-gov-west-1
rm -f test.txt downloaded.txt downloaded2.txt
```

---

## Troubleshooting

### Issue: "Unable to locate credentials"

**Solution:**
```bash
aws configure
# Or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
```

### Issue: "AccessDenied" errors

**Solution:** Verify IAM permissions:
```bash
aws iam get-user --region us-gov-west-1
aws iam list-attached-user-policies --user-name YOUR_USERNAME --region us-gov-west-1
```

Required policy: `AmazonS3FullAccess` or custom policy with S3 permissions.

### Issue: "Bucket already exists"

**Solution:** Bucket names are globally unique. Either:
1. Use the existing bucket if it's yours
2. Choose a different bucket name (update scripts and .env)

### Issue: "Region not supported"

**Possible regions:**
- `us-gov-west-1` (AWS GovCloud US-West)
- `us-gov-east-1` (AWS GovCloud US-East)

Ensure you're using a GovCloud region, not commercial AWS.

### Issue: Integration tests failing

**Check:**
1. AWS credentials configured: `aws sts get-caller-identity`
2. Bucket exists: `aws s3 ls s3://cortap-documents-dev`
3. .env file has correct settings
4. Internet connectivity to AWS GovCloud

---

## Bucket Structure

After setup, your S3 bucket will have this structure:

```
s3://cortap-documents-dev/
├── documents/
│   └── {project_id}/
│       ├── draft-audit-report_20250209_143052.docx
│       ├── rir-package_20250209_150123.docx
│       └── cover-letter_20250209_151045.docx
└── data/
    ├── RSKTY-12345_project-data.json
    └── RSKTY-67890_project-data.json
```

---

## Security Best Practices

✅ **DO:**
- Use IAM roles (not access keys) in production
- Enable MFA for AWS console access
- Rotate access keys regularly (every 90 days)
- Use least-privilege IAM policies
- Enable CloudTrail logging for audit

❌ **DON'T:**
- Commit AWS credentials to git
- Share access keys via email/slack
- Use root account credentials
- Disable encryption
- Make buckets public

---

## Next Steps

After successful setup:

1. ✅ S3 bucket created and configured
2. ✅ Integration tests passing
3. 🔄 Integrate S3 into document generation API (Epic 5.2)
4. 🔄 Build Riskuity API client (Epic 3.5)
5. 🔄 Deploy Lambda to GovCloud (Epic 7)

---

## Support

**AWS GovCloud Documentation:**
- https://docs.aws.amazon.com/govcloud-us/
- https://aws.amazon.com/govcloud-us/getting-started/

**CORTAP-RPT Documentation:**
- `/docs/aws-govcloud-migration-plan.md`
- `/docs/s3-implementation-summary.md`

**Troubleshooting:**
- Check CloudWatch Logs for Lambda errors
- Review IAM permissions
- Verify bucket policies

---

**Document Owner:** Bob Emerick
**Last Updated:** 2025-02-09
