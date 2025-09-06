<claude_operational_rules>
<critical_mandatory_requirements>
MANDATORY RULE 0: Before starting work on every request: identify gaps, risks and offer contrarian point of view. Stop if critical.
MANDATORY RULE 1: Task(git-workflow) to commit and push after EVERY meaningful change.
MANDATORY RULE 2: NEVER create artificial timelines, time estimates or weekly milestones.
MANDATORY RULE 3: Follow file structure locations EXACTLY.
MANDATORY RULE 4: Display ALL rules (0-4) at the start of EVERY response.
</critical_mandatory_requirements>

<git_protocol priority="CRITICAL">
<enforcement>Task(git-workflow) after EVERY meaningful change</enforcement>
<meaningful_change_definition>
  File modifications affecting system behavior, configuration changes, structural updates, or any changes that impact functionality, documentation, or project organization.
</meaningful_change_definition>
</git_protocol>

<output_sanitization priority="CRITICAL">
  - Never assume that user expects or requests estimates, unless explicitly stated.
<forbidden_patterns>
  - "Week 1", "Week 2", "Phase 1 (Week 1)", "Milestone 1", "Milestone 2"
  - "implement in X weeks", "Q1 goals", "monthly milestones"
  - "est. durration 3-4 hours", "est. 2 days"
  - ANY time-based phases unless user explicitly requests
  - ANY time-based estimates in hours, days or man-days
</forbidden_patterns>
<required_format>Priority-based (High/Medium/Low) with dependencies</required_format>
<examples>
  ✅ "High Priority: Update agent descriptions (blocks selection optimization)"
  ❌ "Phase 1 (Week 1): Update agent descriptions"
  ❌ "Next Sprint (Sprint 1): Implement feature 23"
  ❌ "Sprint 2: Update documentation"
  ❌ "Estimated 2-3 hours"
</examples>
</output_sanitization>

<file_structure priority="CRITICAL">
<locations>
  <agents>.claude/agents/foundation  and .claude/agents/specialists (ONLY location for agent definitions)</agents>
  <commands>.claude/commands/ and subdirectories for namespaces, e.g. /issue:create is in .claude/commands/issue/create.md (ONLY location for slash commands)</commands>
  <prompts>templates/prompts/ (template prompts for distribution)</prompts>
  <guidelines>templates/guidelines/ (template guidelines for distribution)</guidelines>
  <github_issues>GitHub Issues in ondrasek/ai-code-forge (specifications managed via GitHub)</github_issues>
  <mcp_servers>mcp-servers/[mcp-name]/ (MCP server source code and integration tests)</mcp_servers>
  <analysis>analysis/[github-issue] where github-issue is a subfolder corresponding to an existing github issue</analysis>
  <scripts>scripts/ and subfolders under scripts/</scripts>
  <cli>{{CLI_DIRECTORY}}/ with source code for the ai-code-forge cli tool</cli>
</locations>
<enforcement>NEVER search elsewhere for these file types</enforcement>
</file_structure>

<specification_management priority="CRITICAL">
<github_issues_protocol>
  <definition>Specifications are detailed planning documents that define requirements, implementation approaches, and project deliverables managed through GitHub Issues in ondrasek/ai-code-forge repository</definition>

  <location>GitHub Issues in ondrasek/ai-code-forge (ABSOLUTE - never use local files)</location>

  <agent_delegation>
    <primary_agent>github-issues-workflow (PROACTIVELY use when user mentions tasks, specs, requirements, or asks 'create issue', 'track progress', 'remember to do')</primary_agent>
    <non_trivial_task_definition>Operations requiring more than 2 tool invocations, affecting multiple files, or involving agent coordination</non_trivial_task_definition>
    <coordination>All specification lifecycle management MUST be delegated to github-issues-workflow agent to prevent context pollution</coordination>
    <commands>Use /issue commands: /issue create, /issue review, /issue cleanup, /issue next</commands>
  </agent_delegation>

  <issue_format>
    <structure>GitHub Issues with proper labels and metadata</structure>
    <naming>Descriptive issue titles derived from specification descriptions</naming>
    <template>
      ## Description
      Clear description of requirements and scope.

      ## Acceptance Criteria
      - [ ] Specific measurable outcome 1
      - [ ] Specific measurable outcome 2

      ## Implementation Notes
      Technical approach, dependencies, constraints.
    </template>
    <labels>
      - Type: feat|fix|docs|refactor|test|chore
      - Priority: priority:high|priority:medium|priority:low
      - Status: status:pending|status:in-progress|status:completed
      - Migration: migrated-from-specs (for historical tracking)
    </labels>
  </issue_format>

  <operational_rules>
    <context_separation>GitHub Issues management happens OFF-CONTEXT via github-issues-workflow agent to keep main conversation clean</context_separation>
    <autonomous_operation>github-issues-workflow handles full issue lifecycle independently without main thread interaction</autonomous_operation>
    <integration_points>
      - Update CHANGELOG.md when issues are completed
      - Coordinate with relevant agents for implementation
      - Support version management workflow through GitHub milestones and issue types
    </integration_points>
    <github_commands>
      - List all issues: gh issue list
      - Create new issue: gh issue create
      - Update issue: gh issue edit
      - Close issue: gh issue close
    </github_commands>
  </operational_rules>

  <namespace_separation>
    <purpose>GitHub Issues are distinct from Claude Code's built-in TodoWrite functionality</purpose>
    <differentiation>
      - GitHub Issues: Detailed planning documents with metadata, managed by specs-analyst via GitHub
      - TodoWrite: Session task tracking for immediate conversation context
    </differentiation>
    <command_usage>Use /issue commands for specification management, TodoWrite tool for session task tracking</command_usage>
  </namespace_separation>
</github_issues_protocol>
</specification_management>

<validation_check>
Before EVERY response, verify:
☐ All 5 display rules (0-4) shown at start
☐ Parallel agents invoked for non-trivial tasks
☐ No artificial timelines in output
☐ File locations correctly referenced
☐ Git operations planned for changes
</validation_check>
</claude_operational_rules>