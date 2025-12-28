# AI Code Forge

**v4.0** - CLI tool for managing AI-assisted development workflows with Claude Code

## Overview

AI Code Forge (`acforge`) is a command-line tool that provides complete infrastructure for AI-assisted software development using [Claude Code](https://claude.com/claude-code). It manages module repositories via git subtrees, automates GitHub workflows, and orchestrates DevContainer-based development environments.

**Key Concept**: This repository contains the **CLI tool**, not the modules themselves. Modules are separate git repositories that `acforge` manages and integrates into your projects using git subtrees under `.acforge/modules/`.

## What It Does

`acforge` is a git subtree management system with developer workflow automation:

1. **Git Subtree Management**: Add, update, and manage module repositories in your projects via git subtrees
2. **GitHub Workflow Automation**: Create issues, PRs, and manage development workflows via GitHub CLI
3. **DevContainer Operations**: Build, configure, and manage isolated development environments
4. **Module Discovery**: Browse and install modules from registry and custom sources
5. **Basic Coding Workflows**: Maintain README.md, CHANGELOG.md, .gitignore, and other project documentation

## Architecture

### CLI-Centric Design

AI Code Forge is built on three foundational CLIs:

- **acforge** (this tool) - Orchestrates all operations
- **Claude Code CLI** - AI-assisted development
- **Git CLI** - Version control and subtree management
- **GitHub CLI** - Issue tracking, PRs, Actions

### Module Repository Model

Modules are **separate git repositories** merged into `.acforge/modules/` as git subtrees. A typical module contains:

**Module Structure**:
- `.claude/` - Claude Code configuration
  - `agents/` - AI agent definitions
  - `commands/` - Slash commands
  - `settings.json` - Claude Code settings
- `.devcontainer/` - DevContainer configuration
  - `devcontainer.json` - Container specification
  - `Dockerfile` - Container image definition
  - `postCreate.sh` - Post-creation scripts
- `templates/` - Template files (e.g., README.md templates)
- `.gitignore` - Ignore patterns to be merged into project
- `module.yaml` - Module metadata and merge strategy definition

Modules are integrated into your project via:
```bash
uvx acforge module add <module-name>
```

This uses `git subtree add` to merge module content into `.acforge/modules/<module-name>`, then intelligently merges files to their target locations based on the module's merge strategy.

### DevContainer Philosophy

Complete isolation from the host machine:

- **No write access** to the development machine
- **No access** to host user home directory
- Working copies in **Docker volumes** mounted into containers
- All development happens inside the container
- Host filesystem remains untouched

### Development Governance

- **GitHub Issues** govern all development work
- Issue-driven workflow with automated tracking
- CI/CD via GitHub Actions
- Integration with Claude Code for AI-assisted issue resolution

## Core Design Principles

1. **Composability**: Mix and match templates based on project needs
2. **Maintainability**: Easy to update templates across multiple projects via git subtree
3. **Isolation**: Complete DevContainer isolation from host system
4. **GitHub-Native**: Issues, PRs, and Actions as primary workflow tools

## Why v4.0?

Version 3.x became difficult to maintain due to monolithic complexity and tight coupling. v4.0 is a complete architectural reset:

- **Separation**: CLI tool separate from template content
- **Git-native**: Leverage git subtree for template management
- **Minimal core**: Focus on orchestration, not implementation
- **Maintainable**: Simple, focused codebase

## Installation

```bash
# Install acforge CLI
pip install acforge

# Or install from source
git clone https://github.com/ondrasek/ai-code-forge.git
cd ai-code-forge
pip install -e .
```

## How It Works

### Module-Based Architecture

Everything in `acforge` is centered around **modules** - separate git repositories that are merged into your project using git subtrees. Modules provide:

- Claude Code configurations (.claude/agents, .claude/commands)
- DevContainer setups (.devcontainer/)
- Tech stack configurations (.gitignore, pyproject.toml, etc.)
- Workflow automations (.github/workflows/)

**Key Concept**: Modules are stored in `.acforge/modules/` as git subtrees and tracked in `.acforge.yaml`. The entire `.acforge/` directory is committed to git.

### Module Lifecycle

**Ephemeral Modules** (temporary agents):
- Install → Run Claude Code with module's .claude config → Remove
- Examples: `start-from-scratch`, `tech-stack`, `security-review`
- Module stays in `.acforge/modules/<name>/` during workflow
- Claude Code loads config from module's location (not merged into project .claude/)
- Module directory removed when workflow completes
- Generated artifacts (README.md, etc.) remain in project

**Long-Lived Modules** (permanent infrastructure):
- Install → Merge files → Keep → Update over time
- Examples: `python-stack`, `typescript-stack`, `devcontainer-base`
- Files are merged into project locations (.claude/, .devcontainer/, .gitignore, etc.)
- Module remains in `.acforge/modules/<name>/` for tracking and updates

### Smart Merging

Modules merge files intelligently based on content type:

- **UNION merging**: `.gitignore`, `.dockerignore` - all entries from all modules
- **Template merging**: `pyproject.toml`, configuration files - structured merge
- **Append merging**: `.claude/agents/`, separate files don't conflict
- **User resolution**: Conflicts prompt for manual resolution

## Usage

### Starting a New Project

```bash
# 1. Initialize acforge in your repository
uvx acforge init

# 2. Bootstrap with README creation workflow
uvx acforge workflow start-from-scratch
# → Installs start-from-scratch module to .acforge/modules/
# → Launches Claude Code with module's .claude config
# → User works with Claude to create README.md
# → Module auto-removed after workflow completes
# → Generated README.md remains in project

# 3. Discuss and select tech stack
uvx acforge workflow tech-stack
# → Installs tech-stack module to .acforge/modules/
# → Launches Claude Code with module's /tech-stack command
# → Discusses options and recommends modules
# → Module auto-removed after workflow completes

# 4. Install long-lived stack modules
uvx acforge module add python-stack
# → Merges .claude/agents/python-*.md
# → Merges .devcontainer/ Python environment
# → Merges Python patterns to .gitignore
# → Adds pyproject.toml template
# → Module stays installed for project lifetime
```

### Module Management

```bash
# List available modules (from registry and custom sources)
uvx acforge module list

# Add a module (long-lived)
uvx acforge module add <module-name>
uvx acforge module add https://github.com/custom/module-repo

# Update module to latest version
uvx acforge module update <module-name>

# Remove module (unmerge files)
uvx acforge module remove <module-name>

# Show installed modules
uvx acforge module status
```

### Workflow Commands

```bash
# Run ephemeral workflows
uvx acforge workflow start-from-scratch
uvx acforge workflow tech-stack
uvx acforge workflow security-review

# Each workflow:
# 1. Installs required module(s)
# 2. Runs Claude Code with specific command
# 3. Optionally removes module after completion
```

### GitHub Operations

```bash
# Create an issue
uvx acforge issue create

# Start work on an issue
uvx acforge issue start <issue-number>

# Create PR from current work
uvx acforge pr create
```

### DevContainer Operations

```bash
# Build devcontainer
uvx acforge devcontainer build

# Rebuild with clean state
uvx acforge devcontainer rebuild
```

### Documentation Maintenance

```bash
# Update README based on codebase changes
uvx acforge docs readme

# Update CHANGELOG for release
uvx acforge docs changelog

# Maintain .gitignore
uvx acforge docs gitignore
```

## Target Audience

- **Individual Developers**: Complete AI-assisted development setup with one tool
- **Development Teams**: Standardized workflows, templates, and environments

## About This Repository

### Self-Hosting Development

The `.claude/` and `.devcontainer/` directories in **this repository** are for developing `acforge` itself. They provide:

- Claude Code configuration for AI-assisted development of the CLI tool
- DevContainer setup for isolated development of this project
- Reference implementation of best practices

**Note**: These are NOT the templates you install in your projects. They are the development environment for building and maintaining the `acforge` CLI tool.

### Repository Structure

**This Repository** (ai-code-forge):
- `.claude/` - Claude Code config for developing acforge
- `.devcontainer/` - DevContainer for developing acforge
- `.github/workflows/` - CI/CD workflows (disabled for v4.0 dev)
- `cli/` - acforge CLI implementation (coming soon)
- `CHANGELOG.md` - Version history
- `CLAUDE.md` - AI operational rules
- `LICENSE` - Project license
- `README.md` - This file

**Project Using acforge**:
- `.acforge/` - acforge module management directory
  - `modules/` - Git subtrees containing installed modules
    - `python-stack/` - Long-lived module (git subtree)
    - `devcontainer-base/` - Long-lived module (git subtree)
  - `acforge.yaml` - Module tracking metadata
- `.claude/` - Claude Code configuration (merged from modules)
  - `agents/` - AI agent definitions
    - `python-linting.md` - From python-stack module
    - `python-testing.md` - From python-stack module
  - `commands/` - Slash commands
  - `settings.json` - Claude Code settings
- `.devcontainer/` - DevContainer configuration (from devcontainer-base module)
  - `devcontainer.json` - From devcontainer-base module
  - `Dockerfile` - From devcontainer-base module
  - `postCreate.sh` - From devcontainer-base module
- `.github/workflows/` - CI/CD workflows (from modules or user-created)
- `.gitignore` - Union of all module .gitignore files
- `pyproject.toml` - From python-stack module
- `README.md` - Created with start-from-scratch workflow
- `src/` - Your code

## Project Status

**v4.0 is currently in active development.** The repository has been reset to establish a clean foundation for the new architecture. Legacy v3.x code is preserved under the `v3.2.0-final` tag.

### Development Governance

All development work is tracked and governed through [GitHub Issues](https://github.com/ondrasek/ai-code-forge/issues). The workflow is:

1. Create issue for feature/bug/enhancement
2. Implement solution in isolated branch or worktree
3. Create PR linking to issue
4. Review and merge via GitHub Actions CI/CD
5. Automated release tagging based on semantic versioning

## What Makes It Unique

- **Git-Native Template Management**: First-class git subtree support for template composition and updates
- **Complete Isolation**: DevContainer philosophy with zero host filesystem access
- **AI-First Workflows**: Deep integration with Claude Code for issue resolution and development
- **GitHub-Centric**: Issues govern development, Actions automate CI/CD
- **CLI Orchestration**: Single tool coordinating Claude Code CLI, Git CLI, and GitHub CLI

## License

See [LICENSE](LICENSE) for details.

## Contributing

All contributions must go through the GitHub Issues workflow:

1. Create an issue describing the feature, bug, or enhancement
2. Discuss and refine the approach in issue comments
3. Implement in a branch/worktree with issue reference
4. Submit PR linking to the issue
5. CI/CD validates and merges

See [CLAUDE.md](CLAUDE.md) for AI operational rules governing development.
