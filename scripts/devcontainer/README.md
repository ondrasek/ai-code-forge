# DevContainer VS Code Launch Scripts

This directory contains scripts for launching VS Code directly into DevContainer environments, providing one-command access to containerized development setups.

## Quick Start

```bash
# Launch VS Code in DevContainer (from project root)
./scripts/devcontainer-code.sh

# With debug output
./scripts/devcontainer-code.sh --debug

# Force restart container before launch  
./scripts/devcontainer-code.sh --force-restart
```

## How It Works

The solution uses the modern **DevContainer CLI + VS Code** approach instead of broken URI schemes:

1. **DevContainer CLI** manages container lifecycle (`devcontainer up`)
2. **VS Code** launches normally (`code .`) and auto-detects the container
3. **VS Code Dev Containers extension** handles the connection automatically

This avoids the problematic `vscode-remote://attached-container+<id>/workspace` URI scheme that doesn't work in practice.

## Prerequisites

### Required Dependencies

- **VS Code** with Dev Containers extension
- **DevContainer CLI**: `npm install -g @devcontainers/cli`  
- **Docker** (running and accessible)

### Auto-Installation

The script will attempt to install DevContainer CLI automatically if npm is available:

```bash
# Automatic installation during script execution
npm install -g @devcontainers/cli
```

## Scripts

### `devcontainer-code.sh`

Main launch script with comprehensive error handling and validation.

**Features:**
- ✅ Dependency validation with helpful error messages
- ✅ DevContainer configuration validation  
- ✅ Container state detection and management
- ✅ Graceful fallbacks and error recovery
- ✅ Debug mode with detailed logging
- ✅ Dry-run mode for testing
- ✅ Force restart option for container issues
- ✅ Cross-platform compatibility (Linux, macOS, Windows/WSL)

**Options:**
```bash
./scripts/devcontainer-code.sh [options]

Options:
  --debug           Enable debug output
  --force-restart   Force restart container before launch  
  --dry-run         Preview actions without execution
  --help           Show help message
```

**Error Handling:**
- Missing dependencies → Installation guidance
- Invalid configuration → JSON validation errors  
- Container issues → Restart and retry logic
- VS Code problems → Manual connection instructions

## DevContainer Configuration

The `.devcontainer/devcontainer.json` configuration is optimized for AI Code Forge development:

### Key Features

- **Base Image**: `mcr.microsoft.com/devcontainers/python:3.13-bullseye`
- **Node.js 20** for npm-based tools
- **GitHub CLI** for repository management
- **Docker-outside-Docker** for container operations within container
- **Zsh + Oh My Zsh** for enhanced terminal experience

### VS Code Integration

**Pre-installed Extensions:**
- Claude Code (anthropic.claude-code)
- Python development tools
- GitHub integration
- Language support for multiple stacks

**Optimized Settings:**
- Python interpreter configuration
- Git auto-fetch enabled  
- Terminal defaults to Zsh
- Extensions auto-update disabled (for stability)

### Container Environment

**Environment Variables:**
- `DEVCONTAINER=true` for detection in launch-claude.sh
- `NODE_OPTIONS=--max-old-space-size=4096` for memory management

**Post-Setup Commands:**
- Pip and uv installation/upgrade
- DevContainer CLI global installation
- Script permissions setup

## Integration with Existing Infrastructure

### launch-claude.sh Integration

The existing `scripts/launch-claude.sh` already detects DevContainer environments:

```bash
# From launch-claude.sh
detect_environment() {
    if [[ -n "${DEVCONTAINER:-}" ]]; then
        echo "🔍 Detected devcontainer environment"
        SKIP_PERMISSIONS="true" 
    fi
}
```

### Workflow Integration

**Development Workflow:**
1. `./scripts/devcontainer-code.sh` - Launch VS Code in container
2. VS Code automatically connects to DevContainer
3. `./scripts/launch-claude.sh` - Enhanced Claude Code setup (auto-detects container)
4. Development work with full AI Code Forge capabilities

## Troubleshooting

### Common Issues

**1. "No DevContainer configuration found"**
```bash
# Ensure .devcontainer/devcontainer.json exists
ls -la .devcontainer/
```

**2. "Docker daemon not running"**
```bash
# Start Docker Desktop or Docker service
sudo systemctl start docker  # Linux
# or open Docker Desktop     # macOS/Windows
```

**3. "DevContainer CLI not found"**
```bash
# Install DevContainer CLI
npm install -g @devcontainers/cli

# Verify installation
devcontainer --version
```

**4. "VS Code not connecting to container"**
- Check VS Code bottom-left corner for "Dev Container" indicator
- Use Command Palette: "Dev Containers: Reopen in Container"
- Restart VS Code if connection fails

**5. "Container fails to start"**
```bash
# Check container logs
docker logs $(docker ps -aq | head -1)

# Force restart
./scripts/devcontainer-code.sh --force-restart

# Clean rebuild
devcontainer down --workspace-folder .
devcontainer up --workspace-folder .
```

### Debug Mode

Enable comprehensive logging:

```bash
./scripts/devcontainer-code.sh --debug
```

**Debug Output Includes:**
- Dependency version information
- Container detection logic
- Command execution details  
- VS Code integration status
- Environment variable settings

### Manual Recovery

If automated launch fails, manual steps:

```bash
# 1. Start DevContainer manually
cd /path/to/ai-code-forge
devcontainer up --workspace-folder .

# 2. Launch VS Code
code .

# 3. Connect via Command Palette
# Ctrl+Shift+P > "Dev Containers: Attach to Running Container"
```

## Advanced Usage

### Custom DevContainer Configuration

Modify `.devcontainer/devcontainer.json` for project-specific needs:

**Adding Features:**
```json
{
  "features": {
    "ghcr.io/devcontainers/features/rust:1": {
      "version": "latest"
    }
  }
}
```

**Custom Extensions:**
```json
{
  "customizations": {
    "vscode": {
      "extensions": [
        "your.custom.extension"
      ]
    }
  }
}
```

### Performance Optimization

**For Large Projects:**
- Use `.dockerignore` to exclude unnecessary files
- Enable buildkit: `DOCKER_BUILDKIT=1`
- Consider pre-built images for faster startup

**Memory Management:**
- Adjust `NODE_OPTIONS` in container environment
- Monitor container resource usage: `docker stats`

## Security Considerations

### Container Security

- Uses non-root user (`vscode`) for container operations
- Docker socket mounting is required for Docker-outside-Docker
- GitHub CLI authentication is isolated within container

### File Permissions

- `updateRemoteUserUID: true` maintains file ownership
- Scripts are made executable via postCreateCommand
- Git configuration preserved between host/container

## Contributing

### Adding New Scripts

1. Place scripts in `scripts/devcontainer/`
2. Follow existing naming convention: `devcontainer-*.sh`  
3. Include help text and error handling
4. Update this README with usage instructions

### Testing

```bash
# Test with dry-run mode
./scripts/devcontainer-code.sh --dry-run

# Test with debug output
./scripts/devcontainer-code.sh --debug

# Test force restart scenario
./scripts/devcontainer-code.sh --force-restart
```

## External References

- [VS Code DevContainers Documentation](https://code.visualstudio.com/docs/devcontainers/containers)
- [DevContainer CLI Reference](https://containers.dev/implementors/cli/)
- [DevContainer Features Registry](https://containers.dev/features)
- [GitHub Codespaces CLI Pattern](https://docs.github.com/en/codespaces/developing-in-codespaces/using-github-codespaces-with-github-cli)