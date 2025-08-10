# Configuration Reference Guide

## Overview

This guide provides detailed documentation for every configuration file and directory in the Claude Code Template. Use this as a reference when customizing your setup or troubleshooting issues.

## Directory Structure Reference

### `.claude/` Directory (Main Configuration)

The `.claude` directory contains all Claude Code configuration and should be copied to `~/.claude/` for global access.

#### Core Files

##### `settings.json`
**Location**: `~/.claude/settings.json`
**Purpose**: Main Claude Code configuration file
**Content**: JSON configuration for Claude Code behavior

```json
{
  // Currently empty - configuration is handled by file structure
  // Future versions may include global settings here
}
```

##### `settings.local.json` (Optional)
**Location**: `~/.claude/settings.local.json`  
**Purpose**: Local environment settings and permissions (user-created)
**Content**: Security permissions and local overrides

```json
{
  "permissions": {
    "allow": [
      "Bash(ls:*)",
      "Bash(find:*)"
    ]
  }
}
```

**Note**: This file does not exist by default and must be created by users who need custom permissions.

**Configuration Options**:
- `permissions.allow`: Array of allowed command patterns
- `permissions.deny`: Array of denied command patterns (not shown)
- Local environment overrides

#### `agents/` Directory

Contains AI agent definitions that work together to handle complex development tasks.

##### `agents/foundation/` - Core Agents (6 Agents)

**Purpose**: Essential agents used in all complex operations (mandatory 3+ agent coordination)

| Agent | File | Purpose | When Used |
|-------|------|---------|-----------|
| **researcher** | `researcher.md` | Information gathering, best practice lookup | All requests needing external knowledge |
| **patterns** | `patterns.md` | Code pattern recognition, anti-pattern detection | Code analysis, architecture review |
| **critic** | `critic.md` | Critical analysis, honest feedback | All requests requiring evaluation |
| **principles** | `principles.md` | SOLID principles, design patterns enforcement | Architecture decisions, code quality |
| **context** | `context.md` | Deep system understanding, context synthesis | Complex system analysis |
| **conflicts** | `conflicts.md` | Mediate between competing approaches | When agents disagree on solutions |

**Mandatory Usage**: These agents are automatically invoked for all non-trivial requests as part of the coordination protocol.

##### `agents/specialists/` - Specialized Agents (11 Agents)

**Purpose**: Domain-specific experts for particular technologies or workflows

| Agent | File | Purpose | Specialization |
|-------|------|---------|----------------|
| **code-cleaner** | `code-cleaner.md` | Code quality, refactoring | Clean code practices, readability |
| **constraint-solver** | `constraint-solver.md` | Handle competing requirements | Requirements analysis, trade-offs |
| **git-workflow** | `git-workflow.md` | Git operations, version control | Git troubleshooting, workflow automation |
| **github-issues-workflow** | `github-issues-workflow.md` | GitHub Issues lifecycle management | Issue tracking, project management |
| **github-pr-workflow** | `github-pr-workflow.md` | GitHub Pull Request workflows | PR creation, review automation |
| **options-analyzer** | `options-analyzer.md` | Solution exploration, alternatives | Decision making, approach comparison |
| **performance-optimizer** | `performance-optimizer.md` | Performance analysis, optimization | Speed, memory, efficiency improvements |
| **prompt-engineer** | `prompt-engineer.md` | AI prompt creation, optimization | Creating effective AI prompts |
| **stack-advisor** | `stack-advisor.md` | Technology selection, architecture | Technology recommendations |
| **test-strategist** | `test-strategist.md` | Testing strategies, test design | Test planning, quality assurance |
| **meta-programmer** | `meta-programmer.md` | Code generation, template creation | Automated code generation |

#### `commands/` Directory

Contains custom slash commands that provide instant access to common development tasks.

##### Core Commands

| Command | File | Purpose | Usage |
|---------|------|---------|-------|
| `/review` | `review.md` | Comprehensive code review | Code quality analysis |
| `/test` | `test.md` | Testing assistance | Test generation, testing strategy |
| `/refactor` | `refactor.md` | Code improvement suggestions | Code restructuring, optimization |
| `/security` | `security.md` | Security audit and recommendations | Security analysis, vulnerability detection |
| `/stacks` | `stacks.md` | List available technology stacks | Technology guidance, stack selection |
| `/discuss` | `discuss.md` | Critical analysis of ideas | Architecture discussions, decision making |
| `/research` | `research.md` | Research and information gathering | Technical research, best practices |
| `/fix` | `fix.md` | Problem diagnosis and resolution | Bug fixing, error resolution |
| `/generate` | `generate.md` | Code and template generation | Boilerplate creation, scaffolding |
| `/performance` | `performance.md` | Performance analysis and optimization | Speed optimization, profiling |
| `/monitor` | `monitor.md` | System monitoring and health checks | Application monitoring, metrics |
| `/deploy` | `deploy.md` | Deployment assistance | Deployment planning, configuration |

##### Specialized Command Groups

**Agent Management** (`commands/agents/`)
- `/agents-audit` - Audit agent usage and effectiveness
- `/agents-create` - Create new custom agents
- `/agents-guide` - Guide to using agents effectively

**Command Management** (`commands/commands/`)
- `/commands-create` - Create new custom commands
- `/commands-review` - Review and improve existing commands

**TODO Management** (`commands/todo/`)
- `/todo-create` - Create and organize tasks
- `/todo-next` - Get next priority task
- `/todo-review` - Review task progress
- `/todo-cleanup` - Clean up completed tasks

**Version Management**
- `/version-prepare` - Prepare for version releases
- `/git` - Git workflow assistance
- `/doc-update` - Update documentation automatically

### Project Structure (Support Files)

The project contains various support files, templates, and configurations organized in multiple directories.

#### Core Subdirectories

##### `templates/prompts/`
**Purpose**: Reusable prompts and templates
**Contents**: 
- `master-prompt.md` - Main Claude Code prompt template
- Additional prompt templates for specific use cases

##### `templates/guidelines/`
**Purpose**: Additional guidelines and instructions for Claude Code
**Contents**:
- `CLAUDE.md` - Copy of main project guidelines
- `claude-agents-guidelines.md` - Agent coordination rules
- `claude-commands-guidelines.md` - Command creation guidelines
- `security-workflows.md` - Security best practices
- `software-tradeoff-framework.md` - Decision-making frameworks
- `stack-mapping.md` - Technology stack guidelines

##### `src/` Directory
**Purpose**: MCP (Model Context Protocol) server implementations
**Contents**:
- `perplexity-mcp/` - Perplexity AI research server source code
- Additional MCP server implementations

**MCP Configuration Example**:
```json
{
  "mcpServers": {
    "perplexity-research": {
      "command": "uv",
      "args": ["--directory", "src/perplexity-mcp", "run", "perplexity-mcp"],
      "env": {
        "PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}",
        "PERPLEXITY_LOG_LEVEL": "debug",
        "PERPLEXITY_LOG_PATH": ".logs/perplexity"
      },
      "alwaysAllow": ["perplexity_search", "perplexity_deep_research"],
      "description": "Perplexity AI research and web search capabilities"
    }
  }
}
```

**Note**: This MCP configuration would need to be added to your Claude Code settings.

##### `.logs/` Directory (Auto-created)
**Purpose**: Diagnostic and troubleshooting logs
**Contents**: 
- Session-based log organization
- MCP server logs
- Debug information for troubleshooting
**Note**: This directory is created automatically when logging is enabled.

##### `scripts/` Directory
**Purpose**: Utility scripts for setup and maintenance
**Contents**:
- `launch-claude.sh` - Enhanced Claude Code wrapper
- `setup-claude-memory.sh` - Memory system configuration
- `test-agents.sh` - Agent testing utilities
- `test-session-logging.sh` - Logging system tests

##### `analysis/` Directory
**Purpose**: Project analysis and optimization reports
**Contents**:
- Performance baseline metrics
- Usage pattern analysis
- Agent ecosystem analysis
- Optimization recommendations

##### `templates/stacks/` Directory
**Purpose**: Technology-specific guidelines
**Contents**:
- `cpp.md`, `csharp.md`, `docker.md`, `java.md` - Language-specific guidelines
- `kotlin.md`, `python.md`, `ruby.md`, `rust.md` - Additional stack templates
- Framework-specific best practices

##### `templates/specs/` Directory
**Purpose**: Specification templates
**Contents**:
- Template files for project specifications
- Standardized documentation formats

## Configuration Integration

### How Configurations Work Together

1. **Agent Coordination**: Foundation agents are automatically invoked together for complex tasks
2. **Command to Agent Mapping**: Commands automatically invoke relevant specialist agents
3. **Environment Integration**: Settings files enable secure environment variable usage
4. **Project Context**: Support files provide project-specific context to agents
5. **MCP Integration**: External tools are seamlessly integrated via MCP configuration

### Configuration Hierarchy

1. **Global Settings**: `~/.claude/settings.json` and `~/.claude/settings.local.json`
2. **Agent Definitions**: All `.md` files in `~/.claude/agents/`
3. **Command Definitions**: All `.md` files in `~/.claude/commands/`
4. **Project Context**: `CLAUDE.md` in project root
5. **Support Files**: `templates/`, `scripts/`, and `src/` directories in project root
6. **Environment Variables**: System environment variables

### Customization Guidelines

#### Adding New Agents

1. Create a new `.md` file in `~/.claude/agents/specialists/`
2. Follow the agent template format
3. Define clear specialization and trigger conditions
4. Test with various scenarios

#### Creating Custom Commands

1. Create a new `.md` file in `~/.claude/commands/`
2. Use descriptive, action-oriented command names
3. Include clear usage instructions
4. Test command functionality

#### Modifying Agent Behavior

1. Edit the relevant agent `.md` file
2. Maintain the agent's core purpose
3. Update trigger conditions if necessary
4. Test changes with typical use cases

#### Environment-Specific Configuration

1. Use `settings.local.json` for local overrides
2. Never commit sensitive data
3. Use environment variables for API keys
4. Document custom configurations

## Security Considerations

### File Permissions

- All configuration files should be readable only by the user
- Executable scripts should have appropriate execute permissions
- Sensitive files should not be world-readable

### Environment Variables

- Use environment variables for all sensitive data
- Never hardcode API keys in configuration files
- Validate environment variables before use
- Use secure methods for sharing keys in team environments

### Agent Security

- Agents operate within Claude Code's security model
- No direct file system access beyond Claude Code permissions
- All operations are logged and auditable
- Sensitive operations require explicit permission

## Troubleshooting Configuration Issues

### Common Problems

1. **Commands not recognized**: Check file location and permissions
2. **Agents not responding**: Verify agent files exist and are readable
3. **Environment variables not available**: Check shell configuration
4. **Permissions denied**: Verify file permissions and ownership

### Diagnostic Commands

```bash
# Check configuration structure
find ~/.claude -type f -name "*.md" | head -10

# Verify permissions
ls -la ~/.claude/

# Test environment variables
echo $CLAUDE_API_KEY

# Validate JSON configuration
python -m json.tool ~/.claude/settings.json
```

### Rebuilding Configuration

If configuration becomes corrupted:

1. Backup current configuration: `cp -r ~/.claude ~/.claude.backup`
2. Remove corrupted configuration: `rm -rf ~/.claude`
3. Re-copy from template: `cp -r .claude ~/.claude`
4. Restore customizations from backup if needed

This comprehensive reference should help you understand, customize, and troubleshoot your Claude Code Template configuration.