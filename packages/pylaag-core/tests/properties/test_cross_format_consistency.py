"""Property-based tests for cross-format consistency."""

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pylaag_core.errors import LaagError, NotFoundError, ParseError, ValidationError

# Import all document types
try:
    from pylaag_openapi import OpenAPIDocument

    OPENAPI_AVAILABLE = True
except ImportError:
    OPENAPI_AVAILABLE = False

try:
    from pylaag_raml import RAMLDocument

    RAML_AVAILABLE = True
except ImportError:
    RAML_AVAILABLE = False

try:
    from pylaag_smithy import SmithyDocument

    SMITHY_AVAILABLE = True
except ImportError:
    SMITHY_AVAILABLE = False


# Strategy for generating extension property names
extension_property_strategy = st.text(min_size=3, max_size=50).map(
    lambda s: f"x-{s.replace(' ', '-').lower()}"
)

# Strategy for extension property values
extension_value_strategy = st.one_of(
    st.text(max_size=100),
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.booleans(),
    st.lists(st.text(max_size=50), max_size=5),
    st.dictionaries(keys=st.text(min_size=1, max_size=20), values=st.text(max_size=50), max_size=5),
)


@given(
    error_class=st.sampled_from([ValidationError, ParseError, NotFoundError]),
    message=st.text(min_size=1, max_size=200),
    context_dict=st.dictionaries(
        keys=st.text(min_size=1, max_size=50),
        values=st.one_of(
            st.text(max_size=100),
            st.integers(),
            st.floats(allow_nan=False, allow_infinity=False),
            st.booleans(),
        ),
        max_size=10,
    ),
)
def test_consistent_error_handling(error_class, message: str, context_dict: dict) -> None:
    """
    Feature: laag-python-port, Property 33: Consistent Error Handling

    **Validates: Requirements 15.2**

    For any error raised by any package (OpenAPI, RAML, Smithy),
    the error should inherit from LaagError and include a context dictionary.
    """
    # Create an error instance
    error = error_class(message, context_dict)

    # Verify it inherits from LaagError
    assert isinstance(error, LaagError)

    # Verify it has a context attribute
    assert hasattr(error, "context")

    # Verify the context is a dictionary
    assert isinstance(error.context, dict)

    # Verify the context matches what was provided
    assert error.context == context_dict

    # Verify the message is preserved
    assert str(error) == message

    # Verify it's a proper exception
    assert isinstance(error, Exception)


@pytest.mark.skipif(not OPENAPI_AVAILABLE, reason="OpenAPI package not available")
@given(
    ext_name=extension_property_strategy,
    ext_value=extension_value_strategy,
)
def test_openapi_extension_property_handling(ext_name: str, ext_value) -> None:
    """
    Feature: laag-python-port, Property 34: Consistent Extension Property Handling

    **Validates: Requirements 15.3**

    For OpenAPI documents, extension properties should be handled consistently
    (set, get, remove operations work the same way).
    """
    doc = OpenAPIDocument()

    # Test set operation
    doc.set_extension(ext_name, ext_value)

    # Test get operation
    retrieved_value = doc.get_extension(ext_name)
    assert retrieved_value == ext_value

    # Test that extension is in the document
    assert ext_name in doc.to_dict()

    # Test remove operation
    doc.remove_extension(ext_name)
    assert doc.get_extension(ext_name) is None
    assert ext_name not in doc.to_dict()


@pytest.mark.skipif(not RAML_AVAILABLE, reason="RAML package not available")
@given(
    ext_name=extension_property_strategy,
    ext_value=extension_value_strategy,
)
def test_raml_extension_property_handling(ext_name: str, ext_value) -> None:
    """
    Feature: laag-python-port, Property 34: Consistent Extension Property Handling

    **Validates: Requirements 15.3**

    For RAML documents, extension properties should be handled consistently
    (set, get, remove operations work the same way).
    """
    doc = RAMLDocument()

    # Test set operation
    doc.set_extension(ext_name, ext_value)

    # Test get operation
    retrieved_value = doc.get_extension(ext_name)
    assert retrieved_value == ext_value

    # Test that extension is in the document
    assert ext_name in doc.to_dict()

    # Test remove operation
    doc.remove_extension(ext_name)
    assert doc.get_extension(ext_name) is None
    assert ext_name not in doc.to_dict()


@pytest.mark.skipif(not SMITHY_AVAILABLE, reason="Smithy package not available")
@given(
    ext_name=extension_property_strategy,
    ext_value=extension_value_strategy,
)
def test_smithy_extension_property_handling(ext_name: str, ext_value) -> None:
    """
    Feature: laag-python-port, Property 34: Consistent Extension Property Handling

    **Validates: Requirements 15.3**

    For Smithy documents, extension properties should be handled consistently
    (set, get, remove operations work the same way).
    """
    doc = SmithyDocument()

    # Test set operation
    doc.set_extension(ext_name, ext_value)

    # Test get operation
    retrieved_value = doc.get_extension(ext_name)
    assert retrieved_value == ext_value

    # Test that extension is in the document
    assert ext_name in doc.to_dict()

    # Test remove operation
    doc.remove_extension(ext_name)
    assert doc.get_extension(ext_name) is None
    assert ext_name not in doc.to_dict()


@pytest.mark.skipif(
    not (OPENAPI_AVAILABLE and RAML_AVAILABLE and SMITHY_AVAILABLE),
    reason="All packages must be available",
)
@given(
    ext_name=extension_property_strategy,
    ext_value=extension_value_strategy,
)
def test_extension_property_consistency_across_formats(ext_name: str, ext_value) -> None:
    """
    Feature: laag-python-port, Property 34: Consistent Extension Property Handling

    **Validates: Requirements 15.3**

    Extension property handling should work identically across all document types.
    """
    # Create documents of all types
    openapi_doc = OpenAPIDocument()
    raml_doc = RAMLDocument()
    smithy_doc = SmithyDocument()

    docs = [
        ("OpenAPI", openapi_doc),
        ("RAML", raml_doc),
        ("Smithy", smithy_doc),
    ]

    for doc_type, doc in docs:
        # Set extension
        doc.set_extension(ext_name, ext_value)

        # Get extension - should return the same value
        assert doc.get_extension(ext_name) == ext_value, f"{doc_type}: get_extension failed"

        # Extension should be in document dict
        assert ext_name in doc.to_dict(), f"{doc_type}: extension not in to_dict()"

        # Remove extension
        doc.remove_extension(ext_name)

        # Get should return None after removal
        assert doc.get_extension(ext_name) is None, (
            f"{doc_type}: get_extension should return None after removal"
        )

        # Extension should not be in document dict after removal
        assert ext_name not in doc.to_dict(), (
            f"{doc_type}: extension still in to_dict() after removal"
        )


@given(
    invalid_ext_name=st.text(min_size=1, max_size=50).filter(lambda s: not s.startswith("x-")),
)
def test_extension_property_validation_consistency(invalid_ext_name: str) -> None:
    """
    Feature: laag-python-port, Property 34: Consistent Extension Property Handling

    **Validates: Requirements 15.3, 11.6**

    All document types should consistently validate that extension properties
    start with "x-".
    """
    docs = []

    if OPENAPI_AVAILABLE:
        docs.append(("OpenAPI", OpenAPIDocument()))

    if RAML_AVAILABLE:
        docs.append(("RAML", RAMLDocument()))

    if SMITHY_AVAILABLE:
        docs.append(("Smithy", SmithyDocument()))

    for _doc_type, doc in docs:
        # Attempting to set an invalid extension property should raise ValueError
        with pytest.raises(ValueError, match="Extension property must start with 'x-'"):
            doc.set_extension(invalid_ext_name, "value")


@pytest.mark.skipif(
    not (OPENAPI_AVAILABLE and RAML_AVAILABLE and SMITHY_AVAILABLE),
    reason="All packages must be available",
)
def test_error_inheritance_consistency() -> None:
    """
    Feature: laag-python-port, Property 33: Consistent Error Handling

    **Validates: Requirements 15.2**

    All error classes across all packages should inherit from LaagError.
    """
    # Test that all error types inherit from LaagError
    error_classes = [ValidationError, ParseError, NotFoundError]

    for error_class in error_classes:
        # Create an instance
        error = error_class("test message", {"key": "value"})

        # Verify inheritance
        assert isinstance(error, LaagError)
        assert isinstance(error, Exception)

        # Verify it has the required attributes
        assert hasattr(error, "context")
        assert isinstance(error.context, dict)

        # Verify the context is accessible
        assert error.context == {"key": "value"}
