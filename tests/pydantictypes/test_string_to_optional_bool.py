"""Tests for string_to_optional_bool.py."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING
from typing import Any

import pytest
from pydantic.dataclasses import dataclass
from pydantic_core import ValidationError

from pydantictypes.string_to_optional_bool import StringToBoolean
from pydantictypes.string_to_optional_bool import StringToOptionalBool
from tests.pydantictypes import BaseTestImportFallback
from tests.pydantictypes import create

if TYPE_CHECKING:
    from types import ModuleType


@dataclass
class Stub:
    value: StringToOptionalBool


class TestStringToBoolean:
    """Tests for StringToBoolean enum."""

    def test_true_value(self) -> None:
        """Test True value."""
        assert StringToBoolean(value=True).value is True

    def test_false_value(self) -> None:
        """Test False value."""
        assert StringToBoolean(value=False).value is False

    def test_str_true(self) -> None:
        """Test string representation of True."""
        assert str(StringToBoolean(value=True)) == "1"

    def test_str_false(self) -> None:
        """Test string representation of False."""
        assert str(StringToBoolean(value=False)) == "0"


class Test:
    """Tests for StringToOptionalBool."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("1", StringToBoolean(value=True)),
            ("0", StringToBoolean(value=False)),
            ("", None),
        ],
    )
    def test(self, value: str, expected: StringToBoolean | None) -> None:
        """Property should be converted to optional bool."""
        stub = create(Stub, [value])
        if expected is None:
            assert stub.value is None
        else:
            assert isinstance(stub.value, StringToBoolean)
            assert stub.value.value == expected.value

    @pytest.mark.parametrize(
        "value",
        [
            "true",
            "false",
            "True",
            "False",
            "yes",
            "no",
            "2",
            "-1",
            " ",
            None,
            datetime.date(2020, 1, 1),
            1,
            0,
            True,
            False,
        ],
    )
    # Reason: Need Any to test various invalid types in parametrized test
    def test_error(self, value: Any) -> None:  # noqa: ANN401
        """Only '1', '0', or '' should be accepted."""
        with pytest.raises((ValidationError, TypeError, ValueError)):
            create(Stub, [value])


class TestImportFallback(BaseTestImportFallback):
    """Tests for import fallback scenarios."""

    def get_module(self) -> ModuleType:
        """Return the module to test for import fallback."""
        # Reason: For testing import fallback behavior
        from pydantictypes import string_to_optional_bool  # pylint: disable=import-outside-toplevel  # noqa: PLC0415

        return string_to_optional_bool

    def supports_unpack_fallback(self) -> bool:
        """This module does not support Unpack fallback testing."""
        return False
