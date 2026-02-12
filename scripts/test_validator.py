#!/usr/bin/env python3
"""
Test script for JSON validator service.

Tests schema validation and completeness checking using real transformation output.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.validator import JsonValidator


async def test_validator():
    """Test JSON validator with real transformed data."""
    print("\n" + "=" * 80)
    print("JSON VALIDATOR TEST")
    print("=" * 80 + "\n")

    # Find latest transformation output
    output_dir = Path(__file__).parent.parent / "output"
    json_files = list(output_dir.glob("project_33_transformed_*.json"))

    if not json_files:
        print("❌ No transformation output files found")
        print(f"   Expected files in: {output_dir}")
        return False

    # Use latest file
    latest_file = sorted(json_files)[-1]
    print(f"📄 Loading: {latest_file.name}")

    with open(latest_file, 'r') as f:
        json_data = json.load(f)

    # Initialize validator
    print("\n🔧 Initializing JsonValidator...")
    validator = JsonValidator()

    # Test 1: Schema Validation
    print("\n" + "-" * 80)
    print("TEST 1: Schema Validation")
    print("-" * 80)

    validation_result = await validator.validate_json_schema(json_data)

    print(f"\n✓ Valid: {validation_result.valid}")
    print(f"✓ Errors: {len(validation_result.errors)}")
    print(f"✓ Warnings: {len(validation_result.warnings)}")

    if validation_result.errors:
        print("\n❌ Validation Errors:")
        for error in validation_result.errors[:10]:  # Show first 10
            print(f"   - {error}")

    if validation_result.warnings:
        print("\n⚠️  Validation Warnings:")
        for warning in validation_result.warnings:
            print(f"   - {warning}")

    # Test 2: Completeness Check (Draft Audit Report)
    print("\n" + "-" * 80)
    print("TEST 2: Completeness Check (Draft Audit Report)")
    print("-" * 80)

    completeness = await validator.check_completeness(
        json_data,
        template_id="draft-audit-report"
    )

    print(f"\n✓ Can Generate: {completeness.can_generate}")
    print(f"✓ Data Quality Score: {completeness.data_quality_score}%")
    print(f"✓ Missing Critical Fields: {len(completeness.missing_critical_fields)}")
    print(f"✓ Missing Optional Fields: {len(completeness.missing_optional_fields)}")

    if completeness.missing_critical_fields:
        print("\n❌ Missing Critical Fields:")
        for field in completeness.missing_critical_fields:
            print(f"   - {field}")

    if completeness.missing_optional_fields:
        print("\n⚠️  Missing Optional Fields:")
        for field in completeness.missing_optional_fields:
            print(f"   - {field}")

    # Test 3: Completeness Check (RIR Template)
    print("\n" + "-" * 80)
    print("TEST 3: Completeness Check (Recipient Information Request)")
    print("-" * 80)

    completeness_rir = await validator.check_completeness(
        json_data,
        template_id="recipient-information-request"
    )

    print(f"\n✓ Can Generate: {completeness_rir.can_generate}")
    print(f"✓ Data Quality Score: {completeness_rir.data_quality_score}%")
    print(f"✓ Missing Critical Fields: {len(completeness_rir.missing_critical_fields)}")
    print(f"✓ Missing Optional Fields: {len(completeness_rir.missing_optional_fields)}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    all_passed = (
        validation_result.valid
        and completeness.can_generate
        and completeness_rir.can_generate
    )

    if all_passed:
        print("\n✅ All validation tests PASSED")
        print(f"   - Schema validation: PASS")
        print(f"   - Draft Audit Report completeness: PASS ({completeness.data_quality_score}%)")
        print(f"   - RIR completeness: PASS ({completeness_rir.data_quality_score}%)")
    else:
        print("\n❌ Some validation tests FAILED")
        if not validation_result.valid:
            print(f"   - Schema validation: FAIL ({len(validation_result.errors)} errors)")
        if not completeness.can_generate:
            print(f"   - Draft Audit Report: FAIL (missing {len(completeness.missing_critical_fields)} critical fields)")
        if not completeness_rir.can_generate:
            print(f"   - RIR: FAIL (missing {len(completeness_rir.missing_critical_fields)} critical fields)")

    print()
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(test_validator())
    sys.exit(0 if success else 1)
