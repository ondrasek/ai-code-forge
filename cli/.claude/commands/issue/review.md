---
description: Analyze GitHub Issues backlog for strategic prioritization.
argument-hint: <issue number> (optional) or [focus areas] (optional)
allowed-tools: Task
---

# GitHub Issue Review

Analyze GitHub Issues backlog and provide strategic prioritization recommendations.

## Instructions

1. Use Task tool to delegate to github-issues-workflow agent:
   - Analyze all open issues for relevance and actionability
   - Group related issues for efficient batch processing
   - Update labels for issues if labels do not match issue definition
   - Cross-reference with other existing relevant issues
   - Assess dependencies and optimal implementation sequences
   - Consider issues that meet $ARGUMENTS for focus areas if provided
   - Review only single issue when <issue number> is in $ARGUMENTS

2. Return strategic analysis with:
   - Backlog health assessment
   - Suggestions for improvement