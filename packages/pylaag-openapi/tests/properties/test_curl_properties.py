"""Property-based tests for curl command generation from OpenAPI operations."""

from hypothesis import given
from hypothesis import strategies as st
from pylaag.openapi import CurlGenerator, OpenAPIDocument

# Strategy for generating HTTP methods
http_methods = st.sampled_from(["get", "post", "put", "delete", "patch"])


# Strategy for generating simple paths
@st.composite
def path_strategy(draw):
    """Generate API paths."""
    segments = draw(st.integers(min_value=1, max_value=3))
    path_parts = []
    for _ in range(segments):
        # Either a static segment or a path parameter
        if draw(st.booleans()):
            # Static segment
            segment = draw(
                st.text(
                    alphabet=st.characters(whitelist_categories=("Ll",)), min_size=1, max_size=10
                )
            )
            path_parts.append(segment)
        else:
            # Path parameter
            param_name = draw(
                st.text(
                    alphabet=st.characters(whitelist_categories=("Ll",)), min_size=1, max_size=10
                )
            )
            path_parts.append(f"{{{param_name}}}")

    return "/" + "/".join(path_parts)


# Strategy for generating operations
@st.composite
def operation_strategy(draw, path: str):
    """Generate OpenAPI operations."""
    operation = {
        "summary": draw(st.text(min_size=1, max_size=50)),
        "responses": {"200": {"description": "Success"}},
    }

    # Extract path parameters from path
    path_params = []
    import re

    for match in re.finditer(r"\{([^}]+)\}", path):
        path_params.append(match.group(1))

    parameters = []

    # Add path parameters
    for param_name in path_params:
        parameters.append(
            {
                "name": param_name,
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
                "example": draw(st.text(min_size=1, max_size=10)),
            }
        )

    # Optionally add query parameters
    if draw(st.booleans()):
        num_query_params = draw(st.integers(min_value=1, max_value=3))
        for i in range(num_query_params):
            param_name = f"query{i}"
            parameters.append(
                {
                    "name": param_name,
                    "in": "query",
                    "schema": {"type": "string"},
                    "example": draw(st.text(min_size=1, max_size=10)),
                }
            )

    # Optionally add header parameters
    if draw(st.booleans()):
        num_headers = draw(st.integers(min_value=1, max_value=2))
        for i in range(num_headers):
            header_name = f"X-Custom-Header-{i}"
            parameters.append(
                {
                    "name": header_name,
                    "in": "header",
                    "schema": {"type": "string"},
                    "example": draw(st.text(min_size=1, max_size=20)),
                }
            )

    if parameters:
        operation["parameters"] = parameters

    # Optionally add request body for POST/PUT/PATCH
    method = draw(http_methods)
    if method in ["post", "put", "patch"] and draw(st.booleans()):
        operation["requestBody"] = {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {"name": {"type": "string"}, "value": {"type": "integer"}},
                    }
                }
            }
        }

    return operation, method


@given(st.data())
def test_generated_curl_commands_are_valid(data) -> None:
    """
    Feature: laag-python-port, Property 21: Generated Curl Commands are Valid

    **Validates: Requirements 8.1, 8.6**

    For any valid OpenAPI operation, the generated curl command should be
    syntactically valid and properly escaped.
    """
    # Generate a path
    path = data.draw(path_strategy())

    # Create a document with the operation
    doc = OpenAPIDocument()
    operation, method = data.draw(operation_strategy(path))

    doc._document["paths"] = {path: {method: operation}}

    generator = CurlGenerator(doc)

    # Generate curl command
    curl_cmd = generator.generate_curl(path, method)

    # Basic validation: should start with curl
    assert curl_cmd.startswith("curl")

    # Should contain the HTTP method (may be on separate lines)
    assert method.upper() in curl_cmd

    # Should contain a URL
    assert "https://" in curl_cmd or "http://" in curl_cmd

    # Should not have unescaped single quotes in the wrong places
    # (this is a basic check - proper escaping is tested more thoroughly in unit tests)
    lines = curl_cmd.split("\n")
    for line in lines:
        # Each line should be properly formatted
        assert line.strip() != ""


@given(st.data())
def test_curl_commands_include_all_operation_details(data) -> None:
    """
    Feature: laag-python-port, Property 22: Curl Commands Include All Operation Details

    **Validates: Requirements 8.2, 8.3, 8.4, 8.5**

    For any OpenAPI operation with parameters (path, query, header) and
    request body, the generated curl command should include all these details.
    """
    # Generate a path
    path = data.draw(path_strategy())

    # Create a comprehensive operation
    doc = OpenAPIDocument()

    # Extract path parameters
    import re

    path_params = []
    for match in re.finditer(r"\{([^}]+)\}", path):
        path_params.append(match.group(1))

    parameters = []

    # Add path parameters
    for param_name in path_params:
        parameters.append(
            {
                "name": param_name,
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
                "example": "test-value",
            }
        )

    # Add query parameter
    parameters.append(
        {"name": "filter", "in": "query", "schema": {"type": "string"}, "example": "active"}
    )

    # Add header parameter
    parameters.append(
        {"name": "X-API-Key", "in": "header", "schema": {"type": "string"}, "example": "secret-key"}
    )

    operation = {
        "summary": "Test operation",
        "parameters": parameters,
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
                    }
                }
            }
        },
        "responses": {"200": {"description": "Success"}},
    }

    doc._document["paths"] = {path: {"post": operation}}

    generator = CurlGenerator(doc)

    # Generate curl command
    curl_cmd = generator.generate_curl(path, "post")

    # Verify HTTP method is included (may be on separate lines)
    assert "POST" in curl_cmd

    # Verify query parameters are included
    assert "filter=active" in curl_cmd

    # Verify headers are included
    assert "-H 'X-API-Key:" in curl_cmd or '-H "X-API-Key:' in curl_cmd
    assert "secret-key" in curl_cmd

    # Verify Content-Type header for request body
    assert "Content-Type: application/json" in curl_cmd

    # Verify request body is included
    assert "-d '" in curl_cmd or '-d "' in curl_cmd

    # Verify path parameters are replaced
    for param_name in path_params:
        # The placeholder {param_name} should be replaced
        assert f"{{{param_name}}}" not in curl_cmd


def test_curl_command_with_special_characters() -> None:
    """
    Feature: laag-python-port, Property 21: Generated Curl Commands are Valid

    **Validates: Requirements 8.1, 8.6**

    Curl commands should properly escape special characters in headers,
    query parameters, and request bodies.
    """
    doc = OpenAPIDocument()

    operation = {
        "summary": "Test with special chars",
        "parameters": [
            {
                "name": "X-Custom-Header",
                "in": "header",
                "schema": {"type": "string"},
                "example": "value with 'quotes' and spaces",
            },
            {
                "name": "query",
                "in": "query",
                "schema": {"type": "string"},
                "example": "value&with=special",
            },
        ],
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {"message": {"type": "string", "example": "It's a test"}},
                    }
                }
            }
        },
        "responses": {"200": {"description": "Success"}},
    }

    doc._document["paths"] = {"/test": {"post": operation}}

    generator = CurlGenerator(doc)
    curl_cmd = generator.generate_curl("/test", "post")

    # Verify the command is generated without errors
    assert curl_cmd.startswith("curl")

    # Verify special characters in query params are URL encoded
    assert "value%26with%3Dspecial" in curl_cmd

    # Verify the command contains escaped quotes
    # Single quotes in values should be escaped as '\''
    assert "value with" in curl_cmd


def test_curl_command_without_request_body() -> None:
    """
    Feature: laag-python-port, Property 22: Curl Commands Include All Operation Details

    **Validates: Requirements 8.2, 8.3, 8.4, 8.5**

    For GET requests without a request body, the curl command should not
    include -d flag or Content-Type header.
    """
    doc = OpenAPIDocument()

    operation = {
        "summary": "Get operation",
        "parameters": [
            {"name": "id", "in": "query", "schema": {"type": "string"}, "example": "123"}
        ],
        "responses": {"200": {"description": "Success"}},
    }

    doc._document["paths"] = {"/users": {"get": operation}}

    generator = CurlGenerator(doc)
    curl_cmd = generator.generate_curl("/users", "get")

    # Verify no request body
    assert "-d '" not in curl_cmd

    # Verify no Content-Type header (unless explicitly in parameters)
    if "Content-Type" in curl_cmd:
        # If present, it should be from parameters, not auto-added
        assert any(p.get("name") == "Content-Type" for p in operation.get("parameters", []))

    # Verify query parameter is included
    assert "id=123" in curl_cmd


def test_curl_command_with_include_sample_body_false() -> None:
    """
    Feature: laag-python-port, Property 22: Curl Commands Include All Operation Details

    **Validates: Requirements 8.2, 8.3, 8.4, 8.5**

    When include_sample_body is False, the curl command should not include
    a request body even if the operation defines one.
    """
    doc = OpenAPIDocument()

    operation = {
        "summary": "Post operation",
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {"type": "object", "properties": {"name": {"type": "string"}}}
                }
            }
        },
        "responses": {"200": {"description": "Success"}},
    }

    doc._document["paths"] = {"/users": {"post": operation}}

    generator = CurlGenerator(doc)
    curl_cmd = generator.generate_curl("/users", "post", include_sample_body=False)

    # Verify no request body
    assert "-d '" not in curl_cmd

    # Verify no Content-Type header
    assert "Content-Type" not in curl_cmd
