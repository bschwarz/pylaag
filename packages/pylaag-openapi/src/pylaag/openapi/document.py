"""OpenAPI document class for managing OpenAPI specifications."""

import json
from typing import Any

import yaml
from pylaag.core import LaagBase, ParseError, ValidationError


class OpenAPIDocument(LaagBase[dict[str, Any]]):
    """Represents an OpenAPI document.

    This class provides methods for creating, parsing, serializing, and
    validating OpenAPI 3.0+ documents.
    """

    def __init__(self, document: dict[str, Any] | None = None):
        """Initialize an OpenAPI document.

        Args:
            document: The OpenAPI document dictionary. If None, creates a
                     minimal valid document structure.
        """
        if document is None:
            document = {
                "openapi": "3.0.0",
                "info": {"title": "API", "version": "1.0.0"},
                "paths": {},
            }
        super().__init__(document)

    @classmethod
    def from_json(cls, json_str: str) -> "OpenAPIDocument":
        """Parse an OpenAPI document from JSON string.

        Args:
            json_str: The JSON string to parse

        Returns:
            An OpenAPIDocument instance

        Raises:
            ParseError: If the JSON is invalid or not an object
        """
        try:
            document = json.loads(json_str)
            if not isinstance(document, dict):
                raise ParseError(
                    "OpenAPI document must be a JSON object, not a list or primitive",
                    {"input": json_str, "type": type(document).__name__},
                )
            return cls(document)
        except json.JSONDecodeError as e:
            raise ParseError(
                f"Failed to parse JSON: {e}", {"input": json_str, "error": str(e)}
            ) from e

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "OpenAPIDocument":
        """Parse an OpenAPI document from YAML string.

        Args:
            yaml_str: The YAML string to parse

        Returns:
            An OpenAPIDocument instance

        Raises:
            ParseError: If the YAML is invalid or not an object
        """
        try:
            document = yaml.safe_load(yaml_str)
            if not isinstance(document, dict):
                raise ParseError(
                    "OpenAPI document must be a YAML object, not a list or primitive",
                    {"input": yaml_str, "type": type(document).__name__},
                )
            return cls(document)
        except yaml.YAMLError as e:
            raise ParseError(
                f"Failed to parse YAML: {e}", {"input": yaml_str, "error": str(e)}
            ) from e

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string.

        Args:
            indent: Number of spaces for indentation (default: 2)

        Returns:
            The document as a JSON string
        """
        return json.dumps(self._document, indent=indent)

    def to_yaml(self) -> str:
        """Serialize to YAML string.

        Returns:
            The document as a YAML string
        """
        return yaml.dump(self._document, default_flow_style=False, sort_keys=False)

    def validate(self) -> None:
        """Validate the OpenAPI document structure.

        Raises:
            ValidationError: If the document is missing required fields
        """
        if "openapi" not in self._document:
            raise ValidationError("Missing required field: openapi")

        if "info" not in self._document:
            raise ValidationError("Missing required field: info")

        info = self._document["info"]
        if "title" not in info:
            raise ValidationError("Missing required field: info.title")

        if "version" not in info:
            raise ValidationError("Missing required field: info.version")

        if "paths" not in self._document:
            raise ValidationError("Missing required field: paths")

    @property
    def openapi_version(self) -> str:
        """Get the OpenAPI version.

        Returns:
            The OpenAPI version string (e.g., "3.0.0")
        """
        version = self._document.get("openapi", "")
        return str(version) if version else ""

    @property
    def info(self) -> dict[str, Any]:
        """Get the info object.

        Returns:
            The info object containing title, version, and other metadata
        """
        info = self._document.get("info", {})
        return dict(info) if isinstance(info, dict) else {}

    @property
    def paths(self) -> dict[str, Any]:
        """Get the paths object.

        Returns:
            The paths object containing all API endpoints
        """
        paths = self._document.get("paths", {})
        return dict(paths) if isinstance(paths, dict) else {}
