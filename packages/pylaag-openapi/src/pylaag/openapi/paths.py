"""Path and operation management for OpenAPI documents."""

from typing import Any, Literal

from pylaag.openapi.document import OpenAPIDocument

HttpMethod = Literal["get", "post", "put", "delete", "patch", "options", "head", "trace"]


class PathManager:
    """Manages paths and operations in an OpenAPI document."""

    def __init__(self, document: OpenAPIDocument):
        """Initialize the PathManager.

        Args:
            document: The OpenAPI document to manage
        """
        self.document = document

    def add_path(self, path: str, path_item: dict[str, Any] | None = None) -> None:
        """Add a path to the document.

        Args:
            path: The path string (e.g., "/users")
            path_item: Optional path item object. If None, creates an empty path item.
        """
        if "paths" not in self.document._document:
            self.document._document["paths"] = {}

        self.document._document["paths"][path] = path_item or {}

    def remove_path(self, path: str) -> bool:
        """Remove a path from the document.

        Args:
            path: The path string to remove

        Returns:
            True if the path was removed, False if it didn't exist
        """
        if "paths" in self.document._document and path in self.document._document["paths"]:
            del self.document._document["paths"][path]
            return True
        return False

    def get_path(self, path: str) -> dict[str, Any] | None:
        """Get a path item from the document.

        Args:
            path: The path string to retrieve

        Returns:
            The path item object, or None if not found
        """
        paths = self.document._document.get("paths", {})
        if not isinstance(paths, dict):
            return None
        return paths.get(path)

    def add_operation(
        self,
        path: str,
        method: HttpMethod,
        operation: dict[str, Any],
    ) -> None:
        """Add an operation to a path.

        If the path doesn't exist, it will be created automatically.

        Args:
            path: The path string (e.g., "/users")
            method: The HTTP method (get, post, put, delete, patch, options, head, trace)
            operation: The operation object
        """
        if path not in self.document._document.get("paths", {}):
            self.add_path(path)

        self.document._document["paths"][path][method] = operation

    def remove_operation(self, path: str, method: HttpMethod) -> bool:
        """Remove an operation from a path.

        Args:
            path: The path string
            method: The HTTP method to remove

        Returns:
            True if the operation was removed, False if it didn't exist
        """
        paths = self.document._document.get("paths", {})
        if path in paths and method in paths[path]:
            del paths[path][method]
            return True
        return False

    def get_operation(self, path: str, method: HttpMethod) -> dict[str, Any] | None:
        """Get an operation from a path.

        Args:
            path: The path string
            method: The HTTP method

        Returns:
            The operation object, or None if not found
        """
        paths = self.document._document.get("paths", {})
        if not isinstance(paths, dict):
            return None
        path_item = paths.get(path, {})
        if not isinstance(path_item, dict):
            return None
        return path_item.get(method)
