#!/bin/bash
set -euo pipefail

# Git Worktree List Utility  
# Lists all git worktrees with detailed information
# Usage: ./worktree-list.sh [--verbose]

WORKTREE_BASE="/workspace/worktrees"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_REPO="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_error() { echo -e "${RED}ERROR:${NC} $1" >&2; }
print_success() { echo -e "${GREEN}SUCCESS:${NC} $1"; }
print_warning() { echo -e "${YELLOW}WARNING:${NC} $1"; }
print_info() { echo -e "${BLUE}INFO:${NC} $1"; }

# Find existing branch for an issue number
find_issue_branch() {
    local issue_num="$1"

    # Common branch naming patterns for issues
    local patterns=(
        "claude/issue-$issue_num-*"
        "issue-$issue_num-*"
        "issue/$issue_num-*"
        "feature/issue-$issue_num-*"
    )

    # Check each pattern in git branches
    for pattern in "${patterns[@]}"; do
        local matches
        matches=$(git branch -a --format="%(refname:short)" | grep -E "^(origin/)?${pattern//\*/.*}$" | head -1 || true)
        if [[ -n "$matches" ]]; then
            # Remove origin/ prefix if present
            echo "${matches#origin/}"
            return 0
        fi
    done

    return 1
}

# Find worktree path for issue branch
find_issue_worktree() {
    local issue_num="$1"
    
    local branch_name
    if branch_name=$(find_issue_branch "$issue_num"); then
        # Look for worktree with this branch
        local worktree_path
        worktree_path=$(git worktree list --porcelain | awk -v branch="$branch_name" '
            /^worktree / { path = substr($0, 10) }
            /^branch refs\/heads\// && substr($0, 19) == branch { print path; exit }
        ')
        
        if [[ -n "$worktree_path" ]]; then
            echo "$worktree_path"
            return 0
        fi
    fi
    
    return 1
}

# Show usage information
show_usage() {
    cat << EOF
Git Worktree List Utility

USAGE:
    ./worktree-list.sh [options] [issue-number]

OPTIONS:
    --verbose, -v    Show detailed information for each worktree
    --dry-run        No effect (list operations are read-only)
    --help, -h       Show this help message

DESCRIPTION:
    Lists all git worktrees with their paths, branches, and status.
    In verbose mode, shows additional details like commit hash and status.
    If issue-number is provided, shows only the worktree for that issue.

EXAMPLES:
    ./worktree-list.sh
    ./worktree-list.sh --verbose
    ./worktree-list.sh -v
    ./worktree-list.sh 123           # Show worktree for issue #123
    ./worktree-list.sh --dry-run

EOF
}

# List worktrees with basic information
list_worktrees() {
    local verbose=false
    local issue_filter=""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --verbose|-v)
                verbose=true
                shift
                ;;
            --dry-run)
                # No-op: list operations are read-only
                print_info "Note: --dry-run has no effect on read-only list operations"
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                # Check if it's a number (issue number)
                if [[ "$1" =~ ^[0-9]+$ ]]; then
                    issue_filter="$1"
                    shift
                else
                    print_error "Unknown option: $1"
                    show_usage
                    exit 1
                fi
                ;;
        esac
    done

    # Handle issue-specific filtering
    if [[ -n "$issue_filter" ]]; then
        print_info "Looking for worktree for issue #$issue_filter:"
        echo
        
        local worktree_path
        if worktree_path=$(find_issue_worktree "$issue_filter"); then
            local branch_name
            branch_name=$(find_issue_branch "$issue_filter")
            
            # Get worktree details for this specific path
            local current_commit=""
            local is_detached=""
            local is_bare=""
            
            # Parse worktree details from git
            while IFS= read -r line; do
                if [[ $line == "worktree $worktree_path" ]]; then
                    continue
                elif [[ $line == branch* ]]; then
                    continue  # We already have the branch name
                elif [[ $line == HEAD* ]]; then
                    current_commit="${line#HEAD }"
                elif [[ $line == "bare" ]]; then
                    is_bare="true"
                elif [[ $line == "detached" ]]; then
                    is_detached="true"
                fi
            done < <(git worktree list --porcelain | awk -v path="$worktree_path" '
                /^worktree / && $0 == "worktree " path { found=1; print }
                found && /^worktree / && $0 != "worktree " path { found=0 }
                found { print }
                /^$/ && found { found=0 }
            ')
            
            print_worktree_info "$worktree_path" "$branch_name" "$current_commit" "$is_bare" "$is_detached" "$verbose"
            echo
            print_success "Found worktree for issue #$issue_filter"
            return 0
        else
            print_error "No worktree found for issue #$issue_filter"
            exit 1
        fi
    fi
    
    print_info "Git Worktrees:"
    echo

    # Get worktree list from git
    if ! git worktree list --porcelain > /dev/null 2>&1; then
        print_error "Failed to retrieve worktree list. Are you in a git repository?"
        exit 1
    fi

    local worktree_count=0
    local current_worktree=""
    local current_branch=""
    local current_commit=""
    local is_bare=""
    local is_detached=""

    # Process git worktree list output
    while IFS= read -r line; do
        if [[ $line == worktree* ]]; then
            # Print previous worktree if exists
            if [[ -n $current_worktree ]]; then
                print_worktree_info "$current_worktree" "$current_branch" "$current_commit" "$is_bare" "$is_detached" "$verbose"
                worktree_count=$((worktree_count + 1))
            fi
            
            # Reset for new worktree
            current_worktree="${line#worktree }"
            current_branch=""
            current_commit=""
            is_bare=""
            is_detached=""
            
        elif [[ $line == branch* ]]; then
            # Extract branch name from "branch refs/heads/branch-name"
            local branch_line="${line#branch refs/heads/}"
            current_branch="$branch_line"
        elif [[ $line == HEAD* ]]; then
            # Extract commit hash from "HEAD commit-hash"
            current_commit="${line#HEAD }"
        elif [[ $line == "bare" ]]; then
            is_bare="true"
        elif [[ $line == "detached" ]]; then
            is_detached="true"
        fi
    done < <(git worktree list --porcelain)

    # Print last worktree
    if [[ -n $current_worktree ]]; then
        print_worktree_info "$current_worktree" "$current_branch" "$current_commit" "$is_bare" "$is_detached" "$verbose"
        worktree_count=$((worktree_count + 1))
    fi

    echo
    print_success "Found $worktree_count worktree(s)"
}

# Print information for a single worktree
print_worktree_info() {
    local worktree_path="$1"
    local branch="$2" 
    local commit="$3"
    local is_bare="$4"
    local is_detached="$5"
    local verbose="$6"
    
    # Determine status indicators
    local status_indicator=""
    local branch_display="$branch"
    
    if [[ $worktree_path == "$MAIN_REPO" ]]; then
        status_indicator="${GREEN}[MAIN]${NC}"
    elif [[ $is_bare == "true" ]]; then
        status_indicator="${YELLOW}[BARE]${NC}"
        branch_display="(bare repository)"
    elif [[ $is_detached == "true" ]]; then
        status_indicator="${RED}[DETACHED]${NC}"
        branch_display="(detached HEAD)"
    fi

    # Basic information
    echo -e "📁 ${BLUE}$worktree_path${NC} $status_indicator"
    
    if [[ $verbose == "true" ]]; then
        echo -e "   Branch: ${GREEN}$branch_display${NC}"
        if [[ -n $commit ]]; then
            echo -e "   Commit: ${YELLOW}${commit:0:8}${NC}"
            
            # Try to get commit message if in verbose mode
            if [[ -d "$worktree_path/.git" ]]; then
                local commit_msg
                commit_msg=$(cd "$worktree_path" && git log -1 --format="%s" 2>/dev/null || echo "Unable to read commit")
                echo -e "   Message: $commit_msg"
            fi
        fi
        
        # Check if directory exists and get modification time
        if [[ -d "$worktree_path" ]]; then
            local mod_time
            mod_time=$(stat -c "%y" "$worktree_path" 2>/dev/null || echo "Unknown")
            echo -e "   Modified: $mod_time"
        else
            echo -e "   ${RED}Status: Directory missing${NC}"
        fi
        echo
    else
        echo -e "   Branch: ${GREEN}$branch_display${NC}"
    fi
}

# Main execution
main() {
    list_worktrees "$@"
}

# Run main function with all arguments
main "$@"