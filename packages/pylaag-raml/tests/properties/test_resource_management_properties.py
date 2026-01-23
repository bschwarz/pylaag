"""Property-based tests for RAML resource management."""

from hypothesis import given
from hypothesis import strategies as st
from pylaag_raml import RAMLDocument, ResourceManager


# Strategy for generating valid resource paths
@st.composite
def resource_path_strategy(draw):
    """Generate valid resource paths."""
    # RAML resource paths start with /
    segments = draw(
        st.lists(
            st.text(
                min_size=1,
                max_size=20,
                alphabet=st.characters(
                    whitelist_categories=("Ll", "Lu", "Nd"), whitelist_characters="-_"
                ),
            ),
            min_size=1,
            max_size=3,
        )
    )
    return "/" + "/".join(segments)


# Strategy for generating HTTP methods
http_method_strategy = st.sampled_from(["get", "post", "put", "delete", "patch", "options", "head"])


# Strategy for generating method definitions
@st.composite
def method_definition_strategy(draw):
    """Generate valid method definitions."""
    return {
        "description": draw(st.text(max_size=200)),
        "responses": {"200": {"description": draw(st.text(max_size=100))}},
    }


@given(
    path=resource_path_strategy(),
    resource_def=st.dictionaries(
        keys=st.text(min_size=1, max_size=20), values=st.text(max_size=100), max_size=5
    ),
)
def test_raml_resource_addition_maintains_validity(path: str, resource_def: dict) -> None:
    """
    Feature: laag-python-port, Property 26: RAML Resource Management

    **Validates: Requirements 13.3**

    For any valid RAML document, adding a resource should maintain
    document validity (all required fields present).
    """
    # Create a valid RAML document
    doc = RAMLDocument()
    doc.validate()  # Should not raise

    # Add resource
    resource_mgr = ResourceManager(doc)
    resource_mgr.add_resource(path, resource_def)

    # Document should still be valid
    doc.validate()  # Should not raise

    # Resource should be retrievable
    retrieved = resource_mgr.get_resource(path)
    assert retrieved == resource_def


@given(path=resource_path_strategy())
def test_raml_resource_removal_maintains_validity(path: str) -> None:
    """
    Feature: laag-python-port, Property 26: RAML Resource Management

    **Validates: Requirements 13.3**

    For any valid RAML document, removing a resource should maintain
    document validity (all required fields present).
    """
    # Create a valid RAML document with a resource
    doc = RAMLDocument()
    resource_mgr = ResourceManager(doc)
    resource_mgr.add_resource(path, {"description": "Test resource"})
    doc.validate()  # Should not raise

    # Remove resource
    result = resource_mgr.remove_resource(path)
    assert result is True

    # Document should still be valid
    doc.validate()  # Should not raise

    # Resource should not be retrievable
    assert resource_mgr.get_resource(path) is None


@given(
    path=resource_path_strategy(),
    method=http_method_strategy,
    method_def=method_definition_strategy(),
)
def test_raml_method_addition_maintains_validity(path: str, method: str, method_def: dict) -> None:
    """
    Feature: laag-python-port, Property 26: RAML Resource Management

    **Validates: Requirements 13.3**

    For any valid RAML document, adding a method to a resource should
    maintain document validity.
    """
    # Create a valid RAML document
    doc = RAMLDocument()
    resource_mgr = ResourceManager(doc)

    # Add method (should create resource if it doesn't exist)
    resource_mgr.add_method(path, method, method_def)

    # Document should still be valid
    doc.validate()  # Should not raise

    # Method should be retrievable
    resource = resource_mgr.get_resource(path)
    assert resource is not None
    assert method in resource
    assert resource[method] == method_def


@given(
    path=resource_path_strategy(),
    method=http_method_strategy,
    method_def=method_definition_strategy(),
)
def test_raml_method_removal_maintains_validity(path: str, method: str, method_def: dict) -> None:
    """
    Feature: laag-python-port, Property 26: RAML Resource Management

    **Validates: Requirements 13.3**

    For any valid RAML document, removing a method from a resource should
    maintain document validity.
    """
    # Create a valid RAML document with a method
    doc = RAMLDocument()
    resource_mgr = ResourceManager(doc)
    resource_mgr.add_method(path, method, method_def)
    doc.validate()  # Should not raise

    # Remove method
    result = resource_mgr.remove_method(path, method)
    assert result is True

    # Document should still be valid
    doc.validate()  # Should not raise

    # Method should not be in resource
    resource = resource_mgr.get_resource(path)
    assert resource is not None
    assert method not in resource


@given(
    paths=st.lists(resource_path_strategy(), min_size=1, max_size=5, unique=True),
    methods=st.lists(http_method_strategy, min_size=1, max_size=3, unique=True),
)
def test_raml_multiple_resources_and_methods_maintain_validity(paths: list, methods: list) -> None:
    """
    Feature: laag-python-port, Property 26: RAML Resource Management

    **Validates: Requirements 13.3**

    Adding multiple resources and methods should maintain document validity.
    """
    # Create a valid RAML document
    doc = RAMLDocument()
    resource_mgr = ResourceManager(doc)

    # Add multiple resources with multiple methods
    for path in paths:
        for method in methods:
            resource_mgr.add_method(
                path,
                method,
                {
                    "description": f"{method.upper()} {path}",
                    "responses": {"200": {"description": "Success"}},
                },
            )

    # Document should still be valid
    doc.validate()  # Should not raise

    # All resources and methods should be retrievable
    for path in paths:
        resource = resource_mgr.get_resource(path)
        assert resource is not None
        for method in methods:
            assert method in resource


def test_raml_resource_manager_add_resource_creates_empty_if_none() -> None:
    """
    Feature: laag-python-port, Property 26: RAML Resource Management

    **Validates: Requirements 13.3**

    Adding a resource with None should create an empty resource definition.
    """
    doc = RAMLDocument()
    resource_mgr = ResourceManager(doc)

    resource_mgr.add_resource("/users", None)

    resource = resource_mgr.get_resource("/users")
    assert resource == {}


def test_raml_resource_manager_remove_nonexistent_returns_false() -> None:
    """
    Feature: laag-python-port, Property 26: RAML Resource Management

    **Validates: Requirements 13.3**

    Removing a non-existent resource should return False.
    """
    doc = RAMLDocument()
    resource_mgr = ResourceManager(doc)

    result = resource_mgr.remove_resource("/nonexistent")
    assert result is False


def test_raml_resource_manager_remove_method_nonexistent_returns_false() -> None:
    """
    Feature: laag-python-port, Property 26: RAML Resource Management

    **Validates: Requirements 13.3**

    Removing a non-existent method should return False.
    """
    doc = RAMLDocument()
    resource_mgr = ResourceManager(doc)

    # Add resource without methods
    resource_mgr.add_resource("/users", {})

    result = resource_mgr.remove_method("/users", "get")
    assert result is False


def test_raml_resource_manager_get_nonexistent_returns_none() -> None:
    """
    Feature: laag-python-port, Property 26: RAML Resource Management

    **Validates: Requirements 13.3**

    Getting a non-existent resource should return None.
    """
    doc = RAMLDocument()
    resource_mgr = ResourceManager(doc)

    resource = resource_mgr.get_resource("/nonexistent")
    assert resource is None
