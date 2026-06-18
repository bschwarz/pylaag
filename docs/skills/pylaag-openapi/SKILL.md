---
name: pylaag-openapi
description: Working with OpenAPI documents using pylaag-openapi. Use when parsing, creating, or modifying OpenAPI specs in Python.
---

# pylaag-openapi — Working with OpenAPI Documents

## Installation & Import

```python
from pylaag.openapi import (
    OpenAPIDocument,
    PathManager,
    HttpMethod,
    ComponentManager,
    ComponentType,
    SampleGenerator,
    CodeGenerator,
    Language,
    CurlGenerator,
)
```

## Creating a Document

```python
# Empty document (defaults provided)
doc = OpenAPIDocument()

# From a dict
doc = OpenAPIDocument({
    "openapi": "3.0.0",
    "info": {"title": "My API", "version": "1.0.0"},
    "paths": {}
})

# From JSON string
doc = OpenAPIDocument.from_json(json_str)

# From YAML string
doc = OpenAPIDocument.from_yaml(yaml_str)
```

## Document Properties & Serialization

```python
doc.openapi_version   # "3.0.0"
doc.info              # {"title": "...", "version": "..."}
doc.paths             # {"paths": {...}}

doc.to_json(indent=2) # JSON string
doc.to_yaml()         # YAML string
```

## Validation

```python
from pylaag.core import ValidationError

try:
    doc.validate()
except ValidationError as e:
    print(e)
```

Checks for `openapi`, `info.title`, `info.version`, and `paths`.

## PathManager — Add/Read Paths & Operations

```python
path_mgr = PathManager(doc)

# Add a bare path
path_mgr.add_path("/users")

# Add an operation (creates path automatically if missing)
path_mgr.add_operation("/users", "get", {
    "summary": "List users",
    "operationId": "listUsers",
    "responses": {"200": {"description": "Success"}}
})

path_mgr.add_operation("/users", "post", {
    "summary": "Create a user",
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/User"}
            }
        }
    },
    "responses": {"201": {"description": "Created"}}
})

# Read
op = path_mgr.get_operation("/users", "get")   # dict | None
pi = path_mgr.get_path("/users")               # dict | None

# Remove
path_mgr.remove_operation("/users", "get")     # bool
path_mgr.remove_path("/users")                 # bool
```

`HttpMethod` is a `Literal` for: `"get" | "post" | "put" | "delete" | "patch" | "options" | "head" | "trace"`

## ComponentManager — Schemas & Reusables

```python
comp_mgr = ComponentManager(doc)

# Add a schema component
comp_mgr.add_component("schemas", "User", {
    "type": "object",
    "required": ["id", "name"],
    "properties": {
        "id":    {"type": "integer"},
        "name":  {"type": "string"},
        "email": {"type": "string", "format": "email"}
    }
})

# Get / remove
schema = comp_mgr.get_component("schemas", "User")   # dict | None
comp_mgr.remove_component("schemas", "User")          # bool

# Resolve a $ref
resolved = comp_mgr.resolve_reference("#/components/schemas/User")
```

`ComponentType` values: `"schemas" | "responses" | "parameters" | "examples" | "requestBodies" | "headers" | "securitySchemes" | "links" | "callbacks"`

## SampleGenerator — Generate Example Data

```python
gen = SampleGenerator(doc)

sample = gen.generate_from_schema({
    "type": "object",
    "required": ["name"],
    "properties": {
        "name":  {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "age":   {"type": "integer", "minimum": 0, "maximum": 120}
    }
})
# → {"name": "AbcDef", "email": "user@example.com", "age": 42}
```

Supports: `string` (with formats: email, uri, date, date-time, uuid), `integer`, `number`, `boolean`, `array`, `object`, `$ref`, `enum`.

## CurlGenerator — Generate curl Commands

```python
curl_gen = CurlGenerator(doc)

cmd = curl_gen.generate_curl(
    path="/users",
    method="post",
    base_url="https://api.example.com",
    include_sample_body=True
)
print(cmd)
# curl -X POST \
#   -H 'Content-Type: application/json' \
#   -d '{"name": "AbcDef", ...}' \
#   'https://api.example.com/users'
```

Raises `NotFoundError` if the operation doesn't exist.

## CodeGenerator — Generate Client Code

```python
codegen = CodeGenerator(doc)

python_code = codegen.generate_client("python")
js_code     = codegen.generate_client("javascript")
ts_code     = codegen.generate_client("typescript")
```

`Language` is `Literal["python", "javascript", "typescript"]`.

Generated Python uses `requests`, JS/TS use `fetch`.

---

## Full Example

```python
from pylaag.openapi import OpenAPIDocument, PathManager, ComponentManager, SampleGenerator

doc = OpenAPIDocument()
doc._document["info"]["title"] = "Users API"

comp_mgr = ComponentManager(doc)
comp_mgr.add_component("schemas", "User", {
    "type": "object",
    "properties": {
        "id":   {"type": "integer"},
        "name": {"type": "string"},
    }
})

path_mgr = PathManager(doc)
path_mgr.add_operation("/users", "get", {
    "operationId": "listUsers",
    "responses": {
        "200": {
            "description": "List of users",
            "content": {
                "application/json": {
                    "schema": {"type": "array", "items": {"$ref": "#/components/schemas/User"}}
                }
            }
        }
    }
})

doc.validate()
print(doc.to_yaml())
```
