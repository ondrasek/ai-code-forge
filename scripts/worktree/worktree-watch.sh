#!/bin/bash

# Claude Code Monitoring Dashboard
# Terminal-based monitoring system for Claude Code instances and worktrees
# Created for GitHub Issue #131

set -eo pipefail

# Configuration
REFRESH_INTERVAL_PROCESS=10    # Process monitoring refresh (seconds)
REFRESH_INTERVAL_GITHUB=300    # GitHub API refresh (seconds)
CACHE_DIR="${HOME}/.cache/worktree-watch"
GITHUB_CACHE_FILE="${CACHE_DIR}/github_cache.json"
LOG_FILE="${CACHE_DIR}/worktree-watch.log"

# Debug mode for testing
DEBUG_MODE="${DEBUG_MODE:-false}"

# Color codes for terminal display
COLOR_RESET="\033[0m"
COLOR_HEADER="\033[1;36m"     # Bright cyan
COLOR_ACTIVE="\033[1;32m"     # Bright green
COLOR_WARNING="\033[1;33m"    # Bright yellow
COLOR_ERROR="\033[1;31m"      # Bright red
COLOR_DIM="\033[2m"           # Dim/gray

# Global variables for data persistence
declare -A WORKTREE_TO_ISSUE
declare -A ISSUE_METADATA
declare -A PROCESS_DATA
LAST_GITHUB_UPDATE=0

# Cleanup function
cleanup() {
    echo -e "\n${COLOR_DIM}Dashboard stopped${COLOR_RESET}"
    tput cnorm  # Restore cursor
    exit 0
}

# Set up cleanup on signals
trap cleanup SIGINT SIGTERM

# Initialize environment
init_dashboard() {
    mkdir -p "$CACHE_DIR"
    
    # Only hide cursor and clear screen if not in test mode
    if [[ "${1:-}" != "--test" ]]; then
        # Hide cursor for cleaner display
        tput civis
        
        # Clear screen
        clear
    fi
    
    log_message "Dashboard initialized"
}

# Logging function
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Debug function
debug_log() {
    if [[ "$DEBUG_MODE" == "true" ]]; then
        echo "DEBUG: $1" >&2
        log_message "DEBUG: $1"
    fi
}

# Display header
show_header() {
    local current_time
    current_time=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo -e "${COLOR_HEADER}"
    echo "╔══════════════════════════════════════════════════════════════════════════════════════╗"
    echo "║                          Claude Code Monitoring Dashboard                           ║"
    echo "║                              $current_time                              ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${COLOR_RESET}\n"
}

# Get all worktrees with enhanced parsing
get_worktrees() {
    local worktree_list
    
    # Clear existing data
    unset WORKTREE_TO_ISSUE
    declare -gA WORKTREE_TO_ISSUE
    
    # Use git worktree list to get all worktrees
    if ! worktree_list=$(git worktree list --porcelain 2>/dev/null); then
        log_message "ERROR: Failed to get worktree list"
        return 1
    fi
    
    # Parse worktree data line by line
    local current_worktree=""
    while IFS= read -r line; do
        if [[ $line =~ ^worktree\ (.+)$ ]]; then
            current_worktree="${BASH_REMATCH[1]}"
        elif [[ $line =~ ^HEAD\ (.+)$ ]] && [[ -n "$current_worktree" ]]; then
            local head_ref="${BASH_REMATCH[1]}"
            local branch_name
            
            # Extract branch name or commit hash
            if [[ $head_ref =~ refs/heads/(.+)$ ]]; then
                branch_name="${BASH_REMATCH[1]}"
            else
                # Detached HEAD - use first 8 chars of commit hash
                branch_name="${head_ref:0:8}"
            fi
            
            # Store worktree to branch mapping
            WORKTREE_TO_ISSUE["$current_worktree"]="$branch_name"
            current_worktree=""
        fi
    done <<< "$worktree_list"
}

# Get GitHub issue data with caching
get_github_data() {
    local current_time
    current_time=$(date +%s)
    
    # Check if cache is still valid
    if [[ -f "$GITHUB_CACHE_FILE" ]] && [[ $((current_time - LAST_GITHUB_UPDATE)) -lt $REFRESH_INTERVAL_GITHUB ]]; then
        # Load from cache
        if command -v jq &>/dev/null && [[ -s "$GITHUB_CACHE_FILE" ]]; then
            log_message "Loading GitHub data from cache"
            return 0
        fi
    fi
    
    # Fetch fresh data from GitHub
    log_message "Fetching fresh GitHub data"
    
    if command -v gh &>/dev/null; then
        # Use GitHub CLI to get issue data
        local issues_json
        if issues_json=$(gh issue list --repo ondrasek/ai-code-forge --json number,title,state,labels,updatedAt --limit 100 2>/dev/null); then
            # Save to cache
            echo "$issues_json" > "$GITHUB_CACHE_FILE"
            LAST_GITHUB_UPDATE=$current_time
            log_message "GitHub data cached successfully"
        else
            log_message "WARNING: Failed to fetch GitHub data via gh CLI"
            # Try to use existing cache if available
            if [[ ! -f "$GITHUB_CACHE_FILE" ]]; then
                echo "[]" > "$GITHUB_CACHE_FILE"  # Empty fallback
            fi
        fi
    else
        log_message "WARNING: GitHub CLI (gh) not available"
        echo "[]" > "$GITHUB_CACHE_FILE"  # Empty fallback
    fi
}

# Parse GitHub data and populate ISSUE_METADATA
parse_github_data() {
    if [[ ! -f "$GITHUB_CACHE_FILE" ]] || ! command -v jq &>/dev/null; then
        log_message "Cannot parse GitHub data - missing cache file or jq"
        return 1
    fi
    
    # Clear existing metadata
    unset ISSUE_METADATA
    declare -gA ISSUE_METADATA
    
    # Simplified approach - parse directly without complex pipe handling
    debug_log "Parsing GitHub data from cache file"
    local parse_count=0
    
    # Parse each issue individually to avoid pipe character issues
    local issue_numbers
    if ! issue_numbers=$(jq -r '.[].number' "$GITHUB_CACHE_FILE" 2>/dev/null); then
        log_message "Failed to parse issue numbers from GitHub cache"
        return 1
    fi
    
    while IFS= read -r number; do
        [[ -z "$number" ]] && continue
        
        # Get individual issue data with error handling
        local title state updated_at labels
        title=$(jq -r ".[] | select(.number==$number) | .title" "$GITHUB_CACHE_FILE" 2>/dev/null || echo "Unknown title")
        state=$(jq -r ".[] | select(.number==$number) | .state" "$GITHUB_CACHE_FILE" 2>/dev/null || echo "UNKNOWN")
        updated_at=$(jq -r ".[] | select(.number==$number) | .updatedAt" "$GITHUB_CACHE_FILE" 2>/dev/null || echo "Unknown date")
        labels=$(jq -r ".[] | select(.number==$number) | [.labels[].name] | join(\",\")" "$GITHUB_CACHE_FILE" 2>/dev/null || echo "")
        
        # Store without pipe delimiters that cause parsing issues
        ISSUE_METADATA["$number"]="$title|$state|$updated_at|$labels"
        debug_log "Parsed issue #$number: ${title:0:30}..."
        ((parse_count++))
    done <<< "$issue_numbers"
    
    debug_log "Parsed $parse_count issues total"
    if [[ ${#ISSUE_METADATA[@]} -gt 0 ]]; then
        debug_log "Issue metadata keys: ${!ISSUE_METADATA[*]}"
    else
        debug_log "No issue metadata found"
    fi
}

# Get Claude Code processes and associate with worktrees
get_claude_processes() {
    local pids
    
    # Clear existing process data
    unset PROCESS_DATA
    declare -gA PROCESS_DATA
    
    # Find Claude Code processes (try multiple possible process names)
    if pids=$(pgrep -f "claude" 2>/dev/null); then
        log_message "Found Claude processes: $pids"
        
        for pid in $pids; do
            # Get process working directory
            local cwd=""
            
            # Try different methods to get working directory
            if [[ -r "/proc/$pid/cwd" ]]; then
                cwd=$(readlink "/proc/$pid/cwd" 2>/dev/null || echo "")
            elif command -v pwdx &>/dev/null; then
                cwd=$(pwdx "$pid" 2>/dev/null | cut -d' ' -f2- || echo "")
            fi
            
            # Get process resource usage
            local cpu_mem
            cpu_mem=$(ps -o pid,pcpu,pmem,comm -p "$pid" --no-headers 2>/dev/null || echo "$pid 0.0 0.0 unknown")
            
            # Find best matching worktree
            local best_match=""
            local best_match_length=0
            
            for worktree in "${!WORKTREE_TO_ISSUE[@]}"; do
                # Resolve symlinks for accurate comparison
                local real_worktree
                real_worktree=$(realpath "$worktree" 2>/dev/null || echo "$worktree")
                local real_cwd
                real_cwd=$(realpath "$cwd" 2>/dev/null || echo "$cwd")
                
                # Check if process cwd is under this worktree
                if [[ "$real_cwd" == "$real_worktree"* ]] && [[ ${#real_worktree} -gt $best_match_length ]]; then
                    best_match="$worktree"
                    best_match_length=${#real_worktree}
                fi
            done
            
            # Store process data
            PROCESS_DATA["$pid"]="$cpu_mem|$cwd|$best_match"
        done
    else
        log_message "No Claude processes found"
    fi
}

# Display dashboard content
display_dashboard() {
    # Display worktree-issue associations
    echo -e "${COLOR_HEADER}Worktrees & Issues:${COLOR_RESET}"
    echo "┌─────────────────────────────────────────────────────────────────────────────────────┐"
    
    if [[ ${#WORKTREE_TO_ISSUE[@]} -eq 0 ]]; then
        echo "│ No worktrees found                                                                  │"
    else
        for worktree in "${!WORKTREE_TO_ISSUE[@]}"; do
            local branch="${WORKTREE_TO_ISSUE[$worktree]}"
            local issue_info="No issue found"
            
            # Try to extract issue number from branch name (multiple patterns)
            local issue_num=""
            if [[ $branch =~ ^([0-9]+)$ ]]; then
                # Direct numeric branch (e.g., "131")
                issue_num="${BASH_REMATCH[1]}"
            elif [[ $branch =~ /([0-9]+)$ ]]; then
                # Branch ending with number (e.g., "feature/131")
                issue_num="${BASH_REMATCH[1]}"
            elif [[ $branch =~ ^.*-([0-9]+)-.*$ ]]; then
                # Branch with number in middle (e.g., "claude-131-feature")
                issue_num="${BASH_REMATCH[1]}"
            elif [[ $branch =~ ^.*[_-]([0-9]+)$ ]]; then
                # Branch ending with underscore/dash and number (e.g., "feature_131")
                issue_num="${BASH_REMATCH[1]}"
            fi
            
            if [[ -n "$issue_num" ]]; then
                debug_log "Found issue number $issue_num from branch $branch"
                if [[ -n "${ISSUE_METADATA[$issue_num]:-}" ]]; then
                    IFS='|' read -r title state updated_at labels <<< "${ISSUE_METADATA[$issue_num]}"
                    local truncated_title="${title:0:40}"
                    [[ ${#title} -gt 40 ]] && truncated_title+="..."
                    issue_info="#$issue_num: $truncated_title [$state]"
                    debug_log "Matched issue #$issue_num: $title"
                else
                    debug_log "No metadata found for issue #$issue_num"
                fi
            else
                debug_log "No issue number found in branch name: $branch"
            fi
            
            # Format worktree path
            local display_path="${worktree##*/}"  # Show only directory name
            printf "│ %-30s │ %-50s │\n" "$display_path ($branch)" "$issue_info"
        done
    fi
    echo "└─────────────────────────────────────────────────────────────────────────────────────┘"
    
    # Display Claude Code processes
    echo -e "\n${COLOR_HEADER}Claude Code Processes:${COLOR_RESET}"
    echo "┌─────────────────────────────────────────────────────────────────────────────────────┐"
    
    if [[ ${#PROCESS_DATA[@]} -eq 0 ]]; then
        echo "│ No Claude Code processes found                                                      │"
    else
        printf "│ %-8s │ %-8s │ %-8s │ %-30s │ %-20s │\n" "PID" "CPU%" "MEM%" "Worktree" "Working Dir"
        echo "├─────────────────────────────────────────────────────────────────────────────────────┤"
        
        for pid in "${!PROCESS_DATA[@]}"; do
            IFS='|' read -r cpu_mem_info cwd best_match <<< "${PROCESS_DATA[$pid]}"
            IFS=' ' read -r p_pid cpu mem comm <<< "$cpu_mem_info"
            
            local display_worktree="${best_match##*/}"
            [[ -z "$display_worktree" ]] && display_worktree="<unassociated>"
            
            local display_cwd="${cwd##*/}"
            [[ -z "$display_cwd" ]] && display_cwd="<unknown>"
            
            printf "│ %-8s │ %-8s │ %-8s │ %-30s │ %-20s │\n" "$pid" "$cpu" "$mem" "$display_worktree" "$display_cwd"
        done
    fi
    echo "└─────────────────────────────────────────────────────────────────────────────────────┘"
    
    # Display status information
    local github_status
    if [[ -f "$GITHUB_CACHE_FILE" ]]; then
        local cache_age=$(($(date +%s) - LAST_GITHUB_UPDATE))
        github_status="Cached (${cache_age}s ago)"
    else
        github_status="No data"
    fi
    
    echo -e "\n${COLOR_DIM}GitHub API: $github_status │ Refresh: ${REFRESH_INTERVAL_PROCESS}s │ Press Ctrl+C to exit${COLOR_RESET}"
}

# Main execution
main() {
    # Check if we're in test mode
    local test_mode="${1:-}"
    
    # Initialize
    init_dashboard "$test_mode"
    
    # Initial data load
    get_github_data
    parse_github_data
    get_worktrees
    get_claude_processes
    
    if [[ "$test_mode" == "--test" ]]; then
        # Test mode - run once and exit (no screen clearing)
        echo -e "\n${COLOR_HEADER}=== CLAUDE DASHBOARD TEST MODE ===${COLOR_RESET}\n"
        show_header
        display_dashboard
        echo -e "\n${COLOR_DIM}Test mode - completed single display${COLOR_RESET}"
        return 0
    fi
    
    # Main dashboard loop
    while true; do
        # Clear screen and show header
        clear
        show_header
        
        # Get current data
        get_worktrees
        get_claude_processes
        
        # Refresh GitHub data if needed
        get_github_data
        parse_github_data
        
        # Display comprehensive dashboard
        display_dashboard
        
        # Wait for refresh interval
        sleep "$REFRESH_INTERVAL_PROCESS"
    done
}

# Check if running as script vs sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi