#!/usr/bin/env python3
"""
Generate RIR Documents from Mock JSON Files

This script demonstrates the end-to-end RIR document generation flow:
1. Load canonical JSON from mock data files
2. Transform JSON to RIR context using RIRContextBuilder
3. Generate RIR document using DocumentGenerator
4. Save documents to output directory

Usage:
    python scripts/generate_rir_documents.py

Output:
    Generated documents saved to: output/rir-documents/
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.document_generator import DocumentGenerator
from app.services.context_builder import RIRContextBuilder
from app.utils.logging import get_logger

logger = get_logger(__name__)


def load_mock_json(filepath: Path) -> dict:
    """Load a mock JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


async def generate_rir_document(
    generator: DocumentGenerator,
    json_data: dict,
    output_path: Path,
    project_name: str
):
    """
    Generate a single RIR document from JSON data.

    Args:
        generator: DocumentGenerator instance
        json_data: Canonical project JSON
        output_path: Path to save the generated document
        project_name: Name for logging
    """
    try:
        # Build RIR context from JSON
        print(f"\n[{project_name}] Building RIR context...")
        context = RIRContextBuilder.build_context(
            json_data,
            correlation_id=f"script-{project_name}"
        )

        # Print context summary
        print(f"  Region: {context['region_number']}")
        print(f"  Review Type: {context['review_type']}")
        print(f"  Recipient: {context['recipient_name']}")
        print(f"  Location: {context['recipient_city_state']}")
        print(f"  Recipient ID: {context['recipient_id']}")
        print(f"  Lead Reviewer: {context['lead_reviewer_name']} ({context['contractor_name']})")
        print(f"  FTA PM: {context['fta_program_manager_name']} - {context['fta_program_manager_title']}")
        print(f"  Site Visit: {context['site_visit_dates']}")

        # Generate document
        print(f"\n[{project_name}] Generating RIR document...")
        document = await generator.generate(
            template_id="rir-package",
            context=context,
            correlation_id=f"script-{project_name}"
        )

        # Save document
        with open(output_path, 'wb') as f:
            document.seek(0)
            f.write(document.read())

        file_size = output_path.stat().st_size
        print(f"[{project_name}] ✓ Generated: {output_path.name} ({file_size:,} bytes)")

        return True

    except Exception as e:
        print(f"[{project_name}] ✗ Error: {str(e)}")
        logger.error(f"Failed to generate RIR for {project_name}", exc_info=True)
        return False


async def main():
    """Main script execution."""
    print("=" * 80)
    print("RIR Document Generator - Mock Data Test")
    print("=" * 80)

    # Setup paths
    project_root = Path(__file__).parent.parent
    mock_data_dir = project_root / "docs" / "schemas" / "mock-data"
    template_dir = project_root / "app" / "templates"
    output_dir = project_root / "output" / "rir-documents"

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nOutput directory: {output_dir}")

    # Initialize DocumentGenerator
    print(f"\nInitializing DocumentGenerator...")
    print(f"  Template directory: {template_dir}")
    generator = DocumentGenerator(template_dir=str(template_dir))

    # Define mock data files and output names
    projects = [
        {
            "file": "project-001-gnhtd-ct.json",
            "name": "GNHTD_CT",
            "output": "RIR_GNHTD_CT_1337_Triennial_Review.docx",
            "description": "Connecticut - Greater New Haven Transit District (1 deficiency)"
        },
        {
            "file": "project-002-mvrta-ma.json",
            "name": "MVRTA_MA",
            "output": "RIR_MVRTA_MA_1374_Triennial_Review.docx",
            "description": "Massachusetts - Merrimack Valley RTA (clean review)"
        },
        {
            "file": "project-003-hrt-va.json",
            "name": "HRT_VA",
            "output": "RIR_HRT_VA_1456_Triennial_Review.docx",
            "description": "Virginia - Hampton Roads Transit (2 deficiencies, 1 ERF)"
        }
    ]

    # Generate documents
    print(f"\n{'=' * 80}")
    print(f"Generating {len(projects)} RIR documents...")
    print(f"{'=' * 80}")

    results = []
    for project in projects:
        print(f"\n{'-' * 80}")
        print(f"Project: {project['description']}")
        print(f"Source: {project['file']}")
        print(f"{'-' * 80}")

        # Load JSON
        json_path = mock_data_dir / project['file']
        if not json_path.exists():
            print(f"✗ Error: Mock JSON file not found: {json_path}")
            results.append(False)
            continue

        json_data = load_mock_json(json_path)

        # Generate document
        output_path = output_dir / project['output']
        success = await generate_rir_document(
            generator,
            json_data,
            output_path,
            project['name']
        )
        results.append(success)

    # Summary
    print(f"\n{'=' * 80}")
    print(f"Generation Summary")
    print(f"{'=' * 80}")
    print(f"Total projects: {len(projects)}")
    print(f"Successful: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")

    if all(results):
        print(f"\n✓ All RIR documents generated successfully!")
        print(f"\nGenerated documents:")
        for project in projects:
            output_path = output_dir / project['output']
            if output_path.exists():
                size_kb = output_path.stat().st_size / 1024
                print(f"  - {output_path.name} ({size_kb:.1f} KB)")

        print(f"\nOutput directory: {output_dir}")
    else:
        print(f"\n✗ Some documents failed to generate. Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    # Run async main
    asyncio.run(main())
