---
description: User-controlled Pull Request creation for implemented GitHub Issue.
argument-hint: <issue-number>
allowed-tools: Task
---

# GitHub Issue Pull Request Creation Phase

!`git status`
!`git diff HEAD`
!`git branch --show-current`

User-controlled PR creation phase with comprehensive analysis and multiple confirmation gates.

## Instructions

1. **Validate Issue Number and Phase 2 Completion**:
   - Ensure issue number is provided as argument
   - Verify Phase 2 (/issue start) completion and implementation metadata
   - Validate current branch state and implementation readiness

2. **Use Task tool to delegate to github-issues-workflow agent**:
   - **Implementation Validation**: Verify Phase 2 completion and current branch state
   - **Current Branch Analysis**: Analyze current branch for implementation changes
   - **GitHub API Integration**: Retrieve issue title, description, labels, metadata
   - **Implementation Analysis**: Analyze commits and changes made during implementation
   - **PR Content Generation**: Generate title and comprehensive description including:
     - Issue summary and context
     - Implementation approach overview
     - Key changes made
     - Testing performed
     - Proper issue references
   - **User Control Gates**:
     - Present generated content for review
     - Allow editing before creation
     - Require explicit confirmation
   - **PR Creation**: Create pull request from current branch with proper issue references ("Closes #<N>")
   - **Status Updates**: Update GitHub issue status upon PR creation
   - **Success Reporting**: Provide PR URL and confirmation

3. **Critical Constraints**:
   - Must validate Phase 2 (/issue start) completion
   - GitHub API error handling with clear messages
   - User abort capability at any point
   - Proper issue reference formatting

4. **Success Criteria**:
   - PR created with comprehensive description
   - Issue properly referenced ("Closes #<N>")
   - GitHub issue status updated
   - PR URL provided to user
   - User maintains full control over PR creation process

## Example Usage

```
/issue pr-create 41
```

This initiates Phase 3 of the three-phase GitHub Issue workflow system.