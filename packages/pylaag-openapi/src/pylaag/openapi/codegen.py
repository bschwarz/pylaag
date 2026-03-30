"""Code generation from OpenAPI documents."""

from typing import Any, Literal

from pylaag.openapi.document import OpenAPIDocument

Language = Literal["python", "javascript", "typescript"]


class CodeGenerator:
    """Generates client code from OpenAPI documents."""

    def __init__(self, document: OpenAPIDocument):
        """Initialize the code generator.

        Args:
            document: The OpenAPI document to generate code from
        """
        self.document = document

    def generate_client(self, language: Language) -> str:
        """Generate a complete client in the specified language.

        Args:
            language: The target language ('python', 'javascript', or 'typescript')

        Returns:
            The generated client code as a string

        Raises:
            ValueError: If the language is not supported
        """
        if language == "python":
            return self._generate_python_client()
        elif language == "javascript":
            return self._generate_javascript_client()
        elif language == "typescript":
            return self._generate_typescript_client()
        else:
            raise ValueError(f"Unsupported language: {language}")

    def _generate_python_client(self) -> str:
        """Generate a Python client.

        Returns:
            The generated Python client code
        """
        info = self.document.info
        # Sanitize title for use as a Python class name
        title = info.get("title", "API")
        # Remove all non-alphanumeric characters except spaces and hyphens first
        import re

        title = re.sub(r"[^a-zA-Z0-9\s\-]", "", title)
        # Then remove spaces and hyphens
        title = title.replace(" ", "").replace("-", "")
        # Ensure it's not empty
        if not title:
            title = "API"
        description = info.get("description", "")
        version = info.get("version", "1.0.0")

        code = f'''"""
{info.get("title", "API")} Client
{description}

Version: {version}
"""

import requests
from typing import Dict, Any, Optional


class {title}Client:
    """Client for {info.get("title", "API")}."""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """Initialize the client.

        Args:
            base_url: The base URL for the API
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()

        if api_key:
            self.session.headers["Authorization"] = f"Bearer {{api_key}}"
'''

        # Generate methods for each operation
        for path, path_item in self.document.paths.items():
            for method in ["get", "post", "put", "delete", "patch"]:
                if method in path_item:
                    operation = path_item[method]
                    code += self._generate_python_method(path, method, operation)

        return code

    def _generate_python_method(self, path: str, method: str, operation: dict[str, Any]) -> str:
        """Generate a Python method for an operation.

        Args:
            path: The API path
            method: The HTTP method
            operation: The operation definition

        Returns:
            The generated Python method code
        """
        operation_id = operation.get("operationId", f"{method}_{path.replace('/', '_').strip('_')}")
        # Escape backslashes in summary to avoid invalid escape sequences in docstrings
        summary = operation.get("summary", "").replace("\\", "\\\\")

        # Convert path parameters to Python format
        python_path = path
        params = []

        for param in operation.get("parameters", []):
            if param.get("in") == "path":
                param_name = param["name"]
                params.append(param_name)
                python_path = python_path.replace(f"{{{param_name}}}", f"{{{param_name}}}")

        # Build parameter list
        param_list = ", ".join(params) if params else ""
        if param_list:
            param_list += ", "

        method_code = f'''

    def {operation_id}(self, {param_list}**kwargs) -> Dict[str, Any]:
        """
        {summary}
        """
        url = f"{{self.base_url}}{python_path}"
        response = self.session.{method}(url, **kwargs)
        response.raise_for_status()
        return response.json()
'''

        return method_code

    def _generate_javascript_client(self) -> str:
        """Generate a JavaScript client.

        Returns:
            The generated JavaScript client code
        """
        info = self.document.info
        # Sanitize title for use as a JavaScript class name
        import re

        title = info.get("title", "API")
        title = re.sub(r"[^a-zA-Z0-9\s\-]", "", title)
        title = title.replace(" ", "").replace("-", "")
        if not title:
            title = "API"
        description = info.get("description", "")
        version = info.get("version", "1.0.0")

        code = f"""/**
 * {info.get("title", "API")} Client
 * {description}
 *
 * Version: {version}
 */

class {title}Client {{
    constructor(baseUrl, apiKey = null) {{
        this.baseUrl = baseUrl.replace(/\\/$/, "");
        this.apiKey = apiKey;
    }}

    async _request(method, path, options = {{}}) {{
        const url = `${{this.baseUrl}}${{path}}`;
        const headers = {{
            "Content-Type": "application/json",
            ...options.headers
        }};

        if (this.apiKey) {{
            headers["Authorization"] = `Bearer ${{this.apiKey}}`;
        }}

        const response = await fetch(url, {{
            method,
            headers,
            ...options
        }});

        if (!response.ok) {{
            throw new Error(`HTTP error! status: ${{response.status}}`);
        }}

        return response.json();
    }}
"""

        # Generate methods for each operation
        for path, path_item in self.document.paths.items():
            for method in ["get", "post", "put", "delete", "patch"]:
                if method in path_item:
                    operation = path_item[method]
                    code += self._generate_javascript_method(path, method, operation)

        code += "\n}\n\nmodule.exports = " + title + "Client;\n"

        return code

    def _generate_javascript_method(self, path: str, method: str, operation: dict[str, Any]) -> str:
        """Generate a JavaScript method for an operation.

        Args:
            path: The API path
            method: The HTTP method
            operation: The operation definition

        Returns:
            The generated JavaScript method code
        """
        operation_id = operation.get("operationId", f"{method}_{path.replace('/', '_').strip('_')}")
        summary = operation.get("summary", "")

        params = []
        for param in operation.get("parameters", []):
            if param.get("in") == "path":
                params.append(param["name"])

        js_path = path
        for param in params:
            js_path = js_path.replace(f"{{{param}}}", f"${{{param}}}")

        # Build parameter list
        param_list = ", ".join(params) if params else ""
        if param_list:
            param_list += ", "

        method_code = f'''

    /**
     * {summary}
     */
    async {operation_id}({param_list}options = {{}}) {{
        return this._request("{method.upper()}", `{js_path}`, options);
    }}
'''

        return method_code

    def _generate_typescript_client(self) -> str:
        """Generate a TypeScript client.

        Returns:
            The generated TypeScript client code
        """
        info = self.document.info
        # Sanitize title for use as a TypeScript class name
        import re

        title = info.get("title", "API")
        title = re.sub(r"[^a-zA-Z0-9\s\-]", "", title)
        title = title.replace(" ", "").replace("-", "")
        if not title:
            title = "API"
        description = info.get("description", "")
        version = info.get("version", "1.0.0")

        code = f"""/**
 * {info.get("title", "API")} Client
 * {description}
 *
 * Version: {version}
 */

export class {title}Client {{
    constructor(private baseUrl: string, private apiKey: string | null = null) {{
        this.baseUrl = baseUrl.replace(/\\/$/, "");
    }}

    private async _request(
        method: string,
        path: string,
        options: RequestInit = {{}}
    ): Promise<any> {{
        const url = `${{this.baseUrl}}${{path}}`;
        const headers: Record<string, string> = {{
            "Content-Type": "application/json",
            ...(options.headers as Record<string, string> || {{}})
        }};

        if (this.apiKey) {{
            headers["Authorization"] = `Bearer ${{this.apiKey}}`;
        }}

        const response = await fetch(url, {{
            method,
            headers,
            ...options
        }});

        if (!response.ok) {{
            throw new Error(`HTTP error! status: ${{response.status}}`);
        }}

        return response.json();
    }}
"""

        # Generate methods for each operation
        for path, path_item in self.document.paths.items():
            for method in ["get", "post", "put", "delete", "patch"]:
                if method in path_item:
                    operation = path_item[method]
                    code += self._generate_typescript_method(path, method, operation)

        code += "\n}\n"

        return code

    def _generate_typescript_method(self, path: str, method: str, operation: dict[str, Any]) -> str:
        """Generate a TypeScript method for an operation.

        Args:
            path: The API path
            method: The HTTP method
            operation: The operation definition

        Returns:
            The generated TypeScript method code
        """
        operation_id = operation.get("operationId", f"{method}_{path.replace('/', '_').strip('_')}")
        summary = operation.get("summary", "")

        params = []
        param_types = []
        for param in operation.get("parameters", []):
            if param.get("in") == "path":
                param_name = param["name"]
                params.append(param_name)
                # Simple type mapping
                param_type = "string"
                if param.get("schema", {}).get("type") == "integer":
                    param_type = "number"
                param_types.append(f"{param_name}: {param_type}")

        ts_path = path
        for param in params:
            ts_path = ts_path.replace(f"{{{param}}}", f"${{{param}}}")

        # Build parameter list
        param_list = ", ".join(param_types) if param_types else ""
        if param_list:
            param_list += ", "

        method_code = f'''

    /**
     * {summary}
     */
    async {operation_id}({param_list}options: RequestInit = {{}}): Promise<any> {{
        return this._request("{method.upper()}", `{ts_path}`, options);
    }}
'''

        return method_code
