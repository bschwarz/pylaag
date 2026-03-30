"""RAML document handling."""

from typing import Any

import yaml
from pylaag.core import LaagBase, ParseError, ValidationError


class RAMLDocument(LaagBase):
    """Represents a RAML document."""

    def __init__(self, document: dict[str, Any] | None = None):
        """Initialize a RAML document.

        Args:
            document: Optional dictionary representing the RAML document.
                     If None, creates a default RAML 1.0 document.
        """
        if document is None:
            document = {
                "#%RAML 1.0": None,
                "title": "API",
                "version": "v1",
                "baseUri": "https://api.example.com",
            }
        super().__init__(document)

    @property
    def title(self) -> str:
        """Get the API title."""
        return str(self._document.get("title", ""))

    @property
    def version(self) -> str:
        """Get the API version."""
        return str(self._document.get("version", ""))

    @property
    def base_uri(self) -> str:
        """Get the base URI."""
        return str(self._document.get("baseUri", ""))

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "RAMLDocument":
        """Parse a RAML document from YAML string.

        Args:
            yaml_str: YAML string containing the RAML document.

        Returns:
            RAMLDocument instance.

        Raises:
            ParseError: If the YAML is invalid.
        """
        try:
            document = yaml.safe_load(yaml_str)
            return cls(document)
        except yaml.YAMLError as e:
            raise ParseError(f"Failed to parse RAML: {e}", {"input": yaml_str}) from e

    def to_yaml(self) -> str:
        """Serialize to YAML string.

        Returns:
            YAML string representation of the document.
        """
        return yaml.dump(self._document, default_flow_style=False, sort_keys=False)

    def validate(self) -> None:
        """Validate the RAML document structure.

        Raises:
            ValidationError: If the document is invalid.
        """
        # Check for RAML version marker
        if "#%RAML 1.0" not in self._document and "#%RAML 0.8" not in self._document:
            raise ValidationError("Missing RAML version marker (#%RAML 1.0 or #%RAML 0.8)")

        if "title" not in self._document:
            raise ValidationError("Missing required field: title")

        if "version" not in self._document:
            raise ValidationError("Missing required field: version")
