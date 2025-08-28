# Issue #205 Technical Analysis

## Repository Technology Stack Analysis

**Primary Technology**: Python CLI Application
**Target Distribution**: PyPI via uvx (universal package runner)
**Package Manager**: uv exclusively (mandated by Python stack guidelines)
**CLI Framework**: Click (already in dependencies)
**Build System**: hatchling (already configured)

### Technology Stack Components

#### 1. Python CLI Development with Click Framework
**Technology Guidelines**: @templates/stacks/python.md

**MANDATORY PATTERNS:**
- **Package Management**: Use `uv` exclusively - NEVER pip, poetry, conda
- **Type Hints**: Required for all functions and methods
- **Code Quality**: Automatic `ruff` formatting and linting, `mypy` type checking
- **Project Structure**: src/package_name/ layout (already implemented)
- **Testing**: pytest with minimum 80% coverage
- **Error Handling**: Explicit exception handling, never bare except clauses

**Current CLI Analysis:**
- ✅ Click framework already implemented (`click>=8.1` dependency)
- ✅ Proper CLI structure with `@click.group()` and subcommands
- ✅ Version management via Click decorators
- ⚠️ Missing comprehensive type hints
- ⚠️ Missing error handling patterns (bare try/except usage)
- ⚠️ No dataclasses for configuration structures

#### 2. Modern Python Packaging with pyproject.toml and hatchling
**Current State Analysis:**

**✅ COMPLIANT:**
- hatchling build backend configured
- Python >=3.13 requirement
- Proper project metadata structure
- uv development dependencies

**🔧 REQUIRES UPDATES:**
- Package name change from "ai-code-forge" to maintain same name but add "acf" alias
- Template bundling via hatchling force-include not implemented
- Missing console script for "acf" alias
- pyproject.toml structure needs optimization for Phase 1 scope

#### 3. uvx Distribution and PyPI Packaging
**Distribution Strategy:**
- **Primary Package**: "ai-code-forge" on PyPI
- **Installation Method**: `uvx install ai-code-forge`
- **Command Aliases**: Both `ai-code-forge` and `acf` available
- **Target Audience**: External repositories (not self-hosting)

**REQUIRED IMPLEMENTATIONS:**
- Add "acf" console script entry point
- Ensure uvx compatibility (no special requirements needed)
- Configure proper project URLs and metadata for PyPI
- Test installation via uvx in isolated environment

#### 4. Package Resources for Template Bundling
**Current Gap Analysis:**
- Templates directory exists at `/templates/` in repository root
- No current mechanism for bundling templates in package
- Need importlib.resources implementation for runtime template access

**MANDATORY IMPLEMENTATION:**
```python
# Required pattern from Python guidelines
from importlib import resources
import json
from pathlib import Path

def load_template(template_name: str) -> str:
    """Load bundled template resource."""
    try:
        template_files = resources.files("ai_code_forge.templates")
        template_file = template_files / f"{template_name}.template"
        return template_file.read_text()
    except FileNotFoundError as e:
        logger.error(f"Template not found: {template_name}")
        raise  # Re-raise, don't swallow (per guidelines)
```

**hatchling force-include configuration needed:**
```toml
[tool.hatch.build.targets.wheel]
packages = ["src/ai_code_forge"]
force-include = {"templates" = "ai_code_forge/templates"}
```

#### 5. JSON State Management Patterns
**Current State Approach**: Three-file JSON structure in `.acf/` directory

**MANDATORY PYTHON PATTERNS:**
```python
@dataclass
class ACFState:
    """State management dataclass (required by guidelines)."""
    installation_id: str
    template_source: str
    last_update: str | None = None

# Required context manager pattern
class StateManager:
    def __enter__(self) -> ACFState:
        return self._load_state()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self._save_state()
        # Explicit error handling per guidelines
```

**Three-file State Structure:**
1. `config.json` - User preferences and settings
2. `state.json` - Installation tracking and metadata
3. `cache.json` - Template cache and performance optimization

#### 6. Python Project Structure Best Practices

**MANDATORY STRUCTURE (per guidelines):**
```
cli/
├── src/ai_code_forge/           # Main package with __init__.py
│   ├── commands/                # Click command modules
│   ├── core/                    # Core functionality
│   ├── templates/               # Bundled templates (bundled via hatchling)
│   └── utils/                   # Utility functions
├── tests/                       # test_*.py files only
├── pyproject.toml               # uv-managed configuration
└── README.md
```

**ENFORCE REQUIREMENTS:**
- pathlib for all file operations (no os.path)
- Context managers for resource management
- Dataclasses for data structures
- Comprehensive docstrings for public APIs

## Architectural Guidelines for CLI Implementation

### Phase 1 Command Architecture

#### Command: `acf status`
**Purpose**: State inspection and configuration analysis
**Technical Requirements**:
- Read three JSON state files with proper error handling
- Display structured output using Click's echo functions
- Validate .acf directory structure
- Check template source accessibility

**Implementation Pattern**:
```python
@click.command()
@click.option("--format", type=click.Choice(["text", "json"]), default="text")
def status(format: str) -> None:
    """Show ACF installation status and configuration."""
    try:
        with StateManager() as state:
            if format == "json":
                click.echo(state.to_json())
            else:
                display_status_text(state)
    except StateError as e:
        logger.error(f"State management error: {e}")
        click.echo("❌ Could not read ACF state", err=True)
        raise click.ClickException(str(e))
```

#### Command: `acf init`
**Purpose**: Bootstrap new repositories with templates
**Technical Requirements**:
- Create .acf directory structure
- Initialize three JSON state files using dataclasses
- Copy templates from bundled resources using importlib.resources
- Validate target directory permissions

#### Command: `acf update`
**Purpose**: Template synchronization with customization preservation
**Technical Requirements**:
- Compare current templates with bundled versions
- Preserve user customizations (requires diff analysis)
- Update state.json with sync metadata
- Handle merge conflicts gracefully

### Validation Using AI-Code-Forge Repository

**Self-Validation Strategy:**
1. Test CLI installation in ai-code-forge repository itself
2. Verify template bundling includes all files from /templates/
3. Validate state management with existing .claude/ directory
4. Test uvx installation and both command aliases

**Quality Assurance Requirements:**
- Type checking with mypy on all modules
- Test coverage minimum 80% (per Python guidelines)
- Integration tests with temporary directories
- CLI testing using Click's testing utilities

### Technology Integration Concerns

#### Template Source Management
**Current Challenge**: Repository contains /templates/ but CLI needs bundled access
**Solution**: hatchling force-include + importlib.resources pattern

#### State Directory Coordination  
**Current Challenge**: Existing .claude/ vs new .acf/ directory structure
**Solution**: CLI operates only on .acf/ directory, preserves existing .claude/

#### Version Synchronization
**Current Challenge**: Template versions vs CLI package versions
**Solution**: Embed template version metadata in bundled resources

## Critical Implementation Requirements

### MANDATORY ADHERENCE TO PYTHON GUIDELINES
1. **uv exclusive usage** - No pip, poetry, or conda in any documentation or scripts
2. **Type hints for all functions** - No untyped public APIs
3. **Dataclasses for data structures** - Replace plain dicts with typed dataclasses
4. **Context managers for resources** - File operations and state management
5. **Explicit error handling** - No bare except clauses, proper exception types
6. **pathlib for file operations** - No os.path usage
7. **ruff formatting and mypy type checking** - Integrate into development workflow

### BUILD SYSTEM REQUIREMENTS
1. **hatchling force-include** for template bundling
2. **Dual console scripts** - both "ai-code-forge" and "acf" entry points
3. **uv lock file maintenance** for reproducible dependencies
4. **PyPI metadata optimization** for discoverability

### TESTING STRATEGY
1. **Click testing utilities** for CLI command testing
2. **pytest fixtures** for temporary directory management
3. **Integration tests** with real template bundling
4. **uvx installation testing** in isolated environments

## Architecture Risks and Mitigation

### Risk: Template Bundling Complexity
**Mitigation**: Use proven importlib.resources patterns, test with package building

### Risk: State Management Race Conditions  
**Mitigation**: Implement file locking, use atomic write operations

### Risk: uvx Distribution Issues
**Mitigation**: Test installation process, provide fallback documentation

### Risk: Version Compatibility
**Mitigation**: Strict Python >=3.13 requirement, comprehensive dependency specification

## Development Workflow Integration

### Code Quality Pipeline
```bash
uv run ruff format .       # Format before committing
uv run ruff check .        # Lint and fix issues
uv run mypy src/           # Type checking required
uv run pytest --cov=src   # Minimum 80% coverage
```

### Package Building and Testing
```bash
uv build                   # Create wheel and sdist
uvx install ./dist/*.whl   # Test installation
acf status                 # Test CLI functionality
```

### Template Bundling Validation
```python
# Verify bundled resources accessible
from importlib import resources
templates = resources.files("ai_code_forge.templates")
assert templates.is_dir()
assert (templates / "CLAUDE.md.template").exists()
```

This technical analysis provides the comprehensive technology stack insights and architectural guidelines needed for the CLI rewrite implementation, ensuring full compliance with established Python development patterns and project requirements.