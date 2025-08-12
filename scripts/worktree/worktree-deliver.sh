#!/bin/bash
set -euo pipefail

# Git Worktree Delivery Utility
# Creates worktree, launches Claude Code with issue context for refinement and implementation
# Usage: ./worktree-deliver.sh <issue-number|branch-name> [--dry-run]

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
Git Worktree Delivery Utility

DESCRIPTION:
    Creates or uses existing worktree for issue/branch, then launches Claude Code
    with custom prompt for issue refinement, implementation planning, and execution.

USAGE:
    $0 <issue-number|branch-name> [--dry-run]

ARGUMENTS:
    issue-number    GitHub issue number (e.g., 123, #123)
    branch-name     Full branch name (e.g., feature/add-launch, issue-129-fix)
    --dry-run       Show what would be executed without running commands

WORKFLOW:
    1. Create or locate worktree for the issue/branch
    2. Fetch issue details from GitHub (if issue number provided)
    3. Launch Claude Code in worktree with custom issue-focused prompt
    4. Claude Code stays in interactive mode for user guidance

EXAMPLES:
    $0 123                          # Create worktree for issue #123, launch with issue context
    $0 \#129                         # Create worktree for issue #129 with context
    $0 feature/add-launch          # Use specific branch worktree
    $0 123 --dry-run               # Show what would happen without execution

NOTES:
    - Automatically creates worktree if it doesn't exist
    - Fetches issue details from GitHub for context (requires gh CLI)
    - Launches Claude Code in interactive mode within the worktree
    - User controls next steps through Claude Code interaction

EOF
}

# Get repository info
get_repo_info() {
    local repo_name=""
    local repo_full_name=""
    
    # Try GitHub CLI first
    if command -v gh >/dev/null 2>&1; then
        repo_name=$(gh repo view --json name --jq .name 2>/dev/null || echo "")
        repo_full_name=$(gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null || echo "")
    fi
    
    # Fallback to git remote parsing if needed
    if [[ -z "$repo_name" ]]; then
        local remote_url
        remote_url=$(git -C "$MAIN_REPO" remote get-url origin 2>/dev/null || echo "")
        if [[ -n "$remote_url" ]]; then
            if [[ "$remote_url" =~ github\.com[:/]([^/]+/[^/]+)(\.git)?$ ]]; then
                repo_full_name="${BASH_REMATCH[1]%.git}"
                repo_name=$(basename "$repo_full_name")
            fi
        fi
    fi
    
    if [[ -z "$repo_name" ]]; then
        print_error "Unable to determine repository name"
        return 1
    fi
    
    echo "$repo_name|$repo_full_name"
}

# Extract issue number from identifier
extract_issue_number() {
    local identifier="$1"
    
    # Remove # prefix if present
    local clean_id="${identifier#\#}"
    
    # Check if it's a pure number (issue number)
    if [[ "$clean_id" =~ ^[0-9]+$ ]]; then
        echo "$clean_id"
        return 0
    fi
    
    # Try to extract from branch name patterns
    if [[ "$clean_id" =~ issue-([0-9]+)- ]] || [[ "$clean_id" =~ issue/([0-9]+)- ]] || [[ "$clean_id" =~ issue-([0-9]+)$ ]]; then
        echo "${BASH_REMATCH[1]}"
        return 0
    fi
    
    return 1
}

# Fetch issue details from GitHub
fetch_issue_details() {
    local issue_num="$1"
    local repo_full_name="$2"
    local dry_run="${3:-false}"
    
    if [[ "$dry_run" == "true" ]]; then
        print_info "[DRY RUN] Would fetch issue #$issue_num details from GitHub"
        echo "title:Sample Issue Title|body:This is a sample issue description for testing.|state:open|labels:bug,enhancement"
        return 0
    fi
    
    # Check if GitHub CLI is available
    if ! command -v gh >/dev/null 2>&1; then
        print_warning "GitHub CLI not available - issue context will be limited"
        echo "title:Issue #$issue_num|body:GitHub CLI not available for detailed context.|state:unknown|labels:"
        return 0
    fi
    
    # Fetch issue details
    local issue_data
    if issue_data=$(gh issue view "$issue_num" --repo "$repo_full_name" --json title,body,state,labels --jq 'if .title then "title:\(.title)|body:\(.body // "")|state:\(.state)|labels:\([.labels[].name] | join(","))" else empty end' 2>/dev/null); then
        echo "$issue_data"
        return 0
    else
        print_warning "Could not fetch issue #$issue_num details (may not exist or access denied)"
        echo "title:Issue #$issue_num|body:Unable to fetch issue details from GitHub.|state:unknown|labels:"
        return 0
    fi
}

# Create custom prompt for Claude Code
create_issue_prompt() {
    local identifier="$1"
    local issue_details="$2"
    local is_issue_mode="$3"
    
    # Parse issue details
    local title body state labels
    if [[ -n "$issue_details" ]]; then
        IFS='|' read -r title body state labels <<< "$issue_details"
        title="${title#title:}"
        body="${body#body:}"
        state="${state#state:}"
        labels="${labels#labels:}"
    fi
    
    cat << EOF
# Issue Delivery Workflow

You are working in a dedicated git worktree for development work. Your task is to help refine and implement the following:

EOF

    if [[ "$is_issue_mode" == "true" && -n "$title" ]]; then
        cat << EOF
## GitHub Issue Context
**Issue**: $identifier
**Title**: $title
**State**: $state
**Labels**: ${labels:-none}

**Description**:
$body

EOF
    else
        cat << EOF
## Branch Context
**Branch/Identifier**: $identifier
**Development Focus**: Work on features and improvements for this branch

EOF
    fi

    cat << EOF
## Workflow Instructions

**Phase 1: Issue Analysis & Refinement**
1. Analyze the issue/requirements thoroughly
2. Ask clarifying questions if anything is unclear
3. Suggest improvements or refinements to the requirements
4. Confirm scope and acceptance criteria

**Phase 2: Implementation Planning**
1. Create detailed implementation plan
2. Identify files that need changes
3. Consider testing strategy
4. Plan documentation updates

**Phase 3: Interactive Implementation**
1. Implement the solution step by step
2. Write tests as needed (TDD approach when appropriate)
3. Update documentation
4. Prepare for code review

## Your Role
- Stay in **interactive mode** - wait for user input between phases
- Ask for confirmation before proceeding to implementation
- Suggest next steps and wait for user guidance
- Focus on high-quality, well-tested solutions

## Current Working Directory
You are now working in the dedicated worktree for this issue. All file operations will be isolated from the main repository until ready to merge.

**Ready to begin?** Let's start with analyzing the requirements and refining the scope.
EOF
}

# Create or use existing worktree
setup_worktree() {
    local identifier="$1"
    local dry_run="${2:-false}"
    
    local create_script="$SCRIPT_DIR/worktree-create.sh"
    if [[ ! -f "$create_script" ]]; then
        print_error "worktree-create.sh not found at $create_script"
        return 1
    fi
    
    print_info "Setting up worktree for: $identifier"
    
    if [[ "$dry_run" == "true" ]]; then
        print_info "[DRY RUN] Would execute: $create_script \"$identifier\" --dry-run"
        return 0
    fi
    
    # Execute worktree creation (it handles existing worktrees gracefully)
    if "$create_script" "$identifier"; then
        return 0
    else
        print_error "Failed to setup worktree for $identifier"
        return 1
    fi
}

# Find worktree directory path
find_worktree_path() {
    local identifier="$1"
    
    local repo_info
    repo_info=$(get_repo_info) || return 1
    local repo_name="${repo_info%|*}"
    
    local base_dir="$WORKTREE_BASE/$repo_name"
    
    if [[ ! -d "$base_dir" ]]; then
        print_error "Worktree base directory not found: $base_dir"
        return 1
    fi
    
    # Clean up identifier
    local clean_id="${identifier#\#}"
    
    # Try exact match first
    local target_dir="$base_dir/$clean_id"
    if [[ -d "$target_dir" ]]; then
        echo "$target_dir"
        return 0
    fi
    
    # Try issue-based directory pattern
    if [[ "$clean_id" =~ ^[0-9]+$ ]]; then
        local issue_dir="$base_dir/issue-$clean_id"
        if [[ -d "$issue_dir" ]]; then
            echo "$issue_dir"
            return 0
        fi
    fi
    
    # Search for directories containing the identifier
    local matches=()
    while IFS= read -r -d '' dir; do
        local dirname=$(basename "$dir")
        if [[ "$dirname" == *"$clean_id"* ]]; then
            matches+=("$dir")
        fi
    done < <(find "$base_dir" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)
    
    if [[ ${#matches[@]} -eq 0 ]]; then
        print_error "No worktree directory found for: $identifier"
        return 1
    elif [[ ${#matches[@]} -eq 1 ]]; then
        echo "${matches[0]}"
        return 0
    else
        print_warning "Multiple matches found, using first: $(basename "${matches[0]}")"
        echo "${matches[0]}"
        return 0
    fi
}

# Launch Claude Code with custom prompt
launch_claude_with_prompt() {
    local worktree_path="$1"
    local custom_prompt="$2"
    local dry_run="${3:-false}"
    
    # Store original directory for cleanup
    local original_dir="$(pwd)"
    
    # Check Claude Code availability
    local claude_command=""
    if command -v claude >/dev/null 2>&1; then
        claude_command="claude"
    else
        local launch_script="$SCRIPT_DIR/../launch-claude.sh"
        if [[ -f "$launch_script" ]]; then
            claude_command="$launch_script"
        else
            print_error "Claude Code not found. Please install Claude Code or ensure launch-claude.sh exists"
            return 1
        fi
    fi
    
    # Create temporary prompt file
    local prompt_file="$worktree_path/.claude-delivery-prompt.md"
    
    if [[ "$dry_run" == "true" ]]; then
        print_info "[DRY RUN] Would change directory to: $worktree_path"
        print_info "[DRY RUN] Would create prompt file: $prompt_file"
        print_info "[DRY RUN] Would display prompt and launch instructions"
        print_info "[DRY RUN] Custom prompt preview (first 200 chars):"
        echo "$custom_prompt" | head -c 200
        echo "..."
        return 0
    fi
    
    # Write prompt to file with error handling
    if ! echo "$custom_prompt" > "$prompt_file"; then
        print_error "Failed to create prompt file: $prompt_file"
        return 1
    fi
    
    # Trap to ensure cleanup on exit/interruption
    trap 'cleanup_prompt_file "$prompt_file" "$original_dir"' EXIT INT TERM
    
    print_success "Worktree ready: $worktree_path"
    print_success "Issue context prepared: $prompt_file"
    print_info ""
    print_info "=============================================="
    print_info "READY TO LAUNCH CLAUDE CODE"
    print_info "=============================================="
    print_info ""
    print_info "Next steps:"
    print_info "1. Change to the worktree directory:"
    print_info "   cd '$worktree_path'"
    print_info ""
    print_info "2. Launch Claude Code:"
    print_info "   $claude_command"
    print_info ""
    print_info "3. Copy and paste the following prompt:"
    print_info ""
    print_info "=============================================="
    cat "$prompt_file"
    print_info "=============================================="
    print_info ""
    print_warning "Claude Code will be in INTERACTIVE mode - provide guidance for next steps"
    print_info ""
    
    # Offer to launch automatically or let user control
    print_info "Launch Claude Code now? [y/N] (or press Ctrl+C to exit)"
    read -r -n 1 response
    echo
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_info "Launching Claude Code in worktree directory..."
        cd "$worktree_path"
        
        # Launch Claude Code normally (not with exec - allows proper return)
        "$claude_command" || {
            local exit_code=$?
            print_error "Claude Code exited with code: $exit_code"
            cd "$original_dir"
            return $exit_code
        }
        
        cd "$original_dir"
        print_success "Claude Code session completed"
    else
        print_info "Setup completed. You can launch Claude Code manually using the instructions above."
    fi
    
    # Cleanup is handled by trap
}

# Cleanup function for prompt file and directory restoration
cleanup_prompt_file() {
    local prompt_file="$1"
    local original_dir="$2"
    
    if [[ -f "$prompt_file" ]]; then
        rm -f "$prompt_file" 2>/dev/null || true
    fi
    
    if [[ -n "$original_dir" && -d "$original_dir" ]]; then
        cd "$original_dir" 2>/dev/null || true
    fi
}

# Main function
main() {
    local identifier=""
    local dry_run=false
    
    # Parse arguments
    if [[ $# -eq 0 ]]; then
        print_error "Missing required argument"
        show_usage
        exit 1
    fi
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --help|-h|help)
                show_usage
                exit 0
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                if [[ -z "$identifier" ]]; then
                    identifier="$1"
                else
                    print_error "Too many arguments: $1"
                    show_usage
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    if [[ -z "$identifier" ]]; then
        print_error "Missing issue number or branch name"
        show_usage
        exit 1
    fi
    
    print_info "Git Worktree Delivery Utility"
    print_info "============================="
    print_info "Target: $identifier"
    
    # Get repository info
    local repo_info
    repo_info=$(get_repo_info) || exit 1
    local repo_name="${repo_info%|*}"
    local repo_full_name="${repo_info#*|}"
    
    print_info "Repository: $repo_name"
    
    # Setup worktree
    setup_worktree "$identifier" "$dry_run" || exit 1
    
    # Find worktree path
    local worktree_path
    if [[ "$dry_run" == "true" ]]; then
        worktree_path="/workspace/worktrees/$repo_name/demo-worktree"
        print_info "[DRY RUN] Simulated worktree path: $worktree_path"
    else
        worktree_path=$(find_worktree_path "$identifier") || exit 1
        print_success "Found worktree: $worktree_path"
    fi
    
    # Check if this is an issue-based workflow
    local issue_num
    local is_issue_mode=false
    if issue_num=$(extract_issue_number "$identifier"); then
        is_issue_mode=true
        print_info "Issue-based workflow detected: #$issue_num"
        
        # Fetch issue details
        local issue_details
        issue_details=$(fetch_issue_details "$issue_num" "$repo_full_name" "$dry_run")
        
        # Create custom prompt with issue context
        local custom_prompt
        custom_prompt=$(create_issue_prompt "$identifier" "$issue_details" "$is_issue_mode")
    else
        print_info "Branch-based workflow: $identifier"
        local custom_prompt
        custom_prompt=$(create_issue_prompt "$identifier" "" "false")
    fi
    
    # Launch Claude Code with custom prompt
    launch_claude_with_prompt "$worktree_path" "$custom_prompt" "$dry_run"
}

# Execute main function
main "$@"