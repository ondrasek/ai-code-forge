#!/bin/bash

# Worktree Watch - Simple Claude Code Monitoring
# Part of the worktree management suite
# Usage: ./worktree.sh watch [--test]

# Get process working directory
get_process_cwd() {
    local pid="$1"
    local cwd=""
    
    # Try multiple methods to get working directory
    if [[ -r "/proc/$pid/cwd" ]]; then
        cwd=$(readlink "/proc/$pid/cwd" 2>/dev/null)
    elif command -v pwdx &>/dev/null; then
        cwd=$(pwdx "$pid" 2>/dev/null | cut -d' ' -f2-)
    elif command -v lsof &>/dev/null; then
        cwd=$(lsof -p "$pid" -d cwd -Fn 2>/dev/null | grep '^n' | cut -c2-)
    fi
    
    echo "${cwd:-unknown}"
}

# Get detailed process metrics
get_process_metrics() {
    local pid="$1"
    local ps_output
    ps_output=$(ps -p "$pid" -o pcpu,pmem,rss,vsz,comm --no-headers 2>/dev/null || echo "0.0 0.0 0 0 unknown")
    
    read -r pcpu pmem rss vsz comm <<< "$ps_output"
    
    # Convert RSS from KB to MB for readability
    local rss_mb=$((rss / 1024))
    
    echo "$pcpu $pmem $rss_mb $vsz $comm"
}

# Extract issue number from branch name
extract_issue_number() {
    local branch="$1"
    local issue_num=""
    
    # Multiple patterns for issue number detection
    if [[ $branch =~ ^refs/heads/([0-9]+)$ ]]; then
        issue_num="${BASH_REMATCH[1]}"
    elif [[ $branch =~ refs/heads/.*[_/-]([0-9]+)$ ]]; then
        issue_num="${BASH_REMATCH[1]}"
    elif [[ $branch =~ ([0-9]+) ]]; then
        issue_num="${BASH_REMATCH[1]}"
    fi
    
    echo "$issue_num"
}

# Find Claude processes associated with a worktree
find_worktree_processes() {
    local worktree_path="$1"
    local associated_pids=""
    
    # Get all Claude processes
    local claude_pids
    if claude_pids=$(pgrep -f "claude" 2>/dev/null); then
        while IFS= read -r pid; do
            [[ -z "$pid" ]] && continue
            
            local cwd=$(get_process_cwd "$pid")
            
            # Check if process working directory is within this worktree
            if [[ "$cwd" == "$worktree_path"* ]]; then
                associated_pids="$associated_pids $pid"
            fi
        done <<< "$claude_pids"
    fi
    
    echo "$associated_pids"
}

# Main display function
show_worktree_status() {
    if ! command -v git &>/dev/null; then
        echo "Error: Git not available"
        return 1
    fi
    
    # Get worktrees
    local worktrees
    if ! worktrees=$(git worktree list --porcelain 2>/dev/null); then
        echo "Error: Failed to list worktrees"
        return 1
    fi
    
    # Parse worktrees and display grouped information
    local current_path=""
    local current_branch=""
    
    while IFS= read -r line; do
        if [[ $line =~ ^worktree\ (.+) ]]; then
            current_path="${BASH_REMATCH[1]}"
        elif [[ $line =~ ^branch\ (.+) ]]; then
            current_branch="${BASH_REMATCH[1]}"
        elif [[ $line =~ ^detached$ ]]; then
            current_branch="(detached HEAD)"
        elif [[ -z "$line" && -n "$current_path" ]]; then
            # Process complete worktree entry
            display_worktree_info "$current_path" "$current_branch"
            current_path=""
            current_branch=""
        fi
    done <<< "$worktrees"
    
    # Handle last entry if no trailing newline
    if [[ -n "$current_path" ]]; then
        display_worktree_info "$current_path" "$current_branch"
    fi
}

# Display information for a single worktree
display_worktree_info() {
    local worktree_path="$1"
    local branch="$2"
    local basename=$(basename "$worktree_path")
    
    # Extract issue number
    local issue_num=$(extract_issue_number "$branch")
    local issue_display=""
    if [[ -n "$issue_num" ]]; then
        issue_display="#$issue_num"
    else
        issue_display="n/a"
    fi
    
    # Clean branch name (remove refs/heads/)
    local clean_branch=${branch#refs/heads/}
    
    # Display worktree header
    echo "$basename | $issue_display | $clean_branch | $worktree_path"
    
    # Find and display associated processes
    local pids=$(find_worktree_processes "$worktree_path")
    
    if [[ -n "$pids" ]]; then
        for pid in $pids; do
            [[ -z "$pid" ]] && continue
            
            local metrics=$(get_process_metrics "$pid")
            read -r pcpu pmem rss_mb vsz comm <<< "$metrics"
            local cwd=$(get_process_cwd "$pid")
            
            echo "  └─ PID $pid | $comm | CPU: ${pcpu}% | Mem: ${pmem}% | RSS: ${rss_mb}MB | CWD: $cwd"
        done
    else
        echo "  └─ No Claude processes found"
    fi
    
    echo ""  # Blank line between worktrees
}

# Main function
main() {
    local test_mode=false
    
    # Parse arguments
    case "${1:-}" in
        "--test"|"-t")
            test_mode=true
            ;;
        "--help"|"-h")
            echo "Usage: $0 [--test] [--help]"
            echo "  --test    Run once and exit"
            echo "  --help    Show this help"
            exit 0
            ;;
    esac
    
    if [[ "$test_mode" == true ]]; then
        # Test mode - run once
        show_worktree_status
        exit 0
    else
        # Interactive mode
        echo "Worktree Watch - Press Ctrl+C to exit"
        echo ""
        
        # Trap for cleanup
        trap 'echo; echo "Exiting..."; exit 0' SIGINT SIGTERM
        
        while true; do
            clear
            echo "Worktree Watch - $(date '+%Y-%m-%d %H:%M:%S')"
            echo ""
            
            show_worktree_status
            
            echo "Refreshing in 10 seconds..."
            sleep 10
        done
    fi
}

# Run main function with all arguments
main "$@"