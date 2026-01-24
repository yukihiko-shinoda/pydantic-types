"""Test for pydantictypes."""

from __future__ import annotations

import importlib
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import TypeVar

import pytest

if TYPE_CHECKING:
    from types import ModuleType

V = TypeVar("V")


def create(target_class: type[V], values: list[Any]) -> V:
    return target_class(*values)


class BaseTestConstraintFunction(ABC):
    """Base class for testing constraint functions."""

    def test_constringtoint_returns_annotated_type(self) -> None:
        """Test constraint function returns proper Annotated type."""
        result = self.get_constraint_function()()
        assert hasattr(result, "__metadata__")
        assert len(result.__metadata__) == self.get_expected_metadata_count()

    def test_constringtoint_basic(self) -> None:
        """Tests constraint function returns proper type."""
        actual = self.get_constraint_function()()
        expected_origin = self.get_expected_origin()
        if expected_origin is not None:
            assert actual.__origin__ is expected_origin

    def test_constringtoint_with_constraints(self) -> None:
        """Tests constraint function with various constraints."""
        if self.supports_constraints():
            actual = self.get_constraint_function()(gt=0, ge=1, lt=1000, le=999, multiple_of=5)
            expected_origin = self.get_expected_origin()
            if expected_origin is not None:
                assert actual.__origin__ is expected_origin

    @abstractmethod
    def get_constraint_function(self) -> Callable[..., Any]:
        """Return the specific constraint function."""
        raise NotImplementedError

    def get_expected_metadata_count(self) -> int:
        """Return expected metadata count."""
        return 3  # Default: BeforeValidator, Interval, MultipleOf

    # Any is needed here because subclasses return different types:
    # - Regular int types return `int`
    # - Optional int types return `Optional[int]` (which is a special form)
    def get_expected_origin(self) -> Any:  # noqa: ANN401
        """Return expected __origin__ type."""
        return int

    def supports_constraints(self) -> bool:
        """Indicate if the function supports constraints."""
        return True


class BaseTestImportFallback(ABC):
    """Base class for testing import fallback scenarios."""

    @pytest.mark.usefixtures("mock_import_failure")
    @pytest.mark.parametrize("module_names", [["typing.Annotated"]])
    def test_typing_extensions_fallback(self) -> None:
        """Test that typing_extensions is used when typing.Annotated import fails."""
        module = self.get_module()
        importlib.reload(module)

    @pytest.mark.usefixtures("mock_import_failure")
    @pytest.mark.parametrize("module_names", [["typing.Unpack"]])
    def test_typing_extensions_unpack_fallback(self) -> None:
        """Test that typing_extensions is used when typing.Unpack import fails."""
        if self.supports_unpack_fallback():
            module = self.get_module()
            importlib.reload(module)

    @abstractmethod
    def get_module(self) -> ModuleType:
        """Return the specific module to test."""
        raise NotImplementedError

    def supports_unpack_fallback(self) -> bool:
        """Indicate if the module supports Unpack fallback testing."""
        return False
