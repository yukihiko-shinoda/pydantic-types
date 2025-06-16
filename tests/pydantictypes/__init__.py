"""Test for pydantictypes."""

from __future__ import annotations

from typing import TypeVar

V = TypeVar("V")


def create(target_class: type[V], values: list[str]) -> V:
    return target_class(*values)
