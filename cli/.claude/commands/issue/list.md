---
description: List GitHub Issues with smart filtering and prioritization.
allowed-tools: Task
---

# GitHub Issue List

List GitHub Issues with intelligent filtering and priority ranking.

## Instructions

1. Use Task tool to delegate to github-issues-workflow agent:
   - Fetch all open issues by default
   - Apply intelligent filtering based on $ARGUMENTS (if provided)
   - Sort by priority and recent activity
   - Format results in readable table with issue numbers, titles, labels
   - Include summary statistics

2. Return formatted issue list with actionable insights