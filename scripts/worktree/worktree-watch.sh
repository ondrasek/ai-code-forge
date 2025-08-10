#!/bin/bash

# Worktree Watch - Simple Claude Code Monitoring
# Part of the worktree management suite
# Usage: ./worktree.sh watch [--test]

# Basic output colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print section header
print_header() {
    echo -e "\n${CYAN}=== $1 ===${NC}"
}

# Print colored status
print_status() {
    local status="$1"
    local message="$2"
    case "$status" in
        "OK") echo -e "${GREEN}✓${NC} $message" ;;
        "ERROR") echo -e "${RED}✗${NC} $message" ;;
        "INFO") echo -e "${BLUE}→${NC} $message" ;;
        "WARN") echo -e "${YELLOW}⚠${NC} $message" ;;
    esac
}

# Show worktrees and their branches
show_worktrees() {
    print_header "Worktrees & Branches"
    
    if ! command -v git &>/dev/null; then
        print_status "ERROR" "Git not available"
        return 1
    fi
    
    local worktrees
    if worktrees=$(git worktree list --porcelain 2>/dev/null); then
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
                # End of worktree entry
                local basename=$(basename "$current_path")
                local issue_hint=""
                
                # Simple issue number detection
                if [[ $current_branch =~ ([0-9]+) ]]; then
                    issue_hint=" [Issue #${BASH_REMATCH[1]}]"
                fi
                
                print_status "INFO" "$basename → $current_branch$issue_hint"
                current_path=""
                current_branch=""
            fi
        done <<< "$worktrees"
        
        # Handle last entry if no trailing newline
        if [[ -n "$current_path" ]]; then
            local basename=$(basename "$current_path")
            local issue_hint=""
            if [[ $current_branch =~ ([0-9]+) ]]; then
                issue_hint=" [Issue #${BASH_REMATCH[1]}]"
            fi
            print_status "INFO" "$basename → $current_branch$issue_hint"
        fi
    else
        print_status "ERROR" "Failed to list worktrees"
        return 1
    fi
    
    return 0
}

# Show Claude Code processes
show_claude_processes() {
    print_header "Claude Code Processes"
    
    if ! command -v pgrep &>/dev/null; then
        print_status "WARN" "pgrep not available - cannot detect Claude processes"
        return 1
    fi
    
    local pids
    if pids=$(pgrep -f "claude" 2>/dev/null); then
        local count=0
        while IFS= read -r pid; do
            if [[ -n "$pid" ]]; then
                local cmd=""
                local cpu_mem=""
                
                # Get command info
                if command -v ps &>/dev/null; then
                    cmd=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
                    cpu_mem=$(ps -p "$pid" -o pcpu,pmem --no-headers 2>/dev/null || echo "0.0 0.0")
                fi
                
                print_status "OK" "PID $pid: $cmd ($cpu_mem)"
                ((count++))
            fi
        done <<< "$pids"
        
        if [[ $count -eq 0 ]]; then
            print_status "INFO" "No Claude processes detected"
        else
            print_status "OK" "Found $count Claude process(es)"
        fi
    else
        print_status "INFO" "No Claude processes detected"
    fi
    
    return 0
}

# Show GitHub status (simple)
show_github_status() {
    print_header "GitHub Integration"
    
    if command -v gh &>/dev/null; then
        print_status "OK" "GitHub CLI available"
        
        # Try to get current repo status
        if gh repo view --json name,owner 2>/dev/null >/dev/null; then
            local repo_info
            repo_info=$(gh repo view --json name,owner 2>/dev/null | jq -r '"\(.owner.login)/\(.name)"' 2>/dev/null || echo "unknown")
            print_status "OK" "Connected to: $repo_info"
        else
            print_status "WARN" "Not in a GitHub repository or not authenticated"
        fi
    else
        print_status "WARN" "GitHub CLI not available"
    fi
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
        print_header "Worktree Watch - Test Mode"
        echo "Monitoring Claude Code processes and worktrees..."
        echo
        
        show_worktrees
        show_claude_processes  
        show_github_status
        
        echo
        print_status "OK" "Test mode completed"
        exit 0
    else
        # Interactive mode
        print_header "Worktree Watch - Interactive Mode"
        echo "Press Ctrl+C to exit"
        echo
        
        # Trap for cleanup
        trap 'echo; print_status "INFO" "Exiting..."; exit 0' SIGINT SIGTERM
        
        while true; do
            clear
            print_header "Worktree Watch - $(date '+%H:%M:%S')"
            echo
            
            show_worktrees
            show_claude_processes
            show_github_status
            
            echo
            print_status "INFO" "Refreshing in 10 seconds... (Ctrl+C to exit)"
            sleep 10
        done
    fi
}

# Run main function with all arguments
main "$@"