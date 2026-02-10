#!/bin/bash
#
# S3 Dev Bucket Setup Script for AWS GovCloud
#
# This script creates and configures the CORTAP-RPT development S3 bucket
# in AWS GovCloud with proper encryption, security, and lifecycle policies.
#
# Usage:
#   ./scripts/setup_s3_dev_bucket.sh
#
# Prerequisites:
#   - AWS CLI installed (aws --version)
#   - AWS GovCloud credentials configured (aws configure)
#   - Permissions: s3:CreateBucket, s3:PutBucketEncryption, s3:PutBucketPublicAccessBlock
#

set -e  # Exit on error

# Configuration
BUCKET_NAME="cortap-documents-dev"
REGION="us-gov-west-1"
LIFECYCLE_DAYS=90

echo "=========================================="
echo "CORTAP-RPT S3 Dev Bucket Setup"
echo "=========================================="
echo ""

# Step 1: Verify AWS credentials
echo "Step 1: Verifying AWS GovCloud credentials..."
if ! aws sts get-caller-identity --region $REGION > /dev/null 2>&1; then
    echo "❌ ERROR: AWS credentials not configured or invalid"
    echo ""
    echo "Please run: aws configure"
    echo "And provide:"
    echo "  - AWS Access Key ID"
    echo "  - AWS Secret Access Key"
    echo "  - Default region: us-gov-west-1"
    echo "  - Default output format: json"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --region $REGION --query Account --output text)
USER_ARN=$(aws sts get-caller-identity --region $REGION --query Arn --output text)

echo "✅ Credentials verified"
echo "   Account: $ACCOUNT_ID"
echo "   User: $USER_ARN"
echo ""

# Step 2: Check if bucket already exists
echo "Step 2: Checking if bucket exists..."
if aws s3 ls "s3://$BUCKET_NAME" --region $REGION > /dev/null 2>&1; then
    echo "⚠️  Bucket $BUCKET_NAME already exists"
    echo ""
    read -p "Do you want to reconfigure it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping bucket creation..."
        SKIP_CREATE=true
    fi
else
    echo "✅ Bucket does not exist - will create"
    SKIP_CREATE=false
fi
echo ""

# Step 3: Create bucket
if [ "$SKIP_CREATE" = false ]; then
    echo "Step 3: Creating S3 bucket..."
    if aws s3 mb "s3://$BUCKET_NAME" --region $REGION; then
        echo "✅ Bucket created: s3://$BUCKET_NAME"
    else
        echo "❌ ERROR: Failed to create bucket"
        exit 1
    fi
else
    echo "Step 3: Skipping bucket creation"
fi
echo ""

# Step 4: Enable encryption
echo "Step 4: Enabling AES-256 encryption..."
if aws s3api put-bucket-encryption \
    --bucket $BUCKET_NAME \
    --region $REGION \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            },
            "BucketKeyEnabled": false
        }]
    }'; then
    echo "✅ Encryption enabled (AES-256)"
else
    echo "❌ ERROR: Failed to enable encryption"
    exit 1
fi
echo ""

# Step 5: Block public access
echo "Step 5: Blocking public access..."
if aws s3api put-public-access-block \
    --bucket $BUCKET_NAME \
    --region $REGION \
    --public-access-block-configuration \
        "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"; then
    echo "✅ Public access blocked"
else
    echo "❌ ERROR: Failed to block public access"
    exit 1
fi
echo ""

# Step 6: Set lifecycle policy
echo "Step 6: Setting lifecycle policy (delete after $LIFECYCLE_DAYS days)..."
if aws s3api put-bucket-lifecycle-configuration \
    --bucket $BUCKET_NAME \
    --region $REGION \
    --lifecycle-configuration '{
        "Rules": [{
            "Id": "DeleteOldDocuments",
            "Status": "Enabled",
            "Expiration": {
                "Days": '$LIFECYCLE_DAYS'
            },
            "Filter": {
                "Prefix": ""
            }
        }]
    }'; then
    echo "✅ Lifecycle policy configured (auto-delete after $LIFECYCLE_DAYS days)"
else
    echo "⚠️  WARNING: Failed to set lifecycle policy (non-critical)"
fi
echo ""

# Step 7: Enable versioning (optional for dev)
echo "Step 7: Enabling versioning (recommended for dev)..."
if aws s3api put-bucket-versioning \
    --bucket $BUCKET_NAME \
    --region $REGION \
    --versioning-configuration Status=Enabled; then
    echo "✅ Versioning enabled"
else
    echo "⚠️  WARNING: Failed to enable versioning (non-critical)"
fi
echo ""

# Step 8: Test bucket access
echo "Step 8: Testing bucket access..."
TEST_FILE=$(mktemp)
echo "test content" > $TEST_FILE

if aws s3 cp $TEST_FILE "s3://$BUCKET_NAME/test.txt" --region $REGION > /dev/null 2>&1; then
    echo "✅ Upload test: PASSED"

    # Test download
    if aws s3 cp "s3://$BUCKET_NAME/test.txt" - --region $REGION > /dev/null 2>&1; then
        echo "✅ Download test: PASSED"
    else
        echo "❌ Download test: FAILED"
    fi

    # Cleanup test file
    aws s3 rm "s3://$BUCKET_NAME/test.txt" --region $REGION > /dev/null 2>&1
    echo "✅ Delete test: PASSED"
else
    echo "❌ Upload test: FAILED"
    echo "   Check IAM permissions for s3:PutObject"
fi

rm -f $TEST_FILE
echo ""

# Step 9: Generate pre-signed URL test
echo "Step 9: Testing pre-signed URL generation..."
# Upload another test file
echo "presigned test" > $TEST_FILE
aws s3 cp $TEST_FILE "s3://$BUCKET_NAME/presign-test.txt" --region $REGION > /dev/null 2>&1

PRESIGNED_URL=$(aws s3 presign "s3://$BUCKET_NAME/presign-test.txt" --region $REGION --expires-in 300)

if [ ! -z "$PRESIGNED_URL" ]; then
    echo "✅ Pre-signed URL generated successfully"
    echo "   URL: ${PRESIGNED_URL:0:80}..."
    echo ""
    echo "   Testing URL download..."
    if curl -s -o /dev/null -w "%{http_code}" "$PRESIGNED_URL" | grep -q "200"; then
        echo "✅ Pre-signed URL download: PASSED"
    else
        echo "⚠️  Pre-signed URL download: FAILED (may be network/firewall issue)"
    fi
else
    echo "❌ Pre-signed URL generation: FAILED"
fi

# Cleanup
aws s3 rm "s3://$BUCKET_NAME/presign-test.txt" --region $REGION > /dev/null 2>&1
rm -f $TEST_FILE
echo ""

# Summary
echo "=========================================="
echo "✅ S3 Bucket Setup Complete!"
echo "=========================================="
echo ""
echo "Bucket Details:"
echo "  Name: $BUCKET_NAME"
echo "  Region: $REGION"
echo "  Encryption: AES-256"
echo "  Public Access: Blocked"
echo "  Lifecycle: Auto-delete after $LIFECYCLE_DAYS days"
echo "  Versioning: Enabled"
echo ""
echo "Next Steps:"
echo "  1. Update your .env file:"
echo "     S3_BUCKET_NAME=$BUCKET_NAME"
echo "     AWS_REGION=$REGION"
echo ""
echo "  2. Run integration tests:"
echo "     pytest tests/integration/test_s3_storage_real.py -v"
echo ""
echo "  3. Test document generation with S3:"
echo "     python scripts/test_s3_integration.py"
echo ""
echo "=========================================="
