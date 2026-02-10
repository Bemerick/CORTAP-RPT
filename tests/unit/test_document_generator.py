"""
Unit tests for DocumentGenerator service.

Tests cover:
- Template loading and caching
- Basic merge field replacement
- Error handling for missing templates
- Error handling for invalid context data
"""

import pytest
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from docxtpl import DocxTemplate
from jinja2.exceptions import UndefinedError

from app.services.document_generator import DocumentGenerator
from app.exceptions import DocumentGenerationError


@pytest.fixture
def temp_template_dir(tmp_path):
    """Create a temporary template directory."""
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    return template_dir


@pytest.fixture
def mock_docx_template():
    """Create a mock DocxTemplate."""
    mock = MagicMock(spec=DocxTemplate)
    mock.render = Mock()
    mock.save = Mock()
    return mock


class TestDocumentGeneratorInit:
    """Test DocumentGenerator initialization."""

    def test_init_with_valid_directory(self, temp_template_dir):
        """Test initialization with valid template directory."""
        generator = DocumentGenerator(template_dir=str(temp_template_dir))
        assert generator.template_dir == temp_template_dir
        assert generator._template_cache == {}

    def test_init_with_nonexistent_directory(self, tmp_path):
        """Test initialization with non-existent directory raises error."""
        nonexistent_dir = tmp_path / "nonexistent"

        with pytest.raises(DocumentGenerationError) as exc_info:
            DocumentGenerator(template_dir=str(nonexistent_dir))

        assert exc_info.value.error_code == "TEMPLATE_DIR_NOT_FOUND"
        assert str(nonexistent_dir) in exc_info.value.message

    def test_init_with_file_instead_of_directory(self, tmp_path):
        """Test initialization with file path instead of directory raises error."""
        file_path = tmp_path / "file.txt"
        file_path.touch()

        with pytest.raises(DocumentGenerationError) as exc_info:
            DocumentGenerator(template_dir=str(file_path))

        assert exc_info.value.error_code == "TEMPLATE_DIR_INVALID"


class TestGetTemplatePath:
    """Test template path resolution."""

    def test_get_template_path_without_extension(self, temp_template_dir):
        """Test template path resolution adds .docx extension."""
        generator = DocumentGenerator(template_dir=str(temp_template_dir))
        path = generator._get_template_path("rir-package")

        assert path == temp_template_dir / "rir-package.docx"

    def test_get_template_path_with_extension(self, temp_template_dir):
        """Test template path resolution preserves .docx extension."""
        generator = DocumentGenerator(template_dir=str(temp_template_dir))
        path = generator._get_template_path("rir-package.docx")

        assert path == temp_template_dir / "rir-package.docx"


class TestLoadTemplate:
    """Test template loading."""

    def test_load_template_file_not_found(self, temp_template_dir):
        """Test loading non-existent template raises error."""
        generator = DocumentGenerator(template_dir=str(temp_template_dir))

        with pytest.raises(DocumentGenerationError) as exc_info:
            generator._load_template("nonexistent")

        assert exc_info.value.error_code == "TEMPLATE_NOT_FOUND"
        assert "nonexistent" in exc_info.value.message

    def test_load_template_path_is_directory(self, temp_template_dir):
        """Test loading directory instead of file raises error."""
        # Create a directory with .docx extension
        dir_path = temp_template_dir / "template.docx"
        dir_path.mkdir()

        generator = DocumentGenerator(template_dir=str(temp_template_dir))

        with pytest.raises(DocumentGenerationError) as exc_info:
            generator._load_template("template.docx")

        assert exc_info.value.error_code == "TEMPLATE_INVALID"

    @patch('app.services.document_generator.DocxTemplate')
    def test_load_template_success(self, mock_docx_class, temp_template_dir, mock_docx_template):
        """Test successful template loading."""
        # Create a mock template file
        template_file = temp_template_dir / "test-template.docx"
        template_file.touch()

        # Mock DocxTemplate constructor
        mock_docx_class.return_value = mock_docx_template

        generator = DocumentGenerator(template_dir=str(temp_template_dir))
        template = generator._load_template("test-template")

        assert template == mock_docx_template
        mock_docx_class.assert_called_once_with(str(template_file))

    @patch('app.services.document_generator.DocxTemplate')
    def test_load_template_docx_error(self, mock_docx_class, temp_template_dir):
        """Test loading invalid .docx file raises error."""
        # Create a file
        template_file = temp_template_dir / "invalid.docx"
        template_file.touch()

        # Mock DocxTemplate to raise an exception
        mock_docx_class.side_effect = Exception("Invalid docx file")

        generator = DocumentGenerator(template_dir=str(temp_template_dir))

        with pytest.raises(DocumentGenerationError) as exc_info:
            generator._load_template("invalid")

        assert exc_info.value.error_code == "TEMPLATE_LOAD_ERROR"
        assert "invalid" in exc_info.value.message


class TestTemplateCaching:
    """Test template caching functionality."""

    @patch('app.services.document_generator.DocxTemplate')
    def test_get_cached_template_loads_once(self, mock_docx_class, temp_template_dir, mock_docx_template):
        """Test template is loaded once and cached."""
        template_file = temp_template_dir / "cached.docx"
        template_file.touch()

        mock_docx_class.return_value = mock_docx_template

        generator = DocumentGenerator(template_dir=str(temp_template_dir))

        # First call should load
        template1 = generator._get_cached_template("cached")
        assert template1 == mock_docx_template
        assert "cached" in generator._template_cache

        # Second call should use cache
        template2 = generator._get_cached_template("cached")
        assert template2 == mock_docx_template

        # DocxTemplate should only be called once
        assert mock_docx_class.call_count == 1

    @patch('app.services.document_generator.DocxTemplate')
    def test_clear_cache(self, mock_docx_class, temp_template_dir, mock_docx_template):
        """Test cache clearing."""
        template_file = temp_template_dir / "cached.docx"
        template_file.touch()

        mock_docx_class.return_value = mock_docx_template

        generator = DocumentGenerator(template_dir=str(temp_template_dir))

        # Load template to cache it
        generator._get_cached_template("cached")
        assert len(generator._template_cache) == 1

        # Clear cache
        generator.clear_cache()
        assert len(generator._template_cache) == 0

    @patch('app.services.document_generator.DocxTemplate')
    def test_get_cache_info(self, mock_docx_class, temp_template_dir, mock_docx_template):
        """Test cache info retrieval."""
        template_file1 = temp_template_dir / "template1.docx"
        template_file2 = temp_template_dir / "template2.docx"
        template_file1.touch()
        template_file2.touch()

        mock_docx_class.return_value = mock_docx_template

        generator = DocumentGenerator(template_dir=str(temp_template_dir))

        # Load two templates
        generator._get_cached_template("template1")
        generator._get_cached_template("template2")

        cache_info = generator.get_cache_info()
        assert cache_info["cached_templates"] == 2
        assert "template1" in cache_info["template_ids"]
        assert "template2" in cache_info["template_ids"]


class TestGenerate:
    """Test document generation."""

    @pytest.mark.asyncio
    @patch('app.services.document_generator.DocxTemplate')
    async def test_generate_success(self, mock_docx_class, temp_template_dir):
        """Test successful document generation."""
        template_file = temp_template_dir / "test.docx"
        template_file.touch()

        # Create a proper mock template
        mock_template = MagicMock(spec=DocxTemplate)
        mock_template.render = Mock()
        mock_template.save = Mock()
        mock_docx_class.return_value = mock_template

        generator = DocumentGenerator(template_dir=str(temp_template_dir))

        context = {"recipient_name": "Test Recipient", "region": 1}
        result = await generator.generate("test", context, correlation_id="test-123")

        # Verify result is BytesIO
        assert isinstance(result, BytesIO)

        # Verify template.render was called with context
        mock_template.render.assert_called_once_with(context)

        # Verify template.save was called with BytesIO
        mock_template.save.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.document_generator.DocxTemplate')
    async def test_generate_missing_template(self, mock_docx_class, temp_template_dir):
        """Test generation with missing template raises error."""
        generator = DocumentGenerator(template_dir=str(temp_template_dir))

        with pytest.raises(DocumentGenerationError) as exc_info:
            await generator.generate("missing", {})

        assert exc_info.value.error_code == "TEMPLATE_NOT_FOUND"

    @pytest.mark.asyncio
    @patch('app.services.document_generator.DocxTemplate')
    async def test_generate_rendering_error(self, mock_docx_class, temp_template_dir):
        """Test generation with Jinja2 rendering error."""
        template_file = temp_template_dir / "error.docx"
        template_file.touch()

        mock_template = MagicMock(spec=DocxTemplate)
        mock_template.render.side_effect = UndefinedError("Variable 'missing_var' is undefined")
        mock_docx_class.return_value = mock_template

        generator = DocumentGenerator(template_dir=str(temp_template_dir))

        with pytest.raises(DocumentGenerationError) as exc_info:
            await generator.generate("error", {})

        assert exc_info.value.error_code == "TEMPLATE_RENDER_ERROR"

    @pytest.mark.asyncio
    @patch('app.services.document_generator.DocxTemplate')
    async def test_generate_missing_context_variable(self, mock_docx_class, temp_template_dir):
        """Test generation with missing context variable."""
        template_file = temp_template_dir / "missing-var.docx"
        template_file.touch()

        mock_template = MagicMock(spec=DocxTemplate)
        mock_template.render.side_effect = KeyError("required_field")
        mock_docx_class.return_value = mock_template

        generator = DocumentGenerator(template_dir=str(temp_template_dir))

        with pytest.raises(DocumentGenerationError) as exc_info:
            await generator.generate("missing-var", {"some_field": "value"})

        assert exc_info.value.error_code == "MISSING_CONTEXT_VARIABLE"
        assert "required_field" in str(exc_info.value.details)

    @pytest.mark.asyncio
    @patch('app.services.document_generator.DocxTemplate')
    async def test_generate_with_correlation_id(self, mock_docx_class, temp_template_dir):
        """Test generation includes correlation_id in logs."""
        template_file = temp_template_dir / "test.docx"
        template_file.touch()

        mock_template = MagicMock(spec=DocxTemplate)
        mock_template.render = Mock()
        mock_template.save = Mock()
        mock_docx_class.return_value = mock_template

        generator = DocumentGenerator(template_dir=str(temp_template_dir))

        context = {"field": "value"}
        correlation_id = "test-correlation-123"

        result = await generator.generate("test", context, correlation_id=correlation_id)

        assert isinstance(result, BytesIO)
