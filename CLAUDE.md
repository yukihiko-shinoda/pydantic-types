# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **pydantictypes**, a Python library that provides common Pydantic type definitions for string-to-integer conversions and datetime parsing. It's built on top of Pydantic v2 and specializes in handling financial data formats (Japanese yen strings) and localized data transformations.

## Development Commands

### Package Management

```bash
# Install dependencies and sync environment
uv sync

# Install for specific Python version
uv install --python 3.7
```

### Testing

```bash
# Run tests without slow tests
uv run inv test

# Run all tests
uv run inv test.all

# Check test coverage
uv run inv test.cov

# Run specific test file
uv run pytest tests/test_pydantictypes.py

# Run specific test module
uv run pytest tests.test_pydantictypes
```

### Code Quality and Linting

```bash
# Run style checks (includes ruff, docformatter, and other tools)
uv run inv style --check

# Run fast lint checks
uv run inv lint

# Run slow lint checks
uv run inv lint.deep
```

### Building and Distribution

```bash
# Build package
uv run inv dist

# Clean build artifacts and caches
uv run inv clean
```

## Architecture Overview

### Core Components

1. **Abstract Base Layer** (`abstract_string_to_*.py`):
   - `ConstrainedStringToInt`: Base class for string-to-integer conversions
   - `ConstrainedInt`: Provides validation constraints (gt, ge, lt, le, multiple_of)
   - Abstract validators for type enforcement

2. **Utility Layer** (`utility.py`):
   - `Utility` class with static conversion methods
   - Core string processing logic for different formats
   - Handles comma removal and regex pattern matching

3. **Validators Layer** (`validators.py`):
   - Custom validators extending Pydantic v1 validators
   - Optional variants for nullable types
   - Number validation with constraints

4. **Type Implementations**:
   - Individual modules for each specific type (e.g., `kanji_yen_string_to_int.py`)
   - Use `Annotated` types with `BeforeValidator`
   - Leverage `annotated_types` for constraint definitions

### Key Type Categories

- **String-to-Integer Converters**: Handle comma-separated numbers, Japanese yen formats
- **DateTime Converters**: Parse various date string formats (YYYY/MM/DD, MM/DD, YYYYMMDD)
- **Optional Variants**: Nullable versions that return None for empty strings

### Validation Pattern

```python
Annotated[
    TargetType,
    BeforeValidator(ValidatorClass(conversion_function).validate),
    [Additional Constraints...]
]
```

## Development Guidelines

### Code Style

- Uses Ruff for formatting with line length 119
- Ruff for linting with comprehensive rule set
- Follows Google docstring convention
- Type hints required throughout (`strict = true` in mypy)

### Testing

- Uses pytest for testing framework
- Test files mirror package structure in `tests/` directory
- Supports testing on Python 3.7+ (oldest supported version)

### Dependencies

- **Pydantic v2** (>=2.0.0): Core validation framework
- **typing_extensions**: For Python <3.11 compatibility
- **annotated_types**: For constraint definitions
- Still uses Pydantic v1 packages

### Adding New Types

1. Create new module in `pydantictypes/` directory
2. Implement using the established validation pattern
3. Add to `__init__.py` imports and `__all__` list
4. Include comprehensive tests in `tests/pydantictypes/`
5. Update README.md with usage examples

### Release Process

1. Update version in `pyproject.toml` and `pydantictypes/__init__.py`
2. Run style checks: `uv run inv style --check`
3. Run fast lint checks: `uv run inv lint`
4. Ensure tests without slow tests pass: `uv run inv test`
5. Run fast lint checks: `uv run inv lint.deep`
6. Ensure all tests pass: `uv run inv test.all`
7. Use bump2version for version management
8. CI/CD handles PyPI deployment on tag push
