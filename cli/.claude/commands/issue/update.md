---
description: Update GitHub Issue with new information or status changes.
argument-hint: Issue number and update details.
allowed-tools: Task
---

# GitHub Issue Update

Update GitHub Issue with new information, labels, or status changes.

## Instructions

1. Use Task tool to delegate to github-issues-workflow agent:
   - Parse $ARGUMENTS to identify issue number and requested changes
   - Verify target issue exists and get current state
   - Apply intelligent updates based on provided information
   - Validate changes were applied successfully

2. Return confirmation with updated issue details and direct link