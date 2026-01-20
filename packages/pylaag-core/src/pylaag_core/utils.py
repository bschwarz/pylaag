"""Utility functions for the laag Python library."""

from typing import Any


def get_nested(obj: dict[str, Any], path: str, default: Any = None) -> Any:
    """Get a nested value from a dictionary using dot notation.

    Args:
        obj: The dictionary to search
        path: Dot-separated path to the value (e.g., 'a.b.c')
        default: Default value to return if path not found

    Returns:
        The value at the specified path, or default if not found

    Example:
        >>> get_nested({'a': {'b': {'c': 1}}}, 'a.b.c')
        1
        >>> get_nested({'a': {'b': {}}}, 'a.b.c', 'not found')
        'not found'
    """
    keys = path.split(".")
    current = obj

    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]

    return current


def set_nested(obj: dict[str, Any], path: str, value: Any) -> None:
    """Set a nested value in a dictionary using dot notation.

    Args:
        obj: The dictionary to modify
        path: Dot-separated path to the value (e.g., 'a.b.c')
        value: The value to set

    Example:
        >>> d = {}
        >>> set_nested(d, 'a.b.c', 1)
        >>> d
        {'a': {'b': {'c': 1}}}
    """
    keys = path.split(".")
    current = obj

    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]

    current[keys[-1]] = value


def delete_nested(obj: dict[str, Any], path: str) -> bool:
    """Delete a nested value from a dictionary using dot notation.

    Args:
        obj: The dictionary to modify
        path: Dot-separated path to the value (e.g., 'a.b.c')

    Returns:
        True if the value was deleted, False if not found

    Example:
        >>> d = {'a': {'b': {'c': 1}}}
        >>> delete_nested(d, 'a.b.c')
        True
        >>> delete_nested(d, 'a.b.c')
        False
    """
    keys = path.split(".")
    current = obj

    for key in keys[:-1]:
        if not isinstance(current, dict) or key not in current:
            return False
        current = current[key]

    if keys[-1] in current:
        del current[keys[-1]]
        return True

    return False
