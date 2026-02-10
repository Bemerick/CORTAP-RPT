"""
Integration tests for RIR document generation.

Tests the complete end-to-end flow:
1. Load canonical JSON from mock data files
2. Transform JSON to RIR context using RIRContextBuilder
3. Generate RIR document using DocumentGenerator
4. Verify document is created and contains expected data

This validates the architecture before Epic 3.5 (Data Service) is implemented.
"""

import json
import pytest
from pathlib import Path
from io import BytesIO

from app.services.document_generator import DocumentGenerator
from app.services.context_builder import RIRContextBuilder


# Test Fixtures

@pytest.fixture
def template_dir():
    """Path to templates directory."""
    return str(Path(__file__).parent.parent.parent / "app" / "templates")


@pytest.fixture
def mock_data_dir():
    """Path to mock data directory."""
    return Path(__file__).parent.parent.parent / "docs" / "schemas" / "mock-data"


@pytest.fixture
def output_dir(tmp_path):
    """Temporary directory for generated documents."""
    output = tmp_path / "generated_documents"
    output.mkdir()
    return output


@pytest.fixture
def generator(template_dir):
    """DocumentGenerator instance."""
    return DocumentGenerator(template_dir=template_dir)


# Helper Functions

def load_mock_json(mock_data_dir: Path, filename: str) -> dict:
    """Load a mock JSON file."""
    filepath = mock_data_dir / filename
    with open(filepath, 'r') as f:
        return json.load(f)


# Integration Tests

class TestRIRDocumentGeneration:
    """Test complete RIR document generation flow."""

    @pytest.mark.asyncio
    async def test_generate_rir_from_gnhtd_ct(
        self,
        generator,
        mock_data_dir,
        output_dir
    ):
        """
        Test RIR generation from Connecticut transit district mock data.

        Source: project-001-gnhtd-ct.json
        - Has 1 deficiency (Subrecipient Oversight)
        - Site visit dates: TBD
        - Virtual exit conference
        """
        # Load mock JSON
        json_data = load_mock_json(mock_data_dir, "project-001-gnhtd-ct.json")

        # Build RIR context
        context = RIRContextBuilder.build_context(json_data, correlation_id="test-gnhtd-ct")

        # Verify context has all required fields
        assert context["region_number"] == 1
        assert context["review_type"] == "Triennial Review"
        assert context["recipient_name"] == "Greater New Haven Transit District"
        assert context["recipient_acronym"] == "GNHTD"
        assert context["recipient_city_state"] == "Hamden, CT"
        assert context["recipient_id"] == "1337"
        assert context["contractor_name"] == "Qi Tech, LLC"
        assert context["lead_reviewer_name"] == "Bobby Killebrew"
        assert context["fta_program_manager_name"] == "Syed T. Ahmed"
        assert context["fta_program_manager_title"] == "General Engineer"
        assert context["site_visit_dates"] == "TBD"

        # Generate document
        document = await generator.generate(
            template_id="rir-package",
            context=context,
            correlation_id="test-gnhtd-ct"
        )

        # Verify document was generated
        assert isinstance(document, BytesIO)
        assert document.getbuffer().nbytes > 0

        # Save for manual inspection
        output_file = output_dir / "RIR_GNHTD_CT_1337.docx"
        with open(output_file, 'wb') as f:
            document.seek(0)
            f.write(document.read())

        assert output_file.exists()
        print(f"\n✓ Generated RIR document: {output_file}")

    @pytest.mark.asyncio
    async def test_generate_rir_from_mvrta_ma(
        self,
        generator,
        mock_data_dir,
        output_dir
    ):
        """
        Test RIR generation from Massachusetts RTA mock data.

        Source: project-002-mvrta-ma.json
        - No deficiencies (clean review)
        - Site visit dates: June 7, 2023 (specific date)
        - All 23 review areas: ND or NA
        """
        # Load mock JSON
        json_data = load_mock_json(mock_data_dir, "project-002-mvrta-ma.json")

        # Build RIR context
        context = RIRContextBuilder.build_context(json_data, correlation_id="test-mvrta-ma")

        # Verify context
        assert context["region_number"] == 1
        assert context["review_type"] == "Triennial Review"
        assert context["recipient_name"] == "Merrimack Valley Regional Transit Authority"
        assert context["recipient_acronym"] == "MVRTA"
        assert context["recipient_city_state"] == "Haverhill, MA"
        assert context["recipient_id"] == "1374"
        assert context["site_visit_dates"] == "June 7, 2023"

        # Generate document
        document = await generator.generate(
            template_id="rir-package",
            context=context,
            correlation_id="test-mvrta-ma"
        )

        # Verify document
        assert isinstance(document, BytesIO)
        assert document.getbuffer().nbytes > 0

        # Save for manual inspection
        output_file = output_dir / "RIR_MVRTA_MA_1374.docx"
        with open(output_file, 'wb') as f:
            document.seek(0)
            f.write(document.read())

        assert output_file.exists()
        print(f"\n✓ Generated RIR document: {output_file}")

    @pytest.mark.asyncio
    async def test_generate_rir_from_hrt_va(
        self,
        generator,
        mock_data_dir,
        output_dir
    ):
        """
        Test RIR generation from Virginia Hampton Roads mock data.

        Source: project-003-hrt-va.json
        - Has 2 deficiencies (Financial Management, Transit Asset Management)
        - Has 1 ERF (Enhanced Review Focus) item
        - Different region (Region 3 vs Region 1)
        - Different contractor
        - Review status: In Progress
        """
        # Load mock JSON
        json_data = load_mock_json(mock_data_dir, "project-003-hrt-va.json")

        # Build RIR context
        context = RIRContextBuilder.build_context(json_data, correlation_id="test-hrt-va")

        # Verify context
        assert context["region_number"] == 3
        assert context["review_type"] == "Triennial Review"
        assert context["recipient_name"] == "Transportation District Commission of Hampton Roads"
        assert context["recipient_acronym"] == "HRT"
        assert context["recipient_city_state"] == "Hampton, VA"
        assert context["recipient_id"] == "1456"
        assert context["contractor_name"] == "Calyptus Consulting Group, Inc."
        assert context["lead_reviewer_name"] == "Ellen Harvey"
        assert context["fta_program_manager_name"] == "Jason Yucis"
        assert context["fta_program_manager_title"] == "Financial Analyst"

        # Generate document
        document = await generator.generate(
            template_id="rir-package",
            context=context,
            correlation_id="test-hrt-va"
        )

        # Verify document
        assert isinstance(document, BytesIO)
        assert document.getbuffer().nbytes > 0

        # Save for manual inspection
        output_file = output_dir / "RIR_HRT_VA_1456.docx"
        with open(output_file, 'wb') as f:
            document.seek(0)
            f.write(document.read())

        assert output_file.exists()
        print(f"\n✓ Generated RIR document: {output_file}")

    @pytest.mark.asyncio
    async def test_generate_all_three_rir_documents(
        self,
        generator,
        mock_data_dir,
        output_dir
    ):
        """
        Test generating all 3 RIR documents in sequence.

        This validates that the template and generator work correctly
        with different data and can be reused multiple times.
        """
        mock_files = [
            ("project-001-gnhtd-ct.json", "RIR_GNHTD_CT_1337.docx"),
            ("project-002-mvrta-ma.json", "RIR_MVRTA_MA_1374.docx"),
            ("project-003-hrt-va.json", "RIR_HRT_VA_1456.docx")
        ]

        generated_documents = []

        for mock_file, output_name in mock_files:
            # Load mock JSON
            json_data = load_mock_json(mock_data_dir, mock_file)

            # Build context
            context = RIRContextBuilder.build_context(
                json_data,
                correlation_id=f"test-{mock_file}"
            )

            # Generate document
            document = await generator.generate(
                template_id="rir-package",
                context=context,
                correlation_id=f"test-{mock_file}"
            )

            # Save document
            output_file = output_dir / output_name
            with open(output_file, 'wb') as f:
                document.seek(0)
                f.write(document.read())

            generated_documents.append(output_file)

        # Verify all 3 documents were created
        assert len(generated_documents) == 3
        for doc_path in generated_documents:
            assert doc_path.exists()
            assert doc_path.stat().st_size > 0
            print(f"\n✓ Generated: {doc_path.name}")

    def test_context_includes_all_16_fields(self, mock_data_dir):
        """
        Test that context builder extracts all 16 required fields.

        Verifies the field mapping from canonical JSON schema to RIR template.
        """
        json_data = load_mock_json(mock_data_dir, "project-001-gnhtd-ct.json")
        context = RIRContextBuilder.build_context(json_data)

        required_fields = [
            "region_number",
            "review_type",
            "recipient_name",
            "recipient_city_state",
            "recipient_id",
            "recipient_website",
            "site_visit_dates",
            "contractor_name",
            "lead_reviewer_name",
            "lead_reviewer_phone",
            "lead_reviewer_email",
            "fta_program_manager_name",
            "fta_program_manager_title",  # The 16th field we added
            "fta_program_manager_phone",
            "fta_program_manager_email",
            "due_date"
        ]

        for field in required_fields:
            assert field in context, f"Missing required field: {field}"

        print(f"\n✓ All 16 fields present in context")


class TestRIRDateFormatting:
    """Test date formatting in RIR context."""

    def test_site_visit_date_formatting_from_iso(self, mock_data_dir):
        """Test that ISO dates are formatted correctly."""
        json_data = load_mock_json(mock_data_dir, "project-002-mvrta-ma.json")

        # Mock data has specific ISO dates
        assert json_data["project"]["site_visit_start_date"] == "2023-06-07"
        assert json_data["project"]["site_visit_end_date"] == "2023-06-07"

        # But also has pre-formatted string
        assert json_data["project"]["site_visit_dates"] == "June 7, 2023"

        context = RIRContextBuilder.build_context(json_data)

        # Should preserve the pre-formatted string
        assert context["site_visit_dates"] == "June 7, 2023"

    def test_site_visit_date_tbd_when_missing(self, mock_data_dir):
        """Test that missing dates default to TBD."""
        json_data = load_mock_json(mock_data_dir, "project-001-gnhtd-ct.json")

        # This project has TBD for site visit dates
        assert json_data["project"]["site_visit_dates"] == "TBD"
        assert json_data["project"]["site_visit_start_date"] is None
        assert json_data["project"]["site_visit_end_date"] is None

        context = RIRContextBuilder.build_context(json_data)

        assert context["site_visit_dates"] == "TBD"
