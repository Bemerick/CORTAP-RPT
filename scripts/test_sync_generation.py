#!/usr/bin/env python3
"""
Integration test script for synchronous report generation endpoint.

This script tests the complete end-to-end flow with real Riskuity data:
1. Authenticate with Riskuity
2. Call the /generate-report-sync endpoint
3. Download the generated document
4. Verify the output

Usage:
    python3 scripts/test_sync_generation.py --project-id 33
    python3 scripts/test_sync_generation.py --project-id 33 --report-type recipient_information_request
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import authentication from test_riskuity_api
from scripts.test_riskuity_api import RiskuityAuth


class SyncGenerationTester:
    """Test synchronous report generation endpoint."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize tester.

        Args:
            base_url: Base URL of CORTAP-RPT service (default: localhost)
        """
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=180.0)  # 3 min timeout

    async def test_generation(
        self,
        project_id: int,
        report_type: str,
        token: str
    ) -> dict:
        """
        Test synchronous report generation.

        Args:
            project_id: Riskuity project ID
            report_type: Report template type
            token: Riskuity Bearer token

        Returns:
            dict: Response from generation endpoint

        Raises:
            Exception: On generation failure
        """
        print(f"\n{'='*80}")
        print(f"Testing Synchronous Report Generation")
        print(f"{'='*80}")
        print(f"Project ID: {project_id}")
        print(f"Report Type: {report_type}")
        print(f"Endpoint: {self.base_url}/api/v1/generate-report-sync")
        print(f"{'='*80}\n")

        # Prepare request
        request_data = {
            "project_id": project_id,
            "report_type": report_type
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        print(f"⏳ Starting generation (this will take 30-60 seconds)...")
        print(f"   Please wait...\n")

        start_time = time.time()

        try:
            # Make request
            response = await self.client.post(
                f"{self.base_url}/api/v1/generate-report-sync",
                json=request_data,
                headers=headers
            )

            elapsed = time.time() - start_time

            print(f"⏱️  Request completed in {elapsed:.1f} seconds\n")

            # Check status
            if response.status_code == 200:
                result = response.json()
                self._print_success_response(result, elapsed)
                return result

            else:
                error = response.json()
                self._print_error_response(response.status_code, error)
                raise Exception(f"Generation failed: {error.get('detail', {}).get('message', 'Unknown error')}")

        except httpx.TimeoutException:
            elapsed = time.time() - start_time
            print(f"❌ Request timed out after {elapsed:.1f} seconds")
            print(f"   The generation may still be running on the server.")
            raise

        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Request failed after {elapsed:.1f} seconds")
            print(f"   Error: {str(e)}")
            raise

    def _print_success_response(self, result: dict, elapsed: float):
        """Print formatted success response."""
        print(f"✅ Generation Successful!\n")
        print(f"{'─'*80}")
        print(f"Report Details:")
        print(f"{'─'*80}")
        print(f"  Report ID:       {result['report_id']}")
        print(f"  Project ID:      {result['project_id']}")
        print(f"  Report Type:     {result['report_type']}")
        print(f"  Status:          {result['status']}")
        print(f"  Generated At:    {result['generated_at']}")
        print(f"  Expires At:      {result['expires_at']}")
        print(f"  File Size:       {result['file_size_bytes']:,} bytes ({result['file_size_bytes'] / 1024:.1f} KB)")
        print(f"  Correlation ID:  {result['correlation_id']}")

        print(f"\n{'─'*80}")
        print(f"Metadata:")
        print(f"{'─'*80}")
        meta = result['metadata']
        print(f"  Recipient:       {meta['recipient_name']}")
        print(f"  Review Type:     {meta['review_type']}")
        print(f"  Review Areas:    {meta['review_areas']}")
        print(f"  Deficiencies:    {meta['deficiency_count']}")
        print(f"  Generation Time: {meta['generation_time_ms']:,} ms ({meta['generation_time_ms'] / 1000:.1f}s)")

        print(f"\n{'─'*80}")
        print(f"Performance Breakdown:")
        print(f"{'─'*80}")
        gen_time = meta['generation_time_ms'] / 1000
        print(f"  Total Request:   {elapsed:.1f}s (100%)")
        print(f"  Backend Work:    {gen_time:.1f}s ({gen_time/elapsed*100:.0f}%)")
        print(f"  Network/Overhead: {elapsed - gen_time:.1f}s ({(elapsed - gen_time)/elapsed*100:.0f}%)")

        print(f"\n{'─'*80}")
        print(f"Download URL:")
        print(f"{'─'*80}")
        print(f"  {result['download_url'][:100]}...")
        print(f"\n💾 You can download the document using the URL above")
        print(f"   (URL expires in 24 hours)")

    def _print_error_response(self, status_code: int, error: dict):
        """Print formatted error response."""
        print(f"❌ Generation Failed (Status: {status_code})\n")

        detail = error.get('detail', {})
        if isinstance(detail, dict):
            print(f"{'─'*80}")
            print(f"Error Details:")
            print(f"{'─'*80}")
            print(f"  Error Code:      {detail.get('error', 'N/A')}")
            print(f"  Message:         {detail.get('message', 'N/A')}")
            print(f"  Timestamp:       {detail.get('timestamp', 'N/A')}")
            print(f"  Correlation ID:  {detail.get('correlation_id', 'N/A')}")

            if 'details' in detail:
                print(f"\n{'─'*80}")
                print(f"Additional Details:")
                print(f"{'─'*80}")
                for key, value in detail['details'].items():
                    if isinstance(value, list):
                        print(f"  {key}:")
                        for item in value[:5]:  # First 5 items
                            print(f"    - {item}")
                        if len(value) > 5:
                            print(f"    ... and {len(value) - 5} more")
                    else:
                        print(f"  {key}: {value}")
        else:
            print(f"  {detail}")

    async def download_document(self, download_url: str, output_path: str):
        """
        Download generated document.

        Args:
            download_url: Presigned S3 URL
            output_path: Local path to save document
        """
        print(f"\n{'='*80}")
        print(f"Downloading Document")
        print(f"{'='*80}\n")

        try:
            print(f"⏳ Downloading from S3...")
            response = await self.client.get(download_url)
            response.raise_for_status()

            # Save to file
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'wb') as f:
                f.write(response.content)

            file_size = len(response.content)
            print(f"✅ Document downloaded successfully!")
            print(f"   Saved to: {output_file}")
            print(f"   File size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")

        except Exception as e:
            print(f"❌ Download failed: {str(e)}")
            raise

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


async def main():
    """Main test function."""
    parser = argparse.ArgumentParser(
        description="Test synchronous report generation endpoint"
    )
    parser.add_argument(
        "--project-id",
        type=int,
        default=33,
        help="Riskuity project ID (default: 33)"
    )
    parser.add_argument(
        "--report-type",
        choices=["draft_audit_report", "recipient_information_request"],
        default="draft_audit_report",
        help="Report type to generate"
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="CORTAP-RPT service base URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download the generated document"
    )
    parser.add_argument(
        "--output",
        default="output/test_generation",
        help="Output directory for downloaded document"
    )

    args = parser.parse_args()

    # Check environment
    riskuity_email = os.getenv("RISKUITY_EMAIL")
    riskuity_password = os.getenv("RISKUITY_PASSWORD")

    if not riskuity_email or not riskuity_password:
        print("❌ Error: RISKUITY_EMAIL and RISKUITY_PASSWORD must be set in .env")
        print("\nPlease add to your .env file:")
        print("  RISKUITY_EMAIL=your.email@example.com")
        print("  RISKUITY_PASSWORD=your_password")
        sys.exit(1)

    try:
        # Step 1: Authenticate with Riskuity
        print(f"\n{'='*80}")
        print(f"Step 1: Authenticate with Riskuity")
        print(f"{'='*80}\n")

        auth = RiskuityAuth(base_url="https://app.riskuity.com")
        token = await auth.get_token(
            username=riskuity_email,
            password=riskuity_password
        )

        if not token:
            print("❌ Failed to get Riskuity token")
            sys.exit(1)

        print(f"✅ Successfully authenticated with Riskuity\n")

        # Step 2: Test generation endpoint
        print(f"{'='*80}")
        print(f"Step 2: Call Generation Endpoint")
        print(f"{'='*80}\n")

        tester = SyncGenerationTester(base_url=args.base_url)

        try:
            result = await tester.test_generation(
                project_id=args.project_id,
                report_type=args.report_type,
                token=token
            )

            # Step 3: Optionally download document
            if args.download and result:
                print(f"\n{'='*80}")
                print(f"Step 3: Download Document")
                print(f"{'='*80}\n")

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{args.report_type}_{args.project_id}_{timestamp}.docx"
                output_path = Path(args.output) / filename

                await tester.download_document(
                    download_url=result['download_url'],
                    output_path=str(output_path)
                )

            # Summary
            print(f"\n{'='*80}")
            print(f"Test Complete! ✅")
            print(f"{'='*80}\n")

            if args.download:
                print(f"📄 Document saved to: {output_path}")
            else:
                print(f"💡 Tip: Use --download to automatically download the document")

        finally:
            await tester.close()

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
