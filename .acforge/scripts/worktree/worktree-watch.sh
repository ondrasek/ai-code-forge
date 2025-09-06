#!/bin/bash

# Worktree Watch - Simple Claude Code Monitoring
# Part of the worktree management suite
# Usage: ./worktree.sh watch [--test]

# Color definitions
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Color CPU utilization based on thresholds
color_cpu() {
    local cpu="$1"
    local cpu_int=${cpu%.*}  # Remove decimal part
    
    if (( cpu_int >= 50 )); then
        echo -e "${RED}${cpu}%${NC} 🔥"
    elif (( cpu_int >= 20 )); then
        echo -e "${YELLOW}${cpu}%${NC} ⚡"
    elif (( cpu_int >= 5 )); then
        echo -e "${GREEN}${cpu}%${NC} ✅"
    else
        echo -e "${GRAY}${cpu}%${NC} 💤"
    fi
}

# Color RSS memory based on thresholds (MB)
color_rss() {
    local rss_mb="$1"
    
    if (( rss_mb >= 1024 )); then  # >= 1GB
        echo -e "${RED}${rss_mb}MB${NC} 🚨"
    elif (( rss_mb >= 512 )); then  # >= 512MB
        echo -e "${YELLOW}${rss_mb}MB${NC} ⚠️"
    elif (( rss_mb >= 100 )); then  # >= 100MB
        echo -e "${GREEN}${rss_mb}MB${NC} 📊"
    else
        echo -e "${GRAY}${rss_mb}MB${NC} 💾"
    fi
}

# Color memory percentage based on thresholds
color_mem() {
    local mem="$1"
    local mem_int=${mem%.*}  # Remove decimal part
    
    if (( mem_int >= 10 )); then
        echo -e "${RED}${mem}%${NC}"
    elif (( mem_int >= 5 )); then
        echo -e "${YELLOW}${mem}%${NC}"
    else
        echo -e "${GREEN}${mem}%${NC}"
    fi
}

# GitHub issue cache directory (per-instance isolation)
CACHE_DIR=$(mktemp -d -t worktree-watch.XXXXXX)
ISSUE_CACHE_FILE="${CACHE_DIR}/issue_cache.json"
ISSUE_CACHE_DURATION=60  # Default: 1 minute in seconds (configurable via --ttl)

# Initialize cache directory and cleanup trap
init_cache() {
    # Cache directory already created by mktemp
    # Set up cleanup trap to remove temporary cache on exit
    trap cleanup_cache EXIT SIGTERM SIGINT
}

# Cleanup temporary cache directory
cleanup_cache() {
    if [[ -n "$CACHE_DIR" && -d "$CACHE_DIR" ]]; then
        rm -rf "$CACHE_DIR"
    fi
}

# Get comprehensive GitHub issue information with progressive discovery
get_issue_info() {
    local issue_num="$1"
    local cache_key="issue_${issue_num}"
    
    # Check if we have cached data that's still valid
    if [[ -f "$ISSUE_CACHE_FILE" ]]; then
        local cache_time=$(stat -c %Y "$ISSUE_CACHE_FILE" 2>/dev/null || echo 0)
        local current_time=$(date +%s)
        local age=$((current_time - cache_time))
        
        if (( age < ISSUE_CACHE_DURATION )); then
            # Use cached data
            local cached_info
            if command -v jq &>/dev/null && cached_info=$(jq -r ".\"$cache_key\" // empty" "$ISSUE_CACHE_FILE" 2>/dev/null); then
                if [[ -n "$cached_info" && "$cached_info" != "null" ]]; then
                    echo "$cached_info"
                    return 0
                fi
            fi
        fi
    fi
    
    # Fetch fresh data from GitHub API with progressive discovery
    if command -v gh &>/dev/null; then
        local repo_info
        if repo_info=$(gh repo view --json owner,name 2>/dev/null); then
            local owner=$(echo "$repo_info" | jq -r '.owner.login' 2>/dev/null)
            local repo=$(echo "$repo_info" | jq -r '.name' 2>/dev/null)
            
            if [[ -n "$owner" && -n "$repo" && "$owner" != "null" && "$repo" != "null" ]]; then
                # Step 1: Fetch basic issue data
                local issue_data
                if issue_data=$(gh api "repos/$owner/$repo/issues/$issue_num" 2>/dev/null); then
                    local title=$(echo "$issue_data" | jq -r '.title // "Unknown"' 2>/dev/null)
                    local url=$(echo "$issue_data" | jq -r '.html_url // ""' 2>/dev/null)
                    local state=$(echo "$issue_data" | jq -r '.state // "unknown"' 2>/dev/null)
                    local assignee=$(echo "$issue_data" | jq -r '.assignee.login // ""' 2>/dev/null)
                    local labels=$(echo "$issue_data" | jq -r '[.labels[].name] | join(",")' 2>/dev/null)
                    local pull_request=$(echo "$issue_data" | jq -r '.pull_request.url // ""' 2>/dev/null)
                    
                    # Initialize result with basic data
                    local result="$title|$url|$state|$assignee|$labels"
                    
                    # Step 2: Progressive discovery - fetch PR data
                    local pr_info=""
                    
                    # First check if issue IS a pull request
                    if [[ -n "$pull_request" ]]; then
                        local pr_data
                        if pr_data=$(gh api "$pull_request" 2>/dev/null); then
                            local pr_state=$(echo "$pr_data" | jq -r '.state // "unknown"' 2>/dev/null)
                            local pr_mergeable=$(echo "$pr_data" | jq -r '.mergeable // false' 2>/dev/null)
                            local pr_merged=$(echo "$pr_data" | jq -r '.merged // false' 2>/dev/null)
                            pr_info="PR:$pr_state"
                            if [[ "$pr_merged" == "true" ]]; then
                                pr_info="$pr_info,merged"
                            elif [[ "$pr_mergeable" == "false" ]]; then
                                pr_info="$pr_info,conflicts"
                            fi
                        fi
                    else
                        # Search for PRs that reference this issue (fixes #N, closes #N, resolves #N)
                        local search_query="\"fixes #$issue_num\" OR \"closes #$issue_num\" OR \"resolves #$issue_num\" OR \"fix #$issue_num\" OR \"close #$issue_num\""
                        local pr_search_result
                        if pr_search_result=$(gh pr list --repo "$owner/$repo" --search "$search_query" --state all --limit 1 --json number,state,title 2>/dev/null); then
                            local pr_count=$(echo "$pr_search_result" | jq '. | length' 2>/dev/null)
                            if [[ "$pr_count" -gt 0 ]]; then
                                local pr_number=$(echo "$pr_search_result" | jq -r '.[0].number // ""' 2>/dev/null)
                                local pr_state=$(echo "$pr_search_result" | jq -r '.[0].state // "unknown"' 2>/dev/null)
                                if [[ -n "$pr_number" && "$pr_number" != "null" ]]; then
                                    pr_info="PR:#$pr_number:$pr_state"
                                    if [[ "$pr_state" == "MERGED" ]]; then
                                        pr_info="$pr_info,merged"
                                    elif [[ "$pr_state" == "CLOSED" ]]; then
                                        pr_info="$pr_info,closed"
                                    fi
                                fi
                            fi
                        fi
                    fi
                    
                    # Add PR info to result or empty string
                    result="$result|$pr_info"
                    
                    # Cache the result
                    if command -v jq &>/dev/null; then
                        local cache_content="{}"
                        if [[ -f "$ISSUE_CACHE_FILE" ]]; then
                            cache_content=$(cat "$ISSUE_CACHE_FILE" 2>/dev/null || echo "{}")
                        fi
                        echo "$cache_content" | jq ".\"$cache_key\" = \"$result\"" > "$ISSUE_CACHE_FILE" 2>/dev/null
                    fi
                    
                    echo "$result"
                    return 0
                fi
            fi
        fi
    fi
    
    # Return empty if we can't fetch
    echo "||||||||"
    return 1
}

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
    
    # Extract issue number and get GitHub info
    local issue_num=$(extract_issue_number "$branch")
    local issue_display="n/a"
    local issue_title=""
    local issue_url=""
    local issue_state=""
    local issue_assignee=""
    local issue_labels=""
    local pr_info=""
    
    if [[ -n "$issue_num" ]]; then
        issue_display="#$issue_num"
        
        # Get issue info from GitHub with caching
        local issue_info=$(get_issue_info "$issue_num")
        if [[ "$issue_info" != "||||||||" ]]; then
            issue_title=$(echo "$issue_info" | cut -d'|' -f1)
            issue_url=$(echo "$issue_info" | cut -d'|' -f2)
            issue_state=$(echo "$issue_info" | cut -d'|' -f3)
            issue_assignee=$(echo "$issue_info" | cut -d'|' -f4)
            issue_labels=$(echo "$issue_info" | cut -d'|' -f5)
            pr_info=$(echo "$issue_info" | cut -d'|' -f6)
        fi
    fi
    
    # Clean branch name (remove refs/heads/)
    local clean_branch=${branch#refs/heads/}
    
    # Display worktree header with emoji (portrait layout)
    echo -e "📁 ${CYAN}$basename${NC}"
    
    # Show issue with state indicator
    local state_emoji=""
    local state_color="$BLUE"
    case "$issue_state" in
        "open") state_emoji="🟢" ;;
        "closed") state_emoji="🔴"; state_color="$RED" ;;
        *) state_emoji="❓" ;;
    esac
    echo -e "   Issue: ${state_color}$issue_display${NC} $state_emoji"
    
    # Show issue title if available
    if [[ -n "$issue_title" && "$issue_title" != "Unknown" ]]; then
        echo -e "   Title: ${GRAY}$issue_title${NC}"
    fi
    
    # Show assignee if available
    if [[ -n "$issue_assignee" ]]; then
        echo -e "   Assignee: ${YELLOW}@$issue_assignee${NC} 👤"
    fi
    
    # Show labels if available
    if [[ -n "$issue_labels" ]]; then
        echo -e "   Labels: ${CYAN}$issue_labels${NC} 🏷️"
    fi
    
    # Show PR info if available
    if [[ -n "$pr_info" ]]; then
        local pr_emoji=""
        local pr_color="$GREEN"
        local pr_display="$pr_info"
        
        # Handle new format: PR:#123:STATE or old format: PR:STATE
        if [[ "$pr_info" =~ ^PR:#([0-9]+):(.+) ]]; then
            local pr_number="${BASH_REMATCH[1]}"
            local pr_state_info="${BASH_REMATCH[2]}"
            pr_display="PR #$pr_number: $pr_state_info"
        fi
        
        case "$pr_info" in
            *"merged"*) pr_emoji="✅"; pr_color="$GREEN" ;;
            *"closed"*) pr_emoji="❌"; pr_color="$RED" ;;
            *"OPEN"*|*"open"*) pr_emoji="🔄"; pr_color="$YELLOW" ;;
            *"conflicts"*) pr_emoji="⚠️"; pr_color="$RED" ;;
        esac
        echo -e "   ${pr_color}$pr_display${NC} $pr_emoji"
    fi
    
    # Show issue URL if available
    if [[ -n "$issue_url" ]]; then
        echo -e "   URL: ${GRAY}$issue_url${NC}"
    fi
    
    echo -e "   Branch: ${GREEN}$clean_branch${NC}"
    echo -e "   Path: ${GRAY}$worktree_path${NC}"
    
    # Find and display associated processes
    local pids=$(find_worktree_processes "$worktree_path")
    
    if [[ -n "$pids" ]]; then
        for pid in $pids; do
            [[ -z "$pid" ]] && continue
            
            local metrics=$(get_process_metrics "$pid")
            read -r pcpu pmem rss_mb vsz comm <<< "$metrics"
            local cwd=$(get_process_cwd "$pid")
            
            # Get colored metrics
            local colored_cpu=$(color_cpu "$pcpu")
            local colored_mem=$(color_mem "$pmem")
            local colored_rss=$(color_rss "$rss_mb")
            
            # Choose process emoji based on command
            local process_emoji="🔧"
            case "$comm" in
                claude) process_emoji="🤖" ;;
                zsh|bash) process_emoji="🐚" ;;
                node) process_emoji="🟢" ;;
            esac
            
            echo -e "   $process_emoji ${YELLOW}PID $pid${NC} ${GRAY}($comm)${NC}"
            echo -e "      CPU: $colored_cpu | Mem: $colored_mem | RSS: $colored_rss"
            echo -e "      CWD: ${GRAY}$cwd${NC}"
        done
    else
        echo -e "   ${GRAY}❌ No Claude processes found${NC}"
    fi
    
    echo ""  # Blank line between worktrees
}

# Main function
main() {
    local test_mode=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            "--test"|"-t")
                test_mode=true
                shift
                ;;
            "--ttl")
                if [[ -n "$2" && "$2" =~ ^[0-9]+$ ]]; then
                    ISSUE_CACHE_DURATION="$2"
                    shift 2
                else
                    echo "Error: --ttl requires a numeric value (seconds)"
                    exit 1
                fi
                ;;
            "--help"|"-h")
                echo "Usage: $0 [--test] [--ttl SECONDS] [--help]"
                echo "  --test         Run once and exit"
                echo "  --ttl SECONDS  Set cache duration in seconds (default: 60)"
                echo "  --help         Show this help"
                echo ""
                echo "Examples:"
                echo "  $0                    # Run with default 1-minute cache"
                echo "  $0 --ttl 300         # Run with 5-minute cache"
                echo "  $0 --ttl 1800        # Run with 30-minute cache (original)"
                echo "  $0 --test --ttl 30   # Test with 30-second cache"
                exit 0
                ;;
            *)
                echo "Error: Unknown option $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Initialize cache directory
    init_cache
    
    if [[ "$test_mode" == true ]]; then
        # Test mode - run once
        show_worktree_status
        exit 0
    else
        # Interactive mode
        echo -e "🔍 ${CYAN}Worktree Watch${NC} - Press ${YELLOW}Ctrl+C${NC} to exit 👋"
        echo ""
        
        # Trap for cleanup
        trap 'echo; echo -e "👋 ${CYAN}Exiting...${NC}"; exit 0' SIGINT SIGTERM
        
        while true; do
            clear
            echo -e "🔍 ${CYAN}Worktree Watch${NC} - $(date '+%Y-%m-%d %H:%M:%S') ⏰"
            echo ""
            
            show_worktree_status
            
            echo -e "🔄 ${GRAY}Refreshing in 10 seconds...${NC}"
            sleep 10
        done
    fi
}

# Run main function with all arguments
main "$@"