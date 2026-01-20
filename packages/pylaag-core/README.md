# pylaag-core

Core utilities and base classes for the laag Python library.

## Overview

This package provides the foundation for all laag packages, including:

- Base classes for API document handlers
- Custom exception classes for error handling
- Utility functions for nested object navigation
- Extension property handling

## Installation

```bash
pip install pylaag-core
```

## Usage

### Base Class

```python
from pylaag_core import LaagBase

class MyDocument(LaagBase):
    def validate(self):
        # Implement validation logic
        pass
```

### Error Handling

```python
from pylaag_core import LaagError, ValidationError, ParseError, NotFoundError

try:
    # Some operation
    pass
except ValidationError as e:
    print(f"Validation failed: {e}")
    print(f"Context: {e.context}")
```

### Utility Functions

```python
from pylaag_core import get_nested, set_nested, delete_nested

data = {'a': {'b': {'c': 1}}}

# Get nested value
value = get_nested(data, 'a.b.c')  # Returns 1

# Set nested value
set_nested(data, 'a.b.d', 2)  # data['a']['b']['d'] = 2

# Delete nested value
delete_nested(data, 'a.b.c')  # Removes data['a']['b']['c']
```

### Extension Properties

```python
from pylaag_core import LaagBase

doc = MyDocument()

# Set extension property
doc.set_extension('x-custom', 'value')

# Get extension property
value = doc.get_extension('x-custom')

# Remove extension property
doc.remove_extension('x-custom')
```

## Requirements

- Python 3.10 or higher

## License

MIT License
