# GitHub Labels Guidelines

## Overview

These guidelines provide comprehensive frameworks for standardized GitHub label management optimized for AI-driven repository workflows. Based on GitHub's official standards and community best practices, these guidelines focus on creating effective label systems for AI agents and human collaborators (not human-readable documentation - these are AI instructions).

## Core Principles

### 1. Structured Label Management

Use GitHub's official space-delimited format with AI-optimized categorization patterns:

```xml
<label_structure priority="CRITICAL">
<definition>Systematic label organization for AI workflow optimization</definition>
<enforcement>ALWAYS use space-delimited format without prefixes</enforcement>
<examples>
  ✅ "good first issue" - GitHub standard format
  ✅ "help wanted" - Community engagement
  ✅ "human feedback needed" - AI-human collaboration
  ❌ "good-first-issue" - Invalid hyphenation
  ❌ "type: feat" - Prohibited prefix system
</examples>
<validation>Labels must align with GitHub ecosystem standards</validation>
</label_structure>
```

### 2. Priority-Based Label Hierarchies

Implement clear priority levels for workflow optimization:

- **CRITICAL**: System-breaking issues requiring immediate attention
- **HIGH**: Important workflow labels affecting user experience  
- **MEDIUM**: Process optimization and community engagement
- **LOW**: Administrative and historical tracking labels

### 3. Explicit Label Enforcement

Use dedicated enforcement mechanisms for consistent application:

```xml
<enforcement>ALWAYS apply one type label to every issue</enforcement>
<enforcement>NEVER use prefix notation in label names</enforcement>
<enforcement>MUST USE priority labels for workflow coordination</enforcement>
```

### 4. Context Separation

Organize labels into distinct categories to prevent overlap:

```xml
<label_categories>
  <type_labels>Feature classification and development tracking</type_labels>
  <priority_labels>Workflow urgency and resource allocation</priority_labels>
  <workflow_labels>Process coordination and automation</workflow_labels>
  <community_labels>Engagement and contribution management</community_labels>
</label_categories>
```

## Label Definition Framework

### Standard Label Structure

```xml
<label_definition>
<role>Core classification for issue and pull request workflow management</role>
<capabilities>
  - Type classification (feat, bug, docs, etc.)
  - Priority assignment (critical, high priority, nice to have)
  - Workflow coordination (dependencies, breaking change)
  - Community engagement (good first issue, help wanted)
</capabilities>
<restrictions>
  - No prefix notation allowed
  - Maximum one type label per issue
  - Must follow GitHub space-delimited format
</restrictions>
<coordination>
  - AI agent label application patterns
  - Automated workflow triggers
  - Human reviewer assignment rules
</coordination>
<output_format>
  - Space-delimited multi-word labels
  - Consistent color coding by category
  - GitHub API compatible naming
</output_format>
</label_definition>
```

### Label Boundary Definition

```xml
<label_boundaries priority="HIGH">
<trigger_patterns>
  - "new feature request" → apply "feat" label
  - "bug report" → apply "bug" + priority label
  - "security issue" → apply "security" + "critical"
  - "documentation needed" → apply "docs" + "help wanted"
</trigger_patterns>
<capability_scope>
  - Type labels: Classify development work categories
  - Priority labels: Determine workflow urgency
  - Workflow labels: Coordinate process dependencies
  - Community labels: Facilitate external contributions
</capability_scope>
<handoff_protocols>
  - Automated labeling via GitHub Actions
  - Manual review for priority assignment
  - Community moderator approval for resolution labels
</handoff_protocols>
</label_boundaries>
```

### Workflow Labels

Process and coordination support labels:

```xml
<workflow_labels priority="MEDIUM">
<coordination>
  - dependencies: Requires completion of other issues first
  - human feedback needed: Agent requires human review and guidance
  - breaking change: Changes that may break existing functionality
  - migrated from specs: Historical tracking for legacy migration
</coordination>
<usage_guidelines>
  - Apply "dependencies" when issues block each other
  - Use "human feedback needed" for agent-human collaboration points
  - Mark "breaking change" for API changes or major modifications
  - Keep "migrated from specs" for historical context only
</usage_guidelines>
</workflow_labels>
```

### Community Labels

GitHub standard labels for community engagement:

```xml
<community_labels priority="MEDIUM">
<engagement>
  - good first issue: Beginner-friendly contribution opportunities
  - help wanted: Community contributions welcome
  - question: Requests for information or clarification
</engagement>
<resolution>
  - duplicate: Already exists or covered elsewhere
  - invalid: Invalid request or incorrect information
  - wontfix: Will not be implemented or fixed
</resolution>
<enforcement>Use GitHub's exact standard labels for maximum compatibility</enforcement>
</community_labels>
```

## Implementation Protocol

### Label Creation Standards

```xml
<creation_protocol priority="HIGH">
<naming_validation>
  ☐ Uses space-delimited format
  ☐ No prefix namespacing
  ☐ Clear, descriptive purpose
  ☐ Aligns with defined categories
  ☐ No semantic overlap with existing labels
</naming_validation>
<color_scheme>
  - Type labels: Distinct colors by functional area
  - Priority labels: Red spectrum (critical → orange → blue)
  - Workflow labels: Yellow/green spectrum for process
  - Community labels: GitHub default colors
</color_scheme>
</creation_protocol>
```

### Migration Strategy

```xml
<migration_approach priority="MEDIUM">
<phase_implementation>
  1. Audit current labels against new standards
  2. Create missing standardized labels
  3. Bulk relabel existing issues following new conventions
  4. Remove deprecated and redundant labels
  5. Update automation and workflows
</phase_implementation>
<change_tracking>
  - Document all label changes
  - Preserve historical context where needed
  - Maintain issue history integrity
</change_tracking>
</migration_approach>
```

### Quality Assurance

```xml
<quality_validation priority="MEDIUM">
<consistency_checking>
  ☐ All labels follow space-delimited naming
  ☐ No prefix namespacing applied
  ☐ Semantic clarity maintained across categories
  ☐ Priority hierarchy properly structured
  ☐ Community labels match GitHub standards
</consistency_checking>
<maintenance_procedures>
  - Regular label usage audit
  - Consistency verification
  - Community feedback integration
  - Evolution based on workflow needs
</maintenance_procedures>
</quality_validation>
```

## Label Application Patterns

### Action-Oriented Label Structure

```xml
<label_application>
<name>Issue Classification System</name>
<purpose>Systematic label assignment for AI-driven workflow optimization</purpose>
<parameters>
  <required>
    - type_label: Primary classification (feat, bug, docs, etc.)
    - context_validation: Issue content analysis for appropriate labeling
  </required>
  <optional>
    - priority_label: Workflow urgency (critical, high priority, nice to have)
    - workflow_labels: Process coordination (dependencies, breaking change)
    - community_labels: Engagement facilitation (good first issue, help wanted)
  </optional>
</parameters>
<validation_chain>
  1. Content analysis for type classification
  2. Impact assessment for priority assignment
  3. Dependency check for workflow coordination
  4. Contribution opportunity evaluation
</validation_chain>
<execution_pattern>
  1. Parse issue content and context
  2. Apply primary type label
  3. Assess and assign priority if applicable
  4. Add workflow coordination labels
  5. Include community engagement labels
</execution_pattern>
<error_handling>
  - Multiple type labels → consolidate to primary type
  - Missing priority on critical issues → escalate for review
  - Conflicting workflow labels → human moderator resolution
</error_handling>
</label_application>
```

### Integration Patterns

```xml
<integration_support priority="LOW">
<automation_compatibility>
  - GitHub Actions workflows
  - Issue template integration
  - Project board filtering
  - Search and discovery features
</automation_compatibility>
<tooling_integration>
  - Compatible with gh CLI commands
  - Supports automated labeling rules
  - Works with third-party GitHub tools
  - Maintains API compatibility
</tooling_integration>
</integration_support>
```

## Label Validation Frameworks

### Input→Process→Output Verification

```xml
<validation_framework priority="HIGH">
<input_validation>
  - Issue content completeness check
  - Label category compatibility verification
  - GitHub API format compliance
  - Existing label conflict detection
</input_validation>
<process_validation>
  - Type classification accuracy
  - Priority assignment appropriateness
  - Workflow coordination completeness
  - Community engagement opportunity assessment
</process_validation>
<output_validation>
  - Space-delimited format verification
  - Color scheme consistency checking
  - GitHub ecosystem compatibility
  - Automation trigger functionality
</output_validation>
</validation_framework>
```

### Self-Verification Protocols

```xml
<self_verification priority="MEDIUM">
<verification_checklist>
  ☐ All required type labels applied
  ☐ Priority assignments align with impact
  ☐ Workflow coordination labels functional
  ☐ Community labels facilitate engagement
  ☐ No prefix notation used
  ☐ Space-delimited format maintained
</verification_checklist>
<verification_automation>
  - GitHub Actions label validation
  - Automated consistency checking
  - Community feedback integration
</verification_automation>
</self_verification>
```

## Claude-Specific Optimizations

### Context Window Efficiency

```xml
<context_optimization priority="HIGH">
<information_density>
  - Hierarchical label organization
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

### Few-Shot Learning Optimization

```xml
<example_patterns priority="MEDIUM">
<pattern_demonstration>
  ✅ "feat" + "high priority" + "good first issue" - New feature request
  ✅ "enhancement" + "nice to have" - Existing feature improvement
  ✅ "security" + "critical" + "breaking change" - Security vulnerability
  ❌ "type: feat" + "priority: critical" - Prohibited prefix system
</pattern_demonstration>
<context_examples>
  - Scenario 1: Bug report → "bug" + priority + workflow labels
  - Scenario 2: Feature request → "feat" + priority + community labels
  - Edge Case: Security issue → "security" + "critical" + "breaking change"
</context_examples>
<learning_reinforcement>
  - Pattern consistency emphasis
  - Key decision point highlighting
  - Success criteria demonstration
</learning_reinforcement>
</example_patterns>
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

*These guidelines optimize GitHub label management for ai-code-forge repository workflows while maintaining GitHub ecosystem compatibility and community standards compliance.*