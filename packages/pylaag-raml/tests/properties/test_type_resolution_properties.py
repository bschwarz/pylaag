"""Property-based tests for RAML type resolution."""

from hypothesis import given
from hypothesis import strategies as st
from pylaag_raml import RAMLDocument, TypeManager

# Strategy for generating valid type names
type_name_strategy = st.text(
    min_size=1,
    max_size=50,
    alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"), whitelist_characters="_"),
)


# Strategy for generating type definitions
@st.composite
def type_definition_strategy(draw):
    """Generate valid type definitions."""
    type_kind = draw(st.sampled_from(["object", "string", "number", "integer", "boolean", "array"]))

    type_def = {"type": type_kind}

    if type_kind == "object":
        type_def["properties"] = {
            draw(st.text(min_size=1, max_size=20)): {"type": "string"}
            for _ in range(draw(st.integers(min_value=1, max_value=3)))
        }
    elif type_kind == "array":
        type_def["items"] = {"type": "string"}
    elif type_kind == "string":
        type_def["minLength"] = draw(st.integers(min_value=0, max_value=10))
        type_def["maxLength"] = draw(st.integers(min_value=10, max_value=100))

    return type_def


@given(type_name=type_name_strategy, type_def=type_definition_strategy())
def test_raml_type_addition_and_resolution(type_name: str, type_def: dict) -> None:
    """
    Feature: laag-python-port, Property 27: RAML Type Resolution

    **Validates: Requirements 13.4**

    For any type reference in a RAML document, resolving the type should
    return the type definition if it exists, or None if it doesn't.
    """
    # Create a valid RAML document
    doc = RAMLDocument()
    type_mgr = TypeManager(doc)

    # Add type
    type_mgr.add_type(type_name, type_def)

    # Resolve type - should return the definition
    resolved = type_mgr.get_type(type_name)
    assert resolved == type_def


@given(type_name=type_name_strategy)
def test_raml_type_resolution_nonexistent_returns_none(type_name: str) -> None:
    """
    Feature: laag-python-port, Property 27: RAML Type Resolution

    **Validates: Requirements 13.4**

    Resolving a non-existent type should return None.
    """
    # Create a valid RAML document
    doc = RAMLDocument()
    type_mgr = TypeManager(doc)

    # Try to resolve non-existent type
    resolved = type_mgr.get_type(type_name)
    assert resolved is None


@given(type_name=type_name_strategy, type_def=type_definition_strategy())
def test_raml_type_removal_makes_resolution_return_none(type_name: str, type_def: dict) -> None:
    """
    Feature: laag-python-port, Property 27: RAML Type Resolution

    **Validates: Requirements 13.4**

    After removing a type, resolving it should return None.
    """
    # Create a valid RAML document
    doc = RAMLDocument()
    type_mgr = TypeManager(doc)

    # Add type
    type_mgr.add_type(type_name, type_def)

    # Verify it exists
    assert type_mgr.get_type(type_name) == type_def

    # Remove type
    result = type_mgr.remove_type(type_name)
    assert result is True

    # Resolve type - should return None
    resolved = type_mgr.get_type(type_name)
    assert resolved is None


@given(
    type_names=st.lists(type_name_strategy, min_size=2, max_size=5, unique=True),
    type_defs=st.lists(type_definition_strategy(), min_size=2, max_size=5),
)
def test_raml_multiple_types_resolution(type_names: list, type_defs: list) -> None:
    """
    Feature: laag-python-port, Property 27: RAML Type Resolution

    **Validates: Requirements 13.4**

    Multiple types should be independently resolvable.
    """
    # Create a valid RAML document
    doc = RAMLDocument()
    type_mgr = TypeManager(doc)

    # Add multiple types
    for type_name, type_def in zip(type_names, type_defs, strict=False):
        type_mgr.add_type(type_name, type_def)

    # All types should be resolvable
    for type_name, type_def in zip(type_names, type_defs, strict=False):
        resolved = type_mgr.get_type(type_name)
        assert resolved == type_def


@given(
    type_name=type_name_strategy,
    type_def1=type_definition_strategy(),
    type_def2=type_definition_strategy(),
)
def test_raml_type_overwrite(type_name: str, type_def1: dict, type_def2: dict) -> None:
    """
    Feature: laag-python-port, Property 27: RAML Type Resolution

    **Validates: Requirements 13.4**

    Adding a type with the same name should overwrite the previous definition.
    """
    # Create a valid RAML document
    doc = RAMLDocument()
    type_mgr = TypeManager(doc)

    # Add first type
    type_mgr.add_type(type_name, type_def1)
    assert type_mgr.get_type(type_name) == type_def1

    # Add second type with same name
    type_mgr.add_type(type_name, type_def2)

    # Should resolve to the second definition
    resolved = type_mgr.get_type(type_name)
    assert resolved == type_def2


def test_raml_type_manager_ensures_types_section() -> None:
    """
    Feature: laag-python-port, Property 27: RAML Type Resolution

    **Validates: Requirements 13.4**

    TypeManager should create the types section if it doesn't exist.
    """
    # Create a document without types section
    doc = RAMLDocument()
    assert "types" not in doc.to_dict()

    type_mgr = TypeManager(doc)
    type_mgr.add_type("User", {"type": "object"})

    # Types section should now exist
    assert "types" in doc.to_dict()
    assert "User" in doc.to_dict()["types"]


def test_raml_type_manager_remove_nonexistent_returns_false() -> None:
    """
    Feature: laag-python-port, Property 27: RAML Type Resolution

    **Validates: Requirements 13.4**

    Removing a non-existent type should return False.
    """
    doc = RAMLDocument()
    type_mgr = TypeManager(doc)

    result = type_mgr.remove_type("NonExistent")
    assert result is False


def test_raml_type_manager_remove_from_empty_document_returns_false() -> None:
    """
    Feature: laag-python-port, Property 27: RAML Type Resolution

    **Validates: Requirements 13.4**

    Removing a type from a document without types section should return False.
    """
    doc = RAMLDocument()
    type_mgr = TypeManager(doc)

    # Don't add any types
    result = type_mgr.remove_type("User")
    assert result is False
