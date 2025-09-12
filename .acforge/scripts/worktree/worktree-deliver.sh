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

# Get repository info.
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

# Validate identifier to prevent path traversal attacks.
validate_identifier() {
    local identifier="$1"
    
    # Check for path traversal attempts
    if [[ "$identifier" == *".."* ]] || [[ "$identifier" =~ ^/ ]] || [[ "$identifier" =~ /$ ]]; then
        print_error "Invalid identifier: contains unsafe characters"
        return 1
    fi
    
    # Check for excessive length
    if [[ ${#identifier} -gt 100 ]]; then
        print_error "Identifier too long (max 100 characters)"
        return 1
    fi
    
    return 0
}

# Extract issue number from identifier.
extract_issue_number() {
    local identifier="$1"
    
    # Validate input first
    validate_identifier "$identifier" || return 1
    
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

# Fetch issue details from GitHub using gh CLI.
fetch_issue_details() {
    local issue_num="$1"
    local repo_full_name="$2"
    local dry_run="${3:-false}"
    
    if [[ "$dry_run" == "true" ]]; then
        print_info "[DRY RUN] Would fetch issue #$issue_num details from GitHub using gh CLI"
        echo "title:Sample Issue Title|body:This is a sample issue description for testing.|state:open|labels:bug,enhancement"
        return 0
    fi
    
    # GitHub CLI is required for this script
    if ! command -v gh >/dev/null 2>&1; then
        print_error "GitHub CLI (gh) is required but not installed"
        print_info "Install it with: https://cli.github.com/"
        return 1
    fi
    
    # Verify gh is authenticated
    if ! gh auth status >/dev/null 2>&1; then
        print_error "GitHub CLI is not authenticated"
        print_info "Run 'gh auth login' to authenticate"
        return 1
    fi
    
    print_info "Fetching issue #$issue_num details from GitHub..."
    
    # Fetch issue details
    local issue_data
    if issue_data=$(gh issue view "$issue_num" --repo "$repo_full_name" --json title,body,state,labels --jq 'if .title then "title:\(.title)|body:\(.body // "")|state:\(.state)|labels:\([.labels[].name] | join(","))" else empty end' 2>/dev/null); then
        print_success "Issue #$issue_num details retrieved successfully"
        echo "$issue_data"
        return 0
    else
        print_error "Could not fetch issue #$issue_num details"
        print_info "Please verify:"
        print_info "  - Issue number $issue_num exists"
        print_info "  - You have access to repository $repo_full_name"
        print_info "  - GitHub CLI authentication is working"
        return 1
    fi
}

# Load and process template for Claude Code prompt.
create_issue_prompt() {
    local identifier="$1"
    local issue_details="$2"
    local is_issue_mode="$3"
    local worktree_path="$4"
    
    # Load template file
    local template_file="$MAIN_REPO/templates/prompts/worktree-deliver.template.md"
    if [[ ! -f "$template_file" ]]; then
        print_error "Template file not found: $template_file"
        return 1
    fi
    
    # Parse issue details
    local title body state labels
    if [[ -n "$issue_details" ]]; then
        IFS='|' read -r title body state labels <<< "$issue_details"
        title="${title#title:}"
        body="${body#body:}"
        state="${state#state:}"
        labels="${labels#labels:}"
    fi
    
    # Include repository configuration context
    local claude_config="Not configured"
    local claude_md="Not available"
    
    # Try to read CLAUDE.md for project context
    if [[ -f "$MAIN_REPO/CLAUDE.md" ]]; then
        claude_md="Available: Repository-specific operational rules and file structure guidelines are configured in CLAUDE.md."
    fi
    
    # Try to read .claude/settings.json for configuration
    if [[ -f "$MAIN_REPO/.claude/settings.json" ]]; then
        claude_config="Available: Claude Code is configured with repository-specific settings (model, permissions, cleanup policies)."
    fi
    
    # Create issue context section
    local issue_context=""
    if [[ "$is_issue_mode" == "true" && -n "$title" ]]; then
        issue_context="**GitHub Issue**: #$identifier  
**Title**: $title  
**State**: $state  
**Labels**: ${labels:-none}  

**Issue Description**:
$body"
    else
        issue_context="**Branch/Identifier**: $identifier  
**Development Focus**: Feature/improvement work for this branch"
    fi
    
    # Load template and substitute variables
    local template_content
    template_content=$(cat "$template_file")
    
    # Perform substitutions
    template_content="${template_content//\{\{WORKTREE_PATH\}\}/$worktree_path}"
    template_content="${template_content//\{\{CLAUDE_CONFIG\}\}/$claude_config}"
    template_content="${template_content//\{\{CLAUDE_MD\}\}/$claude_md}"
    template_content="${template_content//\{\{ISSUE_CONTEXT\}\}/$issue_context}"
    
    echo "$template_content"
}

# Create worktree - fail if already exists.
setup_worktree() {
    local identifier="$1"
    local dry_run="${2:-false}"
    
    # Check if worktree already exists first
    local repo_info
    repo_info=$(get_repo_info) || return 1
    local repo_name="${repo_info%|*}"
    
    local base_dir="$WORKTREE_BASE/$repo_name"
    local clean_id="${identifier#\#}"
    
    # Check various possible worktree directories
    local possible_paths=(
        "$base_dir/$clean_id"
    )
    
    if [[ "$clean_id" =~ ^[0-9]+$ ]]; then
        possible_paths+=("$base_dir/issue-$clean_id")
    fi
    
    for path in "${possible_paths[@]}"; do
        if [[ -d "$path" ]]; then
            print_error "Worktree already exists for $identifier at: $path"
            print_info "Use 'worktree.sh remove $identifier' to remove it first, or work in the existing worktree"
            return 1
        fi
    done
    
    local create_script="$SCRIPT_DIR/worktree-create.sh"
    if [[ ! -f "$create_script" ]]; then
        print_error "worktree-create.sh not found at $create_script"
        return 1
    fi
    
    print_info "Creating new worktree for: $identifier"
    
    if [[ "$dry_run" == "true" ]]; then
        print_info "[DRY RUN] Would execute: $create_script \"$identifier\" --dry-run"
        return 0
    fi
    
    # Execute worktree creation
    if "$create_script" "$identifier"; then
        print_success "New worktree created successfully"
        return 0
    else
        print_error "Failed to create worktree for $identifier"
        return 1
    fi
}

# Find worktree directory path.
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

# Launch Claude Code with custom prompt.
launch_claude_with_prompt() {
    local worktree_path="$1"
    local custom_prompt="$2"
    local dry_run="${3:-false}"
    local identifier="${4:-}"
    
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
    
    # Determine prompt file location based on workflow type
    local prompt_file=""
    local prompt_dir=""
    
    # Check if this is an issue-based workflow
    local issue_num
    if issue_num=$(extract_issue_number "${identifier:-}"); then
        # Create prompt in analysis/issue-XYZ directory to avoid merge conflicts
        # Pad issue number to 3 digits for consistent alphabetical sorting
        local padded_issue_num
        padded_issue_num=$(printf "%03d" "$issue_num")
        prompt_dir="$MAIN_REPO/analysis/issue-$padded_issue_num"
        prompt_file="$prompt_dir/worktree-delivery-prompt-$(date +%Y%m%d-%H%M%S).md"
        print_info "Using analysis directory for issue #$issue_num: $prompt_dir"
    else
        # Fall back to .acforge directory for branch-based workflows
        prompt_dir="$worktree_path/.acforge"
        prompt_file="$prompt_dir/worktree-delivery-prompt-$(date +%Y%m%d-%H%M%S).md"
        print_info "Using .acforge directory for branch-based workflow"
    fi
    
    # Ensure prompt directory exists
    if [[ ! -d "$prompt_dir" ]]; then
        mkdir -p "$prompt_dir" || {
            print_error "Failed to create prompt directory: $prompt_dir"
            return 1
        }
    fi
    
    if [[ "$dry_run" == "true" ]]; then
        print_info "[DRY RUN] Would change directory to: $worktree_path"
        print_info "[DRY RUN] Would create prompt file: $prompt_file"
        print_info "[DRY RUN] Would launch Claude Code with command: $claude_command \"<prompt-content>\""
        print_info "[DRY RUN] Full custom prompt content:"
        print_info "=============================================="
        echo "$custom_prompt"
        print_info "=============================================="
        return 0
    fi
    
    # Write prompt to file with error handling and secure permissions
    if ! (umask 077; echo "$custom_prompt" > "$prompt_file"); then
        print_error "Failed to create prompt file: $prompt_file"
        return 1
    fi
    
    # Trap to ensure cleanup on exit/interruption
    # Variables are expanded immediately when trap is set
    trap "cleanup_prompt_file '$prompt_file' '$original_dir'" EXIT INT TERM
    
    print_success "Worktree ready: $worktree_path"
    print_success "Delivery prompt prepared: $prompt_file"
    print_info ""
    print_info "=============================================="
    print_info "LAUNCHING CLAUDE CODE WITH CUSTOM PROMPT"
    print_info "=============================================="
    print_info ""
    
    # Change to worktree directory
    cd "$worktree_path"
    
    # Update terminal title with issue context
    if [[ -f "$SCRIPT_DIR/worktree-title.sh" ]]; then
        source "$SCRIPT_DIR/worktree-title.sh"
        update_title_from_context "$(basename "$worktree_path")"
    fi
    
    print_info "Starting Claude Code with issue-focused prompt..."
    
    # Launch Claude Code with the prompt as command line argument
    # Claude Code accepts the prompt directly as an argument
    "$claude_command" "$(cat "$prompt_file")" || {
        local exit_code=$?
        print_error "Claude Code exited with code: $exit_code"
        cd "$original_dir"
        return $exit_code
    }
    
    cd "$original_dir"
    print_success "Claude Code session completed"
    
    # Cleanup is handled by trap
}

# Cleanup function for prompt file and directory restoration.
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

# Main function.
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
    
    # Validate identifier for security
    if ! validate_identifier "$identifier"; then
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
        custom_prompt=$(create_issue_prompt "$identifier" "$issue_details" "$is_issue_mode" "$worktree_path")
    else
        print_info "Branch-based workflow: $identifier"
        local custom_prompt
        custom_prompt=$(create_issue_prompt "$identifier" "" "false" "$worktree_path")
    fi
    
    # Launch Claude Code with custom prompt
    launch_claude_with_prompt "$worktree_path" "$custom_prompt" "$dry_run" "$identifier"
}

# Execute main function.
main "$@"