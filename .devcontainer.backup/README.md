# DevContainer Configuration - Repository Development

This devcontainer provides a development environment for working on the Claude Code Template repository.

## Overview

The devcontainer provides:
- **Exact Environment Match**: Mirrors the GitHub Codespace setup precisely
- **Ubuntu 24.04 LTS**: Same base OS as current Codespace (Noble Numbat)
- **Node.js 22.17.0**: Exact version match for Claude CLI compatibility
- **Python 3.12+**: With uv package manager for modern Python development
- **MCP Servers**: Perplexity research server configured and ready
- **All Tools**: Same development tools, extensions, and configurations

## Quick Start

1. **Open in DevContainer**:
   - VS Code: Use "Dev Containers: Reopen in Container" command
   - GitHub Codespaces: Will automatically use this configuration

2. **Set Environment Variables**:
   ```bash
   # Set your API keys as environment variables on your host machine
   export CLAUDE_API_KEY="your-key-here"
   export PERPLEXITY_API_KEY="your-key-here"
   
   # Make them persistent in your shell profile
   echo 'export CLAUDE_API_KEY="your-key"' >> ~/.bashrc
   echo 'export PERPLEXITY_API_KEY="your-key"' >> ~/.bashrc
   ```

3. **Validate Setup**:
   ```bash
   /tmp/validate-environment.sh
   ```

## Environment Details

### Base Configuration
- **Image**: `mcr.microsoft.com/devcontainers/universal:2-linux`
- **User**: `codespace` (matches Codespace user)
- **Shell**: bash with full alias configuration

### Installed Tools
- **Node.js**: 22.17.0 with npm 9.8.1+
- **Python**: 3.12+ with uv package manager
- **Claude CLI**: Latest version via npm
- **MCP Tools**: Inspector, client-cli, server-memory
- **Development Tools**: ruff, pytest, mypy via uv
- **System Tools**: git, docker, github-cli

### VS Code Extensions
- `anthropic.claude-code` - Claude Code integration
- `docker.docker` - Docker support  
- `github.vscode-pull-request-github` - GitHub integration
- `ms-python.python` - Python language support
- `ms-python.vscode-pylance` - Python IntelliSense
- `ms-azuretools.vscode-docker` - Docker development
- `redhat.vscode-yaml` - YAML support
- `qwtel.sqlite-viewer` - SQLite database viewer

### Environment Variables
```bash
CODESPACES=true                    # Mimics Codespace environment
CLAUDE_DEBUG=1                     # Enhanced Claude CLI debugging
MCP_DEBUG=1                        # MCP server debugging
CLAUDE_CODE_ENABLE_TELEMETRY=1     # Enable telemetry (optional)
PYTHONIOENCODING=UTF-8             # Ensure proper encoding
```

### Shell Aliases
```bash
cc='claude'                        # Quick Claude access
claude-init='claude /init'         # Initialize Claude
launch-claude='/.support/scripts/launch-claude.sh'  # Enhanced launcher
```

## Secure Secret Management

The devcontainer includes enterprise-grade secret management with multiple secure sources:

### Secret Sources (Priority Order)

1. **GitHub Codespaces** (Automatic):
   - Configure at: `https://github.com/settings/codespaces`
   - Add repository or organization secrets: `CLAUDE_API_KEY`, `PERPLEXITY_API_KEY`
   - Secrets automatically injected into container

2. **Local Environment Variables** (Development):
   ```bash
   # Set on your host machine
   export CLAUDE_API_KEY="your-key-here"
   export PERPLEXITY_API_KEY="your-key-here"
   
   # Make persistent in your shell profile
   echo 'export CLAUDE_API_KEY="your-key"' >> ~/.bashrc
   echo 'export PERPLEXITY_API_KEY="your-key"' >> ~/.bashrc
   ```

3. **Enterprise Vault Integration** (Advanced):
   ```bash
   export VAULT_TYPE="aws-secrets-manager"  # or azure-key-vault, hashicorp-vault
   export VAULT_URL="your-vault-url"
   ```

### Security Features

- **🔒 Host Isolation**: Environment variables inherited securely from host
- **🛡️ Validation**: Secret format validation and placeholder detection
- **📋 Audit Logging**: Comprehensive secret access logging
- **🧹 Cleanup**: Automatic secret cleanup on container shutdown
- **🔍 Security Scanning**: Automated detection of hardcoded secrets
- **🚫 No File Storage**: No secret files managed in git repository

### Commands

```bash
gh auth login          # GitHub authentication
claude auth status     # Verify Claude authentication
/tmp/validate-environment.sh  # Validate development environment
```

## MCP Server Configuration

The devcontainer automatically sets up the Perplexity MCP server:

- **Location**: `.support/mcp-servers/perplexity/`
- **Python Environment**: Managed by uv
- **Configuration**: `.support/mcp-servers/mcp-config.json`
- **Dependencies**: fastmcp, httpx, python-dotenv
- **Authentication**: Uses `PERPLEXITY_API_KEY` from secure secret management

## Differences from Codespace

While this devcontainer aims for exact replication, some minor differences exist:

1. **Network Environment**: Local Docker networking vs. Codespace cloud networking
2. **Resource Limits**: Depends on local machine vs. standardized Codespace resources
3. **External Services**: Some Codespace-specific integrations may not be available
4. **Performance**: Local container performance varies by host machine

## Troubleshooting

### Common Issues

**Claude CLI Not Working**:
```bash
# Verify installation
claude --version
# Check API key
echo "CLAUDE_API_KEY is set: ${CLAUDE_API_KEY:+yes}"
```

**MCP Server Issues**:
```bash
# Check Python environment
cd .support/mcp-servers/perplexity
uv run python -c "import fastmcp; print('FastMCP OK')"
```

**Permission Issues**:
```bash
# Fix common permission issues
sudo chown -R codespace:codespace ~/.claude
sudo chown -R codespace:codespace .support/logs
```

**Environment Validation**:
```bash
# Run full environment validation
/tmp/validate-environment.sh
```

### Log Files

Check these locations for debugging:
- `.support/logs/` - Claude Code session logs
- `~/.claude/` - Claude CLI configuration and logs
- Container logs via Docker Desktop or `docker logs <container-id>`

## Development Workflow

This devcontainer supports the full Claude Code development workflow:

1. **Agent Development**: Create and test agents in `.claude/agents/`
2. **Command Development**: Build custom commands in `.claude/commands/`
3. **MCP Development**: Extend or modify MCP servers in `.support/mcp-servers/`
4. **Prompt Engineering**: Develop prompts in `.support/prompts/`

## Performance Optimization

For better performance:

1. **Pre-build Images**: Consider using GitHub's pre-build feature
2. **Volume Caching**: The configuration uses cached mounts for better performance
3. **Resource Allocation**: Allocate at least 4GB RAM and 2 CPU cores to the container

## Contributing

When modifying this devcontainer configuration:

1. Test changes thoroughly against the current Codespace environment
2. Update version pins when Codespace environment updates
3. Document any new requirements or breaking changes
4. Validate with `/tmp/validate-environment.sh` after changes

## Version History

- **v1.0**: Initial exact replica of Codespace environment (Ubuntu 24.04, Node 22.17.0, Python 3.12)
- **Current**: Matches Codespace as of commit hash in repository

For the most up-to-date Codespace environment details, check the latest commits and `.support/logs/` directory.