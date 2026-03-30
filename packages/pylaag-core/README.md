# pylaag-core

Core utilities and base classes for the laag Python library.

## Overview

`pylaag-core` provides the foundational components used by all laag packages, including:

- Base classes for API document handlers
- Error handling system
- Utility functions for nested object navigation
- Extension property support

This package is typically installed as a dependency of other laag packages and is not used directly in most cases.

## Installation

```bash
pip install pylaag-core
```

## Features

- **LaagBase**: Abstract base class for all API document handlers
- **Error Classes**: Comprehensive exception hierarchy (LaagError, ValidationError, ParseError, NotFoundError)
- **Utility Functions**: Helper functions for working with nested dictionaries
- **Extension Properties**: Support for x-* custom properties in API documents
- **Type Safety**: Full type hints for static analysis

## Usage

### Base Class

```python
from pylaag.core import LaagBase

class MyDocument(LaagBase):
    def validate(self) -> None:
        # Implement validation logic
        if 'required_field' not in self._document:
            raise ValidationError("Missing required field")
```

### Error Handling

```python
from pylaag.core import ValidationError, ParseError, NotFoundError

try:
    doc.validate()
except ValidationError as e:
    print(f"Validation failed: {e}")
    print(f"Context: {e.context}")
```

### Utility Functions

```python
from pylaag.core import get_nested, set_nested, delete_nested

data = {'a': {'b': {'c': 1}}}

# Get nested value
value = get_nested(data, 'a.b.c')  # Returns 1

# Set nested value
set_nested(data, 'a.b.d', 2)  # data['a']['b']['d'] = 2

# Delete nested value
deleted = delete_nested(data, 'a.b.c')  # Returns True
```

### Extension Properties

```python
from pylaag.core import LaagBase

doc = MyDocument()

# Set extension property
doc.set_extension('x-custom', {'key': 'value'})

# Get extension property
custom = doc.get_extension('x-custom')

# Remove extension property
doc.remove_extension('x-custom')
```

## API Reference

### Classes

#### LaagBase

Abstract base class for all API document handlers.

**Methods:**
- `validate() -> None`: Validate the document (must be implemented by subclasses)
- `get_extension(key: str) -> Optional[Any]`: Get an extension property value
- `set_extension(key: str, value: Any) -> None`: Set an extension property value
- `remove_extension(key: str) -> None`: Remove an extension property
- `to_dict() -> Dict[str, Any]`: Convert to dictionary representation

#### LaagError

Base exception class for all laag errors.

**Attributes:**
- `context: Dict[str, Any]`: Additional context information about the error

#### ValidationError

Raised when document validation fails.

#### ParseError

Raised when document parsing fails.

#### NotFoundError

Raised when a requested resource is not found.

### Functions

#### get_nested

```python
def get_nested(obj: Dict[str, Any], path: str, default: Any = None) -> Any
```

Get a nested value from a dictionary using dot notation.

**Parameters:**
- `obj`: The dictionary to search
- `path`: Dot-separated path (e.g., 'a.b.c')
- `default`: Default value if path not found

**Returns:** The value at the path, or default if not found

#### set_nested

```python
def set_nested(obj: Dict[str, Any], path: str, value: Any) -> None
```

Set a nested value in a dictionary using dot notation.

**Parameters:**
- `obj`: The dictionary to modify
- `path`: Dot-separated path (e.g., 'a.b.c')
- `value`: Value to set

#### delete_nested

```python
def delete_nested(obj: Dict[str, Any], path: str) -> bool
```

Delete a nested value from a dictionary using dot notation.

**Parameters:**
- `obj`: The dictionary to modify
- `path`: Dot-separated path (e.g., 'a.b.c')

**Returns:** True if the value was deleted, False if not found

## Requirements

- Python 3.10 or higher

## License

MIT License - see LICENSE file for details

## Related Packages

- [pylaag-openapi](https://pypi.org/project/pylaag-openapi/) - OpenAPI/Swagger support
- [pylaag-raml](https://pypi.org/project/pylaag-raml/) - RAML support
- [pylaag-smithy](https://pypi.org/project/pylaag-smithy/) - Smithy support
