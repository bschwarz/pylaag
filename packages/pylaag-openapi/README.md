# pylaag-openapi

OpenAPI/Swagger document manipulation for Python.

## Overview

`pylaag-openapi` provides comprehensive support for working with OpenAPI 3.0+ specifications, including:

- Document parsing and serialization (JSON and YAML)
- Path and operation management
- Component management (schemas, responses, parameters, etc.)
- Sample data generation from schemas
- Client code generation (Python, JavaScript, TypeScript)
- Curl command generation

## Installation

```bash
pip install pylaag-openapi
```

This will automatically install `pylaag-core` and `pyyaml` as dependencies.

## Quick Start

```python
from pylaag_openapi import OpenAPIDocument

# Parse an OpenAPI document
doc = OpenAPIDocument.from_yaml(yaml_content)
doc.validate()

# Access document properties
print(doc.info['title'])
print(doc.openapi_version)
print(doc.paths)

# Serialize back to YAML or JSON
yaml_output = doc.to_yaml()
json_output = doc.to_json()
```

## Features

### Document Management

```python
from pylaag_openapi import OpenAPIDocument

# Create a new document
doc = OpenAPIDocument()

# Parse from JSON
doc = OpenAPIDocument.from_json(json_string)

# Parse from YAML
doc = OpenAPIDocument.from_yaml(yaml_string)

# Validate document
doc.validate()  # Raises ValidationError if invalid
```


### Path and Operation Management

```python
from pylaag_openapi import OpenAPIDocument, PathManager

doc = OpenAPIDocument()
path_mgr = PathManager(doc)

# Add a path
path_mgr.add_path('/users', {})

# Add an operation
path_mgr.add_operation('/users', 'get', {
    'summary': 'List users',
    'responses': {
        '200': {
            'description': 'Success',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'array',
                        'items': {'$ref': '#/components/schemas/User'}
                    }
                }
            }
        }
    }
})

# Get an operation
operation = path_mgr.get_operation('/users', 'get')

# Remove an operation
path_mgr.remove_operation('/users', 'get')
```

### Component Management

```python
from pylaag_openapi import OpenAPIDocument, ComponentManager

doc = OpenAPIDocument()
comp_mgr = ComponentManager(doc)

# Add a schema component
comp_mgr.add_component('schemas', 'User', {
    'type': 'object',
    'properties': {
        'id': {'type': 'integer'},
        'name': {'type': 'string'},
        'email': {'type': 'string', 'format': 'email'}
    },
    'required': ['id', 'name', 'email']
})

# Get a component
user_schema = comp_mgr.get_component('schemas', 'User')

# Resolve a reference
resolved = comp_mgr.resolve_reference('#/components/schemas/User')

# Remove a component
comp_mgr.remove_component('schemas', 'User')
```


### Sample Generation

```python
from pylaag_openapi import OpenAPIDocument, SampleGenerator

doc = OpenAPIDocument.from_yaml(yaml_content)
sample_gen = SampleGenerator(doc)

# Generate sample from a schema
schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'age': {'type': 'integer', 'minimum': 0, 'maximum': 120},
        'email': {'type': 'string', 'format': 'email'}
    },
    'required': ['name', 'email']
}

sample = sample_gen.generate_from_schema(schema)
# Example output: {'name': 'abc', 'age': 42, 'email': 'user@example.com'}
```

### Code Generation

```python
from pylaag_openapi import OpenAPIDocument, CodeGenerator

doc = OpenAPIDocument.from_yaml(yaml_content)
code_gen = CodeGenerator(doc)

# Generate Python client
python_code = code_gen.generate_client('python')

# Generate JavaScript client
js_code = code_gen.generate_client('javascript')

# Generate TypeScript client
ts_code = code_gen.generate_client('typescript')
```

### Curl Command Generation

```python
from pylaag_openapi import OpenAPIDocument, CurlGenerator

doc = OpenAPIDocument.from_yaml(yaml_content)
curl_gen = CurlGenerator(doc)

# Generate curl command for an operation
curl_cmd = curl_gen.generate_curl(
    path='/users',
    method='post',
    base_url='https://api.example.com',
    include_sample_body=True
)

print(curl_cmd)
# Output: curl -X POST -H 'Content-Type: application/json' -d '...' 'https://api.example.com/users'
```


### Extension Properties

```python
from pylaag_openapi import OpenAPIDocument

doc = OpenAPIDocument()

# Set extension property
doc.set_extension('x-api-id', 'my-api-123')

# Get extension property
api_id = doc.get_extension('x-api-id')

# Remove extension property
doc.remove_extension('x-api-id')
```

## API Reference

### Classes

#### OpenAPIDocument

Main class for working with OpenAPI documents.

**Class Methods:**
- `from_json(json_str: str) -> OpenAPIDocument`: Parse from JSON string
- `from_yaml(yaml_str: str) -> OpenAPIDocument`: Parse from YAML string

**Methods:**
- `validate() -> None`: Validate the document structure
- `to_json(indent: int = 2) -> str`: Serialize to JSON string
- `to_yaml() -> str`: Serialize to YAML string

**Properties:**
- `openapi_version: str`: The OpenAPI version
- `info: Dict[str, Any]`: The info object
- `paths: Dict[str, Any]`: The paths object

#### PathManager

Manages paths and operations in an OpenAPI document.

**Methods:**
- `add_path(path: str, path_item: Optional[Dict] = None) -> None`
- `remove_path(path: str) -> bool`
- `get_path(path: str) -> Optional[Dict]`
- `add_operation(path: str, method: HttpMethod, operation: Dict) -> None`
- `remove_operation(path: str, method: HttpMethod) -> bool`
- `get_operation(path: str, method: HttpMethod) -> Optional[Dict]`

#### ComponentManager

Manages reusable components in an OpenAPI document.

**Methods:**
- `add_component(component_type: ComponentType, name: str, component: Dict) -> None`
- `remove_component(component_type: ComponentType, name: str) -> bool`
- `get_component(component_type: ComponentType, name: str) -> Optional[Dict]`
- `resolve_reference(ref: str) -> Optional[Dict]`


#### SampleGenerator

Generates sample data from OpenAPI schemas.

**Methods:**
- `generate_from_schema(schema: Dict, depth: int = 0, max_depth: int = 5) -> Any`

#### CodeGenerator

Generates client code from OpenAPI documents.

**Methods:**
- `generate_client(language: Language) -> str`: Generate client code in specified language

**Supported Languages:**
- `'python'`: Python client with requests library
- `'javascript'`: JavaScript client with fetch API
- `'typescript'`: TypeScript client with type annotations

#### CurlGenerator

Generates curl commands from OpenAPI operations.

**Methods:**
- `generate_curl(path: str, method: str, base_url: str = 'https://api.example.com', include_sample_body: bool = True) -> str`

## Requirements

- Python 3.10 or higher
- pylaag-core >= 0.1.0
- pyyaml >= 6.0.1

## License

MIT License - see LICENSE file for details

## Related Packages

- [pylaag-core](https://pypi.org/project/pylaag-core/) - Core utilities
- [pylaag-raml](https://pypi.org/project/pylaag-raml/) - RAML support
- [pylaag-smithy](https://pypi.org/project/pylaag-smithy/) - Smithy support

## Contributing

Contributions are welcome! Please see the main repository for guidelines.

## Links

- [GitHub Repository](https://github.com/laag/laag-python)
- [Issue Tracker](https://github.com/laag/laag-python/issues)
- [Documentation](https://github.com/laag/laag-python#readme)
