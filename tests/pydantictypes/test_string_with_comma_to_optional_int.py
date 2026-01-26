"""Test for string_with_comma_to_optional_int.py ."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Optional

import pytest
from pydantic.dataclasses import dataclass

from pydantictypes.string_with_comma_to_optional_int import StrictStringWithCommaToOptionalInt
from pydantictypes.string_with_comma_to_optional_int import constringwithcommatooptionalint
from tests.pydantictypes import BaseTestConstraintFunction
from tests.pydantictypes import BaseTestImportFallback
from tests.pydantictypes import BaseTestOptionalType
from tests.pydantictypes import create

if TYPE_CHECKING:
    from types import ModuleType


@dataclass
class Stub:
    int_: StrictStringWithCommaToOptionalInt


class Test(BaseTestOptionalType):
    """Tests for StrictStringWithCommaToOptionalInt."""

    Stub = Stub

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("1", 1),
            ("1,000", 1000),
            ("1,000,000", 1000000),
            ("", None),
        ],
    )
    def test(self, value: str, expected: int) -> None:
        """Property should be converted to int."""
        stub = create(Stub, [value])
        assert stub.int_ == expected
        assert isinstance(stub.int_, type(expected))

    @pytest.mark.parametrize(
        "value",
        [
            "1.0",
            "1,000.0",
            "1,000,000.0",
            "1,000,000 1,000,000",
            # "1000000",
            "1,000,000円",
            "1 円",
            "1円",
            "1 ドル",
            "1ドル",
            "¥1",
            "¥ 1",
            "$1",
            "$ 1",
            datetime.date(2020, 1, 1),
            1,
        ],
    )
    # Reason: Need Any to test various invalid types in parametrized test
    def test_error(self, value: Any) -> None:  # noqa: ANN401
        """Pydantic should raise ValidationError."""
        self._assert_error_raised(value)


class TestConstraintFunction(BaseTestConstraintFunction):
    """Tests for constringwithcommatooptionalint function."""

    def get_constraint_function(self) -> Callable[..., Any]:
        """Return the constraint function for this module."""
        return constringwithcommatooptionalint

    def get_expected_metadata_count(self) -> int:
        """Return expected metadata count for optional int types."""
        # Only BeforeValidator (no annotated_types metadata to avoid double-validation)
        return 1

    # Any is needed here to match the base class signature and handle Optional[int]
    def get_expected_origin(self) -> Any:  # noqa: ANN401
        """Return expected __origin__ type for optional int types."""
        return Optional[int]

    def supports_constraints(self) -> bool:
        """Optional int types don't support constraint testing."""
        return False


class TestImportFallback(BaseTestImportFallback):
    """Tests for import fallback scenarios."""

    def get_module(self) -> ModuleType:
        """Return the module to test for import fallback."""
        # Reason: For testing import fallback behavior pylint: disable-next=import-outside-toplevel
        from pydantictypes import string_with_comma_to_optional_int  # noqa: PLC0415

        return string_with_comma_to_optional_int

    def supports_unpack_fallback(self) -> bool:
        """This module no longer uses Unpack (removed for Python 3.10 compatibility)."""
        return False
