"""Smithy document class for managing Smithy specifications."""

import json
from typing import Any

from pylaag_core import LaagBase, ParseError, ValidationError


class SmithyDocument(LaagBase[dict[str, Any]]):
    """Represents a Smithy document.

    This class provides methods for creating, parsing, serializing, and
    validating Smithy 2.0 documents in JSON AST format.
    """

    def __init__(self, document: dict[str, Any] | None = None):
        """Initialize a Smithy document.

        Args:
            document: The Smithy document dictionary. If None, creates a
                     minimal valid document structure.
        """
        if document is None:
            document = {
                "smithy": "2.0",
                "metadata": {},
                "shapes": {},
            }
        super().__init__(document)

    @classmethod
    def from_json(cls, json_str: str) -> "SmithyDocument":
        """Parse a Smithy document from JSON (AST format).

        Args:
            json_str: The JSON string to parse

        Returns:
            A SmithyDocument instance

        Raises:
            ParseError: If the JSON is invalid or not an object
        """
        try:
            document = json.loads(json_str)
            if not isinstance(document, dict):
                raise ParseError(
                    "Smithy document must be a JSON object, not a list or primitive",
                    {"input": json_str, "type": type(document).__name__},
                )
            return cls(document)
        except json.JSONDecodeError as e:
            raise ParseError(
                f"Failed to parse Smithy JSON: {e}",
                {"input": json_str, "error": str(e)},
            ) from e

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string.

        Args:
            indent: Number of spaces for indentation (default: 2)

        Returns:
            The document as a JSON string
        """
        return json.dumps(self._document, indent=indent)

    def validate(self) -> None:
        """Validate the Smithy document structure.

        Raises:
            ValidationError: If the document is missing required fields
        """
        if "smithy" not in self._document:
            raise ValidationError("Missing required field: smithy (version)")

        if "shapes" not in self._document:
            raise ValidationError("Missing required field: shapes")

    @property
    def smithy_version(self) -> str:
        """Get the Smithy version.

        Returns:
            The Smithy version string (e.g., "2.0")
        """
        version = self._document.get("smithy", "")
        return str(version) if version else ""

    @property
    def shapes(self) -> dict[str, Any]:
        """Get the shapes object.

        Returns:
            The shapes object containing all shape definitions
        """
        shapes = self._document.get("shapes", {})
        return dict(shapes) if isinstance(shapes, dict) else {}
