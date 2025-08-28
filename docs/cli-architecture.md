# AI Code Forge CLI Architecture

**Cross-Reference**: [GitHub Issue #205](https://github.com/ondrasek/ai-code-forge/issues/205) - CLI Architecture Rewrite Specification

## Overview

The AI Code Forge CLI (`acf`) is a configuration management tool for coding agents (Claude Code, Cursor, etc.). It provides hassle-free setup and maintenance of agent configurations in any repository using templates and blueprints from the ai-code-forge project.

## Core Principles

### Single Source of Truth
- Templates exist only in `/templates` directory of ai-code-forge repository
- No duplication of content in repository structure
- Build-time bundling eliminates runtime template discovery complexity

### External Repository Focus
- CLI operates on target repositories (not ai-code-forge itself)
- Users run `uvx acf` commands from their project directory
- No requirement to clone or know about ai-code-forge repository structure

### Minimal State Management
- State exists only in `.acf/` directory within each target repository
- No global configuration files (`~/.acf`, `/etc/acf`, etc.)
- Clean, self-contained per-repository state

## Architecture Decisions

### Distribution Model
```
User: uvx ai-code-forge <command>
  ↓
PyPI Package (ai-code-forge)
  ↓  
Bundled Templates (via hatchling force-include)
  ↓
Target Repository Configuration
```

**Key Decisions:**
- **uvx distribution**: No `pip install`, no `git clone` requirement
- **PyPI packaging**: Standard Python packaging with entry point `acf`  
- **Template bundling**: Build-time inclusion from `/templates` using hatchling
- **Offline capability**: Self-contained package works without internet

### Template Packaging Strategy

**Build Configuration:**
```toml
[tool.hatch.build.targets.wheel.force-include]
"../templates" = "ai_code_forge/templates"
```

**Runtime Access:**
```python
from importlib import resources
templates = resources.files("ai_code_forge.templates")
```

**Benefits:**
- Zero repository duplication
- Standard Python packaging practices
- Maintains template organization structure
- Compatible with existing importlib.resources patterns

### State Management

**Repository Structure After CLI Operations:**
```
target-repo/
├── .claude/          # Claude Code configuration
│   ├── agents/
│   ├── commands/
│   └── settings.json
├── .acf/            # ACF state directory
│   ├── template-version.json
│   ├── customizations.json
│   └── status.json
├── CLAUDE.md        # Primary agent instructions
└── ACF.md           # Optional customization documentation
```

**State Files:**
- `template-version.json`: Tracks which template version was used
- `customizations.json`: Records user modifications to templates  
- `status.json`: Current configuration status and drift detection

## Command Architecture

### Command Implementation Pattern
```python
import click

@click.group()
def cli():
    """AI Code Forge CLI for agent configuration management."""
    pass

@cli.command()
def init():
    """Bootstrap repository with agent configuration."""
    pass

@cli.command() 
def update():
    """Sync with latest templates while preserving customizations."""
    pass
```

### Core Commands

#### `uvx acf init`
**Purpose**: Bootstrap new repository with agent configuration
**Behavior**:
- Creates `.claude/` directory structure
- Installs `CLAUDE.md` from templates
- Creates initial `.acf/` state
- Provides interactive template selection

**Template Sources**:
- `/templates/guidelines/CLAUDE.md` → `CLAUDE.md`
- `/templates/stacks/*.md` → `.claude/stacks/`
- Agent and command templates based on user selection

#### `uvx acf update`
**Purpose**: Sync with latest bundled templates while preserving customizations
**Behavior**:
- Compares current config with bundled templates
- Preserves `.local` files (e.g., `.claude/agents/custom.local.md`)
- Updates base templates only
- Records changes in `.acf/status.json`

**Customization Preservation**:
- `.local` file pattern for user customizations
- Three-way merge for complex cases
- User confirmation for breaking changes

#### `uvx acf migrate`
**Purpose**: Convert existing agent configurations to ACF standard
**Behavior**:
- Analyzes existing `.claude/` directory
- Maps to ACF template structure
- Creates `.acf/` state directory
- Preserves existing customizations as `.local` files

#### `uvx acf status`
**Purpose**: Show configuration state and template drift
**Output**:
```
ACF Status for repository: my-project
Template Version: v1.2.3
Last Update: 2024-08-28

Configuration Status:
  ✓ CLAUDE.md (up to date)
  ⚠ .claude/agents/researcher.md (modified, use 'acf update' to sync)
  ✗ .claude/commands/deploy.md (missing, run 'acf update')

Customizations:
  • .claude/agents/custom-agent.local.md
  • .claude/commands/my-command.local.md

Use 'acf explain' for configuration documentation.
```

#### `uvx acf factory-reset`
**Purpose**: Nuclear option - full reset to template defaults
**Behavior**:
- Backs up current configuration to `.acf/backup/`
- Removes all `.claude/` content
- Reinstalls fresh templates
- Resets `.acf/` state

#### `uvx acf explain`
**Purpose**: Documentation and help for configuration elements
**Interactive Interface**:
```bash
$ uvx acf explain
What would you like to know about?
1. CLAUDE.md structure and purpose
2. Agent definitions (.claude/agents/)
3. Command structure (.claude/commands/)
4. Template customization patterns
5. ACF state management
```

#### `uvx acf troubleshoot`
**Purpose**: Diagnostic and validation tool
**Checks**:
- Configuration file syntax validation
- Template compatibility verification
- State consistency checks
- Agent/command reference validation

#### `uvx acf customize`
**Purpose**: Interactive template modification
**Workflow**:
1. Select configuration element to customize
2. Create `.local` version with guided editing
3. Document customization in `ACF.md`
4. Update `.acf/customizations.json`

## Template Organization

### Source Structure (`/templates`)
```
templates/
├── guidelines/
│   ├── CLAUDE.md              # Primary agent instructions
│   ├── claude-agents-guidelines.md
│   └── claude-commands-guidelines.md  
├── prompts/
│   ├── master-prompt.md
│   └── specialized-prompts/
├── stacks/
│   ├── python.md
│   ├── rust.md
│   └── javascript.md
└── readme/
    ├── general-project-template.md
    └── library-package-template.md
```

### Bundled Structure (in package)
```
ai_code_forge/
├── templates/          # Copied from /templates at build time
│   ├── guidelines/
│   ├── prompts/
│   ├── stacks/
│   └── readme/
└── commands/
    ├── init.py
    ├── update.py
    └── ...
```

## Customization Strategy

### `.local` File Pattern
```
.claude/
├── agents/
│   ├── researcher.md      # From template
│   ├── researcher.local.md # User customization
│   └── custom-agent.local.md # Purely user-created
└── commands/
    ├── deploy.md          # From template  
    └── deploy.local.md    # User customization
```

### ACF.md Documentation
```markdown
# Agent Configuration Customizations

## Custom Agents
- `researcher.local.md`: Added domain-specific research capabilities
- `custom-agent.local.md`: Project-specific automation agent

## Modified Commands  
- `deploy.local.md`: Added Docker deployment workflow

## Template Overrides
- CLAUDE.md: Added project-specific operational rules
```

## Evolution Path

### Phase 1: Bundled Templates (Current Specification)
- Templates bundled at build time
- Offline operation
- Standard PyPI distribution

### Phase 2: Hybrid Approach (Future)
```bash
uvx acf update --source=github    # Latest from GitHub
uvx acf update --source=bundled   # Use package templates
```

### Phase 3: Full Discovery (Future)
- Template signature verification
- Multiple template sources
- Template marketplace integration

## Testing Strategy

### Development Testing
- **Primary test case**: Use this repository (ai-code-forge) as guinea pig
- **Migration testing**: Convert existing `.claude/` configuration using CLI
- **Trial and error**: Git provides safety net for experimentation

### Integration Testing  
```python
# Using testcontainers for isolated testing
def test_init_command():
    with temporary_git_repo() as repo:
        result = run_acf(['init'], cwd=repo.path)
        assert repo.path / '.claude' / 'agents' exists
        assert repo.path / 'CLAUDE.md' exists
```

### Validation Testing
- Test against sample repositories
- Validate template bundling process
- Cross-platform uvx compatibility

## Implementation Plan

### Foundation
1. **Delete current CLI**: Remove `cli/` directory entirely
2. **Create clean pyproject.toml**: Hatchling build system with force-include
3. **Basic command structure**: Click-based CLI with subcommands
4. **Template access**: importlib.resources integration

### Core Implementation Order
1. `acf status` - Foundation for state management
2. `acf init` - Primary user entry point
3. `acf update` - Template synchronization
4. `acf migrate` - Existing configuration conversion
5. `acf factory-reset` - Nuclear option
6. `acf explain` - Documentation system
7. `acf troubleshoot` - Diagnostic capabilities
8. `acf customize` - Interactive modification

### Quality Gates
- All commands work on ai-code-forge repository itself
- Package builds and installs via uvx
- Templates bundle correctly without duplication
- State management maintains consistency

## Technical Dependencies

### Core Dependencies
```toml
[project]
dependencies = [
    "click>=8.0.0",      # CLI framework
    "rich>=10.0.0",      # Terminal formatting
    "pydantic>=2.0.0",   # Configuration validation
]
```

### Build Dependencies  
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Optional Dependencies
```toml
[project.optional-dependencies]
test = ["pytest", "testcontainers"]
dev = ["black", "ruff", "mypy"]
```

## Security Considerations

### Template Trust
- Bundled templates are trusted (part of package)
- Future GitHub source requires signature verification
- No arbitrary code execution from templates

### State File Safety
- `.acf/` files contain only configuration metadata
- No executable content in state files
- Validation of all JSON state files

### File System Operations
- All operations within target repository boundary
- No global file system modifications
- Backup strategy for destructive operations

## Cross-References

- **GitHub Issue**: [#205 - CLI Architecture Rewrite](https://github.com/ondrasek/ai-code-forge/issues/205)
- **Template Source**: `/templates` directory in ai-code-forge repository
- **Implementation**: `cli/` directory (to be rewritten)
- **Testing**: Use ai-code-forge repository as primary test case

---

*This document serves as the comprehensive technical specification for the AI Code Forge CLI. It should be updated as implementation proceeds and architectural decisions evolve.*