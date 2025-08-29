# AI Code Forge CLI

A command-line tool for managing AI Code Forge templates and configurations.

## Installation

```bash
# Install via uvx (recommended for ephemeral usage)
uvx acforge --help

# Install persistently
uv tool install acforge
```

## Commands

### `acforge status`

Show comprehensive status of repository configuration and templates.

```bash
# Human-readable status
acforge status

# Verbose output with detailed information
acforge status --verbose

# JSON output for scripting
acforge status --format json
```

## Development

```bash
# Install in development mode
cd cli
uv pip install -e .

# Run tests
uv run pytest

# Type checking
uv run mypy src/

# Formatting
uv run ruff format
uv run ruff check
```

## Architecture

This CLI manages AI development workflows through:

- **Template Management**: Bundled templates for agents, commands, and configurations
- **State Management**: Atomic state tracking in `.acforge/state.json`  
- **Configuration Analysis**: Detection and analysis of existing configurations
- **Customization Preservation**: Support for `.local` files and user modifications

## Phase 1 Implementation

Currently implements:
- ✅ `acforge status` - Complete status reporting and analysis

Coming next:
- 🚧 `acforge init` - Repository initialization with templates
- 🚧 `acforge update` - Template synchronization with customization preservation