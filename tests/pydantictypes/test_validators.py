"""Tests for validators.py."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from typing import Any
from unittest.mock import Mock

import pytest
from pydantic.v1.errors import IntegerError
from pydantic.v1.errors import NumberNotGtError
from pydantic.v1.errors import NumberNotMultipleError
from pydantic.v1.fields import ModelField

from pydantictypes.validators import Number
from pydantictypes.validators import optional_int_validator
from pydantictypes.validators import optional_number_multiple_validator
from pydantictypes.validators import optional_number_size_validator
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
        """Test that string integer input raises IntegerError."""
        with pytest.raises(IntegerError):
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
        """Test that float input raises IntegerError."""
        with pytest.raises(IntegerError):
            optional_strict_int_validator(value)

    @pytest.mark.parametrize(
        ("value", "expected_error"),
        [
            (True, IntegerError),
            (False, IntegerError),
        ],
    )
    # Reason: Parametrized argument
    def test_with_bool_raises_error(self, value: bool, expected_error: type[Exception]) -> None:  # noqa: FBT001
        """Test that boolean input raises IntegerError in strict mode."""
        with pytest.raises(expected_error):
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
        """Test that invalid string input raises IntegerError."""
        with pytest.raises(IntegerError):
            optional_int_validator(value)


class TestOptionalNumberSizeValidator:
    """Tests for optional_number_size_validator."""

    def test_with_none_returns_none(self) -> None:
        """Test that None input returns None."""
        mock_field = Mock(spec=ModelField)
        assert optional_number_size_validator(None, mock_field) is None

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (5, 5),
            (5.5, 5.5),
            (Decimal("5.5"), Decimal("5.5")),
            (0, 0),
            (-10, -10),
        ],
    )
    def test_with_valid_number_calls_underlying_validator(self, value: Number, expected: Number) -> None:
        """Test that valid number input calls the underlying validator."""
        # Create a mock field with a mock type that has no constraints
        mock_field = Mock(spec=ModelField)
        mock_type = Mock()
        mock_type.gt = None
        mock_type.ge = None
        mock_type.lt = None
        mock_type.le = None
        mock_field.type_ = mock_type

        result = optional_number_size_validator(value, mock_field)
        assert result == expected

    @pytest.mark.parametrize(
        ("constraint_value", "test_value"),
        [
            (10, 5),
            (0, -1),
            (100, 50),
        ],
    )
    def test_with_constraint_violation_raises_error(self, constraint_value: int, test_value: int) -> None:
        """Test that constraint violation raises NumberNotGtError."""
        mock_field = Mock(spec=ModelField)
        mock_type = Mock()
        mock_type.gt = constraint_value
        mock_type.ge = None
        mock_type.lt = None
        mock_type.le = None
        mock_field.type_ = mock_type

        with pytest.raises(NumberNotGtError):
            optional_number_size_validator(test_value, mock_field)


class TestOptionalNumberMultipleValidator:
    """Tests for optional_number_multiple_validator."""

    def test_with_none_returns_none(self) -> None:
        """Test that None input returns None."""
        mock_field = Mock(spec=ModelField)
        assert optional_number_multiple_validator(None, mock_field) is None

    @pytest.mark.parametrize(
        ("multiple_of", "value", "expected"),
        [
            (5, 10, 10),
            (5, 15.0, 15.0),
            (3, 9, 9),
            (2, 4.0, 4.0),
        ],
    )
    def test_with_valid_multiple_calls_underlying_validator(
        self,
        multiple_of: int,
        value: Number,
        expected: Number,
    ) -> None:
        """Test that valid multiple input calls the underlying validator."""
        mock_field = Mock(spec=ModelField)
        mock_type = Mock()
        mock_type.multiple_of = multiple_of
        mock_field.type_ = mock_type

        result = optional_number_multiple_validator(value, mock_field)
        assert result == expected

    @pytest.mark.parametrize(
        ("multiple_of", "test_value"),
        [
            (5, 7),
            (3, 8),
            (2, 5),
        ],
    )
    def test_with_multiple_violation_raises_error(self, multiple_of: int, test_value: int) -> None:
        """Test that multiple violation raises NumberNotMultipleError."""
        mock_field = Mock(spec=ModelField)
        mock_type = Mock()
        mock_type.multiple_of = multiple_of
        mock_field.type_ = mock_type

        with pytest.raises(NumberNotMultipleError):
            optional_number_multiple_validator(test_value, mock_field)


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


class TestNumberType:
    """Tests for the Number type alias."""

    @pytest.mark.parametrize(
        ("value", "expected_type"),
        [
            (5, int),
            (5.5, float),
            (Decimal("5.5"), Decimal),
        ],
    )
    def test_number_type_includes_types(self, value: Number, expected_type: type) -> None:
        """Test that Number type includes int, float, and Decimal."""
        assert isinstance(value, expected_type)


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
