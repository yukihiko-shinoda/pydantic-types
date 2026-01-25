"""Tests for empty_string_to_none.py."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING
from typing import Any

import pytest
from pydantic.dataclasses import dataclass
from pydantic_core import ValidationError

from pydantictypes.empty_string_to_none import EmptyStringToNone  # noqa: TC001
from tests.pydantictypes import BaseTestImportFallback
from tests.pydantictypes import create

if TYPE_CHECKING:
    from types import ModuleType


@dataclass
class Stub:
    value: EmptyStringToNone


class Test:
    """Tests for EmptyStringToNone."""

    def test_empty_string_converts_to_none(self) -> None:
        """Empty string should be converted to None."""
        stub = create(Stub, [""])
        assert stub.value is None

    @pytest.mark.parametrize(
        "value",
        [
            "1",
            "non-empty",
            " ",
            "0",
            None,
            datetime.date(2020, 1, 1),
            1,
            0,
        ],
    )
    # Reason: Need Any to test various invalid types in parametrized test
    def test_error(self, value: Any) -> None:  # noqa: ANN401
        """Only empty string should be accepted."""
        with pytest.raises((ValidationError, TypeError, ValueError)):
            create(Stub, [value])


class TestImportFallback(BaseTestImportFallback):
    """Tests for import fallback scenarios."""

    def get_module(self) -> ModuleType:
        """Return the module to test for import fallback."""
        # Reason: For testing import fallback behavior
        from pydantictypes import empty_string_to_none  # pylint: disable=import-outside-toplevel  # noqa: PLC0415

        return empty_string_to_none

    def supports_unpack_fallback(self) -> bool:
        """This module does not support Unpack fallback testing."""
        return False
