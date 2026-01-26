"""Tests for string_to_optional_int.py ."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Optional

import pytest
from pydantic.dataclasses import dataclass
from pydantic_core import ValidationError

from pydantictypes.string_to_optional_int import ConstrainedStringToOptionalInt
from pydantictypes.string_to_optional_int import constringtooptionalint
from tests.pydantictypes import BaseTestConstraintFunction
from tests.pydantictypes import BaseTestImportFallback
from tests.pydantictypes import BaseTestOptionalType
from tests.pydantictypes import create

if TYPE_CHECKING:
    from types import ModuleType


@dataclass
class Stub:
    int_: ConstrainedStringToOptionalInt


class Test(BaseTestOptionalType):
    """Tests for ConstrainedStringToOptionalInt."""

    Stub = Stub

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
            datetime.date(2020, 1, 1),
            1,
        ],
    )
    # Reason: Need Any to test various invalid types in parametrized test
    def test_error(self, value: Any) -> None:  # noqa: ANN401
        """Property should be converted to int."""
        self._assert_error_raised(value)


class TestConstraintFunction(BaseTestConstraintFunction):
    """Tests for constringtooptionalint function."""

    def get_constraint_function(self) -> Callable[..., Any]:
        """Return the constraint function for this module."""
        return constringtooptionalint

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
        # Reason: For testing import fallback behavior
        from pydantictypes import string_to_optional_int  # pylint: disable=import-outside-toplevel  # noqa: PLC0415

        return string_to_optional_int

    def supports_unpack_fallback(self) -> bool:
        """This module no longer uses Unpack (removed for Python 3.10 compatibility)."""
        return False


class TestNumericConstraintsEnforced:
    """Tests that numeric constraints (ge, le, gt, lt, multiple_of) are enforced.

    These tests verify the fix for the critical bug where constraints were silently ignored. Uses TypeAdapter for
    direct validation to avoid dataclass forward reference issues.
    """

    def test_le_constraint_is_enforced(self) -> None:
        """Test that le (less than or equal) constraint is enforced."""
        # Reason: Import inside function to avoid dataclass forward reference issues
        from pydantic import TypeAdapter  # noqa: PLC0415  # pylint: disable=import-outside-toplevel

        optional_10_digits = constringtooptionalint(ge=0, le=9999999999)
        adapter = TypeAdapter(optional_10_digits)

        # Valid value should pass
        result = adapter.validate_python("9999999999")
        assert result == 9999999999  # noqa: PLR2004

        # Value exceeding le constraint should FAIL
        with pytest.raises(ValidationError):
            adapter.validate_python("10000000000")  # This is > 9999999999

    def test_ge_constraint_is_enforced(self) -> None:
        """Test that ge (greater than or equal) constraint is enforced."""
        # Reason: Import inside function to avoid dataclass forward reference issues
        from pydantic import TypeAdapter  # noqa: PLC0415  # pylint: disable=import-outside-toplevel

        positive_int = constringtooptionalint(ge=0, le=100)
        adapter = TypeAdapter(positive_int)

        # Valid value should pass
        result = adapter.validate_python("50")
        assert result == 50  # noqa: PLR2004

        # Negative value should FAIL
        with pytest.raises(ValidationError):
            adapter.validate_python("-1")  # This is < 0

    def test_gt_constraint_is_enforced(self) -> None:
        """Test that gt (greater than) constraint is enforced."""
        # Reason: Import inside function to avoid dataclass forward reference issues
        from pydantic import TypeAdapter  # noqa: PLC0415  # pylint: disable=import-outside-toplevel

        greater_than_zero = constringtooptionalint(gt=0)
        adapter = TypeAdapter(greater_than_zero)

        # Value greater than 0 should pass
        result = adapter.validate_python("1")
        assert result == 1

        # Value equal to 0 should FAIL (gt means strictly greater)
        with pytest.raises(ValidationError):
            adapter.validate_python("0")

    def test_lt_constraint_is_enforced(self) -> None:
        """Test that lt (less than) constraint is enforced."""
        # Reason: Import inside function to avoid dataclass forward reference issues
        from pydantic import TypeAdapter  # noqa: PLC0415  # pylint: disable=import-outside-toplevel

        less_than_100 = constringtooptionalint(lt=100)
        adapter = TypeAdapter(less_than_100)

        # Value less than 100 should pass
        result = adapter.validate_python("99")
        assert result == 99  # noqa: PLR2004

        # Value equal to 100 should FAIL (lt means strictly less)
        with pytest.raises(ValidationError):
            adapter.validate_python("100")

    def test_multiple_of_constraint_is_enforced(self) -> None:
        """Test that multiple_of constraint is enforced."""
        # Reason: Import inside function to avoid dataclass forward reference issues
        from pydantic import TypeAdapter  # noqa: PLC0415  # pylint: disable=import-outside-toplevel

        multiple_of_5 = constringtooptionalint(multiple_of=5)
        adapter = TypeAdapter(multiple_of_5)

        # Value that is multiple of 5 should pass
        result = adapter.validate_python("15")
        assert result == 15  # noqa: PLR2004

        # Value that is not multiple of 5 should FAIL
        with pytest.raises(ValidationError):
            adapter.validate_python("13")

    def test_combined_constraints_are_enforced(self) -> None:
        """Test that multiple constraints work together."""
        # Reason: Import inside function to avoid dataclass forward reference issues
        from pydantic import TypeAdapter  # noqa: PLC0415  # pylint: disable=import-outside-toplevel

        bounded_multiple = constringtooptionalint(ge=10, le=100, multiple_of=10)
        adapter = TypeAdapter(bounded_multiple)

        # Valid values
        assert adapter.validate_python("10") == 10  # noqa: PLR2004
        assert adapter.validate_python("50") == 50  # noqa: PLR2004
        assert adapter.validate_python("100") == 100  # noqa: PLR2004

        # Fails ge constraint
        with pytest.raises(ValidationError):
            adapter.validate_python("5")

        # Fails le constraint
        with pytest.raises(ValidationError):
            adapter.validate_python("110")

        # Fails multiple_of constraint
        with pytest.raises(ValidationError):
            adapter.validate_python("15")

    def test_empty_string_returns_none_with_constraints(self) -> None:
        """Test that empty string returns None even with constraints."""
        # Reason: Import inside function to avoid dataclass forward reference issues
        from pydantic import TypeAdapter  # noqa: PLC0415  # pylint: disable=import-outside-toplevel

        constrained_int = constringtooptionalint(ge=0, le=100)
        adapter = TypeAdapter(constrained_int)

        # Empty string should return None (not raise error)
        result = adapter.validate_python("")
        assert result is None


class TestNoneValueHandling:
    """Tests that None values are handled correctly.

    These tests verify the fix for the bug where TypeError was raised instead of ValidationError.
    """

    def test_none_value_returns_none_for_optional_type(self) -> None:
        """Test that None value is accepted for optional types and returns None."""
        # Reason: Import inside function to avoid dataclass forward reference issues
        from pydantic import TypeAdapter  # noqa: PLC0415  # pylint: disable=import-outside-toplevel

        optional_10_digits = constringtooptionalint(ge=0, le=9999999999)
        adapter = TypeAdapter(optional_10_digits)

        # None should be accepted for optional type and return None
        result = adapter.validate_python(None)
        assert result is None
