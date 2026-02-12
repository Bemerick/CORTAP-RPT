"""
Lambda handler for synchronous report generation.

This handler wraps the FastAPI endpoint for deployment as a Lambda Function URL.
Supports both direct Lambda invocation and HTTP requests via Function URL.
"""

import json
import base64
from typing import Dict, Any

from mangum import Mangum
from app.main import app


# Create Mangum adapter for FastAPI
handler = Mangum(app, lifespan="off")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for synchronous report generation.

    This handler supports two invocation patterns:
    1. Lambda Function URL (HTTP): Proxies HTTP requests to FastAPI
    2. Direct Lambda invocation: For testing or internal use

    Args:
        event: Lambda event (HTTP request or direct invocation)
        context: Lambda context

    Returns:
        dict: HTTP response or direct response

    Example Event (Function URL):
        {
            "requestContext": {"http": {"method": "POST", "path": "/..."}},
            "headers": {"Authorization": "Bearer ..."},
            "body": '{"project_id": 33, "report_type": "draft_audit_report"}'
        }

    Example Event (Direct Invocation):
        {
            "project_id": 33,
            "report_type": "draft_audit_report",
            "token": "Bearer ..."
        }
    """
    # Check if this is an HTTP request (Function URL)
    if "requestContext" in event and "http" in event.get("requestContext", {}):
        # HTTP request via Function URL - use Mangum adapter
        return handler(event, context)

    # Direct Lambda invocation - convert to HTTP format
    try:
        # Extract parameters
        project_id = event.get("project_id")
        report_type = event.get("report_type", "draft_audit_report")
        token = event.get("token", "")

        if not project_id:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "missing_project_id",
                    "message": "project_id is required"
                })
            }

        if not token:
            return {
                "statusCode": 401,
                "body": json.dumps({
                    "error": "missing_token",
                    "message": "token is required for authentication"
                })
            }

        # Convert to HTTP request format for FastAPI
        http_event = {
            "requestContext": {
                "http": {
                    "method": "POST",
                    "path": "/api/v1/generate-report-sync"
                }
            },
            "headers": {
                "Authorization": token if token.startswith("Bearer") else f"Bearer {token}",
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "project_id": project_id,
                "report_type": report_type
            }),
            "isBase64Encoded": False
        }

        # Process through FastAPI
        response = handler(http_event, context)

        # Parse response
        if response.get("isBase64Encoded"):
            body = base64.b64decode(response["body"]).decode("utf-8")
        else:
            body = response["body"]

        result = json.loads(body)

        # Return direct response (without HTTP wrapping)
        return {
            "statusCode": response["statusCode"],
            "result": result
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "handler_error",
                "message": str(e)
            })
        }
