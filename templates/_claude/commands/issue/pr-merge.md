---
description: AI-assisted PR merge with intelligent review analysis and automated merging capabilities.
argument-hint: <issue-number-or-pr-number>
allowed-tools: Task
---

# GitHub Pull Request Merge Analysis Phase

!`git status`
!`git diff HEAD`
!`git branch --show-current`

AI-assisted PR merge with comprehensive review analysis, draft handling, merge conflict detection, and automated merging when no concerns detected.

## Instructions

1. **Validate Input and PR State**:
   - Accept either issue number or PR number as argument
   - Resolve to specific PR if issue number provided
   - Validate PR exists and is accessible

2. **Use Task tool to delegate to github-pr-workflow agent**:
   - **PR State Analysis**: Comprehensive PR state assessment including:
     - Draft status detection and user confirmation for draft → ready transition
     - Merge conflict detection with resolution suggestions
     - CI/CD status checks validation
     - Branch protection rule compliance
   - **Review Analysis**: Intelligent analysis of reviewer comments including:
     - Best-effort interpretation of reviewer intent
     - Identification of blocking vs non-blocking concerns
     - Detection of approval signals vs change requests
     - Analysis of comment sentiment and significance
   - **Multi-Reviewer Handling**: 
     - Authority-weighted consensus for conflicting reviews
     - Resolution of mixed approval/concern scenarios
     - Clear reporting of reviewer disagreements
   - **Merge Decision Logic**:
     - **Automatic merge ONLY if no concerns detected**
     - Clear display of AI analysis and decision rationale
     - User confirmation for edge cases and ambiguous scenarios
   - **Safety Controls**:
     - Comprehensive audit logging of all decisions
     - Git revert preparation and rollback capabilities
     - Clear error handling with actionable messages

3. **Draft PR Handling**:
   - **MUST ask user** whether to switch PR out of draft mode
   - User confirmation required before draft → ready transition
   - Abort gracefully if user declines draft conversion

4. **Merge Conflict Resolution**:
   - Review and detect merge conflicts if present
   - **Suggest resolution approaches** to user
   - Provide guidance on conflict resolution strategies
   - Do not auto-resolve - require user intervention

5. **Critical Constraints**:
   - GitHub permissions handled by native API (not command's responsibility)
   - Best-effort reviewer context interpretation
   - Simple git revert for rollback operations
   - No rate limit handling required - straightforward API calls

6. **Success Criteria**:
   - Clear AI analysis display before any action
   - Automatic merge when no concerns detected
   - User maintains control over ambiguous decisions
   - Comprehensive logging of all merge decisions
   - Rollback capabilities available

## Example Usage

```
/issue pr-merge 188
/issue pr-merge pr-456
```

This provides AI-assisted PR merging with intelligent review analysis and automated decision-making based on reviewer feedback assessment.