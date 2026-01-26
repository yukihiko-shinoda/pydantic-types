"""Tests for abstract_string_to_optional_int.py."""
# pylint: disable=duplicate-code

from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import annotated_types
import pytest

from pydantictypes.abstract_string_to_optional_int import OptionalIntegerMustBeFromStr
from pydantictypes.abstract_string_to_optional_int import abstract_constringtooptionalint
from tests.testlibraries.type_validation import OptionalIntConstraintListAsserter
from tests.testlibraries.type_validation import OptionalIntConstraintListParams


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

    def test_validate_with_none_returns_none(self) -> None:
        """Test that validate returns None for None input (optional type)."""
        mock_converter = Mock()
        validator = OptionalIntegerMustBeFromStr(mock_converter)

        result = validator.validate(None)

        assert result is None
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
    """Tests for abstract_constringtooptionalint function.

    Note: The function now returns only constraint metadata (Interval, MultipleOf),
    not validators. Validators are no longer in the list; constraints are validated
    directly in the OptionalIntegerMustBeFromStr class.
    """

    def test_default_parameters_returns_expected_structure(self) -> None:
        """Test that default parameters return the expected constraint list."""
        result = abstract_constringtooptionalint()

        params = OptionalIntConstraintListParams()
        asserter = OptionalIntConstraintListAsserter(result, params)
        asserter.assert_default_structure(2)

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

        params = OptionalIntConstraintListParams(gt=gt, ge=ge, lt=lt, le=le)
        asserter = OptionalIntConstraintListAsserter(result, params)
        asserter.assert_interval_constraints()

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

        # MultipleOf is now at index 1
        multiple_constraint = result[1]
        if expected_result is None:
            assert multiple_constraint is None
        else:
            assert isinstance(multiple_constraint, annotated_types.MultipleOf)
            assert multiple_constraint.multiple_of == expected_result.multiple_of

    @pytest.mark.parametrize(
        ("gt", "ge", "lt", "le", "multiple_of", "expected_length"),
        [
            (1, 2, 100, 99, 5, 2),
            (0, 1, 50, 49, 10, 2),
        ],
    )
    # Reason: Parametrized argument  # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def test_all_parameters_together(  # noqa: PLR0913
        self,
        gt: int,
        ge: int,
        lt: int,
        le: int,
        multiple_of: int,
        expected_length: int,
    ) -> None:
        """Test function with all parameters set to ensure proper interaction."""
        result = abstract_constringtooptionalint(  # pylint: disable=duplicate-code
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            multiple_of=multiple_of,
        )

        params = OptionalIntConstraintListParams(
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            multiple_of=multiple_of,
        )
        asserter = OptionalIntConstraintListAsserter(result, params)
        asserter.assert_basic_structure(expected_length)
        asserter.assert_interval_constraints()
        asserter.assert_multiple_constraint()

    def test_function_returns_list_type(self) -> None:
        """Test that function returns a list with 2 items."""
        result = abstract_constringtooptionalint()
        assert isinstance(result, list)
        assert len(result) == 2  # noqa: PLR2004

    def test_function_with_keyword_only_parameters(self) -> None:
        """Test that function requires keyword-only parameters."""
        # This should work (keyword arguments)
        result = abstract_constringtooptionalint(strict=True, gt=5)
        # Result[0] is now Interval, not a validator
        assert isinstance(result[0], annotated_types.Interval)
        assert result[0].gt == 5  # noqa: PLR2004

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

        params = OptionalIntConstraintListParams(**kwargs)
        asserter = OptionalIntConstraintListAsserter(result, params)
        if constraint_name == "multiple_of":
            asserter.assert_individual_multiple_constraint(constraint_value)
        else:
            asserter.assert_individual_interval_constraint(constraint_name, constraint_value)


def _simple_converter(value: str) -> int:
    """Simple string-to-int converter for tests."""
    return int(value)


class TestAbstractModuleIntegration:
    """Integration tests for the abstract module components."""

    @pytest.mark.parametrize(
        ("test_input", "expected_result"),
        [
            ("25", 25),
            ("10", 10),
        ],
    )
    def test_validator_converts_valid_input(self, test_input: str, expected_result: int) -> None:
        """Test that validator correctly converts valid string input."""
        validator = OptionalIntegerMustBeFromStr(_simple_converter, gt=0, multiple_of=5)
        result = validator.validate(test_input)
        assert result == expected_result

    def test_validator_returns_none_for_empty_string(self) -> None:
        """Test that validator returns None for empty string input."""
        validator = OptionalIntegerMustBeFromStr(_simple_converter, gt=0, multiple_of=5)
        result = validator.validate("")
        assert result is None

    def test_constraint_function_returns_expected_structure(self) -> None:
        """Test that constraint function returns expected metadata structure."""
        constraints = abstract_constringtooptionalint(gt=0, multiple_of=5)
        # Verify constraint structure - now only 2 items (Interval, MultipleOf)
        assert len(constraints) == 2  # noqa: PLR2004
        assert isinstance(constraints[0], annotated_types.Interval)
        assert isinstance(constraints[1], annotated_types.MultipleOf)

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
