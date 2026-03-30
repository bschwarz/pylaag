"""Property-based tests for error handling."""

from hypothesis import given
from hypothesis import strategies as st
from pylaag.core.errors import LaagError, NotFoundError, ParseError, ValidationError


@given(
    message=st.text(min_size=1, max_size=200),
    context_dict=st.dictionaries(
        keys=st.text(min_size=1, max_size=50),
        values=st.one_of(
            st.text(max_size=100),
            st.integers(),
            st.floats(allow_nan=False, allow_infinity=False),
            st.booleans(),
            st.none(),
        ),
        max_size=10,
    ),
)
def test_error_context_preservation(message: str, context_dict: dict) -> None:
    """
    Feature: laag-python-port, Property 8: Error Context Preservation

    **Validates: Requirements 2.5**

    For any error raised by the library (ValidationError, ParseError, NotFoundError),
    the exception should have a context attribute containing relevant information.
    """
    # Test LaagError base class
    error = LaagError(message, context_dict)
    assert error.context == context_dict
    assert str(error) == message

    # Test ValidationError
    validation_error = ValidationError(message, context_dict)
    assert validation_error.context == context_dict
    assert str(validation_error) == message

    # Test ParseError
    parse_error = ParseError(message, context_dict)
    assert parse_error.context == context_dict
    assert str(parse_error) == message

    # Test NotFoundError
    not_found_error = NotFoundError(message, context_dict)
    assert not_found_error.context == context_dict
    assert str(not_found_error) == message


@given(message=st.text(min_size=1, max_size=200))
def test_error_context_defaults_to_empty_dict(message: str) -> None:
    """
    Feature: laag-python-port, Property 8: Error Context Preservation

    **Validates: Requirements 2.5**

    When no context is provided, the error should have an empty dictionary as context.
    """
    error = LaagError(message)
    assert error.context == {}
    assert isinstance(error.context, dict)

    validation_error = ValidationError(message)
    assert validation_error.context == {}

    parse_error = ParseError(message)
    assert parse_error.context == {}

    not_found_error = NotFoundError(message)
    assert not_found_error.context == {}
