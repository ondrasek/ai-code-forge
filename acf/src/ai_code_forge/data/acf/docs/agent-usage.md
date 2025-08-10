# Agent Usage Guidelines

Claude Code MUST PROACTIVELY use ALL appropriate agents for better results:

## Base Agents (Most Requests)

### research
- **Purpose**: Gather current information, best practices, documentation
- **Use for**: Any request requiring external knowledge or current practices
- **Integration**: Often first agent in workflow, feeds context to others

### criticism
- **Purpose**: Challenge assumptions, identify risks, provide balanced perspective
- **Use for**: Major decisions, architectural choices, before finalizing recommendations
- **Integration**: Usually last in analytical workflows for validation

## Context-Specific Agent Selection

### Code Analysis Tasks
- **patterns**: Detect repeated code, anti-patterns, refactoring opportunities
- **principles**: Apply SOLID, DRY, KISS principles to architecture decisions
- **Use together for**: Code reviews, refactoring planning, architecture evaluation

### Problem Investigation
- **hypothesis**: Form theories, design experiments, systematic debugging
- **completer**: Find missing error handlers, TODOs, incomplete implementations
- **Use for**: Debugging issues, finding gaps, ensuring completeness

### Design and Planning
- **explorer**: Generate multiple solution alternatives, compare approaches
- **constraints**: Handle complex requirements, conflicting needs, trade-offs
- **conflicts**: Mediate when different approaches conflict
- **Use for**: Architecture decisions, complex requirements, design choices

### Specialized Domains
- **generator**: Create code generators, templates, DSLs for repetitive patterns
- **invariants**: Design type systems, state machines, prevent invalid states
- **time**: Analyze git history, predict evolution, understand system changes
- **connector**: Find cross-domain solutions, creative approaches
- **axioms**: First-principles reasoning, fundamental understanding

### Technology-Specific
- **prompter**: AI agent development, LangChain, CrewAI integration

### Maintenance
- **docs**: Update documentation after code changes, maintain consistency
- **whisper**: Apply micro-improvements, fix typos, enhance code quality

## Smart Agent Workflows

### Simple Information Request
- **Agents**: `research` only
- **Example**: "What's the latest version of React?"
- **Rationale**: Straightforward lookup, no analysis needed

### Code Review or Refactoring
- **Agents**: `research` + `patterns` + `principles` + `criticism`
- **Flow**: Research best practices → Find patterns → Apply principles → Validate approach
- **Example**: "Review this authentication module"

### Debugging Investigation
- **Agents**: `research` + `hypothesis` + `criticism`
- **Flow**: Research known issues → Form/test theories → Validate solution
- **Example**: "Why is this API endpoint returning 500 errors?"

### Architecture Planning
- **Agents**: `research` + `explorer` + `constraints` + `principles` + `criticism`
- **Flow**: Research approaches → Generate alternatives → Handle constraints → Apply principles → Critical review
- **Example**: "Design a microservices architecture for this system"

### Feature Implementation
- **Agents**: `research` + `patterns` + `completer` + `docs`
- **Flow**: Research implementation patterns → Check for existing patterns → Ensure completeness → Update docs
- **Example**: "Add caching to the user service"

## Agent Selection Logic

### Context Detection
- **Code files mentioned** → Add `patterns` + `principles`
- **Error messages/debugging** → Add `hypothesis`
- **Architecture/design questions** → Add `explorer` + `constraints`
- **"What's missing" or TODOs** → Add `completer`
- **Major decisions** → Add `criticism`
- **Code changes made** → Add `docs`

### Technology Detection
- **Agent/prompt engineering context** → Add `prompter`
- **Type safety/state machines** → Add `invariants`
- **Historical analysis needed** → Add `time`

### User Intent Detection
- **"Quick question"** → Minimal agents (`research` only)
- **"Deep analysis"** → Comprehensive agent set
- **"Just check X"** → Specific agent focus
- **"Don't use agents"** → No agent invocation

## Inter-Agent Communication
- Agents MUST use Task tool to invoke other agents when needed
- Pass specific context and expected outputs
- Multiple agents can work in parallel when appropriate
- Agents MUST build on each other's findings

## Quality Guidelines
1. **Relevance over completeness** - Use agents that add value
2. **Progressive enhancement** - Start minimal, add based on findings
3. **User experience first** - Don't over-analyze simple requests
4. **Fail gracefully** - Continue if individual agents fail
5. **Time awareness** - Respect user's need for timely responses