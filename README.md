# AI Code Forge

**v4.0** - A composable template system for AI-first development workflows

## Overview

AI Code Forge is a template-driven framework for building and distributing development environments optimized for AI-assisted coding with [Claude Code](https://claude.com/claude-code). It combines Claude configurations, DevContainer definitions, and automation workflows into composable, maintainable templates that can be mixed and matched to fit your project needs.

## Purpose

AI Code Forge serves multiple roles in the AI-assisted development ecosystem:

- **Claude Code Configuration Framework**: Distribute and manage Claude agents, commands, and settings
- **DevContainer Template System**: Create parameterized development environments with AI tooling pre-configured
- **Development Toolkit**: Provide automation workflows and best practices for AI-first development
- **Template Distribution Platform**: Share and apply reusable configurations via git subtrees

All of these capabilities work together through a **composition model** - you can mix and match components based on your project's specific requirements.

## Architecture

AI Code Forge v4.0 follows a **template-first design with configuration as code**:

```
Templates (git subtrees)
├── Claude Configurations
│   ├── Agents (foundation & specialists)
│   ├── Commands (slash commands)
│   └── Settings
├── DevContainer Definitions
│   ├── Dockerfile & configuration
│   ├── Post-create scripts
│   └── Environment setup
└── Workflows & Automation
    ├── GitHub Actions
    ├── CI/CD pipelines
    └── Helper scripts
```

### Core Design Principles

1. **Composability**: Components work together but remain independent - use what you need
2. **Maintainability**: Templates are easy to update, version, and distribute changes to downstream projects

### Why v4.0?

Version 3.x became difficult to maintain due to complexity and tight coupling. v4.0 is a complete architectural reset focused on:
- Clean separation of concerns
- Git-native composition via subtrees
- Minimal, maintainable core
- Easy evolution and updates

## What Makes It Unique

- **AI-First Development**: Purpose-built for Claude Code workflows and AI agent orchestration
- **Git-Based Composition**: Elegant template distribution and updates using git subtrees
- **Opinionated Best Practices**: Proven patterns for AI-assisted development and agent collaboration
- **Zero-Dependency Portability**: Templates are pure configuration files with no runtime dependencies

## Usage

AI Code Forge can be used in two ways:

### 1. CLI Tool
```bash
# Apply a template to your project
acforge apply <template-name>

# Create a new template
acforge template create

# Update templates in your project
acforge update
```

### 2. Direct Git Integration
```bash
# Clone this repository as a starting point
git clone https://github.com/ondrasek/ai-code-forge.git

# Or add templates as git subtrees
git subtree add --prefix=.claude-templates \
  https://github.com/ondrasek/ai-code-forge.git main --squash
```

### Template Marketplace

Browse and discover templates in the marketplace. Templates are applied to your project using git subtrees, giving you:
- Full version history
- Easy updates via `git subtree pull`
- Ability to customize while maintaining upstream connection

## Target Audience

- **Individual Developers**: Set up AI-enhanced development workflows quickly
- **Development Teams**: Standardize AI tooling and development environments across the team

## Project Status

**v4.0 is currently in active development.** The repository has been reset to establish a clean foundation for the new architecture. Legacy v3.x code is preserved under the `v3.2.0-final` tag.

## License

See [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please see our contribution guidelines (coming soon).
