# Laag Python

Python port of the [laag](https://github.com/laag/laag) library for working with API specification formats.

## Overview

Laag Python is a modern collection of packages for working with API specification formats including:

- **OpenAPI/Swagger** - Create, parse, and manipulate OpenAPI 3.0+ documents
- **RAML** - Work with RAML 1.0 and 0.8 specifications
- **Smithy** - Handle Smithy 2.0 IDL documents

## Features

- 🎯 **Type-safe** - Comprehensive type hints for static analysis
- 🔄 **Round-trip parsing** - Parse and serialize without data loss
- 🛠️ **Code generation** - Generate client code in Python, JavaScript, and TypeScript
- 📝 **Sample generation** - Create example data from schemas
- ✅ **Validation** - Validate documents against specifications
- 🧩 **Extensible** - Easy to extend for custom needs

## Installation

```bash
# Install all packages
pip install pylaag-core pylaag-openapi pylaag-raml pylaag-smithy

# Or install individual packages
pip install pylaag-openapi  # OpenAPI support only
pip install pylaag-raml     # RAML support only
pip install pylaag-smithy   # Smithy support only
```

## Documentation

📚 **[Complete Documentation](docs/README.md)**

- **[User Guide](docs/USER_GUIDE.md)** - Comprehensive tutorials and examples
- **[API Reference](docs/API_REFERENCE.md)** - Detailed API documentation
- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Fast lookup for common tasks

## Quick Start

### OpenAPI

```python
from pylaag.openapi import OpenAPIDocument, PathManager

# Create a new API
doc = OpenAPIDocument()
path_mgr = PathManager(doc)

# Add an endpoint
path_mgr.add_operation('/users', 'get', {
    'summary': 'List all users',
    'responses': {
        '200': {'description': 'Success'}
    }
})

# Validate and save
doc.validate()
print(doc.to_yaml())
```

### RAML

```python
from pylaag.raml import RAMLDocument, ResourceManager

# Create a new API
doc = RAMLDocument()
resource_mgr = ResourceManager(doc)

# Add a resource
resource_mgr.add_resource('/users')
resource_mgr.add_method('/users', 'get', {
    'description': 'List all users'
})

# Validate and save
doc.validate()
print(doc.to_yaml())
```

### Smithy

```python
from pylaag.smithy import SmithyDocument, ShapeManager

# Create a new model
doc = SmithyDocument()
shape_mgr = ShapeManager(doc)

# Add a shape
shape_mgr.add_shape('com.example#User', 'structure', {
    'members': {
        'id': {'target': 'smithy.api#String'},
        'name': {'target': 'smithy.api#String'}
    }
})

# Validate and save
doc.validate()
print(doc.to_json())
```

## More Examples

### Generate Sample Data

```python
from pylaag.openapi import SampleGenerator

sample_gen = SampleGenerator(doc)
sample = sample_gen.generate_from_schema({
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'email': {'type': 'string', 'format': 'email'}
    }
})
print(sample)  # {'name': 'xyz', 'email': 'user@example.com'}
```

### Generate Client Code

```python
from pylaag.openapi import CodeGenerator

code_gen = CodeGenerator(doc)
python_client = code_gen.generate_client('python')
js_client = code_gen.generate_client('javascript')
ts_client = code_gen.generate_client('typescript')
```

### Generate Curl Commands

```python
from pylaag.openapi import CurlGenerator

curl_gen = CurlGenerator(doc)
curl_cmd = curl_gen.generate_curl('/users', 'post')
print(curl_cmd)
```

## Development

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run tests
uv run pytest

# Run type checking
uv run mypy packages

# Run linting
uv run ruff check packages
```

## Project Structure

```
laag-python/
├── packages/
│   ├── pylaag-core/      # Core utilities and base classes
│   ├── pylaag-openapi/   # OpenAPI implementation
│   ├── pylaag-raml/      # RAML implementation
│   └── pylaag-smithy/    # Smithy implementation
├── pyproject.toml        # Workspace configuration
└── README.md
```

## Requirements

- Python 3.10 or higher
- PyYAML for YAML parsing

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.

## Related Projects

- [laag](https://github.com/laag/laag) - The original TypeScript implementation
