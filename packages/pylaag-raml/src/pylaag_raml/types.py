"""RAML type management."""

from typing import Any

from pylaag_raml.document import RAMLDocument


class TypeManager:
    """Manages types in a RAML document."""

    def __init__(self, document: RAMLDocument):
        """Initialize the TypeManager.

        Args:
            document: The RAML document to manage.
        """
        self.document = document

    def _ensure_types(self) -> None:
        """Ensure types section exists in the document."""
        if "types" not in self.document._document:
            self.document._document["types"] = {}

    def add_type(self, name: str, type_def: dict[str, Any]) -> None:
        """Add a type definition to the document.

        Args:
            name: The type name.
            type_def: The type definition.
        """
        self._ensure_types()
        self.document._document["types"][name] = type_def

    def remove_type(self, name: str) -> bool:
        """Remove a type definition from the document.

        Args:
            name: The type name to remove.

        Returns:
            True if the type was removed, False if it didn't exist.
        """
        types = self.document._document.get("types", {})
        if name in types:
            del types[name]
            return True
        return False

    def get_type(self, name: str) -> dict[str, Any] | None:
        """Get a type definition.

        Args:
            name: The type name to retrieve.

        Returns:
            The type definition, or None if not found.
        """
        return self.document._document.get("types", {}).get(name)
