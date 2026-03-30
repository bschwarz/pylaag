"""Property-based tests for extension property handling."""

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pylaag.core.base import LaagBase
from pylaag.core.errors import ValidationError


class TestDocument(LaagBase):
    """Concrete implementation of LaagBase for testing."""

    def validate(self) -> None:
        """Validate the test document."""
        # Simple validation for testing
        if "required_field" in self._document and not self._document["required_field"]:
            raise ValidationError("required_field cannot be empty")


# Strategy for generating valid extension property names
extension_key_strategy = st.text(
    min_size=3,
    max_size=20,
    alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"), whitelist_characters="-_"),
).map(lambda s: f"x-{s}")

# Strategy for generating invalid extension property names (not starting with x-)
non_extension_key_strategy = st.text(
    min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"))
).filter(lambda s: not s.startswith("x-"))

# Strategy for generating extension property values
extension_value_strategy = st.one_of(
    st.text(max_size=100),
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.booleans(),
    st.none(),
    st.lists(st.text(max_size=50), max_size=5),
    st.dictionaries(keys=st.text(min_size=1, max_size=20), values=st.text(max_size=50), max_size=5),
)


@given(
    extensions=st.dictionaries(
        keys=extension_key_strategy,
        values=extension_value_strategy,
        min_size=1,
        max_size=10,
    )
)
def test_extension_property_round_trip(extensions: dict) -> None:
    """
    Feature: laag-python-port, Property 1: Extension Property Round Trip

    **Validates: Requirements 1.4, 11.1, 11.5**

    For any valid API document with extension properties (x-* properties),
    parsing the document, then serializing it, then parsing again should
    preserve all extension properties with their original values.
    """
    # Create a document with extension properties
    doc = TestDocument(extensions.copy())

    # Verify all extensions are accessible
    for key, value in extensions.items():
        assert doc.get_extension(key) == value

    # Serialize to dict
    doc_dict = doc.to_dict()

    # Verify extensions are in the serialized dict
    for key, value in extensions.items():
        assert doc_dict[key] == value

    # Parse again from the dict
    doc2 = TestDocument(doc_dict)

    # Verify all extensions are preserved
    for key, value in extensions.items():
        assert doc2.get_extension(key) == value

    # Verify the documents are equivalent
    assert doc2.to_dict() == doc.to_dict()


@given(
    key=extension_key_strategy,
    value=extension_value_strategy,
)
def test_set_and_get_extension(key: str, value: any) -> None:
    """
    Feature: laag-python-port, Property 1: Extension Property Round Trip

    **Validates: Requirements 1.4, 11.1, 11.5**

    Setting an extension property and then getting it should return the same value.
    """
    doc = TestDocument()

    # Set the extension
    doc.set_extension(key, value)

    # Get the extension
    retrieved_value = doc.get_extension(key)

    # Verify the value matches
    assert retrieved_value == value

    # Verify it's in the document dict
    assert doc.to_dict()[key] == value


@given(
    key=extension_key_strategy,
    value=extension_value_strategy,
)
def test_remove_extension(key: str, value: any) -> None:
    """
    Feature: laag-python-port, Property 1: Extension Property Round Trip

    **Validates: Requirements 1.4, 11.1, 11.5**

    Removing an extension property should make it inaccessible.
    """
    doc = TestDocument()

    # Set the extension
    doc.set_extension(key, value)
    assert doc.get_extension(key) == value

    # Remove the extension
    doc.remove_extension(key)

    # Verify it's gone
    assert doc.get_extension(key) is None
    assert key not in doc.to_dict()


@given(
    initial_extensions=st.dictionaries(
        keys=extension_key_strategy,
        values=extension_value_strategy,
        min_size=2,
        max_size=5,
    )
)
def test_extension_extraction_on_init(initial_extensions: dict) -> None:
    """
    Feature: laag-python-port, Property 1: Extension Property Round Trip

    **Validates: Requirements 1.4, 11.1, 11.5**

    Extension properties present in the initial document should be
    automatically extracted and accessible.
    """
    # Create document with extensions in the initial dict
    doc = TestDocument(initial_extensions.copy())

    # Verify all extensions were extracted
    for key, value in initial_extensions.items():
        assert doc.get_extension(key) == value


@given(
    extensions=st.dictionaries(
        keys=extension_key_strategy,
        values=extension_value_strategy,
        min_size=1,
        max_size=5,
    ),
    regular_fields=st.dictionaries(
        keys=non_extension_key_strategy,
        values=st.text(max_size=50),
        min_size=1,
        max_size=5,
    ),
)
def test_extensions_dont_interfere_with_regular_fields(
    extensions: dict, regular_fields: dict
) -> None:
    """
    Feature: laag-python-port, Property 1: Extension Property Round Trip

    **Validates: Requirements 1.4, 11.1, 11.5**

    Extension properties should not interfere with regular document fields.
    """
    # Combine extensions and regular fields
    document = {**regular_fields, **extensions}

    doc = TestDocument(document)

    # Verify extensions are accessible
    for key, value in extensions.items():
        assert doc.get_extension(key) == value

    # Verify regular fields are in the document
    doc_dict = doc.to_dict()
    for key, value in regular_fields.items():
        assert doc_dict[key] == value

    # Verify regular fields are NOT in extensions
    for key in regular_fields.keys():
        assert doc.get_extension(key) is None


@given(
    key=non_extension_key_strategy,
    value=extension_value_strategy,
)
def test_extension_property_validation(key: str, value: any) -> None:
    """
    Feature: laag-python-port, Property 3: Extension Property Validation

    **Validates: Requirements 11.6**

    For any property name that does not start with "x-", attempting to set it
    as an extension property should raise a ValueError.
    """
    doc = TestDocument()

    # Attempting to set a non-extension key should raise ValueError
    with pytest.raises(ValueError, match="Extension property must start with 'x-'"):
        doc.set_extension(key, value)

    # Verify the property was not set
    assert doc.get_extension(key) is None
    assert key not in doc.to_dict()


@given(value=extension_value_strategy)
def test_extension_validation_with_edge_cases(value: any) -> None:
    """
    Feature: laag-python-port, Property 3: Extension Property Validation

    **Validates: Requirements 11.6**

    Test extension validation with various edge cases.
    """
    doc = TestDocument()

    # Valid: starts with x-
    doc.set_extension("x-valid", value)
    assert doc.get_extension("x-valid") == value

    # Invalid: empty string
    with pytest.raises(ValueError):
        doc.set_extension("", value)

    # Invalid: just "x"
    with pytest.raises(ValueError):
        doc.set_extension("x", value)

    # Invalid: "X-" (uppercase)
    with pytest.raises(ValueError):
        doc.set_extension("X-test", value)

    # Invalid: starts with "x" but no dash
    with pytest.raises(ValueError):
        doc.set_extension("xtest", value)

    # Invalid: regular property name
    with pytest.raises(ValueError):
        doc.set_extension("regular", value)
