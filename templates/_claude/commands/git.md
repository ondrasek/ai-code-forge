---
description: Fully automated Git Workflow Protocol implementation with intelligent commit messages and release tagging.
argument-hint: Optional custom commit message to be appended to automatically determined commit message.
allowed-tools: Task(git-workflow), Bash(git status), Bash(git diff), Bash(git log)
---

# Git Workflow Command

!`git status`
!`git branch --show-current`

Executes complete git workflow automation including staging, committing, and release evaluation through the git-workflow specialist agent.

## Instructions

1. **Parse Arguments**: Check if $ARGUMENTS contains custom commit message
   - If custom message provided, pass it to git-workflow agent for integration
   - If no custom message, proceed with automatic commit message generation

2. **Delegate to Specialist Agent**: 
   ```
   Task(git-workflow): Execute complete Git Workflow Protocol with the following parameters:
   - Intelligent staging analysis (not blanket git add)
   - Conventional commit message crafting
   - CHANGELOG.md and README.md validation and updates
   - Automatic release tagging assessment based on 5-criteria evaluation
   - Custom commit message: $ARGUMENTS (if provided)
   ```

3. **Agent Coordination**: The git-workflow agent will handle all complex processing in its context, returning only clean decisions and action items to main context.

## Expected Outcomes

- Intelligent file staging based on content analysis
- Properly formatted conventional commit messages
- Selective documentation updates when warranted
- Automatic release tagging when criteria are met
- Clean main context with minimal processing artifacts