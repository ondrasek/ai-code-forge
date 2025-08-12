# Worktree Delivery Utility

The `worktree-deliver.sh` script provides an end-to-end workflow for issue-based development using git worktrees and Claude Code.

## Overview

This utility combines worktree management with AI-assisted development to create an integrated workflow:

1. **Worktree Setup**: Creates or locates a git worktree for the specified issue/branch
2. **Issue Context**: Fetches GitHub issue details for contextual understanding  
3. **AI Integration**: Launches Claude Code with a custom prompt tailored for issue refinement and implementation
4. **Interactive Workflow**: Keeps Claude Code in interactive mode for user-guided development

## Usage

```bash
./worktree-deliver.sh <issue-number|branch-name> [--dry-run]
```

### Arguments

- `issue-number`: GitHub issue number (e.g., `123`, `#123`)
- `branch-name`: Full branch name (e.g., `feature/add-launch`, `issue-129-fix`)
- `--dry-run`: Show what would be executed without running commands

### Examples

```bash
# Create worktree for issue #123 and launch with issue context
./worktree-deliver.sh 123

# Work with existing branch worktree
./worktree-deliver.sh feature/add-launch

# Preview what would happen without execution
./worktree-deliver.sh 129 --dry-run
```

## Workflow Phases

### Phase 1: Issue Analysis & Refinement
- Analyzes the issue/requirements thoroughly
- Prompts for clarifying questions if anything is unclear
- Suggests improvements or refinements to requirements
- Confirms scope and acceptance criteria

### Phase 2: Implementation Planning  
- Creates detailed implementation plan
- Identifies files that need changes
- Considers testing strategy
- Plans documentation updates

### Phase 3: Interactive Implementation
- Implements the solution step by step
- Writes tests as needed (TDD approach when appropriate)
- Updates documentation
- Prepares for code review

## Prerequisites

- **Git worktree infrastructure**: Uses existing `worktree-create.sh`
- **Claude Code**: Either `claude` command or `launch-claude.sh` script
- **GitHub CLI** (optional): For fetching issue details and enhanced context
- **GitHub Authentication**: If using GitHub CLI features

## Integration with Existing Scripts

This script builds on the existing worktree infrastructure:

- `worktree-create.sh`: Used for worktree creation/location
- `worktree-launch.sh`: Similar pattern for launching Claude Code
- `launch-claude.sh`: Fallback if `claude` command not available

## Issue Context Features

When working with GitHub issues, the script:

- Fetches issue title, description, state, and labels
- Creates contextual prompts with issue details
- Provides structured workflow guidance
- Maintains focus on issue requirements

## Interactive Mode

The script launches Claude Code in interactive mode, meaning:

- Claude waits for user input between phases
- User controls the pace and direction of development
- Allows for iterative refinement and feedback
- Maintains human oversight throughout the process

## File Structure

The script creates:
- Dedicated worktree directory (via `worktree-create.sh`)
- Temporary prompt file: `.claude-delivery-prompt.md` in worktree
- Isolated development environment for the issue

## Error Handling

The script includes comprehensive error handling:

- Validates repository access and GitHub connectivity
- Gracefully handles missing GitHub CLI or authentication
- Provides fallback behavior for missing dependencies
- Clear error messages with suggested resolutions

## Security Considerations

- **Input Validation**: Identifiers are validated to prevent path traversal attacks
- **Secure File Creation**: Temporary files created with restrictive permissions (077)
- **Path Sanitization**: User input sanitized before use in file system operations
- **Length Limits**: Identifiers limited to 100 characters to prevent buffer issues
- **Worktree Isolation**: All operations contained within dedicated worktree scope
- **No Sensitive Data**: Prompts contain only issue context, no credentials or secrets
- **Permission Respect**: Maintains existing repository access controls

## Examples of Generated Prompts

For issue-based workflows, Claude Code receives prompts like:

```markdown
# Issue Delivery Workflow

## GitHub Issue Context
**Issue**: 123
**Title**: Implement launch-codex.sh script
**State**: open
**Labels**: feat, enhancement

**Description**:
Create a launch script for OpenAI Codex CLI integration...

## Workflow Instructions
**Phase 1: Issue Analysis & Refinement**
1. Analyze the issue/requirements thoroughly
2. Ask clarifying questions if anything is unclear
...
```

This provides Claude Code with full context and structured guidance for productive development sessions.