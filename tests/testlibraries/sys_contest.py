"""The sys context to mock import failure in tests."""

from __future__ import annotations

import sys
from importlib.abc import MetaPathFinder
from types import ModuleType
from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from types import TracebackType


class MockTypingModule(ModuleType):
    """Mock typing module that raises ImportError for specific attributes."""

    # Reason: Need Any to accept any module type for mocking
    def __init__(self, original_typing: Any, blocked_attrs: list[str]) -> None:  # noqa: ANN401
        self._original_typing = original_typing
        self._blocked_attrs = blocked_attrs

    # Reason: Need Any to return any attribute type from the original module
    def __getattr__(self, name: str) -> Any:  # noqa: ANN401
        if name in self._blocked_attrs:
            msg = f"cannot import name '{name}' from 'typing'"
            raise ImportError(msg)
        return getattr(self._original_typing, name)


class ImportFailLoader(MetaPathFinder):
    """Custom meta path finder that fails to import specific modules or attributes."""

    def __init__(self, module_attrs: list[str]) -> None:
        self.module_attrs = module_attrs

    # Reason: The specification of `find_spec` is defined in PEP 451:
    # - PEP 451 - A ModuleSpec Type for the Import System | peps.python.org
    #   https://peps.python.org/pep-0451/#finders-and-loaders
    # pylint: disable-next=unused-argument
    def find_spec(self, fullname: str, path: Any = None, target: Any = None) -> None:  # noqa: ANN401,ARG002
        # Handle full module imports
        if fullname in self.module_attrs:
            msg = f"Module {fullname} is not available for testing."
            raise ImportError(msg)


class SysContext:
    """Context manager to temporarily modify sys.modules and mock attribute access."""

    def __init__(self, module_attrs: list[str]) -> None:
        self.module_attrs = module_attrs
        self.original_meta_path = sys.meta_path[:]
        self.original_modules = sys.modules.copy()
        self.mock_modules: dict[str, Any] = {}

    def __enter__(self) -> None:
        import_fail_loader = ImportFailLoader(self.module_attrs)
        sys.meta_path.insert(0, import_fail_loader)

        # Handle attribute-level blocking (e.g., "typing.Annotated")
        for module_attr in self.module_attrs:
            if "." in module_attr:
                module_name, attr_name = module_attr.split(".", 1)
                if module_name in sys.modules:
                    original_typing = sys.modules[module_name]
                    mock_typing = MockTypingModule(original_typing, [attr_name])
                    sys.modules[module_name] = mock_typing
                    self.mock_modules[module_name] = mock_typing
            # Handle full module blocking
            elif module_attr in sys.modules:
                del sys.modules[module_attr]

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        sys.meta_path[:] = self.original_meta_path
        sys.modules.clear()
        sys.modules.update(self.original_modules)
