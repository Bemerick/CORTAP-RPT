# Next Steps: AWS S3 Dev Bucket Setup

**Date:** 2025-02-09
**Status:** Ready for Your Action

---

## What's Been Prepared ✅

1. **S3 Setup Script** - `scripts/setup_s3_dev_bucket.sh`
   - Automated bucket creation
   - Security configuration (encryption, public access blocking)
   - Lifecycle policy (90-day auto-delete)
   - Built-in testing

2. **Integration Tests** - `tests/integration/test_s3_storage_real.py`
   - 14 comprehensive tests for real AWS S3
   - Document upload/download testing
   - Pre-signed URL validation
   - JSON caching verification
   - Full workflow testing

3. **Setup Documentation** - `docs/AWS-SETUP-GUIDE.md`
   - Step-by-step instructions
   - Troubleshooting guide
   - Security best practices

---

## What You Need to Do Now

### Step 1: Configure AWS Credentials (5 minutes)

You need to set up AWS CLI with your GovCloud credentials:

```bash
aws configure
```

**Prompts:**
- AWS Access Key ID: `[Your GovCloud Access Key]`
- AWS Secret Access Key: `[Your GovCloud Secret Key]`
- Default region: `us-gov-west-1`
- Default output format: `json`

**Verify it works:**
```bash
aws sts get-caller-identity --region us-gov-west-1
```

You should see your account info (Account ID, User ARN).

---

### Step 2: Run the S3 Setup Script (2 minutes)

```bash
cd /Users/bob.emerick/dev/AI-projects/CORTAP-RPT

# Run the automated setup
./scripts/setup_s3_dev_bucket.sh
```

**What it does:**
1. Creates `cortap-documents-dev` bucket in us-gov-west-1
2. Enables AES-256 encryption
3. Blocks all public access
4. Sets 90-day lifecycle policy
5. Enables versioning
6. Tests upload/download
7. Tests pre-signed URLs

**Expected output:**
```
==========================================
✅ S3 Bucket Setup Complete!
==========================================

Bucket Details:
  Name: cortap-documents-dev
  Region: us-gov-west-1
  Encryption: AES-256
  ...
```

---

### Step 3: Update .env File (1 minute)

```bash
# Edit your .env file
nano .env
```

Add these lines:
```bash
# AWS Configuration
AWS_REGION=us-gov-west-1
S3_BUCKET_NAME=cortap-documents-dev
```

---

### Step 4: Run Integration Tests (3 minutes)

```bash
# Run all S3 integration tests
pytest tests/integration/test_s3_storage_real.py -v -m integration
```

**Expected result:**
```
============================== 14 passed in 5.23s ===============================
```

**What's being tested:**
- ✅ Upload Word documents to S3
- ✅ Download via pre-signed URLs
- ✅ Upload/retrieve JSON data (caching)
- ✅ Document deletion
- ✅ Error handling
- ✅ Complete end-to-end workflow

---

### Step 5: Manual Verification (Optional, 2 minutes)

Test the bucket manually:

```bash
# Upload a test file
echo "Hello from CORTAP-RPT" > test.txt
aws s3 cp test.txt s3://cortap-documents-dev/test.txt --region us-gov-west-1

# List bucket contents
aws s3 ls s3://cortap-documents-dev/ --region us-gov-west-1

# Generate pre-signed URL
aws s3 presign s3://cortap-documents-dev/test.txt --region us-gov-west-1

# Cleanup
aws s3 rm s3://cortap-documents-dev/test.txt --region us-gov-west-1
rm test.txt
```

---

## If You Run Into Issues

### "Unable to locate credentials"

You haven't run `aws configure` yet. Do that first.

### "AccessDenied" errors

Your IAM user needs S3 permissions. Check with your AWS admin to ensure you have:
- `s3:CreateBucket`
- `s3:PutObject`
- `s3:GetObject`
- `s3:DeleteObject`
- `s3:ListBucket`

### "Bucket already exists"

Either:
1. The bucket was created before → Run the script anyway (it will reconfigure)
2. Someone else owns that name → Choose a different bucket name

### Integration tests fail

Check:
```bash
# 1. AWS credentials work
aws sts get-caller-identity --region us-gov-west-1

# 2. Bucket exists
aws s3 ls s3://cortap-documents-dev --region us-gov-west-1

# 3. .env file is correct
cat .env | grep S3_BUCKET_NAME
```

---

## After Successful Setup

Once all tests pass, you'll have:

✅ **Development S3 bucket** ready in AWS GovCloud
✅ **Integration tests** validating real AWS operations
✅ **Pre-signed URLs** working for document downloads
✅ **JSON caching** operational

**Then we can proceed with:**

1. **Epic 5.2** - Integrate S3 into document generation API
   - Update DocumentGenerator to upload to S3
   - Return pre-signed URLs in API responses

2. **Epic 3.5** - Build Riskuity API client
   - Fetch data from Riskuity
   - Cache in S3 as JSON

3. **Epic 7** - Deploy Lambda to GovCloud
   - Create SAM template
   - Deploy full application

---

## Quick Command Reference

```bash
# Configure AWS
aws configure

# Create S3 bucket (automated)
./scripts/setup_s3_dev_bucket.sh

# Run integration tests
pytest tests/integration/test_s3_storage_real.py -v -m integration

# Check bucket status
aws s3 ls s3://cortap-documents-dev --region us-gov-west-1

# View bucket configuration
aws s3api get-bucket-encryption --bucket cortap-documents-dev --region us-gov-west-1
aws s3api get-public-access-block --bucket cortap-documents-dev --region us-gov-west-1
```

---

## Total Time Required

- AWS credentials setup: **5 minutes**
- Run S3 setup script: **2 minutes**
- Update .env: **1 minute**
- Run integration tests: **3 minutes**

**Total: ~11 minutes to fully operational AWS S3 development environment**

---

## Ready?

Let me know when you've:
1. ✅ Configured AWS credentials (`aws configure`)
2. ✅ Run the setup script (`./scripts/setup_s3_dev_bucket.sh`)
3. ✅ Updated .env file
4. ✅ Integration tests passing

Then we can move forward with integrating S3 into the document generation API!

---

**Questions?** See `/docs/AWS-SETUP-GUIDE.md` for detailed troubleshooting.
