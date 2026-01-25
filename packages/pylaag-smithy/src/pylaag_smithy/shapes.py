"""Shape management for Smithy documents."""

from typing import Any, Literal

from pylaag_smithy.document import SmithyDocument

ShapeType = Literal[
    "service",
    "operation",
    "resource",
    "structure",
    "union",
    "list",
    "map",
    "string",
    "integer",
    "long",
    "float",
    "double",
    "boolean",
    "blob",
    "timestamp",
]


class ShapeManager:
    """Manages shapes in a Smithy document."""

    def __init__(self, document: SmithyDocument):
        """Initialize the ShapeManager.

        Args:
            document: The Smithy document to manage shapes for
        """
        self.document = document

    def _ensure_shapes(self) -> None:
        """Ensure shapes section exists in the document."""
        if "shapes" not in self.document._document:
            self.document._document["shapes"] = {}

    def add_shape(
        self,
        shape_id: str,
        shape_type: ShapeType,
        shape_def: dict[str, Any],
    ) -> None:
        """Add a shape to the document.

        Args:
            shape_id: The fully qualified shape ID (e.g., "com.example#User")
            shape_type: The type of shape to add
            shape_def: The shape definition dictionary (without the type field)
        """
        self._ensure_shapes()

        # Create a copy to avoid mutating the input
        shape_def_copy = shape_def.copy()
        shape_def_copy["type"] = shape_type
        self.document._document["shapes"][shape_id] = shape_def_copy

    def remove_shape(self, shape_id: str) -> bool:
        """Remove a shape from the document.

        Args:
            shape_id: The fully qualified shape ID to remove

        Returns:
            True if the shape was removed, False if it didn't exist
        """
        shapes = self.document._document.get("shapes", {})
        if shape_id in shapes:
            del shapes[shape_id]
            return True
        return False

    def get_shape(self, shape_id: str) -> dict[str, Any] | None:
        """Get a shape from the document.

        Args:
            shape_id: The fully qualified shape ID to retrieve

        Returns:
            The shape definition dictionary, or None if not found
        """
        shapes = self.document._document.get("shapes", {})
        if not isinstance(shapes, dict):
            return None
        shape = shapes.get(shape_id)
        if shape is None:
            return None
        return dict(shape) if isinstance(shape, dict) else None

    def resolve_target(self, target: str) -> dict[str, Any] | None:
        """Resolve a shape target reference.

        Args:
            target: The target shape ID to resolve

        Returns:
            The resolved shape definition, or None if not found
        """
        return self.get_shape(target)
