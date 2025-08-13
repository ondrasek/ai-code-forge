#!/bin/bash
set -euo pipefail

# Git Worktree Launch Utility
# Launches Claude Code in specified worktree directory
# Usage: ./worktree-launch.sh <issue-number|branch-name|directory-path> [claude-options]

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

# Show usage information
show_usage() {
    cat << EOF
Git Worktree Launch Utility

DESCRIPTION:
    Launch Claude Code in a specific worktree directory.
    Automatically finds the worktree for the given issue number or branch name.

USAGE:
    $0 <issue-number|branch-name|directory-path> [claude-options]

ARGUMENTS:
    issue-number    Issue number (e.g., 123, #123)
    branch-name     Branch name (e.g., main, feature/add-launch)
    directory-path  Directory path (e.g., issue-129, custom-dir)
    claude-options  Additional options to pass to Claude Code

EXAMPLES:
    $0 123                          # Launch Claude Code in worktree for issue #123
    $0 \#129                         # Launch Claude Code in worktree for issue #129
    $0 main                         # Launch Claude Code in worktree for main branch
    $0 feature/add-launch          # Launch Claude Code in specific branch worktree
    $0 129 --resume                # Launch with resume option
    $0 123 "help with testing"     # Launch with initial query

NOTES:
    - This script cannot change your shell's working directory
    - You'll need to manually 'cd' to the worktree directory if needed
    - The script launches Claude Code directly in the target worktree

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
        print_error "Unable to determine repository name"
        return 1
    fi
    
    echo "$repo_name"
}

# Validate and sanitize branch name input for security
validate_branch_name() {
    local branch="$1"
    
    # Basic security checks - prevent injection attacks
    if [[ "$branch" =~ \.\. ]] || [[ "$branch" =~ ^- ]] || [[ "$branch" =~ ^/ ]]; then
        return 1
    fi
    
    # Check for dangerous characters that could enable injection
    if [[ "$branch" =~ [\;\|\&\$\`\(\)\{\}\[\]\<\>] ]]; then
        return 1
    fi
    
    # Validate against git naming rules
    if ! git check-ref-format "refs/heads/$branch" 2>/dev/null; then
        return 1
    fi
    
    return 0
}

# Find worktree by branch name using git worktree list
find_worktree_by_branch() {
    local branch="$1"
    
    # Validate branch name for security
    if ! validate_branch_name "$branch"; then
        return 1
    fi
    
    # Use git worktree list to find the worktree with this branch
    local worktree_path
    worktree_path=$(git worktree list --porcelain | awk -v branch="$branch" '
        /^worktree / { path = substr($0, 10) }
        /^branch refs\/heads\// && substr($0, 19) == branch { print path; exit }
    ')
    
    if [[ -n "$worktree_path" ]]; then
        echo "$worktree_path"
        return 0
    fi
    
    # Special case for HEAD (detached HEAD)
    if [[ "$branch" == "HEAD" ]]; then
        local detached_path
        detached_path=$(git worktree list --porcelain | awk '
            /^worktree / { path = substr($0, 10) }
            /^detached$/ { print path; exit }
        ')
        if [[ -n "$detached_path" ]]; then
            print_warning "Found detached HEAD worktree for '$branch'"
            echo "$detached_path"
            return 0
        fi
    fi
    
    # Check if branch exists but is not checked out in any worktree
    if git show-ref --verify --quiet "refs/heads/$branch"; then
        print_warning "Branch '$branch' exists but is not checked out in any worktree"
        print_info "Available worktrees:"
        git worktree list --porcelain | awk '
            /^worktree / { path = substr($0, 10) }
            /^branch refs\/heads\// { branch = substr($0, 19) }
            /^bare$/ { bare = 1 }
            /^detached$/ { detached = 1 }
            /^$/ {
                if (bare) {
                    printf "  %s (bare repository)\n", path
                } else if (detached) {
                    printf "  %s (detached HEAD)\n", path
                } else if (branch) {
                    printf "  %s (%s)\n", path, branch
                }
                branch = ""; bare = 0; detached = 0
            }
        ' | sed 's/^/  /'
        return 1
    fi
    
    return 1
}

# Determine if identifier is a branch name or directory path
is_branch_identifier() {
    local identifier="$1"
    
    # If it's an absolute path or contains directory separators beyond simple branch naming, treat as path
    if [[ "$identifier" =~ ^/ ]] || [[ "$identifier" =~ \.\. ]]; then
        return 1
    fi
    
    # If it exists as a directory in the worktree base, treat as directory path
    local repo_name
    if repo_name=$(get_repo_name 2>/dev/null); then
        local base_dir="$WORKTREE_BASE/$repo_name"
        local clean_id="${identifier#\#}"
        if [[ -d "$base_dir/$clean_id" ]]; then
            return 1  # Directory exists, treat as path
        fi
    fi
    
    # If it passes basic branch name validation, treat as branch
    if validate_branch_name "$identifier"; then
        return 0
    fi
    
    # Default to directory path
    return 1
}

# Find worktree directory for issue number, branch name, or directory path
find_worktree_dir() {
    local identifier="$1"
    local repo_name
    repo_name=$(get_repo_name) || return 1
    
    local base_dir="$WORKTREE_BASE/$repo_name"
    
    # Clean up identifier (remove # prefix if present)
    local clean_id="${identifier#\#}"
    
    # First, try branch resolution if identifier looks like a branch name
    if is_branch_identifier "$clean_id"; then
        local branch_worktree
        if branch_worktree=$(find_worktree_by_branch "$clean_id"); then
            echo "$branch_worktree"
            return 0
        fi
    fi
    
    # Fall back to directory-based resolution
    if [[ ! -d "$base_dir" ]]; then
        print_error "No worktrees found in $base_dir"
        return 1
    fi
    
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
        # If branch resolution was attempted but failed, provide specific error
        if is_branch_identifier "$clean_id"; then
            print_error "No worktree found for branch '$clean_id' and no matching directories"
            print_info "To see all worktrees: git worktree list"
        else
            print_error "No worktree found for identifier '$identifier'"
        fi
        print_info "Available worktrees:"
        if [[ -d "$base_dir" ]]; then
            ls -1 "$base_dir" | sed 's/^/  /' || true
        fi
        return 1
    elif [[ ${#matches[@]} -eq 1 ]]; then
        echo "${matches[0]}"
        return 0
    else
        print_warning "Multiple worktrees match '$identifier':"
        for match in "${matches[@]}"; do
            print_info "  $(basename "$match")"
        done
        print_info "Using first match: $(basename "${matches[0]}")"
        echo "${matches[0]}"
        return 0
    fi
}

# Check if Claude Code command exists and is available
check_claude_available() {
    if ! command -v claude >/dev/null 2>&1; then
        # Try launch-claude.sh script
        local launch_script="$SCRIPT_DIR/../launch-claude.sh"
        if [[ -f "$launch_script" ]]; then
            echo "launch_script"
            return 0
        else
            print_error "Claude Code not found. Please install Claude Code or ensure launch-claude.sh exists"
            return 1
        fi
    else
        echo "claude"
        return 0
    fi
}

# Main function
main() {
    if [[ $# -eq 0 ]]; then
        print_error "Missing required argument"
        show_usage
        exit 1
    fi
    
    local identifier="$1"
    shift
    local claude_args=("$@")
    
    # Handle help
    if [[ "$identifier" == "--help" || "$identifier" == "-h" || "$identifier" == "help" ]]; then
        show_usage
        exit 0
    fi
    
    # Find worktree directory
    print_info "Looking for worktree matching '$identifier'..."
    local worktree_dir
    worktree_dir=$(find_worktree_dir "$identifier") || exit 1
    
    print_success "Found worktree: $(basename "$worktree_dir")"
    print_info "Worktree path: $worktree_dir"
    
    # Verify worktree directory is valid git repository
    # Main repo has .git directory, worktrees have .git file pointing to gitdir
    if [[ ! -e "$worktree_dir/.git" ]]; then
        print_error "Directory $worktree_dir is not a valid git repository"
        exit 1
    fi
    
    # Check Claude availability
    local claude_command
    claude_command=$(check_claude_available) || exit 1
    
    # Launch Claude Code in the worktree directory
    print_info "Launching Claude Code in worktree directory..."
    print_warning "Note: Your shell working directory remains unchanged"
    
    # Add dry-run option for testing
    if [[ "${claude_args[0]:-}" == "--dry-run" ]]; then
        print_info "DRY RUN: Would change to directory: $worktree_dir"
        if [[ "$claude_command" == "launch_script" ]]; then
            local launch_script="$SCRIPT_DIR/../launch-claude.sh"
            print_info "DRY RUN: Would execute: $launch_script ${claude_args[@]:1}"
        else
            print_info "DRY RUN: Would execute: claude ${claude_args[@]:1}"
        fi
        print_success "Launch command validation successful"
        exit 0
    fi
    
    cd "$worktree_dir"
    
    # Update terminal title with issue context
    if [[ -f "$SCRIPT_DIR/worktree-title.sh" ]]; then
        source "$SCRIPT_DIR/worktree-title.sh"
        # Extract issue number from identifier or use auto-detection
        if [[ "$identifier" =~ ^#?([0-9]+)$ ]]; then
            update_terminal_title "${BASH_REMATCH[1]}" "$(basename "$worktree_dir")"
        else
            update_title_from_context "$(basename "$worktree_dir")"
        fi
    fi
    
    if [[ "$claude_command" == "launch_script" ]]; then
        local launch_script="$SCRIPT_DIR/../launch-claude.sh"
        print_info "Using launch-claude.sh script"
        exec "$launch_script" "${claude_args[@]}"
    else
        print_info "Using claude command directly"
        exec claude "${claude_args[@]}"
    fi
}

# Run main function with all arguments
main "$@"