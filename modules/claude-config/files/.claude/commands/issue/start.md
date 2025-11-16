---
description: Systematic implementation execution for planned GitHub Issue with git workflow.
argument-hint: <issue-number>
allowed-tools: Task
---

# GitHub Issue Implementation Phase

!`git status`
!`git branch --show-current`

Systematic execution phase for GitHub Issue implementation with proper git workflow and progress tracking.

## Instructions

1. **Validate Issue Number and Phase 1 Completion**:
   - Ensure issue number is provided as argument
   - Validate approved plan exists from /issue plan phase
   - Verify issue is assigned to current user

2. **Use Task tool to delegate to github-issues-workflow agent**:
   - **Plan Validation**: Load and validate approved plan from Phase 1
   - **Current Branch Workflow**: Work directly on current branch
   - **Progressive Implementation**: Execute plan step-by-step with progress tracking
   - **Agent Coordination**: Use specialized agents (code-cleaner, stack-advisor, test-strategist)
   - **Commit Strategy**: Create meaningful commits throughout implementation
   - **Testing Integration**: Run tests at implementation milestones
   - **Error Recovery**: Provide rollback capabilities and recovery options
   - **Implementation Summary**: Present comprehensive work completion summary
   - **Metadata Storage**: Store implementation details for Phase 3

3. **Critical Constraints**:
   - Must validate Phase 1 (/issue plan) completion before proceeding
   - Work directly on current branch
   - Integration testing at key milestones
   - NO PR creation during this phase (reserved for Phase 3)

4. **Success Criteria**:
   - Implementation completed on current branch
   - All tests passing
   - Implementation summary provided
   - Metadata stored for /issue pr consumption
   - Ready for Phase 3 PR creation

## Example Usage

```
/issue start 41
```

This initiates Phase 2 of the three-phase GitHub Issue workflow system.