"""Property-based tests for OpenAPI component management."""

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pylaag.openapi import ComponentManager, ComponentType, OpenAPIDocument

# Strategy for generating component types
component_type_strategy = st.sampled_from(
    [
        "schemas",
        "responses",
        "parameters",
        "examples",
        "requestBodies",
        "headers",
        "securitySchemes",
        "links",
        "callbacks",
    ]
)


# Strategy for generating component names
component_name_strategy = st.text(
    min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"))
).filter(lambda s: s and s[0].isalpha())


# Strategy for generating simple component definitions
@st.composite
def component_definition_strategy(draw):
    """Generate simple component definitions."""
    return {
        "type": draw(st.sampled_from(["object", "string", "number", "array"])),
        "description": draw(st.text(max_size=100)),
    }


@given(
    component_type=component_type_strategy,
    component_name=component_name_strategy,
    component_def=component_definition_strategy(),
)
def test_reference_resolution_existing_component(
    component_type: ComponentType, component_name: str, component_def: dict
) -> None:
    """
    Feature: laag-python-port, Property 9: Reference Resolution

    **Validates: Requirements 5.4**

    For any valid $ref reference in the format #/components/{type}/{name},
    resolving the reference should return the component if it exists.
    """
    # Create document and component manager
    doc = OpenAPIDocument()
    comp_mgr = ComponentManager(doc)

    # Add a component
    comp_mgr.add_component(component_type, component_name, component_def)

    # Build the reference string
    ref = f"#/components/{component_type}/{component_name}"

    # Resolve the reference
    resolved = comp_mgr.resolve_reference(ref)

    # Should return the component
    assert resolved is not None
    assert resolved == component_def


@given(
    component_type=component_type_strategy,
    component_name=component_name_strategy,
)
def test_reference_resolution_nonexistent_component(
    component_type: ComponentType, component_name: str
) -> None:
    """
    Feature: laag-python-port, Property 9: Reference Resolution

    **Validates: Requirements 5.4**

    For any valid $ref reference to a non-existent component,
    resolving the reference should return None.
    """
    # Create document and component manager
    doc = OpenAPIDocument()
    comp_mgr = ComponentManager(doc)

    # Build the reference string (without adding the component)
    ref = f"#/components/{component_type}/{component_name}"

    # Resolve the reference
    resolved = comp_mgr.resolve_reference(ref)

    # Should return None
    assert resolved is None


@given(
    component_type=component_type_strategy,
    component_name=component_name_strategy,
    component_def=component_definition_strategy(),
)
def test_reference_resolution_nested_paths(
    component_type: ComponentType, component_name: str, component_def: dict
) -> None:
    """
    Feature: laag-python-port, Property 9: Reference Resolution

    **Validates: Requirements 5.4**

    Reference resolution should work for nested paths within components.
    """
    # Create document and component manager
    doc = OpenAPIDocument()
    comp_mgr = ComponentManager(doc)

    # Add a component with nested structure
    nested_component = {
        "type": "object",
        "properties": {
            "nested": component_def,
        },
    }
    comp_mgr.add_component(component_type, component_name, nested_component)

    # Resolve the top-level reference
    ref = f"#/components/{component_type}/{component_name}"
    resolved = comp_mgr.resolve_reference(ref)
    assert resolved == nested_component

    # Resolve a nested reference
    nested_ref = f"#/components/{component_type}/{component_name}/properties/nested"
    nested_resolved = comp_mgr.resolve_reference(nested_ref)
    assert nested_resolved == component_def


@given(
    invalid_ref=st.one_of(
        st.text(min_size=1, max_size=50).filter(lambda s: not s.startswith("#/")),
        st.just("http://example.com/schema"),
        st.just("../other/schema"),
        st.just("file:///path/to/schema"),
    )
)
def test_reference_resolution_rejects_non_local_refs(invalid_ref: str) -> None:
    """
    Feature: laag-python-port, Property 9: Reference Resolution

    **Validates: Requirements 5.4**

    Reference resolution should reject non-local references
    (those not starting with #/).
    """
    # Create document and component manager
    doc = OpenAPIDocument()
    comp_mgr = ComponentManager(doc)

    # Should raise ValueError for non-local references
    with pytest.raises(ValueError, match="Only local references are supported"):
        comp_mgr.resolve_reference(invalid_ref)


@given(
    component_type=component_type_strategy,
    component_name=component_name_strategy,
    component_def=component_definition_strategy(),
)
def test_reference_resolution_after_component_removal(
    component_type: ComponentType, component_name: str, component_def: dict
) -> None:
    """
    Feature: laag-python-port, Property 9: Reference Resolution

    **Validates: Requirements 5.4**

    After removing a component, its reference should resolve to None.
    """
    # Create document and component manager
    doc = OpenAPIDocument()
    comp_mgr = ComponentManager(doc)

    # Add a component
    comp_mgr.add_component(component_type, component_name, component_def)

    # Build the reference string
    ref = f"#/components/{component_type}/{component_name}"

    # Verify it resolves
    assert comp_mgr.resolve_reference(ref) == component_def

    # Remove the component
    removed = comp_mgr.remove_component(component_type, component_name)
    assert removed is True

    # Now it should resolve to None
    assert comp_mgr.resolve_reference(ref) is None


@given(
    component_type=component_type_strategy,
    component_name=component_name_strategy,
    component_def1=component_definition_strategy(),
    component_def2=component_definition_strategy(),
)
def test_reference_resolution_after_component_update(
    component_type: ComponentType,
    component_name: str,
    component_def1: dict,
    component_def2: dict,
) -> None:
    """
    Feature: laag-python-port, Property 9: Reference Resolution

    **Validates: Requirements 5.4**

    After updating a component, its reference should resolve to the new value.
    """
    # Create document and component manager
    doc = OpenAPIDocument()
    comp_mgr = ComponentManager(doc)

    # Add a component
    comp_mgr.add_component(component_type, component_name, component_def1)

    # Build the reference string
    ref = f"#/components/{component_type}/{component_name}"

    # Verify it resolves to the first definition
    assert comp_mgr.resolve_reference(ref) == component_def1

    # Update the component
    comp_mgr.add_component(component_type, component_name, component_def2)

    # Now it should resolve to the second definition
    assert comp_mgr.resolve_reference(ref) == component_def2


@given(
    component_type=component_type_strategy,
    component_name=component_name_strategy,
    component_def=component_definition_strategy(),
)
def test_document_validity_after_component_deletion(
    component_type: ComponentType, component_name: str, component_def: dict
) -> None:
    """
    Feature: laag-python-port, Property 10: Document Validity After Component Deletion

    **Validates: Requirements 4.6, 5.5**

    For any valid OpenAPI document, removing a component should result in
    a document that either remains valid or has only the removed component's
    references broken (not other validation errors).
    """
    # Create a valid document
    doc = OpenAPIDocument()
    comp_mgr = ComponentManager(doc)

    # Document should be valid initially
    doc.validate()

    # Add a component
    comp_mgr.add_component(component_type, component_name, component_def)

    # Document should still be valid
    doc.validate()

    # Remove the component
    removed = comp_mgr.remove_component(component_type, component_name)
    assert removed is True

    # Document should still be valid (required fields still present)
    # Even though references to the removed component would be broken,
    # the document structure itself should remain valid
    doc.validate()

    # Verify the component is actually gone
    assert comp_mgr.get_component(component_type, component_name) is None


@given(
    component_type=component_type_strategy,
    num_components=st.integers(min_value=1, max_value=5),
)
def test_document_validity_after_multiple_component_deletions(
    component_type: ComponentType, num_components: int
) -> None:
    """
    Feature: laag-python-port, Property 10: Document Validity After Component Deletion

    **Validates: Requirements 4.6, 5.5**

    Removing multiple components should maintain document validity.
    """
    # Create a valid document
    doc = OpenAPIDocument()
    comp_mgr = ComponentManager(doc)

    # Document should be valid initially
    doc.validate()

    # Add multiple components
    component_names = [f"Component{i}" for i in range(num_components)]
    for name in component_names:
        comp_mgr.add_component(
            component_type, name, {"type": "object", "description": f"Component {name}"}
        )

    # Document should still be valid
    doc.validate()

    # Remove all components one by one
    for name in component_names:
        removed = comp_mgr.remove_component(component_type, name)
        assert removed is True

        # Document should remain valid after each deletion
        doc.validate()

    # Verify all components are gone
    for name in component_names:
        assert comp_mgr.get_component(component_type, name) is None


@given(
    component_type=component_type_strategy,
    component_name=component_name_strategy,
    component_def=component_definition_strategy(),
)
def test_document_validity_preserved_with_extension_properties(
    component_type: ComponentType, component_name: str, component_def: dict
) -> None:
    """
    Feature: laag-python-port, Property 10: Document Validity After Component Deletion

    **Validates: Requirements 4.6, 5.5**

    Document validity should be preserved even when components have
    extension properties.
    """
    # Create a valid document with extension properties
    doc = OpenAPIDocument()
    doc.set_extension("x-custom", "value")
    comp_mgr = ComponentManager(doc)

    # Document should be valid
    doc.validate()

    # Add a component with extension properties
    component_with_ext = {**component_def, "x-internal": True}
    comp_mgr.add_component(component_type, component_name, component_with_ext)

    # Document should still be valid
    doc.validate()

    # Remove the component
    removed = comp_mgr.remove_component(component_type, component_name)
    assert removed is True

    # Document should still be valid
    doc.validate()

    # Extension properties on the document should be preserved
    assert doc.get_extension("x-custom") == "value"
