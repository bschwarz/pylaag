---
name: pylaag-smithy
description: Working with AWS Smithy models using pylaag-smithy. Use when parsing, creating, or modifying Smithy 2.0 documents in Python.
---

# pylaag-smithy — Working with AWS Smithy Models

## Installation & Import

```python
from pylaag.smithy import SmithyDocument, ShapeManager, TraitManager, OperationManager
```

## Creating a Document

```python
# Empty document
doc = SmithyDocument()

# From a dict
doc = SmithyDocument({
    "smithy": "2.0",
    "metadata": {},
    "shapes": {}
})

# From JSON string
doc = SmithyDocument.from_json(json_str)
```

## Document Properties & Serialization

```python
doc.smithy_version   # "2.0"
doc.shapes           # dict of all shapes

doc.to_json(indent=2)  # JSON string
```

## Validation

```python
from pylaag.core import ValidationError

try:
    doc.validate()
except ValidationError as e:
    print(e)
```

Checks for required `smithy` version and `shapes` fields.

## ShapeManager — Add/Read/Remove Shapes

```python
shape_mgr = ShapeManager(doc)

# Add a structure shape
shape_mgr.add_shape("com.example#User", "structure", {
    "members": {
        "id":   {"target": "smithy.api#String"},
        "name": {"target": "smithy.api#String"},
        "age":  {"target": "smithy.api#Integer"}
    }
})

# Add a service shape
shape_mgr.add_shape("com.example#UserService", "service", {
    "version": "2024-01-01",
    "operations": [{"target": "com.example#GetUser"}]
})

# Add an operation shape
shape_mgr.add_shape("com.example#GetUser", "operation", {
    "input":  {"target": "com.example#GetUserInput"},
    "output": {"target": "com.example#GetUserOutput"}
})

# Read
shape = shape_mgr.get_shape("com.example#User")     # dict | None

# Resolve a target reference
resolved = shape_mgr.resolve_target("com.example#User")

# Remove
shape_mgr.remove_shape("com.example#User")           # bool
```

`ShapeType` values: `"service" | "operation" | "resource" | "structure" | "union" | "list" | "map" | "string" | "integer" | "long" | "float" | "double" | "boolean" | "blob" | "timestamp"`

## TraitManager — Add/Get/Remove Traits

```python
trait_mgr = TraitManager(doc)

# Add a trait to a shape (shape must already exist)
trait_mgr.add_trait_to_shape(
    "com.example#User",
    "smithy.api#documentation",
    "Represents a user in the system."
)

# Add a unit trait (no value)
trait_mgr.add_trait_to_shape("com.example#GetUser", "smithy.api#readonly")

# Add http trait
trait_mgr.add_trait_to_shape("com.example#GetUser", "smithy.api#http", {
    "method": "GET",
    "uri": "/users/{id}"
})

# Get
value = trait_mgr.get_trait("com.example#User", "smithy.api#documentation")
# → "Represents a user in the system."

# Remove
trait_mgr.remove_trait_from_shape("com.example#User", "smithy.api#documentation")  # bool
```

Raises `NotFoundError` if the shape doesn't exist when adding a trait.

---

## Full Example

```python
from pylaag.smithy import SmithyDocument, ShapeManager, TraitManager

doc = SmithyDocument()
shape_mgr = ShapeManager(doc)
trait_mgr = TraitManager(doc)

# Add shapes
shape_mgr.add_shape("com.example#User", "structure", {
    "members": {
        "id":   {"target": "smithy.api#String"},
        "name": {"target": "smithy.api#String"},
    }
})

shape_mgr.add_shape("com.example#GetUser", "operation", {
    "input":  {"target": "com.example#GetUserInput"},
    "output": {"target": "com.example#GetUserOutput"},
})

# Add traits
trait_mgr.add_trait_to_shape("com.example#GetUser", "smithy.api#readonly")
trait_mgr.add_trait_to_shape("com.example#GetUser", "smithy.api#http", {
    "method": "GET",
    "uri": "/users/{id}"
})

# Validate and serialize
doc.validate()
print(doc.to_json())
```
