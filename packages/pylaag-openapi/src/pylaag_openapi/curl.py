"""Curl command generation from OpenAPI operations."""

import json
from urllib.parse import quote

from pylaag_core import NotFoundError

from pylaag_openapi.document import OpenAPIDocument
from pylaag_openapi.samples import SampleGenerator


class CurlGenerator:
    """Generates curl commands from OpenAPI operations.

    This class can generate curl commands for testing API endpoints,
    including proper handling of headers, request bodies, query parameters,
    and special character escaping.
    """

    def __init__(self, document: OpenAPIDocument):
        """Initialize the CurlGenerator.

        Args:
            document: The OpenAPI document containing operations
        """
        self.document = document
        self.sample_generator = SampleGenerator(document)

    def generate_curl(
        self,
        path: str,
        method: str,
        base_url: str = "https://api.example.com",
        include_sample_body: bool = True,
    ) -> str:
        """Generate a curl command for an operation.

        Args:
            path: The API path (e.g., "/users/{id}")
            method: The HTTP method (e.g., "get", "post")
            base_url: The base URL for the API (default: "https://api.example.com")
            include_sample_body: Whether to include a sample request body (default: True)

        Returns:
            A curl command string with proper escaping

        Raises:
            NotFoundError: If the operation is not found in the document
        """
        operation = self.document._document.get("paths", {}).get(path, {}).get(method)

        if not operation:
            raise NotFoundError(f"Operation not found: {method.upper()} {path}")

        # Build the URL with path parameters
        url = f"{base_url.rstrip('/')}{path}"

        # Replace path parameters with placeholder values
        parameters = operation.get("parameters", [])
        for param in parameters:
            if param.get("in") == "path":
                param_name = param["name"]
                # Use example value if available, otherwise use placeholder
                example_value = param.get("example", f"<{param_name}>")
                url = url.replace(f"{{{param_name}}}", str(example_value))

        # Add query parameters
        query_params = []
        for param in parameters:
            if param.get("in") == "query":
                param_name = param["name"]
                example_value = param.get("example", f"<{param_name}>")
                # URL encode the parameter value
                encoded_value = quote(str(example_value))
                query_params.append(f"{param_name}={encoded_value}")

        if query_params:
            url += "?" + "&".join(query_params)

        # Start building the curl command
        parts = ["curl", "-X", method.upper()]

        # Add headers
        headers = []
        for param in parameters:
            if param.get("in") == "header":
                param_name = param["name"]
                example_value = param.get("example", "<value>")
                # Escape single quotes in header value
                escaped_value = str(example_value).replace("'", "'\\''")
                headers.append(f"-H '{param_name}: {escaped_value}'")

        if "requestBody" in operation and include_sample_body:
            headers.append("-H 'Content-Type: application/json'")

        parts.extend(headers)

        # Add request body
        if "requestBody" in operation and include_sample_body:
            content = operation["requestBody"].get("content", {})
            json_content = content.get("application/json", {})
            schema = json_content.get("schema", {})

            if schema:
                sample = self.sample_generator.generate_from_schema(schema)
                body_json = json.dumps(sample, indent=2)
                # Escape single quotes in JSON
                body_json = body_json.replace("'", "'\\''")
                parts.append(f"-d '{body_json}'")

        # Add URL (escape single quotes)
        escaped_url = url.replace("'", "'\\''")
        parts.append(f"'{escaped_url}'")

        return " \\\n  ".join(parts)
