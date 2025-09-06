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