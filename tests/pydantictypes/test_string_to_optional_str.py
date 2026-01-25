"""Tests for string_to_optional_str.py."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING
from typing import Any

import pytest
from pydantic.dataclasses import dataclass
from pydantic_core import ValidationError

from pydantictypes.string_to_optional_str import StringToOptionalStr  # noqa: TC001
from pydantictypes.string_to_optional_str import constringtooptionalstr  # noqa: TC001
from tests.pydantictypes import BaseTestImportFallback
from tests.pydantictypes import create

if TYPE_CHECKING:
    from types import ModuleType


@dataclass
class Stub:
    value: StringToOptionalStr


class Test:
    """Tests for StringToOptionalStr."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("hello", "hello"),
            ("world", "world"),
            ("123", "123"),
            ("", None),
        ],
    )
    def test(self, value: str, expected: str | None) -> None:
        """Property should be converted to optional str."""
        stub = create(Stub, [value])
        assert stub.value == expected

    @pytest.mark.parametrize(
        "value",
        [
            None,
            datetime.date(2020, 1, 1),
            1,
            123,
            True,
            False,
        ],
    )
    # Reason: Need Any to test various invalid types in parametrized test
    def test_error(self, value: Any) -> None:  # noqa: ANN401
        """Only string should be accepted."""
        with pytest.raises((ValidationError, TypeError)):
            create(Stub, [value])


class TestConstraints:
    """Tests for constringtooptionalstr with various constraints."""

    def test_strip_whitespace(self) -> None:
        """Test strip_whitespace constraint."""

        @dataclass
        class StubStrip:
            value: constringtooptionalstr(strip_whitespace=True)  # type: ignore[valid-type]

        stub = create(StubStrip, ["  hello  "])
        assert stub.value == "hello"

    def test_to_lower(self) -> None:
        """Test to_lower constraint."""

        @dataclass
        class StubLower:
            value: constringtooptionalstr(to_lower=True)  # type: ignore[valid-type]

        stub = create(StubLower, ["HELLO"])
        assert stub.value == "hello"

    def test_min_length(self) -> None:
        """Test min_length constraint."""

        @dataclass
        class StubMinLength:
            value: constringtooptionalstr(min_length=5)  # type: ignore[valid-type]

        stub = create(StubMinLength, ["hello"])
        assert stub.value == "hello"

        with pytest.raises(ValidationError):
            create(StubMinLength, ["hi"])

    def test_max_length(self) -> None:
        """Test max_length constraint."""

        @dataclass
        class StubMaxLength:
            value: constringtooptionalstr(max_length=5)  # type: ignore[valid-type]

        stub = create(StubMaxLength, ["hello"])
        assert stub.value == "hello"

        with pytest.raises(ValidationError):
            create(StubMaxLength, ["toolong"])

    def test_curtail_length(self) -> None:
        """Test curtail_length constraint."""

        @dataclass
        class StubCurtail:
            value: constringtooptionalstr(curtail_length=5)  # type: ignore[valid-type]

        stub = create(StubCurtail, ["hello world"])
        assert stub.value == "hello"

    def test_regex(self) -> None:
        """Test regex constraint."""

        @dataclass
        class StubRegex:
            value: constringtooptionalstr(regex=r"^[0-9]{3}$")  # type: ignore[valid-type]  # noqa: F722,RUF100

        stub = create(StubRegex, ["123"])
        assert stub.value == "123"

        with pytest.raises(ValidationError):
            create(StubRegex, ["abc"])

        with pytest.raises(ValidationError):
            create(StubRegex, ["1234"])

    def test_combined_constraints(self) -> None:
        """Test multiple constraints combined."""

        @dataclass
        class StubCombined:
            value: constringtooptionalstr(  # type: ignore[valid-type]
                strip_whitespace=True,
                to_lower=True,
                min_length=3,
                max_length=10,
            )

        stub = create(StubCombined, ["  HELLO  "])
        assert stub.value == "hello"

        with pytest.raises(ValidationError):
            create(StubCombined, ["  HI  "])  # Too short after stripping

    def test_empty_string_returns_none(self) -> None:
        """Test that empty string returns None with constraints."""

        @dataclass
        class StubEmpty:
            value: constringtooptionalstr(min_length=5)  # type: ignore[valid-type]

        stub = create(StubEmpty, [""])
        assert stub.value is None


class TestImportFallback(BaseTestImportFallback):
    """Tests for import fallback scenarios."""

    def get_module(self) -> ModuleType:
        """Return the module to test for import fallback."""
        # Reason: For testing import fallback behavior
        from pydantictypes import string_to_optional_str  # pylint: disable=import-outside-toplevel  # noqa: PLC0415

        return string_to_optional_str

    def supports_unpack_fallback(self) -> bool:
        """This module does not support Unpack fallback testing."""
        return False
