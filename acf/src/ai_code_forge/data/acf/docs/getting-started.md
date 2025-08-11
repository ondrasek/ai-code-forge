# Getting Started with Claude Code Template

## Overview

This template transforms your Claude Code experience into a comprehensive AI-powered development environment. These files provide detailed guidelines and best practices that complement the AI operational instructions in CLAUDE.md, designed for both human reference and AI processing.

## What This Does

Transform your Claude Code experience with:
- ✅ **17 AI agents** with mandatory coordination (minimum 3+ agents for complex tasks)
- ✅ **Context-clean workflows** - Agents handle complex tasks independently, keeping conversations focused
- ✅ **Custom slash commands** like `/review`, `/test`, `/refactor` for instant help
- ✅ **Technology-specific guidance** - Python, Rust, Java, JavaScript, and more
- ✅ **Persistent memory** - Claude remembers your project decisions across sessions
- ✅ **Automatic documentation** - Updates docs with every code change
- ✅ **Automatic setup** - One-time install, works in every project

## Purpose

This template helps developers understand:

1. **Decision-making criteria** - When and why to create certain components
2. **Best practice patterns** - Proven approaches for common development scenarios
3. **Process workflows** - Step-by-step procedures for project maintenance
4. **Quality standards** - Metrics and validation approaches for project health

## Quick Start (5 Minutes)

### Option 1: Manual Setup (Recommended)
1. Clone this repository: `git clone https://github.com/ondrasek/ai-code-forge.git`
2. Copy configuration: `cp -r .claude/ ~/.claude/`
3. Set API key: `echo 'export CLAUDE_API_KEY="your-key"' >> ~/.bashrc && source ~/.bashrc`
4. Test: Open Claude Code and try `/review`

**📖 Detailed Instructions**: See [Configuration Reference](configuration-reference.md) for complete setup details

### Option 2: GitHub Dotfiles (For GitHub Codespaces)
1. [Fork this repository](https://github.com/ondrasek/ai-code-forge/fork) and rename it to `dotfiles`
2. Go to GitHub Settings → Codespaces → Dotfiles → Enable
3. Open any project in Claude Code - you now have superpowers! ✨

**Try immediately:**
```
/review          # Get comprehensive code feedback
/agents-guide     # Explore your AI helpers
/discuss         # Challenge your architectural ideas
```

## What You Get

### Essential AI Agents (Mandatory Baseline)
- **`researcher`** - Find answers and current best practices
- **`patterns`** - Spot code problems and suggest improvements
- **`critic`** - Get honest feedback on your ideas and decisions

**Note**: These 3 agents are automatically used together for all non-trivial requests as part of the mandatory coordination protocol.

### Advanced AI Agents
<details>
<summary>Click to see 16 more specialized agents</summary>

**Problem Solving:**
- `hypothesis` - Scientific debugging approach
- `constraints` - Handle competing requirements
- `resolver` - Mediate conflicting approaches

**Code Quality:**
- `completer` - Find missing functionality and TODOs
- `whisper` - Micro-improvements and polish
- `invariants` - Type safety and state machines

**Architecture:**
- `explorer` - Generate multiple solution approaches
- `axioms` - First-principles reasoning
- `context` - Deep system understanding
- `principles` - Apply SOLID, DRY, KISS principles

**Workflow:**
- `generator` - Code generation and templates
- `prompter` - AI agent development
- `time` - Historical analysis and evolution
- `connector` - Cross-domain creative solutions
- `git-tagger` - Automatic release management
- `git-troubleshooter` - Git error diagnosis and resolution

</details>

### Custom Commands
- `/review` - Comprehensive code review
- `/test` - Testing assistance and generation
- `/refactor` - Code improvement suggestions
- `/security` - Security audit and recommendations

## Setup Documentation

| Guide | Purpose | When to Use |
|-------|---------|-------------|
| **[Configuration Reference](configuration-reference.md)** | Detailed file documentation | Understanding what each file does |
| **[Launch Claude Usage](launch-claude-usage.md)** | Enhanced wrapper tool setup | Setup and usage of launch-claude script |
| **[Customization Guide](customization.md)** | Project adaptation | Making template work for your specific needs |

## Feature Documentation

| Guide | Purpose |
|-------|---------|
| **[Features](features.md)** | Complete overview of all capabilities |
| **[Customization](customization.md)** | Adapt the template for your project |
| **[Agent Usage](agent-usage.md)** | Detailed patterns and examples for coordinating multiple AI agents effectively |
| **[Documentation](documentation.md)** | Guidelines for maintaining project documentation automatically alongside code changes |
| **[Versioning](versioning.md)** | Semantic versioning rules and release management procedures |

## When to Use This Guide

Consult these resources when:

- Planning new features or architectural changes
- Setting up development workflows
- Understanding project conventions and standards
- Training new team members on project practices
- Debugging complex issues or performance problems
- Making architectural decisions with AI assistance

These docs are maintained alongside code changes to ensure accuracy and relevance.

## Real-World Examples

**Note**: All examples automatically include the mandatory baseline agents (researcher + patterns + critic) plus any additional specialized agents.

### Debugging a Complex Bug
```
1. /discuss "Should I rewrite this authentication module?"
2. System automatically uses: researcher + patterns + critic + hypothesis
3. /test to generate test cases that isolate the problem
```

### Architecture Review
```
1. /review to get comprehensive feedback on your code
2. System automatically uses: researcher + patterns + critic + principles
3. Documentation automatically updated with architectural decisions
```

### New Feature Planning
```
1. Use explorer agent for multiple approaches (includes baseline agents)
2. Use constraints agent to handle competing requirements
3. /discuss the trade-offs before implementing
4. Documentation automatically updated when feature is implemented
```

## Troubleshooting

**Commands not working?**
- Make sure you're in a Claude Code session
- Check that the template was installed correctly with `ls .claude/`

**Agents not responding as expected?**
- Try being more specific about what you want
- Use `/agents-guide` to see what each agent does best

**Memory not persisting?**
- Memory is handled by Claude Code's built-in MCP memory server
- No additional setup required for basic memory functionality

## Need Help?

- 📖 **[Full Feature Guide](features.md)** - Everything the template can do
- 🧠 **Memory System** - See scripts/setup-claude-memory.sh for memory system configuration
- 🛠️ **[Customization Guide](customization.md)** - Make it yours
- 🐛 **Issues?** [Report bugs or request features](https://github.com/ondrasek/ai-code-forge/issues)

---

*Ready to supercharge your coding with AI? Install the template and try `/review` on your current code!*