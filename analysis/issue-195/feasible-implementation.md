# Issue #195: Feasible Implementation - Start Small with Real Claude Code Capabilities

## REALITY CHECK: What Claude Code Actually Supports

After examining Claude Code's actual capabilities, my previous complex interception schemes were **not feasible**. Here's what Claude Code really provides and a practical starting approach.

### ✅ Confirmed Claude Code Debug Capabilities

#### Available Debug Flags
```bash
# Primary debug flag
claude --debug                    # Enable debug mode (replaces --mcp-debug)
claude --verbose                  # Verbose output
claude --print                    # Non-interactive with output formats
claude --output-format stream-json # Structured output for parsing
```

#### MCP Management Commands  
```bash
claude mcp list                   # List configured MCP servers
claude mcp get <name>             # Get server details
claude mcp add <name> <cmd> [args] # Add MCP server
claude mcp remove <name>          # Remove MCP server
```

#### Environment Variables (Research-Based)
```bash
export ANTHROPIC_LOG=debug        # Enable debug logging
export CLAUDE_CODE_ENABLE_TELEMETRY=1  # Telemetry
export MCP_TIMEOUT=10000          # MCP timeout
```

### ❌ Feasibility Issues with Complex Interception

1. **No Access to Internal MCP Client**: Claude Code's MCP client is not exposed for interception
2. **No Context Propagation API**: No way to track which sub-agent is executing  
3. **No Protocol-Level Hooks**: Cannot intercept MCP calls at protocol level
4. **Limited Debug Output**: Debug flags don't provide structured analytics data

## 🎯 REALISTIC IMPLEMENTATION: Start Small

### Phase 1: Enhanced Debugging Configuration

#### 1.1 Create Debug Launch Script
**Location**: `scripts/debug-claude.sh`

```bash
#!/bin/bash
# Enhanced Claude Code debugging wrapper

set -euo pipefail

# Debug configuration
export ANTHROPIC_LOG=debug
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export MCP_TIMEOUT=30000

# Create debug log directory
DEBUG_DIR="logs/debug/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$DEBUG_DIR"

# Debug log files
DEBUG_LOG="$DEBUG_DIR/claude-debug.log"
MCP_LOG="$DEBUG_DIR/mcp-debug.log"
VERBOSE_LOG="$DEBUG_DIR/verbose.log"

echo "🔍 Starting Claude Code with enhanced debugging"
echo "📁 Debug logs: $DEBUG_DIR"

# Function to capture and split output
capture_debug_output() {
    local query="$*"
    
    echo "=== Debug Session Started: $(date) ===" >> "$DEBUG_LOG"
    echo "Query: $query" >> "$DEBUG_LOG"
    echo "" >> "$DEBUG_LOG"
    
    # Run Claude with debug and capture all output
    claude --debug --verbose --print "$query" 2>&1 | tee -a "$VERBOSE_LOG" | \
    while IFS= read -r line; do
        echo "$line"
        
        # Split logs by content type
        echo "$line" >> "$DEBUG_LOG"
        
        # Detect MCP-related output
        if [[ "$line" =~ [Mm][Cc][Pp]|server|tool ]]; then
            echo "$line" >> "$MCP_LOG"
        fi
    done
    
    echo "=== Debug Session Ended: $(date) ===" >> "$DEBUG_LOG"
    echo "" >> "$DEBUG_LOG"
}

# Execute with debug capture
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 \"your query here\""
    exit 1
fi

capture_debug_output "$@"

echo "📊 Debug logs saved to:"
echo "  General: $DEBUG_LOG"
echo "  MCP: $MCP_LOG" 
echo "  Verbose: $VERBOSE_LOG"
```

#### 1.2 MCP Server Analysis Script
**Location**: `scripts/analyze-mcp.sh`

```bash
#!/bin/bash
# Analyze MCP server configuration and test connectivity

set -euo pipefail

echo "🔍 MCP Server Analysis"
echo "====================="

# List configured servers
echo "📋 Configured MCP Servers:"
claude mcp list

echo ""
echo "🔧 MCP Server Details:"
# Get details for each server (if any exist)
while read -r server_name; do
    if [[ -n "$server_name" && "$server_name" != "No MCP servers configured"* ]]; then
        echo "Server: $server_name"
        claude mcp get "$server_name" 2>/dev/null || echo "  Failed to get details"
        echo ""
    fi
done < <(claude mcp list 2>/dev/null | tail -n +2)

# Check for MCP configuration files
echo "📄 MCP Configuration Files:"
for config_file in ".mcp.json" "mcp-servers/mcp-config.json" ".claude/mcp-servers.json"; do
    if [[ -f "$config_file" ]]; then
        echo "  ✓ Found: $config_file"
        echo "    Size: $(wc -c < "$config_file") bytes"
        echo "    Modified: $(stat -c %y "$config_file" 2>/dev/null || stat -f %Sm "$config_file" 2>/dev/null)"
    else
        echo "  ✗ Not found: $config_file"
    fi
done

echo ""
echo "🌐 Environment Variables:"
env | grep -i claude | sort
echo ""
env | grep -i mcp | sort
echo ""
env | grep -i anthropic | sort
```

### Phase 2: Basic Usage Pattern Logging

#### 2.1 Usage Tracker Script
**Location**: `scripts/track-usage.sh`

```bash
#!/bin/bash
# Basic usage pattern tracking for Claude Code

set -euo pipefail

USAGE_LOG="logs/usage/claude-usage-$(date +%Y%m%d).log"
mkdir -p "$(dirname "$USAGE_LOG")"

# Function to log usage
log_usage() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local query="$*"
    local query_length=${#query}
    
    # Basic usage metrics
    echo "$timestamp|QUERY_START|length=$query_length|query=[SANITIZED]" >> "$USAGE_LOG"
    
    # Run Claude and capture timing
    local start_time=$(date +%s.%N)
    
    # Execute with basic logging
    local output
    output=$(claude --print "$query" 2>&1)
    local exit_code=$?
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l)
    local output_length=${#output}
    
    # Log completion
    echo "$timestamp|QUERY_END|duration=${duration}s|output_length=$output_length|exit_code=$exit_code" >> "$USAGE_LOG"
    
    # Echo output
    echo "$output"
    
    return $exit_code
}

# Execute with usage tracking
log_usage "$@"
```

#### 2.2 Simple Analytics Script
**Location**: `scripts/analyze-usage.sh`

```bash
#!/bin/bash
# Simple analytics for Claude Code usage logs

set -euo pipefail

USAGE_DIR="logs/usage"

if [[ ! -d "$USAGE_DIR" ]]; then
    echo "No usage logs found. Run track-usage.sh first."
    exit 1
fi

echo "📊 Claude Code Usage Analytics"
echo "=============================="

# Find all usage log files
usage_files=($(find "$USAGE_DIR" -name "claude-usage-*.log" -type f | sort))

if [[ ${#usage_files[@]} -eq 0 ]]; then
    echo "No usage log files found."
    exit 1
fi

echo "📁 Found ${#usage_files[@]} usage log files"
echo ""

# Basic statistics
total_queries=0
total_duration=0
successful_queries=0

for log_file in "${usage_files[@]}"; do
    queries=$(grep "QUERY_START" "$log_file" | wc -l)
    completions=$(grep "QUERY_END" "$log_file" | wc -l)
    
    echo "📄 $(basename "$log_file"): $queries queries, $completions completions"
    
    total_queries=$((total_queries + queries))
    
    # Calculate durations and success rates for this file
    while IFS='|' read -r timestamp type metrics; do
        if [[ "$type" == "QUERY_END" ]]; then
            # Extract duration and exit code
            duration=$(echo "$metrics" | grep -o 'duration=[0-9.]*' | cut -d= -f2)
            exit_code=$(echo "$metrics" | grep -o 'exit_code=[0-9]*' | cut -d= -f2)
            
            if [[ -n "$duration" ]]; then
                total_duration=$(echo "$total_duration + $duration" | bc -l)
            fi
            
            if [[ "$exit_code" == "0" ]]; then
                successful_queries=$((successful_queries + 1))
            fi
        fi
    done < "$log_file"
done

echo ""
echo "📈 Summary Statistics:"
echo "  Total queries: $total_queries"
echo "  Successful queries: $successful_queries"
if [[ $total_queries -gt 0 ]]; then
    success_rate=$(echo "scale=1; $successful_queries * 100 / $total_queries" | bc -l)
    echo "  Success rate: ${success_rate}%"
fi

if [[ $successful_queries -gt 0 ]]; then
    avg_duration=$(echo "scale=2; $total_duration / $successful_queries" | bc -l)
    echo "  Average duration: ${avg_duration}s"
fi

echo ""
echo "🕐 Recent Activity (last 10 queries):"
tail -20 "${usage_files[-1]}" | grep "QUERY_" | tail -10 | while IFS='|' read -r timestamp type metrics; do
    if [[ "$type" == "QUERY_START" ]]; then
        echo "  $timestamp: Query started"
    elif [[ "$type" == "QUERY_END" ]]; then
        duration=$(echo "$metrics" | grep -o 'duration=[0-9.]*' | cut -d= -f2)
        exit_code=$(echo "$metrics" | grep -o 'exit_code=[0-9]*' | cut -d= -f2)
        status="success"
        [[ "$exit_code" != "0" ]] && status="failed"
        echo "  $timestamp: Query completed (${duration}s, $status)"
    fi
done
```

### Phase 3: MCP Server Configuration Helper

#### 3.1 MCP Configuration Validator
**Location**: `scripts/validate-mcp-config.sh`

```bash
#!/bin/bash
# Validate and test MCP server configurations

set -euo pipefail

echo "🔍 MCP Configuration Validator"
echo "============================="

# Function to validate JSON
validate_json() {
    local file="$1"
    if command -v jq >/dev/null 2>&1; then
        if jq empty < "$file" 2>/dev/null; then
            echo "  ✓ Valid JSON"
            return 0
        else
            echo "  ✗ Invalid JSON"
            return 1
        fi
    else
        echo "  ? JSON validation skipped (jq not available)"
        return 0
    fi
}

# Function to test MCP server
test_mcp_server() {
    local server_name="$1"
    echo "Testing server: $server_name"
    
    # Try to get server details
    if claude mcp get "$server_name" >/dev/null 2>&1; then
        echo "  ✓ Server configuration accessible"
    else
        echo "  ✗ Server configuration not accessible"
        return 1
    fi
    
    # Test server with a simple query
    echo "  Testing server with debug query..."
    if timeout 30s claude --debug --print "List available tools" 2>&1 | grep -q "$server_name"; then
        echo "  ✓ Server appears in debug output"
    else
        echo "  ? Server not found in debug output (may be normal)"
    fi
}

# Check configuration files
echo "📄 Configuration Files:"
for config_file in ".mcp.json" "mcp-servers/mcp-config.json"; do
    if [[ -f "$config_file" ]]; then
        echo "Found: $config_file"
        validate_json "$config_file"
        
        # Show server count if jq available
        if command -v jq >/dev/null 2>&1; then
            server_count=$(jq -r '.mcpServers | length' "$config_file" 2>/dev/null || echo "0")
            echo "  Servers defined: $server_count"
        fi
    fi
done

echo ""
echo "🔧 Configured Servers:"
# Test each configured server
claude mcp list | while read -r server_name; do
    if [[ -n "$server_name" && "$server_name" != "No MCP servers configured"* ]]; then
        test_mcp_server "$server_name"
        echo ""
    fi
done
```

## 🎯 Practical Usage for Your Scenarios

### Scenario 1: MCP Server Usage Analysis
```bash
# Start debugging session
./scripts/debug-claude.sh "Create a GitHub issue using the github MCP server"

# Analyze MCP configuration
./scripts/analyze-mcp.sh

# Validate MCP setup
./scripts/validate-mcp-config.sh
```

### Scenario 2: Tool Usage Tracking
```bash
# Track usage patterns
./scripts/track-usage.sh "Read the README file and summarize it"

# Analyze usage patterns
./scripts/analyze-usage.sh
```

### Scenario 3: Debug Output Analysis
```bash
# Generate debug output with structured logging
claude --debug --verbose --output-format stream-json --print "your query" > debug-output.json

# Parse structured output for analysis
jq '.type, .content' debug-output.json
```

## 🎭 Why This Approach is Feasible

1. **Uses Real Claude Code Features**: Only leverages documented debug flags and commands
2. **No Internal Modification**: Works with Claude Code as-is
3. **Incremental Value**: Each script provides immediate debugging value
4. **Simple Implementation**: Shell scripts that anyone can understand and modify
5. **Extensible Foundation**: Can be enhanced as we learn more about Claude Code's capabilities

## ⚠️ Limitations Acknowledged

1. **No Sub-Agent Context**: Cannot track which sub-agent made which call
2. **Limited MCP Visibility**: Only sees what debug output provides
3. **Manual Analysis**: Requires manual inspection of debug logs
4. **No Real-Time Monitoring**: Post-execution analysis only

This is a realistic starting point that provides immediate value while staying within Claude Code's actual capabilities. We can build from here as we discover more about the system's internals.