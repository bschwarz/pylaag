"""Unit tests for sample generation from OpenAPI schemas."""

from pylaag_openapi import OpenAPIDocument, SampleGenerator


class TestSampleGenerator:
    """Unit tests for the SampleGenerator class."""

    def test_generate_string_primitive(self):
        """Test generating a simple string value."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {"type": "string"}
        sample = generator.generate_from_schema(schema)

        assert isinstance(sample, str)
        assert len(sample) > 0

    def test_generate_number_primitive(self):
        """Test generating a number value."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {"type": "number"}
        sample = generator.generate_from_schema(schema)

        assert isinstance(sample, (int, float))

    def test_generate_integer_primitive(self):
        """Test generating an integer value."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {"type": "integer"}
        sample = generator.generate_from_schema(schema)

        assert isinstance(sample, int)

    def test_generate_boolean_primitive(self):
        """Test generating a boolean value."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {"type": "boolean"}
        sample = generator.generate_from_schema(schema)

        assert isinstance(sample, bool)

    def test_generate_null_primitive(self):
        """Test generating a null value."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {"type": "null"}
        sample = generator.generate_from_schema(schema)

        assert sample is None

    def test_generate_email_format(self):
        """Test generating a string with email format."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {"type": "string", "format": "email"}
        sample = generator.generate_from_schema(schema)

        assert isinstance(sample, str)
        assert "@" in sample
        assert sample == "user@example.com"

    def test_generate_uri_format(self):
        """Test generating a string with uri format."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {"type": "string", "format": "uri"}
        sample = generator.generate_from_schema(schema)

        assert isinstance(sample, str)
        assert sample.startswith("http")
        assert sample == "https://example.com"

    def test_generate_date_format(self):
        """Test generating a string with date format."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {"type": "string", "format": "date"}
        sample = generator.generate_from_schema(schema)

        assert isinstance(sample, str)
        assert len(sample) == 10  # YYYY-MM-DD
        assert sample == "2024-01-01"

    def test_generate_datetime_format(self):
        """Test generating a string with date-time format."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {"type": "string", "format": "date-time"}
        sample = generator.generate_from_schema(schema)

        assert isinstance(sample, str)
        assert "T" in sample
        assert sample == "2024-01-01T00:00:00Z"

    def test_generate_uuid_format(self):
        """Test generating a string with uuid format."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {"type": "string", "format": "uuid"}
        sample = generator.generate_from_schema(schema)

        assert isinstance(sample, str)
        assert len(sample) == 36
        assert sample == "f47ac10b-58cc-4372-a567-0e02b2c3d479"

    def test_generate_enum_string(self):
        """Test generating a value from a string enum."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {"type": "string", "enum": ["red", "green", "blue"]}
        sample = generator.generate_from_schema(schema)

        assert sample in ["red", "green", "blue"]

    def test_generate_enum_number(self):
        """Test generating a value from a number enum."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {"type": "number", "enum": [1, 2, 3, 4, 5]}
        sample = generator.generate_from_schema(schema)

        assert sample in [1, 2, 3, 4, 5]

    def test_generate_array_of_strings(self):
        """Test generating an array of strings."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {"type": "array", "items": {"type": "string"}}
        sample = generator.generate_from_schema(schema)

        assert isinstance(sample, list)
        assert len(sample) > 0
        assert all(isinstance(item, str) for item in sample)

    def test_generate_array_with_min_max_items(self):
        """Test generating an array with minItems and maxItems constraints."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 5}
        sample = generator.generate_from_schema(schema)

        assert isinstance(sample, list)
        assert 2 <= len(sample) <= 5
        assert all(isinstance(item, int) for item in sample)

    def test_generate_object_with_properties(self):
        """Test generating an object with properties."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "active": {"type": "boolean"},
            },
        }
        sample = generator.generate_from_schema(schema)

        assert isinstance(sample, dict)
        # Properties may or may not be present since none are required
        # Just verify it's a valid dict (can be empty)

    def test_generate_object_with_required_properties(self):
        """Test generating an object with required properties."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "email": {"type": "string"},
            },
            "required": ["id", "name"],
        }
        sample = generator.generate_from_schema(schema)

        assert isinstance(sample, dict)
        # Required properties must be present
        assert "id" in sample
        assert "name" in sample
        assert isinstance(sample["id"], int)
        assert isinstance(sample["name"], str)

    def test_generate_nested_object(self):
        """Test generating a nested object."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer"},
                    },
                    "required": ["name"],
                },
            },
            "required": ["user"],
        }
        sample = generator.generate_from_schema(schema)

        assert isinstance(sample, dict)
        assert "user" in sample
        assert isinstance(sample["user"], dict)
        assert "name" in sample["user"]

    def test_generate_nested_array(self):
        """Test generating a nested array."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {
            "type": "array",
            "items": {
                "type": "array",
                "items": {"type": "string"},
            },
        }
        sample = generator.generate_from_schema(schema)

        assert isinstance(sample, list)
        assert len(sample) > 0
        assert all(isinstance(item, list) for item in sample)
        # Check nested arrays contain strings
        for nested_array in sample:
            if len(nested_array) > 0:
                assert all(isinstance(s, str) for s in nested_array)

    def test_generate_with_example_value(self):
        """Test that example values are used when present."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        # String example
        schema = {"type": "string", "example": "custom-value"}
        sample = generator.generate_from_schema(schema)
        assert sample == "custom-value"

        # Number example
        schema = {"type": "number", "example": 42.5}
        sample = generator.generate_from_schema(schema)
        assert sample == 42.5

        # Integer example
        schema = {"type": "integer", "example": 123}
        sample = generator.generate_from_schema(schema)
        assert sample == 123

    def test_generate_with_reference(self):
        """Test generating a sample from a schema with $ref."""
        doc = OpenAPIDocument()
        doc._document["components"] = {
            "schemas": {
                "Pet": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "species": {"type": "string"},
                    },
                    "required": ["name"],
                }
            }
        }

        generator = SampleGenerator(doc)
        schema = {"$ref": "#/components/schemas/Pet"}
        sample = generator.generate_from_schema(schema)

        assert isinstance(sample, dict)
        assert "name" in sample
        assert isinstance(sample["name"], str)

    def test_generate_with_invalid_reference(self):
        """Test generating a sample from an invalid $ref returns None."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {"$ref": "#/components/schemas/NonExistent"}
        sample = generator.generate_from_schema(schema)

        assert sample is None

    def test_max_depth_limit(self):
        """Test that max_depth prevents infinite recursion."""
        doc = OpenAPIDocument()
        doc._document["components"] = {
            "schemas": {
                "Node": {
                    "type": "object",
                    "properties": {
                        "value": {"type": "string"},
                        "next": {"$ref": "#/components/schemas/Node"},
                    },
                }
            }
        }

        generator = SampleGenerator(doc)
        schema = {"$ref": "#/components/schemas/Node"}

        # Should not raise an error even with circular reference
        sample = generator.generate_from_schema(schema, max_depth=3)
        assert isinstance(sample, dict)

    def test_generate_with_string_constraints(self):
        """Test generating strings with length constraints."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {"type": "string", "minLength": 5, "maxLength": 10}
        sample = generator.generate_from_schema(schema)

        assert isinstance(sample, str)
        assert 5 <= len(sample) <= 10

    def test_generate_with_number_constraints(self):
        """Test generating numbers with min/max constraints."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {"type": "number", "minimum": 10, "maximum": 20}
        sample = generator.generate_from_schema(schema)

        assert isinstance(sample, (int, float))
        assert 10 <= sample <= 20

    def test_generate_with_integer_constraints(self):
        """Test generating integers with min/max constraints."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {"type": "integer", "minimum": 1, "maximum": 100}
        sample = generator.generate_from_schema(schema)

        assert isinstance(sample, int)
        assert 1 <= sample <= 100

    def test_generate_unknown_type_returns_none(self):
        """Test that unknown schema types return None."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {"type": "unknown"}
        sample = generator.generate_from_schema(schema)

        assert sample is None

    def test_generate_empty_schema_defaults_to_object(self):
        """Test that empty schema defaults to object type."""
        doc = OpenAPIDocument()
        generator = SampleGenerator(doc)

        schema = {}
        sample = generator.generate_from_schema(schema)

        # Empty schema defaults to object type
        assert isinstance(sample, dict)
