---
description: Analyze code quality, identify issues, and provide recommendations.
argument-hint: Optional FILES to review, or empty to review all uncommitted changes.
allowed-tools: Task, Read, Grep, Bash
---

# Code Review

!`git status`
!`git diff --name-only`

Analyze code quality, identify issues, and provide recommendations for uncommitted changes by default, or specified files/commits.

## Instructions

1. Automatically determine review scope:
   - If $ARGUMENTS contains files, review those files
   - If no arguments, review all uncommitted changes
   - Always include memory and historical patterns

2. Execute optimized parallel review clusters with focus detection
1. **Focus Determination Phase**: Auto-detect review focus or ask user for clarification
2. **Efficient Parallel Review Clusters** (3-4 agents per cluster, focus-driven selection):
   - **Core Analysis Cluster**: patterns + principles + critic (essential quality assessment)
   - **Context & Research Cluster**: context + researcher (architectural understanding and external knowledge)  
   - **Specialist Focus Cluster**: Dynamically selected based on detected focus (constraint-solver, performance-optimizer, test-strategist, or code-cleaner)
3. **Synthesis Phase**: conflicts + critic (conflict resolution and final recommendations)
4. **Memory Integration**: Foundation agents store findings for institutional knowledge building

PARAMETERS:
--commits N (review last N commits)
--memory (include historical review patterns)
FILES... (specific files to review)

INTELLIGENT_FOCUS_DETECTION:
1. **Auto-determine from user prompt**: Parse user language for focus signals ("security issues", "performance problems", "test coverage", etc.)
2. **Context analysis**: Examine files/changes to infer review priorities (new dependencies → security, database changes → performance, etc.)
3. **User clarification**: If focus unclear, ask user to specify priority areas before proceeding
4. **Agent-assisted determination**: Use context agent to analyze codebase and suggest focus areas
5. **Default comprehensive**: If no specific focus detected, provide balanced multi-dimensional analysis

OPTIMIZED_PARALLEL_CLUSTERS:
Core Analysis (3 agents): patterns + principles + critic
Context & Research (2 agents): context + researcher  
Specialist Focus (1-2 agents): Dynamically selected based on detected focus
Synthesis (2 agents): conflicts + critic

FOCUS_BASED_SPECIALIST_SELECTION:
- **Performance Focus**: performance-optimizer + constraint-solver
- **Testing Focus**: test-strategist + code-cleaner
- **Documentation Focus**: stack-advisor
- **Architecture Focus**: constraint-solver + options-analyzer
- **Code Quality Focus**: code-cleaner + patterns
- **Comprehensive**: Rotate through multiple specialists based on findings

COORDINATION_PROTOCOL: All clusters execute simultaneously via single message with multiple Task() calls for efficient parallel processing. Total agents: 8-10 (optimized from previous 34-agent approach)

INTELLIGENT_OUTPUT:
- **Focus-Driven Analysis**: Results tailored to auto-detected or user-specified priorities
- **Memory-Enhanced Findings**: Built on historical review patterns and institutional knowledge
- **Optimized Assessment**: Comprehensive analysis through efficient agent coordination (8-10 agents)
- **Auto-Determined Severity**: Intelligent severity classification without user pre-specification
- **Conflict Resolution**: conflicts mediates competing recommendations
- **Prioritized Action Items**: Ranked by impact, effort, and historical success patterns
- **Institutional Knowledge**: All findings stored in memory graph for continuous learning

## Memory Integration Workflow

**BEFORE Review** (Automatic via foundation agents):
- **patterns**: Load historical code pattern discoveries and evolution trends
- **critic**: Check stored risk assessments and failure patterns from similar changes
- **researcher**: Access external best practices and community solutions for identified issues  
- **context**: Load architectural evolution context and historical decision rationale
- **principles**: Review previous principle violation patterns and resolution effectiveness

**DURING Review** (Memory-enhanced analysis):
- **Pattern Evolution Tracking**: Compare current patterns to stored historical data
- **Risk Assessment Enhancement**: Validate risks against stored failure precedents
- **Research Integration**: Apply stored external knowledge to current code context
- **Context-Aware Analysis**: Use architectural memory for system-appropriate recommendations
- **Principle Adherence Trends**: Track principle compliance patterns over time

**AFTER Review** (Institutional knowledge preservation):
- **Pattern Storage**: Update pattern entities with new discoveries and frequency changes
- **Risk Documentation**: Store new risks and update historical success/failure rates
- **Research Archiving**: Preserve validated external solutions and implementation guidance
- **Context Evolution**: Record architectural changes and their impact on review findings
- **Principle Learning**: Document principle application outcomes and team preferences
- **Resolution Patterns**: Store successful conflict resolutions and their effectiveness

## Intelligent Review Strategy

**FOCUS-DRIVEN ANALYSIS**: Command automatically adapts agent selection based on detected review priorities

### Focus Detection Logic
1. **User Prompt Analysis**: Parse explicit focus requests ("check security", "performance review", "test coverage")
2. **Change Pattern Recognition**: Analyze modified files for focus indicators (dependencies → security, algorithms → performance, test files → testing)
3. **Context Clues**: Repository structure and file types suggest review priorities
4. **User Clarification**: Interactive focus selection when automated detection is ambiguous
5. **Comprehensive Default**: Balanced analysis when no specific focus is identified

### Dynamic Agent Coordination
- **Core Foundation Trio**: patterns + principles + critic (always included)
- **Context & Research Duo**: context + researcher (architectural understanding and external knowledge)
- **Specialist Selection**: Dynamically chosen based on detected focus priorities
- **Synthesis Pair**: conflicts + critic (conflict resolution and final recommendations)

**EFFICIENCY PRINCIPLE**: Maintains comprehensive coverage while optimizing agent count (8-10 total) for faster execution and reduced coordination overhead

## Optimized Execution Workflow

### Phase 1: Focus Detection & Context Loading
```
1. Parse user prompt and analyze files/changes for focus indicators
2. If focus unclear, ask user to specify priority areas
3. Load system context: context agent
4. Baseline researcher: researcher agent
```

### Phase 2: Parallel Review Clusters (8-10 agents total)
```
Task: "Execute Core Analysis" (patterns + principles + critic)
Task: "Execute Context & Research analysis" (context + researcher)  
Task: "Execute Specialist Focus analysis" (dynamically selected based on detected focus)
```

### Phase 3: Synthesis & Resolution
```
Task: "Resolve conflicts and synthesize recommendations" (conflicts + critic)
```

**OPTIMIZED AGENT COUNT**: 8-10 agents total (efficient coordination within performance targets)

**MEMORY INTEGRATION**: All foundation agents automatically store findings in persistent memory graph for institutional knowledge building

## Enhanced Output Structure

### Review Summary
- **Scope**: Files/commits analyzed with git context
- **Focus**: Auto-detected or user-specified review priorities
- **Agent Execution**: Confirmation of optimized cluster execution (8-10 agents)
- **Memory Status**: Historical patterns loaded and new findings stored
- **Overall Assessment**: Auto-determined severity levels with confidence scores

### Focus-Driven Findings
- **Code Quality**: From patterns with historical trend analysis
- **Design Principles**: From principles with adherence assessment
- **Architecture & Context**: From context with evolution analysis
- **External Research**: From researcher with best practices integration
- **Specialist Analysis**: Focus-specific findings from dynamically selected specialist agents
- **Critical Risks**: From critic with evidence-based risk assessment

### Intelligent Synthesis
- **Conflict Resolution**: conflicts mediates competing approaches
- **Trade-off Analysis**: Risk vs benefit with historical precedent data
- **Recommended Actions**: Evidence-based prioritization with success probability
- **Implementation Strategy**: Optimized based on stored resolution patterns

### Auto-Prioritized Action Plan
- **Critical**: Auto-detected security vulnerabilities and system stability risks
- **High**: Significant principle violations and performance bottlenecks
- **Medium**: Code quality improvements and architectural concerns
- **Low**: Documentation updates and minor consistency issues

### Knowledge Preservation
- **Pattern Evolution**: Code patterns and trends stored for future reference
- **Risk Intelligence**: Failure patterns and mitigation strategies documented
- **Solution Archive**: Validated external solutions and implementation guidance preserved
- **Decision Context**: Architectural changes and rationale recorded for institutional memory

## Related Commands

- `/security` - Focused security analysis with constraint-solver agent
- `/test` - Test coverage improvements with test-strategist coordination
- `/refactor` - Implement review suggestions and code improvements
- `/performance` - Deep performance analysis with performance-optimizer focus
- `/fix` - Implement specific fixes for identified issues