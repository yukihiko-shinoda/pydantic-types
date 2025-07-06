"""Configuration of pytest."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

import pytest

from tests.testlibraries.sys_contest import SysContext

if TYPE_CHECKING:
    from collections.abc import Generator

collect_ignore = ["setup.py"]


@pytest.fixture
def mock_import_failure(module_names: list[str]) -> Generator[None, None, None]:
    """Fixture to mock import failure.

    Args:
        module_names: List of module names that should fail to import.
    """
    with SysContext(module_names):
        yield


@pytest.fixture
def response() -> dict[Any, Any] | None:
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests  # noqa: ERA001
    # return requests.get("https://github.com/audreyr/cookiecutter-pypackage")  # noqa: ERA001
    return None
