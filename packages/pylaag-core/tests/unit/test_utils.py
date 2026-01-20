"""Unit tests for utility functions."""

from pylaag_core.utils import delete_nested, get_nested, set_nested


class TestGetNested:
    """Tests for get_nested function."""

    def test_get_single_level(self) -> None:
        """Test getting a value at a single level."""
        obj = {"a": 1}
        assert get_nested(obj, "a") == 1

    def test_get_nested_value(self) -> None:
        """Test getting a nested value."""
        obj = {"a": {"b": {"c": 1}}}
        assert get_nested(obj, "a.b.c") == 1

    def test_get_nested_with_multiple_levels(self) -> None:
        """Test getting values at various depths."""
        obj = {"a": {"b": {"c": {"d": {"e": 42}}}}}
        assert get_nested(obj, "a") == {"b": {"c": {"d": {"e": 42}}}}
        assert get_nested(obj, "a.b") == {"c": {"d": {"e": 42}}}
        assert get_nested(obj, "a.b.c") == {"d": {"e": 42}}
        assert get_nested(obj, "a.b.c.d") == {"e": 42}
        assert get_nested(obj, "a.b.c.d.e") == 42

    def test_get_missing_key_returns_default(self) -> None:
        """Test that missing keys return the default value."""
        obj = {"a": {"b": 1}}
        assert get_nested(obj, "a.c") is None
        assert get_nested(obj, "a.c", "default") == "default"
        assert get_nested(obj, "x.y.z", 42) == 42

    def test_get_empty_path(self) -> None:
        """Test getting with an empty path."""
        obj = {"": "value"}
        assert get_nested(obj, "") == "value"

    def test_get_non_dict_intermediate_returns_default(self) -> None:
        """Test that non-dict intermediate values return default."""
        obj = {"a": "string", "b": 123}
        assert get_nested(obj, "a.b") is None
        assert get_nested(obj, "b.c", "default") == "default"

    def test_get_with_various_value_types(self) -> None:
        """Test getting various value types."""
        obj = {
            "string": "hello",
            "number": 42,
            "float": 3.14,
            "bool": True,
            "none": None,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
        }
        assert get_nested(obj, "string") == "hello"
        assert get_nested(obj, "number") == 42
        assert get_nested(obj, "float") == 3.14
        assert get_nested(obj, "bool") is True
        assert get_nested(obj, "none") is None
        assert get_nested(obj, "list") == [1, 2, 3]
        assert get_nested(obj, "dict") == {"nested": "value"}


class TestSetNested:
    """Tests for set_nested function."""

    def test_set_single_level(self) -> None:
        """Test setting a value at a single level."""
        obj: dict = {}
        set_nested(obj, "a", 1)
        assert obj == {"a": 1}

    def test_set_nested_value(self) -> None:
        """Test setting a nested value."""
        obj: dict = {}
        set_nested(obj, "a.b.c", 1)
        assert obj == {"a": {"b": {"c": 1}}}

    def test_set_nested_creates_intermediate_dicts(self) -> None:
        """Test that intermediate dictionaries are created."""
        obj: dict = {}
        set_nested(obj, "a.b.c.d.e", 42)
        assert obj == {"a": {"b": {"c": {"d": {"e": 42}}}}}

    def test_set_overwrites_existing_value(self) -> None:
        """Test that existing values are overwritten."""
        obj = {"a": {"b": {"c": 1}}}
        set_nested(obj, "a.b.c", 2)
        assert obj == {"a": {"b": {"c": 2}}}

    def test_set_preserves_sibling_values(self) -> None:
        """Test that sibling values are preserved."""
        obj = {"a": {"b": 1, "c": 2}}
        set_nested(obj, "a.d", 3)
        assert obj == {"a": {"b": 1, "c": 2, "d": 3}}

    def test_set_with_various_value_types(self) -> None:
        """Test setting various value types."""
        obj: dict = {}
        set_nested(obj, "string", "hello")
        set_nested(obj, "number", 42)
        set_nested(obj, "float", 3.14)
        set_nested(obj, "bool", True)
        set_nested(obj, "none", None)
        set_nested(obj, "list", [1, 2, 3])
        set_nested(obj, "dict", {"nested": "value"})

        assert obj == {
            "string": "hello",
            "number": 42,
            "float": 3.14,
            "bool": True,
            "none": None,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
        }

    def test_set_empty_path(self) -> None:
        """Test setting with an empty path."""
        obj: dict = {}
        set_nested(obj, "", "value")
        assert obj == {"": "value"}


class TestDeleteNested:
    """Tests for delete_nested function."""

    def test_delete_single_level(self) -> None:
        """Test deleting a value at a single level."""
        obj = {"a": 1}
        assert delete_nested(obj, "a") is True
        assert obj == {}

    def test_delete_nested_value(self) -> None:
        """Test deleting a nested value."""
        obj = {"a": {"b": {"c": 1}}}
        assert delete_nested(obj, "a.b.c") is True
        assert obj == {"a": {"b": {}}}

    def test_delete_preserves_siblings(self) -> None:
        """Test that sibling values are preserved."""
        obj = {"a": {"b": 1, "c": 2, "d": 3}}
        assert delete_nested(obj, "a.c") is True
        assert obj == {"a": {"b": 1, "d": 3}}

    def test_delete_missing_key_returns_false(self) -> None:
        """Test that deleting a missing key returns False."""
        obj = {"a": {"b": 1}}
        assert delete_nested(obj, "a.c") is False
        assert delete_nested(obj, "x.y.z") is False
        assert obj == {"a": {"b": 1}}

    def test_delete_non_dict_intermediate_returns_false(self) -> None:
        """Test that non-dict intermediate values return False."""
        obj = {"a": "string"}
        assert delete_nested(obj, "a.b") is False
        assert obj == {"a": "string"}

    def test_delete_leaves_empty_parent_dicts(self) -> None:
        """Test that parent dictionaries are left empty after deletion."""
        obj = {"a": {"b": {"c": 1}}}
        assert delete_nested(obj, "a.b.c") is True
        assert obj == {"a": {"b": {}}}

    def test_delete_multiple_values(self) -> None:
        """Test deleting multiple values."""
        obj = {"a": {"b": 1, "c": 2}, "d": 3}
        assert delete_nested(obj, "a.b") is True
        assert delete_nested(obj, "d") is True
        assert obj == {"a": {"c": 2}}

    def test_delete_same_key_twice_returns_false_second_time(self) -> None:
        """Test that deleting the same key twice returns False the second time."""
        obj = {"a": {"b": 1}}
        assert delete_nested(obj, "a.b") is True
        assert delete_nested(obj, "a.b") is False
