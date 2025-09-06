#!/bin/bash
# Enhanced Claude Code debugging wrapper - captures stdout/stderr output

set -euo pipefail

# Create debug log directory
DEBUG_DIR="logs/debug/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$DEBUG_DIR"

# Debug log files (WE create these by capturing Claude's output)
DEBUG_LOG="$DEBUG_DIR/claude-debug.log"
MCP_LOG="$DEBUG_DIR/mcp-debug.log"
VERBOSE_LOG="$DEBUG_DIR/verbose.log"
STDERR_LOG="$DEBUG_DIR/stderr.log"

echo "🔍 Starting Claude Code with enhanced debugging"
echo "📁 Debug logs: $DEBUG_DIR"
echo "ℹ️  Note: Claude Code doesn't create log files - we capture its stdout/stderr"

# Function to capture and split output
capture_debug_output() {
    local query="$*"
    
    echo "=== Debug Session Started: $(date) ===" | tee -a "$DEBUG_LOG" "$VERBOSE_LOG"
    echo "Query: $query" | tee -a "$DEBUG_LOG" "$VERBOSE_LOG"
    echo "" | tee -a "$DEBUG_LOG" "$VERBOSE_LOG"
    
    # Run Claude with debug and capture stdout and stderr separately
    {
        # Set debug environment variables
        export ANTHROPIC_LOG=debug
        export CLAUDE_CODE_ENABLE_TELEMETRY=1
        export MCP_TIMEOUT=30000
        
        # Capture both stdout and stderr, split them for analysis
        claude --debug --verbose --print "$query" 2> >(tee "$STDERR_LOG" >&2) | \
        tee "$VERBOSE_LOG" | \
        while IFS= read -r line; do
            # Show output to user
            echo "$line"
            
            # Log all output
            echo "$line" >> "$DEBUG_LOG"
            
            # Detect MCP-related output (case insensitive)
            if [[ "$line" =~ [Mm][Cc][Pp]|[Ss]erver|[Tt]ool|[Cc]onnect ]]; then
                echo "$line" >> "$MCP_LOG"
            fi
        done
        
        # Also process stderr for MCP/debug info
        if [[ -f "$STDERR_LOG" ]]; then
            while IFS= read -r line; do
                echo "$line" >> "$DEBUG_LOG"
                if [[ "$line" =~ [Mm][Cc][Pp]|[Ss]erver|[Tt]ool|[Dd][Ee][Bb][Uu][Gg] ]]; then
                    echo "$line" >> "$MCP_LOG"
                fi
            done < "$STDERR_LOG"
        fi
        
    } || true  # Don't fail if Claude fails
    
    echo "=== Debug Session Ended: $(date) ===" | tee -a "$DEBUG_LOG" "$VERBOSE_LOG"
    echo "" | tee -a "$DEBUG_LOG" "$VERBOSE_LOG"
}

# Execute with debug capture
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 \"your query here\""
    echo "Example: $0 \"List the files in this directory\""
    exit 1
fi

capture_debug_output "$@"

echo ""
echo "📊 Debug output captured to:"
echo "  📋 All output: $VERBOSE_LOG"
echo "  🔍 Debug info: $DEBUG_LOG" 
echo "  🔌 MCP/Server: $MCP_LOG"
echo "  ⚠️  Stderr: $STDERR_LOG"
echo ""
echo "💡 To view captured debug info:"
echo "  less $DEBUG_LOG"
echo "  grep -i 'debug\\|error' $STDERR_LOG"