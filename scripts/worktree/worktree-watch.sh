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
    
    # Display worktree header with emoji (portrait layout)
    echo -e "📁 ${CYAN}$basename${NC}"
    echo -e "   Issue: ${BLUE}$issue_display${NC}"
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