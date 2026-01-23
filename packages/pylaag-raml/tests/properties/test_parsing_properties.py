"""Property-based tests for RAML document parsing and serialization."""

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pylaag_core.errors import ParseError, ValidationError
from pylaag_raml import RAMLDocument


# Strategy for generating valid RAML documents
@st.composite
def raml_document_strategy(draw):
    """Generate valid RAML documents."""
    version_marker = draw(st.sampled_from(["#%RAML 1.0", "#%RAML 0.8"]))
    return {
        version_marker: None,
        "title": draw(st.text(min_size=1, max_size=100)),
        "version": draw(st.text(min_size=1, max_size=50)),
        "baseUri": draw(
            st.one_of(
                st.just("https://api.example.com"),
                st.text(min_size=10, max_size=100).map(lambda s: f"https://{s}.com"),
            )
        ),
        "description": draw(st.text(max_size=200)),
    }


# Strategy for generating invalid RAML documents (missing required fields)
@st.composite
def invalid_raml_document_strategy(draw):
    """Generate invalid RAML documents missing required fields."""
    # Choose which required field to omit
    omit_field = draw(st.sampled_from(["version_marker", "title", "version"]))

    doc = {
        "#%RAML 1.0": None,
        "title": "API",
        "version": "v1",
        "baseUri": "https://api.example.com",
    }

    if omit_field == "version_marker":
        del doc["#%RAML 1.0"]
    elif omit_field == "title":
        del doc["title"]
    elif omit_field == "version":
        del doc["version"]

    return doc, omit_field


@given(doc_dict=raml_document_strategy())
def test_raml_yaml_round_trip(doc_dict: dict) -> None:
    """
    Feature: laag-python-port, Property 24: RAML Round Trip

    **Validates: Requirements 13.2, 13.7, 13.8**

    For any valid RAML document object, serializing to YAML
    then parsing should produce an equivalent document object.
    """
    # Create document from dict
    doc = RAMLDocument(doc_dict)

    # Serialize to YAML
    yaml_str = doc.to_yaml()

    # Parse from YAML
    parsed_doc = RAMLDocument.from_yaml(yaml_str)

    # Verify the documents are equivalent
    assert parsed_doc.to_dict() == doc.to_dict()

    # Verify specific fields are preserved
    assert parsed_doc.title == doc.title
    assert parsed_doc.version == doc.version
    assert parsed_doc.base_uri == doc.base_uri


@given(doc_dict=raml_document_strategy())
def test_raml_multiple_round_trips(doc_dict: dict) -> None:
    """
    Feature: laag-python-port, Property 24: RAML Round Trip

    **Validates: Requirements 13.2, 13.7, 13.8**

    Multiple round trips (serialize -> parse -> serialize -> parse)
    should maintain document equivalence.
    """
    # Create document from dict
    doc = RAMLDocument(doc_dict)

    # First round trip
    yaml_str1 = doc.to_yaml()
    doc1 = RAMLDocument.from_yaml(yaml_str1)

    # Second round trip
    yaml_str2 = doc1.to_yaml()
    doc2 = RAMLDocument.from_yaml(yaml_str2)

    # All should be equivalent
    assert doc.to_dict() == doc1.to_dict() == doc2.to_dict()


@given(
    malformed_yaml=st.one_of(
        st.just(":\n  invalid: yaml: structure"),  # Invalid YAML
        st.just("{key: value: extra}"),  # Invalid syntax
        st.just("key: [unclosed"),  # Unclosed bracket
        st.just("{{{{"),  # Invalid braces
        st.just("key:\n  - item\n - bad_indent"),  # Invalid indentation
    )
)
def test_malformed_yaml_rejection(malformed_yaml: str) -> None:
    """
    Feature: laag-python-port, Property 6: Malformed Input Rejection

    **Validates: Requirements 2.2**

    For any malformed YAML string (invalid syntax), parsing should
    raise a ParseError with details about the syntax error.
    """
    with pytest.raises(ParseError) as exc_info:
        RAMLDocument.from_yaml(malformed_yaml)

    # Verify error has context
    assert exc_info.value.context is not None
    assert "input" in exc_info.value.context


@given(doc_dict=raml_document_strategy())
def test_properties_access(doc_dict: dict) -> None:
    """
    Feature: laag-python-port, Property 24: RAML Round Trip

    **Validates: Requirements 13.2, 13.7, 13.8**

    Document properties should provide access to the correct data.
    """
    doc = RAMLDocument(doc_dict)

    # Verify properties match the input
    assert doc.title == doc_dict["title"]
    assert doc.version == doc_dict["version"]
    assert doc.base_uri == doc_dict.get("baseUri", "")


def test_default_document_is_valid() -> None:
    """
    Feature: laag-python-port, Property 25: RAML Validation

    **Validates: Requirements 13.6**

    The default document created with no arguments should be valid.
    """
    doc = RAMLDocument()

    # Should not raise
    doc.validate()

    # Should have required fields
    assert "#%RAML 1.0" in doc.to_dict()
    assert doc.title == "API"
    assert doc.version == "v1"
    assert doc.base_uri == "https://api.example.com"


@given(invalid_doc_data=invalid_raml_document_strategy())
def test_raml_invalid_document_rejection(invalid_doc_data: tuple) -> None:
    """
    Feature: laag-python-port, Property 25: RAML Validation

    **Validates: Requirements 13.6**

    For any RAML document missing required fields (RAML version marker,
    title, version), validation should raise a ValidationError with
    details about the missing field.
    """
    doc_dict, omitted_field = invalid_doc_data

    # Create document (should not raise)
    doc = RAMLDocument(doc_dict)

    # Validation should raise
    with pytest.raises(ValidationError) as exc_info:
        doc.validate()

    # Verify error message mentions the missing field
    error_message = str(exc_info.value)
    assert "Missing required field" in error_message or "Missing RAML version marker" in error_message

    # Verify the error mentions the correct field
    if omitted_field == "version_marker":
        assert "RAML version marker" in error_message
    elif omitted_field == "title":
        assert "title" in error_message
    elif omitted_field == "version":
        assert "version" in error_message


@given(doc_dict=raml_document_strategy())
def test_raml_valid_document_passes_validation(doc_dict: dict) -> None:
    """
    Feature: laag-python-port, Property 25: RAML Validation

    **Validates: Requirements 13.6**

    Valid RAML documents should pass validation without errors.
    """
    doc = RAMLDocument(doc_dict)

    # Should not raise
    doc.validate()


def test_raml_validation_missing_version_marker() -> None:
    """
    Feature: laag-python-port, Property 25: RAML Validation

    **Validates: Requirements 13.6**

    RAML document without version marker should fail validation.
    """
    doc = RAMLDocument({"title": "API", "version": "v1"})

    with pytest.raises(ValidationError) as exc_info:
        doc.validate()

    assert "RAML version marker" in str(exc_info.value)


def test_raml_validation_missing_title() -> None:
    """
    Feature: laag-python-port, Property 25: RAML Validation

    **Validates: Requirements 13.6**

    RAML document without title should fail validation.
    """
    doc = RAMLDocument({"#%RAML 1.0": None, "version": "v1"})

    with pytest.raises(ValidationError) as exc_info:
        doc.validate()

    assert "title" in str(exc_info.value)


def test_raml_validation_missing_version() -> None:
    """
    Feature: laag-python-port, Property 25: RAML Validation

    **Validates: Requirements 13.6**

    RAML document without version should fail validation.
    """
    doc = RAMLDocument({"#%RAML 1.0": None, "title": "API"})

    with pytest.raises(ValidationError) as exc_info:
        doc.validate()

    assert "version" in str(exc_info.value)


def test_raml_08_version_marker_accepted() -> None:
    """
    Feature: laag-python-port, Property 25: RAML Validation

    **Validates: Requirements 13.6**

    RAML 0.8 version marker should be accepted.
    """
    doc = RAMLDocument({"#%RAML 0.8": None, "title": "API", "version": "v1"})

    # Should not raise
    doc.validate()
