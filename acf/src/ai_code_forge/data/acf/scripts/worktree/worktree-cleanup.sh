#!/bin/bash
set -euo pipefail

# Git Worktree Cleanup Utility
# Lists and removes git worktrees for workspace management
# Usage: ./worktree-cleanup.sh [list|remove <worktree-path>|remove-all]

WORKTREE_BASE="/workspace/worktrees"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_REPO="$(cd "$SCRIPT_DIR/.." && pwd)"

# Determine repository name dynamically
get_repo_name() {
    local repo_name=""
    
    # Try GitHub CLI first (if available and authenticated)
    if command -v gh >/dev/null 2>&1; then
        repo_name=$(gh repo view --json name --jq .name 2>/dev/null || echo "")
    fi
    
    # Fallback to basename of repository directory
    if [[ -z "$repo_name" ]]; then
        repo_name=$(basename "$MAIN_REPO")
    fi
    
    # Enhanced repository name validation (standardized security check)
    if [[ ! "$repo_name" =~ ^[a-zA-Z0-9][a-zA-Z0-9._-]*$ ]] || 
       [[ ${#repo_name} -gt 50 ]] ||
       [[ "$repo_name" =~ \.\. ]] ||
       [[ "$repo_name" =~ ^\. ]] ||
       [[ "$repo_name" =~ \$ ]]; then
        print_error "Invalid repository name detected"
        return 1
    fi
    
    # Test path resolution safety
    local test_base="/tmp/repo-validate-$$"
    local test_path="$test_base/$repo_name"
    mkdir -p "$test_base" 2>/dev/null
    if ! realpath -m "$test_path" 2>/dev/null | grep -q "^$test_base/[^/]*$"; then
        rm -rf "$test_base" 2>/dev/null
        print_error "Repository name fails path validation"
        return 1
    fi
    rm -rf "$test_base" 2>/dev/null
    
    echo "$repo_name"
}

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

# Usage information
show_usage() {
    cat << EOF
Usage: $0 [command] [arguments]

Commands:
  list                    List all existing worktrees
  remove <worktree-path>  Remove specific worktree
  remove-all             Remove all worktrees (with confirmation)
  prune                  Remove stale worktree references
  help                   Show this help message

Examples:
  $0 list
  $0 remove /workspace/worktrees/feature-branch
  $0 remove-all
  $0 prune

Location: Manages worktrees in $WORKTREE_BASE/<repository>/
EOF
}

# List all worktrees
list_worktrees() {
    print_info "Git Worktree Status"
    print_info "=================="
    
    cd "$MAIN_REPO"
    
    # Use git worktree list for accurate information
    if git worktree list >/dev/null 2>&1; then
        git worktree list --porcelain | while IFS= read -r line; do
            if [[ "$line" =~ ^worktree ]]; then
                local path="${line#worktree }"
                if [[ "$path" =~ ^$WORKTREE_BASE/ ]]; then
                    echo -e "${GREEN}•${NC} $path"
                else
                    echo -e "${BLUE}•${NC} $path (main)"
                fi
            elif [[ "$line" =~ ^branch ]]; then
                local branch="${line#branch refs/heads/}"
                echo -e "  ${YELLOW}Branch:${NC} $branch"
            elif [[ "$line" =~ ^HEAD ]]; then
                local commit="${line#HEAD }"
                echo -e "  ${BLUE}Commit:${NC} ${commit:0:8}"
            elif [[ -z "$line" ]]; then
                echo
            fi
        done
    else
        print_error "Failed to list worktrees"
        return 1
    fi
    
    # Show worktree base directory contents for comparison
    local repo_name
    if repo_name=$(get_repo_name 2>/dev/null); then
        local repo_base="$WORKTREE_BASE/$repo_name"
        if [[ -d "$repo_base" ]]; then
            print_info "Repository worktree directory contents ($repo_name):"
            find "$repo_base" -maxdepth 1 -type d | sort | while read -r dir; do
                if [[ "$dir" != "$repo_base" ]]; then
                    echo -e "  ${YELLOW}Directory:${NC} $dir"
                fi
            done
        else
            print_info "No repository worktree directory found at: $repo_base"
        fi
    else
        print_info "Could not determine repository name for worktree listing"
    fi
}

# Validate worktree path
validate_worktree_path() {
    local path="$1"
    
    # Check if path is provided
    if [[ -z "$path" ]]; then
        print_error "Worktree path cannot be empty"
        return 1
    fi
    
    # Resolve to canonical path
    if [[ ! -d "$path" ]]; then
        print_error "Worktree directory does not exist: $path"
        return 1
    fi
    
    local canonical_path
    canonical_path=$(realpath "$path")
    local canonical_base
    canonical_base=$(realpath "$WORKTREE_BASE")
    
    # Ensure path is within worktree base (security check)
    if [[ ! "$canonical_path" =~ ^"$canonical_base"/ ]]; then
        print_error "Path is outside worktree base: $canonical_path"
        return 1
    fi
    
    echo "$canonical_path"
}

# Remove single worktree
remove_worktree() {
    local worktree_path="$1"
    local validated_path
    
    validated_path=$(validate_worktree_path "$worktree_path") || return 1
    
    print_info "Removing worktree: $validated_path"
    
    cd "$MAIN_REPO"
    
    # Check if this is a valid git worktree
    if ! git worktree list --porcelain | grep -q "^worktree $validated_path$"; then
        print_warning "Path is not a registered git worktree: $validated_path"
        print_info "Attempting to remove directory anyway..."
    fi
    
    # Remove from git worktree management with proper safety
    local cleanup_args=("worktree" "remove" "--" "$validated_path")
    if git "${cleanup_args[@]}" 2>/dev/null; then
        print_success "Git worktree removed successfully"
    else
        print_warning "Failed to remove git worktree (may already be removed)"
        
        # Manual cleanup if git worktree remove failed - secure implementation
        if [[ -d "$validated_path" ]]; then
            print_info "Removing directory manually: $validated_path"
            # Use array-based command to prevent injection
            local rm_args=("rm" "-rf" "--" "$validated_path")
            if "${rm_args[@]}"; then
                print_success "Directory removed manually: $validated_path"
                return 0
            else
                print_error "Failed to remove directory manually: $validated_path"
                return 1
            fi
        fi
    fi
    
    # Clean up any remaining parent directories if empty
    local parent_dir
    parent_dir=$(dirname "$validated_path")
    if [[ "$parent_dir" != "$WORKTREE_BASE" ]] && [[ -d "$parent_dir" ]]; then
        if rmdir "$parent_dir" 2>/dev/null; then
            print_info "Removed empty parent directory: $parent_dir"
        fi
    fi
}

# Remove all worktrees with confirmation
remove_all_worktrees() {
    print_warning "This will remove ALL worktrees in $WORKTREE_BASE"
    
    # List what will be removed
    if [[ -d "$WORKTREE_BASE" ]]; then
        print_info "Worktrees to be removed:"
        find "$WORKTREE_BASE" -mindepth 1 -maxdepth 1 -type d | while read -r dir; do
            echo -e "  ${RED}•${NC} $dir"
        done
    else
        print_info "No worktree base directory found"
        return 0
    fi
    
    # Confirmation prompt
    echo -n "Are you sure? Type 'yes' to confirm: "
    read -r confirmation
    
    if [[ "$confirmation" != "yes" ]]; then
        print_info "Operation cancelled"
        return 0
    fi
    
    cd "$MAIN_REPO"
    
    # Remove all worktrees managed by git
    git worktree list --porcelain | grep "^worktree" | while read -r line; do
        local path="${line#worktree }"
        if [[ "$path" =~ ^$WORKTREE_BASE/ ]]; then
            print_info "Removing: $path"
            remove_worktree "$path"
        fi
    done
    
    # Clean up any remaining directories
    if [[ -d "$WORKTREE_BASE" ]]; then
        find "$WORKTREE_BASE" -mindepth 1 -maxdepth 1 -type d | while read -r dir; do
            print_info "Cleaning up remaining directory: $dir"
            rm -rf "$dir"
        done
        
        # Remove base directory if empty
        if rmdir "$WORKTREE_BASE" 2>/dev/null; then
            print_success "Removed empty worktree base directory"
        fi
    fi
    
    print_success "All worktrees removed"
}

# Prune stale worktree references
prune_worktrees() {
    print_info "Pruning stale worktree references"
    
    cd "$MAIN_REPO"
    
    if git worktree prune -v; then
        print_success "Worktree references pruned successfully"
    else
        print_error "Failed to prune worktree references"
        return 1
    fi
}

# Main execution
main() {
    local command="${1:-list}"
    
    case "$command" in
        "list"|"")
            list_worktrees
            ;;
        "remove")
            if [[ $# -lt 2 ]]; then
                print_error "remove command requires worktree path"
                show_usage
                exit 1
            fi
            remove_worktree "$2"
            ;;
        "remove-all")
            remove_all_worktrees
            ;;
        "prune")
            prune_worktrees
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            print_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"