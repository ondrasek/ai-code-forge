---
description: Automated GitHub issue duplicate detection and management
argument-hint: <issue-number>
allowed-tools: Task
---

# Dedupe Command

Automated GitHub issue duplicate detection and management system that identifies potential duplicates and provides semi-automated closure workflow.

## Usage

```bash
/issue:dedupe <issue-number>
```

**Parameters:**
- `<issue-number>`: Target issue number to analyze for duplicates

## Instructions

1. **Validate Issue Status**
   - Verify issue exists and is open
   - Check if issue is already marked as duplicate
   - Ensure current user has repository access

2. **Use Task tool to delegate to github-issues-workflow agent:**
   - Extract issue summary and generate search keywords
   - Conduct parallel searches for potential duplicates using diverse search strategies
   - Apply similarity analysis with confidence scoring (85% threshold)
   - Filter results to identify true duplicates vs similar issues
   - Generate structured comment with up to 3 duplicate links following template format
   - Implement 3-day auto-closure mechanism with user override options

3. **GitHub CLI Operations Required:**
   - `gh issue view` for issue details and validation
   - `gh issue list --search` for duplicate detection with strategic query patterns
   - `gh issue comment` for duplicate reporting with template compliance
   - `gh api` for rate limit monitoring and advanced operations

4. **Rate Limiting & Error Handling:**
   - Respect GitHub API limits (30 requests/minute conservative budget)
   - Implement exponential backoff for API failures
   - Handle partial operation recovery and state cleanup
   - Provide clear error messages for common failure scenarios

5. **User Safety Mechanisms:**
   - Conservative confidence thresholds to prevent false positives
   - Clear reversal mechanisms (not-duplicate label support)
   - Transparent process with audit logging
   - Manual confirmation options for edge cases

## Security & Reliability

- Input validation handled via GitHub API (all data pre-validated)
- No user input injection risks (Claude-generated commands only)
- Comprehensive error handling with graceful degradation
- Audit trail for all duplicate detection operations

## Integration

- Works with existing /issue command namespace
- Coordinates with github-issues-workflow agent for complex operations
- Maintains compatibility with issue lifecycle management
- Supports both manual and automated workflow integration

## Expected Output

The command will:
- Identify up to 3 potential duplicate issues
- Comment on original issue with structured duplicate links
- Set up 3-day auto-closure with user interaction options
- Provide clear status updates and error messages
- Enable easy reversal of incorrect duplicate identification