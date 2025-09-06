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