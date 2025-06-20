"""Tests for string_to_optional_int.py ."""

import datetime
from typing import Any

import pytest
from pydantic.dataclasses import dataclass
from pydantic_core import ValidationError

from pydantictypes.string_to_optional_int import ConstrainedStringToOptionalInt
from tests.pydantictypes import create


@dataclass
class Stub:
    int_: ConstrainedStringToOptionalInt


class Test:
    """Tests for ConstrainedStringToOptionalInt."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("1", 1),
            ("1000", 1000),
            ("1000000", 1000000),
            ("", None),
        ],
    )
    def test(self, value: str, expected: int) -> None:
        """Property should be converted to int."""
        stub = create(Stub, [value])
        assert isinstance(stub.int_, type(expected))
        assert stub.int_ == expected

    @pytest.mark.parametrize(
        "value",
        [
            "1.0",
            "1,000",
            "1000000 1000000",
            "1 円",
            "1円",
            "1 ドル",
            "1ドル",
            "¥1",
            "¥ 1",
            "$1",
            "$ 1",
            None,
            datetime.date(2020, 1, 1),
            1,
        ],
    )
    # Reason: This Any is correct
    def test_error(self, value: Any) -> None:  # noqa: ANN401
        """Property should be converted to int."""
        with pytest.raises((ValidationError, TypeError)):
            create(Stub, [value])
