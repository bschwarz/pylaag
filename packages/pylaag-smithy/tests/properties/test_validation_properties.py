"""Property-based tests for Smithy document validation."""

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pylaag.core.errors import ValidationError
from pylaag.smithy import SmithyDocument


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


@given(invalid_doc_data=invalid_smithy_document_strategy())
def test_invalid_document_rejection(invalid_doc_data: tuple) -> None:
    """
    Feature: laag-python-port, Property 29: Smithy Validation

    **Validates: Requirements 14.6**

    For any Smithy document missing required fields (smithy version, shapes),
    validation should raise a ValidationError with details about the missing field.
    """
    doc_dict, omitted_field = invalid_doc_data

    # Create document (should not raise)
    doc = SmithyDocument(doc_dict)

    # Validation should raise
    with pytest.raises(ValidationError) as exc_info:
        doc.validate()

    # Verify error message mentions the missing field
    error_message = str(exc_info.value)
    assert "Missing required field" in error_message

    # Verify the error mentions the correct field
    if omitted_field == "smithy":
        assert "smithy" in error_message
    elif omitted_field == "shapes":
        assert "shapes" in error_message


@given(doc_dict=smithy_document_strategy())
def test_valid_document_passes_validation(doc_dict: dict) -> None:
    """
    Feature: laag-python-port, Property 29: Smithy Validation

    **Validates: Requirements 14.6**

    Valid Smithy documents should pass validation without errors.
    """
    doc = SmithyDocument(doc_dict)

    # Should not raise
    doc.validate()


def test_missing_smithy_version_field() -> None:
    """
    Feature: laag-python-port, Property 29: Smithy Validation

    **Validates: Requirements 14.6**

    A document missing the smithy version field should fail validation.
    """
    doc = SmithyDocument({"shapes": {}})

    with pytest.raises(ValidationError) as exc_info:
        doc.validate()

    assert "smithy" in str(exc_info.value).lower()


def test_missing_shapes_field() -> None:
    """
    Feature: laag-python-port, Property 29: Smithy Validation

    **Validates: Requirements 14.6**

    A document missing the shapes field should fail validation.
    """
    doc = SmithyDocument({"smithy": "2.0"})

    with pytest.raises(ValidationError) as exc_info:
        doc.validate()

    assert "shapes" in str(exc_info.value).lower()


def test_empty_document_fails_validation() -> None:
    """
    Feature: laag-python-port, Property 29: Smithy Validation

    **Validates: Requirements 14.6**

    An empty document should fail validation.
    """
    doc = SmithyDocument({})

    with pytest.raises(ValidationError):
        doc.validate()


def test_minimal_valid_document() -> None:
    """
    Feature: laag-python-port, Property 29: Smithy Validation

    **Validates: Requirements 14.6**

    A minimal document with only required fields should pass validation.
    """
    doc = SmithyDocument({"smithy": "2.0", "shapes": {}})

    # Should not raise
    doc.validate()
