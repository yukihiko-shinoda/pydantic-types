"""Custom data type to convert string with comma to optional int."""

from __future__ import annotations

from contextlib import suppress
from sys import version_info
from typing import Optional

import annotated_types
from pydantic import BeforeValidator

from pydantictypes.abstract_string_to_optional_int import OptionalIntegerMustBeFromStr
from pydantictypes.utility import Utility

# Reason: To use raw typing imports pylint: disable=duplicate-code
try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated
with suppress(ImportError):
    from typing import Unpack

__all__ = [
    "StrictStringWithCommaToOptionalInt",
    "constringwithcommatooptionalint",
]


# Reason: Constraint parameters follow Pydantic specification (gt, ge, lt, le, multiple_of)
def constringwithcommatooptionalint(  # noqa: PLR0913 pylint: disable=too-many-arguments
    *,
    # Reason: Kept for backward compatibility but no longer used in Pydantic v2
    strict: bool = False,  # noqa: ARG001  # pylint: disable=unused-argument
    # Reason: Short parameter names follow Pydantic specification
    gt: int | None = None,  # pylint: disable=invalid-name
    ge: int | None = None,  # pylint: disable=invalid-name
    lt: int | None = None,  # pylint: disable=invalid-name
    le: int | None = None,  # pylint: disable=invalid-name
    multiple_of: int | None = None,
) -> type[int | None]:
    """A wrapper around `int` that allows for additional constraints.

    Args:
        strict: Whether to validate the integer in strict mode. Defaults to `None`.
            Note: This parameter is kept for backward compatibility but is no longer used.
        gt: The value must be greater than this.
        ge: The value must be greater than or equal to this.
        lt: The value must be less than this.
        le: The value must be less than or equal to this.
        multiple_of: The value must be a multiple of this.

    Returns:
        The wrapped integer type.
    """
    # Create validator with constraints - constraints are validated in the validator itself
    validator = OptionalIntegerMustBeFromStr(
        Utility.convert_string_with_comma_to_int,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
    )
    before_validator = BeforeValidator(validator.validate)

    # Build constraint metadata for schema/documentation purposes
    constraints = [
        annotated_types.Interval(gt=gt, ge=ge, lt=lt, le=le),
        annotated_types.MultipleOf(multiple_of) if multiple_of is not None else None,
    ]

    # Reason: Following block is tested in different workflows in GitHub Actions
    if version_info < (3, 11):  # pragma: no cover
        # Filter out None values
        valid_constraints = tuple(c for c in constraints if c is not None)
        # Reason: Cannot use star expression in index on Python 3.7 (syntax was added in Python 3.11)
        annotations = (Optional[int], before_validator) + valid_constraints  # noqa: RUF005
        return Annotated[annotations]  # type: ignore[return-value]
    return Annotated[Optional[int], before_validator, Unpack[constraints]]  # type: ignore[return-value]


# Basic type without constraints (for simple string with comma to optional int conversion)
StrictStringWithCommaToOptionalInt = Annotated[
    Optional[int],
    BeforeValidator(OptionalIntegerMustBeFromStr(Utility.convert_string_with_comma_to_int).validate),
]
