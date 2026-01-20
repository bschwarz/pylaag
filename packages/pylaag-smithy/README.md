# pylaag-smithy

Smithy document manipulation for Python.

## Overview

This package provides support for working with Smithy 2.0 specifications:

- Parse and serialize Smithy documents (JSON AST format)
- Manage shapes and traits
- Manage operations
- Validate Smithy documents

## Installation

```bash
pip install pylaag-smithy
```

## Usage

### Basic Document Operations

```python
from pylaag_smithy import SmithyDocument

# Parse from JSON
doc = SmithyDocument.from_json(smithy_json)

# Validate
doc.validate()

# Access properties
print(doc.smithy_version)
print(doc.shapes)

# Serialize
json_output = doc.to_json()
```

### Shape Management

```python
from pylaag_smithy import ShapeManager

shape_mgr = ShapeManager(doc)

# Add a structure shape
shape_mgr.add_shape('com.example#User', 'structure', {
    'members': {
        'id': {'target': 'smithy.api#Integer'},
        'name': {'target': 'smithy.api#String'}
    }
})

# Get a shape
user_shape = shape_mgr.get_shape('com.example#User')

# Resolve a target
target_shape = shape_mgr.resolve_target('smithy.api#String')
```

### Trait Management

```python
from pylaag_smithy import TraitManager

trait_mgr = TraitManager(doc)

# Add a trait to a shape
trait_mgr.add_trait_to_shape(
    'com.example#ListUsers',
    'smithy.api#http',
    {
        'method': 'GET',
        'uri': '/users'
    }
)

# Get a trait
http_trait = trait_mgr.get_trait('com.example#ListUsers', 'smithy.api#http')
```

### Operation Management

```python
from pylaag_smithy import OperationManager

op_mgr = OperationManager(doc)

# Add an operation
op_mgr.add_operation(
    'com.example#ListUsers',
    output_shape='com.example#UserList'
)

# Get an operation
operation = op_mgr.get_operation('com.example#ListUsers')
```

## Requirements

- Python 3.10 or higher
- pylaag-core

## License

MIT License
