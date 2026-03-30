"""Integration tests for cross-format consistency.

These tests validate that all document formats (OpenAPI, RAML, Smithy)
work consistently and follow the same patterns.

**Validates: Requirements 15.1, 15.2, 15.3, 15.4, 15.5**
"""

import pytest
from pylaag.core.errors import LaagError, ParseError, ValidationError

# Import all document types
try:
    from pylaag.openapi import OpenAPIDocument

    OPENAPI_AVAILABLE = True
except ImportError:
    OPENAPI_AVAILABLE = False

try:
    from pylaag.raml import RAMLDocument

    RAML_AVAILABLE = True
except ImportError:
    RAML_AVAILABLE = False

try:
    from pylaag.smithy import SmithyDocument

    SMITHY_AVAILABLE = True
except ImportError:
    SMITHY_AVAILABLE = False


class TestDocumentCreation:
    """Test creating documents in all formats."""

    @pytest.mark.skipif(not OPENAPI_AVAILABLE, reason="OpenAPI package not available")
    def test_create_openapi_document(self):
        """Test creating an OpenAPI document with default values."""
        doc = OpenAPIDocument()

        # Verify document has required fields
        assert "openapi" in doc.to_dict()
        assert "info" in doc.to_dict()
        assert "paths" in doc.to_dict()

        # Verify document validates
        doc.validate()  # Should not raise

        # Verify properties work
        assert doc.openapi_version == "3.0.0"
        assert isinstance(doc.info, dict)
        assert isinstance(doc.paths, dict)

    @pytest.mark.skipif(not RAML_AVAILABLE, reason="RAML package not available")
    def test_create_raml_document(self):
        """Test creating a RAML document with default values."""
        doc = RAMLDocument()

        # Verify document has required fields
        doc_dict = doc.to_dict()
        assert "#%RAML 1.0" in doc_dict or "#%RAML 0.8" in doc_dict
        assert "title" in doc_dict
        assert "version" in doc_dict

        # Verify document validates
        doc.validate()  # Should not raise

        # Verify properties work
        assert doc.title == "API"
        assert doc.version == "v1"

    @pytest.mark.skipif(not SMITHY_AVAILABLE, reason="Smithy package not available")
    def test_create_smithy_document(self):
        """Test creating a Smithy document with default values."""
        doc = SmithyDocument()

        # Verify document has required fields
        assert "smithy" in doc.to_dict()
        assert "shapes" in doc.to_dict()

        # Verify document validates
        doc.validate()  # Should not raise

        # Verify properties work
        assert doc.smithy_version == "2.0"
        assert isinstance(doc.shapes, dict)


class TestErrorHandling:
    """Test error handling across all packages."""

    @pytest.mark.skipif(not OPENAPI_AVAILABLE, reason="OpenAPI package not available")
    def test_openapi_validation_error(self):
        """Test that OpenAPI validation errors inherit from LaagError."""
        # Create an invalid document (missing required fields)
        doc = OpenAPIDocument({})

        # Validation should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            doc.validate()

        # Verify error inheritance and attributes
        error = exc_info.value
        assert isinstance(error, LaagError)
        assert isinstance(error, Exception)
        assert hasattr(error, "context")
        assert isinstance(error.context, dict)

    @pytest.mark.skipif(not OPENAPI_AVAILABLE, reason="OpenAPI package not available")
    def test_openapi_parse_error(self):
        """Test that OpenAPI parse errors inherit from LaagError."""
        # Try to parse invalid JSON
        with pytest.raises(ParseError) as exc_info:
            OpenAPIDocument.from_json("not valid json {")

        # Verify error inheritance and attributes
        error = exc_info.value
        assert isinstance(error, LaagError)
        assert isinstance(error, Exception)
        assert hasattr(error, "context")
        assert isinstance(error.context, dict)
        assert "input" in error.context

    @pytest.mark.skipif(not RAML_AVAILABLE, reason="RAML package not available")
    def test_raml_validation_error(self):
        """Test that RAML validation errors inherit from LaagError."""
        # Create an invalid document (missing required fields)
        doc = RAMLDocument({})

        # Validation should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            doc.validate()

        # Verify error inheritance and attributes
        error = exc_info.value
        assert isinstance(error, LaagError)
        assert isinstance(error, Exception)
        assert hasattr(error, "context")
        assert isinstance(error.context, dict)

    @pytest.mark.skipif(not RAML_AVAILABLE, reason="RAML package not available")
    def test_raml_parse_error(self):
        """Test that RAML parse errors inherit from LaagError."""
        # Try to parse invalid YAML
        with pytest.raises(ParseError) as exc_info:
            RAMLDocument.from_yaml("invalid: yaml: content: [")

        # Verify error inheritance and attributes
        error = exc_info.value
        assert isinstance(error, LaagError)
        assert isinstance(error, Exception)
        assert hasattr(error, "context")
        assert isinstance(error.context, dict)

    @pytest.mark.skipif(not SMITHY_AVAILABLE, reason="Smithy package not available")
    def test_smithy_validation_error(self):
        """Test that Smithy validation errors inherit from LaagError."""
        # Create an invalid document (missing required fields)
        doc = SmithyDocument({})

        # Validation should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            doc.validate()

        # Verify error inheritance and attributes
        error = exc_info.value
        assert isinstance(error, LaagError)
        assert isinstance(error, Exception)
        assert hasattr(error, "context")
        assert isinstance(error.context, dict)

    @pytest.mark.skipif(not SMITHY_AVAILABLE, reason="Smithy package not available")
    def test_smithy_parse_error(self):
        """Test that Smithy parse errors inherit from LaagError."""
        # Try to parse invalid JSON
        with pytest.raises(ParseError) as exc_info:
            SmithyDocument.from_json("not valid json {")

        # Verify error inheritance and attributes
        error = exc_info.value
        assert isinstance(error, LaagError)
        assert isinstance(error, Exception)
        assert hasattr(error, "context")
        assert isinstance(error.context, dict)
        assert "input" in error.context


class TestExtensionProperties:
    """Test extension properties across all packages."""

    @pytest.mark.skipif(not OPENAPI_AVAILABLE, reason="OpenAPI package not available")
    def test_openapi_extension_properties(self):
        """Test extension property operations on OpenAPI documents."""
        doc = OpenAPIDocument()

        # Test setting extension property
        doc.set_extension("x-custom-field", "custom value")
        assert doc.get_extension("x-custom-field") == "custom value"

        # Test extension appears in document
        assert "x-custom-field" in doc.to_dict()

        # Test removing extension property
        doc.remove_extension("x-custom-field")
        assert doc.get_extension("x-custom-field") is None
        assert "x-custom-field" not in doc.to_dict()

        # Test validation of extension property names
        with pytest.raises(ValueError, match="Extension property must start with 'x-'"):
            doc.set_extension("invalid-name", "value")

    @pytest.mark.skipif(not RAML_AVAILABLE, reason="RAML package not available")
    def test_raml_extension_properties(self):
        """Test extension property operations on RAML documents."""
        doc = RAMLDocument()

        # Test setting extension property
        doc.set_extension("x-custom-field", "custom value")
        assert doc.get_extension("x-custom-field") == "custom value"

        # Test extension appears in document
        assert "x-custom-field" in doc.to_dict()

        # Test removing extension property
        doc.remove_extension("x-custom-field")
        assert doc.get_extension("x-custom-field") is None
        assert "x-custom-field" not in doc.to_dict()

        # Test validation of extension property names
        with pytest.raises(ValueError, match="Extension property must start with 'x-'"):
            doc.set_extension("invalid-name", "value")

    @pytest.mark.skipif(not SMITHY_AVAILABLE, reason="Smithy package not available")
    def test_smithy_extension_properties(self):
        """Test extension property operations on Smithy documents."""
        doc = SmithyDocument()

        # Test setting extension property
        doc.set_extension("x-custom-field", "custom value")
        assert doc.get_extension("x-custom-field") == "custom value"

        # Test extension appears in document
        assert "x-custom-field" in doc.to_dict()

        # Test removing extension property
        doc.remove_extension("x-custom-field")
        assert doc.get_extension("x-custom-field") is None
        assert "x-custom-field" not in doc.to_dict()

        # Test validation of extension property names
        with pytest.raises(ValueError, match="Extension property must start with 'x-'"):
            doc.set_extension("invalid-name", "value")

    @pytest.mark.skipif(
        not (OPENAPI_AVAILABLE and RAML_AVAILABLE and SMITHY_AVAILABLE),
        reason="All packages must be available",
    )
    def test_extension_properties_work_identically(self):
        """Test that extension properties work identically across all formats."""
        # Create documents of all types
        docs = [
            ("OpenAPI", OpenAPIDocument()),
            ("RAML", RAMLDocument()),
            ("Smithy", SmithyDocument()),
        ]

        for doc_type, doc in docs:
            # Set extension
            doc.set_extension("x-test", "test value")

            # Get extension
            value = doc.get_extension("x-test")
            assert value == "test value", f"{doc_type}: get_extension failed"

            # Check in dict
            assert "x-test" in doc.to_dict(), f"{doc_type}: extension not in dict"

            # Remove extension
            doc.remove_extension("x-test")

            # Verify removal
            assert doc.get_extension("x-test") is None, f"{doc_type}: removal failed"
            assert "x-test" not in doc.to_dict(), f"{doc_type}: still in dict after removal"


class TestConsistentMethodNaming:
    """Test that method naming patterns are consistent across formats."""

    @pytest.mark.skipif(
        not (OPENAPI_AVAILABLE and RAML_AVAILABLE and SMITHY_AVAILABLE),
        reason="All packages must be available",
    )
    def test_all_documents_have_validate_method(self):
        """Test that all document types have a validate() method."""
        openapi_doc = OpenAPIDocument()
        raml_doc = RAMLDocument()
        smithy_doc = SmithyDocument()

        # All should have validate method
        assert hasattr(openapi_doc, "validate")
        assert callable(openapi_doc.validate)

        assert hasattr(raml_doc, "validate")
        assert callable(raml_doc.validate)

        assert hasattr(smithy_doc, "validate")
        assert callable(smithy_doc.validate)

        # All should validate successfully with default values
        openapi_doc.validate()
        raml_doc.validate()
        smithy_doc.validate()

    @pytest.mark.skipif(
        not (OPENAPI_AVAILABLE and RAML_AVAILABLE and SMITHY_AVAILABLE),
        reason="All packages must be available",
    )
    def test_all_documents_have_to_dict_method(self):
        """Test that all document types have a to_dict() method."""
        openapi_doc = OpenAPIDocument()
        raml_doc = RAMLDocument()
        smithy_doc = SmithyDocument()

        # All should have to_dict method
        assert hasattr(openapi_doc, "to_dict")
        assert callable(openapi_doc.to_dict)

        assert hasattr(raml_doc, "to_dict")
        assert callable(raml_doc.to_dict)

        assert hasattr(smithy_doc, "to_dict")
        assert callable(smithy_doc.to_dict)

        # All should return dictionaries
        assert isinstance(openapi_doc.to_dict(), dict)
        assert isinstance(raml_doc.to_dict(), dict)
        assert isinstance(smithy_doc.to_dict(), dict)

    @pytest.mark.skipif(
        not (OPENAPI_AVAILABLE and RAML_AVAILABLE and SMITHY_AVAILABLE),
        reason="All packages must be available",
    )
    def test_all_documents_have_extension_methods(self):
        """Test that all document types have consistent extension property methods."""
        docs = [
            OpenAPIDocument(),
            RAMLDocument(),
            SmithyDocument(),
        ]

        for doc in docs:
            # All should have extension property methods
            assert hasattr(doc, "get_extension")
            assert callable(doc.get_extension)

            assert hasattr(doc, "set_extension")
            assert callable(doc.set_extension)

            assert hasattr(doc, "remove_extension")
            assert callable(doc.remove_extension)


class TestConsistentValidation:
    """Test that validation interfaces are consistent across formats."""

    @pytest.mark.skipif(
        not (OPENAPI_AVAILABLE and RAML_AVAILABLE and SMITHY_AVAILABLE),
        reason="All packages must be available",
    )
    def test_validation_raises_validation_error(self):
        """Test that all document types raise ValidationError for invalid documents."""
        # Create invalid documents (empty)
        invalid_openapi = OpenAPIDocument({})
        invalid_raml = RAMLDocument({})
        invalid_smithy = SmithyDocument({})

        # All should raise ValidationError
        with pytest.raises(ValidationError):
            invalid_openapi.validate()

        with pytest.raises(ValidationError):
            invalid_raml.validate()

        with pytest.raises(ValidationError):
            invalid_smithy.validate()

    @pytest.mark.skipif(
        not (OPENAPI_AVAILABLE and RAML_AVAILABLE and SMITHY_AVAILABLE),
        reason="All packages must be available",
    )
    def test_valid_documents_pass_validation(self):
        """Test that valid documents pass validation across all formats."""
        # Create valid documents with default values
        valid_openapi = OpenAPIDocument()
        valid_raml = RAMLDocument()
        valid_smithy = SmithyDocument()

        # All should validate successfully (no exception)
        valid_openapi.validate()
        valid_raml.validate()
        valid_smithy.validate()


class TestBaseClassConsistency:
    """Test that all document types share the same base class."""

    @pytest.mark.skipif(
        not (OPENAPI_AVAILABLE and RAML_AVAILABLE and SMITHY_AVAILABLE),
        reason="All packages must be available",
    )
    def test_all_documents_inherit_from_laag_base(self):
        """Test that all document types inherit from LaagBase."""
        from pylaag.core.base import LaagBase

        openapi_doc = OpenAPIDocument()
        raml_doc = RAMLDocument()
        smithy_doc = SmithyDocument()

        # All should inherit from LaagBase
        assert isinstance(openapi_doc, LaagBase)
        assert isinstance(raml_doc, LaagBase)
        assert isinstance(smithy_doc, LaagBase)
