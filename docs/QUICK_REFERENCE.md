# Laag Python Quick Reference

A quick reference guide for common tasks with the laag Python library.

## Installation

```bash
pip install pylaag-openapi pylaag-raml pylaag-smithy
```

## OpenAPI Quick Reference

### Load and Save

```python
from pylaag.openapi import OpenAPIDocument

# Load
doc = OpenAPIDocument.from_yaml(open('api.yaml').read())
doc = OpenAPIDocument.from_json(open('api.json').read())

# Save
open('api.yaml', 'w').write(doc.to_yaml())
open('api.json', 'w').write(doc.to_json())
```

### Create New Document

```python
doc = OpenAPIDocument()  # Creates minimal valid document
doc.validate()  # Always validate before saving
```

### Add Paths and Operations

```python
from pylaag.openapi import PathManager

path_mgr = PathManager(doc)

# Simple GET
path_mgr.add_operation('/users', 'get', {
    'summary': 'List users',
    'responses': {'200': {'description': 'Success'}}
})

# POST with body
path_mgr.add_operation('/users', 'post', {
    'summary': 'Create user',
    'requestBody': {
        'content': {
            'application/json': {
                'schema': {'$ref': '#/components/schemas/User'}
            }
        }
    },
    'responses': {'201': {'description': 'Created'}}
})

# With path parameters
path_mgr.add_operation('/users/{id}', 'get', {
    'parameters': [
        {'name': 'id', 'in': 'path', 'required': True, 'schema': {'type': 'string'}}
    ],
    'responses': {'200': {'description': 'Success'}}
})
```

### Manage Components

```python
from pylaag.openapi import ComponentManager

comp_mgr = ComponentManager(doc)

# Add schema
comp_mgr.add_component('schemas', 'User', {
    'type': 'object',
    'properties': {
        'id': {'type': 'string'},
        'name': {'type': 'string'}
    }
})

# Get schema
schema = comp_mgr.get_component('schemas', 'User')

# Resolve reference
resolved = comp_mgr.resolve_reference('#/components/schemas/User')
```

### Generate Samples

```python
from pylaag.openapi import SampleGenerator

sample_gen = SampleGenerator(doc)
sample = sample_gen.generate_from_schema({
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'age': {'type': 'integer', 'minimum': 18}
    }
})
```

### Generate Code

```python
from pylaag.openapi import CodeGenerator

code_gen = CodeGenerator(doc)
python_client = code_gen.generate_client('python')
js_client = code_gen.generate_client('javascript')
ts_client = code_gen.generate_client('typescript')
```

### Generate Curl

```python
from pylaag.openapi import CurlGenerator

curl_gen = CurlGenerator(doc)
curl = curl_gen.generate_curl('/users', 'post', base_url='https://api.example.com')
```

### Extension Properties

```python
# Set
doc.set_extension('x-internal', True)

# Get
value = doc.get_extension('x-internal')

# Remove
doc.remove_extension('x-internal')
```

## RAML Quick Reference

### Load and Save

```python
from pylaag.raml import RAMLDocument

# Load
doc = RAMLDocument.from_yaml(open('api.raml').read())

# Save
open('api.raml', 'w').write(doc.to_yaml())
```

### Create New Document

```python
doc = RAMLDocument()
doc.validate()
```

### Add Resources

```python
from pylaag.raml import ResourceManager

resource_mgr = ResourceManager(doc)

# Add resource
resource_mgr.add_resource('/users')

# Add method
resource_mgr.add_method('/users', 'get', {
    'description': 'List users',
    'responses': {
        '200': {
            'body': {
                'application/json': {'type': 'User[]'}
            }
        }
    }
})
```

### Manage Types

```python
from pylaag.raml import TypeManager

type_mgr = TypeManager(doc)

# Add type
type_mgr.add_type('User', {
    'type': 'object',
    'properties': {
        'id': {'type': 'string'},
        'name': {'type': 'string'}
    }
})

# Get type
user_type = type_mgr.get_type('User')
```

## Smithy Quick Reference

### Load and Save

```python
from pylaag.smithy import SmithyDocument

# Load
doc = SmithyDocument.from_json(open('model.json').read())

# Save
open('model.json', 'w').write(doc.to_json())
```

### Create New Document

```python
doc = SmithyDocument()
doc.validate()
```

### Add Shapes

```python
from pylaag.smithy import ShapeManager

shape_mgr = ShapeManager(doc)

# Add structure
shape_mgr.add_shape('com.example#User', 'structure', {
    'members': {
        'id': {'target': 'smithy.api#String'},
        'name': {'target': 'smithy.api#String'}
    }
})

# Add list
shape_mgr.add_shape('com.example#UserList', 'list', {
    'member': {'target': 'com.example#User'}
})

# Get shape
shape = shape_mgr.get_shape('com.example#User')
```

### Add Traits

```python
from pylaag.smithy import TraitManager

trait_mgr = TraitManager(doc)

# Add HTTP trait
trait_mgr.add_trait_to_shape('com.example#GetUser', 'smithy.api#http', {
    'method': 'GET',
    'uri': '/users/{id}'
})

# Get trait
trait = trait_mgr.get_trait('com.example#GetUser', 'smithy.api#http')
```

### Add Operations

```python
from pylaag.smithy import OperationManager

op_mgr = OperationManager(doc)

# Add operation
op_mgr.add_operation(
    'com.example#ListUsers',
    input_shape='com.example#ListUsersInput',
    output_shape='com.example#ListUsersOutput'
)
```

## Error Handling

```python
from pylaag.core import ValidationError, ParseError, NotFoundError

try:
    doc.validate()
except ValidationError as e:
    print(f"Invalid: {e}")
except ParseError as e:
    print(f"Parse error: {e}")
except NotFoundError as e:
    print(f"Not found: {e}")
```

## Utility Functions

```python
from pylaag.core import get_nested, set_nested, delete_nested

data = {'a': {'b': {'c': 1}}}

# Get
value = get_nested(data, 'a.b.c')  # Returns 1

# Set
set_nested(data, 'a.b.d', 2)  # Creates {'a': {'b': {'c': 1, 'd': 2}}}

# Delete
deleted = delete_nested(data, 'a.b.c')  # Returns True
```

## Common Patterns

### Validate Before Saving

```python
try:
    doc.validate()
    with open('api.yaml', 'w') as f:
        f.write(doc.to_yaml())
except ValidationError as e:
    print(f"Cannot save invalid document: {e}")
```

### Build CRUD API

```python
from pylaag.openapi import OpenAPIDocument, PathManager, ComponentManager

doc = OpenAPIDocument()
path_mgr = PathManager(doc)
comp_mgr = ComponentManager(doc)

# Add schema
comp_mgr.add_component('schemas', 'User', {...})

# Add endpoints
path_mgr.add_operation('/users', 'get', {...})      # List
path_mgr.add_operation('/users', 'post', {...})     # Create
path_mgr.add_operation('/users/{id}', 'get', {...}) # Read
path_mgr.add_operation('/users/{id}', 'put', {...}) # Update
path_mgr.add_operation('/users/{id}', 'delete', {...}) # Delete
```

### Convert Formats

```python
# YAML to JSON
doc = OpenAPIDocument.from_yaml(yaml_content)
json_output = doc.to_json()

# JSON to YAML
doc = OpenAPIDocument.from_json(json_content)
yaml_output = doc.to_yaml()
```

### Generate Test Data

```python
from pylaag.openapi import SampleGenerator, ComponentManager

sample_gen = SampleGenerator(doc)
comp_mgr = ComponentManager(doc)

# Get schema and generate sample
schema = comp_mgr.get_component('schemas', 'User')
test_user = sample_gen.generate_from_schema(schema)

# Use in tests
import requests
response = requests.post('https://api.test.com/users', json=test_user)
```

## Type Hints

All functions and methods have full type hints:

```python
from typing import Dict, Any, Optional
from pylaag.openapi import OpenAPIDocument

def process_api(doc: OpenAPIDocument) -> Dict[str, Any]:
    doc.validate()
    return doc.to_dict()
```

## Properties vs Methods

```python
# Properties (no parentheses)
version = doc.openapi_version
info = doc.info
paths = doc.paths

# Methods (with parentheses)
doc.validate()
yaml_str = doc.to_yaml()
dict_repr = doc.to_dict()
```

## Cheat Sheet

| Task              | OpenAPI                               | RAML                                  | Smithy                                |
| ----------------- | ------------------------------------- | ------------------------------------- | ------------------------------------- |
| Load              | `from_yaml()` / `from_json()`         | `from_yaml()`                         | `from_json()`                         |
| Save              | `to_yaml()` / `to_json()`             | `to_yaml()`                           | `to_json()`                           |
| Validate          | `validate()`                          | `validate()`                          | `validate()`                          |
| Add Path/Resource | `PathManager.add_path()`              | `ResourceManager.add_resource()`      | `ShapeManager.add_shape()`            |
| Add Operation     | `PathManager.add_operation()`         | `ResourceManager.add_method()`        | `OperationManager.add_operation()`    |
| Add Component     | `ComponentManager.add_component()`    | `TypeManager.add_type()`              | `ShapeManager.add_shape()`            |
| Extension Props   | `set_extension()` / `get_extension()` | `set_extension()` / `get_extension()` | `set_extension()` / `get_extension()` |

## More Information

- [Full API Reference](API_REFERENCE.md)
- [User Guide with Examples](USER_GUIDE.md)
- [GitHub Repository](https://github.com/laag/laag-python)
