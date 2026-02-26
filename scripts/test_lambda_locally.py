#!/usr/bin/env python3
"""
Test the Lambda handler locally to diagnose 502 errors.

This simulates what happens when API Gateway invokes the Lambda function.
"""

import json
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set environment variables (simulating Lambda environment)
os.environ.setdefault("ENVIRONMENT", "dev")
os.environ.setdefault("LOG_LEVEL", "DEBUG")
os.environ.setdefault("S3_BUCKET_NAME", "cortap-documents-dev-736539455039")
os.environ.setdefault("RISKUITY_API_URL", "https://api.riskuity.com")
os.environ.setdefault("TEMPLATE_DIR", "app/templates")
os.environ.setdefault("PROJECT_CONFIG_PATH", "config/project-setup.json")

try:
    # Test imports
    print("Testing imports...")
    from app.handlers.generate_sync_handler import lambda_handler
    print("✅ Lambda handler imported successfully")

    from app.main import app
    print("✅ FastAPI app imported successfully")

    from app.config import settings
    print("✅ Settings imported successfully")
    print(f"   - S3 Bucket: {settings.s3_bucket_name}")
    print(f"   - Template Dir: {settings.template_dir}")
    print(f"   - Environment: {settings.environment}")

    # Test handler with a simple event
    print("\nTesting Lambda handler with health check...")

    # Simulate API Gateway REST API event (not HTTP API v2)
    event = {
        "resource": "/health",
        "path": "/health",
        "httpMethod": "GET",
        "headers": {
            "Accept": "application/json"
        },
        "queryStringParameters": None,
        "pathParameters": None,
        "body": None,
        "isBase64Encoded": False,
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "test",
            "protocol": "HTTP/1.1",
            "httpMethod": "GET",
            "path": "/dev/health",
            "stage": "dev",
            "requestId": "test-request",
            "requestTime": "01/Jan/2024:00:00:00 +0000",
            "requestTimeEpoch": 1704067200000,
            "identity": {
                "sourceIp": "127.0.0.1"
            }
        }
    }

    # Mock context
    class MockContext:
        function_name = "test"
        memory_limit_in_mb = 2048
        invoked_function_arn = "arn:aws:lambda:us-gov-west-1:123456789012:function:test"
        aws_request_id = "test-request-id"

    context = MockContext()

    # Invoke handler
    print("Invoking handler...")
    response = lambda_handler(event, context)

    print(f"\n✅ Handler executed successfully!")
    print(f"Status Code: {response.get('statusCode')}")
    print(f"Response: {json.dumps(response, indent=2)}")

    # Test with actual API endpoint (would need token)
    print("\n" + "="*50)
    print("To test the actual report generation endpoint, you need:")
    print("1. A valid Riskuity token (Bearer token)")
    print("2. Run this command:")
    print("\npython scripts/test_lambda_locally.py --test-generate --token 'Bearer <token>'")

except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\nThis usually means:")
    print("1. Missing dependencies in requirements.txt")
    print("2. Missing files in the Lambda package")
    print("3. Incorrect Python path")
    sys.exit(1)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*50)
print("All basic tests passed! ✅")
print("\nIf this works locally but fails in AWS, check:")
print("1. Lambda environment variables are set correctly")
print("2. Lambda has permissions to access S3")
print("3. Lambda package includes all necessary files")
print("4. Lambda timeout is sufficient (120s)")
