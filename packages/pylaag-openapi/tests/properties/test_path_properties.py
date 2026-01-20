"""Property-based tests for OpenAPI path and operation management."""

from hypothesis import given
from hypothesis import strategies as st
from pylaag_openapi import OpenAPIDocument, PathManager


# Strategy for generating valid OpenAPI documents
@st.composite
def openapi_document_strategy(draw):
    """Generate valid OpenAPI documents."""
    return {
        "openapi": draw(st.sampled_from(["3.0.0", "3.0.1", "3.0.2", "3.0.3", "3.1.0"])),
        "info": {
            "title": draw(st.text(min_size=1, max_size=100)),
            "version": draw(st.text(min_size=1, max_size=50)),
            "description": draw(st.text(max_size=200)),
        },
        "paths": draw(
            st.dictionaries(
                keys=st.text(min_size=1, max_size=50).map(lambda s: f"/{s}"),
                values=st.dictionaries(
                    keys=st.sampled_from(["get", "post", "put", "delete", "patch"]),
                    values=st.fixed_dictionaries(
                        {
                            "summary": st.text(max_size=100),
                            "responses": st.fixed_dictionaries(
                                {
                                    "200": st.fixed_dictionaries(
                                        {"description": st.text(max_size=100)}
                                    )
                                }
                            ),
                        }
                    ),
                    max_size=3,
                ),
                max_size=5,
            )
        ),
    }


# Strategy for generating path strings
path_strategy = st.text(min_size=1, max_size=50).map(lambda s: f"/{s.replace('/', '_')}")

# Strategy for generating HTTP methods
http_method_strategy = st.sampled_from(
    ["get", "post", "put", "delete", "patch", "options", "head", "trace"]
)

# Strategy for generating operation objects
operation_strategy = st.fixed_dictionaries(
    {
        "summary": st.text(max_size=100),
        "responses": st.fixed_dictionaries(
            {"200": st.fixed_dictionaries({"description": st.text(max_size=100)})}
        ),
    }
)


@given(
    doc_dict=openapi_document_strategy(),
    path=path_strategy,
    method=http_method_strategy,
    operation=operation_strategy,
)
def test_document_validity_after_adding_operation(
    doc_dict: dict, path: str, method: str, operation: dict
) -> None:
    """
    Feature: laag-python-port, Property 11: Document Validity After Operation Modification

    **Validates: Requirements 12.6**

    For any valid OpenAPI document, adding an operation should maintain
    document validity (all required fields present).
    """
    # Create a valid document
    doc = OpenAPIDocument(doc_dict)

    # Verify it's valid before modification
    doc.validate()  # Should not raise

    # Add an operation
    manager = PathManager(doc)
    manager.add_operation(path, method, operation)

    # Document should still be valid after adding operation
    doc.validate()  # Should not raise

    # Verify the operation was added
    assert path in doc.paths
    assert method in doc.paths[path]
    assert doc.paths[path][method] == operation


@given(
    doc_dict=openapi_document_strategy(),
    path=path_strategy,
    method=http_method_strategy,
)
def test_document_validity_after_removing_operation(doc_dict: dict, path: str, method: str) -> None:
    """
    Feature: laag-python-port, Property 11: Document Validity After Operation Modification

    **Validates: Requirements 12.6**

    For any valid OpenAPI document, removing an operation should maintain
    document validity (all required fields present).
    """
    # Create a valid document with an operation
    doc_dict_copy = doc_dict.copy()
    if path not in doc_dict_copy["paths"]:
        doc_dict_copy["paths"][path] = {}
    doc_dict_copy["paths"][path][method] = {
        "summary": "Test operation",
        "responses": {"200": {"description": "Success"}},
    }

    doc = OpenAPIDocument(doc_dict_copy)

    # Verify it's valid before modification
    doc.validate()  # Should not raise

    # Remove the operation
    manager = PathManager(doc)
    result = manager.remove_operation(path, method)

    # Document should still be valid after removing operation
    doc.validate()  # Should not raise

    # Verify the operation was removed
    assert result is True
    assert method not in doc.paths.get(path, {})


@given(
    doc_dict=openapi_document_strategy(),
    path=path_strategy,
)
def test_document_validity_after_adding_path(doc_dict: dict, path: str) -> None:
    """
    Feature: laag-python-port, Property 11: Document Validity After Operation Modification

    **Validates: Requirements 12.6**

    For any valid OpenAPI document, adding a path should maintain
    document validity (all required fields present).
    """
    # Create a valid document
    doc = OpenAPIDocument(doc_dict)

    # Verify it's valid before modification
    doc.validate()  # Should not raise

    # Add a path
    manager = PathManager(doc)
    manager.add_path(path)

    # Document should still be valid after adding path
    doc.validate()  # Should not raise

    # Verify the path was added
    assert path in doc.paths


@given(
    doc_dict=openapi_document_strategy(),
    path=path_strategy,
)
def test_document_validity_after_removing_path(doc_dict: dict, path: str) -> None:
    """
    Feature: laag-python-port, Property 11: Document Validity After Operation Modification

    **Validates: Requirements 12.6**

    For any valid OpenAPI document, removing a path should maintain
    document validity (all required fields present).
    """
    # Create a valid document with a path
    doc_dict_copy = doc_dict.copy()
    doc_dict_copy["paths"][path] = {}

    doc = OpenAPIDocument(doc_dict_copy)

    # Verify it's valid before modification
    doc.validate()  # Should not raise

    # Remove the path
    manager = PathManager(doc)
    result = manager.remove_path(path)

    # Document should still be valid after removing path
    doc.validate()  # Should not raise

    # Verify the path was removed
    assert result is True
    assert path not in doc.paths


@given(
    doc_dict=openapi_document_strategy(),
    operations=st.lists(
        st.tuples(path_strategy, http_method_strategy, operation_strategy),
        min_size=1,
        max_size=10,
    ),
)
def test_document_validity_after_multiple_operations(doc_dict: dict, operations: list) -> None:
    """
    Feature: laag-python-port, Property 11: Document Validity After Operation Modification

    **Validates: Requirements 12.6**

    For any valid OpenAPI document, adding multiple operations should
    maintain document validity (all required fields present).
    """
    # Create a valid document
    doc = OpenAPIDocument(doc_dict)

    # Verify it's valid before modification
    doc.validate()  # Should not raise

    # Add multiple operations
    manager = PathManager(doc)
    for path, method, operation in operations:
        manager.add_operation(path, method, operation)

    # Document should still be valid after adding all operations
    doc.validate()  # Should not raise

    # Build a map of what the final state should be
    # (last operation wins for each path+method combination)
    expected_operations = {}
    for path, method, operation in operations:
        if path not in expected_operations:
            expected_operations[path] = {}
        expected_operations[path][method] = operation

    # Verify the expected operations are present
    for path, methods in expected_operations.items():
        assert path in doc.paths
        for method, operation in methods.items():
            assert method in doc.paths[path]
            assert doc.paths[path][method] == operation


@given(
    doc_dict=openapi_document_strategy(),
    path=path_strategy,
    methods=st.lists(http_method_strategy, min_size=2, max_size=5, unique=True),
)
def test_document_validity_with_multiple_methods_on_same_path(
    doc_dict: dict, path: str, methods: list
) -> None:
    """
    Feature: laag-python-port, Property 11: Document Validity After Operation Modification

    **Validates: Requirements 12.6**

    For any valid OpenAPI document, adding multiple operations to the same
    path should maintain document validity.
    """
    # Create a valid document
    doc = OpenAPIDocument(doc_dict)

    # Verify it's valid before modification
    doc.validate()  # Should not raise

    # Add multiple operations to the same path
    manager = PathManager(doc)
    for method in methods:
        operation = {
            "summary": f"{method.upper()} operation",
            "responses": {"200": {"description": "Success"}},
        }
        manager.add_operation(path, method, operation)

    # Document should still be valid
    doc.validate()  # Should not raise

    # Verify all operations were added to the same path
    assert path in doc.paths
    for method in methods:
        assert method in doc.paths[path]


@given(doc_dict=openapi_document_strategy())
def test_document_validity_preserved_with_empty_paths(doc_dict: dict) -> None:
    """
    Feature: laag-python-port, Property 11: Document Validity After Operation Modification

    **Validates: Requirements 12.6**

    A document with an empty paths object should remain valid.
    """
    # Create a document with empty paths
    doc_dict_copy = doc_dict.copy()
    doc_dict_copy["paths"] = {}

    doc = OpenAPIDocument(doc_dict_copy)

    # Should be valid
    doc.validate()  # Should not raise

    # Verify paths is empty
    assert doc.paths == {}
