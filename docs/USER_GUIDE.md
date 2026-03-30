# Laag Python User Guide

A comprehensive guide to using the laag Python library for working with API specification formats.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Working with OpenAPI](#working-with-openapi)
4. [Working with RAML](#working-with-raml)
5. [Working with Smithy](#working-with-smithy)
6. [Advanced Features](#advanced-features)
7. [Best Practices](#best-practices)

---

## Installation

Install the laag packages using pip:

```bash
# Install all packages
pip install pylaag-core pylaag-openapi pylaag-raml pylaag-smithy

# Or install only what you need
pip install pylaag-openapi  # For OpenAPI only
pip install pylaag-raml     # For RAML only
pip install pylaag-smithy   # For Smithy only
```

---

## Quick Start

### OpenAPI Example

```python
from pylaag.openapi import OpenAPIDocument, PathManager

# Create a new OpenAPI document
doc = OpenAPIDocument()

# Add a path and operation
path_mgr = PathManager(doc)
path_mgr.add_operation('/users', 'get', {
    'summary': 'List all users',
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

# Validate and export
doc.validate()
print(doc.to_yaml())
```

---

## Working with OpenAPI

### Creating and Loading Documents

#### Create a New Document

```python
from pylaag.openapi import OpenAPIDocument

# Create with defaults
doc = OpenAPIDocument()

# Create with custom info
doc = OpenAPIDocument({
    'openapi': '3.0.0',
    'info': {
        'title': 'My API',
        'version': '1.0.0',
        'description': 'A sample API'
    },
    'paths': {}
})
```

#### Load from File

```python
from pylaag.openapi import OpenAPIDocument

# Load from YAML
with open('api.yaml', 'r') as f:
    yaml_content = f.read()
    doc = OpenAPIDocument.from_yaml(yaml_content)

# Load from JSON
with open('api.json', 'r') as f:
    json_content = f.read()
    doc = OpenAPIDocument.from_json(json_content)
```

#### Save to File

```python
# Save as YAML
with open('output.yaml', 'w') as f:
    f.write(doc.to_yaml())

# Save as JSON
with open('output.json', 'w') as f:
    f.write(doc.to_json(indent=2))
```

### Managing Paths and Operations

```python
from pylaag.openapi import OpenAPIDocument, PathManager

doc = OpenAPIDocument()
path_mgr = PathManager(doc)

# Add a simple GET endpoint
path_mgr.add_operation('/users', 'get', {
    'summary': 'Get all users',
    'responses': {
        '200': {'description': 'Success'}
    }
})

# Add a POST endpoint with request body
path_mgr.add_operation('/users', 'post', {
    'summary': 'Create a user',
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {'$ref': '#/components/schemas/User'}
            }
        }
    },
    'responses': {
        '201': {'description': 'Created'},
        '400': {'description': 'Bad Request'}
    }
})

# Add a path with parameters
path_mgr.add_operation('/users/{userId}', 'get', {
    'summary': 'Get user by ID',
    'parameters': [
        {
            'name': 'userId',
            'in': 'path',
            'required': True,
            'schema': {'type': 'string'}
        }
    ],
    'responses': {
        '200': {'description': 'Success'},
        '404': {'description': 'Not Found'}
    }
})

# Remove an operation
path_mgr.remove_operation('/users', 'post')

# Remove an entire path
path_mgr.remove_path('/users/{userId}')
```

### Managing Components

```python
from pylaag.openapi import OpenAPIDocument, ComponentManager

doc = OpenAPIDocument()
comp_mgr = ComponentManager(doc)

# Add a schema component
comp_mgr.add_component('schemas', 'User', {
    'type': 'object',
    'required': ['id', 'name', 'email'],
    'properties': {
        'id': {'type': 'string', 'format': 'uuid'},
        'name': {'type': 'string'},
        'email': {'type': 'string', 'format': 'email'},
        'age': {'type': 'integer', 'minimum': 0}
    }
})

# Add a response component
comp_mgr.add_component('responses', 'NotFound', {
    'description': 'Resource not found',
    'content': {
        'application/json': {
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})

# Add a parameter component
comp_mgr.add_component('parameters', 'PageParam', {
    'name': 'page',
    'in': 'query',
    'schema': {'type': 'integer', 'default': 1}
})

# Get a component
user_schema = comp_mgr.get_component('schemas', 'User')

# Resolve a reference
resolved = comp_mgr.resolve_reference('#/components/schemas/User')

# Remove a component
comp_mgr.remove_component('schemas', 'User')
```

### Generating Sample Data

```python
from pylaag.openapi import OpenAPIDocument, ComponentManager, SampleGenerator

doc = OpenAPIDocument()
comp_mgr = ComponentManager(doc)

# Define a schema
comp_mgr.add_component('schemas', 'User', {
    'type': 'object',
    'required': ['name', 'email'],
    'properties': {
        'name': {'type': 'string'},
        'email': {'type': 'string', 'format': 'email'},
        'age': {'type': 'integer', 'minimum': 18, 'maximum': 100},
        'tags': {
            'type': 'array',
            'items': {'type': 'string'},
            'minItems': 1,
            'maxItems': 5
        }
    }
})

# Generate sample data
sample_gen = SampleGenerator(doc)
user_schema = comp_mgr.get_component('schemas', 'User')
sample = sample_gen.generate_from_schema(user_schema)

print(sample)
# Output: {'name': 'AbCdEfG', 'email': 'user@example.com', 'age': 42, 'tags': ['xyz', 'abc']}
```

### Generating Client Code

```python
from pylaag.openapi import OpenAPIDocument, PathManager, CodeGenerator

doc = OpenAPIDocument()
path_mgr = PathManager(doc)

# Add some operations
path_mgr.add_operation('/users', 'get', {
    'operationId': 'list_users',
    'summary': 'List all users'
})

path_mgr.add_operation('/users/{userId}', 'get', {
    'operationId': 'get_user',
    'summary': 'Get user by ID',
    'parameters': [
        {'name': 'userId', 'in': 'path', 'required': True, 'schema': {'type': 'string'}}
    ]
})

# Generate Python client
code_gen = CodeGenerator(doc)
python_code = code_gen.generate_client('python')
print(python_code)

# Generate JavaScript client
js_code = code_gen.generate_client('javascript')

# Generate TypeScript client
ts_code = code_gen.generate_client('typescript')

# Save to file
with open('api_client.py', 'w') as f:
    f.write(python_code)
```

### Generating Curl Commands

```python
from pylaag.openapi import OpenAPIDocument, PathManager, CurlGenerator

doc = OpenAPIDocument()
path_mgr = PathManager(doc)

# Add an operation
path_mgr.add_operation('/users', 'post', {
    'summary': 'Create user',
    'requestBody': {
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'email': {'type': 'string'}
                    }
                }
            }
        }
    },
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'schema': {'type': 'string'}}
    ]
})

# Generate curl command
curl_gen = CurlGenerator(doc)
curl_cmd = curl_gen.generate_curl(
    '/users',
    'post',
    base_url='https://api.example.com',
    include_sample_body=True
)

print(curl_cmd)
# Output:
# curl -X POST \
#   -H 'Authorization: <value>' \
#   -H 'Content-Type: application/json' \
#   -d '{"name": "xyz", "email": "user@example.com"}' \
#   'https://api.example.com/users'
```

### Working with Extension Properties

```python
from pylaag.openapi import OpenAPIDocument

doc = OpenAPIDocument()

# Add extension properties
doc.set_extension('x-internal', True)
doc.set_extension('x-rate-limit', {'requests': 100, 'period': 'hour'})

# Get extension properties
is_internal = doc.get_extension('x-internal')
rate_limit = doc.get_extension('x-rate-limit')

# Remove extension properties
doc.remove_extension('x-internal')

# Extension properties are preserved during serialization
yaml_output = doc.to_yaml()
```

---

## Working with RAML

### Creating and Loading Documents

```python
from pylaag.raml import RAMLDocument

# Create a new RAML document
doc = RAMLDocument()

# Load from YAML
with open('api.raml', 'r') as f:
    yaml_content = f.read()
    doc = RAMLDocument.from_yaml(yaml_content)

# Save to file
with open('output.raml', 'w') as f:
    f.write(doc.to_yaml())
```

### Managing Resources and Methods

```python
from pylaag.raml import RAMLDocument, ResourceManager

doc = RAMLDocument()
resource_mgr = ResourceManager(doc)

# Add a resource
resource_mgr.add_resource('/users', {
    'displayName': 'Users',
    'description': 'User management'
})

# Add methods to the resource
resource_mgr.add_method('/users', 'get', {
    'description': 'Get all users',
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

resource_mgr.add_method('/users', 'post', {
    'description': 'Create a user',
    'body': {
        'application/json': {
            'type': 'User'
        }
    },
    'responses': {
        '201': {'description': 'Created'}
    }
})

# Add nested resource
resource_mgr.add_resource('/users/{userId}', {
    'uriParameters': {
        'userId': {'type': 'string'}
    }
})

resource_mgr.add_method('/users/{userId}', 'get', {
    'description': 'Get user by ID'
})

# Remove a method
resource_mgr.remove_method('/users', 'post')

# Remove a resource
resource_mgr.remove_resource('/users/{userId}')
```

### Managing Types

```python
from pylaag.raml import RAMLDocument, TypeManager

doc = RAMLDocument()
type_mgr = TypeManager(doc)

# Add a type definition
type_mgr.add_type('User', {
    'type': 'object',
    'properties': {
        'id': {'type': 'string'},
        'name': {'type': 'string', 'required': True},
        'email': {'type': 'string', 'required': True},
        'age': {'type': 'integer', 'minimum': 0}
    }
})

# Add an array type
type_mgr.add_type('UserList', {
    'type': 'array',
    'items': 'User'
})

# Add an enum type
type_mgr.add_type('Status', {
    'type': 'string',
    'enum': ['active', 'inactive', 'pending']
})

# Get a type
user_type = type_mgr.get_type('User')

# Remove a type
type_mgr.remove_type('Status')
```

### Complete RAML Example

```python
from pylaag.raml import RAMLDocument, ResourceManager, TypeManager

# Create document
doc = RAMLDocument({
    '#%RAML': '1.0',
    'title': 'User API',
    'version': 'v1',
    'baseUri': 'https://api.example.com/{version}',
    'mediaType': 'application/json'
})

# Define types
type_mgr = TypeManager(doc)
type_mgr.add_type('User', {
    'type': 'object',
    'properties': {
        'id': {'type': 'string'},
        'name': {'type': 'string', 'required': True},
        'email': {'type': 'string', 'required': True}
    }
})

# Define resources
resource_mgr = ResourceManager(doc)
resource_mgr.add_resource('/users')
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

# Validate and save
doc.validate()
with open('api.raml', 'w') as f:
    f.write(doc.to_yaml())
```

---

## Working with Smithy

### Creating and Loading Documents

```python
from pylaag.smithy import SmithyDocument

# Create a new Smithy document
doc = SmithyDocument()

# Load from JSON
with open('model.json', 'r') as f:
    json_content = f.read()
    doc = SmithyDocument.from_json(json_content)

# Save to file
with open('output.json', 'w') as f:
    f.write(doc.to_json(indent=2))
```

### Managing Shapes

```python
from pylaag.smithy import SmithyDocument, ShapeManager

doc = SmithyDocument()
shape_mgr = ShapeManager(doc)

# Add a structure shape
shape_mgr.add_shape('com.example#User', 'structure', {
    'members': {
        'id': {'target': 'smithy.api#String'},
        'name': {'target': 'smithy.api#String'},
        'email': {'target': 'smithy.api#String'},
        'age': {'target': 'smithy.api#Integer'}
    }
})

# Add a list shape
shape_mgr.add_shape('com.example#UserList', 'list', {
    'member': {'target': 'com.example#User'}
})

# Add a service shape
shape_mgr.add_shape('com.example#UserService', 'service', {
    'version': '2024-01-01',
    'operations': [
        {'target': 'com.example#ListUsers'},
        {'target': 'com.example#GetUser'}
    ]
})

# Get a shape
user_shape = shape_mgr.get_shape('com.example#User')

# Resolve a target
resolved = shape_mgr.resolve_target('com.example#User')

# Remove a shape
shape_mgr.remove_shape('com.example#UserList')
```

### Managing Traits

```python
from pylaag.smithy import SmithyDocument, ShapeManager, TraitManager

doc = SmithyDocument()
shape_mgr = ShapeManager(doc)
trait_mgr = TraitManager(doc)

# Add a shape
shape_mgr.add_shape('com.example#GetUser', 'operation', {
    'input': {'target': 'com.example#GetUserInput'},
    'output': {'target': 'com.example#GetUserOutput'}
})

# Add HTTP trait
trait_mgr.add_trait_to_shape('com.example#GetUser', 'smithy.api#http', {
    'method': 'GET',
    'uri': '/users/{userId}'
})

# Add readonly trait
trait_mgr.add_trait_to_shape('com.example#GetUser', 'smithy.api#readonly', {})

# Get a trait
http_trait = trait_mgr.get_trait('com.example#GetUser', 'smithy.api#http')

# Remove a trait
trait_mgr.remove_trait_from_shape('com.example#GetUser', 'smithy.api#readonly')
```

### Managing Operations

```python
from pylaag.smithy import SmithyDocument, ShapeManager, OperationManager

doc = SmithyDocument()
shape_mgr = ShapeManager(doc)
op_mgr = OperationManager(doc)

# Define input/output shapes
shape_mgr.add_shape('com.example#ListUsersInput', 'structure', {
    'members': {
        'limit': {'target': 'smithy.api#Integer'}
    }
})

shape_mgr.add_shape('com.example#ListUsersOutput', 'structure', {
    'members': {
        'users': {'target': 'com.example#UserList'}
    }
})

# Add an operation
op_mgr.add_operation(
    'com.example#ListUsers',
    input_shape='com.example#ListUsersInput',
    output_shape='com.example#ListUsersOutput'
)

# Add operation with errors
op_mgr.add_operation(
    'com.example#GetUser',
    input_shape='com.example#GetUserInput',
    output_shape='com.example#GetUserOutput',
    errors=['com.example#UserNotFound', 'com.example#InvalidRequest']
)

# Get an operation
operation = op_mgr.get_operation('com.example#ListUsers')

# Remove an operation
op_mgr.remove_operation('com.example#GetUser')
```

### Complete Smithy Example

```python
from pylaag.smithy import SmithyDocument, ShapeManager, TraitManager, OperationManager

# Create document
doc = SmithyDocument({
    'smithy': '2.0',
    'shapes': {}
})

shape_mgr = ShapeManager(doc)
trait_mgr = TraitManager(doc)
op_mgr = OperationManager(doc)

# Define service
shape_mgr.add_shape('com.example#UserService', 'service', {
    'version': '2024-01-01',
    'operations': [{'target': 'com.example#ListUsers'}]
})

# Define structures
shape_mgr.add_shape('com.example#User', 'structure', {
    'members': {
        'id': {'target': 'smithy.api#String'},
        'name': {'target': 'smithy.api#String'}
    }
})

shape_mgr.add_shape('com.example#UserList', 'list', {
    'member': {'target': 'com.example#User'}
})

# Define operation
op_mgr.add_operation(
    'com.example#ListUsers',
    output_shape='com.example#UserList'
)

# Add HTTP trait
trait_mgr.add_trait_to_shape('com.example#ListUsers', 'smithy.api#http', {
    'method': 'GET',
    'uri': '/users'
})

# Validate and save
doc.validate()
with open('model.json', 'w') as f:
    f.write(doc.to_json(indent=2))
```

---

## Advanced Features

### Error Handling

```python
from pylaag.core import ValidationError, ParseError, NotFoundError
from pylaag.openapi import OpenAPIDocument

try:
    # Parse invalid JSON
    doc = OpenAPIDocument.from_json('invalid json')
except ParseError as e:
    print(f"Parse error: {e}")
    print(f"Context: {e.context}")

try:
    # Validate invalid document
    doc = OpenAPIDocument({'openapi': '3.0.0'})  # Missing required fields
    doc.validate()
except ValidationError as e:
    print(f"Validation error: {e}")

try:
    # Access non-existent component
    from pylaag.openapi import ComponentManager
    comp_mgr = ComponentManager(doc)
    schema = comp_mgr.get_component('schemas', 'NonExistent')
    if schema is None:
        print("Component not found")
except NotFoundError as e:
    print(f"Not found: {e}")
```

### Nested Object Navigation

```python
from pylaag.core import get_nested, set_nested, delete_nested

# Complex nested structure
api_spec = {
    'paths': {
        '/users': {
            'get': {
                'responses': {
                    '200': {
                        'content': {
                            'application/json': {
                                'schema': {'type': 'array'}
                            }
                        }
                    }
                }
            }
        }
    }
}

# Get nested value
schema_type = get_nested(api_spec, 'paths./users.get.responses.200.content.application/json.schema.type')
print(schema_type)  # 'array'

# Set nested value
set_nested(api_spec, 'paths./users.get.summary', 'List all users')

# Delete nested value
deleted = delete_nested(api_spec, 'paths./users.get.responses.200.content')
print(deleted)  # True
```

### Document Conversion

```python
from pylaag.openapi import OpenAPIDocument

# Load YAML, save as JSON
with open('api.yaml', 'r') as f:
    doc = OpenAPIDocument.from_yaml(f.read())

with open('api.json', 'w') as f:
    f.write(doc.to_json(indent=2))

# Load JSON, save as YAML
with open('api.json', 'r') as f:
    doc = OpenAPIDocument.from_json(f.read())

with open('api.yaml', 'w') as f:
    f.write(doc.to_yaml())
```

### Programmatic API Building

```python
from pylaag.openapi import OpenAPIDocument, PathManager, ComponentManager

def build_crud_api(resource_name, schema):
    """Build a complete CRUD API for a resource."""
    doc = OpenAPIDocument()
    path_mgr = PathManager(doc)
    comp_mgr = ComponentManager(doc)
    
    # Add schema
    comp_mgr.add_component('schemas', resource_name, schema)
    
    # List endpoint
    path_mgr.add_operation(f'/{resource_name.lower()}s', 'get', {
        'summary': f'List all {resource_name}s',
        'responses': {
            '200': {
                'description': 'Success',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'array',
                            'items': {'$ref': f'#/components/schemas/{resource_name}'}
                        }
                    }
                }
            }
        }
    })
    
    # Create endpoint
    path_mgr.add_operation(f'/{resource_name.lower()}s', 'post', {
        'summary': f'Create a {resource_name}',
        'requestBody': {
            'required': True,
            'content': {
                'application/json': {
                    'schema': {'$ref': f'#/components/schemas/{resource_name}'}
                }
            }
        },
        'responses': {
            '201': {'description': 'Created'}
        }
    })
    
    # Get by ID endpoint
    path_mgr.add_operation(f'/{resource_name.lower()}s/{{id}}', 'get', {
        'summary': f'Get {resource_name} by ID',
        'parameters': [
            {'name': 'id', 'in': 'path', 'required': True, 'schema': {'type': 'string'}}
        ],
        'responses': {
            '200': {'description': 'Success'},
            '404': {'description': 'Not Found'}
        }
    })
    
    # Update endpoint
    path_mgr.add_operation(f'/{resource_name.lower()}s/{{id}}', 'put', {
        'summary': f'Update {resource_name}',
        'parameters': [
            {'name': 'id', 'in': 'path', 'required': True, 'schema': {'type': 'string'}}
        ],
        'requestBody': {
            'required': True,
            'content': {
                'application/json': {
                    'schema': {'$ref': f'#/components/schemas/{resource_name}'}
                }
            }
        },
        'responses': {
            '200': {'description': 'Updated'}
        }
    })
    
    # Delete endpoint
    path_mgr.add_operation(f'/{resource_name.lower()}s/{{id}}', 'delete', {
        'summary': f'Delete {resource_name}',
        'parameters': [
            {'name': 'id', 'in': 'path', 'required': True, 'schema': {'type': 'string'}}
        ],
        'responses': {
            '204': {'description': 'Deleted'}
        }
    })
    
    return doc

# Use the function
user_schema = {
    'type': 'object',
    'required': ['name', 'email'],
    'properties': {
        'id': {'type': 'string'},
        'name': {'type': 'string'},
        'email': {'type': 'string', 'format': 'email'}
    }
}

api = build_crud_api('User', user_schema)
print(api.to_yaml())
```

---

## Best Practices

### 1. Always Validate Documents

```python
from pylaag.openapi import OpenAPIDocument
from pylaag.core import ValidationError

doc = OpenAPIDocument()
# ... make modifications ...

try:
    doc.validate()
    print("Document is valid!")
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### 2. Use Managers for Complex Operations

```python
# Good: Use managers
from pylaag.openapi import OpenAPIDocument, PathManager, ComponentManager

doc = OpenAPIDocument()
path_mgr = PathManager(doc)
comp_mgr = ComponentManager(doc)

path_mgr.add_operation('/users', 'get', {...})
comp_mgr.add_component('schemas', 'User', {...})

# Avoid: Direct dictionary manipulation
# doc._document['paths']['/users'] = {...}  # Don't do this
```

### 3. Handle Errors Gracefully

```python
from pylaag.core import LaagError

try:
    # Your code here
    pass
except LaagError as e:
    # All laag errors inherit from LaagError
    print(f"Error: {e}")
    if e.context:
        print(f"Context: {e.context}")
```

### 4. Use Extension Properties for Metadata

```python
from pylaag.openapi import OpenAPIDocument

doc = OpenAPIDocument()

# Add custom metadata
doc.set_extension('x-api-id', 'user-api-v1')
doc.set_extension('x-owner', 'platform-team')
doc.set_extension('x-internal', True)
```

### 5. Leverage Sample Generation for Testing

```python
from pylaag.openapi import SampleGenerator, ComponentManager

# Generate test data automatically
sample_gen = SampleGenerator(doc)
comp_mgr = ComponentManager(doc)

schema = comp_mgr.get_component('schemas', 'User')
test_data = sample_gen.generate_from_schema(schema)

# Use in tests
import requests
response = requests.post('https://api.example.com/users', json=test_data)
```

### 6. Version Your API Specifications

```python
from pylaag.openapi import OpenAPIDocument

doc = OpenAPIDocument({
    'openapi': '3.0.0',
    'info': {
        'title': 'My API',
        'version': '2.1.0',  # Semantic versioning
        'description': 'Version 2.1.0 - Added user preferences endpoint'
    },
    'paths': {}
})
```

### 7. Document Your APIs Thoroughly

```python
path_mgr.add_operation('/users', 'get', {
    'summary': 'List all users',
    'description': '''
        Returns a paginated list of all users in the system.
        Supports filtering by status and sorting by creation date.
    ''',
    'parameters': [
        {
            'name': 'status',
            'in': 'query',
            'description': 'Filter by user status',
            'schema': {'type': 'string', 'enum': ['active', 'inactive']}
        }
    ],
    'responses': {
        '200': {
            'description': 'Successful response with user list'
        }
    }
})
```

---

## Next Steps

- Explore the [API Reference](API_REFERENCE.md) for detailed method documentation
- Check out the example files in the `examples/` directory
- Read the [TypeScript laag documentation](https://github.com/laag/laag) for additional context
- Join the community and contribute on GitHub

---

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/laag/laag-python/issues
- Documentation: https://github.com/laag/laag-python#readme
