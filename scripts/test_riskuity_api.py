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

    async def get_token(self, username: str, password: str) -> str:
        """
        Authenticate and retrieve the Riskuity access token.

        Args:
            username: Riskuity username
            password: Riskuity password

        Returns:
            str: Access token

        Raises:
            Exception: If authentication fails
        """
        print(f"🔐 Authenticating with Riskuity as user: {username}")

        url = f"{self.base_url}/users/get-token"
        payload = {"username": username, "password": password}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30.0
                )

                if response.status_code == 200:
                    token_data = response.json()
                    print(f"✅ Authentication successful!")
                    print(f"   Token data: {json.dumps(token_data, indent=2)}")

                    # Extract token - adjust based on actual response structure
                    if isinstance(token_data, dict):
                        self.token = token_data.get("access_token") or token_data.get("token") or token_data
                    else:
                        self.token = token_data

                    return self.token
                else:
                    error_msg = response.text
                    print(f"❌ Authentication failed: {response.status_code}")
                    print(f"   Error: {error_msg}")
                    raise Exception(f"Authentication failed: {response.status_code} - {error_msg}")

            except httpx.RequestError as e:
                print(f"❌ Network error: {str(e)}")
                raise


async def test_list_assessments(token: str, project_id: int):
    """
    Test fetching assessments for a project.

    Args:
        token: Riskuity access token
        project_id: Project ID to fetch assessments for
    """
    print(f"\n📋 Fetching assessments for project {project_id}...")

    # Try different endpoint variations (with trailing slashes - API seems to require them)
    urls_to_try = [
        f"https://api.riskuity.com/assessments/?project_id={project_id}",  # With trailing slash
        f"https://api.riskuity.com/projects/{project_id}/assessments/",
        f"https://api.riskuity.com/assessments/",  # Try listing all
        f"https://api.riskuity.com/projects/assessments/{project_id}/",  # Alternative structure
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
    parser = argparse.ArgumentParser(description="Test Riskuity API integration")
    parser.add_argument("--project-id", type=int, help="Project ID to test with")
    parser.add_argument("--assessment-id", type=int, help="Specific assessment ID to fetch detail")
    args = parser.parse_args()

    print("🚀 Riskuity API Test Script")
    print("=" * 50)

    # Get credentials from environment
    username = os.environ.get('RISKUITY_USERNAME', 'fedrisk_api_ci')
    password = os.environ.get('RISKUITY_PASSWORD')

    if not password:
        print("❌ RISKUITY_PASSWORD not set in environment variables")
        print("   Set it in .env file or export RISKUITY_PASSWORD='your-password'")
        return

    # Test authentication
    auth = RiskuityAuth()
    try:
        token = await auth.get_token(username, password)
    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}")
        return

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
