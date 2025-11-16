# Worktree Module

Git worktree management and workflow automation for AI Code Forge.

## Purpose

This module provides comprehensive git worktree management capabilities including:
- Worktree creation and cleanup
- Branch-based workflow automation
- Integration with development environments
- Worktree inspection and monitoring

## What's Included

- **Core Scripts**: Complete worktree management toolkit
- **Workflow Automation**: Create, deliver, and manage worktrees
- **Development Integration**: Launch and inspect worktree environments
- **Cleanup Tools**: Automated worktree maintenance

## Installation

```bash
acforge module install worktree
```

## Usage

After installation, worktree management scripts are available in `scripts/`:

```bash
# Create a new worktree
./scripts/worktree-create.sh feature/new-feature

# List all worktrees
./scripts/worktree-list.sh

# Cleanup unused worktrees
./scripts/worktree-cleanup.sh

# Deliver changes from worktree
./scripts/worktree-deliver.sh
```

## Dependencies

None. This module works with standard git installations.

## Compatibility

- Git: Requires git worktree support
- Claude Code: >=2.78.0
- AI Code Forge: >=4.0.0