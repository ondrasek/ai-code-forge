# Features Guide

Complete overview of what this Claude Code template provides.

## 🤖 AI Agents (20+)

Your personal team of AI specialists with **mandatory coordination** for all non-trivial requests.

### Mandatory Protocol
- **Minimum 3+ agents** automatically used for complex tasks
- **Baseline combination**: researcher + patterns + critic
- **Memory-first research**: System checks MCP memory before web searches
- **Parallel clusters**: Multiple agents work simultaneously when possible

### Essential Agents (Start Here)
| Agent | What It Does | When to Use |
|-------|-------------|-------------|
| **`researcher`** | Finds current best practices and documentation | "What's the latest way to do X?" |
| **`patterns`** | Identifies code patterns and refactoring opportunities | Code reviews, architecture cleanup |
| **`critic`** | Provides honest feedback and challenges assumptions | Before big decisions, design reviews |

### Problem-Solving Agents
| Agent | What It Does | When to Use |
|-------|-------------|-------------|
| **`hypothesis`** | Forms theories and tests them scientifically | Debugging complex issues |
| **`constraints`** | Handles competing requirements and trade-offs | "I need X but also Y, and they conflict" |
| **`resolver`** | Mediates when different approaches conflict | When agents give conflicting advice |

### Code Quality Agents
| Agent | What It Does | When to Use |
|-------|-------------|-------------|
| **`completer`** | Finds missing functionality and TODOs | "What am I missing?" reviews |
| **`whisper`** | Suggests micro-improvements and polish | Final code cleanup |
| **`invariants`** | Ensures type safety and prevents invalid states | Designing robust data structures |

### Architecture Agents
| Agent | What It Does | When to Use |
|-------|-------------|-------------|
| **`explorer`** | Generates multiple solution approaches | "What are my options?" questions |
| **`axioms`** | Builds solutions from first principles | "Why does this work?" deep understanding |
| **`context`** | Explains how systems work and interact | Understanding complex codebases |
| **`principles`** | Applies SOLID, DRY, KISS design principles | Architecture reviews, refactoring |

### Workflow Agents
| Agent | What It Does | When to Use |
|-------|-------------|-------------|
| **`generator`** | Creates code templates and boilerplate | Repetitive code generation |
| **`prompter`** | Helps build AI agents and prompts | Creating custom Claude Code agents |
| **`time`** | Analyzes code history and evolution | Understanding how code evolved |
| **`connector`** | Finds creative cross-domain solutions | "How do other fields solve this?" |
| **`tagger`** | Automatically manages releases and versions | Automated release workflows |

## 📋 Custom Commands

Ready-to-use slash commands for common tasks.

| Command | Purpose | Example Usage |
|---------|---------|---------------|
| **`/review`** | Comprehensive code review | `/review` on any file or selection |
| **`/test`** | Generate tests and testing guidance | `/test` for the current function |
| **`/refactor`** | Code improvement suggestions | `/refactor` messy code sections |
| **`/security`** | Security audit and recommendations | `/security` on authentication code |

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
- **Baseline combination**: researcher + patterns + critic (always included)
- **Memory-first workflow**: Check MCP memory before web searches
- **Context optimization**: Agents keep main context window tidy and focused

### Common Patterns
- **Research → Patterns → Principles → Critic** - For code reviews
- **Explorer → Constraints → Resolver** - For architecture decisions  
- **Hypothesis → Completer → Whisper** - For debugging
- **Researcher → Generator → Principles** - For feature development

### Smart Workflows
- **Parallel execution** - Multiple agents work simultaneously
- **Context sharing** - Agents build on each other's insights
- **Conflict resolution** - Automatic mediation of different approaches
- **Memory integration** - Persistent learning across sessions

---

**Next Steps:**
- 🧠 Learn about the [Memory System](memory-system.md) for persistent context
- 🛠️ [Customize](customization.md) the template for your project
- 📚 Return to [Getting Started](getting-started.md)