---
description: Audit existing agents against creation principles and usage metrics.
argument-hint: Optional agent names to audit, or empty to audit all agents.
allowed-tools: Task, Read, Glob, Grep
---

# Agent Audit

Audit existing agents in .claude/agents/ directory against creation principles and usage metrics for optimization opportunities.

## Instructions

1. Parse $ARGUMENTS for flags and agent names:
   - If --detailed flag present, include comprehensive analysis
   - If agent names specified, audit only those agents
   - If no args, audit all agents in .claude/agents/

2. Execute parallel agent clusters for comprehensive audit
- **Spawns individual agents**: Creates separate audit agents for each agent being evaluated
- **Parallel analysis**: Analyzes agent descriptions in isolated contexts for higher quality
- **Selection optimization**: Identifies low-performing description patterns using creation principles
- **Redundancy detection**: Checks for overlap between agents across separate analyses
- **Coordinated reporting**: Aggregates individual audits into comprehensive report

## Audit Criteria

### Description Quality Assessment
1. **Selection keyword analysis**: Presence of Tier 1/2 keywords
2. **Trigger specificity**: Concrete user context scenarios
3. **Boundary clarity**: Clear capability definitions
4. **Redundancy check**: Overlap with other agent descriptions

### Performance Indicators
1. **Selection frequency**: How often Claude Code invokes the agent
2. **Context efficiency**: Lines of output generated vs. main context pollution
3. **Boundary respect**: Amount of back-and-forth with main context
4. **Output quality**: Structured, actionable results without clarification needs

## Audit Output Format

```
## Agent Audit Report

**Agent**: [agent-name]
**Description Quality**: ⭐⭐⭐⚪⚪ (3/5)
**Selection Keywords**: Missing Tier 1 keywords
**Trigger Specificity**: Generic - needs quoted user phrases
**Boundary Clarity**: Well-defined
**Redundancy Risk**: Low overlap with other agents

### Optimization Recommendations:
1. Add "PROACTIVELY" keyword to description
2. Include quoted trigger phrases like "why does this happen"
3. Specify exact contexts when agent should be invoked

### Suggested Description:
```yaml
description: "PROACTIVELY use when user asks 'why does this happen', 'strange behavior', or debugging unexpected results. Expert at systematic hypothesis formation and testing"
```
```

## Red Flag Detection

**Flags agents for review/elimination:**
- Missing Tier 1 or Tier 2 selection keywords
- Generic descriptions without specific triggers
- Significant overlap with other agent capabilities
- Poor boundary definition requiring main context clarification

## Agent Spawning Strategy

**Enhanced Parallel Agent Cluster Analysis:**
- Use parallel agent clusters for comprehensive ecosystem analysis with universal agent integration
- **Core Quality Cluster**: patterns + principles + critic + researcher (agent analysis with researcher validation)
- **Strategic Optimization Cluster**: options-analyzer + constraint-solver + conflicts + principles (gap analysis with principle validation)
- **Performance Analysis Cluster**: researcher + context + critic (performance with critical assessment)
- **Design Validation Cluster**: principles + constraint-solver + researcher (fundamental validation with evidence researcher)
- **Completeness Assessment Cluster**: code-cleaner + patterns + critic + principles (gap identification with quality validation)
- Parallel execution for maximum performance and comprehensive coverage with universal agent support

**Enhanced Multi-Dimensional Aggregation:**
- Synthesize findings from all enhanced parallel agent clusters with universal agent support
- Cross-validate recommendations between analysis dimensions using critic and principles agents
- Identify ecosystem-wide patterns, gaps, and optimization opportunities with researcher intelligence
- Generate priority-based action plans with dependency mapping validated by constraint-solver and conflicts agents
- Apply completeness verification through code-cleaner agent coordination
- Ensure researcher-backed recommendations through systematic researcher integration

## Batch Analysis

**Options:**
- `--detailed`: Include full analysis and recommendations for each agent
- `agent-name...`: Audit specific agents only (spawns one agent per specified agent)
- No args: Audit all agents in `.claude/agents/` directory (spawns agent per discovered agent)

## Implementation Workflow

### Phase 1: Agent Discovery
```
1. Scan .claude/agents/ directory for all agent files
2. Parse agent names from command arguments (if provided)
3. Apply --detailed flag to audit scope
4. Prepare individual audit tasks for each agent
```

### Phase 2: Enhanced Parallel Agent Cluster Execution
```
Cluster 1 - Core Quality Analysis (patterns + principles + critic + researcher):
  Task: "Analyze agent descriptions, selection optimization, and principle compliance with researcher validation"
  Context: All agent definitions + creation principles + ecosystem patterns + latest agent best practices
  Output: Research-validated description quality assessment with optimization recommendations

Cluster 2 - Strategic Optimization Analysis (explorer + constraints + resolver + principles):
  Task: "Identify capability gaps, redundancies, and coordination opportunities with principle validation"
  Context: Complete agent ecosystem + usage patterns + coordination requirements + design principles
  Output: Principle-validated strategic optimization plan with priority recommendations

Cluster 3 - Performance Intelligence Analysis (researcher + time + context + critic):
  Task: "Analyze historical usage patterns and selection effectiveness with critical assessment"
  Context: Agent usage data + selection algorithm behavior + performance metrics + historical trends
  Output: Critically-assessed performance optimization recommendations with evidence basis

Cluster 4 - Design Validation Analysis (axioms + invariants + connector + researcher):
  Task: "Validate fundamental design principles and cross-domain connections with researcher support"
  Context: Agent design principles + ecosystem architecture + integration patterns + domain researcher
  Output: Research-supported design integrity assessment with architectural recommendations

Cluster 5 - Completeness Assessment Analysis (completer + patterns + critic + principles):
  Task: "Identify missing capabilities and incomplete implementations with quality validation"
  Context: Agent ecosystem completeness + implementation gaps + quality standards + best practices
  Output: Principle-guided completeness assessment with quality-assured gap identification
```

### Phase 3: Aggregation and Analysis
```
1. Collect all individual audit reports
2. Identify ecosystem patterns (redundancy, gaps, quality distribution)
3. Generate priority action list based on impact vs effort
4. Create consolidated recommendations for immediate fixes
```

### Phase 4: Reporting
```
- Executive summary with overall ecosystem health
- Individual agent scores and recommendations  
- Priority optimization actions ranked by impact
- Red flag agents requiring elimination/major revision
```

## Integration with Creation Principles

**Individual agent evaluation criteria** from @templates/guidelines/claude-agents-guidelines.md:
- **Overhead justification**: Does agent reduce >50 lines of main context?
- **Context boundaries**: Clear input/output without back-and-forth?
- **Selection optimization**: Tier 1/2 keywords for Claude Code selection?
- **Focus validation**: Computational tasks, thinking patterns, paradigms, perspectives vs human roles?

**Ecosystem-wide analysis:**
- **Redundancy detection**: Overlapping capabilities across agents
- **Gap identification**: Missing specialized analysis patterns
- **Quality distribution**: Spread of description optimization scores

## Memory Integration

**Before Analysis**: Use `mcp__memory__search_nodes()` to check for:
- Previous audit findings and patterns
- Historical agent performance data
- Known optimization outcomes
- Ecosystem evolution trends

**After Analysis**: Store findings with `mcp__memory__create_entities()` and `mcp__memory__create_relations()`:
- Agent quality assessments and trends
- Optimization recommendations and outcomes
- Ecosystem health metrics over time
- Cross-agent relationship patterns

## Related Commands
- `/agents-create` - Create new agents following principles
- `/agents-guide` - Documentation on using existing agents
- `/agents-audit` - Comprehensive ecosystem analysis (this command)

## Reference Documentation
- @templates/guidelines/claude-agents-guidelines.md - Complete creation and audit principles