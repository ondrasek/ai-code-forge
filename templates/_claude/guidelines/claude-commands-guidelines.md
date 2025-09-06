# Claude Code Slash Command Guidelines

<overview priority="HIGH">
<definition>Comprehensive guidelines, rules, and best practices for defining and implementing slash commands in Claude Code</definition>
<enforcement>ALL command definitions MUST follow these guidelines for proper Claude Code integration</enforcement>
<fundamental_principle priority="CRITICAL">Command definitions are meant for Claude Code. They are instructions, NOT human readable documentation</fundamental_principle>
</overview>

<official_requirements priority="CRITICAL">
<file_structure priority="CRITICAL">
  <location>ALL slash commands MUST be stored in .claude/commands/ directory</location>
  <format>Commands are Markdown (.md) files</format>
  <naming>File name determines command name (without .md extension)</naming>
  <discovery>Commands are automatically discovered by Claude Code</discovery>
  <enforcement>NEVER place command files in any other directory</enforcement>
</file_structure>

<command_file_structure priority="CRITICAL">
  <template>
    ---
    description: Brief command description.
    argument-hint: Expected argument format.
    allowed-tools: Tool1, Tool2(tool arguments), Tool3
    ---

    # Command Title

    Brief description of what the command does.

    ## Instructions

    Detailed step-by-step instructions for Claude to follow.
    Use $ARGUMENTS to reference passed parameters.

    1. First step with $ARGUMENTS
    2. Second step
    3. Final step
  </template>
  <validation>✅ Frontmatter present, ✅ Title section included, ✅ Instructions section detailed</validation>
</command_file_structure>
</official_requirements>

<frontmatter_configuration priority="HIGH">
<supported_fields priority="HIGH">
  <field name="description" priority="HIGH">
    <definition>Brief command explanation for help text</definition>
    <enforcement>MUST be concise and action-oriented</enforcement>
  </field>
  <field name="argument_hint" priority="LOW">
    <definition>Describe expected arguments for user guidance when absolutely necessary</definition>
    <enforcement>AVOID unless arguments are critical - prefer autonomous command design</enforcement>
    <constraint>ONLY include when essential parameters cannot be determined by agent delegation</constraint>
  </field>
  <field name="allowed_tools" priority="HIGH">
    <definition>Array of permitted tools for command execution</definition>
    <enforcement>MUST specify all required tools with parameters</enforcement>
  </field>
</supported_fields>

  <example_frontmatter priority="MEDIUM">
  <template>
    ---
    description: Execute autonomous git workflow with intelligent agent delegation.
    allowed-tools: Task
    ---
  </template>
  <validation>✅ Clear description, ✅ Autonomous design, ✅ Agent delegation via Task tool</validation>
</example_frontmatter>
</frontmatter_configuration>

<naming_conventions priority="HIGH">
<file_naming_rules priority="HIGH">
  <rule>Use lowercase with hyphens for multi-word commands</rule>
  <rule>Be descriptive and action-oriented</rule>
  <rule>Avoid spaces (converted to underscores in normalization)</rule>
  <enforcement>MUST follow kebab-case naming pattern</enforcement>
  
  <examples>
    <correct>git-workflow.md</correct>
    <correct>test-runner.md</correct>
    <correct>deploy-production.md</correct>
  </examples>
</file_naming_rules>

<namespace_implementation priority="MEDIUM">
  <structure>Use subdirectories for logical grouping</structure>
  <format>namespace/command-name.md</format>
  
  <examples>
    <namespace>git/commit.md</namespace>
    <namespace>testing/unit-tests.md</namespace>
    <namespace>deployment/staging.md</namespace>
  </examples>
  
  <validation>✅ Logical grouping, ✅ Consistent namespace structure</validation>
</namespace_implementation>
</naming_conventions>

<parameter_handling priority="HIGH">
<autonomous_design_principle priority="CRITICAL">
  <definition>Commands MUST be primarily autonomous, relying on agent delegation rather than user arguments</definition>
  <enforcement>USE arguments sparingly - only for absolutely essential parameters</enforcement>
  <approach>Commands should determine behavior intelligently and delegate to specialized agents</approach>
  <essential_logic>Include only critical orchestration logic - avoid complex argument-driven branching</essential_logic>
</autonomous_design_principle>

<arguments_keyword priority="MEDIUM">
  <definition>Use $ARGUMENTS to reference passed parameters when absolutely necessary</definition>
  <constraint>MINIMIZE argument dependency - prefer autonomous agent delegation</constraint>
  <essential_use>Reserve for critical parameters that cannot be determined by agents</essential_use>
  <example>Task(agent): Execute with context determination rather than /command --complex-args</example>
  <enforcement>ONLY use $ARGUMENTS when agent delegation cannot determine behavior</enforcement>
</arguments_keyword>

<argument_minimization priority="HIGH">
  <principle>Commands should be autonomous and self-determining</principle>
  <delegation>Delegate complex logic and decision-making to appropriate specialized agents</delegation>
  <orchestration>Focus command logic on agent coordination, not argument processing</orchestration>
  <validation>Agent-driven validation preferred over argument-based validation</validation>
  <guidance>Design commands to work effectively without arguments whenever possible</guidance>
</argument_minimization>
</parameter_handling>

<best_practices priority="HIGH">
<command_design priority="HIGH">
  <principle name="single_responsibility" priority="HIGH">
    <definition>Each command should have one clear purpose</definition>
    <enforcement>AVOID multi-purpose commands that combine unrelated functionality</enforcement>
  </principle>
  
  <principle name="clear_documentation" priority="MEDIUM">
    <definition>Include comprehensive descriptions and examples</definition>
    <enforcement>MUST provide step-by-step instructions for Claude</enforcement>
  </principle>
  
  <principle name="error_handling" priority="HIGH">
    <definition>Anticipate and handle common failure scenarios</definition>
    <enforcement>MUST include error recovery instructions</enforcement>
  </principle>
  
  <principle name="user_feedback" priority="MEDIUM">
    <definition>Provide clear status and progress information</definition>
    <enforcement>SHOULD include progress indicators and completion confirmations</enforcement>
  </principle>
  
  <principle name="idempotency" priority="HIGH">
    <definition>Commands should be safe to run multiple times</definition>
    <enforcement>MUST design commands to handle repeated execution gracefully</enforcement>
  </principle>
</command_design>

<content_structure priority="MEDIUM">
  <section name="title" priority="HIGH">Clear, descriptive command title</section>
  <section name="description" priority="HIGH">Brief explanation of command purpose</section>
  <section name="instructions" priority="CRITICAL">Step-by-step implementation details for Claude execution</section>
  <validation>✅ All sections present, ✅ Instructions detailed and actionable</validation>
</content_structure>
</best_practices>

<implementation_guidelines priority="HIGH">
<command_execution_flow priority="HIGH">
  <step order="1">User invokes command with /command-name parameters</step>
  <step order="2">Claude Code loads command definition from .claude/commands/</step>
  <step order="3">Frontmatter processed for tool permissions and guidance</step>
  <step order="4">$ARGUMENTS substituted with user parameters</step>
  <step order="5">Claude executes instructions using allowed tools</step>
  <validation>✅ Flow understood, ✅ Tool restrictions respected</validation>
</command_execution_flow>

<tool_restrictions priority="CRITICAL">
  <enforcement>Commands can ONLY use tools specified in allowed-tools frontmatter</enforcement>
  <specification>Tools must be listed with their parameter patterns</specification>
  <security>Tool restrictions prevent unauthorized system access</security>
  <validation>✅ All required tools specified, ✅ Parameter patterns included</validation>
</tool_restrictions>
</implementation_guidelines>

<optimization_principles priority="HIGH">
<claude_instruction_optimization priority="HIGH">
  <principle>Commands are AI instruction sets, not human documentation</principle>
  <approach>Write for Claude's interpretation and execution</approach>
  <language>Use imperative, action-oriented language</language>
  <structure>Organize instructions for sequential Claude execution</structure>
  <enforcement>MUST optimize for AI comprehension over human readability</enforcement>
</claude_instruction_optimization>

<autonomous_command_architecture priority="CRITICAL">
  <principle>Commands MUST delegate complex logic to specialized agents</principle>
  <orchestration>Focus on agent coordination rather than direct implementation</orchestration>
  <intelligence>Let agents determine optimal approaches rather than hardcoding logic</intelligence>
  <simplicity>Keep command logic minimal - essential orchestration only</simplicity>
  <enforcement>AVOID complex branching, validation, or processing within commands</enforcement>
</autonomous_command_architecture>

<performance_considerations priority="MEDIUM">
  <consideration>Delegate to agents instead of multiple tool invocations</consideration>
  <consideration>Use Task tool for complex operations requiring specialized expertise</consideration>
  <consideration>Provide agent context rather than detailed command instructions</consideration>
  <consideration>Include completion indicators through agent reporting</consideration>
</performance_considerations>
</optimization_principles>

<validation_framework priority="HIGH">
<command_validation_checklist priority="HIGH">
  <validation name="frontmatter_complete">✅ All required frontmatter fields present</validation>
  <validation name="tools_specified">✅ All necessary tools listed in allowed-tools</validation>
  <validation name="instructions_detailed">✅ Step-by-step instructions provided for Claude</validation>
  <validation name="arguments_handled">✅ $ARGUMENTS usage implemented where needed</validation>
  <validation name="error_handling">✅ Common failure scenarios addressed</validation>
  <validation name="single_purpose">✅ Command maintains single responsibility</validation>
</command_validation_checklist>

<testing_approach priority="MEDIUM">
  <test>Verify command discovery in Claude Code interface</test>
  <test>Test argument passing and $ARGUMENTS substitution</test>
  <test>Validate tool restrictions and permissions</test>
  <test>Confirm error handling and recovery mechanisms</test>
  <test>Verify idempotency with repeated executions</test>
</testing_approach>
</validation_framework>

<operational_enforcement priority="CRITICAL">
<mandatory_practices priority="CRITICAL">
  <practice>NEVER create commands outside .claude/commands/ directory</practice>
  <practice>ALWAYS include proper frontmatter with allowed-tools</practice>
  <practice>MUST write instructions for Claude execution, not human reading</practice>
  <practice>ALWAYS validate command functionality before deployment</practice>
  <practice>MUST maintain single responsibility per command</practice>
</mandatory_practices>
</operational_enforcement>
EOF < /dev/null