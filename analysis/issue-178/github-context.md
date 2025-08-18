# GitHub Issue #178 Context

## Issue Details
- **Title**: fix: worktree watch regression - missing PR association and incomplete process display
- **State**: OPEN
- **Priority**: HIGH (priority:high label)
- **Type**: Bug/Fix (bug, fix labels)
- **Branch**: issue-178-fix-worktree-watch (current working branch)

## Problem Description
The `worktree watch` command has regressed from its original behavior. Two specific issues identified:

1. **Missing PR Association Display**: Fails to display pull requests associated with issues/branches
2. **Incomplete Process Display**: Only shows Claude Code processes instead of all processes working in a branch

## Acceptance Criteria
- [ ] Restore PR association display for issues/branches in worktree watch output
- [ ] Display all processes working in a branch, not just Claude Code processes  
- [ ] Maintain compatibility with existing worktree watch functionality
- [ ] Verify behavior matches original implementation specifications

## Technical Context
- **Component**: worktree watch command
- **Issue Type**: Regression (lost functionality)
- **Impact**: Reduced visibility into branch activity and PR associations
- **Repository**: ai-code-forge (Shell/Python codebase)

## Priority Analysis History
- Initially assessed as medium priority
- **Corrected to HIGH priority** due to:
  - Confirmed regression affecting developer productivity tool
  - Lost functionality breaks existing user expectations
  - No workaround indicated for restoring functionality
  - Developer workflow impact (monitoring commands are critical)

## Related Issues
- Issue #177: worktree functionality bugs (different - missing functionality vs lost functionality)
- Issue #179: Critic agent integration into worktree deliver prompt
- Issue #195: Research comprehensive Claude Code logging system

## Branch Status
- Working on dedicated branch: `issue-178-fix-worktree-watch`
- Clean working directory
- Ready for implementation