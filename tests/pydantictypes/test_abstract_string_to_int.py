"""Tests for abstract_string_to_int.py."""
# pylint: disable=duplicate-code

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import cast
from unittest.mock import Mock

import pytest
from pydantic.v1.errors import NumberNotGeError
from pydantic.v1.errors import NumberNotGtError
from pydantic.v1.errors import NumberNotLeError
from pydantic.v1.errors import NumberNotLtError
from pydantic.v1.errors import NumberNotMultipleError

from pydantictypes.abstract_string_to_int import ConstrainedInt
from pydantictypes.abstract_string_to_int import ConstrainedStringToInt
from pydantictypes.abstract_string_to_int import IntegerMustBeFromStr
from pydantictypes.abstract_string_to_int import constringtoint
from tests.testlibraries.type_validation import ConstrainedIntAsserter
from tests.testlibraries.type_validation import ConstraintIntParams
from tests.testlibraries.type_validation import ConstraintValueAsserter

if TYPE_CHECKING:
    from typing import Type


class TestIntegerMustBeFromStr:
    """Tests for IntegerMustBeFromStr validator class."""

    def test_init_stores_conversion_function(self) -> None:
        """Test that initialization stores the string_to_int function."""
        mock_converter = Mock()
        validator = IntegerMustBeFromStr(mock_converter)
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
        validator = IntegerMustBeFromStr(mock_converter)

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
    # Reason: Need Any to test various non-string types pylint: disable-next=line-too-long
    def test_validate_with_non_string_raises_type_error(self, non_string_value: Any, expected_type_name: str) -> None:  # noqa: ANN401
        """Test that validate raises TypeError for non-string input."""
        mock_converter = Mock()
        validator = IntegerMustBeFromStr(mock_converter)

        with pytest.raises(TypeError) as exc_info:
            validator.validate(non_string_value)

        error_message = str(exc_info.value)
        assert f"String required. Value is {non_string_value}" in error_message
        assert f"Type is <class '{expected_type_name}'>." in error_message
        mock_converter.assert_not_called()

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
    # Reason: Need Any to test various non-string types
    def test_raise_if_not_str_direct(self, non_string_value: Any, expected_type_name: str) -> None:  # noqa: ANN401
        """Test direct call to raise_if_not_str with non-string."""
        mock_converter = Mock()
        validator = IntegerMustBeFromStr(mock_converter)

        with pytest.raises(TypeError) as exc_info:
            validator.raise_if_not_str(non_string_value)

        error_message = str(exc_info.value)
        assert f"String required. Value is {non_string_value}" in error_message
        assert f"Type is <class '{expected_type_name}'>." in error_message

    def test_raise_if_not_str_with_string_does_nothing(self) -> None:
        """Test that raise_if_not_str does nothing for valid strings."""
        mock_converter = Mock()
        validator = IntegerMustBeFromStr(mock_converter)

        # Should not raise any exception
        validator.raise_if_not_str("valid_string")

    def test_validate_propagates_converter_exceptions(self) -> None:
        """Test that validate propagates exceptions from the converter function."""
        mock_converter = Mock(side_effect=ValueError("Invalid conversion"))
        validator = IntegerMustBeFromStr(mock_converter)

        with pytest.raises(ValueError, match="Invalid conversion"):
            validator.validate("invalid")

        mock_converter.assert_called_once_with("invalid")


class TestConstrainedInt:
    """Tests for ConstrainedInt class."""

    def test_default_class_attributes(self) -> None:
        """Test that ConstrainedInt has correct default attributes."""
        self._assert_default_constrained_int_attributes()

    def _assert_default_constrained_int_attributes(self) -> None:
        """Assert ConstrainedInt has correct default attribute values."""
        asserter = ConstrainedIntAsserter(ConstrainedInt)
        asserter.assert_strict_is_false()
        asserter.assert_constraint_attributes_are_none()

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (5, 5),
            ("10", 10),
            (5.7, 5),
            (True, 1),
            (False, 0),
        ],
    )
    # Reason: Need Any to test various invalid types in parametrized test
    def test_validate_with_non_strict_mode(self, value: Any, expected: int) -> None:  # noqa: ANN401
        """Test validate method in non-strict mode."""
        # Create a temporary class with no constraints
        test_constrained_int = cast(
            "Type[ConstrainedInt]",
            type("TestConstrainedInt", (ConstrainedInt,), {"strict": False}),
        )

        result = test_constrained_int.validate(value)
        assert result == expected

    @pytest.mark.parametrize(
        "value",
        [
            5,
            -10,
            0,
        ],
    )
    def test_validate_with_strict_mode_int(self, value: int) -> None:
        """Test validate method in strict mode with integers."""
        # Create a temporary class with strict=True
        strict_constrained_int = cast(
            "Type[ConstrainedInt]",
            type("StrictConstrainedInt", (ConstrainedInt,), {"strict": True}),
        )

        result = strict_constrained_int.validate(value)
        assert result == value

    @pytest.mark.parametrize(
        "invalid_value",
        [
            "5",
            5.7,
            True,
            False,
        ],
    )
    # Reason: Need Any to test various invalid types for strict mode
    def test_validate_with_strict_mode_raises_error(self, invalid_value: Any) -> None:  # noqa: ANN401
        """Test validate method in strict mode raises error for non-integers."""
        # Create a temporary class with strict=True
        strict_constrained_int = cast(
            "Type[ConstrainedInt]",
            type("StrictConstrainedInt", (ConstrainedInt,), {"strict": True}),
        )

        # Should raise some validation error from pydantic v1
        with pytest.raises((ValueError, TypeError)):  # Could be various pydantic v1 errors
            strict_constrained_int.validate(invalid_value)

    def test_number_size_validator_no_constraints(self) -> None:
        """Test number_size_validator with no constraints returns value unchanged."""
        # Create a class with no size constraints
        expected_value = 42
        no_constraints_int = cast("Type[ConstrainedInt]", type("NoConstraintsInt", (ConstrainedInt,), {}))

        result = no_constraints_int.number_size_validator(expected_value)
        assert result == expected_value

    @pytest.mark.parametrize(
        ("gt_value", "test_value", "should_pass"),
        [
            (5, 6, True),
            (5, 10, True),
            (5, 5, False),
            (5, 4, False),
        ],
    )
    # pylint: disable-next=line-too-long
    def test_number_size_validator_greater_gt(self, gt_value: int, test_value: int, should_pass: bool) -> None:  # noqa: FBT001
        """Test number_size_validator with gt constraint."""
        gt_constrained_int = cast(
            "Type[ConstrainedInt]",
            type("GtConstrainedInt", (ConstrainedInt,), {"gt": gt_value}),
        )

        if should_pass:
            result = gt_constrained_int.number_size_validator(test_value)
            assert result == test_value
        else:
            with pytest.raises(NumberNotGtError):
                gt_constrained_int.number_size_validator(test_value)

    @pytest.mark.parametrize(
        ("ge_value", "test_value", "should_pass"),
        [
            (5, 6, True),
            (5, 5, True),
            (5, 4, False),
        ],
    )
    # pylint: disable-next=line-too-long
    def test_number_size_validator_greater_ge(self, ge_value: int, test_value: int, should_pass: bool) -> None:  # noqa: FBT001
        """Test number_size_validator with ge constraint."""
        ge_constrained_int = cast(
            "Type[ConstrainedInt]",
            type("GeConstrainedInt", (ConstrainedInt,), {"ge": ge_value}),
        )

        if should_pass:
            result = ge_constrained_int.number_size_validator(test_value)
            assert result == test_value
        else:
            with pytest.raises(NumberNotGeError):
                ge_constrained_int.number_size_validator(test_value)

    @pytest.mark.parametrize(
        ("lt_value", "test_value", "should_pass"),
        [
            (5, 4, True),
            (5, 1, True),
            (5, 5, False),
            (5, 6, False),
        ],
    )
    # pylint: disable-next=line-too-long
    def test_number_size_validator_less_lt(self, lt_value: int, test_value: int, should_pass: bool) -> None:  # noqa: FBT001
        """Test number_size_validator with lt constraint."""
        lt_constrained_int = cast(
            "Type[ConstrainedInt]",
            type("LtConstrainedInt", (ConstrainedInt,), {"lt": lt_value}),
        )

        if should_pass:
            result = lt_constrained_int.number_size_validator(test_value)
            assert result == test_value
        else:
            with pytest.raises(NumberNotLtError):
                lt_constrained_int.number_size_validator(test_value)

    @pytest.mark.parametrize(
        ("le_value", "test_value", "should_pass"),
        [
            (5, 4, True),
            (5, 5, True),
            (5, 6, False),
        ],
    )
    # pylint: disable-next=line-too-long
    def test_number_size_validator_less_le(self, le_value: int, test_value: int, should_pass: bool) -> None:  # noqa: FBT001
        """Test number_size_validator with le constraint."""
        le_constrained_int = cast(
            "Type[ConstrainedInt]",
            type("LeConstrainedInt", (ConstrainedInt,), {"le": le_value}),
        )

        if should_pass:
            result = le_constrained_int.number_size_validator(test_value)
            assert result == test_value
        else:
            with pytest.raises(NumberNotLeError):
                le_constrained_int.number_size_validator(test_value)

    def test_number_multiple_validator_no_constraint(self) -> None:
        """Test number_multiple_validator with no multiple_of constraint."""
        expected_value = 42
        no_multiple_int = cast("Type[ConstrainedInt]", type("NoMultipleInt", (ConstrainedInt,), {"multiple_of": None}))

        result = no_multiple_int.number_multiple_validator(expected_value)
        assert result == expected_value

    @pytest.mark.parametrize(
        ("multiple_of_value", "test_value", "should_pass"),
        [
            (5, 10, True),
            (5, 15, True),
            (5, 0, True),
            (3, 9, True),
            (5, 7, False),
            (3, 8, False),
        ],
    )
    def test_number_multiple_validator_with_constraint(
        self,
        multiple_of_value: int,
        test_value: int,
        should_pass: bool,  # noqa: FBT001
    ) -> None:
        """Test number_multiple_validator with multiple_of constraint."""
        multiple_constrained_int = cast(
            "Type[ConstrainedInt]",
            type(
                "MultipleConstrainedInt",
                (ConstrainedInt,),
                {"multiple_of": multiple_of_value},
            ),
        )

        if should_pass:
            result = multiple_constrained_int.number_multiple_validator(test_value)
            assert result == test_value
        else:
            with pytest.raises(NumberNotMultipleError):
                multiple_constrained_int.number_multiple_validator(test_value)

    def test_get_pydantic_json_schema_with_constraints(self) -> None:
        """Test __get_pydantic_json_schema__ updates schema with constraints."""
        expected_min = 0
        expected_max = 99
        expected_multiple = 5
        full_constrained_int = cast(
            "Type[ConstrainedInt]",
            type(
                "FullConstrainedInt",
                (ConstrainedInt,),
                {"gt": expected_min, "le": expected_max, "multiple_of": expected_multiple},
            ),
        )

        field_schema: dict[str, Any] = {}
        full_constrained_int.__get_pydantic_json_schema__(field_schema)

        assert field_schema["exclusiveMinimum"] == expected_min
        assert field_schema["maximum"] == expected_max
        assert field_schema["multipleOf"] == expected_multiple

    def test_get_pydantic_json_schema_with_none_values(self) -> None:
        """Test __get_pydantic_json_schema__ with None constraint values."""
        no_constraints_int = cast("Type[ConstrainedInt]", type("NoConstraintsInt", (ConstrainedInt,), {}))

        field_schema: dict[str, Any] = {}
        no_constraints_int.__get_pydantic_json_schema__(field_schema)

        self._assert_schema_has_no_constraints(field_schema)

    def _assert_schema_has_no_constraints(self, field_schema: dict[str, Any]) -> None:
        """Assert field schema has no constraint values."""
        self._assert_minimum_constraints_absent(field_schema)
        self._assert_maximum_constraints_absent(field_schema)
        self._assert_multiple_constraint_absent(field_schema)

    def _assert_minimum_constraints_absent(self, field_schema: dict[str, Any]) -> None:
        """Assert minimum constraint fields are absent from schema."""
        assert "exclusiveMinimum" not in field_schema
        assert "minimum" not in field_schema

    def _assert_maximum_constraints_absent(self, field_schema: dict[str, Any]) -> None:
        """Assert maximum constraint fields are absent from schema."""
        assert "exclusiveMaximum" not in field_schema
        assert "maximum" not in field_schema

    def _assert_multiple_constraint_absent(self, field_schema: dict[str, Any]) -> None:
        """Assert multipleOf constraint field is absent from schema."""
        assert "multipleOf" not in field_schema


class TestConstrainedStringToInt:
    """Tests for ConstrainedStringToInt class."""

    def test_model_config(self) -> None:
        """Test that model_config allows arbitrary types."""
        assert ConstrainedStringToInt.model_config["arbitrary_types_allowed"] is True

    def test_validate_calls_integer_must_be_from_str(self) -> None:
        """Test that validate method calls integer_must_be_from_str."""

        # Create a concrete implementation for testing
        class TestStringToInt(ConstrainedStringToInt):
            @classmethod
            def string_to_int(cls, value: str) -> int:
                return int(value)

        expected_result = 42
        result = TestStringToInt.validate("42")
        assert result == expected_result

    @pytest.mark.parametrize(
        ("non_string_value", "expected_message"),
        [
            (123, "string required"),
            (12.5, "string required"),
            (None, "string required"),
            ([], "string required"),
            ({}, "string required"),
        ],
    )
    def test_integer_must_be_from_str_with_non_string_raises_error(
        self,
        # Reason: Need Any to test various non-string types
        non_string_value: Any,  # noqa: ANN401
        expected_message: str,
    ) -> None:
        """Test that integer_must_be_from_str raises TypeError for non-string input."""

        # Create a concrete implementation for testing
        class TestStringToInt(ConstrainedStringToInt):
            @classmethod
            def string_to_int(cls, value: str) -> int:
                return int(value)

        with pytest.raises(TypeError, match=expected_message):
            TestStringToInt.integer_must_be_from_str(non_string_value)

    def test_integer_must_be_from_str_calls_string_to_int(self) -> None:
        """Test that integer_must_be_from_str calls string_to_int with valid string."""

        # Create a concrete implementation for testing
        class TestStringToInt(ConstrainedStringToInt):
            @classmethod
            def string_to_int(cls, value: str) -> int:
                return int(value) * 2  # Custom conversion for testing

        expected_result = 42
        result = TestStringToInt.integer_must_be_from_str("21")
        assert result == expected_result

    def test_string_to_int_abstract_method(self) -> None:
        """Test that string_to_int is abstract and raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            ConstrainedStringToInt.string_to_int("test")

    def test_validate_with_constraints(self) -> None:
        """Test validate method with various constraints."""

        # Create a concrete implementation with constraints
        class ConstrainedTestInt(ConstrainedStringToInt):
            """Test class with constraints for validation testing."""

            gt = 0
            lt = 100
            multiple_of = 5

            @classmethod
            def string_to_int(cls, value: str) -> int:
                return int(value)

        # Valid value
        expected_result = 25
        result = ConstrainedTestInt.validate("25")
        assert result == expected_result

        # Test constraint violations
        with pytest.raises(NumberNotGtError):
            ConstrainedTestInt.validate("0")

        with pytest.raises(NumberNotLtError):
            ConstrainedTestInt.validate("100")

        with pytest.raises(NumberNotMultipleError):
            ConstrainedTestInt.validate("7")


class TestConstringtointFunction:
    """Tests for constringtoint function."""

    def test_creates_type_with_default_parameters(self) -> None:
        """Test that constringtoint creates a type with default parameters."""

        # Create a concrete base class for testing
        class TestStringToInt(ConstrainedStringToInt):
            @classmethod
            def string_to_int(cls, value: str) -> int:
                return int(value)

        result_type = constringtoint("TestType", TestStringToInt)

        self._assert_type_inheritance_and_name(result_type, TestStringToInt, "TestType")
        self._assert_type_has_default_attributes(result_type)

    def _assert_type_inheritance_and_name(self, result_type: type, base_class: type, expected_name: str) -> None:
        """Assert type inheritance and name."""
        assert issubclass(result_type, base_class)
        assert result_type.__name__ == expected_name

    def _assert_type_has_default_attributes(self, result_type: type) -> None:
        """Assert type has default constraint attribute values."""
        asserter = ConstrainedIntAsserter(result_type)
        asserter.assert_strict_is_false()
        asserter.assert_constraint_attributes_are_none()

    @pytest.mark.parametrize(
        "params",
        [
            ConstraintIntParams(strict=True, gt=1, le=99, multiple_of=5),
            ConstraintIntParams(strict=False, ge=1, lt=50, multiple_of=10),
            ConstraintIntParams(strict=True),
        ],
    )
    def test_creates_type_with_all_parameters(self, params: ConstraintIntParams) -> None:
        """Test that constringtoint creates a type with all parameters set."""

        # Create a concrete base class for testing
        class TestStringToInt(ConstrainedStringToInt):
            @classmethod
            def string_to_int(cls, value: str) -> int:
                return int(value)

        result_type = constringtoint(  # pylint: disable=duplicate-code
            "ParameterizedType",
            TestStringToInt,
            strict=params.strict,
            gt=params.gt,
            ge=params.ge,
            lt=params.lt,
            le=params.le,
            multiple_of=params.multiple_of,
        )

        self._assert_type_inheritance_and_name(result_type, TestStringToInt, "ParameterizedType")
        ConstraintValueAsserter(result_type, params).assert_all()

    def test_created_type_functionality(self) -> None:
        """Test that the created type functions correctly."""

        # Create a concrete base class for testing
        class TestStringToInt(ConstrainedStringToInt):
            @classmethod
            def string_to_int(cls, value: str) -> int:
                return int(value.replace(",", ""))  # Remove commas

        # Create a constrained type
        expected_value_1 = 25
        expected_value_2 = 125
        comma_string_to_int = constringtoint("CommaStringToInt", TestStringToInt, gt=0, lt=1000, multiple_of=5)

        # Test valid conversion
        result = cast("Type[ConstrainedStringToInt]", comma_string_to_int).validate("25")  # pylint: disable=no-member
        assert result == expected_value_1

        # Test with comma removal
        result = cast("Type[ConstrainedStringToInt]", comma_string_to_int).validate("125")  # pylint: disable=no-member
        assert result == expected_value_2

        # Test constraint validation
        with pytest.raises(NumberNotGtError):
            cast("Type[ConstrainedStringToInt]", comma_string_to_int).validate("0")  # pylint: disable=no-member

        with pytest.raises(NumberNotLtError):
            cast("Type[ConstrainedStringToInt]", comma_string_to_int).validate("1000")  # pylint: disable=no-member

        with pytest.raises(NumberNotMultipleError):
            cast("Type[ConstrainedStringToInt]", comma_string_to_int).validate("7")  # pylint: disable=no-member


class TestModuleIntegration:
    """Integration tests for the abstract module components."""

    def test_full_workflow_with_integer_must_be_from_str(self) -> None:
        """Test complete workflow using IntegerMustBeFromStr."""

        def custom_converter(value: str) -> int:
            # Remove commas and convert
            return int(value.replace(",", ""))

        validator = IntegerMustBeFromStr(custom_converter)

        # Test successful conversion
        expected_result = 1234
        result = validator.validate("1,234")
        assert result == expected_result

        # Test error handling
        with pytest.raises(TypeError):
            validator.validate(123)

    def test_full_workflow_with_constringtoint(self) -> None:
        """Test complete workflow using constringtoint function."""

        # Create a concrete implementation
        class CustomStringToInt(ConstrainedStringToInt):
            @classmethod
            def string_to_int(cls, value: str) -> int:
                # Custom logic: multiply by 2
                return int(value) * 2

        # Create constrained type
        expected_result = 12
        double_string_to_int = constringtoint(
            "DoubleStringToInt",
            CustomStringToInt,
            strict=False,
            gt=10,
            le=200,
            multiple_of=4,
        )

        # Test valid conversion (5 * 2 = 10, but 10 is not > 10)
        with pytest.raises(NumberNotGtError):
            cast("Type[ConstrainedStringToInt]", double_string_to_int).validate("5")  # pylint: disable=no-member

        # Test valid conversion (6 * 2 = 12, which is > 10, <= 200, and multiple of 4)
        result = cast("Type[ConstrainedStringToInt]", double_string_to_int).validate("6")  # pylint: disable=no-member
        assert result == expected_result

        # Test constraint violations
        with pytest.raises(NumberNotLeError):
            cast("Type[ConstrainedStringToInt]", double_string_to_int).validate("101")  # pylint: disable=no-member

        with pytest.raises(NumberNotMultipleError):
            cast("Type[ConstrainedStringToInt]", double_string_to_int).validate(  # pylint: disable=no-member
                "7",
            )  # 7 * 2 = 14, which is not multiple of 4

    def test_module_exports_expected_components(self) -> None:
        """Test that the module exports the expected components."""
        self._assert_components_are_callable()
        self._assert_inheritance_relationships()

    def _assert_components_are_callable(self) -> None:
        """Assert all exported components are callable."""
        assert callable(IntegerMustBeFromStr)
        assert callable(ConstrainedInt)
        assert callable(ConstrainedStringToInt)
        assert callable(constringtoint)

    def _assert_inheritance_relationships(self) -> None:
        """Assert correct inheritance relationships exist."""
        assert issubclass(ConstrainedStringToInt, ConstrainedInt)
