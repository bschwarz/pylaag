# pylaag-smithy

Smithy document manipulation for Python.

## Overview

`pylaag-smithy` provides comprehensive support for working with Smithy 2.0 specifications, including:

- Document parsing and serialization (JSON)
- Shape management (structures, operations, services)
- Trait management
- Operation management
- Document validation

## Installation

```bash
pip install pylaag-smithy
```

This will automatically install `pylaag-core` as a dependency.

## Quick Start

```python
from pylaag_smithy import SmithyDocument

# Parse a Smithy document
doc = SmithyDocument.from_json(smithy_json)
doc.validate()

# Access document properties
print(doc.smithy_version)
print(doc.shapes)

# Serialize back to JSON
json_output = doc.to_json()
```

## Features

### Document Management

```python
from pylaag_smithy import SmithyDocument

# Create a new document
doc = SmithyDocument()

# Parse from JSON
doc = SmithyDocument.from_json(json_string)

# Validate document
doc.validate()  # Raises ValidationError if invalid

# Access properties
print(doc.smithy_version)
print(doc.shapes)
```


### Shape Management

```python
from pylaag_smithy import SmithyDocument, ShapeManager

doc = SmithyDocument()
shape_mgr = ShapeManager(doc)

# Add a structure shape
shape_mgr.add_shape('com.example#User', 'structure', {
    'members': {
        'id': {'target': 'smithy.api#Integer'},
        'name': {'target': 'smithy.api#String'},
        'email': {'target': 'smithy.api#String'}
    }
})

# Add a list shape
shape_mgr.add_shape('com.example#UserList', 'list', {
    'member': {'target': 'com.example#User'}
})

# Get a shape
user_shape = shape_mgr.get_shape('com.example#User')

# Resolve a target
resolved = shape_mgr.resolve_target('com.example#User')

# Remove a shape
shape_mgr.remove_shape('com.example#User')
```

### Trait Management

```python
from pylaag_smithy import SmithyDocument, TraitManager

doc = SmithyDocument()
trait_mgr = TraitManager(doc)

# Add a trait to a shape
trait_mgr.add_trait_to_shape('com.example#ListUsers', 'smithy.api#http', {
    'method': 'GET',
    'uri': '/users'
})

# Add documentation trait
trait_mgr.add_trait_to_shape('com.example#User', 'smithy.api#documentation', 
    'Represents a user in the system')

# Get a trait
http_trait = trait_mgr.get_trait('com.example#ListUsers', 'smithy.api#http')

# Remove a trait
trait_mgr.remove_trait_from_shape('com.example#ListUsers', 'smithy.api#http')
```


### Operation Management

```python
from pylaag_smithy import SmithyDocument, OperationManager

doc = SmithyDocument()
op_mgr = OperationManager(doc)

# Add an operation
op_mgr.add_operation(
    'com.example#ListUsers',
    input_shape='com.example#ListUsersInput',
    output_shape='com.example#ListUsersOutput',
    errors=['com.example#ValidationError']
)

# Get an operation
operation = op_mgr.get_operation('com.example#ListUsers')

# Remove an operation
op_mgr.remove_operation('com.example#ListUsers')
```

### Extension Properties

```python
from pylaag_smithy import SmithyDocument

doc = SmithyDocument()

# Set extension property
doc.set_extension('x-api-id', 'my-api-123')

# Get extension property
api_id = doc.get_extension('x-api-id')

# Remove extension property
doc.remove_extension('x-api-id')
```

## API Reference

### Classes

#### SmithyDocument

Main class for working with Smithy documents.

**Class Methods:**
- `from_json(json_str: str) -> SmithyDocument`: Parse from JSON string

**Methods:**
- `validate() -> None`: Validate the document structure
- `to_json(indent: int = 2) -> str`: Serialize to JSON string

**Properties:**
- `smithy_version: str`: The Smithy version
- `shapes: Dict[str, Any]`: The shapes in the document

#### ShapeManager

Manages shapes in a Smithy document.

**Methods:**
- `add_shape(shape_id: str, shape_type: str, definition: Dict) -> None`
- `remove_shape(shape_id: str) -> bool`
- `get_shape(shape_id: str) -> Optional[Dict]`
- `resolve_target(target: str) -> Optional[Dict]`


#### TraitManager

Manages traits applied to shapes in a Smithy document.

**Methods:**
- `add_trait_to_shape(shape_id: str, trait_id: str, trait_value: Any) -> None`
- `remove_trait_from_shape(shape_id: str, trait_id: str) -> bool`
- `get_trait(shape_id: str, trait_id: str) -> Optional[Any]`

#### OperationManager

Manages operations in a Smithy document.

**Methods:**
- `add_operation(operation_id: str, input_shape: Optional[str] = None, output_shape: Optional[str] = None, errors: Optional[List[str]] = None) -> None`
- `remove_operation(operation_id: str) -> bool`
- `get_operation(operation_id: str) -> Optional[Dict]`

## Requirements

- Python 3.10 or higher
- pylaag-core >= 0.1.0

## License

MIT License - see LICENSE file for details

## Related Packages

- [pylaag-core](https://pypi.org/project/pylaag-core/) - Core utilities
- [pylaag-openapi](https://pypi.org/project/pylaag-openapi/) - OpenAPI support
- [pylaag-raml](https://pypi.org/project/pylaag-raml/) - RAML support

## Contributing

Contributions are welcome! Please see the main repository for guidelines.

## Links

- [GitHub Repository](https://github.com/laag/laag-python)
- [Issue Tracker](https://github.com/laag/laag-python/issues)
- [Documentation](https://github.com/laag/laag-python#readme)
