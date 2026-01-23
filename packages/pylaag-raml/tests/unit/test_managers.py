"""Unit tests for RAML resource and type managers."""

from pylaag_raml import RAMLDocument, ResourceManager, TypeManager


class TestResourceManager:
    """Unit tests for ResourceManager."""

    def test_add_resource_with_definition(self):
        """Test adding a resource with a definition."""
        doc = RAMLDocument()
        resource_mgr = ResourceManager(doc)

        resource_def = {"description": "User resource", "displayName": "Users"}
        resource_mgr.add_resource("/users", resource_def)

        retrieved = resource_mgr.get_resource("/users")
        assert retrieved == resource_def

    def test_add_resource_without_definition(self):
        """Test adding a resource without a definition creates empty dict."""
        doc = RAMLDocument()
        resource_mgr = ResourceManager(doc)

        resource_mgr.add_resource("/users")

        retrieved = resource_mgr.get_resource("/users")
        assert retrieved == {}

    def test_add_resource_with_none_definition(self):
        """Test adding a resource with None creates empty dict."""
        doc = RAMLDocument()
        resource_mgr = ResourceManager(doc)

        resource_mgr.add_resource("/users", None)

        retrieved = resource_mgr.get_resource("/users")
        assert retrieved == {}

    def test_remove_existing_resource(self):
        """Test removing an existing resource."""
        doc = RAMLDocument()
        resource_mgr = ResourceManager(doc)

        resource_mgr.add_resource("/users", {"description": "Users"})
        result = resource_mgr.remove_resource("/users")

        assert result is True
        assert resource_mgr.get_resource("/users") is None

    def test_remove_nonexistent_resource(self):
        """Test removing a non-existent resource returns False."""
        doc = RAMLDocument()
        resource_mgr = ResourceManager(doc)

        result = resource_mgr.remove_resource("/nonexistent")
        assert result is False

    def test_get_nonexistent_resource(self):
        """Test getting a non-existent resource returns None."""
        doc = RAMLDocument()
        resource_mgr = ResourceManager(doc)

        resource = resource_mgr.get_resource("/nonexistent")
        assert resource is None

    def test_add_method_to_existing_resource(self):
        """Test adding a method to an existing resource."""
        doc = RAMLDocument()
        resource_mgr = ResourceManager(doc)

        resource_mgr.add_resource("/users", {})
        method_def = {
            "description": "Get all users",
            "responses": {"200": {"description": "Success"}},
        }
        resource_mgr.add_method("/users", "get", method_def)

        resource = resource_mgr.get_resource("/users")
        assert "get" in resource
        assert resource["get"] == method_def

    def test_add_method_creates_resource_if_not_exists(self):
        """Test adding a method creates the resource if it doesn't exist."""
        doc = RAMLDocument()
        resource_mgr = ResourceManager(doc)

        method_def = {
            "description": "Get all users",
            "responses": {"200": {"description": "Success"}},
        }
        resource_mgr.add_method("/users", "get", method_def)

        resource = resource_mgr.get_resource("/users")
        assert resource is not None
        assert "get" in resource
        assert resource["get"] == method_def

    def test_add_multiple_methods_to_resource(self):
        """Test adding multiple methods to a resource."""
        doc = RAMLDocument()
        resource_mgr = ResourceManager(doc)

        get_def = {"description": "Get all users"}
        post_def = {"description": "Create a user"}
        put_def = {"description": "Update a user"}

        resource_mgr.add_method("/users", "get", get_def)
        resource_mgr.add_method("/users", "post", post_def)
        resource_mgr.add_method("/users", "put", put_def)

        resource = resource_mgr.get_resource("/users")
        assert "get" in resource
        assert "post" in resource
        assert "put" in resource
        assert resource["get"] == get_def
        assert resource["post"] == post_def
        assert resource["put"] == put_def

    def test_remove_method_from_resource(self):
        """Test removing a method from a resource."""
        doc = RAMLDocument()
        resource_mgr = ResourceManager(doc)

        resource_mgr.add_method("/users", "get", {"description": "Get users"})
        resource_mgr.add_method("/users", "post", {"description": "Create user"})

        result = resource_mgr.remove_method("/users", "get")

        assert result is True
        resource = resource_mgr.get_resource("/users")
        assert "get" not in resource
        assert "post" in resource

    def test_remove_nonexistent_method(self):
        """Test removing a non-existent method returns False."""
        doc = RAMLDocument()
        resource_mgr = ResourceManager(doc)

        resource_mgr.add_resource("/users", {})
        result = resource_mgr.remove_method("/users", "get")

        assert result is False

    def test_remove_method_from_nonexistent_resource(self):
        """Test removing a method from a non-existent resource returns False."""
        doc = RAMLDocument()
        resource_mgr = ResourceManager(doc)

        result = resource_mgr.remove_method("/nonexistent", "get")
        assert result is False

    def test_all_http_methods(self):
        """Test all standard HTTP methods can be added."""
        doc = RAMLDocument()
        resource_mgr = ResourceManager(doc)

        methods = ["get", "post", "put", "delete", "patch", "options", "head"]

        for method in methods:
            resource_mgr.add_method("/users", method, {"description": f"{method.upper()}"})

        resource = resource_mgr.get_resource("/users")
        for method in methods:
            assert method in resource

    def test_nested_resource_paths(self):
        """Test nested resource paths."""
        doc = RAMLDocument()
        resource_mgr = ResourceManager(doc)

        resource_mgr.add_resource("/users", {"description": "Users"})
        resource_mgr.add_resource("/users/{id}", {"description": "User by ID"})
        resource_mgr.add_resource("/users/{id}/posts", {"description": "User posts"})

        assert resource_mgr.get_resource("/users") is not None
        assert resource_mgr.get_resource("/users/{id}") is not None
        assert resource_mgr.get_resource("/users/{id}/posts") is not None


class TestTypeManager:
    """Unit tests for TypeManager."""

    def test_add_type_creates_types_section(self):
        """Test adding a type creates the types section if it doesn't exist."""
        doc = RAMLDocument()
        assert "types" not in doc.to_dict()

        type_mgr = TypeManager(doc)
        type_mgr.add_type("User", {"type": "object"})

        assert "types" in doc.to_dict()

    def test_add_type_with_definition(self):
        """Test adding a type with a definition."""
        doc = RAMLDocument()
        type_mgr = TypeManager(doc)

        type_def = {
            "type": "object",
            "properties": {"id": {"type": "integer"}, "name": {"type": "string"}},
        }
        type_mgr.add_type("User", type_def)

        retrieved = type_mgr.get_type("User")
        assert retrieved == type_def

    def test_add_multiple_types(self):
        """Test adding multiple types."""
        doc = RAMLDocument()
        type_mgr = TypeManager(doc)

        user_def = {"type": "object", "properties": {"name": {"type": "string"}}}
        post_def = {"type": "object", "properties": {"title": {"type": "string"}}}

        type_mgr.add_type("User", user_def)
        type_mgr.add_type("Post", post_def)

        assert type_mgr.get_type("User") == user_def
        assert type_mgr.get_type("Post") == post_def

    def test_remove_existing_type(self):
        """Test removing an existing type."""
        doc = RAMLDocument()
        type_mgr = TypeManager(doc)

        type_mgr.add_type("User", {"type": "object"})
        result = type_mgr.remove_type("User")

        assert result is True
        assert type_mgr.get_type("User") is None

    def test_remove_nonexistent_type(self):
        """Test removing a non-existent type returns False."""
        doc = RAMLDocument()
        type_mgr = TypeManager(doc)

        result = type_mgr.remove_type("NonExistent")
        assert result is False

    def test_remove_type_from_document_without_types(self):
        """Test removing a type from a document without types section."""
        doc = RAMLDocument()
        type_mgr = TypeManager(doc)

        # Don't add any types
        result = type_mgr.remove_type("User")
        assert result is False

    def test_get_nonexistent_type(self):
        """Test getting a non-existent type returns None."""
        doc = RAMLDocument()
        type_mgr = TypeManager(doc)

        type_def = type_mgr.get_type("NonExistent")
        assert type_def is None

    def test_get_type_from_document_without_types(self):
        """Test getting a type from a document without types section."""
        doc = RAMLDocument()
        type_mgr = TypeManager(doc)

        # Don't add any types
        type_def = type_mgr.get_type("User")
        assert type_def is None

    def test_overwrite_existing_type(self):
        """Test overwriting an existing type."""
        doc = RAMLDocument()
        type_mgr = TypeManager(doc)

        type_def1 = {"type": "string"}
        type_def2 = {"type": "object", "properties": {"name": {"type": "string"}}}

        type_mgr.add_type("User", type_def1)
        assert type_mgr.get_type("User") == type_def1

        type_mgr.add_type("User", type_def2)
        assert type_mgr.get_type("User") == type_def2

    def test_type_with_array(self):
        """Test adding a type with array definition."""
        doc = RAMLDocument()
        type_mgr = TypeManager(doc)

        type_def = {"type": "array", "items": {"type": "string"}}
        type_mgr.add_type("StringArray", type_def)

        retrieved = type_mgr.get_type("StringArray")
        assert retrieved == type_def

    def test_type_with_enum(self):
        """Test adding a type with enum."""
        doc = RAMLDocument()
        type_mgr = TypeManager(doc)

        type_def = {"type": "string", "enum": ["active", "inactive", "pending"]}
        type_mgr.add_type("Status", type_def)

        retrieved = type_mgr.get_type("Status")
        assert retrieved == type_def

    def test_type_with_constraints(self):
        """Test adding a type with constraints."""
        doc = RAMLDocument()
        type_mgr = TypeManager(doc)

        type_def = {"type": "string", "minLength": 1, "maxLength": 100, "pattern": "^[a-zA-Z]+$"}
        type_mgr.add_type("Name", type_def)

        retrieved = type_mgr.get_type("Name")
        assert retrieved == type_def

    def test_nested_type_definition(self):
        """Test adding a type with nested object properties."""
        doc = RAMLDocument()
        type_mgr = TypeManager(doc)

        type_def = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "address": {
                    "type": "object",
                    "properties": {"street": {"type": "string"}, "city": {"type": "string"}},
                },
            },
        }
        type_mgr.add_type("User", type_def)

        retrieved = type_mgr.get_type("User")
        assert retrieved == type_def
