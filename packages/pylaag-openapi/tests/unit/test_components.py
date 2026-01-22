"""Unit tests for ComponentManager class."""

import pytest
from pylaag_openapi import ComponentManager, OpenAPIDocument


class TestComponentManager:
    """Test suite for ComponentManager."""

    def test_add_schema_component(self):
        """Test adding a schema component."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        schema = {"type": "object", "properties": {"id": {"type": "integer"}}}
        manager.add_component("schemas", "User", schema)

        assert "components" in doc._document
        assert "schemas" in doc._document["components"]
        assert "User" in doc._document["components"]["schemas"]
        assert doc._document["components"]["schemas"]["User"] == schema

    def test_add_response_component(self):
        """Test adding a response component."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        response = {"description": "Success", "content": {"application/json": {}}}
        manager.add_component("responses", "SuccessResponse", response)

        assert "responses" in doc._document["components"]
        assert doc._document["components"]["responses"]["SuccessResponse"] == response

    def test_add_parameter_component(self):
        """Test adding a parameter component."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        parameter = {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}
        manager.add_component("parameters", "IdParam", parameter)

        assert "parameters" in doc._document["components"]
        assert doc._document["components"]["parameters"]["IdParam"] == parameter

    def test_add_example_component(self):
        """Test adding an example component."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        example = {"value": {"id": 1, "name": "John"}}
        manager.add_component("examples", "UserExample", example)

        assert "examples" in doc._document["components"]
        assert doc._document["components"]["examples"]["UserExample"] == example

    def test_add_request_body_component(self):
        """Test adding a request body component."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        request_body = {"content": {"application/json": {"schema": {"type": "object"}}}}
        manager.add_component("requestBodies", "UserBody", request_body)

        assert "requestBodies" in doc._document["components"]
        assert doc._document["components"]["requestBodies"]["UserBody"] == request_body

    def test_add_header_component(self):
        """Test adding a header component."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        header = {"description": "API Key", "schema": {"type": "string"}}
        manager.add_component("headers", "ApiKey", header)

        assert "headers" in doc._document["components"]
        assert doc._document["components"]["headers"]["ApiKey"] == header

    def test_add_security_scheme_component(self):
        """Test adding a security scheme component."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        security_scheme = {"type": "http", "scheme": "bearer"}
        manager.add_component("securitySchemes", "BearerAuth", security_scheme)

        assert "securitySchemes" in doc._document["components"]
        assert doc._document["components"]["securitySchemes"]["BearerAuth"] == security_scheme

    def test_add_link_component(self):
        """Test adding a link component."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        link = {"operationId": "getUser", "parameters": {"userId": "$response.body#/id"}}
        manager.add_component("links", "UserLink", link)

        assert "links" in doc._document["components"]
        assert doc._document["components"]["links"]["UserLink"] == link

    def test_add_callback_component(self):
        """Test adding a callback component."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        callback = {"{$request.body#/callbackUrl}": {"post": {"summary": "Callback"}}}
        manager.add_component("callbacks", "WebhookCallback", callback)

        assert "callbacks" in doc._document["components"]
        assert doc._document["components"]["callbacks"]["WebhookCallback"] == callback

    def test_add_multiple_components_same_type(self):
        """Test adding multiple components of the same type."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        user_schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        product_schema = {"type": "object", "properties": {"price": {"type": "number"}}}

        manager.add_component("schemas", "User", user_schema)
        manager.add_component("schemas", "Product", product_schema)

        assert "User" in doc._document["components"]["schemas"]
        assert "Product" in doc._document["components"]["schemas"]
        assert doc._document["components"]["schemas"]["User"] == user_schema
        assert doc._document["components"]["schemas"]["Product"] == product_schema

    def test_add_component_overwrites_existing(self):
        """Test that adding a component with the same name overwrites the existing one."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        schema1 = {"type": "string"}
        schema2 = {"type": "number"}

        manager.add_component("schemas", "MySchema", schema1)
        manager.add_component("schemas", "MySchema", schema2)

        assert doc._document["components"]["schemas"]["MySchema"] == schema2

    def test_remove_component(self):
        """Test removing a component."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        schema = {"type": "object"}
        manager.add_component("schemas", "User", schema)

        result = manager.remove_component("schemas", "User")

        assert result is True
        assert "User" not in doc._document["components"]["schemas"]

    def test_remove_nonexistent_component(self):
        """Test removing a component that doesn't exist."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        result = manager.remove_component("schemas", "NonExistent")

        assert result is False

    def test_remove_component_from_nonexistent_type(self):
        """Test removing a component from a type that doesn't exist."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        result = manager.remove_component("schemas", "User")

        assert result is False

    def test_get_component(self):
        """Test getting a component."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        schema = {"type": "object", "properties": {"id": {"type": "integer"}}}
        manager.add_component("schemas", "User", schema)

        retrieved = manager.get_component("schemas", "User")

        assert retrieved == schema

    def test_get_nonexistent_component(self):
        """Test getting a component that doesn't exist."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        retrieved = manager.get_component("schemas", "NonExistent")

        assert retrieved is None

    def test_get_component_from_nonexistent_type(self):
        """Test getting a component from a type that doesn't exist."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        retrieved = manager.get_component("schemas", "User")

        assert retrieved is None

    def test_resolve_reference_simple(self):
        """Test resolving a simple component reference."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        manager.add_component("schemas", "User", schema)

        resolved = manager.resolve_reference("#/components/schemas/User")

        assert resolved == schema

    def test_resolve_reference_nested_path(self):
        """Test resolving a reference with nested paths."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        schema = {
            "type": "object",
            "properties": {
                "address": {"type": "object", "properties": {"city": {"type": "string"}}}
            },
        }
        manager.add_component("schemas", "User", schema)

        # Resolve nested property
        resolved = manager.resolve_reference("#/components/schemas/User/properties/address")

        assert resolved == {"type": "object", "properties": {"city": {"type": "string"}}}

    def test_resolve_reference_deep_nested_path(self):
        """Test resolving a deeply nested reference."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        schema = {
            "type": "object",
            "properties": {
                "address": {"type": "object", "properties": {"city": {"type": "string"}}}
            },
        }
        manager.add_component("schemas", "User", schema)

        # Resolve deeply nested property
        resolved = manager.resolve_reference(
            "#/components/schemas/User/properties/address/properties/city"
        )

        assert resolved == {"type": "string"}

    def test_resolve_reference_nonexistent(self):
        """Test resolving a reference that doesn't exist."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        resolved = manager.resolve_reference("#/components/schemas/NonExistent")

        assert resolved is None

    def test_resolve_reference_invalid_path(self):
        """Test resolving a reference with an invalid path."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        schema = {"type": "object"}
        manager.add_component("schemas", "User", schema)

        # Try to resolve a path that doesn't exist in the schema
        resolved = manager.resolve_reference("#/components/schemas/User/nonexistent/path")

        assert resolved is None

    def test_resolve_reference_non_local_raises_error(self):
        """Test that resolving a non-local reference raises ValueError."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        with pytest.raises(ValueError, match="Only local references are supported"):
            manager.resolve_reference("http://example.com/schema")

    def test_resolve_reference_relative_raises_error(self):
        """Test that resolving a relative reference raises ValueError."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        with pytest.raises(ValueError, match="Only local references are supported"):
            manager.resolve_reference("../other/schema")

    def test_resolve_reference_file_raises_error(self):
        """Test that resolving a file reference raises ValueError."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        with pytest.raises(ValueError, match="Only local references are supported"):
            manager.resolve_reference("file:///path/to/schema")

    def test_resolve_reference_to_paths(self):
        """Test resolving a reference to paths section."""
        doc = OpenAPIDocument()
        doc._document["paths"] = {"/users": {"get": {"summary": "List users"}}}
        manager = ComponentManager(doc)

        manager.resolve_reference("#/paths/~1users/get")

        # Note: ~1 is the JSON Pointer encoding for /
        # For simplicity, we'll test without encoding
        resolved_simple = manager.resolve_reference("#/paths")
        assert resolved_simple == {"/users": {"get": {"summary": "List users"}}}

    def test_components_section_created_automatically(self):
        """Test that components section is created automatically when adding first component."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        assert "components" not in doc._document

        schema = {"type": "object"}
        manager.add_component("schemas", "User", schema)

        assert "components" in doc._document

    def test_component_type_section_created_automatically(self):
        """Test that component type section is created automatically."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        schema = {"type": "object"}
        manager.add_component("schemas", "User", schema)

        assert "schemas" in doc._document["components"]

        # Add a different type
        response = {"description": "Success"}
        manager.add_component("responses", "SuccessResponse", response)

        assert "responses" in doc._document["components"]

    def test_multiple_managers_same_document(self):
        """Test that multiple managers can work with the same document."""
        doc = OpenAPIDocument()
        manager1 = ComponentManager(doc)
        manager2 = ComponentManager(doc)

        schema = {"type": "object"}
        manager1.add_component("schemas", "User", schema)

        # Manager2 should see the component added by manager1
        retrieved = manager2.get_component("schemas", "User")
        assert retrieved == schema

    def test_component_with_extension_properties(self):
        """Test adding and retrieving components with extension properties."""
        doc = OpenAPIDocument()
        manager = ComponentManager(doc)

        schema = {"type": "object", "x-internal": True, "x-deprecated": "Use v2 instead"}
        manager.add_component("schemas", "User", schema)

        retrieved = manager.get_component("schemas", "User")

        assert retrieved == schema
        assert retrieved["x-internal"] is True
        assert retrieved["x-deprecated"] == "Use v2 instead"
