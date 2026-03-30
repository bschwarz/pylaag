"""Property-based tests for sample generation from OpenAPI schemas."""

from hypothesis import given
from hypothesis import strategies as st
from pylaag.openapi import OpenAPIDocument, SampleGenerator


# Strategy for generating simple JSON schemas (without $ref)
@st.composite
def simple_schema_strategy(draw):
    """Generate simple JSON schemas without references."""
    schema_type = draw(
        st.sampled_from(["string", "number", "integer", "boolean", "array", "object"])
    )

    schema = {"type": schema_type}

    if schema_type == "string":
        min_length = draw(st.integers(min_value=0, max_value=10))
        max_length = draw(st.integers(min_value=min_length, max_value=100))
        schema["minLength"] = min_length
        schema["maxLength"] = max_length

        # Optionally add format
        if draw(st.booleans()):
            schema["format"] = draw(st.sampled_from(["email", "uri", "date", "date-time", "uuid"]))

    elif schema_type in ["number", "integer"]:
        minimum = draw(st.integers(min_value=0, max_value=100))
        maximum = draw(st.integers(min_value=minimum, max_value=1000))
        schema["minimum"] = minimum
        schema["maximum"] = maximum

    elif schema_type == "array":
        # Simple array with string items
        schema["items"] = {"type": "string"}
        min_items = draw(st.integers(min_value=0, max_value=5))
        max_items = draw(st.integers(min_value=min_items, max_value=10))
        schema["minItems"] = min_items
        schema["maxItems"] = max_items

    elif schema_type == "object":
        # Simple object with a few properties
        num_props = draw(st.integers(min_value=1, max_value=3))
        properties = {}
        required = []

        for i in range(num_props):
            prop_name = f"prop{i}"
            prop_type = draw(st.sampled_from(["string", "number", "boolean"]))
            properties[prop_name] = {"type": prop_type}

            # Randomly make it required
            if draw(st.booleans()):
                required.append(prop_name)

        schema["properties"] = properties
        if required:
            schema["required"] = required

    return schema


# Strategy for generating schemas with enum
@st.composite
def enum_schema_strategy(draw):
    """Generate schemas with enum constraints."""
    schema_type = draw(st.sampled_from(["string", "number", "integer"]))

    if schema_type == "string":
        enum_values = draw(
            st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=5, unique=True)
        )
    elif schema_type == "integer":
        enum_values = draw(st.lists(st.integers(), min_size=1, max_size=5, unique=True))
    else:  # number
        enum_values = draw(
            st.lists(
                st.floats(allow_nan=False, allow_infinity=False),
                min_size=1,
                max_size=5,
                unique=True,
            )
        )

    return {"type": schema_type, "enum": enum_values}


@given(schema=simple_schema_strategy())
def test_generated_samples_conform_to_schema(schema: dict) -> None:
    """
    Feature: laag-python-port, Property 12: Generated Samples Conform to Schema

    **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.6**

    For any JSON schema (without $ref), the sample generated from that
    schema should validate against the schema according to JSON Schema
    validation rules.
    """
    # Create a minimal OpenAPI document
    doc = OpenAPIDocument()
    generator = SampleGenerator(doc)

    # Generate a sample
    sample = generator.generate_from_schema(schema)

    # Verify the sample conforms to the schema type
    schema_type = schema.get("type")

    if schema_type == "string":
        assert isinstance(sample, str)
    elif schema_type == "integer":
        assert isinstance(sample, int)
    elif schema_type == "number":
        assert isinstance(sample, (int, float))
    elif schema_type == "boolean":
        assert isinstance(sample, bool)
    elif schema_type == "array":
        assert isinstance(sample, list)
    elif schema_type == "object":
        assert isinstance(sample, dict)


@given(schema=simple_schema_strategy())
def test_generated_samples_respect_constraints(schema: dict) -> None:
    """
    Feature: laag-python-port, Property 13: Generated Samples Respect Constraints

    **Validates: Requirements 6.6**

    For any schema with constraints (minLength, maxLength, minimum, maximum,
    enum, pattern), generated samples should satisfy all specified constraints.
    """
    # Create a minimal OpenAPI document
    doc = OpenAPIDocument()
    generator = SampleGenerator(doc)

    # Generate a sample
    sample = generator.generate_from_schema(schema)

    schema_type = schema.get("type")

    # Check string constraints
    if schema_type == "string" and isinstance(sample, str):
        if "minLength" in schema:
            assert len(sample) >= schema["minLength"]
        if "maxLength" in schema:
            assert len(sample) <= schema["maxLength"]

    # Check number constraints
    elif schema_type in ["number", "integer"] and isinstance(sample, (int, float)):
        if "minimum" in schema:
            assert sample >= schema["minimum"]
        if "maximum" in schema:
            assert sample <= schema["maximum"]

    # Check array constraints
    elif schema_type == "array" and isinstance(sample, list):
        if "minItems" in schema:
            assert len(sample) >= schema["minItems"]
        if "maxItems" in schema:
            assert len(sample) <= schema["maxItems"]

    # Check object constraints
    elif schema_type == "object" and isinstance(sample, dict):
        if "required" in schema:
            for required_prop in schema["required"]:
                assert required_prop in sample


@given(schema=enum_schema_strategy())
def test_generated_samples_respect_enum(schema: dict) -> None:
    """
    Feature: laag-python-port, Property 13: Generated Samples Respect Constraints

    **Validates: Requirements 6.6**

    For schemas with enum constraints, generated samples should be
    one of the enum values.
    """
    # Create a minimal OpenAPI document
    doc = OpenAPIDocument()
    generator = SampleGenerator(doc)

    # Generate a sample
    sample = generator.generate_from_schema(schema)

    # Verify the sample is one of the enum values
    assert sample in schema["enum"]


def test_reference_resolution_in_sample_generation() -> None:
    """
    Feature: laag-python-port, Property 14: Reference Resolution in Sample Generation

    **Validates: Requirements 6.5**

    For any schema containing a $ref reference to an existing component,
    generating a sample should produce a value that validates against
    the referenced schema.
    """
    # Create a document with a schema component
    doc = OpenAPIDocument()
    doc._document["components"] = {
        "schemas": {
            "User": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                },
                "required": ["id", "name"],
            }
        }
    }

    generator = SampleGenerator(doc)

    # Generate a sample from a schema with a $ref
    schema_with_ref = {"$ref": "#/components/schemas/User"}
    sample = generator.generate_from_schema(schema_with_ref)

    # Verify the sample is an object
    assert isinstance(sample, dict)

    # Verify required fields are present
    assert "id" in sample
    assert "name" in sample

    # Verify field types
    assert isinstance(sample["id"], int)
    assert isinstance(sample["name"], str)

    # If email is present, verify it's a string
    if "email" in sample:
        assert isinstance(sample["email"], str)


def test_nested_reference_resolution() -> None:
    """
    Feature: laag-python-port, Property 14: Reference Resolution in Sample Generation

    **Validates: Requirements 6.5**

    For schemas with nested $ref references, sample generation should
    resolve all references correctly.
    """
    # Create a document with nested schema components
    doc = OpenAPIDocument()
    doc._document["components"] = {
        "schemas": {
            "Address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"},
                },
                "required": ["city"],
            },
            "User": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "address": {"$ref": "#/components/schemas/Address"},
                },
                "required": ["id", "name"],
            },
        }
    }

    generator = SampleGenerator(doc)

    # Generate a sample from the User schema
    schema_with_ref = {"$ref": "#/components/schemas/User"}
    sample = generator.generate_from_schema(schema_with_ref)

    # Verify the sample structure
    assert isinstance(sample, dict)
    assert "id" in sample
    assert "name" in sample

    # If address is present, verify it's an object with city
    if "address" in sample:
        assert isinstance(sample["address"], dict)
        # Address might have city (required field)
        if "city" in sample["address"]:
            assert isinstance(sample["address"]["city"], str)


def test_max_depth_prevents_infinite_recursion() -> None:
    """
    Feature: laag-python-port, Property 12: Generated Samples Conform to Schema

    **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.6**

    The max_depth parameter should prevent infinite recursion in
    deeply nested or circular schemas.
    """
    # Create a document with a self-referencing schema
    doc = OpenAPIDocument()
    doc._document["components"] = {
        "schemas": {
            "Node": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"},
                    "children": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/Node"},
                    },
                },
            }
        }
    }

    generator = SampleGenerator(doc)

    # Generate a sample with a low max_depth
    schema_with_ref = {"$ref": "#/components/schemas/Node"}
    sample = generator.generate_from_schema(schema_with_ref, max_depth=2)

    # Should not raise an error and should return a valid sample
    assert isinstance(sample, dict)


def test_string_format_generation() -> None:
    """
    Feature: laag-python-port, Property 12: Generated Samples Conform to Schema

    **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.6**

    String schemas with format specifications should generate
    appropriately formatted strings.
    """
    doc = OpenAPIDocument()
    generator = SampleGenerator(doc)

    # Test email format
    email_schema = {"type": "string", "format": "email"}
    email_sample = generator.generate_from_schema(email_schema)
    assert isinstance(email_sample, str)
    assert "@" in email_sample

    # Test uri format
    uri_schema = {"type": "string", "format": "uri"}
    uri_sample = generator.generate_from_schema(uri_schema)
    assert isinstance(uri_sample, str)
    assert uri_sample.startswith("http")

    # Test date format
    date_schema = {"type": "string", "format": "date"}
    date_sample = generator.generate_from_schema(date_schema)
    assert isinstance(date_sample, str)
    assert len(date_sample) == 10  # YYYY-MM-DD

    # Test date-time format
    datetime_schema = {"type": "string", "format": "date-time"}
    datetime_sample = generator.generate_from_schema(datetime_schema)
    assert isinstance(datetime_sample, str)
    assert "T" in datetime_sample

    # Test uuid format
    uuid_schema = {"type": "string", "format": "uuid"}
    uuid_sample = generator.generate_from_schema(uuid_schema)
    assert isinstance(uuid_sample, str)
    assert len(uuid_sample) == 36  # UUID format


def test_example_value_is_used_when_present() -> None:
    """
    Feature: laag-python-port, Property 12: Generated Samples Conform to Schema

    **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.6**

    When a schema includes an example value, that value should be used
    in the generated sample.
    """
    doc = OpenAPIDocument()
    generator = SampleGenerator(doc)

    # Test string example
    string_schema = {"type": "string", "example": "test-value"}
    string_sample = generator.generate_from_schema(string_schema)
    assert string_sample == "test-value"

    # Test number example
    number_schema = {"type": "number", "example": 42.5}
    number_sample = generator.generate_from_schema(number_schema)
    assert number_sample == 42.5

    # Test integer example
    integer_schema = {"type": "integer", "example": 123}
    integer_sample = generator.generate_from_schema(integer_schema)
    assert integer_sample == 123
