"""Property-based tests for Smithy shape management."""

from hypothesis import given
from hypothesis import strategies as st
from pylaag_smithy import ShapeManager, SmithyDocument


@st.composite
def shape_id_strategy(draw):
    """Generate valid Smithy shape IDs."""
    namespace = draw(
        st.text(
            min_size=1,
            max_size=20,
            alphabet=st.characters(
                whitelist_categories=("Ll", "Lu", "Nd"), whitelist_characters="."
            ),
        )
    )
    name = draw(
        st.text(
            min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"))
        )
    )
    return f"{namespace}#{name}"


@st.composite
def shape_type_strategy(draw):
    """Generate valid Smithy shape types."""
    return draw(
        st.sampled_from(
            [
                "service",
                "operation",
                "resource",
                "structure",
                "union",
                "list",
                "map",
                "string",
                "integer",
                "long",
                "float",
                "double",
                "boolean",
                "blob",
                "timestamp",
            ]
        )
    )


@st.composite
def shape_def_strategy(draw):
    """Generate valid shape definitions."""
    # Simple shape definition with optional members
    shape_def = {}

    # Add members for structure types
    if draw(st.booleans()):
        members = draw(
            st.dictionaries(
                keys=st.text(
                    min_size=1,
                    max_size=10,
                    alphabet=st.characters(whitelist_categories=("Ll", "Lu")),
                ),
                values=st.fixed_dictionaries({"target": st.text(min_size=1, max_size=20)}),
                max_size=3,
            )
        )
        if members:
            shape_def["members"] = members

    return shape_def


@given(
    shape_id=shape_id_strategy(), shape_type=shape_type_strategy(), shape_def=shape_def_strategy()
)
def test_shape_management_maintains_validity(shape_id, shape_type, shape_def):
    """
    Feature: laag-python-port, Property 30: Smithy Shape Management

    **Validates: Requirements 14.3**

    For any valid Smithy document, adding or removing shapes should maintain
    document validity (all required fields present).
    """
    # Create a valid document
    doc = SmithyDocument()
    doc.validate()  # Should not raise

    # Add a shape
    shape_mgr = ShapeManager(doc)
    shape_mgr.add_shape(shape_id, shape_type, shape_def)

    # Document should still be valid
    doc.validate()  # Should not raise

    # Verify the shape was added
    retrieved_shape = shape_mgr.get_shape(shape_id)
    assert retrieved_shape is not None
    assert retrieved_shape["type"] == shape_type

    # Remove the shape
    removed = shape_mgr.remove_shape(shape_id)
    assert removed is True

    # Document should still be valid
    doc.validate()  # Should not raise

    # Verify the shape was removed
    assert shape_mgr.get_shape(shape_id) is None


@given(
    shape_id=shape_id_strategy(), shape_type=shape_type_strategy(), shape_def=shape_def_strategy()
)
def test_add_shape_preserves_definition(shape_id, shape_type, shape_def):
    """
    Feature: laag-python-port, Property 30: Smithy Shape Management

    **Validates: Requirements 14.3**

    Adding a shape should preserve all fields in the shape definition.
    """
    doc = SmithyDocument()
    shape_mgr = ShapeManager(doc)

    # Add the shape
    shape_mgr.add_shape(shape_id, shape_type, shape_def)

    # Retrieve and verify
    retrieved = shape_mgr.get_shape(shape_id)
    assert retrieved is not None
    assert retrieved["type"] == shape_type

    # Verify all fields from shape_def are present
    for key, value in shape_def.items():
        assert key in retrieved
        assert retrieved[key] == value


@given(shape_id=shape_id_strategy())
def test_remove_nonexistent_shape_returns_false(shape_id):
    """
    Feature: laag-python-port, Property 30: Smithy Shape Management

    **Validates: Requirements 14.3**

    Removing a non-existent shape should return False.
    """
    doc = SmithyDocument()
    shape_mgr = ShapeManager(doc)

    # Try to remove a shape that doesn't exist
    removed = shape_mgr.remove_shape(shape_id)
    assert removed is False


@given(shape_id=shape_id_strategy())
def test_get_nonexistent_shape_returns_none(shape_id):
    """
    Feature: laag-python-port, Property 30: Smithy Shape Management

    **Validates: Requirements 14.3**

    Getting a non-existent shape should return None.
    """
    doc = SmithyDocument()
    shape_mgr = ShapeManager(doc)

    # Try to get a shape that doesn't exist
    shape = shape_mgr.get_shape(shape_id)
    assert shape is None
