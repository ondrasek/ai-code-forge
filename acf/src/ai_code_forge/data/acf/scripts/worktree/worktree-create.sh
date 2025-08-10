#!/bin/bash
set -euo pipefail

# Git Worktree Creation Utility
# Creates and manages git worktrees for parallel development workflows
# Usage: ./worktree-create.sh <branch-name> [issue-number]

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
    
    # Enhanced repository name validation (security check)
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
Usage: $0 <branch-name> [issue-number]
       $0 --from-issue <issue-number>

Creates a git worktree for parallel development workflow.

Arguments:
  branch-name     Name of the branch to create worktree for
  issue-number    Optional GitHub issue number for validation
  --from-issue    Create worktree from GitHub issue (auto-detects or creates branch)

Examples:
  $0 feature/new-agent
  $0 claude/issue-105-worktree 105
  $0 --from-issue 105
  $0 hotfix/critical-bug

Location: Worktrees created in $WORKTREE_BASE/<repository>/<branch-name>
EOF
}

# Validate that path contains no symlinks (security check)
validate_no_symlinks() {
    local path="$1"
    local parent_path
    parent_path="$(dirname "$path")"
    
    # Check if target path or any parent is a symlink
    if [[ -L "$path" ]] || [[ -L "$parent_path" ]]; then
        print_error "Symlink detected in path - security violation"
        return 1
    fi
    
    # Check if any component in the path chain is a symlink
    local check_path="$path"
    while [[ "$check_path" != "/" && "$check_path" != "." ]]; do
        if [[ -L "$check_path" ]]; then
            print_error "Symlink detected in path chain - security violation"
            return 1
        fi
        check_path="$(dirname "$check_path")"
    done
    
    return 0
}

# Validate branch name
validate_branch_name() {
    local branch="$1"
    
    # Check for empty branch name
    if [[ -z "$branch" ]]; then
        print_error "Branch name cannot be empty"
        return 1
    fi
    
    # Check length (reasonable limit)
    if [[ ${#branch} -gt 100 ]]; then
        print_error "Branch name too long (max 100 characters)"
        return 1
    fi
    
    # Validate characters (alphanumeric, hyphens, underscores, forward slashes)
    if [[ ! "$branch" =~ ^[a-zA-Z0-9/_-]+$ ]]; then
        print_error "Branch name contains invalid characters. Only alphanumeric, hyphens, underscores, and forward slashes allowed"
        return 1
    fi
    
    # Comprehensive path traversal prevention
    local decoded_branch
    # Handle URL encoding and other escape sequences
    decoded_branch=$(printf '%b' "${branch//%/\\x}" 2>/dev/null || echo "$branch")
    
    # Check for various path traversal patterns
    if [[ "$decoded_branch" =~ \.\. ]] || 
       [[ "$decoded_branch" =~ ^/ ]] || 
       [[ "$decoded_branch" =~ //+ ]] ||
       [[ "$decoded_branch" =~ \\\.\\\.[\\/] ]] ||
       [[ "$branch" =~ %2e ]] || [[ "$branch" =~ %2f ]]; then
        print_error "Branch name contains path traversal sequences"
        return 1
    fi
    
    # Additional path validation with temporary directory test
    local test_base="/tmp/branch-validate-$$"
    local test_path="$test_base/$branch"
    mkdir -p "$test_base" 2>/dev/null
    local canonical_test_path
    canonical_test_path=$(realpath -m "$test_path" 2>/dev/null)
    local canonical_test_base
    canonical_test_base=$(realpath -m "$test_base" 2>/dev/null)
    if [[ ! "$canonical_test_path" == "$canonical_test_base/$branch" ]]; then
        rm -rf "$test_base" 2>/dev/null
        print_error "Branch name fails security validation"
        return 1
    fi
    rm -rf "$test_base" 2>/dev/null
    
    # Prevent git-sensitive names
    if [[ "$branch" =~ ^(HEAD|refs|objects|hooks)$ ]]; then
        print_error "Branch name conflicts with git internals"
        return 1
    fi
    
    return 0
}

# Find existing branch for GitHub issue
find_issue_branch() {
    local issue_num="$1"
    
    # Common branch naming patterns for issues
    local patterns=(
        "claude/issue-$issue_num-*"
        "issue-$issue_num-*"
        "issue/$issue_num-*"
        "feature/issue-$issue_num-*"
    )
    
    # Check local branches first
    for pattern in "${patterns[@]}"; do
        local found_branch
        found_branch=$(git branch --list "$pattern" 2>/dev/null | head -1 | sed 's/^[* ] *//')
        if [[ -n "$found_branch" ]]; then
            echo "$found_branch"
            return 0
        fi
    done
    
    # Check remote branches
    for pattern in "${patterns[@]}"; do
        local found_branch
        found_branch=$(git branch -r --list "origin/$pattern" 2>/dev/null | head -1 | sed 's/^[* ] *origin\///')
        if [[ -n "$found_branch" ]]; then
            echo "$found_branch"
            return 0
        fi
    done
    
    return 1
}

# Create branch name from GitHub issue
create_issue_branch_name() {
    local issue_num="$1"
    local issue_title=""
    
    # Try to get issue title from GitHub CLI
    if command -v gh >/dev/null 2>&1; then
        issue_title=$(gh issue view "$issue_num" --repo ondrasek/ai-code-forge --json title --jq .title 2>/dev/null || echo "")
    fi
    
    # Create branch name
    local branch_suffix=""
    local prefix="claude/issue-$issue_num-"
    local max_suffix_length=$((100 - ${#prefix}))
    
    if [[ -n "$issue_title" ]]; then
        # Convert title to branch-friendly format
        branch_suffix=$(echo "$issue_title" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-*\|-*$//g')
        # Ensure total branch name stays under 100 characters
        if [[ ${#branch_suffix} -gt $max_suffix_length ]]; then
            branch_suffix=$(echo "$branch_suffix" | cut -c1-$max_suffix_length)
        fi
    else
        branch_suffix="implementation"
    fi
    
    echo "claude/issue-$issue_num-$branch_suffix"
}

# Process --from-issue flag
process_issue_mode() {
    local issue_num="$1"
    
    print_info "Processing issue #$issue_num" >&2
    
    # Validate issue number
    validate_issue_number "$issue_num" || return 1
    
    # Look for existing branch
    local existing_branch
    if existing_branch=$(find_issue_branch "$issue_num"); then
        print_success "Found existing branch for issue #$issue_num: $existing_branch" >&2
        echo "$existing_branch"
        return 0
    fi
    
    # Create new branch name
    local new_branch
    new_branch=$(create_issue_branch_name "$issue_num")
    print_info "Creating new branch for issue #$issue_num: $new_branch" >&2
    echo "$new_branch"
    return 0
}

# Validate issue number (optional)
validate_issue_number() {
    local issue="$1"
    
    if [[ -n "$issue" ]]; then
        if [[ ! "$issue" =~ ^[0-9]+$ ]] || [[ $issue -lt 1 ]] || [[ $issue -gt 99999 ]]; then
            print_error "Issue number must be a positive integer (1-99999)"
            return 1
        fi
        
        # Validate issue exists on GitHub (if gh CLI available)
        if command -v gh >/dev/null 2>&1; then
            if ! gh issue view "$issue" --repo ondrasek/ai-code-forge --json number >/dev/null 2>&1; then
                print_error "Issue #$issue not found or not accessible on GitHub"
                print_info "Please verify the issue exists and you have access to it"
                print_info "Continue anyway? (y/N)"
                read -r confirm
                if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
                    print_info "Operation cancelled by user"
                    return 1
                fi
                print_warning "Proceeding with potentially invalid issue #$issue"
            else
                print_success "Validated issue #$issue exists on GitHub" >&2
            fi
        else
            print_warning "GitHub CLI not available - cannot validate issue #$issue"
            print_info "Continue without GitHub validation? (y/N)"
            read -r confirm
            if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
                print_info "Operation cancelled by user"
                return 1
            fi
        fi
    fi
    
    return 0
}

# Create worktree directory safely
create_worktree_path() {
    local branch="$1"
    local repo_name
    repo_name=$(get_repo_name) || return 1
    local worktree_path="$WORKTREE_BASE/$repo_name/$branch"
    
    # Ensure base directories exist - fix race condition by validating after creation
    if [[ ! -d "$WORKTREE_BASE" ]]; then
        print_info "Creating worktree base directory: $WORKTREE_BASE" >&2
        # Create directory first, then validate - prevents TOCTOU race condition
        if ! mkdir -p "$WORKTREE_BASE" 2>/dev/null; then
            print_error "Failed to create worktree base directory: $WORKTREE_BASE"
            return 1
        fi
        # Validate after creation to prevent race conditions
        validate_no_symlinks "$WORKTREE_BASE" || {
            rm -rf "$WORKTREE_BASE" 2>/dev/null
            print_error "Symlink security violation in worktree base path"
            return 1
        }
    fi
    
    local repo_base="$WORKTREE_BASE/$repo_name"
    if [[ ! -d "$repo_base" ]]; then
        print_info "Creating repository worktree directory: $repo_base" >&2
        # Create directory first, then validate - prevents TOCTOU race condition
        if ! mkdir -p "$repo_base" 2>/dev/null; then
            print_error "Failed to create repository directory: $repo_base"
            return 1
        fi
        # Validate after creation to prevent race conditions
        validate_no_symlinks "$repo_base" || {
            rm -rf "$repo_base" 2>/dev/null
            print_error "Symlink security violation in repository path"
            return 1
        }
    fi
    
    # Check if worktree already exists and validate no symlinks
    if [[ -d "$worktree_path" ]]; then
        print_error "Worktree already exists at path"
        return 1
    fi
    
    # Validate no symlinks in final path before creation
    validate_no_symlinks "$worktree_path" || return 1
    
    # Validate final path is within worktree base (security check)
    local canonical_path
    canonical_path=$(realpath -m "$worktree_path")
    local canonical_base
    canonical_base=$(realpath -m "$WORKTREE_BASE")
    
    if [[ ! "$canonical_path" =~ ^"$canonical_base"/ ]]; then
        print_error "Path escapes worktree security boundary"
        return 1
    fi
    
    echo "$canonical_path"
}

# Create git worktree
create_git_worktree() {
    local branch="$1"
    local worktree_path="$2"
    
    print_info "Creating git worktree for branch: $branch"
    
    # Change to main repository directory
    cd "$MAIN_REPO"
    
    # Check if branch exists locally or remotely
    local branch_exists=false
    if git show-ref --verify --quiet "refs/heads/$branch"; then
        print_info "Using existing local branch: $branch"
        branch_exists=true
    elif git show-ref --verify --quiet "refs/remotes/origin/$branch"; then
        print_info "Using existing remote branch: origin/$branch"
        branch_exists=true
    else
        print_info "Creating new branch: $branch"
    fi
    
    # Create worktree with proper shell safety
    local cmd_args=()
    if $branch_exists; then
        cmd_args=("worktree" "add" "--" "$worktree_path" "$branch")
    else
        # Create new branch based on current HEAD
        cmd_args=("worktree" "add" "-b" "$branch" "--" "$worktree_path")
    fi
    
    # Execute with array expansion to prevent injection
    if ! git "${cmd_args[@]}"; then
        return 1
    fi
    
    # Auto-push new branches to origin
    if ! $branch_exists; then
        print_info "Pushing new branch to origin: $branch"
        if git push --set-upstream origin "$branch"; then
            print_success "Branch pushed to origin successfully"
        else
            print_warning "Failed to push branch to origin (continuing anyway)"
            print_info "You can manually push later with: git push --set-upstream origin $branch"
        fi
    fi
    
    return 0
}

# Add comment to GitHub issue when branch is created
add_issue_comment() {
    local issue_num="$1"
    local branch_name="$2"
    
    # Only add comment if GitHub CLI is available and this is a new branch
    if ! command -v gh >/dev/null 2>&1; then
        print_warning "GitHub CLI not available - skipping issue comment"
        return 0
    fi
    
    print_info "Adding comment to issue #$issue_num"
    
    local comment_body="🚀 **Development branch created**

Branch \`$branch_name\` has been created for this issue.

**To work on this issue:**
\`\`\`bash
# Clone the worktree (if not already done)
git worktree add /workspace/worktrees/ai-code-forge/$branch_name $branch_name

# Or switch to existing worktree
cd /workspace/worktrees/ai-code-forge/$branch_name
\`\`\`

This comment was automatically generated by the worktree creation script."
    
    if gh issue comment "$issue_num" --repo ondrasek/ai-code-forge --body "$comment_body" 2>/dev/null; then
        print_success "Comment added to issue #$issue_num"
    else
        print_warning "Failed to add comment to issue #$issue_num (continuing anyway)"
    fi
}

# Main execution
main() {
    local branch_name=""
    local issue_number=""
    local from_issue_mode=false
    
    # Parse arguments
    case "${1:-}" in
        "--from-issue")
            if [[ $# -lt 2 ]]; then
                print_error "--from-issue requires an issue number"
                show_usage
                exit 1
            fi
            from_issue_mode=true
            issue_number="$2"
            ;;
        "")
            print_error "Missing required arguments"
            show_usage
            exit 1
            ;;
        *)
            branch_name="$1"
            issue_number="${2:-}"
            ;;
    esac
    
    print_info "Git Worktree Creation Utility"
    print_info "=============================="
    
    # Handle --from-issue mode
    if $from_issue_mode; then
        if branch_name=$(process_issue_mode "$issue_number"); then
            print_info "Using branch: $branch_name"
        else
            print_error "Failed to process issue #$issue_number"
            exit 1
        fi
    fi
    
    # Validate inputs
    validate_branch_name "$branch_name" || exit 1
    validate_issue_number "$issue_number" || exit 1
    
    # Create worktree path
    local worktree_path
    worktree_path=$(create_worktree_path "$branch_name") || exit 1
    
    # Create git worktree
    if create_git_worktree "$branch_name" "$worktree_path"; then
        print_success "Worktree created successfully!"
        print_info "Location: $worktree_path"
        
        # Add comment to GitHub issue if this was created from an issue
        if $from_issue_mode && [[ -n "$issue_number" ]]; then
            add_issue_comment "$issue_number" "$branch_name"
        fi
        
        print_info ""
        print_info "To work in this worktree:"
        print_info "  cd \"$worktree_path\""
        print_info "  # Launch Claude Code from this directory"
    else
        print_error "Failed to create git worktree: $worktree_path"
        # Comprehensive cleanup on failure - remove git state and directory
        if [[ -d "$worktree_path" ]]; then
            print_info "Cleaning up partial worktree creation: $worktree_path"
            # Remove git worktree reference first (most important)
            local cleanup_args=("worktree" "remove" "--force" "--" "$worktree_path")
            if git "${cleanup_args[@]}" 2>/dev/null; then
                print_info "Git worktree reference removed successfully"
            else
                print_warning "Could not remove git worktree reference (may not exist)"
            fi
            # Remove directory structure with secure command
            local rm_args=("rm" "-rf" "--" "$worktree_path")
            if "${rm_args[@]}" 2>/dev/null; then
                print_info "Directory structure removed: $worktree_path"
            else
                print_error "Failed to remove directory structure: $worktree_path"
            fi
            print_success "Cleanup completed for failed worktree creation"
        fi
        exit 1
    fi
}

# Check arguments
if [[ $# -lt 1 ]] || [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    show_usage
    exit 0
fi

# Execute main function
main "$@"