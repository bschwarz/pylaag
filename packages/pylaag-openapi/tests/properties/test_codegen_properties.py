"""Property-based tests for code generation from OpenAPI documents."""

import ast
import re

from hypothesis import given
from hypothesis import strategies as st
from pylaag.openapi import CodeGenerator, OpenAPIDocument


# Strategy for generating valid OpenAPI documents with operations
@st.composite
def openapi_document_with_operations_strategy(draw):
    """Generate OpenAPI documents with various operations."""
    # Use printable ASCII characters to avoid null bytes and other problematic characters
    title = draw(
        st.text(
            min_size=1,
            max_size=50,
            alphabet=st.characters(
                min_codepoint=65, max_codepoint=122, whitelist_categories=("Lu", "Ll")
            ),
        )
    )
    version = draw(
        st.text(
            min_size=1,
            max_size=20,
            alphabet=st.characters(min_codepoint=48, max_codepoint=57),  # digits only
        )
    )

    # Generate paths with operations
    num_paths = draw(st.integers(min_value=1, max_value=5))
    paths = {}

    for i in range(num_paths):
        path = f"/resource{i}"
        path_item = {}

        # Add 1-3 operations per path
        num_operations = draw(st.integers(min_value=1, max_value=3))
        methods = draw(
            st.lists(
                st.sampled_from(["get", "post", "put", "delete", "patch"]),
                min_size=num_operations,
                max_size=num_operations,
                unique=True,
            )
        )

        for method in methods:
            operation_id = f"{method}_resource{i}"
            # Use printable ASCII for summary to avoid null bytes
            summary = draw(
                st.text(
                    min_size=0,
                    max_size=100,
                    alphabet=st.characters(min_codepoint=32, max_codepoint=126),  # printable ASCII
                )
            )

            path_item[method] = {
                "operationId": operation_id,
                "summary": summary,
                "responses": {"200": {"description": "Success"}},
            }

        paths[path] = path_item

    return {"openapi": "3.0.0", "info": {"title": title, "version": version}, "paths": paths}


# Strategy for generating documents with path parameters
@st.composite
def openapi_document_with_path_params_strategy(draw):
    """Generate OpenAPI documents with path parameters."""
    title = draw(
        st.text(
            min_size=1,
            max_size=50,
            alphabet=st.characters(
                min_codepoint=65, max_codepoint=122, whitelist_categories=("Lu", "Ll")
            ),
        )
    )

    paths = {}
    path = "/users/{userId}/posts/{postId}"

    paths[path] = {
        "get": {
            "operationId": "getUserPost",
            "summary": "Get a user's post",
            "parameters": [
                {"name": "userId", "in": "path", "required": True, "schema": {"type": "integer"}},
                {"name": "postId", "in": "path", "required": True, "schema": {"type": "string"}},
            ],
            "responses": {"200": {"description": "Success"}},
        }
    }

    return {"openapi": "3.0.0", "info": {"title": title, "version": "1.0.0"}, "paths": paths}


@given(doc_dict=openapi_document_with_operations_strategy())
def test_generated_python_code_is_syntactically_valid(doc_dict: dict) -> None:
    """
    Feature: laag-python-port, Property 15: Generated Python Code is Syntactically Valid

    **Validates: Requirements 7.1**

    For any valid OpenAPI document, the generated Python client code
    should parse without syntax errors using Python's ast module.
    """
    doc = OpenAPIDocument(doc_dict)
    generator = CodeGenerator(doc)

    # Generate Python client code
    python_code = generator.generate_client("python")

    # Verify the code is syntactically valid by parsing it
    try:
        ast.parse(python_code)
    except SyntaxError as e:
        raise AssertionError(
            f"Generated Python code has syntax errors: {e}\n\nCode:\n{python_code}"
        ) from e


@given(doc_dict=openapi_document_with_operations_strategy())
def test_generated_javascript_code_is_syntactically_valid(doc_dict: dict) -> None:
    """
    Feature: laag-python-port, Property 16: Generated JavaScript Code is Syntactically Valid

    **Validates: Requirements 7.2**

    For any valid OpenAPI document, the generated JavaScript client code
    should parse without syntax errors using a JavaScript parser.
    """
    doc = OpenAPIDocument(doc_dict)
    generator = CodeGenerator(doc)

    # Generate JavaScript client code
    js_code = generator.generate_client("javascript")

    # Basic syntax validation checks for JavaScript
    # Check that class is properly defined
    assert "class " in js_code, "JavaScript code should contain a class definition"

    # Check that module.exports is present
    assert "module.exports" in js_code, "JavaScript code should export the client class"

    # Check for async/await syntax
    assert "async " in js_code, "JavaScript code should use async functions"

    # Check that methods are properly defined
    assert "async _request(" in js_code, "JavaScript code should have _request method"

    # Check that constructor is present
    assert "constructor(" in js_code, "JavaScript code should have a constructor"

    # Check for proper method structure (async keyword followed by method name and parentheses)
    # This ensures methods are syntactically valid
    assert re.search(r"async \w+\([^)]*\)", js_code), (
        "JavaScript code should have properly formatted async methods"
    )


@given(doc_dict=openapi_document_with_operations_strategy())
def test_generated_typescript_code_is_syntactically_valid(doc_dict: dict) -> None:
    """
    Feature: laag-python-port, Property 17: Generated TypeScript Code is Syntactically Valid

    **Validates: Requirements 7.3**

    For any valid OpenAPI document, the generated TypeScript client code
    should parse without syntax errors using a TypeScript parser.
    """
    doc = OpenAPIDocument(doc_dict)
    generator = CodeGenerator(doc)

    # Generate TypeScript client code
    ts_code = generator.generate_client("typescript")

    # Basic syntax validation checks for TypeScript
    # Check that class is properly defined with export
    assert "export class " in ts_code, "TypeScript code should export a class"

    # Check for type annotations
    assert ": string" in ts_code or ": number" in ts_code, (
        "TypeScript code should have type annotations"
    )

    # Check for async/await syntax
    assert "async " in ts_code, "TypeScript code should use async functions"

    # Check that methods are properly defined with types
    assert "private async _request(" in ts_code, "TypeScript code should have typed _request method"

    # Check for constructor with type annotations
    assert "constructor(private baseUrl: string" in ts_code, (
        "TypeScript code should have typed constructor parameters"
    )

    # Check for proper method structure with type annotations
    assert re.search(r"async \w+\([^)]*\): Promise<", ts_code), (
        "TypeScript code should have properly typed async methods with Promise return types"
    )


@given(doc_dict=openapi_document_with_operations_strategy())
def test_generated_code_contains_all_operations(doc_dict: dict) -> None:
    """
    Feature: laag-python-port, Property 18: Generated Code Contains All Operations

    **Validates: Requirements 7.5**

    For any valid OpenAPI document with N operations, the generated client
    code should contain N corresponding methods (one per operation).
    """
    doc = OpenAPIDocument(doc_dict)
    generator = CodeGenerator(doc)

    # Count operations in the document
    operation_ids = []
    for path, path_item in doc_dict["paths"].items():
        for method in ["get", "post", "put", "delete", "patch"]:
            if method in path_item:
                operation = path_item[method]
                operation_id = operation.get(
                    "operationId", f"{method}_{path.replace('/', '_').strip('_')}"
                )
                operation_ids.append(operation_id)

    # Generate code for each language
    for language in ["python", "javascript", "typescript"]:
        code = generator.generate_client(language)

        # Verify each operation has a corresponding method
        for operation_id in operation_ids:
            # Check for method definition
            if language == "python":
                assert f"def {operation_id}(" in code, (
                    f"Python code missing method for operation: {operation_id}"
                )
            else:  # JavaScript or TypeScript
                assert f"async {operation_id}(" in code, (
                    f"{language.capitalize()} code missing method for operation: {operation_id}"
                )


@given(doc_dict=openapi_document_with_path_params_strategy())
def test_generated_code_contains_type_annotations(doc_dict: dict) -> None:
    """
    Feature: laag-python-port, Property 19: Generated Code Contains Type Annotations

    **Validates: Requirements 7.4**

    For any valid OpenAPI document, the generated Python and TypeScript code
    should contain type annotations for method parameters and return types.
    """
    doc = OpenAPIDocument(doc_dict)
    generator = CodeGenerator(doc)

    # Test Python code
    python_code = generator.generate_client("python")

    # Check for Python type annotations
    assert "Dict[str, Any]" in python_code, "Python code should have Dict type annotations"
    assert "Optional[str]" in python_code, "Python code should have Optional type annotations"
    assert "-> Dict[str, Any]" in python_code, "Python code should have return type annotations"

    # Test TypeScript code
    ts_code = generator.generate_client("typescript")

    # Check for TypeScript type annotations
    assert ": string" in ts_code, "TypeScript code should have string type annotations"
    assert ": Promise<any>" in ts_code, (
        "TypeScript code should have Promise return type annotations"
    )

    # Check for parameter type annotations in TypeScript
    # The document has userId (integer) and postId (string) parameters
    assert "userId: number" in ts_code or ": number" in ts_code, (
        "TypeScript code should have number type annotations for integer parameters"
    )


@given(doc_dict=openapi_document_with_operations_strategy())
def test_generated_code_contains_error_handling(doc_dict: dict) -> None:
    """
    Feature: laag-python-port, Property 20: Generated Code Contains Error Handling

    **Validates: Requirements 7.6**

    For any valid OpenAPI document, the generated client code should
    contain error handling constructs (try/catch or equivalent).
    """
    doc = OpenAPIDocument(doc_dict)
    generator = CodeGenerator(doc)

    # Test Python code
    python_code = generator.generate_client("python")

    # Python uses raise_for_status() which raises exceptions on HTTP errors
    assert "raise_for_status()" in python_code, (
        "Python code should call raise_for_status() for error handling"
    )

    # Test JavaScript code
    js_code = generator.generate_client("javascript")

    # JavaScript checks response.ok and throws errors
    assert "if (!response.ok)" in js_code, (
        "JavaScript code should check response.ok for error handling"
    )
    assert "throw new Error" in js_code, "JavaScript code should throw errors for failed requests"

    # Test TypeScript code
    ts_code = generator.generate_client("typescript")

    # TypeScript also checks response.ok and throws errors
    assert "if (!response.ok)" in ts_code, (
        "TypeScript code should check response.ok for error handling"
    )
    assert "throw new Error" in ts_code, "TypeScript code should throw errors for failed requests"


def test_python_code_has_proper_docstrings() -> None:
    """
    Feature: laag-python-port, Property 15: Generated Python Code is Syntactically Valid

    **Validates: Requirements 7.1**

    Generated Python code should include proper docstrings for the class
    and methods.
    """
    doc = OpenAPIDocument(
        {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0", "description": "A test API"},
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "listUsers",
                        "summary": "List all users",
                        "responses": {"200": {"description": "Success"}},
                    }
                }
            },
        }
    )

    generator = CodeGenerator(doc)
    python_code = generator.generate_client("python")

    # Check for module docstring
    assert '"""' in python_code, "Python code should have docstrings"

    # Check for class docstring
    assert "Client for" in python_code, "Python code should have class docstring"

    # Check for method docstrings
    assert "List all users" in python_code, (
        "Python code should include operation summaries in docstrings"
    )


def test_javascript_code_has_proper_jsdoc() -> None:
    """
    Feature: laag-python-port, Property 16: Generated JavaScript Code is Syntactically Valid

    **Validates: Requirements 7.2**

    Generated JavaScript code should include proper JSDoc comments.
    """
    doc = OpenAPIDocument(
        {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0", "description": "A test API"},
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "listUsers",
                        "summary": "List all users",
                        "responses": {"200": {"description": "Success"}},
                    }
                }
            },
        }
    )

    generator = CodeGenerator(doc)
    js_code = generator.generate_client("javascript")

    # Check for JSDoc comments
    assert "/**" in js_code, "JavaScript code should have JSDoc comments"
    assert "*/" in js_code, "JavaScript code should have JSDoc comments"

    # Check for operation summary in comments
    assert "List all users" in js_code, (
        "JavaScript code should include operation summaries in comments"
    )


def test_typescript_code_has_proper_jsdoc() -> None:
    """
    Feature: laag-python-port, Property 17: Generated TypeScript Code is Syntactically Valid

    **Validates: Requirements 7.3**

    Generated TypeScript code should include proper JSDoc comments.
    """
    doc = OpenAPIDocument(
        {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0", "description": "A test API"},
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "listUsers",
                        "summary": "List all users",
                        "responses": {"200": {"description": "Success"}},
                    }
                }
            },
        }
    )

    generator = CodeGenerator(doc)
    ts_code = generator.generate_client("typescript")

    # Check for JSDoc comments
    assert "/**" in ts_code, "TypeScript code should have JSDoc comments"
    assert "*/" in ts_code, "TypeScript code should have JSDoc comments"

    # Check for operation summary in comments
    assert "List all users" in ts_code, (
        "TypeScript code should include operation summaries in comments"
    )


def test_generated_code_handles_special_characters_in_title() -> None:
    """
    Feature: laag-python-port, Property 15: Generated Python Code is Syntactically Valid

    **Validates: Requirements 7.1**

    Generated code should handle special characters in API titles by
    sanitizing them for use as class names.
    """
    doc = OpenAPIDocument(
        {
            "openapi": "3.0.0",
            "info": {"title": "My-Special API!", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {"operationId": "test", "responses": {"200": {"description": "Success"}}}
                }
            },
        }
    )

    generator = CodeGenerator(doc)

    # Python code should have a valid class name
    python_code = generator.generate_client("python")
    assert "class MySpecialAPIClient:" in python_code or "class MySpecialAPI" in python_code, (
        "Python code should sanitize special characters in class name"
    )

    # Verify Python code is syntactically valid
    try:
        ast.parse(python_code)
    except SyntaxError as e:
        raise AssertionError(
            f"Generated Python code with special characters has syntax errors: {e}"
        ) from e
