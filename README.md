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

## Quick Start

### OpenAPI

```python
from pylaag_openapi import OpenAPIDocument

# Parse an OpenAPI document
doc = OpenAPIDocument.from_yaml(yaml_content)
doc.validate()

# Access document properties
print(doc.info['title'])
print(doc.openapi_version)

# Serialize back to YAML or JSON
yaml_output = doc.to_yaml()
json_output = doc.to_json()
```

### RAML

```python
from pylaag_raml import RAMLDocument

# Parse a RAML document
doc = RAMLDocument.from_yaml(raml_content)
doc.validate()

# Access document properties
print(doc.title)
print(doc.version)
```

### Smithy

```python
from pylaag_smithy import SmithyDocument

# Parse a Smithy document
doc = SmithyDocument.from_json(smithy_json)
doc.validate()

# Access shapes
print(doc.shapes)
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
