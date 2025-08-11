# DevContainer VS Code Launch Script

A shell script solution for launching VS Code directly into running DevContainers, eliminating the need for manual "Reopen in Container" steps.

## Overview

This script (`devcontainer-code.sh`) provides one-command access to containerized development environments by:

1. **Detecting running DevContainers** using repository labels from your existing setup
2. **Using DevContainer CLI** (Microsoft's official automation tool) for reliable connection
3. **Launching VS Code** directly into the container workspace
4. **Providing fallback methods** if primary approach fails

## Usage

```bash
# Launch VS Code in DevContainer (basic usage)
./scripts/devcontainer-code.sh

# Enable debug output
./scripts/devcontainer-code.sh --debug

# Preview actions without execution
./scripts/devcontainer-code.sh --dry-run

# Show help
./scripts/devcontainer-code.sh --help
```

## Prerequisites

### Required
- **VS Code** installed with `code` command available in PATH
- **Docker** running with existing DevContainer

### Recommended
- **DevContainer CLI** for best results:
  ```bash
  npm install -g @devcontainers/cli
  ```

## How It Works

### Container Detection Strategy
1. **Primary**: Uses repository label `my.repositoryName=ai-code-forge` (from existing DevContainer setup)
2. **Fallback**: Searches for any container with `devcontainer.metadata` label
3. **Error handling**: Provides clear instructions if no containers found

### Connection Methods
1. **DevContainer CLI**: `devcontainer exec --workspace-folder ... --container-id ... code /workspace`
2. **Docker exec**: `docker exec <container> code /workspace`
3. **Manual fallback**: Opens VS Code with instructions for manual connection

### Integration with Existing Setup

Works seamlessly with your current DevContainer configuration:
- ✅ **No modifications** to `.devcontainer/devcontainer.json`
- ✅ **Uses existing labels** (`my.repositoryName=${localWorkspaceFolderBasename}`)
- ✅ **Respects workspace structure** (`/workspace` mount point)
- ✅ **Maintains permissions** (vscode user, existing setup)

## Troubleshooting

### "No running DevContainer found"
Ensure your DevContainer is running:
1. Open VS Code in project directory
2. Command Palette → "Dev Containers: Reopen in Container"
3. Wait for container to start, then try script again

### "DevContainer CLI not found"
Install the official CLI:
```bash
npm install -g @devcontainers/cli
```
The script will use fallback methods without it, but CLI provides better reliability.

### "VS Code doesn't connect properly"
The script includes multiple fallback approaches:
1. If DevContainer CLI fails → tries direct docker exec
2. If docker exec fails → opens VS Code with manual instructions
3. Provides container ID for manual "Attach to Running Container"

### Debug Mode
Use `--debug` flag to see detailed execution:
```bash
./scripts/devcontainer-code.sh --debug
```

## Technical Details

### Why This Approach Works
- **Uses official tools**: DevContainer CLI is Microsoft's recommended automation approach
- **Leverages existing labels**: Your DevContainer setup already includes perfect identification
- **Multiple fallbacks**: Graceful degradation if primary methods fail
- **No container changes**: Works with existing setup without modifications

### Why URI Schemes Don't Work
Research confirmed that `vscode-remote://attached-container+<id>/workspace` is not officially supported:
- These are internal VS Code URI schemes not intended for external use
- They change between VS Code versions without notice
- Microsoft intentionally limits access to ensure proper container state management

### Alternative Approaches Considered
1. **VS Code Remote URI**: Unreliable, breaks between versions
2. **Extension API**: Requires VS Code extension development
3. **Manual methods**: Defeats automation purpose

The DevContainer CLI approach is the most reliable and future-proof solution.

## Integration Examples

### With existing launch-claude.sh
```bash
#!/bin/bash
# Launch DevContainer VS Code, then start Claude Code
./scripts/devcontainer-code.sh
sleep 3  # Give VS Code time to connect
./scripts/launch-claude.sh
```

### As alias for convenience
Add to your shell profile:
```bash
alias dev-code='./scripts/devcontainer-code.sh'
```

## Future Enhancements

Potential improvements (if needed):
- Support for multiple workspace folders
- Integration with worktree scripts
- Container health checking before launch
- Support for remote DevContainers (Codespaces, etc.)

## References

- [DevContainer CLI Documentation](https://code.visualstudio.com/docs/devcontainers/devcontainer-cli)
- [VS Code DevContainers Guide](https://code.visualstudio.com/docs/devcontainers/containers)
- [GitHub Issue #158](https://github.com/ondrasek/ai-code-forge/issues/158) - Original request