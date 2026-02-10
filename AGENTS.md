# AGENTS.md - Coding Agent Guidelines for odooshow

## Project Overview

odooshow is a Python library that uses `rich` to render Odoo recordsets as formatted
tables in the Odoo shell. It provides visualization utilities for developers working
with Odoo data.

- **License**: AGPL-3.0
- **Python**: >=3.6.3, <4.0
- **Main dependency**: rich ^12.5.1
- **Package manager**: Poetry

## Build & Development Commands

### Installation

```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Testing

```bash
# Run all tests
poetry run pytest

# Run a single test file
poetry run pytest tests/test_odooshow.py

# Run a specific test function
poetry run pytest tests/test_odooshow.py::test_version

# Run with verbose output
poetry run pytest -v

# Run with coverage (if configured)
poetry run pytest --cov=odooshow
```

Note: Tests require an Odoo instance to be fully functional. The `tests/local_tests.py`
file demonstrates manual testing with OdooRPC against a local Odoo server.

### Linting & Code Quality

```bash
# Run flake8 (primary linter)
poetry run flake8 odooshow/ tests/

# Run pylint with optional checks
poetry run pylint --rcfile=.pylintrc odooshow/

# Run pylint with mandatory checks only
poetry run pylint --rcfile=.pylintrc-mandatory odooshow/

# Run black formatter
poetry run black odooshow/ tests/

# Run isort for import sorting
poetry run isort odooshow/ tests/

# Run all pre-commit hooks
pre-commit run --all-files
```

### Building & Publishing

```bash
# Build package
poetry build

# Publish is automated via GitHub Actions on tag push (v*.*.*)
```

## Code Style Guidelines

### Formatting

- **Formatter**: Black
- **Line length**: 88 characters (configured in .flake8)
- **Max complexity**: 16 (configured in .flake8)
- **Encoding pragma**: Do not use (removed by pre-commit)
- **Line endings**: LF only (no CRLF)

### Import Conventions

- **Import sorter**: isort
- **Order**: Standard library, third-party, local imports
- **Style**: Each import on separate lines, alphabetically sorted within groups
- Unused imports are auto-removed by autoflake
- `__init__.py` files may have unused imports (F401 ignored)

Example:

```python
from odoo.release import major_version
import warnings

from rich import box
from rich.console import Console
from rich.table import Table
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `OdooShow`)
- **Functions/Methods**: snake_case (e.g., `show_read`, `_cell_value`)
- **Private methods**: Prefix with underscore (e.g., `_render_record_rows`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `GROUP_OPERATORS`)
- **Module-level variables**: snake_case (e.g., `o_purple`, `console`)

### Type Hints & Documentation

- Docstrings use Google/Sphinx style with `:param` and `:return` tags
- Type hints in docstrings rather than annotations (Python 3.6 compatibility)
- Document public functions thoroughly; private methods have briefer docs

Example:

```python
def _cell_value(self, record, field, attrs):
    """Cell value treatment and formatting

    :param record record: Odoo record
    :param str field: Field name
    :param dict attrs: Field attributes
    :return any: formatted value
    """
```

### Error Handling

- Use broad `except Exception` sparingly, only for OdooRPC compatibility edge cases
- Prefer explicit error handling where possible
- Use warnings module for deprecation warnings

### Class Design Patterns

- Use `__all__` to explicitly export public API
- Use decorators for cross-cutting concerns (e.g., `@unpack_values`)
- Method dispatch via string interpolation pattern: `f"_{type}_format"`
- Check method existence with `__contains__`: `method_name in self`

## Project Structure

```
odooshow/
├── odooshow/
│   ├── __init__.py      # Package exports, version info
│   └── odooshow.py      # Main implementation
├── tests/
│   ├── __init__.py
│   ├── test_odooshow.py # pytest tests
│   └── local_tests.py   # Manual OdooRPC tests
├── pyproject.toml       # Poetry config, dependencies
├── .flake8              # Flake8 configuration
├── .pylintrc            # Pylint config (optional checks)
├── .pylintrc-mandatory  # Pylint config (mandatory checks)
└── .pre-commit-config.yaml
```

## Key Patterns

### Odoo Version Compatibility

The code handles multiple Odoo versions:

```python
from odoo.release import major_version

if major_version < "18.0" and view_type == "list":
    view_type = "tree"
if major_version >= "16.0":
    # Use new API
else:
    # Use deprecated API with warning suppression
```

### Rich Table Rendering

- Use `rich.table.Table` for structured output
- Use `rich.console.Console` for printing
- Support hyperlinks in supported terminals: `[link=URL]text[/link]`
- Use emoji codes for boolean rendering: `:heavy_check_mark:`

### Public API

Only two functions are exported:

- `show(records, fields=None, ...)` - Render recordset as table
- `show_read(read_records, ...)` - Render model.read() results

## Pre-commit Hooks (in order)

1. forbidden-files - Block .rej files
2. autoflake - Remove unused imports/variables
3. black - Code formatting
4. pyupgrade - Python syntax upgrades
5. isort - Import sorting
6. prettier - XML/YAML formatting
7. trailing-whitespace, end-of-file-fixer, etc.
8. flake8 - Linting
9. pylint - Static analysis
10. eslint - JavaScript (if applicable)

## Version Management

- Version defined in both `pyproject.toml` and `odooshow/__init__.py`
- Keep both in sync when updating
- Use semantic versioning (currently 0.6.1)
- Tags trigger PyPI publish: `v*.*.*`
