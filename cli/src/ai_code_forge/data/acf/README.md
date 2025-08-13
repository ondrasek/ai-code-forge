# AI Code Forge

**Transform Claude Code into a specialized AI agent system with templates, workflows, and intelligent automation.**

[![Version](https://img.shields.io/github/v/release/ondrasek/ai-code-forge)](https://github.com/ondrasek/ai-code-forge/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Issues](https://img.shields.io/github/issues/ondrasek/ai-code-forge)](https://github.com/ondrasek/ai-code-forge/issues)

A comprehensive template system that enhances Claude Code with specialized AI agents, technology stack configurations, and automated workflows. Get your AI development environment running in under 3 minutes.

## Quick Start

### Method 1: ACF CLI Tool (Recommended)

```bash
# Install ACF tool
pip install ai-code-forge

# Deploy configuration to your project
ai-code-forge install

# Verify installation
ai-code-forge status
```

### Method 2: Development Installation

```bash
# 1. Clone and build from source
git clone https://github.com/ondrasek/ai-code-forge.git
cd ai-code-forge/acf

# 2. Build and install the configuration manager
./build.sh
python -m src.acf.main install

# 3. Verify installation
python -m src.acf.main status
```

### Method 3: Manual Setup

```bash
# 1. Clone and setup
git clone https://github.com/ondrasek/ai-code-forge.git
cd ai-code-forge

# 2. Launch enhanced Claude Code
./scripts/launch-claude.sh

# 3. Create worktrees for parallel development (optional)
./scripts/worktree/worktree.sh create feature/new-feature
./scripts/worktree/worktree.sh create --from-issue 126  # From GitHub issue
```

**Requirements**: Claude Code CLI, Git, Python 3.13+, Node.js

## What You Get

- **🤖 Specialized AI Agents**: Pre-built agents for code analysis, testing, security, and performance
- **📚 Technology Templates**: Battle-tested configurations for Python, Rust, Java, C++, TypeScript, Docker
- **🔧 Automated Workflows**: GitHub integration, git operations, and project management
- **🔍 Research Integration**: Real-time web search via Perplexity MCP server
- **📝 Smart Documentation**: Templates and guidelines for consistent project documentation
- **⚡ Launch Scripts**: One-command setup for different development scenarios
- **🚀 ACF CLI Tool**: Configuration management tool for automated AI Code Forge setup

## Core Features

### AI Agent System
**Transform Claude Code into a specialized development assistant:**
- **Code Analysis Agents**: Automated code review, pattern detection, quality assessment
- **Workflow Agents**: Git operations, GitHub integration, testing automation
- **Performance Agents**: Optimization analysis, bottleneck detection, security scanning
- **Documentation Agents**: README generation, API documentation, code comments

### Technology Stack Intelligence
**Pre-configured expertise for major development stacks:**
- **Python**: Django/FastAPI patterns, pytest strategies, poetry workflows
- **Rust**: Cargo optimization, async patterns, memory safety validation
- **Java**: Spring Boot setup, Maven/Gradle best practices, testing frameworks
- **TypeScript**: Node.js/React patterns, testing strategies, build optimization
- **Docker**: Multi-stage builds, security hardening, size optimization

### ACF CLI Tool
**Automated Configuration Management:**
- **Installation Command**: `ai-code-forge install` - Deploys complete Claude Code configuration
- **Status Monitoring**: `ai-code-forge status` - Verifies installation and shows components
- **Targeted Deployment**: `--target` option for custom installation directories
- **Force Updates**: `--force` option for overwriting existing configurations
- **File Management**: Automatically installs `.claude/`, `.acf/`, and `CLAUDE.md`

**What Gets Installed:**
- **`.claude/`** - All agents, commands, and Claude Code settings
- **`.acf/`** - Templates, documentation, and ACF-specific tools
- **`CLAUDE.md`** - Core operational rules and project guidelines

## Script System

Utility scripts for Claude Code setup and operation:

- `launch-claude.sh` - Launch Claude Code with enhanced configuration and logging
- `worktree/worktree.sh` - Unified interface for git worktree management and parallel development
- `worktree-create.sh` - Core worktree creation utility with GitHub issue integration
- `worktree-list.sh` - Advanced worktree listing with detailed status information

### Git Worktree Management

Parallel development workflow utilities:

- `worktree/worktree.sh` - Unified worktree management interface with GitHub Issues integration
  - `worktree.sh create <branch> [issue-number]` - Create new worktree with optional issue linking
  - `worktree.sh create --from-issue <num>` - Create from GitHub issue (auto-detects existing branches)
  - `worktree.sh list` - List all worktrees with detailed status information
  - `worktree.sh cleanup` - Clean up invalid worktrees with safety checks

## Technology Stack Integration

Built-in configurations for:

- **Python**: Django, FastAPI, pytest, poetry
- **Rust**: Cargo, async, memory safety
- **Java**: Spring Boot, Maven/Gradle, JUnit
- **TypeScript**: Node.js, React, testing frameworks
- **C++**: Modern standards, CMake
- **Docker**: Multi-stage builds, optimization
- **Ruby**, **C#**, **Kotlin**: Basic configurations

Each stack includes:
- Automated detection
- Best practices and patterns
- Security guidelines  
- Testing strategies

## MCP Server

Includes Perplexity MCP server implementation:

```bash
cd src/perplexity-mcp
# See README.md for setup instructions
```

Provides real-time web search and research capabilities through the `/research` command.

## Architecture

```
├── analysis/             # Project analysis and research
├── docs/                # Documentation and guides
├── research/            # Technical research documents
├── scripts/             # Setup and utility scripts
├── src/                 # Source code
│   └── perplexity-mcp/  # MCP server implementation
├── templates/           # Template system
│   ├── guidelines/      # Agent and workflow templates
│   ├── prompts/        # Master prompt templates
│   ├── specs/          # Specification templates
│   └── stacks/         # Technology stack configurations
├── CLAUDE.md           # Core operational rules
└── CHANGELOG.md        # Version history
```

## Development Workflow

1. **Template-Based Setup**: Use provided templates for agent and stack configuration
2. **GitHub Issues Integration**: Specification management through GitHub Issues
3. **Memory System**: Cross-session context preservation via CLAUDE.md
4. **Research Integration**: Real-time web research via Perplexity MCP server
5. **Automated Git Operations**: Consistent versioning and change management

## Configuration

The system provides template-based configuration:

- Technology stack guidelines in `templates/stacks/`
- Agent framework templates in `templates/guidelines/`
- Master prompt templates in `templates/prompts/`
- Core operational rules in `CLAUDE.md`

## Documentation

- **[Getting Started](docs/getting-started.md)** - Setup instructions
- **[Agent Usage](docs/agent-usage.md)** - Working with AI agents
- **[Features](docs/features.md)** - Complete feature reference
- **[Configuration](docs/configuration-reference.md)** - Customization options
- **[Launch Scripts](docs/launch-claude-usage.md)** - Script configuration

## Getting Help

- **📚 Documentation**: Comprehensive guides in `/docs/` directory
- **🐛 Issues**: [Report bugs or request features](https://github.com/ondrasek/ai-code-forge/issues)
- **💡 Discussions**: [Community discussions and Q&A](https://github.com/ondrasek/ai-code-forge/discussions)
- **📖 Examples**: Real-world usage examples in `/templates/` and `/analysis/`

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Project Status**: Actively maintained • Version 2.78.0+ • MIT License

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Repository Structure**: Development workspace containing templates, agents, and tools for enhancing Claude Code with specialized AI workflows.