#!/bin/bash
# Quick deployment script for schema fix

set -e

echo "============================================"
echo "Deploy CORTAP Lambda Schema Fix"
echo "============================================"
echo ""

# Check if MFA code provided
if [ -z "$1" ]; then
  echo "Usage: ./deploy-fix.sh <MFA_CODE>"
  echo ""
  echo "Example: ./deploy-fix.sh 123456"
  echo ""
  echo "Get your 6-digit MFA code from your authenticator app and run again."
  exit 1
fi

MFA_CODE=$1

echo "Step 1: Authenticating with AWS GovCloud..."
echo ""

# Get session token
CREDS=$(aws sts get-session-token \
  --serial-number arn:aws-us-gov:iam::736539455039:mfa/bob.emerick \
  --token-code $MFA_CODE \
  --duration-seconds 43200 \
  --region us-gov-west-1 2>&1)

# Check for errors
if echo "$CREDS" | grep -q "error occurred"; then
  echo "❌ Authentication failed:"
  echo "$CREDS"
  echo ""
  echo "Common issues:"
  echo "  - MFA code expired (get a new code and try again)"
  echo "  - MFA code already used (wait for next code)"
  echo "  - Wrong MFA device serial number"
  exit 1
fi

# Extract credentials
export AWS_ACCESS_KEY_ID=$(echo $CREDS | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo $CREDS | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(echo $CREDS | jq -r '.Credentials.SessionToken')

if [ -z "$AWS_ACCESS_KEY_ID" ] || [ "$AWS_ACCESS_KEY_ID" = "null" ]; then
  echo "❌ Failed to extract credentials"
  exit 1
fi

echo "✅ Authenticated successfully!"
echo ""

echo "Step 2: Creating deployment package..."
echo ""

cd .aws-sam/build/GenerateReportSyncFunction
zip -r /tmp/cortap-lambda-fix.zip . -q

PACKAGE_SIZE=$(ls -lh /tmp/cortap-lambda-fix.zip | awk '{print $5}')
echo "✅ Package created: $PACKAGE_SIZE"
echo ""

echo "Step 3: Deploying to Lambda..."
echo ""

aws lambda update-function-code \
  --function-name cortap-generate-report-sync-dev \
  --zip-file fileb:///tmp/cortap-lambda-fix.zip \
  --region us-gov-west-1

echo ""
echo "✅ Deployment initiated!"
echo ""

echo "Step 4: Waiting for deployment to complete..."
echo ""

aws lambda wait function-updated \
  --function-name cortap-generate-report-sync-dev \
  --region us-gov-west-1

echo "✅ Deployment complete!"
echo ""

# Clean up
cd ../../..
rm -f /tmp/cortap-lambda-fix.zip

echo "Step 5: Verifying deployment..."
echo ""

STATUS=$(aws lambda get-function \
  --function-name cortap-generate-report-sync-dev \
  --region us-gov-west-1 \
  --query 'Configuration.[LastUpdateStatus,LastModified,CodeSize]' \
  --output text)

echo "Lambda Status: $STATUS"
echo ""

echo "============================================"
echo "✅ DEPLOYMENT SUCCESSFUL!"
echo "============================================"
echo ""
echo "Next Steps:"
echo ""
echo "1. Notify Riskuity developer to retry their test"
echo "2. They should now get 200 OK with download URL"
echo "3. Monitor CloudWatch logs for success"
echo ""
echo "Test command for developer:"
echo ""
echo "curl -X POST 'https://qs5wkdxe8l.execute-api.us-gov-west-1.amazonaws.com/dev/api/v1/generate-report-sync' \\"
echo "  -H 'Authorization: Bearer <THEIR_TOKEN>' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"project_id\": 33, \"report_type\": \"draft_audit_report\"}'"
echo ""
