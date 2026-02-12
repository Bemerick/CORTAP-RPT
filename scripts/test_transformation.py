"""
Test script for end-to-end Riskuity data transformation.

This script:
1. Fetches project controls from Riskuity API for project 33
2. Transforms 494 controls into 21 FY26 review areas
3. Validates the output structure
4. Saves the result to a JSON file

Usage:
    python scripts/test_transformation.py
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from dotenv import load_dotenv

from app.services.riskuity_client import RiskuityClient
from app.services.data_transformer import DataTransformer

# Load environment variables
load_dotenv()


async def test_transformation():
    """Test end-to-end transformation of project 33 data."""

    print("=" * 80)
    print("🧪 RISKUITY DATA TRANSFORMATION TEST")
    print("=" * 80)
    print()

    # Configuration
    project_id = 33
    base_url = "https://api.riskuity.com"

    # Get authentication token from cache
    token_cache_file = Path(__file__).parent.parent / ".riskuity_token_cache.json"

    if not token_cache_file.exists():
        print("❌ No cached token found!")
        print(f"   Please run: python scripts/test_riskuity_api.py --list-projects")
        print(f"   This will authenticate and cache the token.")
        return

    with open(token_cache_file) as f:
        cache_data = json.load(f)
        token = cache_data.get("token")

    print(f"✅ Using cached token (expires: {cache_data.get('expires_at')})")
    print()

    # Step 1: Fetch project controls from Riskuity
    print("📥 Step 1: Fetching project controls from Riskuity API")
    print(f"   Project ID: {project_id}")
    print(f"   Endpoint: /projects/project_controls/{project_id}")

    async with httpx.AsyncClient(follow_redirects=True) as http_client:
        client = RiskuityClient(
            base_url=base_url,
            api_key=token,
            http_client=http_client,
            timeout=30.0
        )

        try:
            project_controls = await client.get_project_controls(
                project_id=project_id,
                limit=1000,
                correlation_id="test-transformation-001"
            )

            print(f"   ✅ Fetched {len(project_controls)} project controls")

            # Show sample control structure
            if project_controls:
                sample = project_controls[0]
                print(f"\n   Sample control structure:")
                print(f"      Control ID: {sample.get('id')}")
                print(f"      Control Name: {sample.get('control', {}).get('name', 'N/A')}")
                print(f"      Assessment Status: {sample.get('assessment', {}).get('status', 'N/A')}")

        except Exception as e:
            print(f"   ❌ Failed to fetch project controls: {str(e)}")
            return

    print()

    # Step 2: Transform data using DataTransformer
    print("🔄 Step 2: Transforming data to canonical JSON schema")
    print(f"   Input: {len(project_controls)} project controls")
    print(f"   Target: 21 FY26 review areas")

    transformer = DataTransformer()

    # Prepare project metadata (these would normally come from config or user input)
    project_metadata = {
        "region_number": 1,
        "review_type": "Triennial Review",
        "recipient_name": "CORTAP FY26 Assessment Test",
        "recipient_acronym": "TEST",
        "recipient_city_state": "Washington, DC",
        "recipient_id": str(project_id),
        "site_visit_dates": "TBD",
        "exit_conference_format": "virtual",
        "lead_reviewer_name": "Test Reviewer",
        "contractor_name": "Test Contractor",
        "lead_reviewer_phone": "555-1234",
        "lead_reviewer_email": "test@example.com",
        "fta_program_manager_name": "Test PM",
        "fta_program_manager_title": "Program Manager",
        "fta_program_manager_phone": "555-5678",
        "fta_program_manager_email": "pm@dot.gov",
    }

    try:
        canonical_json = transformer.transform(
            project_id=project_id,
            riskuity_project_controls=project_controls,
            project_metadata=project_metadata,
            correlation_id="test-transformation-001"
        )

        print(f"   ✅ Transformation complete!")
        print(f"   Output review areas: {len(canonical_json['assessments'])}")
        print(f"   Has deficiencies: {canonical_json['metadata']['has_deficiencies']}")
        print(f"   Deficiency count: {canonical_json['metadata']['deficiency_count']}")

    except Exception as e:
        print(f"   ❌ Transformation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return

    print()

    # Step 3: Validate output structure
    print("✅ Step 3: Validating output structure")

    # Check required fields
    required_fields = ["project_id", "generated_at", "data_version", "project",
                      "contractor", "fta_program_manager", "assessments", "metadata"]

    for field in required_fields:
        if field in canonical_json:
            print(f"   ✅ {field}: present")
        else:
            print(f"   ❌ {field}: MISSING")

    # Validate assessments
    print(f"\n   Review Areas Found ({len(canonical_json['assessments'])}):")
    review_areas_by_finding = {"D": [], "ND": [], "NA": []}

    for assessment in sorted(canonical_json['assessments'], key=lambda x: x['review_area']):
        finding = assessment['finding']
        review_area = assessment['review_area']
        review_areas_by_finding[finding].append(review_area)

        status_icon = {"D": "🔴", "ND": "🟢", "NA": "⚪"}[finding]
        print(f"      {status_icon} {finding:2} | {review_area}")

    print(f"\n   Summary:")
    print(f"      Deficient (D): {len(review_areas_by_finding['D'])} areas")
    print(f"      Non-Deficient (ND): {len(review_areas_by_finding['ND'])} areas")
    print(f"      Not Applicable (NA): {len(review_areas_by_finding['NA'])} areas")

    print()

    # Step 4: Save output to file
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"project_{project_id}_transformed_{timestamp}.json"

    print(f"💾 Step 4: Saving output to file")
    print(f"   Output file: {output_file}")

    try:
        with open(output_file, 'w') as f:
            json.dump(canonical_json, f, indent=2)

        file_size = output_file.stat().st_size / 1024  # KB
        print(f"   ✅ Saved successfully ({file_size:.1f} KB)")

    except Exception as e:
        print(f"   ❌ Failed to save file: {str(e)}")
        return

    print()
    print("=" * 80)
    print("✅ TRANSFORMATION TEST COMPLETE")
    print("=" * 80)
    print()
    print(f"Summary:")
    print(f"  • Input: {len(project_controls)} project controls")
    print(f"  • Output: {len(canonical_json['assessments'])} review areas")
    print(f"  • Deficiencies: {canonical_json['metadata']['deficiency_count']}")
    print(f"  • Output file: {output_file}")
    print()


if __name__ == "__main__":
    asyncio.run(test_transformation())
