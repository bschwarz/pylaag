"""Integration example demonstrating RAML resource and type management."""

from pylaag_raml import RAMLDocument, ResourceManager, TypeManager


def main():
    """Demonstrate RAML resource and type management."""
    # Create a new RAML document
    doc = RAMLDocument()
    print("Created RAML document")
    print(f"Title: {doc.title}")
    print(f"Version: {doc.version}")
    print()

    # Create managers
    resource_mgr = ResourceManager(doc)
    type_mgr = TypeManager(doc)

    # Add types
    print("Adding types...")
    type_mgr.add_type(
        "User",
        {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "email": {"type": "string"},
            },
            "required": ["id", "name", "email"],
        },
    )

    type_mgr.add_type(
        "Post",
        {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "title": {"type": "string"},
                "content": {"type": "string"},
                "authorId": {"type": "integer"},
            },
            "required": ["id", "title", "authorId"],
        },
    )
    print("Added User and Post types")
    print()

    # Add resources with methods
    print("Adding resources...")
    resource_mgr.add_method(
        "/users",
        "get",
        {
            "description": "Get all users",
            "responses": {"200": {"body": {"application/json": {"type": "User[]"}}}},
        },
    )

    resource_mgr.add_method(
        "/users",
        "post",
        {
            "description": "Create a new user",
            "body": {"application/json": {"type": "User"}},
            "responses": {"201": {"body": {"application/json": {"type": "User"}}}},
        },
    )

    resource_mgr.add_method(
        "/users/{id}",
        "get",
        {
            "description": "Get a user by ID",
            "responses": {
                "200": {"body": {"application/json": {"type": "User"}}},
                "404": {"description": "User not found"},
            },
        },
    )

    resource_mgr.add_method(
        "/users/{id}/posts",
        "get",
        {
            "description": "Get all posts by a user",
            "responses": {"200": {"body": {"application/json": {"type": "Post[]"}}}},
        },
    )
    print("Added /users and /users/{id} resources with methods")
    print()

    # Validate the document
    print("Validating document...")
    doc.validate()
    print("Document is valid!")
    print()

    # Display the document structure
    print("Document structure:")
    print(f"- Types: {list(type_mgr.get_type('User').keys()) if type_mgr.get_type('User') else []}")
    print("- Resources:")
    for path in ["/users", "/users/{id}", "/users/{id}/posts"]:
        resource = resource_mgr.get_resource(path)
        if resource:
            methods = [m for m in resource.keys() if m in ["get", "post", "put", "delete", "patch"]]
            print(f"  - {path}: {', '.join(methods)}")
    print()

    # Serialize to YAML
    print("YAML output:")
    print(doc.to_yaml())


if __name__ == "__main__":
    main()
