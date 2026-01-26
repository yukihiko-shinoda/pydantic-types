"""Tests for validators.py."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from typing import Any

import pytest

from pydantictypes.validators import optional_int_validator
from pydantictypes.validators import optional_strict_int_validator
from pydantictypes.validators import string_validator

if TYPE_CHECKING:
    from collections.abc import Callable


class TestOptionalStrictIntValidator:
    """Tests for optional_strict_int_validator."""

    def test_with_none_returns_none(self) -> None:
        """Test that None input returns None."""
        assert optional_strict_int_validator(None) is None

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (5, 5),
            (0, 0),
            (-10, -10),
        ],
    )
    def test_with_valid_int_returns_int(self, value: int, expected: int) -> None:
        """Test that valid integer input returns the integer."""
        assert optional_strict_int_validator(value) == expected

    @pytest.mark.parametrize(
        "value",
        [
            "5",
            "0",
            "-10",
        ],
    )
    def test_with_string_int_raises_error(self, value: str) -> None:
        """Test that string integer input raises TypeError in strict mode."""
        with pytest.raises(TypeError):
            optional_strict_int_validator(value)

    @pytest.mark.parametrize(
        "value",
        [
            5.5,
            5.0,
            -10.7,
        ],
    )
    def test_with_float_raises_error(self, value: float) -> None:
        """Test that float input raises TypeError in strict mode."""
        with pytest.raises(TypeError):
            optional_strict_int_validator(value)

    @pytest.mark.parametrize(
        "value",
        [
            True,
            False,
        ],
    )
    # Reason: Parametrized argument
    def test_with_bool_raises_error(self, value: bool) -> None:  # noqa: FBT001
        """Test that boolean input raises TypeError in strict mode."""
        with pytest.raises(TypeError):
            optional_strict_int_validator(value)


class TestOptionalIntValidator:
    """Tests for optional_int_validator."""

    def test_with_none_returns_none(self) -> None:
        """Test that None input returns None."""
        assert optional_int_validator(None) is None

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (5, 5),
            (0, 0),
            (-10, -10),
        ],
    )
    def test_with_valid_int_returns_int(self, value: int, expected: int) -> None:
        """Test that valid integer input returns the integer."""
        assert optional_int_validator(value) == expected

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("5", 5),
            ("0", 0),
            ("-10", -10),
        ],
    )
    def test_with_string_int_returns_int(self, value: str, expected: int) -> None:
        """Test that string integer input returns integer."""
        assert optional_int_validator(value) == expected

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (5.7, 5),
            (5.0, 5),
            (-10.9, -10),
        ],
    )
    def test_with_float_returns_int(self, value: float, expected: int) -> None:
        """Test that float input returns integer (truncated)."""
        assert optional_int_validator(value) == expected

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (True, 1),
            (False, 0),
        ],
    )
    # Reason: Parametrized argument
    def test_with_bool_returns_int(self, value: bool, expected: int) -> None:  # noqa: FBT001
        """Test that boolean input returns integer (True=1, False=0)."""
        assert optional_int_validator(value) == expected

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (Decimal(5), 5),
            (Decimal("5.7"), 5),
            (Decimal(0), 0),
        ],
    )
    def test_with_decimal_returns_int(self, value: Decimal, expected: int) -> None:
        """Test that Decimal input returns integer."""
        assert optional_int_validator(value) == expected

    @pytest.mark.parametrize(
        "value",
        [
            "not_a_number",
            "abc",
            "5.5.5",
        ],
    )
    def test_with_invalid_string_raises_error(self, value: str) -> None:
        """Test that invalid string input raises ValueError."""
        with pytest.raises(ValueError, match="invalid literal"):
            optional_int_validator(value)


class TestStringValidator:
    """Tests for string_validator."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("hello", "hello"),
            ("", ""),
            ("123", "123"),
            ("こんにちは", "こんにちは"),
        ],
    )
    def test_with_valid_string_returns_string(self, value: str, expected: str) -> None:
        """Test that valid string input returns the string."""
        assert string_validator(value) == expected

    @pytest.mark.parametrize(
        "value",
        [
            123,
            None,
            [],
            {},
            5.5,
        ],
    )
    def test_with_non_string_raises_type_error(self, value: object) -> None:
        """Test that non-string input raises TypeError."""
        with pytest.raises(TypeError, match="string required"):
            string_validator(value)


class TestValidatorErrorHandling:
    """Tests for validator error handling scenarios."""

    @pytest.mark.parametrize(
        "large_value",
        [
            2**63 - 1,
            2**31 - 1,
            1000000,
        ],
    )
    def test_optional_strict_int_validator_with_large_int(self, large_value: int) -> None:
        """Test optional_strict_int_validator with very large integers."""
        assert optional_strict_int_validator(large_value) == large_value

    @pytest.mark.parametrize(
        "large_value",
        [
            2**63 - 1,
            2**31 - 1,
            1000000,
        ],
    )
    def test_optional_int_validator_with_large_string(self, large_value: int) -> None:
        """Test optional_int_validator with very large string numbers."""
        large_string = str(large_value)
        assert optional_int_validator(large_string) == large_value

    @pytest.mark.parametrize(
        "unicode_string",
        [
            "こんにちは",
            "héllo",
            "мир",
        ],
    )
    def test_string_validator_with_unicode(self, unicode_string: str) -> None:
        """Test string_validator with unicode strings."""
        assert string_validator(unicode_string) == unicode_string

    @pytest.mark.parametrize(
        ("validator_func", "test_value"),
        [
            (optional_int_validator, 5),
            (optional_int_validator, 5.0),
            (optional_strict_int_validator, 5),
        ],
    )
    def test_optional_validators_type_preservation(
        self,
        validator_func: Callable[[Any], int | None],
        test_value: object,
    ) -> None:
        """Test that optional validators preserve original type information."""
        assert isinstance(validator_func(test_value), int)
