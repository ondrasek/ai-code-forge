# AI Code Forge Documentation

Welcome to AI Code Forge v4.0+ documentation. This version introduces a revolutionary modular architecture that replaces the atomic template approach.

## Getting Started

- [**Modular Architecture**](modular-architecture.md) - Complete overview of the new modular system
- [**Claude Code Components**](claude-code-components.md) - Skills, Sub-Agents, and Slash Commands explained

## Module Development

- [Creating Modules](modules/creating-modules.md) - Guide to developing custom modules
- [Creating Skills](modules/creating-skills.md) - Guide to developing Claude Skills

## Architecture Overview

AI Code Forge v4.0+ is built around Claude Code components:

- **Modules**: Filesystem components and configuration
- **Skills**: AI enhancement capabilities (optional)
- **Sub-Agents**: Specialized task execution with isolation
- **Slash Commands**: Workflow automation and orchestration
- **Git Integration**: Rollback and state management
- **CLI**: Enhanced command interface

## Key Changes from v3.x

- ❌ **Removed**: Atomic template deployment
- ❌ **Removed**: OpenAI Codex and OpenCode CLI support
- ❌ **Removed**: MCP servers and analysis directories
- ✅ **Added**: Modular architecture with independent versioning
- ✅ **Added**: Git-based rollback and state management
- ✅ **Added**: Claude Skills integration
- ✅ **Added**: M:N module-skills relationships

## Migration Notice

**No backward compatibility** is provided from v3.x to v4.0+. This represents a complete architectural change requiring fresh setup.

## Quick Start

```bash
# Install core Claude Code configuration
acforge module install claude-config

# Add Python development environment
acforge module install python

# Add Git worktree management
acforge module install worktree

# List available modules
acforge module list --available
```

## Support

For questions about the modular architecture or module development:

1. Review the [Modular Architecture](modular-architecture.md) documentation
2. Check the module development guides
3. Examine existing modules in the repository
4. Open issues for specific technical questions