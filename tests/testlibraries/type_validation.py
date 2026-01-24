"""Helper classes for type validation assertions in tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

import annotated_types

from pydantictypes.validators import optional_int_validator
from pydantictypes.validators import optional_number_multiple_validator
from pydantictypes.validators import optional_number_size_validator
from pydantictypes.validators import optional_strict_int_validator

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass
class ConstraintIntParams:
    """Data class holding constraint parameter values."""

    strict: bool
    gt: int | None = None
    ge: int | None = None
    lt: int | None = None
    le: int | None = None
    multiple_of: int | None = None


class ConstrainedIntAsserter:
    """Helper class to assert ConstrainedInt class attributes."""

    def __init__(self, cls: Any) -> None:  # noqa: ANN401
        """Initialize with the class to assert.

        Args:
            cls: The ConstrainedInt class or subclass to assert.
        """
        self.cls = cls

    def assert_strict_is_false(self) -> None:
        """Assert class strict attribute is False."""
        assert self.cls.strict is False

    def assert_constraint_attributes_are_none(self) -> None:
        """Assert class constraint attributes are None."""
        self.assert_size_constraints_are_none()
        self.assert_multiple_constraint_is_none()

    def assert_size_constraints_are_none(self) -> None:
        """Assert class size constraint attributes are None."""
        assert self.cls.gt is None
        assert self.cls.ge is None
        assert self.cls.lt is None
        assert self.cls.le is None

    def assert_multiple_constraint_is_none(self) -> None:
        """Assert class multiple_of constraint attribute is None."""
        assert self.cls.multiple_of is None


class ConstraintValueAsserter:
    """Helper class to assert constraint values on a type."""

    # Reason: The argument of pydantic type
    def __init__(self, result_type: Any, params: ConstraintIntParams) -> None:  # noqa: ANN401
        """Initialize with type and expected constraint values.

        Args:
            result_type: The type to assert.
            params: Constraint parameter values.
        """
        self.result_type = result_type
        self.params = params

    def assert_all(self) -> None:
        """Assert all constraint values."""
        self.assert_strict_attribute_value()
        self.assert_size_constraint_values()
        self.assert_multiple_constraint_value()

    def assert_strict_attribute_value(self) -> None:
        """Assert type strict attribute has expected value."""
        assert self.result_type.strict == self.params.strict

    def assert_size_constraint_values(self) -> None:
        """Assert type size constraint attributes have expected values."""
        assert self.result_type.gt == self.params.gt
        assert self.result_type.ge == self.params.ge
        assert self.result_type.lt == self.params.lt
        assert self.result_type.le == self.params.le

    def assert_multiple_constraint_value(self) -> None:
        """Assert type multiple_of attribute has expected value."""
        assert self.result_type.multiple_of == self.params.multiple_of


@dataclass
class OptionalIntConstraintListParams:
    """Data class holding expected constraint list parameter values."""

    strict: bool | None = None
    gt: int | None = None
    ge: int | None = None
    lt: int | None = None
    le: int | None = None
    multiple_of: int | None = None


class OptionalIntConstraintListAsserter:
    """Helper class to assert constraint list from abstract_constringtooptionalint()."""

    def __init__(self, result: list[Any], params: OptionalIntConstraintListParams) -> None:
        """Initialize with result list and expected constraint values.

        Args:
            result: The constraint list returned by abstract_constringtooptionalint().
            params: Expected constraint parameter values.
        """
        self.result = result
        self.params = params

    def assert_result_length(self, expected_length: int) -> None:
        """Assert result list length."""
        assert len(self.result) == expected_length

    def assert_validator_type(self, strict: bool) -> None:  # noqa: FBT001
        """Assert first validator type based on strict parameter."""
        expected_validator = optional_strict_int_validator if strict else optional_int_validator
        assert self.result[0] is expected_validator

    def assert_size_and_multiple_validators(self) -> None:
        """Assert size and multiple validators."""
        assert self.result[1] is optional_number_size_validator
        assert self.result[2] is optional_number_multiple_validator

    def assert_interval_type(self) -> None:
        """Assert interval is correct type."""
        interval = self.result[3]
        assert isinstance(interval, annotated_types.Interval)

    def assert_interval_values(self) -> None:
        """Assert interval constraint values using stored expected values."""
        interval = self.result[3]
        assert interval.gt == self.params.gt
        assert interval.ge == self.params.ge
        assert interval.lt == self.params.lt
        assert interval.le == self.params.le

    def assert_interval_constraints(self) -> None:
        """Assert interval constraint values."""
        self.assert_interval_type()
        self.assert_interval_values()

    def assert_multiple_type(self) -> None:
        """Assert multiple constraint is correct type."""
        multiple_constraint = self.result[4]
        assert isinstance(multiple_constraint, annotated_types.MultipleOf)

    def assert_multiple_value(self) -> None:
        """Assert multiple constraint value using stored expected value."""
        multiple_constraint = self.result[4]
        assert multiple_constraint.multiple_of == self.params.multiple_of

    def assert_multiple_constraint(self) -> None:
        """Assert multiple_of constraint value."""
        self.assert_multiple_type()
        self.assert_multiple_value()

    def assert_basic_structure(self, expected_length: int) -> None:
        """Assert basic structure and validator types."""
        self.assert_result_length(expected_length)
        if self.params.strict is not None:
            self.assert_validator_type(self.params.strict)
        self.assert_size_and_multiple_validators()

    def assert_default_structure(self, expected_length: int, expected_validator: Callable[..., Any]) -> None:
        """Assert default structure."""
        self.assert_result_length(expected_length)
        self._assert_default_validators(expected_validator)
        self._assert_default_interval_and_constraint()

    def _assert_default_validators(self, expected_validator: Callable[..., Any]) -> None:
        """Assert default validator types."""
        assert self.result[0] is expected_validator
        assert self.result[1] is optional_number_size_validator
        assert self.result[2] is optional_number_multiple_validator

    def _assert_default_interval_and_constraint(self) -> None:
        """Assert default interval and constraint."""
        assert isinstance(self.result[3], annotated_types.Interval)
        assert self.result[4] is None

    def assert_individual_multiple_constraint(self, constraint_value: int) -> None:
        """Assert individual multiple constraint."""
        multiple_constraint = self.result[4]
        assert isinstance(multiple_constraint, annotated_types.MultipleOf)
        assert multiple_constraint.multiple_of == constraint_value

    def assert_individual_interval_constraint(self, constraint_name: str, constraint_value: int) -> None:
        """Assert individual interval constraint."""
        interval = self.result[3]
        assert isinstance(interval, annotated_types.Interval)
        assert getattr(interval, constraint_name) == constraint_value
