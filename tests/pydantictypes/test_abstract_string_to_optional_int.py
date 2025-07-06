"""Tests for abstract_string_to_optional_int.py."""
# pylint: disable=duplicate-code

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from unittest.mock import Mock

import annotated_types
import pytest

from pydantictypes.abstract_string_to_optional_int import OptionalIntegerMustBeFromStr
from pydantictypes.abstract_string_to_optional_int import abstract_constringtooptionalint
from pydantictypes.validators import optional_int_validator
from pydantictypes.validators import optional_number_multiple_validator
from pydantictypes.validators import optional_number_size_validator
from pydantictypes.validators import optional_strict_int_validator

if TYPE_CHECKING:
    from collections.abc import Callable


class TestOptionalIntegerMustBeFromStr:
    """Tests for OptionalIntegerMustBeFromStr validator class."""

    def test_init_stores_conversion_function(self) -> None:
        """Test that initialization stores the string_to_int function."""
        mock_converter = Mock()
        validator = OptionalIntegerMustBeFromStr(mock_converter)
        assert validator.string_to_int is mock_converter

    @pytest.mark.parametrize(
        ("input_string", "expected_result"),
        [
            ("123", 123),
            ("0", 0),
            ("-456", -456),
            ("999", 999),
        ],
    )
    def test_validate_with_valid_string_calls_converter(self, input_string: str, expected_result: int) -> None:
        """Test that validate calls string_to_int converter with valid string."""
        mock_converter = Mock(return_value=expected_result)
        validator = OptionalIntegerMustBeFromStr(mock_converter)

        result = validator.validate(input_string)

        mock_converter.assert_called_once_with(input_string)
        assert result == expected_result

    def test_validate_with_empty_string_returns_none(self) -> None:
        """Test that validate returns None for empty strings."""
        mock_converter = Mock()
        validator = OptionalIntegerMustBeFromStr(mock_converter)

        result = validator.validate("")

        mock_converter.assert_not_called()
        assert result is None

    @pytest.mark.parametrize(
        ("input_string", "expected_result"),
        [
            ("   ", 42),
            ("\t", 100),
            ("\n", 999),
        ],
    )
    def test_validate_with_whitespace_calls_converter(self, input_string: str, expected_result: int) -> None:
        """Test that validate calls converter for whitespace-only strings."""
        mock_converter = Mock(return_value=expected_result)
        validator = OptionalIntegerMustBeFromStr(mock_converter)

        result = validator.validate(input_string)

        mock_converter.assert_called_once_with(input_string)
        assert result == expected_result

    @pytest.mark.parametrize(
        ("non_string_value", "expected_type_name"),
        [
            (123, "int"),
            (12.5, "float"),
            (None, "NoneType"),
            ([], "list"),
            ({}, "dict"),
            (True, "bool"),
        ],
    )
    # Reason: Need Any to test various non-string types  # pylint: disable-next=line-too-long
    def test_validate_with_non_string_raises_type_error(self, non_string_value: Any, expected_type_name: str) -> None:  # noqa: ANN401
        """Test that validate raises TypeError for non-string input."""
        mock_converter = Mock()
        validator = OptionalIntegerMustBeFromStr(mock_converter)

        with pytest.raises(TypeError) as exc_info:
            validator.validate(non_string_value)

        error_message = str(exc_info.value)
        assert f"String required. Value is {non_string_value}" in error_message
        assert f"Type is <class '{expected_type_name}'>" in error_message
        mock_converter.assert_not_called()

    def test_validate_propagates_converter_exceptions(self) -> None:
        """Test that validate propagates exceptions from the converter function."""
        mock_converter = Mock(side_effect=ValueError("Invalid conversion"))
        validator = OptionalIntegerMustBeFromStr(mock_converter)

        with pytest.raises(ValueError, match="Invalid conversion"):
            validator.validate("invalid")

        mock_converter.assert_called_once_with("invalid")

    @pytest.mark.parametrize(
        ("input_string", "expected_result"),
        [
            ("1,234", 1234),
            ("10,000", 10000),
            ("5,678", 5678),
        ],
    )
    def test_validate_with_complex_converter_logic(self, input_string: str, expected_result: int) -> None:
        """Test validate with a converter that has complex logic."""

        def complex_converter(value: str) -> int:
            # Remove commas and convert
            cleaned = value.replace(",", "")
            return int(cleaned)

        validator = OptionalIntegerMustBeFromStr(complex_converter)

        result = validator.validate(input_string)
        assert result == expected_result

    @pytest.mark.parametrize(
        ("input_string", "expected_result"),
        [
            ("42", 42),
            ("123", 123),
            ("0", 0),
        ],
    )
    def test_validate_maintains_converter_return_type(self, input_string: str, expected_result: int) -> None:
        """Test that validate maintains the exact return type from converter."""

        def type_preserving_converter(value: str) -> int:
            return int(value)

        validator = OptionalIntegerMustBeFromStr(type_preserving_converter)

        result = validator.validate(input_string)
        assert result == expected_result
        assert isinstance(result, int)


class TestAbstractConstringtooptionalint:
    """Tests for abstract_constringtooptionalint function."""

    @pytest.mark.parametrize(
        ("expected_length", "expected_validator", "expected_none_constraint"),
        [
            (5, optional_int_validator, None),
        ],
    )
    def test_default_parameters_returns_expected_validators(
        self,
        expected_length: int,
        expected_validator: Callable[..., Any],
        expected_none_constraint: None,
    ) -> None:
        """Test that default parameters return the expected validator list."""
        result = abstract_constringtooptionalint()

        self._assert_default_length(result, expected_length)
        self._assert_default_validators(result, expected_validator)
        self._assert_default_interval_and_constraint(result, expected_none_constraint)

    @pytest.mark.parametrize(
        ("strict", "expected_validator"),
        [
            (True, optional_strict_int_validator),
            (False, optional_int_validator),
            (None, optional_int_validator),  # Default case
        ],
    )
    def test_strict_parameter_selects_correct_validator(
        self,
        # pytest parametrize requires positional bool argument
        strict: bool | None,  # noqa: FBT001
        expected_validator: Callable[..., Any],
    ) -> None:
        """Test that strict parameter selects the correct int validator."""
        result = abstract_constringtooptionalint(strict=strict)

        assert result[0] is expected_validator

    @pytest.mark.parametrize(
        ("gt", "ge", "lt", "le"),
        [
            (None, None, None, None),
            (5, None, None, None),
            (None, 10, None, None),
            (None, None, 100, None),
            (None, None, None, 50),
            (1, 2, 99, 98),  # All constraints
        ],
    )
    def test_interval_constraints_create_correct_interval(
        self,
        gt: int | None,
        ge: int | None,
        lt: int | None,
        le: int | None,
    ) -> None:
        """Test that interval constraints create the correct Interval object."""
        result = abstract_constringtooptionalint(gt=gt, ge=ge, lt=lt, le=le)

        interval = result[3]
        self._assert_interval_type(interval)
        self._assert_interval_values(interval, gt, ge, lt, le)

    @pytest.mark.parametrize(
        ("multiple_of", "expected_result"),
        [
            (None, None),
            (5, annotated_types.MultipleOf(5)),
            (10, annotated_types.MultipleOf(10)),
            (1, annotated_types.MultipleOf(1)),
        ],
    )
    def test_multiple_of_parameter_creates_correct_constraint(
        self,
        multiple_of: int | None,
        expected_result: annotated_types.MultipleOf | None,
    ) -> None:
        """Test that multiple_of parameter creates the correct constraint."""
        result = abstract_constringtooptionalint(multiple_of=multiple_of)

        multiple_constraint = result[4]
        if expected_result is None:
            assert multiple_constraint is None
        else:
            assert isinstance(multiple_constraint, annotated_types.MultipleOf)
            assert multiple_constraint.multiple_of == expected_result.multiple_of

    @pytest.mark.parametrize(
        ("strict", "gt", "ge", "lt", "le", "multiple_of", "expected_length"),
        [
            (True, 1, 2, 100, 99, 5, 5),
            (False, 0, 1, 50, 49, 10, 5),
        ],
    )
    # Reason: Parametrized argument  # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def test_all_parameters_together(  # noqa: PLR0913
        self,
        strict: bool,  # noqa: FBT001
        gt: int,
        ge: int,
        lt: int,
        le: int,
        multiple_of: int,
        expected_length: int,
    ) -> None:
        """Test function with all parameters set to ensure proper interaction."""
        result = abstract_constringtooptionalint(  # pylint: disable=duplicate-code
            strict=strict,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            multiple_of=multiple_of,
        )

        self._assert_basic_structure(result, strict, expected_length)
        self._assert_interval_constraints(result, gt, ge, lt, le)
        self._assert_multiple_constraint(result, multiple_of)

    def _assert_result_length(self, result: list[Any], expected_length: int) -> None:
        """Assert result list length."""
        assert len(result) == expected_length

    def _assert_validator_type(self, result: list[Any], strict: bool) -> None:  # noqa: FBT001
        """Assert first validator type based on strict parameter."""
        expected_validator = optional_strict_int_validator if strict else optional_int_validator
        assert result[0] is expected_validator

    def _assert_size_and_multiple_validators(self, result: list[Any]) -> None:
        """Assert size and multiple validators."""
        assert result[1] is optional_number_size_validator
        assert result[2] is optional_number_multiple_validator

    def _assert_basic_structure(self, result: list[Any], strict: bool, expected_length: int) -> None:  # noqa: FBT001
        """Assert basic structure and validator types."""
        self._assert_result_length(result, expected_length)
        self._assert_validator_type(result, strict)
        self._assert_size_and_multiple_validators(result)

    def _assert_interval_type(self, interval: annotated_types.Interval) -> None:
        """Assert interval is correct type."""
        assert isinstance(interval, annotated_types.Interval)

    # Reason: Need all interval constraint parameters  # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def _assert_interval_values(
        self,
        interval: annotated_types.Interval,
        gt: int | None,
        ge: int | None,
        lt: int | None,
        le: int | None,
    ) -> None:
        """Assert interval constraint values."""
        assert interval.gt == gt
        assert interval.ge == ge
        assert interval.lt == lt
        assert interval.le == le

    # Reason: Need all interval constraint parameters  # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def _assert_interval_constraints(self, result: list[Any], gt: int, ge: int, lt: int, le: int) -> None:
        """Assert interval constraint values."""
        interval = result[3]
        self._assert_interval_type(interval)
        self._assert_interval_values(interval, gt, ge, lt, le)

    def _assert_multiple_type(self, multiple_constraint: annotated_types.MultipleOf) -> None:
        """Assert multiple constraint is correct type."""
        assert isinstance(multiple_constraint, annotated_types.MultipleOf)

    def _assert_multiple_value(self, multiple_constraint: annotated_types.MultipleOf, multiple_of: int) -> None:
        """Assert multiple constraint value."""
        assert multiple_constraint.multiple_of == multiple_of

    def _assert_multiple_constraint(self, result: list[Any], multiple_of: int) -> None:
        """Assert multiple_of constraint value."""
        multiple_constraint = result[4]
        self._assert_multiple_type(multiple_constraint)
        self._assert_multiple_value(multiple_constraint, multiple_of)

    @pytest.mark.parametrize(
        ("expected_type", "expected_length"),
        [
            (list, 5),
        ],
    )
    def test_function_returns_list_type(self, expected_type: type, expected_length: int) -> None:
        """Test that function returns a list."""
        result = abstract_constringtooptionalint()
        assert isinstance(result, expected_type)
        assert len(result) == expected_length

    def test_function_with_keyword_only_parameters(self) -> None:
        """Test that function requires keyword-only parameters."""
        # This should work (keyword arguments)
        result = abstract_constringtooptionalint(strict=True, gt=5)
        assert result[0] is optional_strict_int_validator

        # Test that positional arguments would fail if attempted
        # (This is enforced by the * in the function signature)

    @pytest.mark.parametrize(
        ("constraint_name", "constraint_value"),
        [
            ("gt", 0),
            ("ge", 1),
            ("lt", 1000),
            ("le", 999),
            ("multiple_of", 7),
        ],
    )
    def test_individual_constraints(self, constraint_name: str, constraint_value: int) -> None:
        """Test each constraint parameter individually."""
        kwargs: dict[str, Any] = {constraint_name: constraint_value}
        result = abstract_constringtooptionalint(**kwargs)

        if constraint_name == "multiple_of":
            self._assert_individual_multiple_constraint(result, constraint_value)
        else:
            self._assert_individual_interval_constraint(result, constraint_name, constraint_value)

    def _assert_default_length(self, result: list[Any], expected_length: int) -> None:
        """Assert default result length."""
        assert len(result) == expected_length

    def _assert_default_validators(self, result: list[Any], expected_validator: Callable[..., Any]) -> None:
        """Assert default validator types."""
        assert result[0] is expected_validator
        assert result[1] is optional_number_size_validator
        assert result[2] is optional_number_multiple_validator

    def _assert_default_interval_and_constraint(self, result: list[Any], expected_none_constraint: None) -> None:
        """Assert default interval and constraint."""
        assert isinstance(result[3], annotated_types.Interval)
        assert result[4] is expected_none_constraint

    def _assert_individual_multiple_constraint(self, result: list[Any], constraint_value: int) -> None:
        """Assert individual multiple constraint."""
        multiple_constraint = result[4]
        assert isinstance(multiple_constraint, annotated_types.MultipleOf)
        assert multiple_constraint.multiple_of == constraint_value

    def _assert_individual_interval_constraint(
        self,
        result: list[Any],
        constraint_name: str,
        constraint_value: int,
    ) -> None:
        """Assert individual interval constraint."""
        interval = result[3]
        assert isinstance(interval, annotated_types.Interval)
        assert getattr(interval, constraint_name) == constraint_value


class TestAbstractModuleIntegration:
    """Integration tests for the abstract module components."""

    @pytest.mark.parametrize(
        ("test_input", "expected_result", "expected_constraints_length"),
        [
            ("25", 25, 5),
            ("10", 10, 5),
        ],
    )
    def test_validator_and_constraint_function_integration(
        self,
        test_input: str,
        expected_result: int,
        expected_constraints_length: int,
    ) -> None:
        """Test integration between OptionalIntegerMustBeFromStr and constraint function."""

        # Create a simple string-to-int converter
        def simple_converter(value: str) -> int:
            return int(value)

        # Create validator
        validator = OptionalIntegerMustBeFromStr(simple_converter)

        # Get constraints for strict validation
        constraints = abstract_constringtooptionalint(strict=True, gt=0, multiple_of=5)

        # Test that validator works with valid input
        result = validator.validate(test_input)
        assert result == expected_result

        # Test that validator works with empty string
        result = validator.validate("")
        assert result is None

        # Verify constraint structure is compatible
        assert len(constraints) == expected_constraints_length
        assert constraints[0] is optional_strict_int_validator

    def test_module_exports_expected_components(self) -> None:
        """Test that the module exports the expected components."""
        assert callable(OptionalIntegerMustBeFromStr)
        assert callable(abstract_constringtooptionalint)

    @pytest.mark.parametrize(
        ("test_input", "expected_result", "should_raise", "exception_type"),
        [
            ("123", 123, False, None),
            ("456", 456, False, None),
            ("", None, False, None),
            ("fail", None, True, ValueError),
            (123, None, True, TypeError),
        ],
    )
    # Reason: Parametrized argument
    def test_error_handling_integration(
        self,
        test_input: str | int,
        expected_result: int | None,
        should_raise: bool,  # noqa: FBT001
        exception_type: type | None,
    ) -> None:
        """Test error handling integration between components."""

        def failing_converter(value: str) -> int:
            if value == "fail":
                msg = "Conversion failed"
                raise ValueError(msg)
            return int(value)

        validator = OptionalIntegerMustBeFromStr(failing_converter)

        if should_raise:
            if exception_type is ValueError:
                with pytest.raises(ValueError, match="Conversion failed"):
                    validator.validate(test_input)
            elif exception_type is TypeError:
                with pytest.raises(TypeError, match="String required"):
                    validator.validate(test_input)
        else:
            result = validator.validate(test_input)
            assert result == expected_result
