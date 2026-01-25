"""Property-based tests for Smithy target resolution."""

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
                "structure",
                "string",
                "integer",
                "boolean",
            ]
        )
    )


@given(shape_id=shape_id_strategy(), shape_type=shape_type_strategy())
def test_resolve_target_returns_existing_shape(shape_id, shape_type):
    """
    Feature: laag-python-port, Property 31: Smithy Target Resolution

    **Validates: Requirements 14.3**

    For any target reference in a Smithy document, resolving the target
    should return the shape if it exists.
    """
    doc = SmithyDocument()
    shape_mgr = ShapeManager(doc)

    # Add a shape
    shape_def = {"description": "Test shape"}
    shape_mgr.add_shape(shape_id, shape_type, shape_def)

    # Resolve the target
    resolved = shape_mgr.resolve_target(shape_id)

    # Should return the shape
    assert resolved is not None
    assert resolved["type"] == shape_type
    assert resolved["description"] == "Test shape"


@given(target=shape_id_strategy())
def test_resolve_target_returns_none_for_nonexistent(target):
    """
    Feature: laag-python-port, Property 31: Smithy Target Resolution

    **Validates: Requirements 14.3**

    For any target reference in a Smithy document, resolving the target
    should return None if it doesn't exist.
    """
    doc = SmithyDocument()
    shape_mgr = ShapeManager(doc)

    # Try to resolve a non-existent target
    resolved = shape_mgr.resolve_target(target)

    # Should return None
    assert resolved is None


@given(shape_id=shape_id_strategy(), shape_type=shape_type_strategy())
def test_resolve_target_equivalent_to_get_shape(shape_id, shape_type):
    """
    Feature: laag-python-port, Property 31: Smithy Target Resolution

    **Validates: Requirements 14.3**

    Resolving a target should be equivalent to getting the shape directly.
    """
    doc = SmithyDocument()
    shape_mgr = ShapeManager(doc)

    # Add a shape
    shape_def = {"description": "Test shape"}
    shape_mgr.add_shape(shape_id, shape_type, shape_def)

    # Both methods should return the same result
    resolved = shape_mgr.resolve_target(shape_id)
    direct = shape_mgr.get_shape(shape_id)

    assert resolved == direct


@given(
    shape_ids=st.lists(shape_id_strategy(), min_size=1, max_size=5, unique=True),
    shape_type=shape_type_strategy(),
)
def test_resolve_multiple_targets(shape_ids, shape_type):
    """
    Feature: laag-python-port, Property 31: Smithy Target Resolution

    **Validates: Requirements 14.3**

    Multiple shapes can be resolved independently.
    """
    doc = SmithyDocument()
    shape_mgr = ShapeManager(doc)

    # Add multiple shapes
    for i, shape_id in enumerate(shape_ids):
        shape_def = {"description": f"Shape {i}"}
        shape_mgr.add_shape(shape_id, shape_type, shape_def)

    # Resolve each target
    for i, shape_id in enumerate(shape_ids):
        resolved = shape_mgr.resolve_target(shape_id)
        assert resolved is not None
        assert resolved["description"] == f"Shape {i}"
