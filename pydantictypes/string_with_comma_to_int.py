"""Custom data type to convert string with comma to int."""

from __future__ import annotations

import annotated_types
from pydantic import BeforeValidator

from pydantictypes.abstract_string_to_int import IntegerMustBeFromStr
from pydantictypes.utility import Utility

try:
    from typing import Annotated
except ImportError:
    # Reason: Maybe mypy's bug
    from typing_extensions import Annotated  # type: ignore[assignment]

__all__ = [
    "StrictStringWithCommaToInt",
]


# Reason: Followed Pydantic specification.
def constringtoint(  # noqa: PLR0913  # pylint: disable=too-many-arguments
    *,
    strict: bool | None = None,  # noqa: ARG001  # pylint: disable=unused-argument
    gt: int | None = None,
    ge: int | None = None,
    lt: int | None = None,
    le: int | None = None,
    multiple_of: int | None = None,
) -> type[int]:
    """A wrapper around `int` that allows for additional constraints.

    Args:
        strict: Whether to validate the integer in strict mode. Defaults to `None`.
        gt: The value must be greater than this.
        ge: The value must be greater than or equal to this.
        lt: The value must be less than this.
        le: The value must be less than or equal to this.
        multiple_of: The value must be a multiple of this.

    Returns:
        The wrapped integer type.
    """
    return Annotated[  # type: ignore[return-value]
        int,
        BeforeValidator(IntegerMustBeFromStr(Utility.convert_string_with_comma_to_int).validate),
        annotated_types.Interval(gt=gt, ge=ge, lt=lt, le=le),
        annotated_types.MultipleOf(multiple_of) if multiple_of is not None else None,
    ]


StrictStringWithCommaToInt = Annotated[
    int,
    BeforeValidator(IntegerMustBeFromStr(Utility.convert_string_with_comma_to_int).validate),
]
