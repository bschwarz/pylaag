"""Property-based tests for OpenAPI document parsing and serialization."""

import json

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pylaag_core.errors import ParseError, ValidationError
from pylaag_openapi import OpenAPIDocument


# Strategy for generating valid OpenAPI documents
@st.composite
def openapi_document_strategy(draw):
    """Generate valid OpenAPI documents."""
    return {
        "openapi": draw(st.sampled_from(["3.0.0", "3.0.1", "3.0.2", "3.0.3", "3.1.0"])),
        "info": {
            "title": draw(st.text(min_size=1, max_size=100)),
            "version": draw(st.text(min_size=1, max_size=50)),
            "description": draw(st.text(max_size=200)),
        },
        "paths": draw(
            st.dictionaries(
                keys=st.text(min_size=1, max_size=50).map(lambda s: f"/{s}"),
                values=st.dictionaries(
                    keys=st.sampled_from(["get", "post", "put", "delete", "patch"]),
                    values=st.fixed_dictionaries(
                        {
                            "summary": st.text(max_size=100),
                            "responses": st.fixed_dictionaries(
                                {
                                    "200": st.fixed_dictionaries(
                                        {"description": st.text(max_size=100)}
                                    )
                                }
                            ),
                        }
                    ),
                    max_size=3,
                ),
                max_size=5,
            )
        ),
    }


# Strategy for generating invalid OpenAPI documents (missing required fields)
@st.composite
def invalid_openapi_document_strategy(draw):
    """Generate invalid OpenAPI documents missing required fields."""
    # Choose which required field to omit
    omit_field = draw(st.sampled_from(["openapi", "info", "info.title", "info.version", "paths"]))

    doc = {
        "openapi": "3.0.0",
        "info": {"title": "API", "version": "1.0.0"},
        "paths": {},
    }

    if omit_field == "openapi":
        del doc["openapi"]
    elif omit_field == "info":
        del doc["info"]
    elif omit_field == "info.title":
        del doc["info"]["title"]
    elif omit_field == "info.version":
        del doc["info"]["version"]
    elif omit_field == "paths":
        del doc["paths"]

    return doc, omit_field


@given(doc_dict=openapi_document_strategy())
def test_json_round_trip(doc_dict: dict) -> None:
    """
    Feature: laag-python-port, Property 4: JSON Round Trip

    **Validates: Requirements 3.1, 3.4, 3.6**

    For any valid OpenAPI document object, serializing to JSON
    then parsing should produce an equivalent document object.
    """
    # Create document from dict
    doc = OpenAPIDocument(doc_dict)

    # Serialize to JSON
    json_str = doc.to_json()

    # Parse from JSON
    parsed_doc = OpenAPIDocument.from_json(json_str)

    # Verify the documents are equivalent
    assert parsed_doc.to_dict() == doc.to_dict()

    # Verify specific fields are preserved
    assert parsed_doc.openapi_version == doc.openapi_version
    assert parsed_doc.info == doc.info
    assert parsed_doc.paths == doc.paths


@given(doc_dict=openapi_document_strategy())
def test_yaml_round_trip(doc_dict: dict) -> None:
    """
    Feature: laag-python-port, Property 5: YAML Round Trip

    **Validates: Requirements 3.2, 3.5, 3.6**

    For any valid OpenAPI document object, serializing to YAML
    then parsing should produce an equivalent document object.
    """
    # Create document from dict
    doc = OpenAPIDocument(doc_dict)

    # Serialize to YAML
    yaml_str = doc.to_yaml()

    # Parse from YAML
    parsed_doc = OpenAPIDocument.from_yaml(yaml_str)

    # Verify the documents are equivalent
    assert parsed_doc.to_dict() == doc.to_dict()

    # Verify specific fields are preserved
    assert parsed_doc.openapi_version == doc.openapi_version
    assert parsed_doc.info == doc.info
    assert parsed_doc.paths == doc.paths


@given(doc_dict=openapi_document_strategy())
def test_json_yaml_cross_format(doc_dict: dict) -> None:
    """
    Feature: laag-python-port, Property 4 & 5: Cross-format Round Trip

    **Validates: Requirements 3.1, 3.2, 3.4, 3.5, 3.6**

    A document serialized to JSON and then to YAML (or vice versa)
    should maintain equivalence.
    """
    # Create document from dict
    doc = OpenAPIDocument(doc_dict)

    # JSON -> YAML -> JSON
    json_str1 = doc.to_json()
    doc_from_json = OpenAPIDocument.from_json(json_str1)
    yaml_str = doc_from_json.to_yaml()
    doc_from_yaml = OpenAPIDocument.from_yaml(yaml_str)
    json_str2 = doc_from_yaml.to_json()

    # Parse both JSON strings and compare
    parsed1 = json.loads(json_str1)
    parsed2 = json.loads(json_str2)
    assert parsed1 == parsed2


@given(
    doc_dict=openapi_document_strategy(),
    indent=st.integers(min_value=0, max_value=8),
)
def test_json_serialization_with_indent(doc_dict: dict, indent: int) -> None:
    """
    Feature: laag-python-port, Property 4: JSON Round Trip

    **Validates: Requirements 3.1, 3.4, 3.6**

    JSON serialization with different indent values should still
    produce parseable and equivalent documents.
    """
    doc = OpenAPIDocument(doc_dict)

    # Serialize with custom indent
    json_str = doc.to_json(indent=indent)

    # Should be valid JSON
    parsed_doc = OpenAPIDocument.from_json(json_str)

    # Should be equivalent
    assert parsed_doc.to_dict() == doc.to_dict()


@given(
    malformed_json=st.one_of(
        st.text(min_size=1, max_size=100).filter(
            lambda s: not s.strip().startswith("{")
        ),  # Not JSON
        st.just("{invalid json}"),  # Invalid JSON syntax
        st.just('{"key": }'),  # Missing value
        st.just('{"key": "value"'),  # Missing closing brace
        st.just("[1, 2, 3]"),  # Valid JSON but not an object
    )
)
def test_malformed_json_rejection(malformed_json: str) -> None:
    """
    Feature: laag-python-port, Property 6: Malformed Input Rejection

    **Validates: Requirements 2.2**

    For any malformed JSON string (invalid syntax), parsing should
    raise a ParseError with details about the syntax error.
    """
    with pytest.raises(ParseError) as exc_info:
        OpenAPIDocument.from_json(malformed_json)

    # Verify error has context
    assert exc_info.value.context is not None
    assert "input" in exc_info.value.context or "error" in exc_info.value.context


@given(
    malformed_yaml=st.one_of(
        st.just(":\n  invalid: yaml: structure"),  # Invalid YAML
        st.just("- item1\n- item2\n  - nested"),  # Invalid indentation
        st.just("{key: value: extra}"),  # Invalid syntax
        st.just("key: [unclosed"),  # Unclosed bracket
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
        OpenAPIDocument.from_yaml(malformed_yaml)

    # Verify error has context
    assert exc_info.value.context is not None
    assert "input" in exc_info.value.context or "error" in exc_info.value.context


@given(invalid_doc_data=invalid_openapi_document_strategy())
def test_invalid_document_rejection(invalid_doc_data: tuple) -> None:
    """
    Feature: laag-python-port, Property 2: Invalid Document Rejection

    **Validates: Requirements 2.1, 3.3**

    For any document missing required OpenAPI fields (openapi, info,
    info.title, info.version, paths), validation should raise a
    ValidationError with details about the missing field.
    """
    doc_dict, omitted_field = invalid_doc_data

    # Create document (should not raise)
    doc = OpenAPIDocument(doc_dict)

    # Validation should raise
    with pytest.raises(ValidationError) as exc_info:
        doc.validate()

    # Verify error message mentions the missing field
    error_message = str(exc_info.value)
    assert "Missing required field" in error_message

    # Verify the error mentions the correct field
    if omitted_field == "openapi":
        assert "openapi" in error_message
    elif omitted_field == "info":
        assert "info" in error_message
    elif omitted_field == "info.title":
        assert "title" in error_message
    elif omitted_field == "info.version":
        assert "version" in error_message
    elif omitted_field == "paths":
        assert "paths" in error_message


@given(doc_dict=openapi_document_strategy())
def test_valid_document_passes_validation(doc_dict: dict) -> None:
    """
    Feature: laag-python-port, Property 2: Invalid Document Rejection

    **Validates: Requirements 2.1, 3.3**

    Valid OpenAPI documents should pass validation without errors.
    """
    doc = OpenAPIDocument(doc_dict)

    # Should not raise
    doc.validate()


@given(doc_dict=openapi_document_strategy())
def test_properties_access(doc_dict: dict) -> None:
    """
    Feature: laag-python-port, Property 4: JSON Round Trip

    **Validates: Requirements 3.1, 3.4, 3.6**

    Document properties should provide access to the correct data.
    """
    doc = OpenAPIDocument(doc_dict)

    # Verify properties match the input
    assert doc.openapi_version == doc_dict["openapi"]
    assert doc.info == doc_dict["info"]
    assert doc.paths == doc_dict["paths"]


def test_default_document_is_valid() -> None:
    """
    Feature: laag-python-port, Property 2: Invalid Document Rejection

    **Validates: Requirements 2.1, 3.3**

    The default document created with no arguments should be valid.
    """
    doc = OpenAPIDocument()

    # Should not raise
    doc.validate()

    # Should have required fields
    assert doc.openapi_version == "3.0.0"
    assert doc.info["title"] == "API"
    assert doc.info["version"] == "1.0.0"
    assert doc.paths == {}
