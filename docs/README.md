# Laag Python Documentation

Welcome to the laag Python library documentation! This library provides a comprehensive toolkit for working with API specification formats including OpenAPI, RAML, and Smithy.

## Documentation Overview

### 📚 [User Guide](USER_GUIDE.md)
**Start here if you're new to laag!**

The User Guide provides comprehensive tutorials and examples covering:
- Installation and setup
- Working with OpenAPI documents
- Working with RAML specifications
- Working with Smithy models
- Advanced features and patterns
- Best practices

Perfect for learning the library from scratch with step-by-step examples.

### 📖 [API Reference](API_REFERENCE.md)
**Complete reference for all classes, methods, and properties**

The API Reference provides detailed documentation for:
- Core package (pylaag-core)
- OpenAPI package (pylaag-openapi)
- RAML package (pylaag-raml)
- Smithy package (pylaag-smithy)

Use this when you need to look up specific method signatures, parameters, and return types.

### ⚡ [Quick Reference](QUICK_REFERENCE.md)
**Fast lookup for common tasks**

The Quick Reference provides:
- Code snippets for common operations
- Quick syntax reminders
- Cheat sheet for all three formats
- Common patterns and recipes

Perfect for experienced users who need a quick reminder.

### 🔄 [Migration from TypeScript](MIGRATION_FROM_TYPESCRIPT.md)
**Guide for TypeScript laag users**

The Migration Guide provides:
- Naming convention differences
- Side-by-side code comparisons
- Common pitfalls and solutions
- Complete migration checklist

Perfect for developers familiar with the TypeScript version.

## Quick Start

### Installation

```bash
pip install pylaag-openapi pylaag-raml pylaag-smithy
```

### Hello World - OpenAPI

```python
from pylaag_openapi import OpenAPIDocument, PathManager

# Create a new API
doc = OpenAPIDocument()
path_mgr = PathManager(doc)

# Add an endpoint
path_mgr.add_operation('/hello', 'get', {
    'summary': 'Say hello',
    'responses': {
        '200': {
            'description': 'Success',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string'}
                        }
                    }
                }
            }
        }
    }
})

# Validate and save
doc.validate()
print(doc.to_yaml())
```

## Package Structure

The laag Python library is organized into four packages:

### pylaag-core
Foundation package providing:
- Base classes for all document types
- Error handling system
- Utility functions for nested object navigation
- Extension property support

### pylaag-openapi
OpenAPI 3.0+ support including:
- Document parsing and serialization (JSON/YAML)
- Path and operation management
- Component management (schemas, responses, parameters, etc.)
- Sample data generation from schemas
- Client code generation (Python, JavaScript, TypeScript)
- Curl command generation

### pylaag-raml
RAML 1.0/0.8 support including:
- Document parsing and serialization (YAML)
- Resource and method management
- Type definition management
- Trait support

### pylaag-smithy
Smithy 2.0 support including:
- Document parsing and serialization (JSON)
- Shape management (structures, lists, maps, etc.)
- Trait application and management
- Operation management

## Key Features

### 🎯 Type Safety
Full type hints throughout the library for excellent IDE support and static analysis.

```python
from pylaag_openapi import OpenAPIDocument
from typing import Dict, Any

def process_api(doc: OpenAPIDocument) -> Dict[str, Any]:
    doc.validate()
    return doc.to_dict()
```

### 🔄 Format Conversion
Easy conversion between JSON and YAML formats.

```python
# Load YAML, save as JSON
doc = OpenAPIDocument.from_yaml(yaml_content)
json_output = doc.to_json()
```

### 🧩 Extension Properties
Support for custom extension properties (x-*) across all formats.

```python
doc.set_extension('x-internal', True)
doc.set_extension('x-api-id', 'user-api-v1')
```

### 🎲 Sample Generation
Automatic sample data generation from schemas.

```python
from pylaag_openapi import SampleGenerator

sample_gen = SampleGenerator(doc)
sample = sample_gen.generate_from_schema(schema)
```

### 💻 Code Generation
Generate client code in multiple languages.

```python
from pylaag_openapi import CodeGenerator

code_gen = CodeGenerator(doc)
python_client = code_gen.generate_client('python')
js_client = code_gen.generate_client('javascript')
ts_client = code_gen.generate_client('typescript')
```

### 🔧 Curl Generation
Generate curl commands for testing APIs.

```python
from pylaag_openapi import CurlGenerator

curl_gen = CurlGenerator(doc)
curl_cmd = curl_gen.generate_curl('/users', 'post')
```

## Common Use Cases

### 1. API Documentation Generation
Load existing API specs and generate documentation or client libraries.

### 2. API Design and Prototyping
Programmatically build API specifications with validation.

### 3. API Testing
Generate sample data and curl commands for testing.

### 4. API Migration
Convert between different specification formats or versions.

### 5. API Validation
Validate API specifications against format standards.

### 6. Code Generation
Generate client SDKs in multiple programming languages.

## Error Handling

All laag errors inherit from `LaagError`:

```python
from pylaag_core import LaagError, ValidationError, ParseError, NotFoundError

try:
    doc = OpenAPIDocument.from_yaml(content)
    doc.validate()
except ParseError as e:
    print(f"Failed to parse: {e}")
except ValidationError as e:
    print(f"Invalid document: {e}")
except LaagError as e:
    print(f"Error: {e}")
    print(f"Context: {e.context}")
```

## Best Practices

1. **Always validate** documents before saving or using them
2. **Use managers** (PathManager, ComponentManager, etc.) instead of direct dictionary manipulation
3. **Handle errors** gracefully with try-except blocks
4. **Use extension properties** for custom metadata
5. **Leverage type hints** for better IDE support
6. **Version your APIs** using semantic versioning

## Examples

Check out the examples in each package's test directory:
- `packages/pylaag-openapi/tests/` - OpenAPI examples
- `packages/pylaag-raml/tests/` - RAML examples
- `packages/pylaag-smithy/tests/` - Smithy examples

## Support and Contributing

- **GitHub**: https://github.com/laag/laag-python
- **Issues**: https://github.com/laag/laag-python/issues
- **TypeScript Version**: https://github.com/laag/laag

## License

MIT License - see LICENSE file for details.

## Related Projects

- [laag (TypeScript)](https://github.com/laag/laag) - The original TypeScript implementation
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [RAML Specification](https://raml.org/)
- [Smithy Specification](https://smithy.io/)

---

**Ready to get started?** Head over to the [User Guide](USER_GUIDE.md) for detailed tutorials and examples!
