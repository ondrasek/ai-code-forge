---
description: Create GitHub pull request using github-pr-workflow agent.
argument-hint: Optional PR title, "draft" flag, or base branch.
allowed-tools: Task
---

# Pull Request Creator

!`git status`
!`git diff HEAD`
!`git branch --show-current`

## Instructions

1. **Validation**
   - Verify github-pr-workflow agent is available before delegation
   - If agent unavailable, display error: "github-pr-workflow agent not found" and exit

2. **Parameter Processing**
   - Parse $ARGUMENTS for: custom PR title, "draft" flag, or base branch specification
   - Validate arguments format and provide error guidance for invalid parameters

3. **Agent Delegation**
   - Task(github-pr-workflow) with parsed $ARGUMENTS
   - If delegation fails, provide manual PR guidance: "Visit GitHub repository, create PR manually using current branch"

## Error Recovery

- **Agent failure**: Provide repository URL and manual PR creation steps
- **Invalid arguments**: Display expected format examples
- **Git state issues**: Instruct user to check branch status and authentication