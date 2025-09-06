---
description: Deep analysis and implementation planning for specific GitHub Issue.
argument-hint: <issue-number>
allowed-tools: Task
---

# GitHub Issue Planning Phase

Comprehensive planning phase for GitHub Issue implementation with deep analysis and user approval gates.

## Instructions

1. **Validate Issue Number**:
   - Ensure issue number is provided as argument
   - Validate issue exists and is accessible

2. **Use Task tool to delegate to github-issues-workflow agent**:
   - **GitHub Integration**: Assign issue to current user via GitHub CLI
   - **Codebase Analysis**: Perform deep analysis of relevant code sections
   - **Research Phase**: Extensive research on solutions, patterns, and best practices
   - **Implementation Planning**: Generate detailed, step-by-step implementation plan
   - **Quality Review**: Invoke critic agent to review plan completeness and feasibility
   - **User Approval Gate**: Present complete findings and require explicit approval before any modifications
   - **Plan Persistence**: Store approved plan for /issue start consumption
   - **Update Github Issue**: Update github issue with the created plan description, add/remove appropriate labels from the issue

3. **Critical Constraints**:
   - All work occurs on current branch (no branching during planning)
   - NO code modifications during planning phase
   - Error handling for invalid issue numbers and assignment conflicts
   - Integration with existing /issue commands without conflicts

4. **Success Criteria**:
   - Issue assigned to current user
   - Comprehensive implementation plan approved by user
   - Plan stored for Phase 2 (/issue start) consumption
   - No code modifications made during planning

## Example Usage

```
/issue plan 41
```

This initiates Phase 1 of the three-phase GitHub Issue workflow system.