"""Base class for all API document handlers."""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class LaagBase(ABC, Generic[T]):
    """Base class for all API document handlers.

    This class provides common functionality for managing API documents,
    including extension property handling and document serialization.
    """

    def __init__(self, document: dict[str, Any] | None = None):
        """Initialize the base document handler.

        Args:
            document: The document dictionary to manage. If None, an empty dict is used.
        """
        self._document: dict[str, Any] = document or {}
        self._extensions: dict[str, Any] = {}
        self._extract_extensions()

    @abstractmethod
    def validate(self) -> None:
        """Validate the document against its specification.

        Raises:
            ValidationError: If the document is invalid
        """
        pass

    def _extract_extensions(self) -> None:
        """Extract x-* properties from document into the extensions dict."""
        for key, value in list(self._document.items()):
            if key.startswith("x-"):
                self._extensions[key] = value

    def get_extension(self, key: str) -> Any | None:
        """Get an extension property value.

        Args:
            key: The extension property key (should start with 'x-')

        Returns:
            The extension property value, or None if not found
        """
        return self._extensions.get(key)

    def set_extension(self, key: str, value: Any) -> None:
        """Set an extension property value.

        Args:
            key: The extension property key (must start with 'x-')
            value: The value to set

        Raises:
            ValueError: If the key does not start with 'x-'
        """
        if not key.startswith("x-"):
            raise ValueError(f"Extension property must start with 'x-': {key}")
        self._extensions[key] = value
        self._document[key] = value

    def remove_extension(self, key: str) -> None:
        """Remove an extension property.

        Args:
            key: The extension property key to remove
        """
        self._extensions.pop(key, None)
        self._document.pop(key, None)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            A copy of the document dictionary
        """
        return self._document.copy()
