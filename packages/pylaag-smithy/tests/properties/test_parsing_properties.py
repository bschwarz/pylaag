"""Property-based tests for Smithy document parsing and serialization."""

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pylaag_core.errors import ParseError
from pylaag_smithy import SmithyDocument


# Strategy for generating valid Smithy documents
@st.composite
def smithy_document_strategy(draw):
    """Generate valid Smithy documents."""
    return {
        "smithy": draw(st.sampled_from(["2.0", "2"])),
        "metadata": draw(
            st.dictionaries(
                keys=st.text(min_size=1, max_size=50),
                values=st.one_of(
                    st.text(max_size=100),
                    st.integers(),
                    st.booleans(),
                ),
                max_size=3,
            )
        ),
        "shapes": draw(
            st.dictionaries(
                keys=st.text(min_size=1, max_size=50).map(lambda s: f"com.example#{s}"),
                values=st.fixed_dictionaries(
                    {
                        "type": st.sampled_from(
                            [
                                "structure",
                                "string",
                                "integer",
                                "boolean",
                                "list",
                                "map",
                            ]
                        ),
                    }
                ),
                max_size=5,
            )
        ),
    }


# Strategy for generating invalid Smithy documents (missing required fields)
@st.composite
def invalid_smithy_document_strategy(draw):
    """Generate invalid Smithy documents missing required fields."""
    # Choose which required field to omit
    omit_field = draw(st.sampled_from(["smithy", "shapes"]))

    doc = {
        "smithy": "2.0",
        "metadata": {},
        "shapes": {},
    }

    if omit_field == "smithy":
        del doc["smithy"]
    elif omit_field == "shapes":
        del doc["shapes"]

    return doc, omit_field


@given(doc_dict=smithy_document_strategy())
def test_json_round_trip(doc_dict: dict) -> None:
    """
    Feature: laag-python-port, Property 28: Smithy Round Trip

    **Validates: Requirements 14.2, 14.7, 14.8**

    For any valid Smithy document object, serializing to JSON
    then parsing should produce an equivalent document object.
    """
    # Create document from dict
    doc = SmithyDocument(doc_dict)

    # Serialize to JSON
    json_str = doc.to_json()

    # Parse from JSON
    parsed_doc = SmithyDocument.from_json(json_str)

    # Verify the documents are equivalent
    assert parsed_doc.to_dict() == doc.to_dict()

    # Verify specific fields are preserved
    assert parsed_doc.smithy_version == doc.smithy_version
    assert parsed_doc.shapes == doc.shapes


@given(
    doc_dict=smithy_document_strategy(),
    indent=st.integers(min_value=0, max_value=8),
)
def test_json_serialization_with_indent(doc_dict: dict, indent: int) -> None:
    """
    Feature: laag-python-port, Property 28: Smithy Round Trip

    **Validates: Requirements 14.2, 14.7, 14.8**

    JSON serialization with different indent values should still
    produce parseable and equivalent documents.
    """
    doc = SmithyDocument(doc_dict)

    # Serialize with custom indent
    json_str = doc.to_json(indent=indent)

    # Should be valid JSON
    parsed_doc = SmithyDocument.from_json(json_str)

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
        SmithyDocument.from_json(malformed_json)

    # Verify error has context
    assert exc_info.value.context is not None
    assert "input" in exc_info.value.context or "error" in exc_info.value.context


@given(doc_dict=smithy_document_strategy())
def test_properties_access(doc_dict: dict) -> None:
    """
    Feature: laag-python-port, Property 28: Smithy Round Trip

    **Validates: Requirements 14.2, 14.7, 14.8**

    Document properties should provide access to the correct data.
    """
    doc = SmithyDocument(doc_dict)

    # Verify properties match the input
    assert doc.smithy_version == doc_dict["smithy"]
    assert doc.shapes == doc_dict["shapes"]


def test_default_document_is_valid() -> None:
    """
    Feature: laag-python-port, Property 29: Smithy Validation

    **Validates: Requirements 14.6**

    The default document created with no arguments should be valid.
    """
    doc = SmithyDocument()

    # Should not raise
    doc.validate()

    # Should have required fields
    assert doc.smithy_version == "2.0"
    assert doc.shapes == {}
