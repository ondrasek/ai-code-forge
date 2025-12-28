# acforge-cli Tech Stack

## Core Technology

**Language**: Python 3.14+
- Latest Python features
- Modern async/await support
- Enhanced type hints and pattern matching
- Performance improvements

## CLI Framework

**Typer** - Modern CLI framework
- Type-hint based command definitions
- Built on Click (proven, reliable)
- Automatic help generation
- Excellent support for namespace commands
- Perfect for complex CLI structures like `acforge module add`, `acforge workflow start-from-scratch`

**Rich** - Terminal output formatting
- Beautiful tables, progress bars, and formatting
- Syntax highlighting for code/config display
- Markdown rendering in terminal
- Seamless integration with Typer
- Enhanced user experience

## Configuration & Data Management

**Pydantic** - Data validation and serialization
- Type-safe configuration models
- Automatic validation
- Serialization to/from YAML
- Clear error messages
- Perfect for `.acforge.yaml` management

**PyYAML** - YAML parsing
- Human-readable configuration files
- Industry standard for config files
- Works seamlessly with Pydantic

## Git Integration

**Hybrid Approach**:

1. **subprocess + git CLI** - For git subtree operations
   - Direct control over complex subtree commands
   - Full access to git subtree features
   - Reliable and predictable

2. **GitPython** - For standard git operations
   - Status checking
   - Diff generation
   - Branch management
   - Cleaner API for simple operations

## File Merging System

**Strategy Pattern** - Plugin-based merge strategies
- Different strategies for different file types:
  - **UNION Strategy**: `.gitignore`, `.dockerignore` - merge all entries
  - **Template Strategy**: `pyproject.toml`, config files - structured merge
  - **Append Strategy**: `.claude/agents/` - separate files, no conflicts
  - **User Resolution Strategy**: Conflicts require manual resolution
- Extensible for new file types
- Type-safe strategy interfaces

## Testing

**pytest** - Testing framework
- Modern, fixture-based testing
- Rich plugin ecosystem
- Excellent async support

**Hypothesis** - Property-based testing
- Generates edge cases automatically
- Tests properties rather than examples
- Catches bugs traditional tests miss
- Perfect for testing file merging strategies

**pytest-cov** - Coverage reporting
- Track test coverage
- Identify untested code paths

## Packaging & Distribution

**UV** - Modern Python package manager
- Extremely fast (Rust-based)
- Replaces pip, pip-tools, virtualenv, poetry
- Perfect for `uvx acforge` usage
- Lock files for reproducible builds
- PEP 517/518 compliant

## Additional Tools

**Ruff** - Linting and formatting
- Extremely fast (Rust-based)
- Replaces flake8, black, isort
- Consistent code style
- Configured via `pyproject.toml`

**MyPy** - Static type checking
- Type safety validation
- Works with Pydantic models
- Catches errors before runtime

## Project Structure

```
acforge-cli/
├── src/
│   └── acforge/
│       ├── __init__.py
│       ├── cli/              # Typer CLI commands
│       │   ├── __init__.py
│       │   ├── main.py       # Entry point
│       │   ├── module.py     # acforge module commands
│       │   ├── workflow.py   # acforge workflow commands
│       │   ├── issue.py      # acforge issue commands
│       │   ├── pr.py         # acforge pr commands
│       │   └── devcontainer.py
│       ├── core/             # Core functionality
│       │   ├── git.py        # Git operations
│       │   ├── config.py     # Pydantic models
│       │   ├── merge.py      # File merging strategies
│       │   └── registry.py   # Module discovery
│       └── strategies/       # Merge strategy implementations
│           ├── union.py
│           ├── template.py
│           └── append.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── property/             # Hypothesis tests
├── pyproject.toml            # UV/PEP 517 configuration
├── uv.lock                   # UV lock file
└── README.md
```

## Development Workflow

1. **UV for environment management**: `uv venv`, `uv pip install`
2. **Ruff for linting**: `ruff check src/`
3. **MyPy for type checking**: `mypy src/`
4. **Pytest for testing**: `pytest tests/`
5. **Hypothesis for property testing**: Tests in `tests/property/`

## Key Dependencies

```toml
[project]
name = "acforge"
requires-python = ">=3.14"
dependencies = [
    "typer[all]>=0.12.0",      # CLI framework with Rich integration
    "rich>=13.0.0",             # Terminal formatting
    "pydantic>=2.0.0",          # Data validation
    "pyyaml>=6.0",              # YAML parsing
    "gitpython>=3.1.0",         # Git operations
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "hypothesis>=6.0.0",
    "mypy>=1.8.0",
    "ruff>=0.2.0",
]
```

## Design Principles

1. **Type Safety First**: Use Pydantic and MyPy for runtime and static type checking
2. **Modern Python**: Leverage Python 3.14+ features (pattern matching, type hints)
3. **Fast Tooling**: Use Rust-based tools (UV, Ruff) for speed
4. **Beautiful UX**: Rich terminal output for excellent developer experience
5. **Extensible**: Strategy pattern allows easy addition of new merge strategies
6. **Testable**: Property-based testing with Hypothesis ensures robustness

## Why This Stack?

- **Fast**: UV and Ruff provide blazing-fast development experience
- **Modern**: Leverages latest Python 3.14+ features
- **Type-Safe**: Pydantic + MyPy catch errors early
- **User-Friendly**: Rich + Typer provide beautiful CLI UX
- **Reliable**: Hypothesis testing finds edge cases
- **Maintainable**: Clear patterns and strong typing
- **Future-Proof**: Modern tools with active development
