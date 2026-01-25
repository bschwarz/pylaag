"""Property-based tests for Smithy trait application."""

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pylaag_core import NotFoundError
from pylaag_smithy import ShapeManager, SmithyDocument, TraitManager


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
def trait_name_strategy(draw):
    """Generate valid trait names."""
    namespace = draw(
        st.text(
            min_size=1,
            max_size=20,
            alphabet=st.characters(whitelist_categories=("Ll", "Lu"), whitelist_characters="."),
        )
    )
    name = draw(
        st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("Ll", "Lu")))
    )
    return f"{namespace}#{name}"


@st.composite
def trait_value_strategy(draw):
    """Generate valid trait values."""
    return draw(
        st.one_of(
            st.none(),
            st.dictionaries(
                keys=st.text(
                    min_size=1,
                    max_size=10,
                    alphabet=st.characters(whitelist_categories=("Ll", "Lu")),
                ),
                values=st.one_of(st.text(max_size=20), st.integers(), st.booleans()),
                max_size=3,
            ),
        )
    )


@given(
    shape_id=shape_id_strategy(),
    trait_name=trait_name_strategy(),
    trait_value=trait_value_strategy(),
)
def test_trait_application_adds_to_shape(shape_id, trait_name, trait_value):
    """
    Feature: laag-python-port, Property 32: Smithy Trait Application

    **Validates: Requirements 14.4**

    For any shape in a Smithy document, adding a trait should result in
    the trait appearing in the shape's traits collection.
    """
    doc = SmithyDocument()
    shape_mgr = ShapeManager(doc)
    trait_mgr = TraitManager(doc)

    # Add a shape first
    shape_mgr.add_shape(shape_id, "structure", {})

    # Add a trait to the shape
    trait_mgr.add_trait_to_shape(shape_id, trait_name, trait_value)

    # Verify the trait was added
    retrieved_trait = trait_mgr.get_trait(shape_id, trait_name)

    if trait_value is None:
        # None should be stored as empty dict
        assert retrieved_trait == {}
    else:
        assert retrieved_trait == trait_value


@given(shape_id=shape_id_strategy(), trait_name=trait_name_strategy())
def test_trait_application_to_nonexistent_shape_raises_error(shape_id, trait_name):
    """
    Feature: laag-python-port, Property 32: Smithy Trait Application

    **Validates: Requirements 14.4**

    Adding a trait to a non-existent shape should raise NotFoundError.
    """
    doc = SmithyDocument()
    trait_mgr = TraitManager(doc)

    # Try to add a trait to a non-existent shape
    with pytest.raises(NotFoundError) as exc_info:
        trait_mgr.add_trait_to_shape(shape_id, trait_name, {})

    # Verify the error contains the shape ID
    assert shape_id in str(exc_info.value)


@given(
    shape_id=shape_id_strategy(),
    trait_names=st.lists(trait_name_strategy(), min_size=1, max_size=5, unique=True),
)
def test_multiple_traits_on_same_shape(shape_id, trait_names):
    """
    Feature: laag-python-port, Property 32: Smithy Trait Application

    **Validates: Requirements 14.4**

    Multiple traits can be added to the same shape.
    """
    doc = SmithyDocument()
    shape_mgr = ShapeManager(doc)
    trait_mgr = TraitManager(doc)

    # Add a shape
    shape_mgr.add_shape(shape_id, "structure", {})

    # Add multiple traits
    for i, trait_name in enumerate(trait_names):
        trait_value = {"index": i}
        trait_mgr.add_trait_to_shape(shape_id, trait_name, trait_value)

    # Verify all traits were added
    for i, trait_name in enumerate(trait_names):
        retrieved = trait_mgr.get_trait(shape_id, trait_name)
        assert retrieved == {"index": i}


@given(
    shape_id=shape_id_strategy(),
    trait_name=trait_name_strategy(),
    trait_value=trait_value_strategy(),
)
def test_remove_trait_from_shape(shape_id, trait_name, trait_value):
    """
    Feature: laag-python-port, Property 32: Smithy Trait Application

    **Validates: Requirements 14.4**

    Removing a trait should remove it from the shape's traits collection.
    """
    doc = SmithyDocument()
    shape_mgr = ShapeManager(doc)
    trait_mgr = TraitManager(doc)

    # Add a shape and trait
    shape_mgr.add_shape(shape_id, "structure", {})
    trait_mgr.add_trait_to_shape(shape_id, trait_name, trait_value)

    # Verify the trait exists
    assert trait_mgr.get_trait(shape_id, trait_name) is not None

    # Remove the trait
    removed = trait_mgr.remove_trait_from_shape(shape_id, trait_name)
    assert removed is True

    # Verify the trait was removed
    assert trait_mgr.get_trait(shape_id, trait_name) is None


@given(shape_id=shape_id_strategy(), trait_name=trait_name_strategy())
def test_remove_nonexistent_trait_returns_false(shape_id, trait_name):
    """
    Feature: laag-python-port, Property 32: Smithy Trait Application

    **Validates: Requirements 14.4**

    Removing a non-existent trait should return False.
    """
    doc = SmithyDocument()
    shape_mgr = ShapeManager(doc)
    trait_mgr = TraitManager(doc)

    # Add a shape without any traits
    shape_mgr.add_shape(shape_id, "structure", {})

    # Try to remove a non-existent trait
    removed = trait_mgr.remove_trait_from_shape(shape_id, trait_name)
    assert removed is False


@given(shape_id=shape_id_strategy(), trait_name=trait_name_strategy())
def test_get_trait_from_nonexistent_shape_returns_none(shape_id, trait_name):
    """
    Feature: laag-python-port, Property 32: Smithy Trait Application

    **Validates: Requirements 14.4**

    Getting a trait from a non-existent shape should return None.
    """
    doc = SmithyDocument()
    trait_mgr = TraitManager(doc)

    # Try to get a trait from a non-existent shape
    trait = trait_mgr.get_trait(shape_id, trait_name)
    assert trait is None
