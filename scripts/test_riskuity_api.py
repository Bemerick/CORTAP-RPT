"""
Test script for Riskuity API authentication and data fetching.

This script:
1. Authenticates with Riskuity using username/password
2. Gets an access token
3. Tests fetching assessments for a project
4. Displays the data structure

Usage:
    python scripts/test_riskuity_api.py --project-id 12345
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class RiskuityAuth:
    """Handle Riskuity authentication."""

    def __init__(self, base_url: str = "https://api.riskuity.com"):
        self.base_url = base_url.rstrip("/")
        self.token = None

    async def get_token(self, username: str, password: str, mfa_code: str = None) -> str:
        """
        Authenticate and retrieve the Riskuity access token.
        Supports two-step authentication with OTP for user accounts.

        Args:
            username: Riskuity username (email)
            password: Riskuity password
            mfa_code: Optional MFA/2FA code (6-digit)

        Returns:
            str: Access token

        Raises:
            Exception: If authentication fails
        """
        print(f"🔐 Authenticating with Riskuity as user: {username}")

        # Step 1: Initial authentication with email/password
        url = f"{self.base_url}/users/get-auth-token"
        payload = {"email": username, "password": password}

        async with httpx.AsyncClient() as client:
            try:
                # Step 1: Get initial response (may require OTP)
                print(f"   Step 1: Sending credentials...")
                response = await client.post(
                    url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    token_data = response.json()
                    status = token_data.get("status")

                    # Check if OTP is required
                    if status == "EMAIL_OTP":
                        print(f"   Status: {status} - OTP verification required")

                        if not mfa_code:
                            delivery = token_data.get("delivery", "email")
                            print(f"\n⚠️  OTP required! Check your {delivery} for the verification code.")
                            print(f"   Run again with: --mfa-code YOUR_CODE")
                            raise Exception("OTP required but not provided")

                        # Step 2: Submit OTP (needs password too)
                        print(f"   Step 2: Submitting OTP code: {mfa_code}")

                        otp_payload = {"email": username, "password": password, "otp": mfa_code}
                        otp_response = await client.post(
                            url,
                            json=otp_payload,
                            headers={
                                "Content-Type": "application/json",
                                "Accept": "application/json"
                            },
                            timeout=30.0
                        )

                        if otp_response.status_code == 200:
                            final_data = otp_response.json()
                            print(f"✅ Authentication successful!")

                            # Extract token
                            self.token = final_data.get("access_token") or final_data.get("token")

                            if self.token:
                                self._decode_and_display_token(self.token)
                                return self.token
                            else:
                                raise Exception("No token in response")
                        else:
                            error_msg = otp_response.text
                            print(f"❌ OTP verification failed: {otp_response.status_code}")
                            print(f"   Error: {error_msg}")
                            raise Exception(f"OTP verification failed: {otp_response.status_code}")

                    else:
                        # No OTP required (service account or OTP disabled)
                        print(f"✅ Authentication successful!")
                        self.token = token_data.get("access_token") or token_data.get("token")

                        if self.token:
                            self._decode_and_display_token(self.token)
                            return self.token
                        else:
                            raise Exception("No token in response")

                else:
                    error_msg = response.text
                    print(f"❌ Authentication failed: {response.status_code}")
                    print(f"   Error: {error_msg}")
                    raise Exception(f"Authentication failed: {response.status_code} - {error_msg}")

            except httpx.RequestError as e:
                print(f"❌ Network error: {str(e)}")
                raise

    def _decode_and_display_token(self, token: str):
        """Decode JWT token and display key information."""
        try:
            import base64

            # JWT format: header.payload.signature
            parts = token.split('.')
            if len(parts) != 3:
                return

            # Decode payload (add padding if needed)
            payload = parts[1]
            payload += '=' * (4 - len(payload) % 4)
            decoded = base64.urlsafe_b64decode(payload)
            payload_data = json.loads(decoded)

            print(f"\n📋 Token Information:")
            print(f"   User ID: {payload_data.get('user_id')}")
            print(f"   Tenant ID: {payload_data.get('tenant_id')}")
            print(f"   Email: {payload_data.get('email')}")
            print(f"   Is Superuser: {payload_data.get('is_superuser')}")

        except Exception as e:
            print(f"   (Could not decode token: {e})")


async def test_list_projects(token: str):
    """
    Test fetching all projects from Riskuity.

    Args:
        token: Riskuity access token

    Returns:
        list: List of projects or None if failed
    """
    print(f"\n📋 Fetching all projects...")

    # Based on Riskuity API documentation
    # The /projects/ endpoint requires query parameters: offset, limit, sort_by, get_role
    endpoints_to_try = [
        {
            "url": "https://api.riskuity.com/projects/tenant/",
            "params": None,
            "description": "GET /projects/tenant/ (WORKING)"
        },
        {
            "url": "https://api.riskuity.com/projects/",
            "params": {
                "offset": 0,
                "limit": 10,
                "sort_by": "name",
                "get_role": False  # Try boolean instead of string
            },
            "description": "GET /projects/ with boolean get_role"
        },
        {
            "url": "https://api.riskuity.com/projects/",
            "params": {
                "offset": 0,
                "limit": 10,
            },
            "description": "GET /projects/ minimal params"
        },
    ]

    async with httpx.AsyncClient() as client:
        for endpoint in endpoints_to_try:
            url = endpoint["url"]
            params = endpoint["params"]
            desc = endpoint["description"]

            print(f"\n   Trying: {desc}")
            print(f"   URL: {url}")
            if params:
                print(f"   Params: {params}")

            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }

            try:
                response = await client.get(url, headers=headers, params=params, timeout=30.0)

                if response.status_code == 200:
                    projects = response.json()
                    print(f"✅ Successfully fetched projects!")
                    print(f"   Count: {len(projects) if isinstance(projects, list) else 'N/A'}")
                    print(f"\n📄 Projects (first 5):")

                    if isinstance(projects, list):
                        for i, project in enumerate(projects[:5]):
                            print(f"\n   Project {i+1}:")
                            print(f"      ID: {project.get('id')}")
                            print(f"      Name: {project.get('name')}")
                            print(f"      Status: {project.get('status')}")
                            print(f"      Created: {project.get('created_at')}")
                    else:
                        print(json.dumps(projects, indent=2)[:1000])

                    if isinstance(projects, list) and len(projects) > 5:
                        print(f"\n   ... and {len(projects) - 5} more projects")

                    return projects
                else:
                    print(f"   ❌ Failed: {response.status_code}")
                    if response.status_code != 500:
                        print(f"   Error: {response.text[:500]}")

            except httpx.RequestError as e:
                print(f"   ❌ Network error: {str(e)}")
                continue

        print(f"\n❌ All endpoint variations failed")
        return None


async def test_list_assessments(token: str, project_id: int = None):
    """
    Test fetching assessments for a project.

    Args:
        token: Riskuity access token
        project_id: Project ID to fetch assessments for (optional - if None, lists all)
    """
    if project_id:
        print(f"\n📋 Fetching assessments for project {project_id}...")
    else:
        print(f"\n📋 Fetching all assessments...")

    # Based on Riskuity API documentation - use /projects/project_controls/{project_id}/
    if project_id:
        urls_to_try = [
            f"https://api.riskuity.com/projects/project_controls/{project_id}/",  # Get Project Controls By Project
            f"https://api.riskuity.com/assessments/?project_id={project_id}",
        ]
    else:
        urls_to_try = [
            "https://api.riskuity.com/assessments/",
        ]

    async with httpx.AsyncClient() as client:
        for url in urls_to_try:
            print(f"\n   Trying: {url}")
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }

            try:
                response = await client.get(url, headers=headers, timeout=30.0)

                if response.status_code == 200:
                    assessments = response.json()
                    print(f"✅ Successfully fetched assessments!")
                    print(f"   Count: {len(assessments) if isinstance(assessments, list) else 'N/A'}")
                    print(f"\n📄 Response structure (first 2):")
                    print(json.dumps(assessments[:2] if isinstance(assessments, list) else assessments, indent=2)[:1500])
                    if isinstance(assessments, list) and len(assessments) > 2:
                        print("   ...")
                    return assessments
                else:
                    print(f"   ❌ Failed: {response.status_code}")
                    if response.status_code != 500:  # Show error for non-500s
                        print(f"   Error: {response.text[:200]}")

            except httpx.RequestError as e:
                print(f"   ❌ Network error: {str(e)}")
                continue

        print(f"\n❌ All endpoint variations failed")
        return None


async def test_get_assessment_detail(token: str, assessment_id: int):
    """
    Test fetching a single assessment by ID.

    Args:
        token: Riskuity access token
        assessment_id: Assessment ID to fetch
    """
    print(f"\n🔍 Fetching assessment detail for ID {assessment_id}...")

    url = f"https://api.riskuity.com/assessments/{assessment_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)

            if response.status_code == 200:
                assessment = response.json()
                print(f"✅ Successfully fetched assessment detail!")
                print(f"\n📄 Assessment structure:")
                print(json.dumps(assessment, indent=2))
                return assessment
            else:
                print(f"❌ Failed to fetch assessment: {response.status_code}")
                print(f"   Error: {response.text}")
                return None

        except httpx.RequestError as e:
            print(f"❌ Network error: {str(e)}")
            return None


async def test_data_extraction(assessments: list):
    """
    Test extracting data from assessment structure.

    Args:
        assessments: List of assessment objects
    """
    if not assessments:
        print("\n⚠️  No assessments to analyze")
        return

    print(f"\n🔬 Analyzing assessment data structure...")

    first_assessment = assessments[0]

    # Extract key fields
    print(f"\n📊 Sample Assessment Fields:")
    print(f"   ID: {first_assessment.get('id')}")
    print(f"   Name: {first_assessment.get('name')}")
    print(f"   Status: {first_assessment.get('status')}")

    # Project control info
    project_control = first_assessment.get('project_control', {})
    if project_control:
        print(f"\n📁 Project Control Info:")
        print(f"   Project ID: {project_control.get('project', {}).get('id')}")
        print(f"   Project Name: {project_control.get('project', {}).get('name')}")
        print(f"   Control Family: {project_control.get('control_family', {}).get('name')}")
        print(f"   Control Name: {project_control.get('control', {}).get('name')}")

    # Group by control family
    from collections import defaultdict
    families = defaultdict(int)
    for assessment in assessments:
        family = assessment.get('project_control', {}).get('control_family', {}).get('name', 'Unknown')
        families[family] += 1

    print(f"\n📊 Control Family Distribution ({len(families)} families):")
    for family, count in sorted(families.items(), key=lambda x: -x[1])[:10]:
        print(f"   {family}: {count} controls")


async def main():
    """Main test function."""
    parser = argparse.ArgumentParser(
        description="Test Riskuity API integration",
        epilog="""
Examples:
  # Test with CI/CD account (no MFA)
  python3 scripts/test_riskuity_api.py --list-projects

  # Test with user account (with MFA)
  python3 scripts/test_riskuity_api.py --username your.email@dot.gov --mfa-code 123456 --list-projects

  # Test specific project
  python3 scripts/test_riskuity_api.py --username your.email@dot.gov --mfa-code 123456 --project-id 42
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--username", help="Riskuity username/email (uses RISKUITY_USERNAME env var if not provided)")
    parser.add_argument("--password", help="Riskuity password (uses RISKUITY_PASSWORD env var if not provided)")
    parser.add_argument("--mfa-code", help="MFA/2FA code (6 digits) for user accounts")
    parser.add_argument("--project-id", type=int, help="Project ID to test with")
    parser.add_argument("--assessment-id", type=int, help="Specific assessment ID to fetch detail")
    parser.add_argument("--list-projects", action="store_true", help="List all projects")
    args = parser.parse_args()

    print("🚀 Riskuity API Test Script")
    print("=" * 50)

    # Get credentials from command line or environment
    username = args.username or os.environ.get('RISKUITY_USERNAME', 'fedrisk_api_ci')
    password = args.password or os.environ.get('RISKUITY_PASSWORD')
    mfa_code = args.mfa_code

    if not password:
        print("❌ Password not provided")
        print("   Option 1: Set RISKUITY_PASSWORD environment variable")
        print("   Option 2: Use --password flag")
        return

    # Test authentication
    auth = RiskuityAuth()
    try:
        token = await auth.get_token(username, password, mfa_code)
    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}")
        return

    # Test listing projects
    if args.list_projects or (not args.project_id and not args.assessment_id):
        projects = await test_list_projects(token)

        if projects and isinstance(projects, list) and len(projects) > 0:
            print(f"\n💡 You can now test with a specific project:")
            print(f"   python3 scripts/test_riskuity_api.py --project-id {projects[0].get('id')}")

        # If projects failed, try listing all assessments
        if not projects:
            print(f"\n💡 Trying to list all assessments instead...")
            assessments = await test_list_assessments(token, None)

    # Test listing assessments
    if args.project_id:
        assessments = await test_list_assessments(token, args.project_id)

        if assessments:
            await test_data_extraction(assessments)

            # Test fetching a single assessment detail
            if isinstance(assessments, list) and len(assessments) > 0:
                first_id = assessments[0].get('id')
                if first_id:
                    await test_get_assessment_detail(token, first_id)

    # Test specific assessment detail
    if args.assessment_id:
        await test_get_assessment_detail(token, args.assessment_id)

    print("\n✅ Test complete!")


if __name__ == "__main__":
    asyncio.run(main())
