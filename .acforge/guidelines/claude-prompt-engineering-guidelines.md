# Claude Prompt Engineering Guidelines

## Overview

These guidelines provide comprehensive frameworks for writing AI instructions, agent definitions, and command prompts optimized specifically for Claude models. Based on 2025 Anthropic best practices and analysis of successful implementation patterns, these guidelines focus on creating effective AI instructions (not human-readable documentation).

## Core Principles

### 1. Structured XML Prompting

Use XML-style tags for complex structured instructions. This aligns with Claude's optimal parsing patterns:

```xml
<instruction_type priority="CRITICAL|HIGH|MEDIUM|LOW">
<definition>Clear explanation of the instruction purpose</definition>
<enforcement>Specific enforcement mechanism</enforcement>
<examples>
  ✅ Correct example
  ❌ Incorrect example
</examples>
<validation>Validation criteria or checklist</validation>
</instruction_type>
```

### 2. Priority-Based Hierarchies

Implement clear priority levels for instruction enforcement:

- **CRITICAL**: System-breaking instructions that must never be ignored
- **HIGH**: Important behaviors that significantly impact functionality  
- **MEDIUM**: Best practices and optimization guidelines
- **LOW**: Preferences and stylistic choices

### 3. Explicit Enforcement Patterns

Use dedicated `<enforcement>` sections with specific mechanisms:

```xml
<enforcement>Task(agent-type) after EVERY condition</enforcement>
<enforcement>NEVER perform action unless explicit condition</enforcement>
<enforcement>ALWAYS validate input before processing</enforcement>
```

### 4. Context Separation

Organize instructions into distinct sections to prevent interference:

```xml
<operational_rules>
  <context_separation>Different instruction types in separate containers</context_separation>
  <autonomous_operation>Independent operation guidelines</autonomous_operation>
</operational_rules>
```

## Agent Definition Framework

### Standard Agent Structure

```xml
<agent_definition>
<role>Specific role and responsibility boundary</role>
<capabilities>
  - Tool access list
  - Functional boundaries
  - Integration patterns
</capabilities>
<restrictions>
  - Clear limitations
  - Boundary enforcement
  - Handoff conditions
</restrictions>
<coordination>
  - Multi-agent interaction patterns
  - Handoff protocols
  - Context preservation methods
</coordination>
<output_format>
  - Expected response structure
  - Formatting requirements
  - Validation patterns
</output_format>
</agent_definition>
```

### Agent Boundary Definition

```xml
<agent_boundaries priority="HIGH">
<trigger_patterns>
  - "keyword1", "phrase pattern", "user asks X"
  - PROACTIVELY use when conditions met
  - MUST USE when specific scenarios occur
</trigger_patterns>
<capability_scope>
  - What this agent CAN do
  - What this agent CANNOT do
  - Tool access permissions
</capability_scope>
<handoff_protocols>
  - When to delegate to other agents
  - Context preservation requirements
  - Completion criteria
</handoff_protocols>
</agent_boundaries>
```

### Role Clarity Patterns

```xml
<role_definition priority="CRITICAL">
<primary_function>Single, clear responsibility statement</primary_function>
<expertise_areas>
  - Domain 1: Specific capabilities
  - Domain 2: Specific capabilities
</expertise_areas>
<decision_authority>
  - Decisions this agent can make autonomously
  - Decisions requiring user confirmation
  - Decisions requiring other agent consultation
</decision_authority>
</role_definition>
```

## Command Prompt Patterns

### Action-Oriented Structure

```xml
<command_definition>
<name>/command-name</name>
<purpose>Clear, actionable objective</purpose>
<parameters>
  <required>
    - param1: description and validation
    - param2: description and validation
  </required>
  <optional>
    - param3: description and default behavior
  </optional>
</parameters>
<validation_chain>
  1. Input validation criteria
  2. Precondition checks
  3. Permission verification
  4. Resource availability
</validation_chain>
<execution_pattern>
  1. Setup and preparation steps
  2. Core operation sequence
  3. Validation and verification
  4. Cleanup and reporting
</execution_pattern>
<error_handling>
  - Common failure modes
  - Recovery strategies
  - Escalation protocols
</error_handling>
</command_definition>
```

### Parameter Validation Chains

```xml
<parameter_validation priority="HIGH">
<input_checks>
  - Type validation (string, number, boolean)
  - Format validation (regex patterns, length limits)
  - Content validation (allowlists, business rules)
</input_checks>
<dependency_validation>
  - Required file existence
  - Permission verification
  - Resource availability checks
</dependency_validation>
<security_validation>
  - Path traversal prevention
  - Injection attack prevention
  - Access control verification
</security_validation>
</parameter_validation>
```

### Execution Monitoring

```xml
<execution_monitoring priority="MEDIUM">
<progress_tracking>
  - Milestone checkpoints
  - Progress indicator updates
  - User communication patterns
</progress_tracking>
<error_detection>
  - Early failure detection
  - Resource exhaustion monitoring
  - Performance threshold monitoring
</error_detection>
<quality_assurance>
  - Output validation
  - Consistency checks
  - Completeness verification
</quality_assurance>
</execution_monitoring>
```

## System Instruction Patterns

### Clear Role Definition

```xml
<system_role priority="CRITICAL">
<identity>Specific AI assistant type and capabilities</identity>
<primary_objectives>
  - Objective 1 with success criteria
  - Objective 2 with success criteria
</primary_objectives>
<behavioral_constraints>
  - What must always be done
  - What must never be done
  - Conditional behaviors
</behavioral_constraints>
</system_role>
```

### Output Format Specification

```xml
<output_requirements priority="HIGH">
<format_structure>
  - Response format (markdown, JSON, plain text)
  - Section organization
  - Required headers/footers
</format_structure>
<content_requirements>
  - Information completeness
  - Detail level specifications
  - Tone and style guidelines
</content_requirements>
<validation_markers>
  - Success indicators
  - Completion signals
  - Error condition reporting
</validation_markers>
</output_requirements>
```

### Conditional Logic Implementation

```xml
<conditional_behavior priority="MEDIUM">
<if_conditions>
  <condition trigger="user_asks_X">
    <action>Specific response pattern</action>
    <escalation>Fallback if action fails</escalation>
  </condition>
  <condition trigger="context_contains_Y">
    <action>Alternative response pattern</action>
    <validation>Success criteria</validation>
  </condition>
</if_conditions>
<default_behavior>
  - Standard operating mode
  - Fallback actions
  - Error recovery patterns
</default_behavior>
</conditional_behavior>
```

## Validation Frameworks

### Input→Process→Output Verification

```xml
<validation_framework priority="HIGH">
<input_validation>
  - Parameter completeness check
  - Format and type verification
  - Business rule compliance
  - Security constraint validation
</input_validation>
<process_validation>
  - Step-by-step verification
  - Intermediate result checking
  - Resource utilization monitoring
  - Error condition detection
</process_validation>
<output_validation>
  - Completeness verification
  - Format compliance checking
  - Quality standard validation
  - User requirement fulfillment
</output_validation>
</validation_framework>
```

### Quality Assurance Patterns

```xml
<quality_assurance priority="MEDIUM">
<consistency_checking>
  - Cross-reference validation
  - Logical consistency verification
  - Style guideline compliance
</consistency_checking>
<completeness_validation>
  - Requirement coverage analysis
  - Missing component detection
  - Dependency satisfaction verification
</completeness_validation>
<performance_optimization>
  - Efficiency pattern identification
  - Resource usage optimization
  - Response time optimization
</performance_optimization>
</quality_assurance>
```

### Self-Verification Protocols

```xml
<self_verification priority="MEDIUM">
<verification_checklist>
  ☐ All required parameters processed
  ☐ Output format compliance verified
  ☐ Quality standards met
  ☐ Error conditions handled
  ☐ User requirements satisfied
</verification_checklist>
<verification_automation>
  - Automated checks where possible
  - Manual verification triggers
  - Escalation for failed verification
</verification_automation>
</self_verification>
```

## Claude-Specific Optimizations

### Context Window Efficiency

```xml
<context_optimization priority="HIGH">
<information_density>
  - Hierarchical information organization
  - Priority-based content ordering
  - Redundancy elimination
</information_density>
<memory_patterns>
  - Context preservation strategies
  - Information compression techniques
  - Reference-based instruction patterns
</memory_patterns>
<token_efficiency>
  - Structured markup optimization
  - Abbreviated pattern usage
  - Symbol-based shorthand systems
</token_efficiency>
</context_optimization>
```

### Chain of Thought Integration

```xml
<reasoning_patterns priority="MEDIUM">
<explicit_reasoning>
  - Step-by-step thought processes
  - Decision rationale documentation
  - Alternative consideration patterns
</explicit_reasoning>
<problem_decomposition>
  - Complex task breakdown strategies
  - Dependency identification patterns
  - Sequential execution planning
</problem_decomposition>
<solution_validation>
  - Reasoning verification steps
  - Logic consistency checking
  - Conclusion validation patterns
</solution_validation>
</reasoning_patterns>
```

### Few-Shot Learning Optimization

```xml
<example_patterns priority="MEDIUM">
<pattern_demonstration>
  ✅ Correct implementation example
  ❌ Incorrect implementation example
  🔧 Common variation examples
</pattern_demonstration>
<context_examples>
  - Scenario 1: Input → Process → Output
  - Scenario 2: Input → Process → Output
  - Edge Case: Input → Process → Output
</context_examples>
<learning_reinforcement>
  - Pattern consistency emphasis
  - Key decision point highlighting
  - Success criteria demonstration
</learning_reinforcement>
</example_patterns>
```

## Error Recovery Patterns

### Graceful Failure Handling

```xml
<error_recovery priority="HIGH">
<failure_detection>
  - Early warning indicators
  - Critical failure conditions
  - Performance degradation signs
</failure_detection>
<recovery_strategies>
  - Automatic retry mechanisms
  - Fallback operation modes
  - Alternative solution pathways
</recovery_strategies>
<escalation_protocols>
  - Human intervention triggers
  - Alternative agent handoff
  - System limitation acknowledgment
</escalation_protocols>
</error_recovery>
```

### Instruction Conflict Resolution

```xml
<conflict_resolution priority="HIGH">
<priority_hierarchy>
  - CRITICAL overrides all other instructions
  - HIGH overrides MEDIUM and LOW
  - MEDIUM overrides LOW only
  - Explicit override patterns
</priority_hierarchy>
<conflict_detection>
  - Contradictory instruction identification
  - Ambiguity recognition patterns
  - Resolution requirement triggers
</conflict_detection>
<resolution_protocols>
  - Automatic resolution where possible
  - User clarification requests
  - Default behavior specifications
</resolution_protocols>
</conflict_resolution>
```

### Degraded Operation Modes

```xml
<degraded_operation priority="MEDIUM">
<capability_reduction>
  - Feature limitation protocols
  - Performance optimization modes
  - Simplified operation patterns
</capability_reduction>
<service_continuation>
  - Core function preservation
  - Essential feature prioritization
  - User expectation management
</service_continuation>
<recovery_planning>
  - Normal operation restoration
  - Progressive capability restoration
  - User notification patterns
</recovery_planning>
</degraded_operation>
```

## Implementation Guidelines

### File Structure Requirements

Following the established file structure patterns:

```
templates/guidelines/     ← Template guidelines for distribution
.claude/agents/           ← Agent definitions only
.claude/commands/         ← Slash command definitions only
templates/prompts/        ← Template prompts for distribution
```

### Version Control Integration

```xml
<version_control priority="HIGH">
<change_tracking>
  - Meaningful change identification
  - Commit message standards
  - Version tagging protocols
</change_tracking>
<collaboration_patterns>
  - Multi-user editing guidelines
  - Conflict resolution procedures
  - Review and approval processes
</collaboration_patterns>
</version_control>
```

### Migration Strategies

```xml
<migration_guidelines priority="MEDIUM">
<incremental_adoption>
  - Phase-based implementation
  - Backward compatibility preservation
  - Progressive enhancement patterns
</incremental_adoption>
<validation_during_migration>
  - Before/after comparison testing
  - Functionality verification protocols
  - Performance impact assessment
</validation_during_migration>
</migration_guidelines>
```

## Quality Assurance Checklist

### Pre-Implementation Validation

```xml
<implementation_checklist>
☐ Clear objective definition
☐ Scope and boundary specification
☐ Success criteria establishment
☐ Failure mode identification
☐ Resource requirement assessment
☐ Integration point verification
☐ Testing strategy development
☐ Documentation completeness
</implementation_checklist>
```

### Post-Implementation Verification

```xml
<verification_checklist>
☐ Functional requirement satisfaction
☐ Performance standard compliance
☐ Error handling effectiveness
☐ Integration compatibility
☐ Documentation accuracy
☐ User experience quality
☐ Maintenance procedure clarity
☐ Migration pathway validation
</verification_checklist>
```

### Ongoing Maintenance

```xml
<maintenance_patterns priority="LOW">
<regular_review>
  - Performance monitoring
  - User feedback incorporation
  - Technology update adaptation
</regular_review>
<continuous_improvement>
  - Optimization opportunity identification
  - Enhancement implementation
  - Best practice evolution
</continuous_improvement>
</maintenance_patterns>
```

---

*These guidelines are optimized for Claude models and focus on AI instruction effectiveness rather than human readability. They extract successful patterns from proven implementations and provide frameworks for creating robust, maintainable AI instruction systems.*