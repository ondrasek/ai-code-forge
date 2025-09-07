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
    $0 <issue-number|main>

ARGUMENTS:
    issue-number    Issue number (e.g., 123, #123) - numbers only
    main           Main branch worktree (configurable per repository)

SECURITY:
    Only issue numbers and 'main' are accepted for security reasons.
    Branch names and arbitrary paths are not allowed.

EXAMPLES:
    $0 123                      # Output path for issue #123 worktree
    $0 \#123                     # Output path for issue #123 worktree (with # prefix)
    $0 main                     # Output path for main branch worktree
    
    # Usage with cd command:
    cd \$($0 123)              # Change to worktree for issue #123
    cd \$($0 main)             # Change to main branch worktree

SHELL INTEGRATION:
    # Recommended shell function:
    wtd() { cd "\$(worktree.sh path "\$1")"; }  # Only works with issue numbers and 'main'
    
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
        echo "ERROR: Unable to determine repository name" >&2
        echo "."
        return 1
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

# Validate input - only issue numbers and "main" allowed
validate_identifier() {
    local identifier="$1"
    
    # Allow "main"
    if [[ "$identifier" == "main" ]]; then
        return 0
    fi
    
    # Remove # prefix if present for validation
    local clean_id="${identifier#\#}"
    
    # Allow only pure numbers (issue numbers)
    if [[ "$clean_id" =~ ^[0-9]+$ ]]; then
        return 0
    fi
    
    # Reject everything else
    echo "ERROR: Only issue numbers (e.g., 123, #123) and 'main' are allowed" >&2
    return 1
}

# Find worktree directory for validated issue number or main
find_worktree_dir() {
    local identifier="$1"
    
    # Strict input validation
    if ! validate_identifier "$identifier"; then
        echo "."
        return 1
    fi
    
    local repo_name
    repo_name=$(get_repo_name) || {
        echo "."
        return 1
    }
    
    local base_dir="$WORKTREE_BASE/$repo_name"
    
    if [[ ! -d "$base_dir" ]]; then
        echo "ERROR: No worktrees found in $base_dir" >&2
        echo "."
        return 1
    fi
    
    # Handle "main" special case - try both "main" and actual main branch name
    local search_identifiers=()
    if [[ "$identifier" == "main" ]]; then
        # Try "main" first (in case worktree was created as "main")
        search_identifiers+=("main")
        # Also try the actual main branch name
        local main_branch
        main_branch=$(get_main_branch)
        if [[ "$main_branch" != "main" ]]; then
            search_identifiers+=("$main_branch")
        fi
    else
        search_identifiers+=("$identifier")
    fi
    
    # Search through all possible identifiers
    local all_matches=()
    
    for search_id in "${search_identifiers[@]}"; do
        # Clean up identifier (remove # prefix if present) - now safe after validation
        local clean_id="${search_id#\#}"
        
        # Try exact match first
        local target_dir="$base_dir/$clean_id"
        if [[ -d "$target_dir" ]]; then
            echo "$target_dir"
            return 0
        fi
        
        # Search for directories containing the identifier (now safe - only numbers or main branch)
        while IFS= read -r -d '' dir; do
            local dirname=$(basename "$dir")
            if [[ "$dirname" == *"$clean_id"* ]]; then
                all_matches+=("$dir")
            fi
        done < <(find "$base_dir" -mindepth 1 -maxdepth 1 -type d -print0)
    done
    
    # Use the original identifier for error messages
    local clean_original="${identifier#\#}"
    
    if [[ ${#all_matches[@]} -eq 0 ]]; then
        if [[ "$identifier" == "main" ]]; then
            echo "ERROR: No worktree found for main branch (tried: ${search_identifiers[*]})" >&2
        else
            echo "ERROR: No worktree found for issue #$clean_original" >&2
        fi
        echo "."
        return 1
    elif [[ ${#all_matches[@]} -eq 1 ]]; then
        echo "${all_matches[0]}"
        return 0
    else
        if [[ "$identifier" == "main" ]]; then
            echo "WARNING: Multiple worktrees match main branch, using first match" >&2
        else
            echo "WARNING: Multiple worktrees match issue #$clean_original, using first match" >&2
        fi
        echo "${all_matches[0]}"
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