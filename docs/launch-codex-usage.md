# launch-codex.sh - OpenAI Codex CLI Enhanced Wrapper

## Overview

`launch-codex.sh` is an enhanced wrapper for the OpenAI Codex CLI that provides advanced features including session-based logging, environment detection, secure configuration management, and integration with the AI Code Forge ecosystem.

## Features

### Core Features
- **Enhanced CLI Interface** - Comprehensive command-line options mirroring launch-claude.sh
- **Session-Based Logging** - Organized logging to `.acf/logs/codex/[SESSION]/` directories
- **Environment Auto-Detection** - Automatic detection of devcontainer/codespace environments
- **Secure Configuration** - Safe .env file loading with validation and masking
- **Multiple Authentication Modes** - ChatGPT subscription or API key authentication
- **Approval Modes** - Suggest, auto-edit, or full-auto approval workflows

### Advanced Features
- **Multi-Agent Log Analysis** - Analyze logs using Claude Code agents
- **Troubleshooting Tools** - Specialized Codex CLI troubleshooting
- **Configuration Management** - TOML-based configuration with profiles
- **Session Management** - Continue and resume conversation capabilities
- **Debug Logging** - Comprehensive debug output with Rust logging support

## Installation

### Prerequisites
1. **OpenAI Codex CLI** - Install the Codex CLI tool:
   ```bash
   npm install -g @openai/codex
   ```

2. **Authentication** - Set up authentication:
   - **ChatGPT Subscription** (Recommended): Sign in to your ChatGPT account
   - **API Key**: Set `OPENAI_API_KEY` environment variable

### Setup
1. Ensure the script is executable:
   ```bash
   chmod +x scripts/launch-codex.sh
   ```

2. Optionally, create a symlink for easier access:
   ```bash
   ln -s "$(pwd)/scripts/launch-codex.sh" ~/bin/launch-codex
   ```

## Usage

### Basic Usage
```bash
# Basic query with default settings
./scripts/launch-codex.sh "Review my code for improvements"

# Interactive mode (no arguments)
./scripts/launch-codex.sh

# Continue previous conversation
./scripts/launch-codex.sh -c "Add error handling"

# Start fresh conversation
./scripts/launch-codex.sh --no-continue "New feature request"
```

### Authentication Modes
```bash
# Use ChatGPT subscription (default)
./scripts/launch-codex.sh --auth-mode chatgpt "Optimize this function"

# Use API key authentication
./scripts/launch-codex.sh --auth-mode api-key "Refactor this code"
```

### Approval Modes
```bash
# Suggest mode - review changes before applying (default)
./scripts/launch-codex.sh --suggest "Fix this bug"

# Auto-edit mode - apply changes with confirmation
./scripts/launch-codex.sh --auto-edit "Implement feature X"

# Full-auto mode - apply changes without confirmation
./scripts/launch-codex.sh --full-auto "Add tests"
```

### Configuration and Profiles
```bash
# Use specific configuration file
./scripts/launch-codex.sh --config ~/.codex/work-config.toml "Work task"

# Use specific profile
./scripts/launch-codex.sh --profile work "Enterprise development"

# Combine profile and approval mode
./scripts/launch-codex.sh --profile production --suggest "Production fix"
```

### Logging and Debugging
```bash
# Enable verbose logging (default for non-interactive)
./scripts/launch-codex.sh --verbose "Debug this issue"

# Force logging in interactive mode
./scripts/launch-codex.sh --force-logs

# Custom log file
./scripts/launch-codex.sh --log-file custom.log "Custom logging"

# Disable all logging
./scripts/launch-codex.sh --no-logs --quiet "Quick query"
```

### Advanced Features
```bash
# Analyze existing logs with Claude Code agents
./scripts/launch-codex.sh --analyze-logs

# Troubleshoot Codex CLI issues
./scripts/launch-codex.sh --troubleshoot-codex

# Clean all session logs
./scripts/launch-codex.sh --clean-logs

# Dry run to see command without execution
./scripts/launch-codex.sh --dry-run "Test command"
```

### Session Management
```bash
# Resume with interactive session selection
./scripts/launch-codex.sh --resume

# Resume specific session by ID
./scripts/launch-codex.sh --resume abc123 "Continue this work"

# Disable continue mode for fresh start
./scripts/launch-codex.sh --no-continue "Brand new conversation"
```

## Configuration

### Codex Configuration File
The script automatically loads configuration from `~/.codex/config.toml`:

```toml
[default]
model = "gpt-4"
max_tokens = 4000
temperature = 0.1

[default.auth]
mode = "chatgpt"

[work]
model = "gpt-4-turbo"
max_tokens = 8000
temperature = 0.2

[work.auth]
mode = "api-key"
api_key_env = "WORK_OPENAI_API_KEY"
```

### Environment Variables
Create `.env` files in your project root for secure configuration:

```bash
# .env
OPENAI_API_KEY=your_api_key_here
CODEX_DEFAULT_MODEL=gpt-4
CODEX_DEFAULT_PROFILE=work

# Authentication
WORK_OPENAI_API_KEY=work_specific_key
```

### Environment Detection
The script automatically detects and configures for:
- **Devcontainers** - Enables `--dangerously-skip-permissions`
- **GitHub Codespaces** - Optimizes for cloud environment
- **Docker containers** - Adjusts permission handling
- **Local environments** - Standard configuration

## Session-Based Logging

### Log Directory Structure
```
.acf/logs/codex/
├── 20250812-143022/           # Session timestamp
│   ├── session-20250812-143022.log      # Main session log
│   ├── codex-20250812-143022.log        # Codex-specific output
│   ├── debug-20250812-143022.log        # Debug information
│   ├── telemetry-20250812-143022.log    # Telemetry data
│   └── session-info-20250812-143022.txt # Session metadata
└── 20250812-150134/           # Another session
    └── ...
```

### Log Analysis
Use built-in log analysis for insights:
```bash
# Analyze recent sessions for patterns and issues
./scripts/launch-codex.sh --analyze-logs

# Specialized troubleshooting analysis
./scripts/launch-codex.sh --troubleshoot-codex
```

## Integration with AI Code Forge

### Shared Utilities
The script uses `scripts/lib/launcher-utils.sh` for common functionality:
- Environment detection and auto-configuration
- Secure .env file loading with validation
- Session-based logging setup
- Security validation functions

### Worktree Integration
Works seamlessly with the AI Code Forge worktree system:
```bash
# Use within a worktree
cd /workspace/worktrees/my-feature/
./scripts/launch-codex.sh "Implement this feature"
```

### Agent Integration
Built-in integration with Claude Code agents for:
- **Log Analysis** - Pattern detection and insight generation
- **Troubleshooting** - Systematic problem diagnosis
- **Performance Analysis** - Resource usage and optimization

## Security Features

### Input Validation
- Command injection prevention in .env values
- File size limits and permission validation
- Secure handling of sensitive environment variables

### Environment Variable Masking
Sensitive values are automatically masked in debug output:
```bash
# Masked output in logs
API_KEY=***masked***
TOKEN=***masked***
SECRET=***masked***
```

### Safe Configuration Loading
- Validates .env file permissions
- Prevents loading world-readable files
- Sanitizes configuration values

## Troubleshooting

### Common Issues

#### 1. Codex CLI Not Found
```bash
❌ Error: Missing required tools for Codex CLI:
   - codex

💡 Install Codex CLI with: npm install -g @openai/codex
💡 Or visit: https://github.com/openai/codex
```

**Solution**: Install the OpenAI Codex CLI as shown above.

#### 2. Authentication Issues
```bash
❌ Error: Authentication failed
```

**Solutions**:
- For ChatGPT mode: Ensure you're signed in to ChatGPT
- For API key mode: Set `OPENAI_API_KEY` environment variable
- Check your subscription status and API key validity

#### 3. Configuration File Issues
```bash
ℹ️  No Codex configuration file found at ~/.codex/config.toml
```

**Solution**: Create a configuration file or use `--config` to specify location.

#### 4. Permission Issues
```bash
❌ Error: Permission denied
```

**Solution**: Use `--skip-permissions` flag or ensure proper file permissions.

### Debug Mode
Enable comprehensive debugging:
```bash
./scripts/launch-codex.sh --debug --verbose "Debug this issue"
```

This will show:
- Environment detection results
- Configuration loading steps
- Command construction details
- Detailed execution information

### Log Analysis for Troubleshooting
Use the built-in troubleshooting tools:
```bash
# Comprehensive troubleshooting analysis
./scripts/launch-codex.sh --troubleshoot-codex

# General log analysis
./scripts/launch-codex.sh --analyze-logs
```

## Command Reference

### All Options
```
-h, --help                Show help message
-q, --quiet              Disable verbose mode
--no-debug               Disable debug mode
--no-logs                Disable log saving
--force-logs             Force enable logging in interactive mode
-m, --model MODEL        Set model (default: gpt-4)
--log-file FILE          Custom log file
-c, --continue           Continue most recent conversation
--no-continue            Start new conversation
-r, --resume [ID]        Resume conversation (optional session ID)
--dry-run                Show command without execution
--analyze-logs           Analyze logs with Claude Code agents
--clean-logs             Remove all session directories
--troubleshoot-codex     Troubleshoot Codex CLI issues
--skip-permissions       Skip permission checks
--no-skip-permissions    Enforce permission checks
--no-env                 Disable .env file loading
--env-file FILE          Load specific .env file
--auth-mode MODE         Authentication: "chatgpt" or "api-key"
--profile PROFILE        Configuration profile
--approval-mode MODE     Approval: "suggest", "auto-edit", "full-auto"
--config FILE            Specific config file
--suggest                Suggest approval mode
--auto-edit              Auto-edit approval mode
--full-auto              Full-auto approval mode
```

## Examples

### Development Workflow
```bash
# Start development session with auto-edit
./scripts/launch-codex.sh --auto-edit --profile dev "Implement user authentication"

# Continue working on the same feature
./scripts/launch-codex.sh -c "Add password validation"

# Review and analyze the session
./scripts/launch-codex.sh --analyze-logs
```

### Production Workflow
```bash
# Production environment with safety checks
./scripts/launch-codex.sh --suggest --profile production "Fix critical bug"

# Troubleshoot production issues
./scripts/launch-codex.sh --troubleshoot-codex
```

### Quick Tasks
```bash
# Quick code review without logging
./scripts/launch-codex.sh --no-logs --quiet "Quick code review"

# Test command construction
./scripts/launch-codex.sh --dry-run "Test this"
```

## Integration Examples

### CI/CD Integration
```bash
# In CI/CD pipeline
./scripts/launch-codex.sh --no-logs --auth-mode api-key --full-auto "Run automated code review"
```

### IDE Integration
```bash
# From IDE terminal
./scripts/launch-codex.sh --auto-edit --log-file ide-session.log "Refactor selected code"
```

### Team Workflows
```bash
# Team lead analysis
./scripts/launch-codex.sh --analyze-logs

# Shared configuration
./scripts/launch-codex.sh --config /shared/team-codex-config.toml --profile team "Team task"
```