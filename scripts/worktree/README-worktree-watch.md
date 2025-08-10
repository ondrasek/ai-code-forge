# Worktree Watch - Claude Code Monitoring

A terminal-based monitoring system for Claude Code instances and their associated worktrees, providing real-time process monitoring and GitHub issue integration. 

Part of the worktree management suite - use via `./worktree.sh watch` command.

## Overview

The Worktree Watch tool (`worktree-watch.sh`) provides a "top"-like interface for monitoring Claude Code processes, their resource usage, and their association with git worktrees and GitHub issues.

## Features

### Core Monitoring
- **Process Detection**: Automatically finds and monitors Claude Code processes
- **Resource Monitoring**: Displays CPU and memory usage for each process
- **Worktree Association**: Best-effort association of processes with specific worktrees
- **Real-time Updates**: Refreshes process data every 10 seconds

### GitHub Integration
- **Issue Metadata**: Fetches issue titles, states, labels, and update times
- **Branch-Issue Mapping**: Automatically associates branches with GitHub issues
- **Rate Limiting Protection**: Caches GitHub data for 5+ minutes to respect API limits
- **Offline Capability**: Graceful degradation when GitHub API is unavailable

### Display Features
- **Terminal Dashboard**: Professional terminal-based interface with tables
- **Color Coding**: Visual indicators for different data types and states  
- **Responsive Layout**: Adapts to different terminal sizes
- **Status Information**: Shows cache status and refresh timings

## Installation

### Prerequisites

**Required:**
- Bash 4.0+ (for associative arrays)
- Git (for worktree operations)

**Recommended:**
- [GitHub CLI (`gh`)](https://cli.github.com/) - For GitHub integration
- [`jq`](https://stedolan.github.io/jq/) - For JSON parsing
- `pwdx` or `/proc/PID/cwd` - For process-worktree association (Linux)

### Setup

1. The script is automatically executable as part of the worktree management suite:
   ```bash
   ./worktree.sh watch
   ```

2. Configure GitHub CLI (optional but recommended):
   ```bash
   gh auth login
   ```

3. Run the dashboard:
   ```bash
   ./scripts/monitoring/claude-dashboard.sh
   ```

## Usage

### Basic Usage

```bash
# Start the dashboard
./scripts/monitoring/claude-dashboard.sh

# Test mode (single display, no loop)
./scripts/monitoring/claude-dashboard.sh --test

# Enable debug mode
DEBUG_MODE=true ./scripts/monitoring/claude-dashboard.sh
```

### Dashboard Interface

The dashboard displays three main sections:

#### 1. Worktrees & Issues
```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 131 (622652b7)                 │ #131: Implement Claude Code monitoring... [OPEN]   │
│ ai-code-forge (622652b7)       │ No issue found                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

#### 2. Claude Code Processes
```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ PID      │ CPU%     │ MEM%     │ Worktree                       │ Working Dir          │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ 15649    │ 10.5     │ 4.9      │ 131                            │ 131                  │
│ 3597     │ 9.4      │ 5.4      │ ai-code-forge                  │ ai-code-forge        │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

#### 3. Status Bar
```
GitHub API: Cached (45s ago) │ Refresh: 10s │ Press Ctrl+C to exit
```

## Configuration

### Environment Variables

- `DEBUG_MODE`: Enable debug logging (default: `false`)
- `REFRESH_INTERVAL_PROCESS`: Process refresh interval in seconds (default: `10`)
- `REFRESH_INTERVAL_GITHUB`: GitHub API refresh interval in seconds (default: `300`)

### Cache Location

The dashboard stores cache and log files in:
- `~/.cache/claude-dashboard/github_cache.json` - GitHub API cache
- `~/.cache/claude-dashboard/dashboard.log` - Application logs

## Branch-to-Issue Association

The dashboard automatically detects issue numbers from branch names using these patterns:

| Branch Pattern | Example | Detected Issue |
|----------------|---------|----------------|
| Direct number | `131` | `#131` |
| Feature branch | `feature/131` | `#131` |
| Descriptive | `claude-131-dashboard` | `#131` |
| Underscore | `feature_131` | `#131` |

## Process-Worktree Association

The dashboard uses a "longest path match" algorithm to associate Claude Code processes with worktrees:

1. **Process Detection**: Finds processes matching "claude" pattern
2. **Working Directory**: Gets process working directory via `pwdx` or `/proc/PID/cwd`
3. **Path Matching**: Matches process CWD to worktree roots using longest prefix
4. **Display**: Shows associated worktree or "<unassociated>" for orphaned processes

## Troubleshooting

### Common Issues

**No Claude processes found:**
- Ensure Claude Code is running
- Check if process names match the search pattern
- Try debug mode: `DEBUG_MODE=true ./claude-dashboard.sh`

**GitHub integration not working:**
- Install and authenticate GitHub CLI: `gh auth login`
- Check network connectivity
- Verify repository access: `gh repo view ondrasek/ai-code-forge`

**Process-worktree association issues:**
- Ensure processes are running within worktree directories
- Check `pwdx` availability: `command -v pwdx`
- Verify `/proc/PID/cwd` access on Linux systems

### Debug Mode

Enable debug mode for detailed logging:
```bash
DEBUG_MODE=true ./scripts/monitoring/claude-dashboard.sh --test
```

Check logs:
```bash
tail -f ~/.cache/claude-dashboard/dashboard.log
```

## Technical Details

### Architecture

- **Data Collection**: Separate functions for processes, worktrees, and GitHub data
- **Caching Layer**: GitHub API responses cached with TTL to prevent rate limiting
- **Display Engine**: Terminal-based rendering with color coding and formatting
- **Error Handling**: Graceful degradation for missing dependencies

### Performance

- **GitHub API**: Respects rate limits with 5-minute default caching
- **Process Monitoring**: Efficient `ps` command usage with targeted filtering
- **Memory Usage**: Associative arrays for O(1) data lookup
- **Terminal Updates**: Optimized screen clearing and rendering

### Security Considerations

- **GitHub Tokens**: Uses GitHub CLI's secure token storage
- **Process Privacy**: Read-only process information, no memory inspection
- **File Permissions**: Cache files created with user permissions only
- **Command Injection**: Safe parameter handling throughout

## Implementation Status

**Phase 2 Complete** - Core implementation finished with:

✅ **Process Monitoring**: Real-time Claude Code process detection and resource monitoring  
✅ **Worktree Integration**: Comprehensive worktree enumeration and association  
✅ **GitHub API**: Full integration with caching and rate limiting  
✅ **Terminal Dashboard**: Professional dashboard interface with formatted display  
✅ **Issue Association**: Multi-pattern branch-to-issue number detection  
✅ **Error Handling**: Graceful degradation and comprehensive logging  
✅ **Cross-platform**: Linux primary with macOS considerations  
✅ **Documentation**: Complete usage and troubleshooting documentation  

**Ready for Phase 3**: Pull request preparation with comprehensive testing strategy.

---

*Created for GitHub Issue #131 - Claude Code monitoring dashboard implementation*