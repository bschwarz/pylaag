"""Sample data generation from OpenAPI schemas."""

import random
import string
from typing import Any

from pylaag_openapi.components import ComponentManager
from pylaag_openapi.document import OpenAPIDocument


class SampleGenerator:
    """Generates sample data from OpenAPI schemas.

    This class can generate example values that conform to JSON Schema
    definitions, including support for various types, formats, constraints,
    and $ref references.
    """

    def __init__(self, document: OpenAPIDocument):
        """Initialize the SampleGenerator.

        Args:
            document: The OpenAPI document containing schemas
        """
        self.document = document
        self.component_manager = ComponentManager(document)

    def generate_from_schema(
        self,
        schema: dict[str, Any],
        depth: int = 0,
        max_depth: int = 5,
    ) -> Any:
        """Generate a sample value from a schema.

        Args:
            schema: The JSON schema to generate from
            depth: Current recursion depth (default: 0)
            max_depth: Maximum recursion depth to prevent infinite loops (default: 5)

        Returns:
            A sample value conforming to the schema
        """
        if depth > max_depth:
            return None

        # Handle $ref
        if "$ref" in schema:
            ref_schema = self.component_manager.resolve_reference(schema["$ref"])
            if ref_schema:
                return self.generate_from_schema(ref_schema, depth + 1, max_depth)
            return None

        # Handle enum
        if "enum" in schema:
            return random.choice(schema["enum"])

        schema_type = schema.get("type", "object")

        if schema_type == "string":
            return self._generate_string(schema)
        elif schema_type == "number" or schema_type == "integer":
            return self._generate_number(schema)
        elif schema_type == "boolean":
            return random.choice([True, False])
        elif schema_type == "array":
            return self._generate_array(schema, depth, max_depth)
        elif schema_type == "object":
            return self._generate_object(schema, depth, max_depth)
        elif schema_type == "null":
            return None

        return None

    def _generate_string(self, schema: dict[str, Any]) -> str:
        """Generate a string value.

        Args:
            schema: The schema definition for the string

        Returns:
            A generated string value
        """
        if "example" in schema:
            return str(schema["example"])

        # Get length constraints
        min_length = schema.get("minLength", 1)
        # Only use maxLength if explicitly specified
        max_length = schema.get("maxLength")

        format_type = schema.get("format")

        # For format types, respect length constraints if they're specified
        if format_type == "email":
            base_email = "user@example.com"
            # Check if we can use the base email
            if max_length is None or max_length >= len(base_email):
                if min_length <= len(base_email):
                    return base_email
            # Try to use a shorter email if constraints allow
            elif max_length >= 7 and min_length <= 6:
                return "a@b.co"[:max_length]
            # Can't satisfy constraints with email format, fall through
            format_type = None
        elif format_type == "uri":
            base_uri = "https://example.com"
            if max_length is None or max_length >= len(base_uri):
                if min_length <= len(base_uri):
                    return base_uri
            elif max_length >= 10 and min_length <= 10:
                return "http://a.b"[:max_length]
            format_type = None
        elif format_type == "date":
            base_date = "2024-01-01"
            if (max_length is None or max_length >= len(base_date)) and (
                min_length <= len(base_date)
            ):
                return base_date
            format_type = None
        elif format_type == "date-time":
            base_datetime = "2024-01-01T00:00:00Z"
            if (max_length is None or max_length >= len(base_datetime)) and (
                min_length <= len(base_datetime)
            ):
                return base_datetime
            format_type = None
        elif format_type == "uuid":
            base_uuid = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
            if (max_length is None or max_length >= len(base_uuid)) and (
                min_length <= len(base_uuid)
            ):
                return base_uuid
            format_type = None

        # If no format or format couldn't be used, generate random string
        # Use default max_length of 20 if not specified
        if max_length is None:
            max_length = 20

        length = random.randint(min_length, min(max_length, 20))

        return "".join(random.choices(string.ascii_letters, k=length))

    def _generate_number(self, schema: dict[str, Any]) -> int | float:
        """Generate a number value.

        Args:
            schema: The schema definition for the number

        Returns:
            A generated number value (int or float)
        """
        if "example" in schema:
            return schema["example"]

        minimum = schema.get("minimum", 0)
        maximum = schema.get("maximum", 100)

        if schema.get("type") == "integer":
            return random.randint(int(minimum), int(maximum))
        else:
            return random.uniform(minimum, maximum)

    def _generate_array(
        self,
        schema: dict[str, Any],
        depth: int,
        max_depth: int,
    ) -> list[Any]:
        """Generate an array value.

        Args:
            schema: The schema definition for the array
            depth: Current recursion depth
            max_depth: Maximum recursion depth

        Returns:
            A generated array
        """
        items_schema = schema.get("items", {})
        min_items = schema.get("minItems", 1)
        max_items = schema.get("maxItems", 3)

        # Cap max_items at 3 for reasonable sample size
        effective_max = min(max_items, 3)

        # Handle case where min_items >= effective_max
        if min_items >= effective_max:
            count = min_items
        else:
            count = random.randint(min_items, effective_max)

        return [self.generate_from_schema(items_schema, depth + 1, max_depth) for _ in range(count)]

    def _generate_object(
        self,
        schema: dict[str, Any],
        depth: int,
        max_depth: int,
    ) -> dict[str, Any]:
        """Generate an object value.

        Args:
            schema: The schema definition for the object
            depth: Current recursion depth
            max_depth: Maximum recursion depth

        Returns:
            A generated object
        """
        result: dict[str, Any] = {}
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        for prop_name, prop_schema in properties.items():
            if prop_name in required or random.random() > 0.5:
                result[prop_name] = self.generate_from_schema(
                    prop_schema,
                    depth + 1,
                    max_depth,
                )

        return result
