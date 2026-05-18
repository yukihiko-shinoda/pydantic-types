"""Validators."""

from __future__ import annotations

from typing import Any


# Reason: Pydantic validators must accept Any type to handle various input types
def optional_strict_int_validator(value: Any) -> int | None:  # noqa: ANN401
    """Convert value to int in strict mode, allowing None."""
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        msg = "value is not a valid integer"
        # Reason: must be ValueError: Pydantic v2 only wraps ValueError into ValidationError; otherwise TypeError propagates to the caller uncaught by Pydantic
        raise ValueError(msg)  # noqa: TRY004
    return value


# Reason: Pydantic validators must accept Any type to handle various input types
def optional_int_validator(value: Any) -> int | None:  # noqa: ANN401
    """Convert value to int, allowing None."""
    if value is None:
        return None
    return int(value)


# Reason: Pydantic validators must accept Any type to handle various input types
def string_validator(value: Any) -> str:  # noqa: ANN401
    """Validate that value is a string."""
    if not isinstance(value, str):
        msg = "string required"
        # Reason: must be ValueError: Pydantic v2 only wraps ValueError into ValidationError; otherwise TypeError propagates to the caller uncaught by Pydantic
        raise ValueError(msg)  # noqa: TRY004
    return value
