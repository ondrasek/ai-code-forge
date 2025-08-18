# Claude Code Debugging Scripts

These scripts provide practical debugging and analytics capabilities for Claude Code using only documented features.

## Scripts Overview

### 🔍 `debug-claude.sh`
Enhanced debugging wrapper that captures Claude Code's stdout/stderr output.

**Usage:**
```bash
./scripts/debug-claude.sh "Create a GitHub issue"
```

**Features:**
- Captures Claude Code's stdout and stderr streams
- Sets debug environment variables (ANTHROPIC_LOG=debug)
- Splits captured output by content type (general, MCP-specific)
- Creates timestamped log directories with all captured output

**Important:** Claude Code doesn't create log files automatically - this script captures its console output and saves it to files.

**Output:**
- `logs/debug/YYYYMMDD_HHMMSS/verbose.log` - Complete stdout capture
- `logs/debug/YYYYMMDD_HHMMSS/stderr.log` - Complete stderr capture  
- `logs/debug/YYYYMMDD_HHMMSS/claude-debug.log` - Combined output
- `logs/debug/YYYYMMDD_HHMMSS/mcp-debug.log` - MCP-related output filtered from captured streams

### 🔧 `analyze-mcp.sh`
Analyzes MCP server configuration and connectivity.

**Usage:**
```bash
./scripts/analyze-mcp.sh
```

**Features:**
- Lists configured MCP servers
- Shows server details and configuration
- Checks for MCP configuration files
- Displays relevant environment variables

### 📊 `track-usage.sh`
Basic usage pattern tracking with timing and success metrics.

**Usage:**
```bash
./scripts/track-usage.sh "Your query here"
```

**Features:**
- Logs query timing and success rates
- Tracks output sizes and execution duration
- Creates daily usage log files
- Sanitizes sensitive query content

**Output:**
- `logs/usage/claude-usage-YYYYMMDD.log` - Daily usage statistics

### 📈 `analyze-usage.sh`
Analyzes usage logs to show patterns and statistics.

**Usage:**
```bash
./scripts/analyze-usage.sh
```

**Features:**
- Aggregates statistics across all usage logs
- Shows success rates and average durations
- Displays recent activity summary
- Calculates performance metrics

### ✅ `validate-mcp-config.sh`
Validates MCP server configurations and tests connectivity.

**Usage:**
```bash
./scripts/validate-mcp-config.sh
```

**Features:**
- Validates JSON configuration files
- Tests server accessibility
- Checks for common configuration issues
- Reports server status and availability

## Environment Variables

These scripts use the following environment variables for enhanced debugging:

```bash
export ANTHROPIC_LOG=debug              # Enable debug output to stderr
export CLAUDE_CODE_ENABLE_TELEMETRY=1   # Enable telemetry output
export MCP_TIMEOUT=30000                # MCP server timeout (ms)
```

**Important:** These environment variables affect Claude Code's stdout/stderr output, not log file creation. The scripts capture this output and save it to log files.

## Dependencies

- **bash** (required)
- **jq** (optional, for JSON validation)
- **bc** (required for duration calculations)
- **timeout** (optional, for server testing)

## Example Workflows

### Debug MCP Server Issues
```bash
# 1. Analyze current MCP configuration
./scripts/analyze-mcp.sh

# 2. Validate MCP setup
./scripts/validate-mcp-config.sh

# 3. Run debug session with MCP usage
./scripts/debug-claude.sh "Use the github MCP server to create an issue"

# 4. Review MCP-specific debug output
less logs/debug/*/mcp-debug.log
```

### Track Usage Patterns
```bash
# 1. Track several queries
./scripts/track-usage.sh "Read the README file"
./scripts/track-usage.sh "Create a simple Python script"
./scripts/track-usage.sh "Analyze the codebase structure"

# 2. Analyze usage patterns
./scripts/analyze-usage.sh
```

### Comprehensive Analysis
```bash
# 1. Initial setup analysis
./scripts/analyze-mcp.sh
./scripts/validate-mcp-config.sh

# 2. Run tracked debug session
./scripts/track-usage.sh "$(echo 'Complex query with MCP usage')"

# 3. Capture detailed debug output
./scripts/debug-claude.sh "Same complex query for detailed analysis"

# 4. Review all results
./scripts/analyze-usage.sh
ls logs/debug/*/
```

## Limitations

These scripts work within Claude Code's actual capabilities:

- **No automatic log files** - Claude Code doesn't create log files; we capture stdout/stderr
- **No sub-agent context tracking** - Cannot identify which sub-agent made which call
- **Limited MCP visibility** - Only sees what appears in Claude's debug output to console
- **Manual analysis required** - Requires manual inspection of captured output
- **Post-execution analysis** - No real-time monitoring capabilities
- **Output-dependent** - Can only analyze what Claude Code actually outputs to console

## Future Enhancements

As Claude Code capabilities evolve, these scripts can be enhanced to:

- Parse structured debug output for automated analysis
- Integrate with additional Claude Code debug flags
- Provide real-time monitoring if supported
- Export data to external analytics tools

## Troubleshooting

**Script permissions:**
```bash
chmod +x scripts/*.sh
```

**Missing dependencies:**
```bash
# Install jq for JSON validation
brew install jq  # macOS
apt-get install jq  # Ubuntu/Debian
```

**Log directory permissions:**
```bash
mkdir -p logs/{debug,usage}
chmod 755 logs/{debug,usage}
```