---
description: Recommend next GitHub Issue to work on based on priority analysis.
allowed-tools: Task
---

# GitHub Issue Next Task

!`git status`

Recommend the highest-value GitHub Issue to work on next.

## Instructions

1. Use Task tool to delegate to github-issues-workflow agent:
   - Analyze all open issues for priority and actionability
   - Identify unblocked tasks ready for immediate implementation
   - Consider dependencies and logical work sequences
   - Rank by impact, urgency, feasibility, and current context
   - Limit to top 3 recommendations unless $ARGUMENTS specify otherwise

2. Return prioritized recommendations with:
   - Issue details and clear rationale
   - Implementation readiness assessment
   - Dependency information