"""Unit tests for PathManager class."""

from pylaag.openapi import OpenAPIDocument, PathManager


class TestPathManager:
    """Test suite for PathManager."""

    def test_add_path(self):
        """Test adding a path to the document."""
        doc = OpenAPIDocument()
        manager = PathManager(doc)

        manager.add_path("/users")

        assert "/users" in doc.paths
        assert doc.paths["/users"] == {}

    def test_add_path_with_path_item(self):
        """Test adding a path with a path item object."""
        doc = OpenAPIDocument()
        manager = PathManager(doc)

        path_item = {"summary": "User operations"}
        manager.add_path("/users", path_item)

        assert "/users" in doc.paths
        assert doc.paths["/users"] == path_item

    def test_remove_path(self):
        """Test removing a path from the document."""
        doc = OpenAPIDocument()
        manager = PathManager(doc)

        manager.add_path("/users")
        result = manager.remove_path("/users")

        assert result is True
        assert "/users" not in doc.paths

    def test_remove_nonexistent_path(self):
        """Test removing a path that doesn't exist."""
        doc = OpenAPIDocument()
        manager = PathManager(doc)

        result = manager.remove_path("/nonexistent")

        assert result is False

    def test_get_path(self):
        """Test getting a path from the document."""
        doc = OpenAPIDocument()
        manager = PathManager(doc)

        path_item = {"summary": "User operations"}
        manager.add_path("/users", path_item)

        retrieved = manager.get_path("/users")

        assert retrieved == path_item

    def test_get_nonexistent_path(self):
        """Test getting a path that doesn't exist."""
        doc = OpenAPIDocument()
        manager = PathManager(doc)

        retrieved = manager.get_path("/nonexistent")

        assert retrieved is None

    def test_add_operation_get(self):
        """Test adding a GET operation."""
        doc = OpenAPIDocument()
        manager = PathManager(doc)

        operation = {"summary": "List users", "responses": {"200": {"description": "Success"}}}
        manager.add_operation("/users", "get", operation)

        assert "/users" in doc.paths
        assert "get" in doc.paths["/users"]
        assert doc.paths["/users"]["get"] == operation

    def test_add_operation_post(self):
        """Test adding a POST operation."""
        doc = OpenAPIDocument()
        manager = PathManager(doc)

        operation = {"summary": "Create user", "responses": {"201": {"description": "Created"}}}
        manager.add_operation("/users", "post", operation)

        assert "post" in doc.paths["/users"]
        assert doc.paths["/users"]["post"] == operation

    def test_add_operation_put(self):
        """Test adding a PUT operation."""
        doc = OpenAPIDocument()
        manager = PathManager(doc)

        operation = {"summary": "Update user", "responses": {"200": {"description": "Updated"}}}
        manager.add_operation("/users/{id}", "put", operation)

        assert "put" in doc.paths["/users/{id}"]

    def test_add_operation_delete(self):
        """Test adding a DELETE operation."""
        doc = OpenAPIDocument()
        manager = PathManager(doc)

        operation = {"summary": "Delete user", "responses": {"204": {"description": "Deleted"}}}
        manager.add_operation("/users/{id}", "delete", operation)

        assert "delete" in doc.paths["/users/{id}"]

    def test_add_operation_patch(self):
        """Test adding a PATCH operation."""
        doc = OpenAPIDocument()
        manager = PathManager(doc)

        operation = {"summary": "Patch user", "responses": {"200": {"description": "Patched"}}}
        manager.add_operation("/users/{id}", "patch", operation)

        assert "patch" in doc.paths["/users/{id}"]

    def test_add_operation_options(self):
        """Test adding an OPTIONS operation."""
        doc = OpenAPIDocument()
        manager = PathManager(doc)

        operation = {"summary": "Options", "responses": {"200": {"description": "OK"}}}
        manager.add_operation("/users", "options", operation)

        assert "options" in doc.paths["/users"]

    def test_add_operation_head(self):
        """Test adding a HEAD operation."""
        doc = OpenAPIDocument()
        manager = PathManager(doc)

        operation = {"summary": "Head", "responses": {"200": {"description": "OK"}}}
        manager.add_operation("/users", "head", operation)

        assert "head" in doc.paths["/users"]

    def test_add_operation_trace(self):
        """Test adding a TRACE operation."""
        doc = OpenAPIDocument()
        manager = PathManager(doc)

        operation = {"summary": "Trace", "responses": {"200": {"description": "OK"}}}
        manager.add_operation("/users", "trace", operation)

        assert "trace" in doc.paths["/users"]

    def test_add_operation_creates_path_if_missing(self):
        """Test that adding an operation creates the path if it doesn't exist."""
        doc = OpenAPIDocument()
        manager = PathManager(doc)

        operation = {"summary": "List users"}
        manager.add_operation("/users", "get", operation)

        assert "/users" in doc.paths
        assert "get" in doc.paths["/users"]

    def test_remove_operation(self):
        """Test removing an operation from a path."""
        doc = OpenAPIDocument()
        manager = PathManager(doc)

        operation = {"summary": "List users"}
        manager.add_operation("/users", "get", operation)

        result = manager.remove_operation("/users", "get")

        assert result is True
        assert "get" not in doc.paths["/users"]

    def test_remove_nonexistent_operation(self):
        """Test removing an operation that doesn't exist."""
        doc = OpenAPIDocument()
        manager = PathManager(doc)

        manager.add_path("/users")
        result = manager.remove_operation("/users", "get")

        assert result is False

    def test_remove_operation_from_nonexistent_path(self):
        """Test removing an operation from a path that doesn't exist."""
        doc = OpenAPIDocument()
        manager = PathManager(doc)

        result = manager.remove_operation("/nonexistent", "get")

        assert result is False

    def test_get_operation(self):
        """Test getting an operation from a path."""
        doc = OpenAPIDocument()
        manager = PathManager(doc)

        operation = {"summary": "List users"}
        manager.add_operation("/users", "get", operation)

        retrieved = manager.get_operation("/users", "get")

        assert retrieved == operation

    def test_get_nonexistent_operation(self):
        """Test getting an operation that doesn't exist."""
        doc = OpenAPIDocument()
        manager = PathManager(doc)

        manager.add_path("/users")
        retrieved = manager.get_operation("/users", "get")

        assert retrieved is None

    def test_get_operation_from_nonexistent_path(self):
        """Test getting an operation from a path that doesn't exist."""
        doc = OpenAPIDocument()
        manager = PathManager(doc)

        retrieved = manager.get_operation("/nonexistent", "get")

        assert retrieved is None

    def test_multiple_operations_on_same_path(self):
        """Test adding multiple operations to the same path."""
        doc = OpenAPIDocument()
        manager = PathManager(doc)

        get_op = {"summary": "List users"}
        post_op = {"summary": "Create user"}

        manager.add_operation("/users", "get", get_op)
        manager.add_operation("/users", "post", post_op)

        assert "get" in doc.paths["/users"]
        assert "post" in doc.paths["/users"]
        assert doc.paths["/users"]["get"] == get_op
        assert doc.paths["/users"]["post"] == post_op
