#!/bin/bash
set -euo pipefail

# Git Worktree Creation Utility
# Creates and manages git worktrees for parallel development workflows
# Usage: ./worktree-create.sh <branch-name> [issue-number]

WORKTREE_BASE="/workspace/worktrees"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_REPO="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Get repository full name (owner/repo) dynamically
get_repo_full_name() {
    local repo_full_name=""
    
    # Try GitHub CLI first (if available and authenticated)
    if command -v gh >/dev/null 2>&1; then
        repo_full_name=$(gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null || echo "")
    fi
    
    # Fallback to git remote origin URL parsing
    if [[ -z "$repo_full_name" ]]; then
        local remote_url
        remote_url=$(git remote get-url origin 2>/dev/null || echo "")
        if [[ -n "$remote_url" ]]; then
            # Parse GitHub URL formats:
            # https://github.com/owner/repo.git
            # git@github.com:owner/repo.git
            if [[ "$remote_url" =~ github\.com[:/]([^/]+/[^/]+)(\.git)?$ ]]; then
                repo_full_name="${BASH_REMATCH[1]%.git}"
            fi
        fi
    fi
    
    # Validate format
    if [[ "$repo_full_name" =~ ^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$ ]]; then
        echo "$repo_full_name"
        return 0
    else
        print_error "Unable to determine GitHub repository (owner/repo format)" >&2
        return 1
    fi
}

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
Usage: $0 <branch-name-or-issue> [issue-number] [--dry-run]
       $0 --from-issue <issue-number> [--dry-run]
       $0 --numeric-only <branch-name> [--dry-run]

Creates a git worktree for parallel development workflow.
When a numeric value is provided as branch-name-or-issue, automatically creates
descriptive branch name from GitHub issue (equivalent to --from-issue).

Arguments:
  branch-name-or-issue  Branch name OR issue number (auto-detected)
  issue-number         Optional GitHub issue number for validation
  --from-issue         Create worktree from GitHub issue (auto-detects or creates branch)
  --numeric-only       Force numeric branch name (disables auto-detection)
  --dry-run           Show what commands would be executed without running them

Examples:
  $0 132                    # Auto-detects issue, creates "issue-132-descriptive-name"
  $0 feature/new-agent      # Uses literal branch name
  $0 --from-issue 105       # Explicit issue mode
  $0 --numeric-only 132     # Forces branch name "132" (no auto-detection)
  $0 --from-issue 105 --dry-run

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
        "issue-$issue_num-*"
        "issue-$issue_num-*"
        "issue/$issue_num-*"
        "feature/issue-$issue_num-*"
    )

    # Check local branches first
    for pattern in "${patterns[@]}"; do
        local found_branch
        found_branch=$(git branch --list "$pattern" 2>/dev/null | head -1 | sed 's/^[*+ ] *//')
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
        local repo_full_name
        if repo_full_name=$(get_repo_full_name); then
            issue_title=$(gh issue view "$issue_num" --repo "$repo_full_name" --json title --jq .title 2>/dev/null || echo "")
        fi
    fi

    # Create branch name with smart truncation
    local branch_suffix=""
    local prefix="issue-$issue_num-"
    local max_total_length=35  # Keep total branch name short
    local max_suffix_length=$((max_total_length - ${#prefix}))

    if [[ -n "$issue_title" ]]; then
        # Convert title to branch-friendly format
        local clean_title=$(echo "$issue_title" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-*\|-*$//g')
        
        # Smart truncation: keep meaningful words, truncate at word boundaries
        if [[ ${#clean_title} -gt $max_suffix_length ]]; then
            # Extract first few meaningful words (skip common words)
            local words=($(echo "$clean_title" | tr '-' '\n' | grep -vE '^(the|and|or|for|with|from|in|on|at|by|of|a|an|that|this|is|are|will|should|would|could|to)$' | head -4))
            
            branch_suffix=""
            local current_length=0
            for word in "${words[@]}"; do
                local test_suffix="${branch_suffix}${branch_suffix:+-}${word}"
                if [[ ${#test_suffix} -le $max_suffix_length ]]; then
                    branch_suffix="$test_suffix"
                    current_length=${#branch_suffix}
                else
                    break
                fi
            done
            
            # If no meaningful words found or result too short, use truncated original
            if [[ ${#branch_suffix} -lt 4 ]]; then
                branch_suffix=$(echo "$clean_title" | cut -c1-$((max_suffix_length-3)))
                # Remove partial word at end
                branch_suffix=$(echo "$branch_suffix" | sed 's/-[^-]*$//')
                [[ -n "$branch_suffix" ]] || branch_suffix="work"
            fi
        else
            branch_suffix="$clean_title"
        fi
    else
        branch_suffix="work"
    fi

    echo "issue-$issue_num-$branch_suffix"
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
            local repo_full_name
            if repo_full_name=$(get_repo_full_name); then
                if ! gh issue view "$issue" --repo "$repo_full_name" --json number >/dev/null 2>&1; then
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

# Create worktree directory name from branch
create_worktree_directory_name() {
    local branch="$1"
    
    # Extract issue number if this is an issue-based branch
    if [[ "$branch" =~ ^issue-([0-9]+)- ]]; then
        echo "issue-${BASH_REMATCH[1]}"
        return 0
    fi
    
    # For non-issue branches, use the branch name as-is
    echo "$branch"
}

# Create worktree directory safely
create_worktree_path() {
    local branch="$1"
    local repo_name
    repo_name=$(get_repo_name) || return 1
    
    # Get directory name (may differ from branch name)
    local directory_name
    directory_name=$(create_worktree_directory_name "$branch")
    local worktree_path="$WORKTREE_BASE/$repo_name/$directory_name"

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
        # Special handling for issue-based directories that might be reused
        if [[ "$directory_name" =~ ^issue-[0-9]+$ ]]; then
            print_error "Worktree directory '$directory_name' already exists"
            print_info "This issue may already have a worktree. Use different branch name or remove existing worktree."
            print_info "Existing worktree path: $worktree_path"
        else
            print_error "Worktree already exists at path: $worktree_path"
        fi
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
# Returns: 0 if successful, 1 if failed
# Sets global variable 'branch_was_created' to true if new branch was created, false if existing branch was used
create_git_worktree() {
    local branch="$1"
    local worktree_path="$2"
    local dry_run="${3:-false}"

    if [[ "$dry_run" == "true" ]]; then
        print_info "[DRY RUN] Would create git worktree for branch: $branch"
        print_info "[DRY RUN] Would change to directory: $MAIN_REPO"
    else
        print_info "Creating git worktree for branch: $branch"
        # Change to main repository directory
        cd "$MAIN_REPO"
    fi

    # Check if branch exists locally or remotely
    local branch_exists=false
    if [[ "$dry_run" == "true" ]]; then
        print_info "[DRY RUN] Would check if branch exists with: git show-ref --verify --quiet refs/heads/$branch"
        print_info "[DRY RUN] Would check if remote branch exists with: git show-ref --verify --quiet refs/remotes/origin/$branch"
        print_info "[DRY RUN] Assuming new branch for demonstration"
        branch_exists=false
    else
        if git show-ref --verify --quiet "refs/heads/$branch"; then
            print_info "Using existing local branch: $branch"
            branch_exists=true
        elif git show-ref --verify --quiet "refs/remotes/origin/$branch"; then
            print_info "Using existing remote branch: origin/$branch"
            branch_exists=true
        else
            print_info "Creating new branch: $branch"
        fi
    fi

    # Set global variable to indicate if branch was newly created
    branch_was_created=true
    if $branch_exists; then
        branch_was_created=false
    fi

    # Clean up any stale worktree registrations first
    print_info "Cleaning up stale worktree registrations..."
    git worktree prune 2>/dev/null || true
    
    # Create worktree with proper shell safety
    local cmd_args=()
    if $branch_exists; then
        cmd_args=("git" "worktree" "add" "--" "$worktree_path" "$branch")
    else
        # Create new branch based on current HEAD
        cmd_args=("git" "worktree" "add" "-b" "$branch" "--" "$worktree_path")
    fi

    # Execute with array expansion to prevent injection
    if [[ "$dry_run" == "true" ]]; then
        print_info "[DRY RUN] Would execute: git worktree prune"
        print_info "[DRY RUN] Would execute: ${cmd_args[*]}"
    else
        if ! git "${cmd_args[@]:1}"; then  # Remove 'git' from array since we're calling git directly
            return 1
        fi
    fi

    # Auto-push new branches to origin
    if ! $branch_exists; then
        if [[ "$dry_run" == "true" ]]; then
            print_info "[DRY RUN] Would push new branch: git push --set-upstream origin $branch"
        else
            print_info "Pushing new branch to origin: $branch"
            if git push --set-upstream origin "$branch"; then
                print_success "Branch pushed to origin successfully"
            else
                print_warning "Failed to push branch to origin (continuing anyway)"
                print_info "You can manually push later with: git push --set-upstream origin $branch"
            fi
        fi
    fi

    return 0
}

# Add comment to GitHub issue when branch is created
add_issue_comment() {
    local issue_num="$1"
    local branch_name="$2"
    local dry_run="${3:-false}"

    # Only add comment if GitHub CLI is available and this is a new branch
    if ! command -v gh >/dev/null 2>&1; then
        print_warning "GitHub CLI not available - skipping issue comment"
        return 0
    fi

    if [[ "$dry_run" == "true" ]]; then
        print_info "[DRY RUN] Would add comment to issue #$issue_num"
        print_info "[DRY RUN] Would change to directory: $MAIN_REPO"
        
        # Still get repo info for dry run demo
        local repo_full_name="owner/repo"  # placeholder for dry run
        local branch_url="https://github.com/${repo_full_name}/tree/${branch_name}"
        local comment_body="Branch [$branch_name]($branch_url)"
        
        print_info "[DRY RUN] Would execute: gh issue comment $issue_num --repo <detected-repo> --body '$comment_body'"
        return 0
    fi

    print_info "Adding comment to issue #$issue_num"

    # Ensure we're in the main repository directory for accurate repo info
    cd "$MAIN_REPO"

    # Get repository info for branch URL and commenting
    local repo_full_name
    if ! repo_full_name=$(get_repo_full_name); then
        print_error "Unable to determine repository for GitHub operations"
        return 1
    fi
    
    # Create GitHub branch URL
    local branch_url="https://github.com/${repo_full_name}/tree/${branch_name}"
    
    local comment_body="Branch [$branch_name]($branch_url)"

    if gh issue comment "$issue_num" --repo "$repo_full_name" --body "$comment_body" 2>/dev/null; then
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
    local numeric_only_mode=false
    local dry_run=false

    # Parse arguments
    local args=("$@")
    local arg_count=$#
    
    # Check for --dry-run flag and remove it from args
    for i in "${!args[@]}"; do
        if [[ "${args[i]}" == "--dry-run" ]]; then
            dry_run=true
            unset 'args[i]'
            ((arg_count--))
        fi
    done
    
    # Rebuild args array
    local clean_args=()
    for arg in "${args[@]}"; do
        [[ -n "$arg" ]] && clean_args+=("$arg")
    done

    case "${clean_args[0]:-}" in
        "--from-issue")
            if [[ ${#clean_args[@]} -lt 2 ]]; then
                print_error "--from-issue requires an issue number"
                show_usage
                exit 1
            fi
            from_issue_mode=true
            issue_number="${clean_args[1]}"
            ;;
        "--numeric-only")
            if [[ ${#clean_args[@]} -lt 2 ]]; then
                print_error "--numeric-only requires a branch name"
                show_usage
                exit 1
            fi
            numeric_only_mode=true
            branch_name="${clean_args[1]}"
            issue_number="${clean_args[2]:-}"
            ;;
        "")
            print_error "Missing required arguments"
            show_usage
            exit 1
            ;;
        *)
            # Auto-detection logic: if first argument is purely numeric, treat as issue
            if [[ "${clean_args[0]}" =~ ^[0-9]+$ ]] && [[ ! "$numeric_only_mode" == "true" ]]; then
                print_info "Auto-detected issue number: ${clean_args[0]}"
                from_issue_mode=true
                issue_number="${clean_args[0]}"
            else
                branch_name="${clean_args[0]}"
                issue_number="${clean_args[1]:-}"
            fi
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
    if [[ "$dry_run" == "true" ]]; then
        print_info "[DRY RUN] Would create worktree path for branch: $branch_name"
        local directory_name
        directory_name=$(create_worktree_directory_name "$branch_name")
        worktree_path="/workspace/worktrees/$(basename "$MAIN_REPO")/$directory_name"  # simulated path
        print_info "[DRY RUN] Simulated path: $worktree_path"
    else
        worktree_path=$(create_worktree_path "$branch_name") || exit 1
    fi

    # Create git worktree
    if create_git_worktree "$branch_name" "$worktree_path" "$dry_run"; then
        if [[ "$dry_run" == "true" ]]; then
            print_success "[DRY RUN] Would create worktree successfully!"
            print_info "[DRY RUN] Location would be: $worktree_path"
        else
            print_success "Worktree created successfully!"
            print_info "Location: $worktree_path"
        fi

        # Add comment to GitHub issue only if this was created from an issue AND a new branch was created
        if $from_issue_mode && [[ -n "$issue_number" ]] && [[ "$branch_was_created" == "true" ]]; then
            add_issue_comment "$issue_number" "$branch_name" "$dry_run"
        elif $from_issue_mode && [[ -n "$issue_number" ]] && [[ "$branch_was_created" == "false" ]]; then
            print_info "Using existing branch - skipping GitHub issue comment"
        fi

        # Update terminal title if we're in an issue context
        if [[ "$dry_run" == "false" ]] && [[ -f "$SCRIPT_DIR/worktree-title.sh" ]]; then
            source "$SCRIPT_DIR/worktree-title.sh"
            if $from_issue_mode && [[ -n "$issue_number" ]]; then
                # Change to the worktree directory temporarily to update title context
                local original_pwd=$(pwd)
                cd "$worktree_path" 2>/dev/null || true
                update_terminal_title "$issue_number" "$(basename "$worktree_path")"
                cd "$original_pwd" 2>/dev/null || true
            fi
        fi

        print_info ""
        if [[ "$dry_run" == "true" ]]; then
            print_info "[DRY RUN] To work in this worktree you would run:"
            print_info "  cd \"$worktree_path\""
            print_info "  # Launch Claude Code from this directory"
        else
            print_info "To work in this worktree:"
            print_info "  cd \"$worktree_path\""
            print_info "  # Launch Claude Code from this directory"
        fi
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