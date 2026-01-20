"""Error classes for the laag Python library."""

from typing import Any


class LaagError(Exception):
    """Base exception for all laag errors."""

    def __init__(self, message: str, context: dict[str, Any] | None = None):
        super().__init__(message)
        self.context = context or {}


class ValidationError(LaagError):
    """Raised when document validation fails."""

    pass


class ParseError(LaagError):
    """Raised when document parsing fails."""

    pass


class NotFoundError(LaagError):
    """Raised when a requested resource is not found."""

    pass
