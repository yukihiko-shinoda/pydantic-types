"""Tests for symbol_yen_string_to_int.py ."""

import datetime
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable

import pytest
from pydantic import ValidationError
from pydantic.dataclasses import dataclass

from pydantictypes.symbol_yen_string_to_int import SymbolYenStringToInt
from pydantictypes.symbol_yen_string_to_int import constringtoint
from tests.pydantictypes import BaseTestConstraintFunction
from tests.pydantictypes import BaseTestImportFallback
from tests.pydantictypes import create

if TYPE_CHECKING:
    from types import ModuleType


@dataclass
class Stub:
    int_: SymbolYenStringToInt


class Test:
    """Tests for SymbolYenStringToInt."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (r"\1", 1),
            (r"\1,000", 1000),
            (r"\1,000,000", 1000000),
        ],
    )
    def test(self, value: str, expected: int) -> None:
        """Property should be converted to int."""
        stub = create(Stub, [value])
        assert stub.int_ == expected
        assert isinstance(stub.int_, int)

    @pytest.mark.parametrize(
        "value",
        [
            r"\1.0",
            r"\1,000.0",
            r"\1,000,000.0",
            # r"\1,000,000 \1,000,000",
            # r"\1000000",
            # r"\1,000,000円",
            # r"\1 円",
            # r"\1円",
            # r"\1 ドル",
            # r"\1ドル",
            r"¥1",
            r"¥ 1",
            r"$1",
            r"$ 1",
            "",
            None,
            datetime.date(2020, 1, 1),
            1,
        ],
    )
    # Reason: This Any is correct
    def test_error(self, value: Any) -> None:  # noqa: ANN401
        """Property should be converted to int."""
        with pytest.raises(ValidationError):
            create(Stub, [value])


class TestConstraintFunction(BaseTestConstraintFunction):
    """Tests for constringtoint function."""

    def get_constraint_function(self) -> Callable[..., Any]:
        """Return the constringtoint function for this module."""
        return constringtoint


class TestImportFallback(BaseTestImportFallback):
    """Tests for import fallback behavior."""

    def get_module(self) -> "ModuleType":
        """Return the module to test for import fallback."""
        # Reason: For testing import fallback behavior
        from pydantictypes import symbol_yen_string_to_int  # pylint: disable=import-outside-toplevel  # noqa: PLC0415

        return symbol_yen_string_to_int
