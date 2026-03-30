"""Trait management for Smithy documents."""

from typing import Any

from pylaag.core import NotFoundError
from pylaag.smithy.document import SmithyDocument
from pylaag.smithy.shapes import ShapeManager


class TraitManager:
    """Manages traits in a Smithy document."""

    def __init__(self, document: SmithyDocument):
        """Initialize the TraitManager.

        Args:
            document: The Smithy document to manage traits for
        """
        self.document = document
        self.shape_manager = ShapeManager(document)

    def add_trait_to_shape(
        self,
        shape_id: str,
        trait_name: str,
        trait_value: Any = None,
    ) -> None:
        """Add a trait to a shape.

        Args:
            shape_id: The fully qualified shape ID
            trait_name: The trait name (e.g., "smithy.api#required")
            trait_value: The trait value (default: empty dict if None)

        Raises:
            NotFoundError: If the shape doesn't exist
        """
        shapes = self.document._document.get("shapes", {})
        if not isinstance(shapes, dict) or shape_id not in shapes:
            raise NotFoundError(
                f"Shape not found: {shape_id}",
                {"shape_id": shape_id},
            )

        shape = shapes[shape_id]
        if not isinstance(shape, dict):
            raise NotFoundError(
                f"Shape not found: {shape_id}",
                {"shape_id": shape_id},
            )

        if "traits" not in shape:
            shape["traits"] = {}

        shape["traits"][trait_name] = trait_value if trait_value is not None else {}

    def remove_trait_from_shape(self, shape_id: str, trait_name: str) -> bool:
        """Remove a trait from a shape.

        Args:
            shape_id: The fully qualified shape ID
            trait_name: The trait name to remove

        Returns:
            True if the trait was removed, False if it didn't exist
        """
        shapes = self.document._document.get("shapes", {})
        if not isinstance(shapes, dict) or shape_id not in shapes:
            return False

        shape = shapes[shape_id]
        if not isinstance(shape, dict):
            return False

        if "traits" in shape and trait_name in shape["traits"]:
            del shape["traits"][trait_name]
            return True
        return False

    def get_trait(self, shape_id: str, trait_name: str) -> Any | None:
        """Get a trait value from a shape.

        Args:
            shape_id: The fully qualified shape ID
            trait_name: The trait name to retrieve

        Returns:
            The trait value, or None if not found
        """
        shapes = self.document._document.get("shapes", {})
        if not isinstance(shapes, dict) or shape_id not in shapes:
            return None

        shape = shapes[shape_id]
        if not isinstance(shape, dict):
            return None

        if "traits" in shape:
            return shape["traits"].get(trait_name)
        return None
