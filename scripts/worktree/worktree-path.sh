#!/bin/bash
set -euo pipefail

# Git Worktree Path Utility
# Outputs the directory path for specified worktree
# Usage: ./worktree-path.sh <issue-number|branch-name|main>

WORKTREE_BASE="/workspace/worktrees"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_REPO="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Show usage information
show_usage() {
    cat << EOF
Git Worktree Path Utility

DESCRIPTION:
    Output the directory path for a specified worktree.
    Designed for use with cd command substitution.

USAGE:
    $0 <issue-number|branch-name|main>

ARGUMENTS:
    issue-number    Issue number (e.g., 123, #123)
    branch-name     Full branch name (e.g., feature/add-cwd, 129)
    main           Main branch worktree (configurable per repository)

EXAMPLES:
    $0 123                      # Output path for issue #123 worktree
    $0 feature/add-cwd         # Output path for specific branch worktree  
    $0 main                    # Output path for main branch worktree
    
    # Usage with cd command:
    cd \$($0 123)              # Change to worktree for issue #123
    cd \$($0 main)             # Change to main branch worktree

SHELL INTEGRATION:
    # Recommended alias (note: use function instead of alias for parameters):
    wtd() { cd "\$(worktree.sh path "\$1")"; }
    
    # Usage:
    wtd 123                    # Change to issue #123 worktree
    wtd main                   # Change to main branch worktree

EOF
}

# Get repository name for worktree path construction
get_repo_name() {
    local repo_name=""
    
    # Try GitHub CLI first
    if command -v gh >/dev/null 2>&1; then
        repo_name=$(gh repo view --json name --jq .name 2>/dev/null || echo "")
    fi
    
    # Fallback to git remote parsing
    if [[ -z "$repo_name" ]]; then
        local remote_url
        remote_url=$(git -C "$MAIN_REPO" remote get-url origin 2>/dev/null || echo "")
        if [[ -n "$remote_url" ]]; then
            # Extract repo name from URL
            if [[ "$remote_url" =~ github\.com[:/][^/]+/([^/]+)(\.git)?$ ]]; then
                repo_name="${BASH_REMATCH[1]%.git}"
            fi
        fi
    fi
    
    if [[ -z "$repo_name" ]]; then
        echo "."
        return 0
    fi
    
    echo "$repo_name"
}

# Get main branch name (configurable per repository)
get_main_branch() {
    local main_branch=""
    
    # Try to get default branch from git
    if command -v git >/dev/null 2>&1; then
        # Try remote HEAD first
        main_branch=$(git -C "$MAIN_REPO" symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "")
        
        # Fallback to common main branch names
        if [[ -z "$main_branch" ]]; then
            for branch in main master develop; do
                if git -C "$MAIN_REPO" show-ref --verify --quiet "refs/remotes/origin/$branch"; then
                    main_branch="$branch"
                    break
                fi
            done
        fi
    fi
    
    # Ultimate fallback
    if [[ -z "$main_branch" ]]; then
        main_branch="main"
    fi
    
    echo "$main_branch"
}

# Find worktree directory for issue number, branch name, or main
find_worktree_dir() {
    local identifier="$1"
    local repo_name
    repo_name=$(get_repo_name)
    if [[ "$repo_name" == "." ]]; then
        echo "."
        return 0
    fi
    
    local base_dir="$WORKTREE_BASE/$repo_name"
    
    if [[ ! -d "$base_dir" ]]; then
        echo "."
        return 0
    fi
    
    # Handle "main" special case
    if [[ "$identifier" == "main" ]]; then
        local main_branch
        main_branch=$(get_main_branch)
        identifier="$main_branch"
    fi
    
    # Clean up identifier (remove # prefix if present)
    local clean_id="${identifier#\#}"
    
    # Try exact match first
    local target_dir="$base_dir/$clean_id"
    if [[ -d "$target_dir" ]]; then
        echo "$target_dir"
        return 0
    fi
    
    # Search for directories containing the identifier
    local matches=()
    while IFS= read -r -d '' dir; do
        local dirname=$(basename "$dir")
        if [[ "$dirname" == *"$clean_id"* ]]; then
            matches+=("$dir")
        fi
    done < <(find "$base_dir" -mindepth 1 -maxdepth 1 -type d -print0)
    
    if [[ ${#matches[@]} -eq 0 ]]; then
        echo "."
        return 0
    elif [[ ${#matches[@]} -eq 1 ]]; then
        echo "${matches[0]}"
        return 0
    else
        # Multiple matches - use first one
        echo "${matches[0]}"
        return 0
    fi
}

# Main function
main() {
    if [[ $# -eq 0 ]]; then
        echo "ERROR: Missing required argument" >&2
        show_usage >&2
        exit 1
    fi
    
    local identifier="$1"
    
    # Handle help
    if [[ "$identifier" == "--help" || "$identifier" == "-h" || "$identifier" == "help" ]]; then
        show_usage
        exit 0
    fi
    
    # Find and output worktree directory
    find_worktree_dir "$identifier"
}

# Run main function with all arguments
main "$@"