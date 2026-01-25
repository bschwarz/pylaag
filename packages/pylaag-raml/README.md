# pylaag-raml

RAML document manipulation for Python.

## Overview

`pylaag-raml` provides comprehensive support for working with RAML 1.0 and 0.8 specifications, including:

- Document parsing and serialization (YAML)
- Resource and method management
- Type definition management
- Trait management
- Document validation

## Installation

```bash
pip install pylaag-raml
```

This will automatically install `pylaag-core` and `pyyaml` as dependencies.

## Quick Start

```python
from pylaag_raml import RAMLDocument

# Parse a RAML document
doc = RAMLDocument.from_yaml(raml_content)
doc.validate()

# Access document properties
print(doc.title)
print(doc.version)
print(doc.base_uri)

# Serialize back to YAML
yaml_output = doc.to_yaml()
```

## Features

### Document Management

```python
from pylaag_raml import RAMLDocument

# Create a new document
doc = RAMLDocument()

# Parse from YAML
doc = RAMLDocument.from_yaml(yaml_string)

# Validate document
doc.validate()  # Raises ValidationError if invalid

# Access properties
print(doc.title)
print(doc.version)
print(doc.base_uri)
```


### Resource Management

```python
from pylaag_raml import RAMLDocument, ResourceManager

doc = RAMLDocument()
resource_mgr = ResourceManager(doc)

# Add a resource
resource_mgr.add_resource('/users', {
    'displayName': 'Users',
    'description': 'User management endpoints'
})

# Add a method to a resource
resource_mgr.add_method('/users', 'get', {
    'description': 'List all users',
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

# Get a resource
resource = resource_mgr.get_resource('/users')

# Remove a method
resource_mgr.remove_method('/users', 'get')

# Remove a resource
resource_mgr.remove_resource('/users')
```

### Type Management

```python
from pylaag_raml import RAMLDocument, TypeManager

doc = RAMLDocument()
type_mgr = TypeManager(doc)

# Add a type definition
type_mgr.add_type('User', {
    'type': 'object',
    'properties': {
        'id': {
            'type': 'integer',
            'required': True
        },
        'name': {
            'type': 'string',
            'required': True
        },
        'email': {
            'type': 'string',
            'required': True
        }
    }
})

# Get a type
user_type = type_mgr.get_type('User')

# Remove a type
type_mgr.remove_type('User')
```


### Extension Properties

```python
from pylaag_raml import RAMLDocument

doc = RAMLDocument()

# Set extension property
doc.set_extension('x-api-id', 'my-api-123')

# Get extension property
api_id = doc.get_extension('x-api-id')

# Remove extension property
doc.remove_extension('x-api-id')
```

## API Reference

### Classes

#### RAMLDocument

Main class for working with RAML documents.

**Class Methods:**
- `from_yaml(yaml_str: str) -> RAMLDocument`: Parse from YAML string

**Methods:**
- `validate() -> None`: Validate the document structure
- `to_yaml() -> str`: Serialize to YAML string

**Properties:**
- `title: str`: The API title
- `version: str`: The API version
- `base_uri: str`: The base URI for the API

#### ResourceManager

Manages resources and methods in a RAML document.

**Methods:**
- `add_resource(path: str, resource: Optional[Dict] = None) -> None`
- `remove_resource(path: str) -> bool`
- `get_resource(path: str) -> Optional[Dict]`
- `add_method(path: str, method: str, method_def: Dict) -> None`
- `remove_method(path: str, method: str) -> bool`

#### TypeManager

Manages type definitions in a RAML document.

**Methods:**
- `add_type(name: str, type_def: Dict) -> None`
- `remove_type(name: str) -> bool`
- `get_type(name: str) -> Optional[Dict]`

## Requirements

- Python 3.10 or higher
- pylaag-core >= 0.1.0
- pyyaml >= 6.0.1

## License

MIT License - see LICENSE file for details

## Related Packages

- [pylaag-core](https://pypi.org/project/pylaag-core/) - Core utilities
- [pylaag-openapi](https://pypi.org/project/pylaag-openapi/) - OpenAPI support
- [pylaag-smithy](https://pypi.org/project/pylaag-smithy/) - Smithy support

## Contributing

Contributions are welcome! Please see the main repository for guidelines.

## Links

- [GitHub Repository](https://github.com/laag/laag-python)
- [Issue Tracker](https://github.com/laag/laag-python/issues)
- [Documentation](https://github.com/laag/laag-python#readme)
