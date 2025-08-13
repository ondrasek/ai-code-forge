---
description: Clean up completed and obsolete GitHub Issues.
allowed-tools: Task, Bash
---

# GitHub Issue Cleanup

Identify and clean up completed or obsolete GitHub Issues.

## Instructions

1. Use Task tool to delegate to github-issues-workflow agent:
   - Analyze codebase and CHANGELOG to identify completed issues
   - Identify stale/obsolete issues no longer relevant
   - Cross-reference with actual GitHub issue status
   - Consider $ARGUMENTS for cleanup scope if provided
   - Present findings for user confirmation before closing

2. After user confirmation, close identified issues with appropriate comments
3. Return cleanup summary with counts and actions taken