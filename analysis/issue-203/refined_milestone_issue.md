# Support for GitHub Milestones in Issues Managed via gh CLI

## Problem Statement

AI Code Forge currently lacks structured milestone management, creating challenges in:
- **Release coordination**: No systematic way to group issues for version releases
- **Progress visibility**: Cannot track completion percentage or burndown for feature sets
- **Due date management**: No integration between GitHub milestone deadlines and workflow planning
- **Issue categorization**: Missing temporal organization for related work items

## Solution Overview

Implement GitHub milestone management through CLI commands that integrate with existing `github-issues-workflow` agent, providing:
1. **CRUD Operations**: Create, list, edit, and delete milestones via `/milestone:*` commands
2. **Issue Integration**: Assign issues to milestones with automatic cross-referencing
3. **Progress Tracking**: Real-time completion analytics and deadline monitoring
4. **Release Coordination**: Connect milestone completion to version management workflow

**Key Design Principle**: Extend existing architecture without over-engineering - leverage GitHub's native milestone features rather than building complex custom systems.

## Acceptance Criteria

### High Priority: Core Milestone Operations

#### `/milestone:create` - Create New Milestone
- [ ] **Command Implementation**
  ```bash
  /milestone:create "v2.1.0 Release" "Major OAuth integration release" "2025-10-15"
  # Creates: https://github.com/owner/repo/milestone/N
  ```
- [ ] **API Integration**: `gh api repos/:owner/:repo/milestones --method POST`
- [ ] **Input Validation**:
  - Title uniqueness within repository
  - Due date format: ISO 8601 (YYYY-MM-DD)
  - Description length: max 1000 characters
- [ ] **Error Handling**: Duplicate titles, invalid dates, permission failures
- [ ] **File Location**: `.claude/commands/milestone/create.md`

#### `/milestone:list` - Browse Milestones
- [ ] **Command Variants**:
  ```bash
  /milestone:list                    # All open milestones
  /milestone:list --state closed     # Completed milestones
  /milestone:list --all             # Open and closed
  ```
- [ ] **Output Format**:
  ```
  📊 Repository Milestones
  #12 v2.1.0 Release    ██████░░░░ 60% (12/20)  Due: Oct 15
  #11 v2.0.1 Hotfix     ████████░░ 80% (4/5)   Due: Sep 20
  ```
- [ ] **API Query**: `gh api repos/:owner/:repo/milestones --jq '.[] | {number, title, state, due_on, open_issues, closed_issues}'`
- [ ] **File Location**: `.claude/commands/milestone/list.md`

#### `/milestone:edit` - Update Milestone
- [ ] **Command Syntax**:
  ```bash
  /milestone:edit 12 --title "v2.1.0 Major Release"
  /milestone:edit 12 --due-date "2025-11-01"
  /milestone:edit 12 --close
  ```
- [ ] **API Integration**: `gh api repos/:owner/:repo/milestones/:number --method PATCH`
- [ ] **State Validation**: Only allow open → closed transitions
- [ ] **File Location**: `.claude/commands/milestone/edit.md`

#### `/milestone:delete` - Remove Milestone
- [ ] **Safety Features**:
  - Confirmation prompt for milestones with assigned issues
  - Option to reassign issues before deletion
  - Preview of affected issues before confirmation
- [ ] **Command Flow**:
  ```bash
  /milestone:delete 12
  # Prompt: "Milestone 'v2.1.0' has 5 assigned issues. Reassign to different milestone? [Y/n]"
  ```
- [ ] **File Location**: `.claude/commands/milestone/delete.md`

### High Priority: Issue-Milestone Integration

#### Smart Issue Assignment
- [ ] **Milestone Suggestion During Issue Creation**
  - Analyze issue content for version-related keywords ("v2.1", "release", "feature")
  - Match issue priority/type labels with milestone themes
  - Suggest milestones with compatible due dates (not overdue, reasonable capacity)
  - Implementation: Extend `.claude/agents/specialists/github-issues-workflow.md`

#### `/milestone:assign` - Bulk Issue Assignment
- [ ] **Command Syntax**:
  ```bash
  /milestone:assign 12 #145 #146 #147    # Assign multiple issues
  /milestone:assign 12 --label feat      # Assign all feat issues
  /milestone:assign 12 --author ondrasek  # Assign all issues by author
  ```
- [ ] **Batch API Operations**: Use `gh api graphql` for efficient multi-issue updates
- [ ] **Validation Checks**:
  - Verify all issue numbers exist
  - Confirm milestone is open
  - Check for existing milestone assignments
- [ ] **Error Recovery**: Track partial failures, allow retry for failed assignments
- [ ] **File Location**: `.claude/commands/milestone/assign.md`

#### Automatic Cross-Referencing
- [ ] **Issue Comments**: Add "📋 Assigned to milestone: [v2.1.0 Release](milestone_url)" when assigned
- [ ] **Milestone Updates**: Update milestone description with "🔗 Related issues: #145, #146, #147"
- [ ] **Bidirectional Linking**: Maintain consistency between issue and milestone references
- [ ] **Integration Point**: Leverage existing cross-reference system in `github-issues-workflow` agent

### Medium Priority: Progress Analytics

#### `/milestone:progress` - Real-time Analytics
- [ ] **Visual Progress Display**:
  ```bash
  📊 v2.1.0 Release Progress
  ██████████░░░░░░░░░░ 60% (12/20 issues completed)
  ⏱️  Due: Oct 15, 2025 (23 days remaining)
  📈 Velocity: 2.1 issues/week (on track)
  🎯 Risk: LOW - ahead of schedule
  ```
- [ ] **Issue Type Breakdown**:
  ```
  🏷️  By Issue Type:
    feat: ████████░░ 80% (8/10)
    fix:  ██████░░░░ 60% (3/5) 
    docs: ██░░░░░░░░ 20% (1/5)
  ```
- [ ] **Risk Calculation**:
  - Current velocity vs required velocity to meet deadline
  - Flag milestones >80% time elapsed with <60% completion
  - Account for weekends and holidays in deadline calculation

#### Release Planning Integration
- [ ] **Milestone Completion Triggers**:
  - Auto-generate CHANGELOG entry from milestone issues
  - Suggest version bump based on issue types (feat=minor, fix=patch)
  - Create release branch when milestone reaches 90% completion
- [ ] **CHANGELOG Generation**: Group issues by type with milestone context:
  ```markdown
  ## [2.1.0] - 2025-10-15 (Milestone: v2.1.0 Release)
  ### Added
  - OAuth integration (#145)
  ### Fixed  
  - Rate limiting bug (#146)
  ```
- [ ] **Integration Point**: Extend `.claude/agents/specialists/git-workflow.md`

#### Progress Reports
- [ ] **Markdown Export**: Generate milestone status reports for PR descriptions
- [ ] **Blocked Issues Detection**: Identify issues waiting on dependencies
- [ ] **Ready-to-Close Analysis**: Find completed issues awaiting closure

### Low Priority: Advanced Features (Future Enhancements)

#### Milestone Templates
- [ ] **Template System**: Create reusable milestone configurations
  ```json
  // templates/milestones/major-release.json
  {
    "title_pattern": "v{major}.{minor}.0 Release",
    "description_template": "Major release with breaking changes and new features",
    "default_duration_days": 90,
    "suggested_labels": ["breaking-change", "feat", "docs"]
  }
  ```
- [ ] **Template Usage**: `/milestone:create --template major-release --version 3.0`
- [ ] **File Location**: `templates/milestones/`

#### Milestone Dependencies (Stretch Goal)
- [ ] **Dependency Metadata**: Store milestone relationships in descriptions using structured format:
  ```markdown
  <!-- milestone-dependencies: ["v2.0.0-dependencies"] -->
  <!-- milestone-blocks: ["v2.1.0-features"] -->
  ```
- [ ] **Validation**: Prevent closing milestones with incomplete dependencies
- [ ] **Visualization**: Show dependency chains in `/milestone:list --dependencies`

#### Performance Analytics (Nice-to-Have)
- [ ] **Historical Tracking**: Store milestone completion data in `analysis/milestones/history.json`
- [ ] **Velocity Analysis**: Calculate average completion times by milestone type
- [ ] **Accuracy Metrics**: Track estimation accuracy over time for planning improvements

## Technical Implementation

### File Structure (CLAUDE.md Compliance)
```
.claude/commands/milestone/
├── create.md          # /milestone:create command
├── list.md            # /milestone:list command  
├── edit.md            # /milestone:edit command
├── delete.md          # /milestone:delete command
├── assign.md          # /milestone:assign command
└── progress.md        # /milestone:progress command

templates/milestones/
└── *.json             # Milestone templates (future)

analysis/milestones/
└── history.json       # Performance data (future)
```

### Agent Integration Points
- **github-issues-workflow**: Extended with milestone suggestion logic
- **git-workflow**: Enhanced with milestone-triggered release operations
- **No new agents created**: Leverages existing agent architecture

### GitHub API Integration Examples

#### Milestone CRUD Operations
```bash
# Create milestone
gh api repos/ondrasek/ai-code-forge/milestones \
  --method POST \
  --field title="v2.1.0 Release" \
  --field description="Major OAuth integration release" \
  --field due_on="2025-10-15T23:59:59Z" \
  --field state="open"

# List milestones with progress data  
gh api repos/ondrasek/ai-code-forge/milestones \
  --jq '.[] | {number, title, state, due_on, open_issues, closed_issues, 
              progress: ((.closed_issues / (.open_issues + .closed_issues)) * 100)}'

# Update milestone state
gh api repos/ondrasek/ai-code-forge/milestones/12 \
  --method PATCH --field state="closed"
```

#### Efficient Issue Assignment
```bash
# Single issue assignment
gh api repos/ondrasek/ai-code-forge/issues/145 \
  --method PATCH --field milestone=12

# Batch assignment using GraphQL
gh api graphql -f query='
  mutation {
    updateIssue(input: {id: "issue_node_id", milestoneId: "milestone_node_id"}) {
      issue { number title }
    }
  }'
```

#### Progress Analytics Query
```bash
# Get milestone with detailed issue data
gh api repos/ondrasek/ai-code-forge/milestones/12 \
  --jq '{title, state, due_on, open_issues, closed_issues, 
         completion_rate: ((.closed_issues / (.open_issues + .closed_issues)) * 100),
         days_remaining: ((now | strftime("%Y-%m-%d")) as $today | 
           (.due_on | strptime("%Y-%m-%d") | mktime) - 
           ($today | strptime("%Y-%m-%d") | mktime)) / 86400}'
```

### Error Handling Strategy

#### GitHub API Resilience
- **Rate Limiting**: Monitor `gh api rate-limit`, implement exponential backoff
- **Permission Errors**: Graceful fallback to read-only operations
- **Network Failures**: Retry with user-friendly progress indicators
- **API Changes**: Version checking to detect GitHub API compatibility

#### Data Integrity
- **Validation**: Pre-flight checks before destructive operations
- **Atomic Operations**: Rollback capability for multi-step processes
- **Consistency**: Verify milestone-issue relationships before modifications
- **User Confirmation**: Interactive prompts for risky operations (delete with issues)

### Expected User Experience

#### Milestone Creation Flow
```bash
$ /milestone:create "v2.1.0 Release" "OAuth integration and performance improvements" "2025-10-15"
✅ Created milestone #12: v2.1.0 Release
📅 Due: October 15, 2025 (41 days from now)
📊 Current status: 0 issues assigned
🔗 https://github.com/ondrasek/ai-code-forge/milestone/12

💡 Suggestion: Use /milestone:assign 12 --label feat to add feature issues
```

#### Progress Monitoring
```bash
$ /milestone:progress 12
📊 v2.1.0 Release - 60% Complete
███████████████████░ 60% (12 of 20 issues)

📅 Timeline:
  Due date: Oct 15, 2025 (23 days remaining)
  Velocity: 2.1 issues/week
  Forecast: ✅ On track (estimated completion: Oct 12)

📈 Progress by Type:
  • feat: ████████░░ 8/10 (80%) - 2 remaining
  • fix:  ██████░░░░ 3/5  (60%) - 2 remaining  
  • docs: ██░░░░░░░░ 1/5  (20%) - 4 remaining

🚨 Attention Needed:
  • #156: Blocked by #155 (OAuth dependency)
  • #159: No activity for 7 days

✅ Ready for Review: #148, #151, #153
```

#### Issue Assignment Workflow
```bash
$ /milestone:assign 12 #145 #146 #147
✅ Assigned 3 issues to milestone v2.1.0 Release:
  • #145: OAuth provider integration
  • #146: Rate limiting improvements  
  • #147: API response caching

📊 Updated progress: 60% → 65% (15/23 issues)
🔗 Cross-references added to all issues
```

### Architecture Integration

#### Existing Agent Extensions
- **github-issues-workflow**: 
  - Add milestone suggestion during issue creation
  - Include milestone context in cross-references
  - Handle milestone assignment in issue lifecycle
- **git-workflow**:
  - Trigger version operations on milestone completion
  - Generate milestone-based CHANGELOG entries
  - Coordinate release branch creation

#### Integration Principles
- **No Circular Dependencies**: Clear data flow between agents
- **Existing Patterns**: Follow established command and agent conventions
- **Minimal Complexity**: Extend rather than replace existing functionality

### Performance Requirements

#### API Efficiency
- **Batch Operations**: Use GraphQL for multi-issue assignments
- **Caching**: Cache milestone data locally with 5-minute TTL
- **Pagination**: Handle repositories with 100+ milestones gracefully
- **Rate Limiting**: Stay within GitHub's 5000 requests/hour limit

#### Response Time Targets
- **CRUD Operations**: < 2 seconds for milestone creation/editing
- **Progress Analytics**: < 3 seconds for complex calculations
- **Bulk Assignment**: < 5 seconds for assigning 20+ issues
- **List Operations**: < 1 second for displaying milestone table

## Prerequisites and Constraints

### Required Dependencies
- **GitHub CLI**: v2.40+ with authenticated access
- **Repository Permissions**: Write access to milestones and issues
- **Existing Agents**: `github-issues-workflow` and `git-workflow` agents

### Operational Limits
- **GitHub API**: 5000 requests/hour rate limit
- **Repository Scale**: Optimized for <100 milestones, <1000 issues
- **Concurrent Users**: No conflict resolution for simultaneous edits
- **Data Storage**: GitHub API only (no local persistence)

### Architecture Constraints
- **File Structure**: Must follow CLAUDE.md command organization
- **Agent Boundaries**: Extend existing agents, don't create new ones
- **Context Separation**: Keep milestone operations isolated from other workflows

## Risk Mitigation

### Technical Risks
- **GitHub API Dependency**: Complete reliance on external service
  - *Mitigation*: Graceful fallbacks, error retry logic, rate limit monitoring
- **Data Consistency**: Race conditions in concurrent milestone operations
  - *Mitigation*: Pre-flight validation, atomic operations, user confirmations
- **Performance**: Slow operations on large repositories
  - *Mitigation*: Pagination, caching, batch APIs, progress indicators

### Integration Risks  
- **Agent Coordination**: Complex interactions between github-issues-workflow and git-workflow
  - *Mitigation*: Clear interface boundaries, extensive integration testing
- **Command Conflicts**: New `/milestone:*` commands may conflict with existing patterns
  - *Mitigation*: Follow established command conventions, thorough compatibility testing

### User Experience Risks
- **Complexity**: Too many options may overwhelm users
  - *Mitigation*: Start with simple core features, add complexity gradually
- **Adoption**: Users may not see value in milestone features
  - *Mitigation*: Clear documentation, practical examples, integration with popular workflows


## Implementation Priority

### High Priority (Core Functionality)
1. **Basic CRUD Operations**: Create, list, edit, delete milestones
2. **Issue Assignment**: Assign issues to milestones with cross-referencing
3. **Progress Analytics**: Real-time completion tracking and visualization
4. **github-issues-workflow Integration**: Milestone-aware issue creation

### Medium Priority (Enhanced Workflow)
1. **Release Integration**: Connect milestone completion to git-workflow
2. **Bulk Operations**: Multi-issue assignment and management
3. **Advanced Analytics**: Risk assessment and deadline forecasting

### Low Priority (Future Enhancements)
1. **Templates**: Reusable milestone configurations
2. **Dependencies**: Milestone blocking relationships
3. **Historical Analytics**: Performance tracking over time

**No artificial timelines or estimates** - implementation follows priority order with dependencies clearly mapped.

## Success Criteria

### Functional Requirements
- [ ] All `/milestone:*` commands work reliably with proper error handling
- [ ] Issues can be assigned to milestones with automatic cross-referencing  
- [ ] Progress analytics provide accurate completion percentages and timeline forecasts
- [ ] Integration with `github-issues-workflow` suggests relevant milestones during issue creation
- [ ] Milestone completion triggers appropriate git-workflow operations

### Quality Standards
- [ ] Commands follow CLAUDE.md file structure exactly
- [ ] All operations complete within performance targets
- [ ] Error messages are clear and actionable
- [ ] GitHub API usage stays within rate limits
- [ ] No conflicts with existing workflow patterns

### User Experience Goals
- [ ] Intuitive command syntax that feels natural
- [ ] Visual progress indicators that are easy to interpret
- [ ] Helpful suggestions and automation that reduces manual work
- [ ] Clear documentation with practical examples

---

**Ready for Development**: This specification provides concrete implementation details, clear acceptance criteria, and measurable success metrics while avoiding over-engineering and maintaining focus on user value.