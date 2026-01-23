"""RAML resource management."""

from typing import Any

from pylaag_raml.document import RAMLDocument


class ResourceManager:
    """Manages resources in a RAML document."""

    def __init__(self, document: RAMLDocument):
        """Initialize the ResourceManager.

        Args:
            document: The RAML document to manage.
        """
        self.document = document

    def add_resource(self, path: str, resource: dict[str, Any] | None = None) -> None:
        """Add a resource to the document.

        Args:
            path: The resource path (e.g., '/users').
            resource: Optional resource definition. If None, creates an empty resource.
        """
        if path not in self.document._document:
            self.document._document[path] = resource or {}

    def remove_resource(self, path: str) -> bool:
        """Remove a resource from the document.

        Args:
            path: The resource path to remove.

        Returns:
            True if the resource was removed, False if it didn't exist.
        """
        if path in self.document._document:
            del self.document._document[path]
            return True
        return False

    def get_resource(self, path: str) -> dict[str, Any] | None:
        """Get a resource definition.

        Args:
            path: The resource path to retrieve.

        Returns:
            The resource definition, or None if not found.
        """
        return self.document._document.get(path)

    def add_method(self, path: str, method: str, method_def: dict[str, Any]) -> None:
        """Add a method to a resource.

        Args:
            path: The resource path.
            method: The HTTP method (e.g., 'get', 'post').
            method_def: The method definition.
        """
        if path not in self.document._document:
            self.add_resource(path)

        self.document._document[path][method] = method_def

    def remove_method(self, path: str, method: str) -> bool:
        """Remove a method from a resource.

        Args:
            path: The resource path.
            method: The HTTP method to remove.

        Returns:
            True if the method was removed, False if it didn't exist.
        """
        if path in self.document._document and method in self.document._document[path]:
            del self.document._document[path][method]
            return True
        return False
