#!/bin/bash
# Simple deployment using default credentials

set -e

echo "============================================"
echo "Deploy CORTAP Lambda Schema Fix"
echo "============================================"
echo ""

# Get MFA code
if [ -z "$1" ]; then
  echo "Usage: ./quick-deploy.sh <MFA_CODE>"
  echo ""
  echo "Get fresh 6-digit code from authenticator app"
  exit 1
fi

MFA_CODE=$1

echo "Step 1: Getting session token..."
echo ""

# Use default profile to get session
CREDS=$(aws sts get-session-token \
  --serial-number arn:aws-us-gov:iam::736539455039:mfa/bob \
  --token-code $MFA_CODE \
  --duration-seconds 43200 \
  --region us-gov-west-1 \
  --output json 2>&1)

# Check for errors
if echo "$CREDS" | grep -q "error occurred"; then
  echo "❌ Failed to get session token:"
  echo "$CREDS"
  echo ""
  echo "Troubleshooting:"
  echo "  - Get a FRESH MFA code (they expire every 30 seconds)"
  echo "  - Make sure you're using the code from your AWS GovCloud MFA device"
  exit 1
fi

# Extract and export credentials
export AWS_ACCESS_KEY_ID=$(echo $CREDS | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo $CREDS | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(echo $CREDS | jq -r '.Credentials.SessionToken')

if [ "$AWS_ACCESS_KEY_ID" = "null" ]; then
  echo "❌ Failed to parse credentials"
  echo "$CREDS"
  exit 1
fi

echo "✅ Authenticated!"
EXPIRY=$(echo $CREDS | jq -r '.Credentials.Expiration')
echo "   Valid until: $EXPIRY"
echo ""

echo "Step 2: Deploying Lambda function..."
echo ""

# Deploy (package already created)
aws lambda update-function-code \
  --function-name cortap-generate-report-sync-dev \
  --zip-file fileb:///tmp/cortap-lambda-fix.zip \
  --region us-gov-west-1

echo ""
echo "Step 3: Waiting for update to complete..."
aws lambda wait function-updated \
  --function-name cortap-generate-report-sync-dev \
  --region us-gov-west-1

echo ""
echo "✅ Deployment complete!"
echo ""

# Verify
STATUS=$(aws lambda get-function \
  --function-name cortap-generate-report-sync-dev \
  --region us-gov-west-1 \
  --query 'Configuration.[LastUpdateStatus,LastModified]' \
  --output text)

echo "Status: $STATUS"
echo ""
echo "============================================"
echo "✅ SUCCESS - Fix is now deployed!"
echo "============================================"
echo ""
echo "Next: Tell Riskuity developer to retry their test"
echo "Expected: 200 OK with download URL"
echo ""

# Clean up
rm -f /tmp/cortap-lambda-fix.zip
echo "Cleaned up deployment package"
