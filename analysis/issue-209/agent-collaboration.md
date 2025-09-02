# Agent Collaboration Framework - Issue #209

## Cross-Agent Coordination Strategy

This document establishes the coordination framework for implementing repository detection across multiple specialized agents while maintaining system reliability and avoiding implementation conflicts.

## Agent Responsibility Matrix

### Foundation Agents (Research and Analysis)
✅ **context** - Complete ✅ **researcher** - Complete ✅ **stack-advisor** - Complete ✅ **critic** - Complete

**Findings Summary:**
- 42 hardcoded repository references identified across system
- Enhanced detection approach validated as optimal solution
- Security and error handling requirements established
- Risk mitigation strategies developed

### Implementation Agents (Next Phase)

#### Primary Implementation Agents
**github-issues-workflow** (Terminal Agent - High Priority)
- **Scope**: 20+ hardcoded references in GitHub issue operations
- **Complexity**: Multi-step workflows with issue creation, updates, and management
- **Constraints**: Terminal agent (cannot spawn other agents)
- **Requirements**: Self-contained repository detection implementation

**git-workflow** (Terminal Agent - High Priority)  
- **Scope**: 8+ hardcoded references in git operations with GitHub integration
- **Complexity**: Git operations combined with GitHub issue management
- **Constraints**: Terminal agent (cannot spawn other agents)
- **Requirements**: Coordination with github-issues-workflow for consistent context

**github-pr-workflow** (Terminal Agent - High Priority)
- **Scope**: 10+ hardcoded references in pull request operations
- **Complexity**: PR creation and management workflows
- **Constraints**: Terminal agent (cannot spawn other agents)
- **Requirements**: Repository detection for PR target validation

#### Supporting Implementation Agents
**code-cleaner** (Standard Agent - Medium Priority)
- **Scope**: Code quality improvements after primary implementation
- **Role**: Clean up implementation, optimize error handling
- **Timing**: After primary agents complete implementation

**test-strategist** (Standard Agent - Medium Priority)
- **Scope**: Comprehensive testing strategy for cross-repository functionality
- **Role**: Design test matrix for multiple repository contexts
- **Timing**: Parallel with primary implementation

**performance-optimizer** (Standard Agent - Low Priority)
- **Scope**: Optimize repository detection and caching mechanisms
- **Role**: Performance tuning after functional implementation
- **Timing**: Final optimization phase

## Implementation Coordination Protocol

### Shared Context Requirements
All implementation agents MUST:
1. **Read Analysis Files**: Review complete analysis directory before starting work
2. **Update Progress**: Document implementation decisions and progress
3. **Reference Prior Work**: Build upon foundation agent findings
4. **Coordinate Changes**: Ensure consistent repository detection patterns

### Common Implementation Patterns

#### Standard Repository Detection Function
All agents should implement this consistent pattern:
```bash
# Shared repository detection utility
detect_repository_context() {
    local repo_context
    local fallback_repo="${ACFORGE_REPO:-ondrasek/ai-code-forge}"
    
    # Attempt auto-detection
    repo_context=$(gh repo view --json nameWithOwner --jq '.nameWithOwner' 2>/dev/null)
    
    if [[ -z "$repo_context" ]]; then
        # Fallback to environment variable or hardcoded default
        repo_context="$fallback_repo"
        echo "WARNING: Using fallback repository: $repo_context" >&2
    fi
    
    # Validate repository access
    if ! validate_repository_access "$repo_context"; then
        echo "ERROR: Cannot access repository: $repo_context" >&2
        return 1
    fi
    
    echo "$repo_context"
}
```

#### Standard Error Handling Pattern
```bash
handle_repository_detection_failure() {
    echo "ERROR: Repository detection failed" >&2
    echo "Solutions:" >&2
    echo "  1. Run from within a git repository directory" >&2
    echo "  2. Set ACFORGE_REPO environment variable" >&2
    echo "  3. Use explicit --repo parameter if supported" >&2
    return 1
}
```

### Agent-Specific Implementation Notes

#### github-issues-workflow Agent
**Critical Requirements:**
- Must maintain backward compatibility with ondrasek/ai-code-forge
- Implement consistent repository context across all issue operations
- Handle label discovery dynamically (never hardcode labels)
- Provide clear error messages for repository detection failures

**Implementation Priorities:**
1. Core issue operations (create, update, list, close)
2. Label management with dynamic discovery
3. Issue commenting and status management
4. Integration with milestone and project management

#### git-workflow Agent  
**Critical Requirements:**
- Coordinate repository context with github-issues-workflow
- Handle git operations with GitHub integration consistently
- Maintain commit message and tagging functionality
- Ensure branch operations work across repository contexts

**Implementation Priorities:**
1. Commit and push operations with issue references
2. Branch management and PR integration
3. Tag creation with proper repository context
4. Git configuration and repository initialization

#### github-pr-workflow Agent
**Critical Requirements:**
- Validate PR target repository matches current context
- Handle fork scenarios with proper repository detection
- Maintain PR creation and management workflows
- Coordinate with git-workflow for branch operations

**Implementation Priorities:**
1. PR creation with dynamic repository detection
2. PR review and approval workflows
3. Merge and close operations
4. Draft PR and multi-repository coordination

## Risk Management and Coordination

### Critical Coordination Points
1. **Repository Context Consistency**: All agents must use same repository detection logic
2. **Error Message Standardization**: Consistent error handling across all agents
3. **Fallback Behavior**: Coordinated fallback to ensure no silent failures
4. **Testing Coordination**: Shared test scenarios across all implementations

### Conflict Resolution Protocol
When agents have conflicting implementation approaches:
1. **Reference Foundation Analysis**: Use research findings as authoritative source
2. **Prioritize Safety**: Choose approach that minimizes risk of regression
3. **Document Decisions**: Update decision-rationale.md with conflict resolution
4. **Validate Consistency**: Ensure resolution maintains system coherence

## Implementation Timeline and Dependencies

### Phase 1: Core Detection Implementation (High Priority)
- github-issues-workflow, git-workflow, github-pr-workflow
- Shared repository detection utility development
- Basic error handling and validation

### Phase 2: Enhancement and Testing (Medium Priority)  
- test-strategist develops comprehensive test matrix
- code-cleaner optimizes implementation quality
- Cross-repository validation testing

### Phase 3: Optimization and Documentation (Low Priority)
- performance-optimizer tunes detection and caching
- Documentation updates for new behavior
- User guidance and troubleshooting materials

## Quality Assurance Coordination

### Shared Testing Requirements
- All agents must validate against same test repository scenarios
- Consistent error handling validation across implementations
- Cross-agent workflow testing for coordinated operations

### Validation Checkpoints
1. **Individual Agent Testing**: Each agent validates its repository detection
2. **Integration Testing**: Cross-agent workflows maintain repository context
3. **Regression Testing**: Existing ondrasek/ai-code-forge functionality preserved
4. **Multi-Repository Testing**: Validation across different repository contexts

## Communication and Documentation Standards

### Progress Documentation
Each implementation agent must:
- Update `implementation-notes.md` with progress and decisions
- Reference foundation agent analysis in implementation decisions
- Document any deviations from planned approach with rationale

### Cross-Agent References
When agents build upon each other's work:
- **Explicit Attribution**: Reference specific agent contributions
- **Decision Inheritance**: Build upon prior agent decisions rather than revisiting
- **Conflict Documentation**: Document any conflicts with prior agent work

### Final Integration Documentation
The last implementing agent must:
- Consolidate all implementation decisions into coherent documentation
- Validate consistency across all agent implementations
- Update GitHub issue with comprehensive implementation summary

## Success Metrics for Agent Coordination

### Process Metrics
- All agents reference and update analysis directory appropriately
- Implementation consistency across all agents
- No conflicts between agent implementation approaches

### Outcome Metrics
- Repository detection works consistently across all agents
- Error handling provides clear, actionable guidance
- Cross-repository functionality validated across multiple contexts

This framework ensures coordinated, consistent implementation across all specialized agents while maintaining system reliability and avoiding implementation conflicts.