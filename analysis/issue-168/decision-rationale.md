# Decision Rationale - Issue #168

## Primary Storage Decision: GitHub Actions Artifacts

**Chosen Approach**: Store JSON reports as GitHub Actions workflow artifacts with selective permanent archival.

### Technical Rationale:

**Why Artifacts Over Repository Storage:**
- **Purpose-Built**: Artifacts designed exactly for workflow-generated files requiring human review
- **Cost-Effective**: Free for public repositories, reasonable pricing for private ($0.008/GB/day)  
- **Retention Management**: Built-in lifecycle management (1-400 days configurable)
- **Security**: Integrated with GitHub permissions, no custom access control needed
- **Performance**: v4 artifacts provide immediate API access and 90% performance improvement

**Why Not Git Repository Storage:**
- **Repository Pollution**: JSON reports would clutter git history
- **No Automatic Cleanup**: Reports would persist indefinitely without manual management
- **Access Complexity**: Would require custom tooling for report browsing

### Implementation Architecture:

```yaml
# Primary: Workflow Artifacts (30-90 day retention)
- name: Upload Issue Analysis Report
  uses: actions/upload-artifact@v4
  with:
    name: issue-analysis-${{ github.run_id }}
    path: reports/
    retention-days: 90

# Secondary: Selective Permanent Archival
- name: Archive Significant Reports
  if: contains(github.event.inputs.archive, 'true')
  run: |
    git add reports/significant/
    git commit -m "archive: issue analysis summary"
```

### Artifact Structure:

```json
{
  "metadata": {
    "workflow_run_id": "${{ github.run_id }}",
    "commit_sha": "${{ github.sha }}",
    "timestamp": "2025-08-12T15:30:00Z",
    "analysis_scope": "issues_1-20"
  },
  "analysis_results": {
    "issues_analyzed": 167,
    "label_recommendations": [...],
    "confidence_scores": {...},
    "protected_labels_found": [...]
  },
  "safety_checks": {
    "protected_labels_verified": true,
    "api_rate_limits_respected": true,
    "dry_run_mode": true
  }
}
```

### Critical Migration Note:
**January 30, 2025 Deadline**: Must use `actions/upload-artifact@v4` as v3 will stop working. This provides immediate implementation benefit with 90% performance improvement.

### Cost Analysis:
- **Public Repository**: Free (current ai-code-forge status)
- **Private Repository**: ~$2-5/month for daily 10MB reports with 90-day retention
- **Optimization**: Use compression, appropriate retention periods, automated cleanup

### Human Review Integration:
1. **Workflow Summary**: Generate markdown summary for immediate GitHub UI visibility
2. **Artifact Download**: JSON reports downloadable for detailed analysis  
3. **PR Comments**: Key findings posted as automated comments
4. **Issue Updates**: Safe recommendations applied via follow-up workflows

This approach balances automation safety, cost efficiency, and human oversight requirements while leveraging GitHub's native infrastructure.