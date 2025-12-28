---
description: Intelligently refine GitHub Issues through automated research, critical questioning, and elaboration.
argument-hint: <issue number> or <issue URL>
allowed-tools: Task
---

# GitHub Issue Refinement

Enhance GitHub Issues through intelligent analysis, critical questioning, and comprehensive elaboration with automated workflow integration.

## Instructions

1. Use Task tool to delegate to github-issues-workflow agent:
   - Parse $ARGUMENTS to extract issue number/URL
   - Fetch and analyze existing issue content thoroughly
   - Conduct comprehensive research on context and dependencies
   - Generate critical questions to clarify ambiguous requirements
   - Elaborate on technical implementation considerations and edge cases
   - Identify potential constraints, risks, and integration points
   - Suggest improved acceptance criteria and test scenarios
   - Analyze dependencies and cross-references with related issues
   - Prepare structured refinement analysis

2. Present refinement results with:
   - **Critical Questions**: Key clarifications needed from stakeholders
   - **Technical Analysis**: Implementation considerations, constraints, and dependencies
   - **Enhanced Acceptance Criteria**: Specific, measurable, and testable outcomes
   - **Risk Assessment**: Potential issues, edge cases, and mitigation strategies
   - **Integration Points**: Related issues, dependencies, and system impacts

3. **Safety-First GitHub Integration**:
   - Generate read-only analysis requiring manual human review
   - Never automatically modify GitHub issues without explicit approval
   - Present refinement suggestions for manual application
   - Include workflow automation recommendations with safety constraints

## Usage Examples

```
/issue:refine 90
/issue:refine https://github.com/ondrasek/ai-code-forge/issues/90
```

## Refinement Capabilities

- **Contextual Research**: Analyze codebase, related issues, and project patterns
- **Critical Analysis**: Question assumptions, identify gaps, and propose improvements
- **Technical Elaboration**: Detailed implementation considerations and architecture impacts
- **Edge Case Detection**: Identify potential failure scenarios and boundary conditions
- **Dependency Mapping**: Cross-reference related issues and system components
- **Acceptance Criteria Enhancement**: Transform vague requirements into measurable outcomes

## Integration Features

- **Agent Coordination**: Seamlessly integrates with github-issues-workflow agent
- **Context Preservation**: Maintains clean separation between analysis and execution
- **Workflow Automation**: Optional GitHub Actions integration with human oversight
- **Safety Mechanisms**: Prevents infinite loops and over-automation through conservative design