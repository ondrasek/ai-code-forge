---
description: Create new GitHub Issue with intelligent classification and metadata.
argument-hint: Issue description or topic.
allowed-tools: Task
---

# GitHub Issue Creation

Create new GitHub Issue with intelligent classification based on content analysis.

## Instructions

1. Use Task tool to delegate to github-issues-workflow agent:
   - Analyze $ARGUMENTS (if provided) or prompt user for issue description
   - Automatically classify issue type based on content
   - Generate appropriate title and labels
   - Create GitHub issue with proper metadata
   - Return issue number and URL

2. Provide confirmation with issue details and direct link