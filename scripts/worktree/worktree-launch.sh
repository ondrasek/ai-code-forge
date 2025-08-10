#!/bin/bash
set -euo pipefail

# Git Worktree Launch Utility
# Launches Claude Code in specified worktree directory
# Usage: ./worktree-launch.sh <issue-number|branch-name> [claude-options]

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
    $0 <issue-number|branch-name> [claude-options]

ARGUMENTS:
    issue-number    Issue number (e.g., 123, #123)
    branch-name     Full branch name (e.g., feature/add-launch, 129)
    claude-options  Additional options to pass to Claude Code

EXAMPLES:
    $0 123                          # Launch Claude Code in worktree for issue #123
    $0 \#129                         # Launch Claude Code in worktree for issue #129
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

# Find worktree directory for issue number or branch name
find_worktree_dir() {
    local identifier="$1"
    local repo_name
    repo_name=$(get_repo_name) || return 1
    
    local base_dir="$WORKTREE_BASE/$repo_name"
    
    if [[ ! -d "$base_dir" ]]; then
        print_error "No worktrees found in $base_dir"
        return 1
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
        print_error "No worktree found for identifier '$identifier'"
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
    if [[ ! -e "$worktree_dir/.git" ]]; then
        print_error "Directory $worktree_dir is not a valid git worktree"
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