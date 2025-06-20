"""Validators."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from typing import Any
from typing import Union

# pylint: disable=no-name-in-module
from pydantic.v1.validators import int_validator
from pydantic.v1.validators import number_multiple_validator
from pydantic.v1.validators import number_size_validator
from pydantic.v1.validators import strict_int_validator

if TYPE_CHECKING:
    from pydantic.v1.fields import ModelField  # pylint: disable=no-name-in-module,unused-import


Number = Union[int, float, Decimal]


# Reason: This Any is correct
def optional_strict_int_validator(value: Any) -> int | None:  # noqa: ANN401
    if value is None:
        return None
    return strict_int_validator(value)


# Reason: This Any is correct
def optional_int_validator(value: Any) -> int | None:  # noqa: ANN401
    if value is None:
        return None
    return int_validator(value)


def optional_number_size_validator(value: Number | None, field: ModelField) -> Number | None:
    if value is None:
        return None
    return number_size_validator(value, field)


def optional_number_multiple_validator(value: Number | None, field: ModelField) -> Number | None:
    if value is None:
        return None
    return number_multiple_validator(value, field)


# Reason: This Any is correct
def string_validator(value: Any) -> str:  # noqa: ANN401
    if not isinstance(value, str):
        msg = "string required"
        raise TypeError(msg)
    return value
