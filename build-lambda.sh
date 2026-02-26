#!/bin/bash
set -e

echo "Moving large directories out of the way..."
echo "  - output/ (generated reports)"
[ -d output ] && mv output /tmp/cortap-output-backup-$$ || true
echo "  - docs/ (project documentation - not needed for Lambda)"
[ -d docs ] && mv docs /tmp/cortap-docs-backup-$$ || true

echo "Cleaning previous build..."
rm -rf .aws-sam

echo "Building Lambda package..."
echo "  Note: docs/ excluded to reduce package size"
echo "  Runtime assets are in app/schemas/, app/templates/, config/"
sam build

echo "Restoring directories..."
[ -d /tmp/cortap-output-backup-$$ ] && mv /tmp/cortap-output-backup-$$ output || true
[ -d /tmp/cortap-docs-backup-$$ ] && mv /tmp/cortap-docs-backup-$$ docs || true

echo ""
echo "Build complete!"
du -sh .aws-sam/build/GenerateReportSyncFunction
