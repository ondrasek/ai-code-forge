# Implementation Notes - Issue #168

## Implementation Progress Tracking

### Phase 1: Artifact-Based Reporting Workflow ✅ APPROVED
**Decision**: Implement GitHub Actions workflow that generates JSON reports stored as artifacts.

### Implementation Plan:

#### 1. GitHub Actions Workflow Design
**File**: `.github/workflows/issue-housekeeping.yml`
**Features**:
- Manual trigger via `workflow_dispatch` for testing
- Future: Scheduled execution (weekly via cron)
- Dry-run mode only (no label changes)
- Artifact upload with 90-day retention
- Cost monitoring and API rate limiting

#### 2. Issue Analysis Script
**Approach**: Python script that:
- Fetches all open issues via GitHub API
- Analyzes each issue with Claude Code
- Generates structured JSON report
- Implements safety protections (protected labels)
- Respects API rate limits with exponential backoff

#### 3. Safety Features (MANDATORY)
- **Protected Labels**: Hard-coded list of labels that CANNOT be removed
  - `critical`, `security`, `high priority`
- **Confidence Thresholds**: Only recommend changes with high confidence
- **API Rate Limiting**: Respect GitHub's 1,000 req/hour limit
- **Cost Controls**: Monitor Claude API token usage

#### 4. Report Structure
```json
{
  "metadata": {
    "workflow_run_id": "...",
    "timestamp": "2025-08-12T15:30:00Z",
    "analysis_scope": "all_open_issues",
    "safety_mode": "dry_run_only"
  },
  "summary": {
    "issues_analyzed": 167,
    "recommendations_count": 15,
    "protected_labels_found": 8,
    "api_calls_made": 180,
    "estimated_cost": "$0.45"
  },
  "issues": [
    {
      "number": 114,
      "title": "enhance github-pr-workflow agent...",
      "current_labels": ["feat", "human feedback needed"],
      "recommendations": {
        "remove": ["human feedback needed"],
        "add": [],
        "confidence": "high",
        "reasoning": "Issue appears resolved based on recent comments"
      }
    }
  ],
  "safety_checks": {
    "protected_labels_respected": true,
    "rate_limits_within_bounds": true,
    "dry_run_verified": true
  }
}
```

#### 5. Human Review Process
- Workflow generates artifact with JSON report
- Human downloads and reviews recommendations
- Manual application of approved changes
- Future enhancement: Semi-automated application with approval

### Next Steps:
1. Create workflow YAML file
2. Implement Python analysis script
3. Test with small issue subset
4. Validate artifact generation and access
5. Full dry-run test on all issues

### Dependencies:
- Claude Code CLI available in GitHub Actions environment
- GitHub API token with `issues:read` permissions
- Python environment for analysis script

### Risk Mitigation:
- Start with manual triggers only
- Implement comprehensive logging
- Monitor costs and API usage
- Clear rollback procedures documented