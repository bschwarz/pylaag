"""Unit tests for Smithy managers."""

import pytest
from pylaag.core import NotFoundError
from pylaag.smithy import OperationManager, ShapeManager, SmithyDocument, TraitManager


class TestShapeManager:
    """Unit tests for ShapeManager."""

    def test_add_structure_shape(self):
        """Test adding a structure shape."""
        doc = SmithyDocument()
        shape_mgr = ShapeManager(doc)

        shape_mgr.add_shape(
            "com.example#User",
            "structure",
            {
                "members": {
                    "id": {"target": "smithy.api#String"},
                    "name": {"target": "smithy.api#String"},
                }
            },
        )

        shape = shape_mgr.get_shape("com.example#User")
        assert shape is not None
        assert shape["type"] == "structure"
        assert "members" in shape
        assert "id" in shape["members"]
        assert "name" in shape["members"]

    def test_add_list_shape(self):
        """Test adding a list shape."""
        doc = SmithyDocument()
        shape_mgr = ShapeManager(doc)

        shape_mgr.add_shape(
            "com.example#UserList",
            "list",
            {"member": {"target": "com.example#User"}},
        )

        shape = shape_mgr.get_shape("com.example#UserList")
        assert shape is not None
        assert shape["type"] == "list"
        assert shape["member"]["target"] == "com.example#User"

    def test_add_map_shape(self):
        """Test adding a map shape."""
        doc = SmithyDocument()
        shape_mgr = ShapeManager(doc)

        shape_mgr.add_shape(
            "com.example#UserMap",
            "map",
            {
                "key": {"target": "smithy.api#String"},
                "value": {"target": "com.example#User"},
            },
        )

        shape = shape_mgr.get_shape("com.example#UserMap")
        assert shape is not None
        assert shape["type"] == "map"
        assert shape["key"]["target"] == "smithy.api#String"
        assert shape["value"]["target"] == "com.example#User"

    def test_add_primitive_shapes(self):
        """Test adding primitive shape types."""
        doc = SmithyDocument()
        shape_mgr = ShapeManager(doc)

        primitives = [
            "string",
            "integer",
            "long",
            "float",
            "double",
            "boolean",
            "blob",
            "timestamp",
        ]

        for i, prim_type in enumerate(primitives):
            shape_id = f"com.example#Custom{prim_type.capitalize()}{i}"
            shape_mgr.add_shape(shape_id, prim_type, {})

            shape = shape_mgr.get_shape(shape_id)
            assert shape is not None
            assert shape["type"] == prim_type

    def test_remove_shape(self):
        """Test removing a shape."""
        doc = SmithyDocument()
        shape_mgr = ShapeManager(doc)

        shape_mgr.add_shape("com.example#User", "structure", {})
        assert shape_mgr.get_shape("com.example#User") is not None

        removed = shape_mgr.remove_shape("com.example#User")
        assert removed is True
        assert shape_mgr.get_shape("com.example#User") is None

    def test_remove_nonexistent_shape(self):
        """Test removing a non-existent shape."""
        doc = SmithyDocument()
        shape_mgr = ShapeManager(doc)

        removed = shape_mgr.remove_shape("com.example#NonExistent")
        assert removed is False

    def test_resolve_target(self):
        """Test resolving a target reference."""
        doc = SmithyDocument()
        shape_mgr = ShapeManager(doc)

        shape_mgr.add_shape(
            "com.example#User",
            "structure",
            {"members": {"id": {"target": "smithy.api#String"}}},
        )

        resolved = shape_mgr.resolve_target("com.example#User")
        assert resolved is not None
        assert resolved["type"] == "structure"

    def test_resolve_nonexistent_target(self):
        """Test resolving a non-existent target."""
        doc = SmithyDocument()
        shape_mgr = ShapeManager(doc)

        resolved = shape_mgr.resolve_target("com.example#NonExistent")
        assert resolved is None


class TestTraitManager:
    """Unit tests for TraitManager."""

    def test_add_trait_to_shape(self):
        """Test adding a trait to a shape."""
        doc = SmithyDocument()
        shape_mgr = ShapeManager(doc)
        trait_mgr = TraitManager(doc)

        shape_mgr.add_shape("com.example#User", "structure", {})
        trait_mgr.add_trait_to_shape(
            "com.example#User",
            "smithy.api#documentation",
            "User information",
        )

        trait = trait_mgr.get_trait("com.example#User", "smithy.api#documentation")
        assert trait == "User information"

    def test_add_trait_with_dict_value(self):
        """Test adding a trait with a dictionary value."""
        doc = SmithyDocument()
        shape_mgr = ShapeManager(doc)
        trait_mgr = TraitManager(doc)

        shape_mgr.add_shape("com.example#GetUser", "operation", {})
        trait_mgr.add_trait_to_shape(
            "com.example#GetUser",
            "smithy.api#http",
            {"method": "GET", "uri": "/users/{id}"},
        )

        trait = trait_mgr.get_trait("com.example#GetUser", "smithy.api#http")
        assert trait["method"] == "GET"
        assert trait["uri"] == "/users/{id}"

    def test_add_trait_with_none_value(self):
        """Test adding a trait with None value (should become empty dict)."""
        doc = SmithyDocument()
        shape_mgr = ShapeManager(doc)
        trait_mgr = TraitManager(doc)

        shape_mgr.add_shape("com.example#User", "structure", {})
        trait_mgr.add_trait_to_shape("com.example#User", "smithy.api#required", None)

        trait = trait_mgr.get_trait("com.example#User", "smithy.api#required")
        assert trait == {}

    def test_add_trait_to_nonexistent_shape(self):
        """Test adding a trait to a non-existent shape."""
        doc = SmithyDocument()
        trait_mgr = TraitManager(doc)

        with pytest.raises(NotFoundError) as exc_info:
            trait_mgr.add_trait_to_shape(
                "com.example#NonExistent",
                "smithy.api#documentation",
                "Test",
            )

        assert "com.example#NonExistent" in str(exc_info.value)

    def test_remove_trait_from_shape(self):
        """Test removing a trait from a shape."""
        doc = SmithyDocument()
        shape_mgr = ShapeManager(doc)
        trait_mgr = TraitManager(doc)

        shape_mgr.add_shape("com.example#User", "structure", {})
        trait_mgr.add_trait_to_shape(
            "com.example#User",
            "smithy.api#documentation",
            "User info",
        )

        removed = trait_mgr.remove_trait_from_shape(
            "com.example#User",
            "smithy.api#documentation",
        )
        assert removed is True

        trait = trait_mgr.get_trait("com.example#User", "smithy.api#documentation")
        assert trait is None

    def test_remove_nonexistent_trait(self):
        """Test removing a non-existent trait."""
        doc = SmithyDocument()
        shape_mgr = ShapeManager(doc)
        trait_mgr = TraitManager(doc)

        shape_mgr.add_shape("com.example#User", "structure", {})

        removed = trait_mgr.remove_trait_from_shape(
            "com.example#User",
            "smithy.api#documentation",
        )
        assert removed is False

    def test_multiple_traits_on_shape(self):
        """Test adding multiple traits to the same shape."""
        doc = SmithyDocument()
        shape_mgr = ShapeManager(doc)
        trait_mgr = TraitManager(doc)

        shape_mgr.add_shape("com.example#User", "structure", {})
        trait_mgr.add_trait_to_shape(
            "com.example#User",
            "smithy.api#documentation",
            "User information",
        )
        trait_mgr.add_trait_to_shape(
            "com.example#User",
            "smithy.api#sensitive",
            {},
        )

        doc_trait = trait_mgr.get_trait("com.example#User", "smithy.api#documentation")
        sens_trait = trait_mgr.get_trait("com.example#User", "smithy.api#sensitive")

        assert doc_trait == "User information"
        assert sens_trait == {}


class TestOperationManager:
    """Unit tests for OperationManager."""

    def test_add_operation_with_input_and_output(self):
        """Test adding an operation with input and output shapes."""
        doc = SmithyDocument()
        op_mgr = OperationManager(doc)

        op_mgr.add_operation(
            "com.example#GetUser",
            input_shape="com.example#GetUserInput",
            output_shape="com.example#GetUserOutput",
        )

        operation = op_mgr.get_operation("com.example#GetUser")
        assert operation is not None
        assert operation["type"] == "operation"
        assert operation["input"]["target"] == "com.example#GetUserInput"
        assert operation["output"]["target"] == "com.example#GetUserOutput"

    def test_add_operation_with_errors(self):
        """Test adding an operation with error shapes."""
        doc = SmithyDocument()
        op_mgr = OperationManager(doc)

        op_mgr.add_operation(
            "com.example#GetUser",
            input_shape="com.example#GetUserInput",
            output_shape="com.example#GetUserOutput",
            errors=["com.example#UserNotFound", "com.example#InvalidRequest"],
        )

        operation = op_mgr.get_operation("com.example#GetUser")
        assert operation is not None
        assert "errors" in operation
        assert len(operation["errors"]) == 2
        assert operation["errors"][0]["target"] == "com.example#UserNotFound"
        assert operation["errors"][1]["target"] == "com.example#InvalidRequest"

    def test_add_operation_minimal(self):
        """Test adding an operation with no input, output, or errors."""
        doc = SmithyDocument()
        op_mgr = OperationManager(doc)

        op_mgr.add_operation("com.example#Ping")

        operation = op_mgr.get_operation("com.example#Ping")
        assert operation is not None
        assert operation["type"] == "operation"
        assert "input" not in operation
        assert "output" not in operation
        assert "errors" not in operation

    def test_remove_operation(self):
        """Test removing an operation."""
        doc = SmithyDocument()
        op_mgr = OperationManager(doc)

        op_mgr.add_operation("com.example#GetUser")
        assert op_mgr.get_operation("com.example#GetUser") is not None

        removed = op_mgr.remove_operation("com.example#GetUser")
        assert removed is True
        assert op_mgr.get_operation("com.example#GetUser") is None

    def test_remove_nonexistent_operation(self):
        """Test removing a non-existent operation."""
        doc = SmithyDocument()
        op_mgr = OperationManager(doc)

        removed = op_mgr.remove_operation("com.example#NonExistent")
        assert removed is False

    def test_operation_is_shape(self):
        """Test that operations are stored as shapes."""
        doc = SmithyDocument()
        op_mgr = OperationManager(doc)
        shape_mgr = ShapeManager(doc)

        op_mgr.add_operation("com.example#GetUser")

        # Should be retrievable as a shape
        shape = shape_mgr.get_shape("com.example#GetUser")
        assert shape is not None
        assert shape["type"] == "operation"


class TestIntegration:
    """Integration tests for all managers working together."""

    def test_complete_service_definition(self):
        """Test creating a complete service with shapes, operations, and traits."""
        doc = SmithyDocument()
        shape_mgr = ShapeManager(doc)
        trait_mgr = TraitManager(doc)
        op_mgr = OperationManager(doc)

        # Add input/output structures
        shape_mgr.add_shape(
            "com.example#GetUserInput",
            "structure",
            {"members": {"userId": {"target": "smithy.api#String"}}},
        )

        shape_mgr.add_shape(
            "com.example#GetUserOutput",
            "structure",
            {
                "members": {
                    "userId": {"target": "smithy.api#String"},
                    "name": {"target": "smithy.api#String"},
                }
            },
        )

        # Add error structure
        shape_mgr.add_shape(
            "com.example#UserNotFound",
            "structure",
            {"members": {"message": {"target": "smithy.api#String"}}},
        )

        # Add operation
        op_mgr.add_operation(
            "com.example#GetUser",
            input_shape="com.example#GetUserInput",
            output_shape="com.example#GetUserOutput",
            errors=["com.example#UserNotFound"],
        )

        # Add traits to operation
        trait_mgr.add_trait_to_shape(
            "com.example#GetUser",
            "smithy.api#http",
            {"method": "GET", "uri": "/users/{userId}"},
        )

        trait_mgr.add_trait_to_shape(
            "com.example#GetUser",
            "smithy.api#documentation",
            "Retrieves a user by ID",
        )

        # Verify everything is in place
        operation = op_mgr.get_operation("com.example#GetUser")
        assert operation is not None
        assert operation["input"]["target"] == "com.example#GetUserInput"
        assert operation["output"]["target"] == "com.example#GetUserOutput"
        assert len(operation["errors"]) == 1

        http_trait = trait_mgr.get_trait("com.example#GetUser", "smithy.api#http")
        assert http_trait["method"] == "GET"

        doc_trait = trait_mgr.get_trait("com.example#GetUser", "smithy.api#documentation")
        assert doc_trait == "Retrieves a user by ID"

        # Document should still be valid
        doc.validate()
