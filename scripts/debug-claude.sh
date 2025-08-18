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