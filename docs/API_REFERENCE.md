# Laag Python API Reference

Complete API reference for the laag Python library.

## Table of Contents

- [Core Package (pylaag-core)](#core-package-pylaag-core)
- [OpenAPI Package (pylaag-openapi)](#openapi-package-pylaag-openapi)
- [RAML Package (pylaag-raml)](#raml-package-pylaag-raml)
- [Smithy Package (pylaag-smithy)](#smithy-package-pylaag-smithy)

---

## Core Package (pylaag-core)

### LaagBase

Abstract base class for all API document handlers.

```python
from pylaag_core import LaagBase
```

#### Methods

##### `validate() -> None`
Validate the document against its specification. Must be implemented by subclasses.

**Raises:**
- `ValidationError`: If the document is invalid

##### `get_extension(key: str) -> Optional[Any]`
Get an extension property value.

**Parameters:**
- `key`: Extension property name (must start with 'x-')

**Returns:** The extension property value, or None if not found

##### `set_extension(key: str, value: Any) -> None`
Set an extension property value.

**Parameters:**
- `key`: Extension property name (must start with 'x-')
- `value`: Value to set

**Raises:**
- `ValueError`: If key doesn't start with 'x-'

##### `remove_extension(key: str) -> None`
Remove an extension property.

**Parameters:**
- `key`: Extension property name to remove

##### `to_dict() -> Dict[str, Any]`
Convert the document to a dictionary representation.

**Returns:** Dictionary representation of the document

---

### Error Classes

#### `LaagError`
Base exception for all laag errors.

**Attributes:**
- `context`: Dictionary containing error context information

#### `ValidationError`
Raised when document validation fails. Inherits from `LaagError`.

#### `ParseError`
Raised when document parsing fails. Inherits from `LaagError`.

#### `NotFoundError`
Raised when a requested resource is not found. Inherits from `LaagError`.

---

### Utility Functions

#### `get_nested(obj: Dict[str, Any], path: str, default: Any = None) -> Any`
Get a nested value from a dictionary using dot notation.

**Parameters:**
- `obj`: Dictionary to search
- `path`: Dot-separated path (e.g., 'a.b.c')
- `default`: Default value if path not found

**Returns:** Value at the path, or default if not found

**Example:**
```python
from pylaag_core import get_nested

data = {'a': {'b': {'c': 1}}}
value = get_nested(data, 'a.b.c')  # Returns 1
```

#### `set_nested(obj: Dict[str, Any], path: str, value: Any) -> None`
Set a nested value in a dictionary using dot notation.

**Parameters:**
- `obj`: Dictionary to modify
- `path`: Dot-separated path
- `value`: Value to set

**Example:**
```python
from pylaag_core import set_nested

data = {}
set_nested(data, 'a.b.c', 1)  # Creates {'a': {'b': {'c': 1}}}
```

#### `delete_nested(obj: Dict[str, Any], path: str) -> bool`
Delete a nested value from a dictionary using dot notation.

**Parameters:**
- `obj`: Dictionary to modify
- `path`: Dot-separated path

**Returns:** True if deleted, False if not found

---

## OpenAPI Package (pylaag-openapi)

### OpenAPIDocument

Represents an OpenAPI document.

```python
from pylaag_openapi import OpenAPIDocument
```

#### Class Methods

##### `from_json(json_str: str) -> OpenAPIDocument`
Parse an OpenAPI document from JSON string.

**Parameters:**
- `json_str`: JSON string to parse

**Returns:** OpenAPIDocument instance

**Raises:**
- `ParseError`: If JSON is invalid

##### `from_yaml(yaml_str: str) -> OpenAPIDocument`
Parse an OpenAPI document from YAML string.

**Parameters:**
- `yaml_str`: YAML string to parse

**Returns:** OpenAPIDocument instance

**Raises:**
- `ParseError`: If YAML is invalid

#### Instance Methods

##### `to_json(indent: int = 2) -> str`
Serialize to JSON string.

**Parameters:**
- `indent`: Number of spaces for indentation

**Returns:** JSON string representation

##### `to_yaml() -> str`
Serialize to YAML string.

**Returns:** YAML string representation

##### `validate() -> None`
Validate the OpenAPI document structure.

**Raises:**
- `ValidationError`: If document is invalid

#### Properties

##### `openapi_version: str`
Get the OpenAPI version.

##### `info: Dict[str, Any]`
Get the info object.

##### `paths: Dict[str, Any]`
Get the paths object.

---

### PathManager

Manages paths and operations in an OpenAPI document.

```python
from pylaag_openapi import PathManager

path_mgr = PathManager(document)
```

#### Methods

##### `add_path(path: str, path_item: Optional[Dict[str, Any]] = None) -> None`
Add a path to the document.

**Parameters:**
- `path`: Path string (e.g., '/users')
- `path_item`: Optional path item definition

##### `remove_path(path: str) -> bool`
Remove a path from the document.

**Parameters:**
- `path`: Path string to remove

**Returns:** True if removed, False if not found

##### `get_path(path: str) -> Optional[Dict[str, Any]]`
Get a path item.

**Parameters:**
- `path`: Path string

**Returns:** Path item dictionary, or None if not found

##### `add_operation(path: str, method: HttpMethod, operation: Dict[str, Any]) -> None`
Add an operation to a path.

**Parameters:**
- `path`: Path string
- `method`: HTTP method ('get', 'post', 'put', 'delete', 'patch', 'options', 'head', 'trace')
- `operation`: Operation definition

##### `remove_operation(path: str, method: HttpMethod) -> bool`
Remove an operation from a path.

**Parameters:**
- `path`: Path string
- `method`: HTTP method

**Returns:** True if removed, False if not found

##### `get_operation(path: str, method: HttpMethod) -> Optional[Dict[str, Any]]`
Get an operation.

**Parameters:**
- `path`: Path string
- `method`: HTTP method

**Returns:** Operation dictionary, or None if not found

---

### ComponentManager

Manages reusable components in an OpenAPI document.

```python
from pylaag_openapi import ComponentManager

comp_mgr = ComponentManager(document)
```

#### Methods

##### `add_component(component_type: ComponentType, name: str, component: Dict[str, Any]) -> None`
Add a component to the document.

**Parameters:**
- `component_type`: Type of component ('schemas', 'responses', 'parameters', 'examples', 'requestBodies', 'headers', 'securitySchemes', 'links', 'callbacks')
- `name`: Component name
- `component`: Component definition

##### `remove_component(component_type: ComponentType, name: str) -> bool`
Remove a component from the document.

**Parameters:**
- `component_type`: Type of component
- `name`: Component name

**Returns:** True if removed, False if not found

##### `get_component(component_type: ComponentType, name: str) -> Optional[Dict[str, Any]]`
Get a component.

**Parameters:**
- `component_type`: Type of component
- `name`: Component name

**Returns:** Component dictionary, or None if not found

##### `resolve_reference(ref: str) -> Optional[Dict[str, Any]]`
Resolve a $ref reference.

**Parameters:**
- `ref`: Reference string (e.g., '#/components/schemas/User')

**Returns:** Referenced component, or None if not found

**Raises:**
- `ValueError`: If reference is not a local reference

---

### SampleGenerator

Generates sample data from OpenAPI schemas.

```python
from pylaag_openapi import SampleGenerator

sample_gen = SampleGenerator(document)
```

#### Methods

##### `generate_from_schema(schema: Dict[str, Any], depth: int = 0, max_depth: int = 5) -> Any`
Generate a sample value from a schema.

**Parameters:**
- `schema`: JSON Schema definition
- `depth`: Current recursion depth (internal use)
- `max_depth`: Maximum recursion depth

**Returns:** Generated sample value

**Supported Features:**
- Primitive types (string, number, integer, boolean, null)
- String formats (email, uri, date, date-time, uuid)
- Arrays with min/max items
- Objects with required properties
- Enums
- $ref resolution
- Constraints (min, max, minLength, maxLength)

---

### CodeGenerator

Generates client code from OpenAPI documents.

```python
from pylaag_openapi import CodeGenerator

code_gen = CodeGenerator(document)
```

#### Methods

##### `generate_client(language: Language) -> str`
Generate a complete client in the specified language.

**Parameters:**
- `language`: Target language ('python', 'javascript', 'typescript')

**Returns:** Generated client code as string

**Raises:**
- `ValueError`: If language is not supported

---

### CurlGenerator

Generates curl commands from OpenAPI operations.

```python
from pylaag_openapi import CurlGenerator

curl_gen = CurlGenerator(document)
```

#### Methods

##### `generate_curl(path: str, method: str, base_url: str = 'https://api.example.com', include_sample_body: bool = True) -> str`
Generate a curl command for an operation.

**Parameters:**
- `path`: Path string
- `method`: HTTP method
- `base_url`: Base URL for the API
- `include_sample_body`: Whether to include a sample request body

**Returns:** Curl command string

**Raises:**
- `NotFoundError`: If operation not found

---

## RAML Package (pylaag-raml)

### RAMLDocument

Represents a RAML document.

```python
from pylaag_raml import RAMLDocument
```

#### Class Methods

##### `from_yaml(yaml_str: str) -> RAMLDocument`
Parse a RAML document from YAML string.

**Parameters:**
- `yaml_str`: YAML string to parse

**Returns:** RAMLDocument instance

**Raises:**
- `ParseError`: If YAML is invalid

#### Instance Methods

##### `to_yaml() -> str`
Serialize to YAML string.

**Returns:** YAML string representation

##### `validate() -> None`
Validate the RAML document structure.

**Raises:**
- `ValidationError`: If document is invalid

#### Properties

##### `title: str`
Get the document title.

##### `version: str`
Get the API version.

##### `base_uri: Optional[str]`
Get the base URI.

---

### ResourceManager

Manages resources and methods in a RAML document.

```python
from pylaag_raml import ResourceManager

resource_mgr = ResourceManager(document)
```

#### Methods

##### `add_resource(path: str, resource: Optional[Dict[str, Any]] = None) -> None`
Add a resource to the document.

**Parameters:**
- `path`: Resource path (e.g., '/users')
- `resource`: Optional resource definition

##### `remove_resource(path: str) -> bool`
Remove a resource from the document.

**Parameters:**
- `path`: Resource path

**Returns:** True if removed, False if not found

##### `get_resource(path: str) -> Optional[Dict[str, Any]]`
Get a resource.

**Parameters:**
- `path`: Resource path

**Returns:** Resource dictionary, or None if not found

##### `add_method(path: str, method: str, method_def: Dict[str, Any]) -> None`
Add a method to a resource.

**Parameters:**
- `path`: Resource path
- `method`: HTTP method
- `method_def`: Method definition

##### `remove_method(path: str, method: str) -> bool`
Remove a method from a resource.

**Parameters:**
- `path`: Resource path
- `method`: HTTP method

**Returns:** True if removed, False if not found

---

### TypeManager

Manages type definitions in a RAML document.

```python
from pylaag_raml import TypeManager

type_mgr = TypeManager(document)
```

#### Methods

##### `add_type(name: str, type_def: Dict[str, Any]) -> None`
Add a type definition.

**Parameters:**
- `name`: Type name
- `type_def`: Type definition

##### `remove_type(name: str) -> bool`
Remove a type definition.

**Parameters:**
- `name`: Type name

**Returns:** True if removed, False if not found

##### `get_type(name: str) -> Optional[Dict[str, Any]]`
Get a type definition.

**Parameters:**
- `name`: Type name

**Returns:** Type definition, or None if not found

---

## Smithy Package (pylaag-smithy)

### SmithyDocument

Represents a Smithy document.

```python
from pylaag_smithy import SmithyDocument
```

#### Class Methods

##### `from_json(json_str: str) -> SmithyDocument`
Parse a Smithy document from JSON string.

**Parameters:**
- `json_str`: JSON string to parse

**Returns:** SmithyDocument instance

**Raises:**
- `ParseError`: If JSON is invalid

#### Instance Methods

##### `to_json(indent: int = 2) -> str`
Serialize to JSON string.

**Parameters:**
- `indent`: Number of spaces for indentation

**Returns:** JSON string representation

##### `validate() -> None`
Validate the Smithy document structure.

**Raises:**
- `ValidationError`: If document is invalid

#### Properties

##### `smithy_version: str`
Get the Smithy version.

##### `shapes: Dict[str, Any]`
Get the shapes object.

---

### ShapeManager

Manages shapes in a Smithy document.

```python
from pylaag_smithy import ShapeManager

shape_mgr = ShapeManager(document)
```

#### Methods

##### `add_shape(shape_id: str, shape_type: str, definition: Optional[Dict[str, Any]] = None) -> None`
Add a shape to the document.

**Parameters:**
- `shape_id`: Shape identifier (e.g., 'com.example#User')
- `shape_type`: Shape type ('structure', 'string', 'integer', 'list', 'map', 'service', 'operation', etc.)
- `definition`: Optional shape definition

##### `remove_shape(shape_id: str) -> bool`
Remove a shape from the document.

**Parameters:**
- `shape_id`: Shape identifier

**Returns:** True if removed, False if not found

##### `get_shape(shape_id: str) -> Optional[Dict[str, Any]]`
Get a shape.

**Parameters:**
- `shape_id`: Shape identifier

**Returns:** Shape dictionary, or None if not found

##### `resolve_target(target: str) -> Optional[Dict[str, Any]]`
Resolve a target reference to a shape.

**Parameters:**
- `target`: Target identifier

**Returns:** Shape dictionary, or None if not found

---

### TraitManager

Manages traits applied to shapes in a Smithy document.

```python
from pylaag_smithy import TraitManager

trait_mgr = TraitManager(document)
```

#### Methods

##### `add_trait_to_shape(shape_id: str, trait_name: str, trait_value: Any = None) -> None`
Add a trait to a shape.

**Parameters:**
- `shape_id`: Shape identifier
- `trait_name`: Trait name (e.g., 'smithy.api#http')
- `trait_value`: Optional trait value

**Raises:**
- `NotFoundError`: If shape not found

##### `remove_trait_from_shape(shape_id: str, trait_name: str) -> bool`
Remove a trait from a shape.

**Parameters:**
- `shape_id`: Shape identifier
- `trait_name`: Trait name

**Returns:** True if removed, False if not found

##### `get_trait(shape_id: str, trait_name: str) -> Optional[Any]`
Get a trait value from a shape.

**Parameters:**
- `shape_id`: Shape identifier
- `trait_name`: Trait name

**Returns:** Trait value, or None if not found

---

### OperationManager

Manages operations in a Smithy document.

```python
from pylaag_smithy import OperationManager

op_mgr = OperationManager(document)
```

#### Methods

##### `add_operation(operation_id: str, input_shape: Optional[str] = None, output_shape: Optional[str] = None, errors: Optional[List[str]] = None) -> None`
Add an operation to the document.

**Parameters:**
- `operation_id`: Operation identifier
- `input_shape`: Optional input shape identifier
- `output_shape`: Optional output shape identifier
- `errors`: Optional list of error shape identifiers

##### `remove_operation(operation_id: str) -> bool`
Remove an operation from the document.

**Parameters:**
- `operation_id`: Operation identifier

**Returns:** True if removed, False if not found

##### `get_operation(operation_id: str) -> Optional[Dict[str, Any]]`
Get an operation.

**Parameters:**
- `operation_id`: Operation identifier

**Returns:** Operation dictionary, or None if not found
