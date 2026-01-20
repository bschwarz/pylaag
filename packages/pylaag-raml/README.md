# pylaag-raml

RAML document manipulation for Python.

## Overview

This package provides support for working with RAML 1.0 and 0.8 specifications:

- Parse and serialize RAML documents
- Manage resources and methods
- Manage type definitions
- Validate RAML documents

## Installation

```bash
pip install pylaag-raml
```

## Usage

### Basic Document Operations

```python
from pylaag_raml import RAMLDocument

# Parse from YAML
doc = RAMLDocument.from_yaml(raml_content)

# Validate
doc.validate()

# Access properties
print(doc.title)
print(doc.version)
print(doc.base_uri)

# Serialize
yaml_output = doc.to_yaml()
```

### Resource Management

```python
from pylaag_raml import ResourceManager

resource_mgr = ResourceManager(doc)

# Add a resource
resource_mgr.add_resource('/users')

# Add a method to a resource
resource_mgr.add_method('/users', 'get', {
    'description': 'List users',
    'responses': {
        '200': {
            'body': {
                'application/json': {
                    'type': 'User[]'
                }
            }
        }
    }
})
```

### Type Management

```python
from pylaag_raml import TypeManager

type_mgr = TypeManager(doc)

# Add a type definition
type_mgr.add_type('User', {
    'type': 'object',
    'properties': {
        'id': 'integer',
        'name': 'string'
    }
})

# Get a type definition
user_type = type_mgr.get_type('User')
```

## Requirements

- Python 3.10 or higher
- pylaag-core
- PyYAML

## License

MIT License
