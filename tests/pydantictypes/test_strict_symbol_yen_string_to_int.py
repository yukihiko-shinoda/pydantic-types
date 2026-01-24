"""Tests for StrictSymbolYenStringToInt."""

import datetime
from typing import Any

import pytest
from pydantic.dataclasses import dataclass
from pydantic_core import ValidationError

from pydantictypes.symbol_yen_string_to_int import StrictSymbolYenStringToInt
from tests.pydantictypes import create


@dataclass
class Stub:
    int_: StrictSymbolYenStringToInt


class TestStrictSymbolYenStringToInt:
    """Tests for StrictSymbolYenStringToInt."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (r"\1", 1),
            (r"\1,000", 1000),
            (r"\1,000,000", 1000000),
            (r"\123", 123),
            (r"\999,999", 999999),
        ],
    )
    def test_valid_conversion(self, value: str, expected: int) -> None:
        """Property should be converted to int from valid yen string."""
        stub = create(Stub, [value])
        assert stub.int_ == expected
        assert isinstance(stub.int_, int)

    @pytest.mark.parametrize(
        "value",
        [
            # Decimal values (unsupported)
            r"\1.0",
            r"\1,000.0",
            r"\1,000,000.0",
            r"\123.45",
            # Wrong currency symbols
            r"¥1",
            r"¥ 1",
            r"$1",
            r"$ 1",
            # Missing backslash
            r"1",
            r"1,000",
            r"1,000,000",
            # Empty or None
            "",
            None,
            # Wrong types
            datetime.date(2020, 1, 1),
            1,
            1.0,
            [],
            {},
            # Invalid patterns
            r"\ 1",  # Space after backslash
            r"\abc",  # Non-numeric
            r"abc",  # No backslash, no numbers
        ],
    )
    # Reason: Need Any to test various invalid types in parametrized test
    def test_invalid_conversion(self, value: Any) -> None:  # noqa: ANN401
        """Pydantic should raise ValidationError for invalid values."""
        with pytest.raises((ValidationError, TypeError)):
            create(Stub, [value])

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (r"\0", 0),  # Zero
            (r"\999,999,999", 999999999),  # Large number
        ],
    )
    def test_edge_cases(self, value: str, expected: int) -> None:
        """Test edge cases for StrictSymbolYenStringToInt."""
        stub = create(Stub, [value])
        assert stub.int_ == expected
        assert isinstance(stub.int_, int)

    def test_permissive_patterns(self) -> None:
        """Test that the regex is permissive and matches various patterns."""
        # These patterns are actually valid because the regex just looks for \followed by digits
        valid_cases = [
            (r"\1 円", 1),  # Extra text after is ignored
            (r"\1円", 1),
            (r"\1 ドル", 1),
            (r"\1ドル", 1),
            (r"\\1", 1),  # Double backslash still works
            (r" \1", 1),  # Leading space is ignored
            (r"\1,000,000 \1,000,000", 1000000),  # Takes first match
        ]

        for value, expected in valid_cases:
            stub = create(Stub, [value])
            assert stub.int_ == expected

    def test_comma_variations(self) -> None:
        """Test different comma patterns."""
        # Valid comma patterns
        valid_cases = [
            (r"\1,000", 1000),
            (r"\12,345", 12345),
            (r"\123,456", 123456),
            (r"\1,234,567", 1234567),
        ]

        for value, expected in valid_cases:
            stub = create(Stub, [value])
            assert stub.int_ == expected

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (r"\1,23", 123),  # Unusual comma placement
        ],
    )
    def test_unusual_comma_patterns(self, value: str, expected: int) -> None:
        """Test unusual comma patterns that still work."""
        # Invalid comma patterns should still work if they match the regex
        # The regex pattern r"\\([\d,]+)" will match, but int conversion handles comma removal
        stub = create(Stub, [value])
        assert stub.int_ == expected
