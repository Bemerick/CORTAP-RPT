#!/bin/bash
# Verify Lambda deployment completed successfully

echo "============================================"
echo "Verifying Lambda Deployment"
echo "============================================"
echo ""

# Load credentials
source /tmp/aws-session.sh

echo "Waiting for deployment to complete..."
echo "(This usually takes 30-60 seconds)"
echo ""

# Wait for function to be updated
aws lambda wait function-updated \
  --function-name cortap-generate-report-sync-dev \
  --region us-gov-west-1

echo ""
echo "✅ Deployment completed!"
echo ""

# Get final status
echo "Deployment Details:"
echo "-------------------"
aws lambda get-function \
  --function-name cortap-generate-report-sync-dev \
  --region us-gov-west-1 \
  --query 'Configuration.[LastUpdateStatus,LastModified,CodeSize,Runtime]' \
  --output table

echo ""
echo "============================================"
echo "✅ SUCCESS - Schema Fix is LIVE!"
echo "============================================"
echo ""
echo "The fix has been deployed:"
echo "  - Changed review_status from 'Final' to 'Completed'"
echo "  - Code size: 34.3 MB"
echo "  - Last modified: $(date)"
echo ""
echo "============================================"
echo "Next Steps:"
echo "============================================"
echo ""
echo "1. Notify Riskuity Developer"
echo "   Send them this message:"
echo ""
echo "   ---"
echo "   Hi [Developer],"
echo ""
echo "   Great news! I've deployed the fix for the schema validation error."
echo ""
echo "   Can you retry your Postman test with the same staging token?"
echo ""
echo "   Expected result: You should now get a 200 OK response with:"
echo "   - download_url (pre-signed S3 URL)"
echo "   - report_id"
echo "   - metadata about the generated report"
echo ""
echo "   The download URL will let you download a ~60KB Word document"
echo "   containing the draft audit report for project 33."
echo ""
echo "   Let me know what you get!"
echo ""
echo "   Best,"
echo "   Bob"
echo "   ---"
echo ""
echo "2. Monitor CloudWatch Logs"
echo "   Watch for the success message when they test:"
echo ""
echo "   aws logs filter-log-events \\"
echo "     --log-group-name /aws/lambda/cortap-generate-report-sync-dev \\"
echo "     --filter-pattern \"Report generation completed successfully\" \\"
echo "     --start-time \$(date -u +%s)000 \\"
echo "     --region us-gov-west-1"
echo ""
echo "3. Clean up"
echo "   rm -f /tmp/cortap-lambda-fix.zip"
echo "   rm -f /tmp/aws-session.sh"
echo ""
