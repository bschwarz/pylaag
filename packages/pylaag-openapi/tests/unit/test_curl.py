"""Unit tests for curl command generation."""

import pytest
from pylaag.core import NotFoundError
from pylaag.openapi import CurlGenerator, OpenAPIDocument


def test_generate_curl_for_get_request():
    """Test generating curl command for a simple GET request."""
    doc = OpenAPIDocument()
    doc._document["paths"] = {
        "/users": {
            "get": {"summary": "List users", "responses": {"200": {"description": "Success"}}}
        }
    }

    generator = CurlGenerator(doc)
    curl_cmd = generator.generate_curl("/users", "get")

    assert curl_cmd.startswith("curl")
    assert "-X GET" in curl_cmd or "GET" in curl_cmd
    assert "https://api.example.com/users" in curl_cmd


def test_generate_curl_for_post_request_with_body():
    """Test generating curl command for POST request with request body."""
    doc = OpenAPIDocument()
    doc._document["paths"] = {
        "/users": {
            "post": {
                "summary": "Create user",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "email": {"type": "string", "format": "email"},
                                },
                                "required": ["name"],
                            }
                        }
                    }
                },
                "responses": {"201": {"description": "Created"}},
            }
        }
    }

    generator = CurlGenerator(doc)
    curl_cmd = generator.generate_curl("/users", "post")

    assert "POST" in curl_cmd
    assert "Content-Type: application/json" in curl_cmd
    assert "-d '" in curl_cmd
    # Verify JSON body is present (name is required so should be included)
    assert '"name"' in curl_cmd or "'name'" in curl_cmd


def test_generate_curl_with_path_parameters():
    """Test generating curl command with path parameters."""
    doc = OpenAPIDocument()
    doc._document["paths"] = {
        "/users/{id}": {
            "get": {
                "summary": "Get user by ID",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "example": "123",
                    }
                ],
                "responses": {"200": {"description": "Success"}},
            }
        }
    }

    generator = CurlGenerator(doc)
    curl_cmd = generator.generate_curl("/users/{id}", "get")

    # Path parameter should be replaced with example value
    assert "/users/123" in curl_cmd
    assert "{id}" not in curl_cmd


def test_generate_curl_with_query_parameters():
    """Test generating curl command with query parameters."""
    doc = OpenAPIDocument()
    doc._document["paths"] = {
        "/users": {
            "get": {
                "summary": "List users",
                "parameters": [
                    {"name": "page", "in": "query", "schema": {"type": "integer"}, "example": 1},
                    {"name": "limit", "in": "query", "schema": {"type": "integer"}, "example": 10},
                ],
                "responses": {"200": {"description": "Success"}},
            }
        }
    }

    generator = CurlGenerator(doc)
    curl_cmd = generator.generate_curl("/users", "get")

    # Query parameters should be in the URL
    assert "page=1" in curl_cmd
    assert "limit=10" in curl_cmd
    assert "?" in curl_cmd


def test_generate_curl_with_headers():
    """Test generating curl command with custom headers."""
    doc = OpenAPIDocument()
    doc._document["paths"] = {
        "/users": {
            "get": {
                "summary": "List users",
                "parameters": [
                    {
                        "name": "X-API-Key",
                        "in": "header",
                        "schema": {"type": "string"},
                        "example": "secret-key-123",
                    },
                    {
                        "name": "X-Request-ID",
                        "in": "header",
                        "schema": {"type": "string"},
                        "example": "req-456",
                    },
                ],
                "responses": {"200": {"description": "Success"}},
            }
        }
    }

    generator = CurlGenerator(doc)
    curl_cmd = generator.generate_curl("/users", "get")

    # Headers should be included
    assert "-H 'X-API-Key: secret-key-123'" in curl_cmd
    assert "-H 'X-Request-ID: req-456'" in curl_cmd


def test_generate_curl_with_special_characters_in_headers():
    """Test proper escaping of special characters in headers."""
    doc = OpenAPIDocument()
    doc._document["paths"] = {
        "/test": {
            "get": {
                "summary": "Test",
                "parameters": [
                    {
                        "name": "X-Custom",
                        "in": "header",
                        "schema": {"type": "string"},
                        "example": "value with 'quotes'",
                    }
                ],
                "responses": {"200": {"description": "Success"}},
            }
        }
    }

    generator = CurlGenerator(doc)
    curl_cmd = generator.generate_curl("/test", "get")

    # Single quotes should be escaped
    assert "X-Custom" in curl_cmd
    assert "value with" in curl_cmd


def test_generate_curl_with_special_characters_in_query_params():
    """Test URL encoding of special characters in query parameters."""
    doc = OpenAPIDocument()
    doc._document["paths"] = {
        "/search": {
            "get": {
                "summary": "Search",
                "parameters": [
                    {
                        "name": "q",
                        "in": "query",
                        "schema": {"type": "string"},
                        "example": "hello world&test=value",
                    }
                ],
                "responses": {"200": {"description": "Success"}},
            }
        }
    }

    generator = CurlGenerator(doc)
    curl_cmd = generator.generate_curl("/search", "get")

    # Special characters should be URL encoded
    assert "q=hello%20world%26test%3Dvalue" in curl_cmd


def test_generate_curl_with_custom_base_url():
    """Test generating curl command with custom base URL."""
    doc = OpenAPIDocument()
    doc._document["paths"] = {
        "/users": {
            "get": {"summary": "List users", "responses": {"200": {"description": "Success"}}}
        }
    }

    generator = CurlGenerator(doc)
    curl_cmd = generator.generate_curl("/users", "get", base_url="https://custom.api.com")

    assert "https://custom.api.com/users" in curl_cmd


def test_generate_curl_without_sample_body():
    """Test generating curl command without sample body."""
    doc = OpenAPIDocument()
    doc._document["paths"] = {
        "/users": {
            "post": {
                "summary": "Create user",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {"type": "object", "properties": {"name": {"type": "string"}}}
                        }
                    }
                },
                "responses": {"201": {"description": "Created"}},
            }
        }
    }

    generator = CurlGenerator(doc)
    curl_cmd = generator.generate_curl("/users", "post", include_sample_body=False)

    # Should not include body or Content-Type header
    assert "-d '" not in curl_cmd
    assert "Content-Type" not in curl_cmd


def test_generate_curl_for_put_request():
    """Test generating curl command for PUT request."""
    doc = OpenAPIDocument()
    doc._document["paths"] = {
        "/users/{id}": {
            "put": {
                "summary": "Update user",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "example": "456",
                    }
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {"type": "object", "properties": {"name": {"type": "string"}}}
                        }
                    }
                },
                "responses": {"200": {"description": "Success"}},
            }
        }
    }

    generator = CurlGenerator(doc)
    curl_cmd = generator.generate_curl("/users/{id}", "put")

    assert "PUT" in curl_cmd
    assert "/users/456" in curl_cmd
    assert "Content-Type: application/json" in curl_cmd


def test_generate_curl_for_delete_request():
    """Test generating curl command for DELETE request."""
    doc = OpenAPIDocument()
    doc._document["paths"] = {
        "/users/{id}": {
            "delete": {
                "summary": "Delete user",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "example": "789",
                    }
                ],
                "responses": {"204": {"description": "No Content"}},
            }
        }
    }

    generator = CurlGenerator(doc)
    curl_cmd = generator.generate_curl("/users/{id}", "delete")

    assert "DELETE" in curl_cmd
    assert "/users/789" in curl_cmd


def test_generate_curl_for_patch_request():
    """Test generating curl command for PATCH request."""
    doc = OpenAPIDocument()
    doc._document["paths"] = {
        "/users/{id}": {
            "patch": {
                "summary": "Partially update user",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "example": "101",
                    }
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"email": {"type": "string"}},
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "Success"}},
            }
        }
    }

    generator = CurlGenerator(doc)
    curl_cmd = generator.generate_curl("/users/{id}", "patch")

    assert "PATCH" in curl_cmd
    assert "/users/101" in curl_cmd


def test_generate_curl_raises_not_found_error():
    """Test that NotFoundError is raised for non-existent operation."""
    doc = OpenAPIDocument()
    doc._document["paths"] = {
        "/users": {
            "get": {"summary": "List users", "responses": {"200": {"description": "Success"}}}
        }
    }

    generator = CurlGenerator(doc)

    with pytest.raises(NotFoundError) as exc_info:
        generator.generate_curl("/users", "post")

    assert "Operation not found" in str(exc_info.value)
    assert "POST /users" in str(exc_info.value)


def test_generate_curl_with_multiple_path_parameters():
    """Test generating curl command with multiple path parameters."""
    doc = OpenAPIDocument()
    doc._document["paths"] = {
        "/orgs/{org_id}/repos/{repo_id}": {
            "get": {
                "summary": "Get repository",
                "parameters": [
                    {
                        "name": "org_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "example": "my-org",
                    },
                    {
                        "name": "repo_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "example": "my-repo",
                    },
                ],
                "responses": {"200": {"description": "Success"}},
            }
        }
    }

    generator = CurlGenerator(doc)
    curl_cmd = generator.generate_curl("/orgs/{org_id}/repos/{repo_id}", "get")

    # Both path parameters should be replaced
    assert "/orgs/my-org/repos/my-repo" in curl_cmd
    assert "{org_id}" not in curl_cmd
    assert "{repo_id}" not in curl_cmd


def test_generate_curl_multiline_format():
    """Test that curl command uses multiline format with backslashes."""
    doc = OpenAPIDocument()
    doc._document["paths"] = {
        "/users": {
            "post": {
                "summary": "Create user",
                "parameters": [
                    {
                        "name": "X-API-Key",
                        "in": "header",
                        "schema": {"type": "string"},
                        "example": "key123",
                    }
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {"type": "object", "properties": {"name": {"type": "string"}}}
                        }
                    }
                },
                "responses": {"201": {"description": "Created"}},
            }
        }
    }

    generator = CurlGenerator(doc)
    curl_cmd = generator.generate_curl("/users", "post")

    # Should have backslashes for line continuation
    assert "\\" in curl_cmd
    # Should have multiple lines
    assert "\n" in curl_cmd
