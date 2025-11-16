# Claude Code Components for AI Code Forge

## Overview

Understanding Claude Code's component architecture is critical for AI Code Forge's modular design. This document explains the technical relationships between Skills, Sub-Agents, and Slash Commands.

## Component Definitions

### Claude Skills Platform
- **Technical Function**: Auto-injected context providers
- **File Structure**: `SKILL.md` with YAML frontmatter + optional resources
- **Activation**: Heuristic pattern matching by Claude's inference engine
- **Content**: 30-50 tokens of domain expertise instructions
- **Platform**: Works across Claude.ai, Claude Code, and API
- **Requirements**: Pro+ plan tiers

**What Skills Contain:**
```
skills/python-linting/
├── SKILL.md          # Instructions + YAML metadata
├── examples/          # Reference code snippets
├── templates/         # Code/config templates
└── scripts/           # Executable tools (not injected)
```

**Technical Reality:** Skills provide KNOWLEDGE, not EXECUTION. They enhance Claude's responses with domain expertise.

### Sub-Agents
- **Technical Function**: Isolated AI assistants in separate context windows
- **Implementation**: Markdown files with YAML frontmatter in `.claude/agents/`
- **Execution**: Explicit delegation via Task tool with memory isolation
- **Performance**: 2-3x latency penalty due to multiple API calls
- **Use Case**: Specialized task execution with context boundaries

### Slash Commands
- **Technical Function**: Prompt injection system loading from `.claude/commands/`
- **Performance**: Zero API overhead - direct main thread injection
- **Structure**: Hierarchical namespace support (e.g., `git/commit.md`)
- **Use Case**: Fast workflow automation and orchestration

## Architecture Relationships

### Layered Design (Orthogonal Components)
1. **Layer 3 (Message)**: Slash Commands - workflow automation
2. **Layer 4 (Message)**: Skills - auto-invoked expertise
3. **Layer 5 (Conversation)**: Sub-Agents - isolated delegation

### Interaction Patterns
- **Commands orchestrate** → **Sub-agents execute** → **Skills provide context**
- **Performance Hierarchy**: Commands (fast) → Skills (medium) → Sub-agents (slower)
- **No component overlap** - clean separation of concerns

## Modular Architecture Integration

### Module Ownership Model

**Modules Bundle Complete Functionality:**
```
modules/python/
├── files/
│   ├── .devcontainer/           # Infrastructure
│   ├── configs/                 # Tooling setup
│   └── .claude/                 # Claude Code components
│       ├── agents/              # Module-owned sub-agents
│       │   ├── python-linter.md
│       │   └── python-tester.md
│       └── commands/            # Module-owned commands
│           └── python/
│               ├── lint.md
│               ├── test.md
│               └── format.md
├── skills/                      # Optional AI expertise
│   ├── python-linting/
│   └── python-testing/
```

### Relationship Patterns

**1:N Module Ownership:**
- **1 Module** → **N Sub-Agents** (specialized for technology)
- **1 Module** → **N Commands** (namespaced workflows)
- **1 Module** → **N Skills** (domain expertise)

**M:N Shared Components:**
```yaml
# Module-specific components
modules/python/skills: ["python-linting"]
modules/typescript/skills: ["typescript-analysis"]

# Shared across modules
modules/both/skills: ["code-review", "architecture-advisor"]
```

### Namespace Organization

**Module-Owned (Technology-Specific):**
- **Commands**: `/python lint`, `/rust cargo`, `/docker build`
- **Sub-Agents**: `python-specialist`, `rust-specialist`
- **Skills**: `python-linting`, `typescript-analysis`

**Shared (Cross-Cutting):**
- **Commands**: `/review`, `/refactor`, `/git commit`
- **Sub-Agents**: `git-workflow`, `github-pr-workflow`
- **Skills**: `code-review`, `architecture-advisor`

## Distribution Strategy

### Bundled Installation
```yaml
# manifests/bundles.yaml
python:
  modules: ["claude-config", "devcontainer-base", "python"]
  skills: ["python-linting", "python-testing", "code-review"]
```

**User Experience:**
```bash
acforge module install python
# Installs: Python tooling + Python expertise + Claude automation
```

### Component Dependencies
```
Infrastructure Layer:    devcontainer, configs, tooling
Automation Layer:        sub-agents, slash commands
Intelligence Layer:      skills (optional enhancement)
```

## Technical Implications

### Skills as Optional Enhancement
- **Filesystem components work without Skills platform**
- **Skills require Pro+ Claude plans** - distribution consideration
- **Skills enhance AI responses but don't block functionality**
- **Skills provide domain expertise that pure filesystem can't**

### Performance Considerations
- **Commands**: Immediate execution (0ms overhead)
- **Skills**: Context injection (minimal overhead)
- **Sub-Agents**: Heavy delegation (2-3x latency)

### Module Design Principles
1. **Complete Functionality**: Each module provides full technology stack
2. **Clean Boundaries**: Module-owned components with shared generic ones
3. **Optional Intelligence**: Skills enhance but don't block core functionality
4. **Performance Awareness**: Consider component overhead in workflow design

## Example: Python Module Components

### Filesystem Components (Required)
- Python devcontainer with tooling
- Linting configurations (flake8, black, mypy)
- Testing framework setup

### Claude Code Components (Automation)
- **Commands**: `/python lint`, `/python test`, `/python format`
- **Sub-Agents**: `python-linter`, `python-tester`

### Skills (Intelligence - Optional)
- **python-linting**: PEP 8 expertise, tool recommendations
- **python-testing**: Testing patterns, framework guidance
- **code-review**: General code quality (shared across modules)

### Result
Complete Python development experience:
- **Infrastructure**: Ready-to-use Python environment
- **Automation**: Streamlined Python workflows
- **Intelligence**: Expert-level Python guidance

This architecture provides comprehensive development environments while maintaining modularity and component independence.

## Migration Strategy

### Current State
AI Code Forge v4.0+ modular architecture aligns with Claude Code's layered design.

### Implementation Phases
1. **Foundation**: Filesystem modules (devcontainer-base, claude-config)
2. **Technology**: Language-specific modules with owned components
3. **Intelligence**: Skills integration as platform matures
4. **Advanced**: Complex M:N relationships and shared components

### Compatibility
- Directory structure follows official Claude Code patterns
- Component relationships leverage established architecture
- Modular approach enables gradual adoption and rollback