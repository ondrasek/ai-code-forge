# launch-claude - Enhanced Claude Code Wrapper

`launch-claude` is a powerful wrapper for Claude Code that provides enhanced functionality, better defaults, and advanced logging capabilities.

## Features

- **Enhanced Defaults**: All logging enabled by default (verbose, debug, MCP debug, save logs), Sonnet model as default
- **Master Prompt Loading**: Automatic loading of custom prompts from `templates/prompts/master-prompt.md`
- **Environment Variable Loading**: Secure loading of `.env` files with validation and sensitive value masking
- **Advanced Logging**: Comprehensive logging enabled by default with timestamped files
- **Log Analysis**: Built-in log analysis using Claude Code agents
- **Easy Installation**: Automated installation script for multiple shells

## Installation

### Manual Setup

```bash
# Manually add the alias to your shell config
echo "alias launch-claude='$(pwd)/scripts/launch-claude.sh'" >> ~/.bashrc
source ~/.bashrc
```

### Verify Installation

```bash
launch-claude --help
```

## Usage

### Basic Usage

```bash
# Simple query with all logging enabled by default
launch-claude "Review my code"

# Interactive mode (same as claude without arguments)
launch-claude
```

### Disabling Logging Options

```bash
# Disable verbose mode (quiet mode)
launch-claude --quiet "Clean output without verbose logging"

# Disable debug mode
launch-claude --no-debug "Reduce debug verbosity"

# Disable MCP server debugging
launch-claude --no-mcp-debug "Turn off MCP debug output"

# Disable log saving
launch-claude --no-logs "Don't save session logs"

# Minimal logging mode
launch-claude --quiet --no-debug --no-mcp-debug --no-logs "Minimal output"
```

### Logging Customization

```bash
# Save logs to specific file (keeps all other defaults)
launch-claude --log-file debug.log "Debug session"

# Analyze existing log files using Claude Code agents
launch-claude --analyze-logs
```

### Model Selection

```bash
# Set custom model (keeps all logging defaults)
launch-claude --model opus "Complex reasoning task"

# Combined custom model with selective logging disable
launch-claude --model opus --quiet "Clean output with opus model"
```

## Configuration

### Master Prompt

Create a custom master prompt that gets automatically prepended to all queries:

```bash
# Create/edit the master prompt file
vim templates/prompts/master-prompt.md
```

Example master prompt content:
```markdown
# Project-Specific Instructions

You are working on a specialized project. Please:
- Follow our coding standards
- Use TypeScript for all new code
- Write comprehensive tests
- Update documentation
```

### Environment Variables (.env File Support)

`launch-claude` automatically loads environment variables from `.env` files in your project root. This enables secure storage of API keys and configuration:

```bash
# Create .env file in project root
cat > .env << EOF
# Claude API Configuration
ANTHROPIC_API_KEY=your-api-key-here
CLAUDE_MODEL=sonnet

# MCP Configuration  
MCP_LOG_LEVEL=debug
MCP_TIMEOUT=30000

# Custom Environment Variables
PROJECT_ENV=development
DEBUG_LEVEL=verbose
EOF
```

#### Supported .env Files (in order of precedence)
- `.env.development` - Development-specific overrides
- `.env.local` - Local machine overrides  
- `.env` - Base configuration

#### Security Features
- **File Permission Validation**: Warns about world-readable .env files
- **Sensitive Value Masking**: Hides API keys, tokens, and passwords in debug output
- **Command Injection Prevention**: Validates values for dangerous patterns
- **Size Limits**: Prevents DoS attacks via large files (100KB max)
- **Environment Precedence**: Existing environment variables take priority

#### Usage Examples
```bash
# Use default .env file loading
launch-claude "Deploy the application"

# Disable .env loading
launch-claude --no-env "Use only system environment"

# Load specific .env file
launch-claude --env-file .env.production "Production deployment"
```

### Legacy Environment Variables

The following environment variables are set when using debug mode:

- `CLAUDE_DEBUG=1` - Enable Claude Code debug output
- `MCP_LOG_LEVEL=debug` - Set MCP server log level to debug
- `ANTHROPIC_DEBUG=1` - Enable Anthropic API debug logging

## Log Analysis

The `--analyze-logs` feature uses multiple Claude Code agents to analyze your log files:

- **researcher agent**: Investigates log patterns and issues
- **patterns agent**: Identifies recurring patterns and anti-patterns
- **Additional agents**: As needed for comprehensive analysis

### Log Analysis Process

1. Finds up to 5 most recent log files in `.logs/` directory
2. Uses Claude Code with multiple agents for analysis
3. Provides actionable insights for:
   - Performance issues
   - Error patterns
   - Optimization opportunities
   - Code quality improvements

## Log Management

### Cleaning Log Files

The `--clean-logs` feature provides safe deletion of all Claude Code session directories:

```bash
# Remove all existing session directories with confirmation
launch-claude --clean-logs
```

**Safety Features:**
- Shows session counts and file counts before deletion
- Requires user confirmation
- Provides detailed deletion report per session
- Handles permission errors gracefully
- Cleans up empty base directory

### Log File Organization

Log files are organized in session-based directories with timestamped structure:
```
.logs/
├── 20250801-110044/                    # Session started Aug 1, 2025 at 11:00:44
│   ├── session-20250801-110044.log     # Main session log
│   ├── mcp-20250801-110044.log         # MCP server communication
│   ├── debug-20250801-110044.log       # Debug output
│   ├── telemetry-20250801-110044.log   # Performance metrics
│   └── session-info.txt                # Session metadata
├── 20250802-074500/                    # Session started Aug 2, 2025 at 7:45:00
│   ├── session-20250802-074500.log
│   ├── mcp-20250802-074500.log
│   ├── debug-20250802-074500.log
│   ├── telemetry-20250802-074500.log
│   └── session-info.txt
└── ...
```

**Benefits of Session-Based Structure:**
- **Complete Session Tracking**: All logs for a single session are grouped together
- **Easy Cleanup**: Delete entire sessions at once
- **Timeline Analysis**: Chronological session organization
- **Session Metadata**: Each session includes configuration and timing information

## MCP Server Troubleshooting

### Automated MCP Diagnostics

The `--troubleshoot-mcp` feature provides comprehensive MCP server analysis:

```bash
# Analyze MCP server issues using specialized agents
launch-claude --troubleshoot-mcp
```

**Analysis Coverage:**
- **Connection Issues**: Server startup, handshake, network connectivity
- **Configuration Problems**: Invalid configs, missing variables, permissions
- **Runtime Errors**: Crashes, memory leaks, protocol violations
- **Performance Issues**: Slow responses, resource usage, bottlenecks
- **Integration Problems**: Communication errors, tool failures

**Specialized Agent Analysis:**
- `foundation-research`: Investigates root causes and patterns
- `specialist-options-analyzer`: Explores solution alternatives
- `foundation-patterns`: Identifies anti-patterns and best practices
- `specialist-constraint-solver`: Resolves configuration conflicts

### Troubleshooting Process

1. **File Discovery**: Finds relevant log files and configurations
2. **Multi-Agent Analysis**: Uses specialized agents for comprehensive review
3. **Root Cause Analysis**: Identifies underlying issues and dependencies
4. **Solution Recommendations**: Provides step-by-step fixes
5. **Prevention Strategies**: Suggests measures to avoid future issues

## Command Reference

| Option | Description | Example |
|--------|-------------|---------|
| `-h, --help` | Show help message | `launch-claude --help` |
| `-q, --quiet` | Disable verbose mode | `launch-claude --quiet "query"` |
| `--no-debug` | Disable debug mode | `launch-claude --no-debug "query"` |
| `--no-mcp-debug` | Disable MCP debug logging | `launch-claude --no-mcp-debug "query"` |
| `--no-logs` | Disable log saving | `launch-claude --no-logs "query"` |
| `-m, --model MODEL` | Set model | `launch-claude --model opus "query"` |
| `--log-file FILE` | Save logs to file | `launch-claude --log-file log.txt "query"` |
| `--analyze-logs` | Analyze existing logs | `launch-claude --analyze-logs` |
| `--clean-logs` | Remove all existing session directories | `launch-claude --clean-logs` |
| `--troubleshoot-mcp` | Troubleshoot MCP server issues | `launch-claude --troubleshoot-mcp` |

## Default Behavior Changes

| Feature | Claude Default | launch-claude Default | Override |
|---------|----------------|--------------|----------|
| Verbose Mode | Off | On | `--quiet` |
| Debug Mode | Off | On | `--no-debug` |
| MCP Debug | Off | On | `--no-mcp-debug` |
| Log Saving | Off | On (timestamped) | `--no-logs` |
| Model | Various | sonnet | `--model` |
| Master Prompt | None | Auto-loaded | Edit `templates/prompts/master-prompt.md` |

## Troubleshooting

### Common Issues

**launch-claude command not found**
```bash
# Check if alias is installed
type launch-claude

# Re-add alias if needed (manual setup)
```

**Permission denied**
```bash
# Make script executable
chmod +x scripts/launch-claude.sh
```

**Master prompt not loading**
```bash
# Check if file exists
ls -la templates/prompts/master-prompt.md

# Create if missing
mkdir -p templates/prompts
touch templates/prompts/master-prompt.md
```

### Debug Mode Output

When using `--debug`, you'll see:
- Command being executed
- Environment variables set
- Master prompt loading status
- Log file locations
- All parameters passed to Claude

## Integration with Claude Code Features

`launch-claude` is fully compatible with all Claude Code features:

- **Agents**: All 20+ specialized agents work normally
- **Commands**: Slash commands (e.g., `/review`, `/test`) work as expected
- **MCP Servers**: Full MCP server support with enhanced debugging
- **Memory**: MCP memory servers work with all logging features
- **Project Settings**: Respects `.claude/settings.json` configurations

## Examples

### Development Workflow

```bash
# Start development session (all logging enabled by default)
launch-claude "Let's implement the user authentication feature"

# Debug performance issues (already has all debug features enabled)
launch-claude "Why is the login endpoint slow?"

# Review code with minimal output if desired
launch-claude --quiet "Review the authentication module for security issues"

# Analyze previous session logs
launch-claude --analyze-logs

# Troubleshoot MCP server issues
launch-claude --troubleshoot-mcp

# Clean up log files when disk space is needed
launch-claude --clean-logs
```

### Team Usage

```bash
# Share master prompt across team
git add templates/prompts/master-prompt.md
git commit -m "Add team coding standards to master prompt"

# Use consistent model for team sessions (logging enabled by default)
launch-claude --model sonnet "Implement feature X according to our standards"
```

### CI/CD Integration

```bash
# Automated code review in scripts (with custom log file)
launch-claude --log-file ci-review.log "Review this PR for issues" < pr-description.txt

# Quiet mode for CI/CD pipelines
launch-claude --quiet --no-logs "Review this PR for issues" < pr-description.txt

# Generate analysis reports
launch-claude --analyze-logs > code-quality-report.md

# Clean logs in CI environments to manage disk space
launch-claude --clean-logs

# Automated MCP troubleshooting in CI/CD diagnostics
launch-claude --troubleshoot-mcp > mcp-diagnostics.md
```

## File Structure

```
scripts/
├── launch-claude.sh              # Main launch-claude script
templates/prompts/
├── master-prompt.md     # Custom master prompt (auto-created)
.logs/                   # Log files (auto-created when using --save-logs)
├── launch-claude-20240128-143022.log
├── launch-claude-20240128-151045.log
└── ...
```