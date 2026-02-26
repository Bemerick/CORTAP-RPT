#!/bin/bash
set -e

echo "Moving large directories out of the way..."
[ -d output ] && mv output /tmp/cortap-output-backup-$$ || true
[ -d docs ] && mv docs /tmp/cortap-docs-backup-$$ || true

echo "Cleaning previous build..."
rm -rf .aws-sam

echo "Building Lambda package..."
sam build

echo "Restoring directories..."
[ -d /tmp/cortap-output-backup-$$ ] && mv /tmp/cortap-output-backup-$$ output || true
[ -d /tmp/cortap-docs-backup-$$ ] && mv /tmp/cortap-docs-backup-$$ docs || true

echo "Build complete!"
du -sh .aws-sam/build/GenerateReportSyncFunction
