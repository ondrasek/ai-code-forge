# AI Code Forge

**v4.0** - CLI tool for managing AI-assisted development workflows with Claude Code

## Overview

AI Code Forge (`acforge`) is a command-line tool that provides complete infrastructure for AI-assisted software development using [Claude Code](https://claude.com/claude-code). It manages template repositories via git subtrees, automates GitHub workflows, and orchestrates DevContainer-based development environments.

**Key Concept**: This repository contains the **CLI tool**, not the templates themselves. Templates are separate git repositories that `acforge` manages and integrates into your projects using git subtrees.

## What It Does

`acforge` is a git subtree management system with developer workflow automation:

1. **Git Subtree Management**: Add, update, and manage template repositories in your projects
2. **GitHub Workflow Automation**: Create issues, PRs, and manage development workflows via GitHub CLI
3. **DevContainer Operations**: Build, configure, and manage isolated development environments
4. **Template Discovery**: Browse and install templates from the marketplace

## Architecture

### CLI-Centric Design

AI Code Forge is built on three foundational CLIs:

```
acforge (this tool)
├── Claude Code CLI ──→ AI-assisted development
├── Git CLI ──────────→ Version control & subtree management
└── GitHub CLI ───────→ Issue tracking, PRs, Actions
```

### Template Repository Model

Templates are **separate git repositories** containing:

```
template-repository/
├── .claude/
│   ├── agents/           # AI agent definitions
│   ├── commands/         # Slash commands
│   └── settings.json     # Claude Code configuration
├── .devcontainer/
│   ├── devcontainer.json
│   ├── Dockerfile
│   └── postCreate.sh
└── .github/workflows/    # CI/CD automation
```

Templates are integrated into your project via:
```bash
acforge template add <template-repo-url>
```

This uses `git subtree` to merge template content while maintaining upstream connection for updates.

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

## Usage

### Template Management

```bash
# Discover available templates
acforge template list

# Add a template to your project
acforge template add https://github.com/username/template-repo

# Update templates to latest version
acforge template update

# Remove a template
acforge template remove <template-name>
```

### GitHub Workflow

```bash
# Create an issue
acforge issue create

# Start work on an issue
acforge issue start <issue-number>

# Create PR from current work
acforge pr create
```

### DevContainer Operations

```bash
# Build devcontainer
acforge devcontainer build

# Rebuild with clean state
acforge devcontainer rebuild
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

```
ai-code-forge/
├── .claude/              # Claude Code config for developing acforge
├── .devcontainer/        # DevContainer for developing acforge
├── cli/                  # acforge CLI implementation (coming soon)
├── CHANGELOG.md          # Version history
├── CLAUDE.md             # AI operational rules
└── README.md             # This file
```

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
