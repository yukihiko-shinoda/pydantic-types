"""Tests for string_with_length_constraint.py."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pydantic.dataclasses import dataclass
from pydantic_core import ValidationError

# Reason: These are used in dataclass field annotations which require runtime availability
from pydantictypes.string_with_length_constraint import ConstrainedOptionalStringWithLength  # noqa: TC001
from pydantictypes.string_with_length_constraint import ConstrainedStringWithLength  # noqa: TC001
from pydantictypes.string_with_length_constraint import constrained_optional_string  # noqa: TC001
from pydantictypes.string_with_length_constraint import constrained_string  # noqa: TC001
from tests.pydantictypes import BaseTestImportFallback
from tests.pydantictypes import create

if TYPE_CHECKING:
    from types import ModuleType


@dataclass
class StubString:
    value: ConstrainedStringWithLength


@dataclass
class StubOptionalString:
    value: ConstrainedOptionalStringWithLength


class TestConstrainedStringWithLength:
    """Tests for ConstrainedStringWithLength."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("hello", "hello"),
            ("", ""),
            ("a", "a"),
            ("test string", "test string"),
            ("1234567890", "1234567890"),
        ],
    )
    def test_valid_strings(self, value: str, expected: str) -> None:
        """String should be accepted."""
        stub = create(StubString, [value])
        assert isinstance(stub.value, str)
        assert stub.value == expected

    @pytest.mark.parametrize(
        "value",
        [
            123,
            None,
            [],
            {},
            12.34,
        ],
    )
    def test_type_error(self, value: str) -> None:
        """Non-string values should raise TypeError."""
        with pytest.raises((ValidationError, TypeError)):
            create(StubString, [value])


class TestConstrainedOptionalStringWithLength:
    """Tests for ConstrainedOptionalStringWithLength."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("hello", "hello"),
            ("", None),
            ("a", "a"),
            ("test string", "test string"),
        ],
    )
    def test_valid_strings(self, value: str, expected: str | None) -> None:
        """String should be accepted or converted to None."""
        stub = create(StubOptionalString, [value])
        assert isinstance(stub.value, type(expected))
        assert stub.value == expected

    @pytest.mark.parametrize(
        "value",
        [
            123,
            [],
            {},
        ],
    )
    def test_type_error(self, value: str) -> None:
        """Non-string values should raise TypeError."""
        with pytest.raises((ValidationError, TypeError)):
            create(StubOptionalString, [value])

    def test_none_value(self) -> None:
        """None should be converted to None."""
        stub = create(StubOptionalString, [None])
        assert stub.value is None


class TestConstrainedStringFunction:
    """Tests for constrained_string function."""

    def test_min_length(self) -> None:
        """Test minimum length constraint."""

        @dataclass
        class Stub:
            value: constrained_string(min_length=3)  # type: ignore[valid-type]

        stub = create(Stub, ["abc"])
        assert stub.value == "abc"

        stub = create(Stub, ["abcd"])
        assert stub.value == "abcd"

        with pytest.raises(ValidationError):
            create(Stub, ["ab"])

    def test_max_length(self) -> None:
        """Test maximum length constraint."""

        @dataclass
        class Stub:
            value: constrained_string(max_length=5)  # type: ignore[valid-type]

        stub = create(Stub, ["abc"])
        assert stub.value == "abc"

        stub = create(Stub, ["abcde"])
        assert stub.value == "abcde"

        with pytest.raises(ValidationError):
            create(Stub, ["abcdef"])

    def test_equal_to(self) -> None:
        """Test exact length constraint."""

        @dataclass
        class Stub:
            value: constrained_string(equal_to=4)  # type: ignore[valid-type]

        stub = create(Stub, ["abcd"])
        assert stub.value == "abcd"

        with pytest.raises(ValidationError):
            create(Stub, ["abc"])

        with pytest.raises(ValidationError):
            create(Stub, ["abcde"])

    def test_min_and_max_length(self) -> None:
        """Test combined min and max length constraints."""

        @dataclass
        class Stub:
            value: constrained_string(min_length=3, max_length=5)  # type: ignore[valid-type]

        stub = create(Stub, ["abc"])
        assert stub.value == "abc"

        stub = create(Stub, ["abcd"])
        assert stub.value == "abcd"

        stub = create(Stub, ["abcde"])
        assert stub.value == "abcde"

        with pytest.raises(ValidationError):
            create(Stub, ["ab"])

        with pytest.raises(ValidationError):
            create(Stub, ["abcdef"])


class TestConstrainedOptionalStringFunction:
    """Tests for constrained_optional_string function."""

    def test_min_length(self) -> None:
        """Test minimum length constraint with optional."""

        @dataclass
        class Stub:
            value: constrained_optional_string(min_length=3)  # type: ignore[valid-type]

        stub = create(Stub, ["abc"])
        assert stub.value == "abc"

        stub = create(Stub, [""])
        assert stub.value is None

        with pytest.raises(ValidationError):
            create(Stub, ["ab"])

    def test_max_length(self) -> None:
        """Test maximum length constraint with optional."""

        @dataclass
        class Stub:
            value: constrained_optional_string(max_length=5)  # type: ignore[valid-type]

        stub = create(Stub, ["abc"])
        assert stub.value == "abc"

        stub = create(Stub, [""])
        assert stub.value is None

        with pytest.raises(ValidationError):
            create(Stub, ["abcdef"])

    def test_equal_to(self) -> None:
        """Test exact length constraint with optional."""

        @dataclass
        class Stub:
            value: constrained_optional_string(equal_to=4)  # type: ignore[valid-type]

        stub = create(Stub, ["abcd"])
        assert stub.value == "abcd"

        stub = create(Stub, [""])
        assert stub.value is None

        with pytest.raises(ValidationError):
            create(Stub, ["abc"])

    def test_min_and_max_length(self) -> None:
        """Test combined min and max length constraints with optional."""

        @dataclass
        class Stub:
            value: constrained_optional_string(min_length=3, max_length=5)  # type: ignore[valid-type]

        stub = create(Stub, ["abc"])
        assert stub.value == "abc"

        stub = create(Stub, [""])
        assert stub.value is None

        with pytest.raises(ValidationError):
            create(Stub, ["ab"])

        with pytest.raises(ValidationError):
            create(Stub, ["abcdef"])


class TestImportFallback(BaseTestImportFallback):
    """Tests for import fallback scenarios."""

    def get_module(self) -> ModuleType:
        """Return the module to test for import fallback."""
        # Reason: For testing import fallback behavior
        from pydantictypes import string_with_length_constraint  # pylint: disable=import-outside-toplevel  # noqa: PLC0415,I001

        return string_with_length_constraint

    def supports_unpack_fallback(self) -> bool:
        """This module does not support Unpack fallback testing."""
        return False
