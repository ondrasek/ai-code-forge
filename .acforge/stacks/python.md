# Python Stack Instructions

MANDATORY operational instructions for Claude Code when working with Python projects.

## Package Management - NO EXCEPTIONS

**MANDATORY: Use uv exclusively** - NEVER use pip, poetry, conda, or other tools.

```bash
uv init                     # New projects only
uv add package             # Add dependencies
uv add --dev pytest        # Development dependencies
uv run python script.py    # Execute scripts
uv run pytest             # Run tests
```

## Project Structure - ENFORCE

**MANDATORY structure for new Python projects:**
```
src/package_name/          # Main package with __init__.py
tests/                     # test_*.py files only
pyproject.toml             # uv-managed configuration
```

## Code Quality - AUTOMATIC

**MANDATORY quality tools setup:**
```bash
uv add --dev ruff pytest mypy
uv run ruff format .       # Format before committing
uv run ruff check .        # Lint and fix
uv run mypy src/           # Type checking required
uv run pytest --cov=src   # Minimum 80% coverage
```

## Required Patterns - ENFORCE

**MANDATORY type hints for all functions:**
```python
def process(items: list[str], config: dict[str, Any] | None = None) -> bool:
    """Process items with optional configuration."""
    pass
```

**MANDATORY dataclasses for data structures:**
```python
@dataclass
class User:
    name: str
    email: str | None = None
```

**MANDATORY context managers for resources:**
```python
with database_connection() as conn:
    # Use connection - automatic cleanup
```

**MANDATORY explicit error handling:**
```python
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise  # Re-raise, don't swallow
```

## Environment Configuration - REQUIRED

**MANDATORY environment setup:**
```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
```

## Non-Negotiable Requirements

- **ENFORCE**: PEP 8 compliance via ruff formatting
- **REQUIRE**: Type hints for all public functions and methods
- **MANDATE**: Docstrings for all public APIs
- **NO EXCEPTIONS**: Explicit error handling - never bare except clauses
- **ENFORCE**: pathlib for all file operations - no os.path
- **REQUIRE**: Test coverage minimum 80%
- **MANDATE**: Use dataclasses over plain classes for data
- **ENFORCE**: Context managers for resource management