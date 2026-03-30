"""Integration example demonstrating Smithy shape and trait management."""

from pylaag.smithy import OperationManager, ShapeManager, SmithyDocument, TraitManager


def main():
    """Demonstrate creating a complete Smithy service definition."""
    # Create a new Smithy document
    doc = SmithyDocument()
    print("Created Smithy document")
    print(f"Version: {doc.smithy_version}")

    # Initialize managers
    shape_mgr = ShapeManager(doc)
    trait_mgr = TraitManager(doc)
    op_mgr = OperationManager(doc)

    # Define input structure
    shape_mgr.add_shape(
        "com.example#GetUserInput",
        "structure",
        {
            "members": {
                "userId": {
                    "target": "smithy.api#String",
                }
            }
        },
    )
    print("\nAdded GetUserInput structure")

    # Define output structure
    shape_mgr.add_shape(
        "com.example#GetUserOutput",
        "structure",
        {
            "members": {
                "userId": {"target": "smithy.api#String"},
                "name": {"target": "smithy.api#String"},
                "email": {"target": "smithy.api#String"},
            }
        },
    )
    print("Added GetUserOutput structure")

    # Define error structure
    shape_mgr.add_shape(
        "com.example#UserNotFoundError",
        "structure",
        {
            "members": {
                "message": {"target": "smithy.api#String"},
            }
        },
    )
    print("Added UserNotFoundError structure")

    # Add error trait to the error structure
    trait_mgr.add_trait_to_shape(
        "com.example#UserNotFoundError",
        "smithy.api#error",
        "client",
    )
    print("Added error trait to UserNotFoundError")

    # Create the operation
    op_mgr.add_operation(
        "com.example#GetUser",
        input_shape="com.example#GetUserInput",
        output_shape="com.example#GetUserOutput",
        errors=["com.example#UserNotFoundError"],
    )
    print("\nAdded GetUser operation")

    # Add HTTP trait to the operation
    trait_mgr.add_trait_to_shape(
        "com.example#GetUser",
        "smithy.api#http",
        {
            "method": "GET",
            "uri": "/users/{userId}",
            "code": 200,
        },
    )
    print("Added HTTP trait to GetUser operation")

    # Add documentation trait
    trait_mgr.add_trait_to_shape(
        "com.example#GetUser",
        "smithy.api#documentation",
        "Retrieves a user by their unique identifier",
    )
    print("Added documentation trait to GetUser operation")

    # Validate the document
    doc.validate()
    print("\n✓ Document is valid!")

    # Display the complete document
    print("\nComplete Smithy document:")
    print(doc.to_json(indent=2))

    # Demonstrate target resolution
    print("\n--- Target Resolution ---")
    input_shape = shape_mgr.resolve_target("com.example#GetUserInput")
    print(f"Resolved GetUserInput: {input_shape}")

    # Demonstrate trait retrieval
    print("\n--- Trait Retrieval ---")
    http_trait = trait_mgr.get_trait("com.example#GetUser", "smithy.api#http")
    print(f"HTTP trait: {http_trait}")

    doc_trait = trait_mgr.get_trait("com.example#GetUser", "smithy.api#documentation")
    print(f"Documentation: {doc_trait}")

    # Demonstrate operation retrieval
    print("\n--- Operation Details ---")
    operation = op_mgr.get_operation("com.example#GetUser")
    print(f"Operation type: {operation['type']}")
    print(f"Input: {operation['input']['target']}")
    print(f"Output: {operation['output']['target']}")
    print(f"Errors: {[e['target'] for e in operation['errors']]}")


if __name__ == "__main__":
    main()
