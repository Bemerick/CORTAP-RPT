#!/bin/bash
# Check deployment status of schema fix

echo "============================================"
echo "CORTAP Lambda Deployment Status Check"
echo "============================================"
echo ""

# Check local build status
echo "✅ Local Status:"
echo "  - Fix committed: $(git log -1 --oneline | grep 'review_status')"
echo "  - Build completed: $(ls -lh .aws-sam/build/GenerateReportSyncFunction/app/services/data_transformer.py | awk '{print $5, $6, $7, $8}')"
echo "  - Fix in build: $(grep -c 'Completed' .aws-sam/build/GenerateReportSyncFunction/app/services/data_transformer.py) occurrence(s)"
echo ""

# Check AWS deployment status
echo "🔄 AWS Deployment Status:"
echo ""
echo "Checking AWS Lambda function..."

# Try to get function info
LAMBDA_STATUS=$(aws lambda get-function \
  --function-name cortap-generate-report-sync-dev \
  --profile govcloud-mfa \
  --region us-gov-west-1 \
  --query 'Configuration.[LastModified,LastUpdateStatus,CodeSha256]' \
  --output text 2>&1)

if echo "$LAMBDA_STATUS" | grep -q "ExpiredTokenException"; then
  echo ""
  echo "❌ AWS Session Expired"
  echo ""
  echo "You need to authenticate with AWS MFA first:"
  echo ""
  echo "  ./scripts/aws-mfa-login.ksh"
  echo ""
  echo "Then deploy with:"
  echo ""
  echo "  cd .aws-sam/build/GenerateReportSyncFunction"
  echo "  zip -r /tmp/cortap-lambda-fix.zip . -q"
  echo "  aws lambda update-function-code \\"
  echo "    --function-name cortap-generate-report-sync-dev \\"
  echo "    --zip-file fileb:///tmp/cortap-lambda-fix.zip \\"
  echo "    --profile govcloud-mfa \\"
  echo "    --region us-gov-west-1"
  echo "  cd ../../.."
  echo "  rm -f /tmp/cortap-lambda-fix.zip"
  echo ""
  exit 1
elif echo "$LAMBDA_STATUS" | grep -q "error"; then
  echo "❌ Error checking Lambda: $LAMBDA_STATUS"
  exit 1
else
  echo "✅ Lambda Status: $LAMBDA_STATUS"
  echo ""

  # Check last deployment time
  LAST_MODIFIED=$(echo "$LAMBDA_STATUS" | awk '{print $1}')
  echo "Last deployed: $LAST_MODIFIED"

  # Check if it was deployed after our commit
  COMMIT_TIME=$(git log -1 --format=%ai ce2a3d2)
  echo "Fix committed: $COMMIT_TIME"
  echo ""

  # Convert times to compare
  DEPLOY_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${LAST_MODIFIED%.*}" "+%s" 2>/dev/null)
  COMMIT_EPOCH=$(date -j -f "%Y-%m-%d %H:%M:%S" "${COMMIT_TIME% *}" "+%s" 2>/dev/null)

  if [ -n "$DEPLOY_EPOCH" ] && [ -n "$COMMIT_EPOCH" ]; then
    if [ $DEPLOY_EPOCH -gt $COMMIT_EPOCH ]; then
      echo "✅ Lambda has been deployed AFTER the fix was committed!"
      echo "   The fix should be live."
    else
      echo "⚠️  Lambda was deployed BEFORE the fix was committed."
      echo "   You need to deploy the update."
    fi
  fi
fi

echo ""
echo "============================================"
echo "Next Steps:"
echo "============================================"
echo ""
echo "If NOT deployed yet:"
echo "  1. Authenticate: ./scripts/aws-mfa-login.ksh"
echo "  2. Deploy: See commands above"
echo "  3. Verify: Run this script again"
echo ""
echo "If deployed:"
echo "  1. Ask Riskuity developer to retry their test"
echo "  2. They should get 200 OK with download URL"
echo "  3. Monitor CloudWatch logs for success"
echo ""
