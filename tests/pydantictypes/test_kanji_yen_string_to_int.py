"""Tests for string_with_comma_to_int.py ."""

import datetime
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable

import pytest
from pydantic.dataclasses import dataclass
from pydantic_core import ValidationError

from pydantictypes.kanji_yen_string_to_int import StrictKanjiYenStringToInt
from pydantictypes.kanji_yen_string_to_int import constringtoint
from tests.pydantictypes import BaseTestConstraintFunction
from tests.pydantictypes import BaseTestImportFallback
from tests.pydantictypes import create

if TYPE_CHECKING:
    from types import ModuleType


@dataclass
class Stub:
    int_: StrictKanjiYenStringToInt


# Reason: It's impossible to reduce duplicate code due to pytest's specification.
class Test:  # pylint: disable=duplicate-code
    """Tests for StrictKanjiYenStringToInt."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("1 円", 1),
            ("1,000 円", 1000),
            ("1,000,000 円", 1000000),
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
            "1.0 円",
            "1.0,000 円",
            "1,000.0 円",
            "1,000,000.0",
            "1,000,000",
            # "1,000,000 円 1,000,000 円",
            # "1,000,000 円 1,000,000",
            # "1,000,000 1,000,000 円",
            "1,000,000 1,000,000",
            # "1000000 円",
            "1000000",
            # "1,000,000円",
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
    # Reason: Need Any to test various invalid types in parametrized test
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
        from pydantictypes import kanji_yen_string_to_int  # pylint: disable=import-outside-toplevel  # noqa: PLC0415

        return kanji_yen_string_to_int
