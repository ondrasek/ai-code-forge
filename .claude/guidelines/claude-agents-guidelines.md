# Agent Creation Principles

<overview priority="CRITICAL">
<definition>Empirically-derived principles for determining when agents provide measurable value over inline processing</definition>
<enforcement>ALL agent creation decisions MUST be validated against these principles before implementation</enforcement>
</overview>

<context_and_scope priority="CRITICAL">
<critical_note priority="CRITICAL">
  <definition>These principles apply to agent creation decisions and system architecture</definition>
  <constraint>They do NOT override CLAUDE.md's operational mandates for parallel agent usage in existing workflows</constraint>
</critical_note>

<principle_application priority="HIGH">
  <agent_creation>Apply all principles rigorously - prefer consolidation over new agents</agent_creation>
  <agent_usage>Follow CLAUDE.md aggressive parallel coordination for optimal analysis</agent_usage>
  <system_evolution>Balance principle-driven design with operational performance requirements</system_evolution>
</principle_application>

<conflict_resolution priority="CRITICAL">
  <rule>When principles conflict with CLAUDE.md operational mandates, operational requirements take precedence</rule>
  <scope>These principles guide long-term system design, not immediate execution patterns</scope>
</conflict_resolution>
</context_and_scope>

<core_principles priority="CRITICAL">
<principle name="context_window_decluttering" priority="CRITICAL" order="1">
  <definition>The fundamental value of dedicated sub-agents is maintaining a clean, focused main context window</definition>
  
  <purpose>
    <primary>Prevent main context pollution with lengthy intermediate analysis steps</primary>
    <pollution_sources>
      <source>Multi-file code examination artifacts</source>
      <source>Complex reasoning chains that obscure primary task focus</source>
      <source>Repetitive processing output that adds noise without immediate value</source>
      <source>Detailed technical research that supports but doesn't directly answer user queries</source>
    </pollution_sources>
  </purpose>

  <critical_requirements priority="CRITICAL">
    <requirement>Agent tasks MUST remove clutter from main context - not just organize it differently</requirement>
    <requirement>Agent outputs MUST be concise summaries - detailed work stays in agent context</requirement>
    <requirement>Multiple tool calls and file analysis MUST happen in agent context - never in main</requirement>
    <requirement>Intermediate reasoning MUST be contained - main context sees only conclusions</requirement>
    <requirement>Complex research MUST be synthesized - raw information gathering stays isolated</requirement>
  </critical_requirements>

  <evidence_of_success>
    <criteria>Main context conversations remain focused on user intent rather than processing artifacts</criteria>
    <outcome>Users see clean, actionable results without intermediate computational noise</outcome>
  </evidence_of_success>

  <context_pollution_anti_patterns>
    <anti_pattern>Running multi-file analysis directly in main context</anti_pattern>
    <anti_pattern>Showing detailed reasoning chains for simple requests</anti_pattern>
    <anti_pattern>Displaying raw tool output instead of synthesized insights</anti_pattern>
    <anti_pattern>Performing iterative refinement cycles visibly in main context</anti_pattern>
    <anti_pattern>Presenting unsorted research results requiring user filtering</anti_pattern>
  </context_pollution_anti_patterns>
</principle>

<principle name="capability_uniqueness" priority="CRITICAL" order="1a">
  <definition>Each agent must provide distinct, non-overlapping value to the system</definition>
  <core_principle>Agent specialization value diminishes when coordination overhead exceeds analytical benefits</core_principle>
  <optimization>The system optimizes for unique contributions rather than exhaustive coverage</optimization>

  <uniqueness_guidelines priority="HIGH">
    <guideline name="domain_cohesion">Natural problem domains should not be artificially split across multiple agents</guideline>
    <guideline name="tool_synergy">Agents using identical tool combinations for similar outcomes indicate consolidation opportunity</guideline>
    <guideline name="capability_boundaries">Each agent should own a distinct analytical perspective or computational approach</guideline>
    <guideline name="authority_assignment">Single agent should be authoritative source for each domain expertise</guideline>
  </uniqueness_guidelines>

  <system_optimization_principle>Minimize total agent count while maximizing unique value contribution. Quality of specialization matters more than quantity of specialists</system_optimization_principle>
</principle>

<principle name="overhead_justification" priority="HIGH" order="2">
  <definition>Create agents only when the complexity reduction in main context exceeds the overhead of agent creation and maintenance</definition>
  
  <measurable_criteria priority="HIGH">
    <criterion>Task generates >50 lines of intermediate analysis that pollutes main context</criterion>
    <criterion>Process requires >3 sequential tool invocations with complex state management</criterion>
    <criterion>Logic gets reused across >3 different scenarios</criterion>
  </measurable_criteria>
  
  <evidence_requirement>Document specific overhead reduction achieved</evidence_requirement>
</principle>

<principle name="prompt_specialization" priority="MEDIUM" order="3">
  <definition>Agents provide specialized prompting strategies for specific analysis patterns, not magical cognitive differences</definition>
  
  <practical_examples>
    <example>patterns agent: Optimized prompting for systematic code pattern detection</example>
    <example>critic agent: Prompting designed to generate contrarian analysis</example>
    <example>completer agent: Prompting focused on finding gaps and missing implementations</example>
  </practical_examples>
  
  <reality_check>All agents use the same language model with different instructions</reality_check>
</principle>

<principle name="context_boundary_management" priority="MEDIUM" order="4">
  <definition>Agents should handle tasks that have clear input/output boundaries and don't require ongoing main context interaction</definition>
  
  <good_boundaries>
    <boundary>Input: File paths or code snippets</boundary>
    <boundary>Process: Self-contained analysis</boundary>
    <boundary>Output: Structured recommendations</boundary>
  </good_boundaries>
  
  <bad_boundaries>
    <boundary>Requires iterative clarification from main context</boundary>
    <boundary>Needs access to ongoing conversation state</boundary>
    <boundary>Produces outputs requiring main context interpretation</boundary>
  </bad_boundaries>
</principle>

<principle name="computational_tasks_focus" priority="HIGH" order="5">
  <definition>Agents should embody computational tasks, thinking patterns, paradigms, and analytical perspectives - not human organizational roles</definition>
  
  <correct_approaches priority="HIGH">
    <approach>Computational tasks: patterns - Systematically detect code duplication across files</approach>
    <approach>Context window isolation: researcher - Gather information without cluttering main context</approach>
    <approach>Thinking patterns: critic - Apply contrarian analysis methodology</approach>
    <approach>Paradigms: axioms - Derive solutions from first principles reasoning</approach>
    <approach>Perspectives: constraints - View problems through limitation/trade-off lens</approach>
    <approach>Points of view: hypothesis - Approach debugging through systematic theory formation</approach>
  </correct_approaches>
  
  <incorrect_approaches priority="CRITICAL">
    <anti_pattern>Human roles: project-manager, team-lead, stakeholder, scrum-master</anti_pattern>
    <anti_pattern>Social dynamics: mediator, facilitator, coordinator</anti_pattern>
    <anti_pattern>Organizational positions: architect, senior-developer, tech-lead</anti_pattern>
  </incorrect_approaches>
  
  <rationale>Agents excel at computational processing, systematic analysis patterns, and specialized analytical perspectives. They provide value through focused thinking approaches and context isolation - not at replicating human social dynamics or organizational responsibilities.</rationale>
</principle>

<principle name="coordination_efficiency" priority="HIGH" order="6">
  <definition>System performance emerges from agent interaction patterns, not individual agent capabilities</definition>
  <core_principle>The value of agent specialization must exceed the cost of coordination</core_principle>
  
  <efficiency_guidelines priority="HIGH">
    <guideline>Self-Sufficiency: Agents requiring multiple other agents for basic functionality indicate poor boundary design</guideline>
    <guideline>Proportional Complexity: Agent sophistication should match task complexity requirements</guideline>
    <guideline>Resource Awareness: Agent selection should consider computational cost relative to analytical value</guideline>
    <guideline>Execution Patterns: Different task types warrant different coordination approaches</guideline>
  </efficiency_guidelines>
  
  <scalability_principle>Agent systems have natural complexity thresholds. Beyond these thresholds, coordination overhead degrades rather than enhances system performance</scalability_principle>
</principle>

<principle name="command_agent_balance" priority="CRITICAL" order="7">
  <definition>Specialization should favor commands over agents due to context window economics</definition>
  <core_principle>Commands are selected by users and have zero context window overhead, while agents are selected by Claude Code and consume context resources</core_principle>
  
  <balance_guidelines priority="CRITICAL">
    <guideline>User-Directed Specialization: When users need specific workflows or specialized analysis, create commands</guideline>
    <guideline>System-Directed Generalization: Agents should handle broad analytical patterns that Claude Code can automatically select</guideline>
    <guideline>Context Efficiency: Commands avoid the coordination overhead and context fragmentation of multi-agent workflows</guideline>
    <guideline>Selection Clarity: User command selection eliminates agent boundary ambiguity and selection errors</guideline>
  </balance_guidelines>
  
  <specialization_hierarchy>Commands > Agents > Agent Combinations. Move down the hierarchy only when the previous level cannot adequately address the need</specialization_hierarchy>
</principle>
</core_principles>

<decision_framework priority="CRITICAL">
<agent_creation_checklist priority="CRITICAL">
  <prerequisite name="command_first_evaluation" priority="CRITICAL">
    <check>Specialization need cannot be addressed through user-selected commands</check>
    <check>Requires Claude Code automatic selection rather than user direction</check>
    <check>Task benefits from system-directed rather than user-directed specialization</check>
    <check>Cannot be efficiently implemented as specialized command workflow</check>
  </prerequisite>

  <primary_justification name="context_window_decluttering" priority="CRITICAL">
    <check>Task currently pollutes main context with >50 lines of intermediate processing</check>
    <check>Multiple file reads/analysis would clutter main context with technical artifacts</check>
    <check>Complex reasoning chains would obscure primary user intent in main context</check>
  </primary_justification>

  <secondary_validations priority="HIGH">
    <validation name="uniqueness_validation">Agent provides distinct value not available through existing agents</validation>
    <validation name="overhead_justification">Complexity reduction exceeds creation and maintenance overhead</validation>
    <validation name="boundary_clarity">Clear input/output specifications without main context dependency</validation>
    <validation name="computational_focus">Embodies computational task or thinking pattern, not human organizational role</validation>
  </secondary_validations>
</agent_creation_checklist>

<elimination_criteria priority="HIGH">
  <red_flags>
    <flag>Context pollution: Agent use still results in cluttered main context conversations</flag>
    <flag>Failed decluttering: Complex processing remains visible in main context despite agent use</flag>
    <flag>Low utilization: <5 invocations per month</flag>
    <flag>High maintenance: Frequent specification updates required</flag>
    <flag>Poor boundaries: Consistent need for main context clarification</flag>
    <flag>Redundant function: Capabilities overlap significantly with other agents</flag>
  </red_flags>

  <principle_based_elimination priority="CRITICAL">
    <criterion>Uniqueness failure: Agent provides nearly identical functionality to existing agents</criterion>
    <criterion>Coordination inefficiency: Agent requires extensive coordination for basic domain tasks</criterion>
    <criterion>System degradation: Agent use increases system complexity without proportional analytical value</criterion>
    <criterion>Domain incoherence: Agent handles artificially narrow slice of broader cohesive domain</criterion>
    <criterion>Redundant approaches: Uses identical methodologies as other agents for overlapping outcomes</criterion>
    <criterion>Selection ambiguity: Unclear boundaries create confusion in agent selection decisions</criterion>
  </principle_based_elimination>
</elimination_criteria>
</decision_framework>

<implementation_guidelines priority="HIGH">
<agent_specification_requirements priority="HIGH">
  <requirement name="context_decluttering_justification">Specific evidence of how agent keeps main context clean and focused</requirement>
  <requirement name="complexity_justification">Quantified evidence of context reduction</requirement>
  <requirement name="boundary_definition">Clear input/output specifications</requirement>
  <requirement name="success_criteria">Measurable outcomes that determine agent effectiveness</requirement>
  <requirement name="maintenance_cost">Resources required to keep agent current</requirement>
</agent_specification_requirements>
</implementation_guidelines>

<claude_code_selection_mechanism priority="CRITICAL">
<selection_algorithm priority="CRITICAL">
  <primary_factors>
    <factor priority="CRITICAL">Agent name: Must be descriptive and unique</factor>
    <factor priority="CRITICAL">Description field: Critical for matching user requests to appropriate agents</factor>
    <factor priority="HIGH">Content analysis: Scans description text for relevant keywords and patterns</factor>
  </primary_factors>
</selection_algorithm>

<description_optimization priority="CRITICAL">
  <high_impact_elements priority="CRITICAL">
    <element>Action keywords: "Expert at", "specialized in", "designed for"</element>
    <element>Proactive indicators: "PROACTIVELY", "automatically", "should be used when"</element>
    <element>Mandatory language: "MUST USE", "required for", "essential when"</element>
    <element>Specific triggers: Concrete scenarios that warrant agent invocation</element>
    <element>Capability boundaries: What the agent does and doesn't handle</element>
  </high_impact_elements>

  <proven_patterns priority="HIGH">
    <pattern name="mandatory_usage">
      MUST USE when debugging 'why does this happen', 'strange behavior', 'performance issue', 'it should work but doesn't', or investigating unexpected results
    </pattern>
    <pattern name="proactive_triggers">
      PROACTIVELY use after writing significant code for quality analysis and potential improvements
    </pattern>
    <pattern name="specific_expertise">
      Expert at detecting code patterns, anti-patterns, duplication, and refactoring opportunities across codebases
    </pattern>
  </proven_patterns>

  <selection_priority_keywords priority="CRITICAL">
    <tier_1 priority="CRITICAL">
      <keyword>MUST USE</keyword>
      <keyword>PROACTIVELY</keyword>
      <keyword>ALWAYS use</keyword>
      <keyword>MUST USE AUTOMATICALLY</keyword>
      <keyword>required for</keyword>
      <keyword>should be used when</keyword>
    </tier_1>
    <tier_2 priority="HIGH">
      <keyword>Expert at</keyword>
      <keyword>specialized in</keyword>
      <keyword>designed for</keyword>
      <keyword>Use when</keyword>
    </tier_2>
    <tier_3 priority="MEDIUM">
      <keyword>helps with</keyword>
      <keyword>assists in</keyword>
      <keyword>provides</keyword>
    </tier_3>
  </selection_priority_keywords>

  <mandatory_description_template priority="CRITICAL">
    <template>
      name: [descriptive-name]
      description: "[TIER1_KEYWORD] when [specific_user_context] or [quoted_user_phrases]. Expert at [specific_capability_statement]."
    </template>
    
    <template_components>
      <component>[TIER1_KEYWORD]: MUST USE | PROACTIVELY use | ALWAYS use | MUST USE AUTOMATICALLY</component>
      <component>[specific_user_context]: When user does/asks/mentions X</component>
      <component>[quoted_user_phrases]: 'exact user language', 'common phrases', 'trigger words'</component>
      <component>Expert at [specific_capability_statement]: Clear capability boundary with "Expert at [doing X]"</component>
    </template_components>
  </mandatory_description_template>
</description_optimization>
</claude_code_selection_mechanism>

<operational_constraints priority="CRITICAL">
<timeline_restrictions priority="CRITICAL">
  <constraint>Follow CLAUDE.md NO ARTIFICIAL TIMELINES protocol</constraint>
  <enforcement>NEVER create mock weekly milestones or arbitrary time-based phases in agent analysis or recommendations</enforcement>
</timeline_restrictions>

<current_agent_status priority="MEDIUM">
  <note>Existing agents remain unchanged pending empirical evaluation against these principles</note>
  <future_modifications>Future agent modifications should follow the validation framework and selection optimization guidelines</future_modifications>
</current_agent_status>
</operational_constraints>
EOF < /dev/null