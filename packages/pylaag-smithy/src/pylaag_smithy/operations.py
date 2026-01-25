"""Operation management for Smithy documents."""

from typing import Any

from pylaag_smithy.document import SmithyDocument
from pylaag_smithy.shapes import ShapeManager


class OperationManager:
    """Manages operations in a Smithy document."""

    def __init__(self, document: SmithyDocument):
        """Initialize the OperationManager.

        Args:
            document: The Smithy document to manage operations for
        """
        self.document = document
        self.shape_manager = ShapeManager(document)

    def add_operation(
        self,
        operation_id: str,
        input_shape: str | None = None,
        output_shape: str | None = None,
        errors: list[str] | None = None,
    ) -> None:
        """Add an operation to the document.

        Args:
            operation_id: The fully qualified operation ID (e.g., "com.example#GetUser")
            input_shape: The input shape ID (optional)
            output_shape: The output shape ID (optional)
            errors: List of error shape IDs (optional)
        """
        operation_def: dict[str, Any] = {}

        if input_shape:
            operation_def["input"] = {"target": input_shape}

        if output_shape:
            operation_def["output"] = {"target": output_shape}

        if errors:
            operation_def["errors"] = [{"target": err} for err in errors]

        self.shape_manager.add_shape(operation_id, "operation", operation_def)

    def remove_operation(self, operation_id: str) -> bool:
        """Remove an operation from the document.

        Args:
            operation_id: The fully qualified operation ID to remove

        Returns:
            True if the operation was removed, False if it didn't exist
        """
        return self.shape_manager.remove_shape(operation_id)

    def get_operation(self, operation_id: str) -> dict[str, Any] | None:
        """Get an operation from the document.

        Args:
            operation_id: The fully qualified operation ID to retrieve

        Returns:
            The operation definition dictionary, or None if not found
        """
        return self.shape_manager.get_shape(operation_id)
