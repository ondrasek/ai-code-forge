# VS Code DevContainer Direct Launch Script

## Overview

The `devcontainer-code.sh` script automates launching VS Code locally and connecting it directly to a running DevContainer, eliminating the need for manual "Reopen in DevContainer" commands.

## Problem Solved

**Before**: Manual workflow requiring:
1. Launch VS Code (`code .`)
2. Command Palette → "Remote-Containers: Reopen in Container"
3. Wait for container to start/connect
4. Navigate to workspace

**After**: One command workflow:
```bash
./scripts/devcontainer-code.sh
```

## Requirements

- **VS Code** with Remote-Containers extension installed
- **Docker** running with DevContainer already started
- **DevContainer** configured with proper labeling (already set in this project)

## Usage

### Basic Usage
```bash
# Launch VS Code connected to DevContainer
./scripts/devcontainer-code.sh

# With debug output to see what's happening
./scripts/devcontainer-code.sh --debug

# Preview actions without executing (for testing)
./scripts/devcontainer-code.sh --dry-run

# Show help
./scripts/devcontainer-code.sh --help
```

### Integration with Existing Scripts
```bash
# Can be combined with existing launch-claude.sh workflow
./scripts/launch-claude.sh && ./scripts/devcontainer-code.sh
```

## How It Works

### Container Detection
The script uses the existing DevContainer labeling system:
```bash
# From .devcontainer/devcontainer.json
"runArgs": [
  "--label", "my.repositoryName=${localWorkspaceFolderBasename}"
]
```

Detection process:
1. **Primary**: Find container by label `my.repositoryName=ai-code-forge`
2. **Fallback**: Find container by name pattern if label missing
3. **Validation**: Ensure container is running and accessible

### VS Code Connection Methods
The script tries multiple connection approaches in order:

1. **Method 1: Direct Remote Connection**
   ```bash
   code --remote attached-container+<container-id> /workspace
   ```

2. **Method 2: Folder URI Scheme**
   ```bash
   code --folder-uri "vscode-remote://attached-container+<container-id>/workspace"
   ```

3. **Method 3: Container Name Connection**
   ```bash
   code --remote attached-container+<container-name> /workspace
   ```

### Error Handling
- **Dependencies**: Validates Docker and VS Code CLI availability
- **Container Detection**: Clear error messages if no container found
- **Method Fallbacks**: Tries multiple connection approaches
- **Manual Recovery**: Provides fallback instructions if all methods fail

## Technical Details

### Container Requirements
The DevContainer must be:
- **Running**: `docker ps` shows it as active
- **Labeled**: Contains `my.repositoryName=ai-code-forge` label
- **Accessible**: VS Code can connect to it
- **Workspace Ready**: `/workspace` folder accessible

### VS Code Requirements
- **Remote-Containers Extension**: Must be installed and enabled
- **CLI Access**: `code` command available in PATH
- **Permissions**: Sufficient permissions to connect to Docker containers

### Supported Platforms
- **Linux**: Full support (primary development environment)
- **macOS**: Should work with Docker Desktop
- **Windows/WSL**: Should work with Docker Desktop and WSL setup

## Troubleshooting

### Common Issues

**1. "No running DevContainer found"**
```bash
# Check if container is running
docker ps --filter "label=my.repositoryName=ai-code-forge"

# If empty, start DevContainer first:
code . # Then use "Reopen in Container"
```

**2. "Docker is not running"**
```bash
# Start Docker service
sudo systemctl start docker  # Linux
# Or start Docker Desktop      # macOS/Windows
```

**3. "VS Code CLI not found"**
```bash
# Install VS Code CLI access
# In VS Code: Command Palette → "Shell Command: Install 'code' command in PATH"
```

**4. "All VS Code connection methods failed"**
- Check VS Code Remote-Containers extension is installed
- Try manual connection as fallback:
  1. Run `code .`
  2. Command Palette → "Remote-Containers: Attach to Running Container"
  3. Select your container
  4. Open `/workspace` folder

### Debug Mode
Use `--debug` flag to see detailed execution:
```bash
./scripts/devcontainer-code.sh --debug
```

This shows:
- Container detection process
- Which connection method is being tried
- Container details (ID, name, image)
- Connection attempt results

### Container Inspection
```bash
# List all DevContainers
docker ps --filter "label=my.repositoryName"

# Get specific container details
docker inspect <container-id>

# Check container logs
docker logs <container-id>
```

## Integration Examples

### With launch-claude.sh
```bash
#!/bin/bash
# Combined launcher script
./scripts/launch-claude.sh
if [ $? -eq 0 ]; then
    echo "Launching VS Code in DevContainer..."
    ./scripts/devcontainer-code.sh
fi
```

### With Alias
Add to your `.bashrc` or `.zshrc`:
```bash
alias dev-code='cd /path/to/ai-code-forge && ./scripts/devcontainer-code.sh'
```

### With IDE Launch
For IDEs like IntelliJ IDEA with terminal integration:
```bash
# Terminal command in IDE
./scripts/devcontainer-code.sh --debug
```

## Development Notes

### Extending the Script
The script is designed for extensibility:
- Add new connection methods in the `methods` array
- Modify container detection logic in `detect_devcontainer()`
- Update validation in `check_dependencies()`

### Testing Changes
```bash
# Test without launching VS Code
./scripts/devcontainer-code.sh --dry-run --debug

# Validate container detection
docker ps --filter "label=my.repositoryName=ai-code-forge"
```

### Performance Considerations
- Container detection is fast (single Docker query)
- VS Code launch time depends on extension loading
- First connection may take longer than subsequent ones

## Security Considerations

### Docker Access
- Script requires Docker access (docker group membership or sudo)
- No privileged container operations performed
- Only reads container metadata and connects VS Code

### VS Code Connection
- Uses standard VS Code Remote-Containers extension
- No custom network access or port forwarding
- Follows VS Code security model

## Future Enhancements

### Potential Improvements
1. **Multi-Container Support**: Handle multiple DevContainers per project
2. **Auto-Start**: Start DevContainer if not running
3. **Profile Support**: Different VS Code configurations per project
4. **Integration**: Deeper integration with existing ai-code-forge tools

### VS Code CLI Evolution
Monitor VS Code releases for:
- New remote connection CLI options
- DevContainer CLI integration improvements
- URI scheme updates

The script is designed to be maintainable as VS Code evolves its DevContainer CLI capabilities.