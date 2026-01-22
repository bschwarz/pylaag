"""Component management for OpenAPI documents."""

from typing import Any, Literal

from pylaag_openapi.document import OpenAPIDocument

ComponentType = Literal[
    "schemas",
    "responses",
    "parameters",
    "examples",
    "requestBodies",
    "headers",
    "securitySchemes",
    "links",
    "callbacks",
]


class ComponentManager:
    """Manages components in an OpenAPI document.

    Components are reusable elements like schemas, responses, parameters, etc.
    that can be referenced throughout the document using $ref.
    """

    def __init__(self, document: OpenAPIDocument):
        """Initialize the ComponentManager.

        Args:
            document: The OpenAPI document to manage
        """
        self.document = document

    def _ensure_components(self) -> None:
        """Ensure the components section exists in the document."""
        if "components" not in self.document._document:
            self.document._document["components"] = {}

    def add_component(
        self,
        component_type: ComponentType,
        name: str,
        component: dict[str, Any],
    ) -> None:
        """Add a component to the document.

        Args:
            component_type: The type of component (schemas, responses, etc.)
            name: The name of the component
            component: The component definition
        """
        self._ensure_components()

        if component_type not in self.document._document["components"]:
            self.document._document["components"][component_type] = {}

        self.document._document["components"][component_type][name] = component

    def remove_component(self, component_type: ComponentType, name: str) -> bool:
        """Remove a component from the document.

        Args:
            component_type: The type of component
            name: The name of the component to remove

        Returns:
            True if the component was removed, False if it didn't exist
        """
        components = self.document._document.get("components", {})
        if component_type in components and name in components[component_type]:
            del components[component_type][name]
            return True
        return False

    def get_component(
        self,
        component_type: ComponentType,
        name: str,
    ) -> dict[str, Any] | None:
        """Get a component from the document.

        Args:
            component_type: The type of component
            name: The name of the component

        Returns:
            The component definition, or None if not found
        """
        component = self.document._document.get("components", {}).get(component_type, {}).get(name)
        if isinstance(component, dict):
            return component
        return None

    def resolve_reference(self, ref: str) -> dict[str, Any] | None:
        """Resolve a $ref reference to its actual component.

        Only local references in the format #/path/to/component are supported.

        Args:
            ref: The reference string (e.g., "#/components/schemas/User")

        Returns:
            The resolved component, or None if not found

        Raises:
            ValueError: If the reference is not a local reference
        """
        if not ref.startswith("#/"):
            raise ValueError(f"Only local references are supported: {ref}")

        # Remove '#/' prefix and split into parts
        path = ref[2:]
        parts = path.split("/")

        # Navigate through the document
        current: Any = self.document._document
        for part in parts:
            if not isinstance(current, dict) or part not in current:
                return None
            current = current[part]

        # Ensure we return a dict or None
        if isinstance(current, dict):
            return dict(current)
        return None
