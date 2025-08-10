# Features Guide

Complete overview of what this Claude Code template provides.

## 🤖 AI Agents (17 Included)

Your personal team of AI specialists with **mandatory coordination** for all non-trivial requests.

### Mandatory Protocol
- **Minimum 3+ agents** automatically used for complex tasks
- **Baseline combination**: research + patterns + criticism
- **Memory-first research**: System checks MCP memory before web searches
- **Parallel clusters**: Multiple agents work simultaneously when possible

### Foundation Agents (6 Core Agents)
| Agent | What It Does | When to Use |
|-------|-------------|-------------|
| **`researcher`** | Finds current best practices and documentation | "What's the latest way to do X?" |
| **`patterns`** | Identifies code patterns and refactoring opportunities | Code reviews, architecture cleanup |
| **`critic`** | Provides honest feedback and challenges assumptions | Before big decisions, design reviews |
| **`context`** | Explains how systems work and interact | Understanding complex codebases |
| **`principles`** | Applies SOLID, DRY, KISS design principles | Architecture reviews, refactoring |
| **`conflicts`** | Mediates when different approaches conflict | When agents give conflicting advice |

### Specialist Agents (11 Domain Experts)
| Agent | What It Does | When to Use |
|-------|-------------|-------------|
| **`constraint-solver`** | Handles competing requirements and trade-offs | "I need X but also Y, and they conflict" |
| **`code-cleaner`** | Finds missing functionality and TODOs | "What am I missing?" reviews |
| **`performance-optimizer`** | Performance analysis and optimization | Speed optimization, profiling |
| **`test-strategist`** | Testing strategies and test design | Test planning, quality assurance |
| **`options-analyzer`** | Generates multiple solution approaches | "What are my options?" questions |
| **`git-workflow`** | Git operations and version control | Git troubleshooting, workflow automation |
| **`github-issues-workflow`** | GitHub Issues lifecycle management | Issue tracking, project management |
| **`github-pr-workflow`** | GitHub Pull Request workflows | PR creation, review automation |
| **`stack-advisor`** | Technology selection and architecture | Technology recommendations |
| **`prompt-engineer`** | AI prompt creation and optimization | Creating effective AI prompts |
| **`meta-programmer`** | Code generation and template creation | Automated code generation |




## 📋 Custom Commands (31 Included)

Ready-to-use slash commands for common tasks.

### Core Commands
| Command | Purpose | Example Usage |
|---------|---------|---------------|
| **`/review`** | Comprehensive code review | `/review` on any file or selection |
| **`/test`** | Generate tests and testing guidance | `/test` for the current function |
| **`/refactor`** | Code improvement suggestions | `/refactor` messy code sections |
| **`/security`** | Security audit and recommendations | `/security` on authentication code |
| **`/research`** | Research and information gathering | `/research` for technical questions |
| **`/fix`** | Problem diagnosis and resolution | `/fix` bug reports and errors |
| **`/generate`** | Code and template generation | `/generate` boilerplate code |
| **`/performance`** | Performance analysis | `/performance` optimization tasks |

### Issue Management Commands
| Command | Purpose |
|---------|---------|
| **`/issue create`** | Create new GitHub issues |
| **`/issue review`** | Review existing issues |
| **`/issue next`** | Get next priority issue |
| **`/issue cleanup`** | Clean up completed issues |

### Workflow Commands
| Command | Purpose |
|---------|---------|
| **`/git`** | Git workflow assistance |
| **`/deploy`** | Deployment assistance |
| **`/monitor`** | System monitoring |
| **`/stacks`** | Technology stack guidance |
| **`/discuss`** | Architecture discussions |

**Plus 16 additional specialized commands** for agents, version management, and project-specific workflows.

## 🧠 Memory System

Claude Code remembers your project across sessions.

### What Gets Remembered
- **Architectural decisions** and their reasoning
- **Code patterns** you've established
- **Design principles** your team follows
- **Debugging insights** and solutions
- **Refactoring outcomes** and lessons learned

### How It Works
1. **Automatic capture** - Insights stored as you work
2. **Cross-session persistence** - Knowledge survives restarts
3. **Team collaboration** - Shared memory via git
4. **Export/import** - Backup and restore insights

### Memory Types
- **`research_topic`** - Investigation findings
- **`architectural_decision`** - Design choices and trade-offs
- **`design_pattern`** - Code patterns and their usage
- **`principle_violation`** - Issues found and fixes applied
- **`tagging_decision`** - Release management decisions

## 🛠️ Technology Integration

Automatic best practices for your tech stack.

### Supported Technologies
| Technology | Features |
|------------|----------|
| **Python** | uv workflows, testing with pytest, modern Python patterns |
| **Rust** | Cargo workflows, error handling, async patterns |
| **JavaScript/TypeScript** | npm/yarn workflows, testing, modern JS patterns |
| **Java** | Maven/Gradle, Spring Boot, testing patterns |
| **Kotlin** | Backend development, coroutines, Spring integration |
| **Ruby** | Bundler workflows, Rails patterns, testing |
| **C#/.NET** | dotnet CLI, ASP.NET Core, testing patterns |
| **C++** | Modern C++20 features, CMake, testing |
| **Docker** | Container best practices, security, optimization |

### How It Works
- **Automatic detection** - Scans your project for technology indicators
- **Best practices** - Loads appropriate guidelines and patterns
- **Tool integration** - Works with your existing toolchain
- **Agent specialization** - Agents understand your tech stack

## 🎯 Context-Clean Task Management

Intelligent task coordination through specialized agents that keep your main context clean and focused.

### Agent-Based Task Orchestration
- **Delegated task management** - Agents handle complex multi-step workflows independently
- **Clean main context** - No polluting TODO lists in your primary workspace
- **Intelligent coordination** - Agents automatically break down complex requests
- **Context preservation** - Task progress stored in persistent memory

### How It Works
- **Automatic detection** - System recognizes when tasks need structured coordination
- **Agent delegation** - Complex workflows handed off to specialized task agents
- **Memory integration** - Progress and context preserved across sessions
- **Clean handoffs** - Agents return concise results without cluttering main context

### Benefits
- **Focused conversations** - Main context stays clean and on-topic
- **Comprehensive execution** - Nothing gets overlooked through agent coordination
- **Persistent progress** - Work continues seamlessly across sessions
- **Professional output** - Clean, organized results without intermediate noise

## 🔧 MCP Tool Integration

External integrations that extend Claude Code capabilities.

### Built-in Tools
- **Memory Server** - Persistent knowledge storage
- **SQLite Server** - Structured data storage and queries

### What This Enables
- **Cross-session memory** persists between Claude Code sessions
- **Structured data storage** for complex project information
- **Team collaboration** through shared knowledge bases
- **Backup and restore** of project insights

## 🚀 Automation Features

### Documentation Protocol (MANDATORY)
- **Same commit rule** - Documentation updates included with every code change
- **Automatic checks** - README.md, CHANGELOG.md, API docs, CLAUDE.md always reviewed
- **Immediate updates** - New features, API changes, configuration changes documented instantly
- **docs agent integration** - Automatic documentation maintenance

### Git Integration
- **Automatic memory export** before every commit
- **Autonomous tagging** based on completion criteria
- **Trunk-based development** workflow optimization
- **Change documentation** in commit messages

### Workflow Automation
- **Technology detection** and automatic best practice application
- **Agent coordination** - agents work together automatically
- **Memory integration** - insights flow between sessions
- **Quality gates** - automated code quality checks

## 🎯 Agent Coordination

Agents work together in intelligent clusters with **mandatory coordination protocols**.

### Mandatory Protocol (ENFORCED)
- **Minimum 3+ agents** for all non-trivial requests - no exceptions
- **Baseline combination**: research + patterns + criticism (always included)
- **Memory-first workflow**: Check MCP memory before web searches
- **Context optimization**: Agents keep main context window tidy and focused

### Common Patterns
- **Research → Patterns → Principles → Criticism** - For code reviews
- **Explorer → Constraints → Conflicts** - For architecture decisions
- **Hypothesis → Completer → Whisper** - For debugging
- **Research → Generator → Principles** - For feature development

### Smart Workflows
- **Parallel execution** - Multiple agents work simultaneously
- **Context sharing** - Agents build on each other's insights
- **Conflict resolution** - Automatic mediation of different approaches
- **Memory integration** - Persistent learning across sessions

---

**Next Steps:**
- 🧠 Memory system setup available via scripts/setup-claude-memory.sh
- 🛠️ [Customize](customization.md) the template for your project
- 📚 Return to [Getting Started](getting-started.md)