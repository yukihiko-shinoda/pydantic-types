"""Test for string_with_comma_to_int.py ."""
# pylint: disable=duplicate-code

import datetime
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable

import pytest
from pydantic.dataclasses import dataclass
from pydantic_core import ValidationError

from pydantictypes.string_with_comma_to_int import StrictStringWithCommaToInt
from pydantictypes.string_with_comma_to_int import constringtoint
from tests.pydantictypes import BaseTestConstraintFunction
from tests.pydantictypes import BaseTestImportFallback
from tests.pydantictypes import create

if TYPE_CHECKING:
    from types import ModuleType


@dataclass
class Stub:
    int_: StrictStringWithCommaToInt


# Reason: It's impossible to reduce duplicate code due to pytest's specification.
class Test:  # pylint: disable=duplicate-code
    """Tests for StrictStringWithCommaToInt."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("1", 1),
            ("1,000", 1000),
            ("1,000,000", 1000000),
        ],
    )
    def test(self, value: str, expected: int) -> None:
        """Property should be converted to int."""
        stub = create(Stub, [value])
        assert isinstance(stub.int_, int)
        assert stub.int_ == expected

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
            "",
            None,
            datetime.date(2020, 1, 1),
            1,
        ],
    )
    # Reason: This Any is correct
    def test_error(self, value: Any) -> None:  # noqa: ANN401
        """Pydantic should raise ValidationError."""
        with pytest.raises((ValidationError, TypeError)):
            create(Stub, [value])


class TestConstraintFunction(BaseTestConstraintFunction):
    def get_constraint_function(self) -> Callable[..., Any]:
        return constringtoint


class TestImportFallback(BaseTestImportFallback):
    def get_module(self) -> "ModuleType":
        # Reason: For testing import fallback behavior
        from pydantictypes import string_with_comma_to_int  # pylint: disable=import-outside-toplevel  # noqa: PLC0415

        return string_with_comma_to_int
