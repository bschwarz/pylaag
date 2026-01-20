# pylaag-openapi

OpenAPI/Swagger document manipulation for Python.

## Overview

This package provides comprehensive support for working with OpenAPI 3.0+ documents:

- Parse and serialize OpenAPI documents (JSON and YAML)
- Manage paths, operations, and components
- Generate sample data from schemas
- Generate client code in multiple languages
- Generate curl commands for testing

## Installation

```bash
pip install pylaag-openapi
```

## Usage

### Basic Document Operations

```python
from pylaag_openapi import OpenAPIDocument

# Parse from YAML
doc = OpenAPIDocument.from_yaml(yaml_content)

# Parse from JSON
doc = OpenAPIDocument.from_json(json_content)

# Validate
doc.validate()

# Access properties
print(doc.info['title'])
print(doc.openapi_version)
print(doc.paths)

# Serialize
yaml_output = doc.to_yaml()
json_output = doc.to_json()
```

### Path and Operation Management

```python
from pylaag_openapi import OpenAPIDocument, PathManager

doc = OpenAPIDocument()
path_mgr = PathManager(doc)

# Add a path
path_mgr.add_path('/users')

# Add an operation
path_mgr.add_operation('/users', 'get', {
    'summary': 'List users',
    'responses': {
        '200': {
            'description': 'Success'
        }
    }
})

# Remove an operation
path_mgr.remove_operation('/users', 'get')
```

### Component Management

```python
from pylaag_openapi import ComponentManager

comp_mgr = ComponentManager(doc)

# Add a schema component
comp_mgr.add_component('schemas', 'User', {
    'type': 'object',
    'properties': {
        'id': {'type': 'integer'},
        'name': {'type': 'string'}
    }
})

# Resolve a reference
schema = comp_mgr.resolve_reference('#/components/schemas/User')
```

### Sample Generation

```python
from pylaag_openapi import SampleGenerator

sample_gen = SampleGenerator(doc)

schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'age': {'type': 'integer', 'minimum': 0, 'maximum': 120}
    }
}

sample = sample_gen.generate_from_schema(schema)
# Returns: {'name': 'abc...', 'age': 42}
```

### Code Generation

```python
from pylaag_openapi import CodeGenerator

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
from pylaag_openapi import CurlGenerator

curl_gen = CurlGenerator(doc)

# Generate curl command
curl_cmd = curl_gen.generate_curl(
    '/users',
    'get',
    base_url='https://api.example.com'
)
print(curl_cmd)
```

## Requirements

- Python 3.10 or higher
- pylaag-core
- PyYAML

## License

MIT License
