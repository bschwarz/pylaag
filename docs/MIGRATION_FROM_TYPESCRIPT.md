# Migration Guide: TypeScript to Python

This guide helps developers migrate from the TypeScript laag library to the Python version.

## Overview

The Python port maintains API compatibility with the TypeScript version while following Python conventions. Most concepts translate directly, with naming adjusted to follow Python style (snake_case instead of camelCase).

## Key Differences

### Naming Conventions

| TypeScript    | Python       | Notes                           |
| ------------- | ------------ | ------------------------------- |
| `camelCase`   | `snake_case` | Method and variable names       |
| `PascalCase`  | `PascalCase` | Class names (unchanged)         |
| `from_json()` | `fromJson()` | Class methods use snake_case    |
| `to_yaml()`   | `toYaml()`   | Instance methods use snake_case |

### Import Statements

**TypeScript:**
```typescript
import { OpenAPIDocument, PathManager } from '@laag/openapi';
```

**Python:**
```python
from pylaag.openapi import OpenAPIDocument, PathManager
```

### Package Names

| TypeScript      | Python           |
| --------------- | ---------------- |
| `@laag/core`    | `pylaag-core`    |
| `@laag/openapi` | `pylaag-openapi` |
| `@laag/raml`    | `pylaag-raml`    |
| `@laag/smithy`  | `pylaag-smithy`  |

## Common Patterns

### Creating Documents

**TypeScript:**
```typescript
const doc = new OpenAPIDocument();
```

**Python:**
```python
doc = OpenAPIDocument()
```

### Parsing Documents

**TypeScript:**
```typescript
const doc = OpenAPIDocument.fromYaml(yamlContent);
const doc2 = OpenAPIDocument.fromJson(jsonContent);
```

**Python:**
```python
doc = OpenAPIDocument.from_yaml(yaml_content)
doc2 = OpenAPIDocument.from_json(json_content)
```

### Serializing Documents

**TypeScript:**
```typescript
const yaml = doc.toYaml();
const json = doc.toJson();
```

**Python:**
```python
yaml = doc.to_yaml()
json = doc.to_json()
```

### Managing Paths

**TypeScript:**
```typescript
const pathMgr = new PathManager(doc);
pathMgr.addPath('/users', {});
pathMgr.addOperation('/users', 'get', {
  summary: 'List users'
});
```

**Python:**
```python
path_mgr = PathManager(doc)
path_mgr.add_path('/users', {})
path_mgr.add_operation('/users', 'get', {
    'summary': 'List users'
})
```

### Managing Components

**TypeScript:**
```typescript
const compMgr = new ComponentManager(doc);
compMgr.addComponent('schemas', 'User', {
  type: 'object',
  properties: {
    id: { type: 'string' },
    name: { type: 'string' }
  }
});
```

**Python:**
```python
comp_mgr = ComponentManager(doc)
comp_mgr.add_component('schemas', 'User', {
    'type': 'object',
    'properties': {
        'id': {'type': 'string'},
        'name': {'type': 'string'}
    }
})
```

### Extension Properties

**TypeScript:**
```typescript
doc.setExtension('x-internal', true);
const value = doc.getExtension('x-internal');
doc.removeExtension('x-internal');
```

**Python:**
```python
doc.set_extension('x-internal', True)
value = doc.get_extension('x-internal')
doc.remove_extension('x-internal')
```

### Error Handling

**TypeScript:**
```typescript
try {
  doc.validate();
} catch (error) {
  if (error instanceof ValidationError) {
    console.log('Validation failed:', error.message);
  }
}
```

**Python:**
```python
from pylaag.core import ValidationError

try:
    doc.validate()
except ValidationError as e:
    print(f'Validation failed: {e}')
```

## Type System Differences

### TypeScript Interfaces → Python Type Hints

**TypeScript:**
```typescript
interface User {
  id: string;
  name: string;
  age?: number;
}

function processUser(user: User): void {
  // ...
}
```

**Python:**
```python
from typing import Optional, Dict, Any

def process_user(user: Dict[str, Any]) -> None:
    # Access with dictionary syntax
    user_id: str = user['id']
    name: str = user['name']
    age: Optional[int] = user.get('age')
```

### Optional Parameters

**TypeScript:**
```typescript
function addPath(path: string, pathItem?: object): void {
  // ...
}
```

**Python:**
```python
from typing import Optional, Dict, Any

def add_path(path: str, path_item: Optional[Dict[str, Any]] = None) -> None:
    # ...
```

### Union Types

**TypeScript:**
```typescript
type HttpMethod = 'get' | 'post' | 'put' | 'delete';
```

**Python:**
```python
from typing import Literal

HttpMethod = Literal['get', 'post', 'put', 'delete']
```

## Data Structure Differences

### Objects

**TypeScript:**
```typescript
const operation = {
  summary: 'List users',
  responses: {
    '200': { description: 'Success' }
  }
};
```

**Python:**
```python
operation = {
    'summary': 'List users',
    'responses': {
        '200': {'description': 'Success'}
    }
}
```

Note: Python requires quotes around all dictionary keys.

### Boolean Values

**TypeScript:**
```typescript
const config = {
  required: true,
  deprecated: false
};
```

**Python:**
```python
config = {
    'required': True,  # Capital T
    'deprecated': False  # Capital F
}
```

### Null Values

**TypeScript:**
```typescript
const value = null;
```

**Python:**
```python
value = None  # Capital N
```

## Async/Await

The Python version does not use async/await as the TypeScript version does for I/O operations. All operations are synchronous.

**TypeScript:**
```typescript
const content = await fs.readFile('api.yaml', 'utf-8');
const doc = OpenAPIDocument.fromYaml(content);
```

**Python:**
```python
with open('api.yaml', 'r') as f:
    content = f.read()
doc = OpenAPIDocument.from_yaml(content)
```

## Complete Migration Example

### TypeScript Version

```typescript
import { OpenAPIDocument, PathManager, ComponentManager } from '@laag/openapi';
import * as fs from 'fs';

async function buildApi() {
  const doc = new OpenAPIDocument();
  const pathMgr = new PathManager(doc);
  const compMgr = new ComponentManager(doc);

  // Add schema
  compMgr.addComponent('schemas', 'User', {
    type: 'object',
    required: ['name', 'email'],
    properties: {
      id: { type: 'string' },
      name: { type: 'string' },
      email: { type: 'string', format: 'email' }
    }
  });

  // Add endpoint
  pathMgr.addOperation('/users', 'get', {
    summary: 'List all users',
    responses: {
      '200': {
        description: 'Success',
        content: {
          'application/json': {
            schema: {
              type: 'array',
              items: { $ref: '#/components/schemas/User' }
            }
          }
        }
      }
    }
  });

  // Validate and save
  doc.validate();
  await fs.promises.writeFile('api.yaml', doc.toYaml());
}
```

### Python Version

```python
from pylaag.openapi import OpenAPIDocument, PathManager, ComponentManager

def build_api():
    doc = OpenAPIDocument()
    path_mgr = PathManager(doc)
    comp_mgr = ComponentManager(doc)

    # Add schema
    comp_mgr.add_component('schemas', 'User', {
        'type': 'object',
        'required': ['name', 'email'],
        'properties': {
            'id': {'type': 'string'},
            'name': {'type': 'string'},
            'email': {'type': 'string', 'format': 'email'}
        }
    })

    # Add endpoint
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

    # Validate and save
    doc.validate()
    with open('api.yaml', 'w') as f:
        f.write(doc.to_yaml())
```

## Migration Checklist

- [ ] Update import statements to use Python package names
- [ ] Convert camelCase to snake_case for methods and variables
- [ ] Add quotes around all dictionary keys
- [ ] Change `true`/`false` to `True`/`False`
- [ ] Change `null` to `None`
- [ ] Remove async/await and use synchronous file operations
- [ ] Update error handling to use Python exceptions
- [ ] Add type hints for better IDE support
- [ ] Use `with` statements for file operations
- [ ] Update test assertions to use pytest syntax

## Common Pitfalls

### 1. Forgetting Quotes on Dictionary Keys

**Wrong:**
```python
operation = {
    summary: 'List users'  # SyntaxError!
}
```

**Correct:**
```python
operation = {
    'summary': 'List users'
}
```

### 2. Using Lowercase Boolean Values

**Wrong:**
```python
config = {'required': true}  # NameError!
```

**Correct:**
```python
config = {'required': True}
```

### 3. Using null Instead of None

**Wrong:**
```python
value = null  # NameError!
```

**Correct:**
```python
value = None
```

### 4. Forgetting to Convert Method Names

**Wrong:**
```python
doc.toYaml()  # AttributeError!
```

**Correct:**
```python
doc.to_yaml()
```

## Testing Differences

### TypeScript (Jest)

```typescript
describe('OpenAPIDocument', () => {
  it('should create a valid document', () => {
    const doc = new OpenAPIDocument();
    expect(() => doc.validate()).not.toThrow();
  });
});
```

### Python (pytest)

```python
def test_openapi_document_creation():
    """Test that a new document is valid."""
    doc = OpenAPIDocument()
    doc.validate()  # Should not raise
```

## Additional Resources

- [Python User Guide](USER_GUIDE.md)
- [Python API Reference](API_REFERENCE.md)
- [TypeScript laag Documentation](https://github.com/laag/laag)

## Getting Help

If you encounter issues during migration:
1. Check the [API Reference](API_REFERENCE.md) for correct method names
2. Review the [User Guide](USER_GUIDE.md) for examples
3. Open an issue on [GitHub](https://github.com/laag/laag-python/issues)
