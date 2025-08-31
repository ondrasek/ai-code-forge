#!/bin/bash
set -euo pipefail

# Git Worktree Inspect Utility
# Provides comprehensive analysis of worktree state for issue workflow management
# Usage: ./worktree-inspect.sh <ISSUE_SPEC> [--json] [--verbose]

WORKTREE_BASE="/workspace/worktrees"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_REPO="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print colored output
print_error() { echo -e "${RED}ERROR:${NC} $1" >&2; }
print_success() { echo -e "${GREEN}SUCCESS:${NC} $1"; }
print_warning() { echo -e "${YELLOW}WARNING:${NC} $1"; }
print_info() { echo -e "${BLUE}INFO:${NC} $1"; }
print_debug() { echo -e "${CYAN}DEBUG:${NC} $1"; }

# Global variables for state tracking
declare -A WORKTREE_STATE
declare -A ISSUE_STATE
declare -A GIT_STATE
declare -A ASSISTANT_STATE

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

# Parse issue specification into canonical components
parse_issue_spec() {
    local spec="$1"
    
    # Strip leading # if present
    spec="${spec#\#}"
    
    # Check if it's a pure number (GitHub issue number)
    if [[ "$spec" =~ ^[0-9]+$ ]] && [[ $spec -ge 1 ]] && [[ $spec -le 99999 ]]; then
        ISSUE_STATE["number"]="$spec"
        ISSUE_STATE["spec_type"]="number"
        return 0
    fi
    
    # Check if it looks like a branch name
    if [[ "$spec" =~ ^[a-zA-Z0-9/_-]+$ ]] && [[ ${#spec} -le 100 ]]; then
        ISSUE_STATE["branch_name"]="$spec"
        ISSUE_STATE["spec_type"]="branch"
        return 0
    fi
    
    # Assume it's an issue title for fuzzy matching
    ISSUE_STATE["title_search"]="$spec"
    ISSUE_STATE["spec_type"]="title"
    return 0
}

# Find issue number from branch name patterns
find_issue_from_branch() {
    local branch="$1"
    
    # Common branch naming patterns - order matters, most specific first
    local patterns=(
        "claude/issue-([0-9]+)-.*"        # claude/issue-123-feature
        "claude/issue-([0-9]+)$"          # claude/issue-123
        "feature/issue-([0-9]+)-.*"       # feature/issue-123-name
        "feature/issue-([0-9]+)$"         # feature/issue-123
        "issue/([0-9]+)-.*"               # issue/123-feature
        "issue/([0-9]+)$"                 # issue/123
        "issue-([0-9]+)-.*"               # issue-123-feature
        "issue-([0-9]+)$"                 # issue-123
        "([0-9]+)-.*"                     # 123-feature (simple number prefix)
        "([0-9]+)$"                       # 123 (simple number)
    )
    
    for pattern in "${patterns[@]}"; do
        if [[ "$branch" =~ ^${pattern}$ ]]; then
            echo "${BASH_REMATCH[1]}"
            return 0
        fi
    done
    
    return 1
}

# Find existing branches for an issue number
find_issue_branches() {
    local issue_num="$1"
    local found_branches=()
    
    # Common branch naming patterns for issues - order matters, most specific first
    local patterns=(
        "claude/issue-$issue_num-*"      # claude/issue-123-feature
        "claude/issue-$issue_num"        # claude/issue-123
        "feature/issue-$issue_num-*"     # feature/issue-123-name
        "feature/issue-$issue_num"       # feature/issue-123
        "issue/$issue_num-*"             # issue/123-feature
        "issue/$issue_num"               # issue/123
        "issue-$issue_num-*"             # issue-123-feature
        "issue-$issue_num"               # issue-123
        "$issue_num-*"                   # 123-feature
        "$issue_num"                     # 123
    )
    
    # Check local branches
    for pattern in "${patterns[@]}"; do
        local matches
        mapfile -t matches < <(git branch --list "$pattern" 2>/dev/null | sed 's/^[*+ ] *//')
        for match in "${matches[@]}"; do
            [[ -n "$match" ]] && found_branches+=("$match")
        done
    done
    
    # Check remote branches
    for pattern in "${patterns[@]}"; do
        local matches
        mapfile -t matches < <(git branch -r --list "origin/$pattern" 2>/dev/null | sed 's/^[* ] *origin\///')
        for match in "${matches[@]}"; do
            [[ -n "$match" ]] && found_branches+=("$match")
        done
    done
    
    # Remove duplicates and print
    printf "%s\n" "${found_branches[@]}" | sort -u
}

# Search for issues by title using GitHub CLI
search_issues_by_title() {
    local search_term="$1"
    
    if ! command -v gh >/dev/null 2>&1; then
        return 1
    fi
    
    local repo_full_name
    if ! repo_full_name=$(get_repo_full_name); then
        return 1
    fi
    
    # Search for issues with title matching
    gh issue list --repo "$repo_full_name" --search "$search_term in:title" --json number,title,state --limit 5 2>/dev/null || return 1
}

# Resolve issue specification to canonical form
resolve_issue_spec() {
    local spec="$1"
    
    parse_issue_spec "$spec"
    
    case "${ISSUE_STATE[spec_type]}" in
        "number")
            # Already have issue number, validate it exists
            validate_github_issue "${ISSUE_STATE[number]}"
            ;;
        "branch")
            # Try to extract issue number from branch name
            local issue_num
            if issue_num=$(find_issue_from_branch "${ISSUE_STATE[branch_name]}"); then
                ISSUE_STATE["number"]="$issue_num"
                validate_github_issue "$issue_num" || true  # Don't fail if we can't validate
            fi
            ;;
        "title")
            # Search for matching issues
            local search_results
            if search_results=$(search_issues_by_title "${ISSUE_STATE[title_search]}"); then
                local issue_count
                issue_count=$(echo "$search_results" | jq length)
                if [[ $issue_count -eq 1 ]]; then
                    ISSUE_STATE["number"]=$(echo "$search_results" | jq -r '.[0].number')
                    ISSUE_STATE["title"]=$(echo "$search_results" | jq -r '.[0].title')
                    ISSUE_STATE["state"]=$(echo "$search_results" | jq -r '.[0].state')
                elif [[ $issue_count -gt 1 ]]; then
                    print_warning "Multiple issues found matching '$spec'. Using first match."
                    ISSUE_STATE["number"]=$(echo "$search_results" | jq -r '.[0].number')
                    ISSUE_STATE["title"]=$(echo "$search_results" | jq -r '.[0].title')
                    ISSUE_STATE["state"]=$(echo "$search_results" | jq -r '.[0].state')
                else
                    print_error "No issues found matching title: $spec"
                    return 1
                fi
            else
                print_warning "Unable to search issues by title (GitHub CLI may not be available)"
                return 1
            fi
            ;;
    esac
    
    return 0
}

# Validate GitHub issue exists and get metadata
validate_github_issue() {
    local issue_num="$1"
    
    if ! command -v gh >/dev/null 2>&1; then
        ISSUE_STATE["github_available"]="false"
        return 1
    fi
    
    local repo_full_name
    if ! repo_full_name=$(get_repo_full_name); then
        ISSUE_STATE["github_available"]="false"
        return 1
    fi
    
    local issue_info
    if issue_info=$(gh issue view "$issue_num" --repo "$repo_full_name" --json number,title,state,assignees,labels,url 2>/dev/null); then
        ISSUE_STATE["github_available"]="true"
        ISSUE_STATE["exists"]="true"
        ISSUE_STATE["number"]="$issue_num"
        ISSUE_STATE["title"]=$(echo "$issue_info" | jq -r .title)
        ISSUE_STATE["state"]=$(echo "$issue_info" | jq -r .state)
        ISSUE_STATE["url"]=$(echo "$issue_info" | jq -r .url)
        
        # Get assignees
        local assignees
        assignees=$(echo "$issue_info" | jq -r '.assignees[]?.login' | tr '\n' ',' | sed 's/,$//')
        ISSUE_STATE["assignees"]="$assignees"
        
        # Get labels
        local labels
        labels=$(echo "$issue_info" | jq -r '.labels[]?.name' | tr '\n' ',' | sed 's/,$//')
        ISSUE_STATE["labels"]="$labels"
        
        return 0
    else
        ISSUE_STATE["github_available"]="true"
        ISSUE_STATE["exists"]="false"
        return 1
    fi
}

# Find worktree path for issue or branch
find_worktree_path() {
    local issue_num="${ISSUE_STATE[number]:-}"
    local branch_name="${ISSUE_STATE[branch_name]:-}"
    
    # If we have an issue number, look for branches
    if [[ -n "$issue_num" ]]; then
        local branches
        mapfile -t branches < <(find_issue_branches "$issue_num")
        for branch in "${branches[@]}"; do
            local worktree_path
            worktree_path=$(git worktree list --porcelain | awk -v branch="$branch" '
                /^worktree / { path = substr($0, 10) }
                /^branch refs\/heads\// && substr($0, 19) == branch { print path; exit }
            ')
            if [[ -n "$worktree_path" ]]; then
                WORKTREE_STATE["path"]="$worktree_path"
                WORKTREE_STATE["branch"]="$branch"
                return 0
            fi
        done
    fi
    
    # If we have a specific branch name, look for it
    if [[ -n "$branch_name" ]]; then
        local worktree_path
        worktree_path=$(git worktree list --porcelain | awk -v branch="$branch_name" '
            /^worktree / { path = substr($0, 10) }
            /^branch refs\/heads\// && substr($0, 19) == branch { print path; exit }
        ')
        if [[ -n "$worktree_path" ]]; then
            WORKTREE_STATE["path"]="$worktree_path"
            WORKTREE_STATE["branch"]="$branch_name"
            return 0
        fi
    fi
    
    return 1
}

# Analyze worktree directory state
analyze_worktree_directory() {
    local worktree_path="${WORKTREE_STATE[path]:-}"
    
    if [[ -z "$worktree_path" ]]; then
        WORKTREE_STATE["exists"]="false"
        return 1
    fi
    
    if [[ -d "$worktree_path" ]]; then
        WORKTREE_STATE["exists"]="true"
        
        # Check if it's a valid git repository
        # In worktrees, .git is usually a file pointing to the actual git directory
        # Use git rev-parse as the definitive test for a valid git repository
        if (cd "$worktree_path" && git rev-parse --git-dir >/dev/null 2>&1); then
            WORKTREE_STATE["git_valid"]="true"
        else
            WORKTREE_STATE["git_valid"]="false"
        fi
        
        # Get directory modification time
        local mod_time
        mod_time=$(stat -c "%Y" "$worktree_path" 2>/dev/null || echo "0")
        WORKTREE_STATE["last_modified"]="$mod_time"
        
        # Check size (human readable)
        local size
        size=$(du -sh "$worktree_path" 2>/dev/null | cut -f1 || echo "unknown")
        WORKTREE_STATE["size"]="$size"
        
        return 0
    else
        WORKTREE_STATE["exists"]="false"
        return 1
    fi
}

# Analyze AI assistant state
analyze_assistant_state() {
    local worktree_path="${WORKTREE_STATE[path]:-}"
    
    if [[ -z "$worktree_path" ]] || [[ "${WORKTREE_STATE[exists]}" != "true" ]]; then
        ASSISTANT_STATE["available"]="false"
        return 1
    fi
    
    local acforge_run_dir="$worktree_path/.acforge-run"
    
    if [[ -d "$acforge_run_dir" ]]; then
        ASSISTANT_STATE["directory_exists"]="true"
        
        # Check for active process indicators
        local pid_files
        mapfile -t pid_files < <(find "$acforge_run_dir" -name "*.pid" 2>/dev/null)
        
        local active_count=0
        for pid_file in "${pid_files[@]}"; do
            if [[ -f "$pid_file" ]]; then
                local pid
                pid=$(cat "$pid_file" 2>/dev/null)
                if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
                    ((active_count++))
                fi
            fi
        done
        
        ASSISTANT_STATE["active_processes"]="$active_count"
        
        # Check for session files
        local session_count
        session_count=$(find "$acforge_run_dir" -name "session-*" -type d 2>/dev/null | wc -l)
        ASSISTANT_STATE["session_count"]="$session_count"
        
        # Get last activity time
        local last_activity
        last_activity=$(find "$acforge_run_dir" -type f -printf "%T@\n" 2>/dev/null | sort -n | tail -1)
        ASSISTANT_STATE["last_activity"]="${last_activity:-0}"
        
        return 0
    else
        ASSISTANT_STATE["directory_exists"]="false"
        ASSISTANT_STATE["active_processes"]="0"
        ASSISTANT_STATE["session_count"]="0"
        return 1
    fi
}

# Analyze git state within worktree
analyze_git_state() {
    local worktree_path="${WORKTREE_STATE[path]:-}"
    local branch="${WORKTREE_STATE[branch]:-}"
    
    if [[ -z "$worktree_path" ]] || [[ "${WORKTREE_STATE[exists]}" != "true" ]] || [[ "${WORKTREE_STATE[git_valid]}" != "true" ]]; then
        GIT_STATE["available"]="false"
        return 1
    fi
    
    # Change to worktree directory for git operations
    local original_dir
    original_dir=$(pwd)
    
    if ! cd "$worktree_path" 2>/dev/null; then
        GIT_STATE["available"]="false"
        return 1
    fi
    
    GIT_STATE["available"]="true"
    
    # Check working directory status
    local status_output
    status_output=$(git status --porcelain 2>/dev/null || echo "")
    if [[ -z "$status_output" ]]; then
        GIT_STATE["working_clean"]="true"
        GIT_STATE["uncommitted_changes"]="0"
    else
        GIT_STATE["working_clean"]="false"
        GIT_STATE["uncommitted_changes"]=$(echo "$status_output" | wc -l)
    fi
    
    # Get current commit
    local current_commit
    current_commit=$(git rev-parse HEAD 2>/dev/null || echo "")
    GIT_STATE["current_commit"]="${current_commit:0:8}"
    
    # Check tracking branch status
    local tracking_branch
    tracking_branch=$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo "")
    
    if [[ -n "$tracking_branch" ]]; then
        GIT_STATE["has_tracking"]="true"
        GIT_STATE["tracking_branch"]="$tracking_branch"
        
        # Check commits ahead/behind
        local ahead_behind
        ahead_behind=$(git rev-list --left-right --count HEAD..."$tracking_branch" 2>/dev/null || echo "0	0")
        GIT_STATE["commits_ahead"]=$(echo "$ahead_behind" | cut -f1)
        GIT_STATE["commits_behind"]=$(echo "$ahead_behind" | cut -f2)
        
        # Determine sync status
        local ahead=${GIT_STATE["commits_ahead"]}
        local behind=${GIT_STATE["commits_behind"]}
        
        if [[ "$ahead" == "0" ]] && [[ "$behind" == "0" ]]; then
            GIT_STATE["sync_status"]="synced"
        elif [[ "$ahead" -gt 0 ]] && [[ "$behind" == "0" ]]; then
            GIT_STATE["sync_status"]="ahead"
        elif [[ "$ahead" == "0" ]] && [[ "$behind" -gt 0 ]]; then
            GIT_STATE["sync_status"]="behind"
        else
            GIT_STATE["sync_status"]="diverged"
        fi
    else
        GIT_STATE["has_tracking"]="false"
        GIT_STATE["sync_status"]="no_tracking"
    fi
    
    # Get last commit info
    local last_commit_info
    last_commit_info=$(git log -1 --format="%h|%s|%an|%ar" 2>/dev/null || echo "")
    if [[ -n "$last_commit_info" ]]; then
        IFS='|' read -r commit_hash commit_msg commit_author commit_date <<< "$last_commit_info"
        GIT_STATE["last_commit_hash"]="$commit_hash"
        GIT_STATE["last_commit_message"]="$commit_msg"
        GIT_STATE["last_commit_author"]="$commit_author"
        GIT_STATE["last_commit_date"]="$commit_date"
    fi
    
    # Check for stash entries
    local stash_count
    stash_count=$(git stash list 2>/dev/null | wc -l)
    GIT_STATE["stash_count"]="$stash_count"
    
    # Return to original directory
    cd "$original_dir"
    
    return 0
}

# Generate human-readable status summary
generate_summary_output() {
    local verbose="${1:-false}"
    
    # Header
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}                                    WORKTREE INSPECTION REPORT${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════════════════════${NC}"
    echo
    
    # Issue Information
    echo -e "${CYAN}🎯 ISSUE INFORMATION${NC}"
    echo -e "   ${BLUE}Specification:${NC} ${ISSUE_STATE[original_spec]:-"N/A"}"
    
    if [[ "${ISSUE_STATE[github_available]:-false}" == "true" ]]; then
        if [[ "${ISSUE_STATE[exists]:-false}" == "true" ]]; then
            echo -e "   ${BLUE}Issue #${ISSUE_STATE[number]}:${NC} ${ISSUE_STATE[title]:-"N/A"}"
            echo -e "   ${BLUE}Status:${NC} ${ISSUE_STATE[state]:-"unknown"}"
            echo -e "   ${BLUE}URL:${NC} ${ISSUE_STATE[url]:-"N/A"}"
            
            if [[ -n "${ISSUE_STATE[assignees]:-}" ]]; then
                echo -e "   ${BLUE}Assignees:${NC} ${ISSUE_STATE[assignees]}"
            fi
            
            if [[ -n "${ISSUE_STATE[labels]:-}" ]]; then
                echo -e "   ${BLUE}Labels:${NC} ${ISSUE_STATE[labels]}"
            fi
        else
            echo -e "   ${RED}❌ Issue #${ISSUE_STATE[number]:-"unknown"} not found on GitHub${NC}"
        fi
    else
        echo -e "   ${YELLOW}⚠️  GitHub CLI not available - cannot validate issue${NC}"
    fi
    echo
    
    # Worktree Information
    echo -e "${CYAN}📁 WORKTREE STATUS${NC}"
    
    if [[ "${WORKTREE_STATE[exists]:-false}" == "true" ]]; then
        echo -e "   ${GREEN}✅ Worktree exists${NC}"
        echo -e "   ${BLUE}Path:${NC} ${WORKTREE_STATE[path]}"
        echo -e "   ${BLUE}Branch:${NC} ${WORKTREE_STATE[branch]:-"unknown"}"
        echo -e "   ${BLUE}Size:${NC} ${WORKTREE_STATE[size]:-"unknown"}"
        
        if [[ "$verbose" == "true" ]]; then
            local mod_timestamp="${WORKTREE_STATE[last_modified]:-0}"
            if [[ "$mod_timestamp" != "0" ]]; then
                local mod_date
                mod_date=$(date -d "@$mod_timestamp" 2>/dev/null || echo "unknown")
                echo -e "   ${BLUE}Modified:${NC} $mod_date"
            fi
        fi
        
        if [[ "${WORKTREE_STATE[git_valid]:-false}" == "true" ]]; then
            echo -e "   ${GREEN}✅ Valid git repository${NC}"
        else
            echo -e "   ${RED}❌ Invalid git repository structure${NC}"
        fi
    else
        echo -e "   ${RED}❌ Worktree does not exist${NC}"
        if [[ -n "${ISSUE_STATE[number]:-}" ]]; then
            echo -e "   ${YELLOW}💡 Suggestion: Run \`./worktree.sh create --from-issue ${ISSUE_STATE[number]}\`${NC}"
        fi
    fi
    echo
    
    # Git State Information (only if worktree exists and is valid)
    if [[ "${GIT_STATE[available]:-false}" == "true" ]]; then
        echo -e "${CYAN}🔀 GIT STATUS${NC}"
        
        # Working directory status
        if [[ "${GIT_STATE[working_clean]:-false}" == "true" ]]; then
            echo -e "   ${GREEN}✅ Working directory clean${NC}"
        else
            echo -e "   ${YELLOW}⚠️  ${GIT_STATE[uncommitted_changes]:-0} uncommitted changes${NC}"
        fi
        
        # Sync status
        case "${GIT_STATE[sync_status]:-unknown}" in
            "synced")
                echo -e "   ${GREEN}✅ Synchronized with remote${NC}"
                ;;
            "ahead")
                echo -e "   ${YELLOW}⬆️  ${GIT_STATE[commits_ahead]:-0} commits ahead of remote${NC}"
                ;;
            "behind")
                echo -e "   ${YELLOW}⬇️  ${GIT_STATE[commits_behind]:-0} commits behind remote${NC}"
                ;;
            "diverged")
                echo -e "   ${RED}🔄 Diverged: ${GIT_STATE[commits_ahead]:-0} ahead, ${GIT_STATE[commits_behind]:-0} behind${NC}"
                ;;
            "no_tracking")
                echo -e "   ${YELLOW}⚠️  No tracking branch configured${NC}"
                ;;
            *)
                echo -e "   ${RED}❓ Unknown sync status${NC}"
                ;;
        esac
        
        # Current commit
        if [[ -n "${GIT_STATE[current_commit]:-}" ]]; then
            echo -e "   ${BLUE}Current commit:${NC} ${GIT_STATE[current_commit]}"
        fi
        
        # Last commit details (verbose mode)
        if [[ "$verbose" == "true" ]] && [[ -n "${GIT_STATE[last_commit_message]:-}" ]]; then
            echo -e "   ${BLUE}Last commit:${NC} ${GIT_STATE[last_commit_message]}"
            echo -e "   ${BLUE}Author:${NC} ${GIT_STATE[last_commit_author]:-"unknown"}"
            echo -e "   ${BLUE}Date:${NC} ${GIT_STATE[last_commit_date]:-"unknown"}"
        fi
        
        # Stash information
        local stash_count="${GIT_STATE[stash_count]:-0}"
        if [[ "$stash_count" -gt 0 ]]; then
            echo -e "   ${BLUE}Stashes:${NC} $stash_count entries"
        fi
        
        echo
    fi
    
    # AI Assistant Status
    echo -e "${CYAN}🤖 AI ASSISTANT STATUS${NC}"
    
    if [[ "${ASSISTANT_STATE[directory_exists]:-false}" == "true" ]]; then
        local active_processes="${ASSISTANT_STATE[active_processes]:-0}"
        local session_count="${ASSISTANT_STATE[session_count]:-0}"
        
        if [[ "$active_processes" -gt 0 ]]; then
            echo -e "   ${GREEN}✅ AI Assistant running (${active_processes} active processes)${NC}"
        else
            echo -e "   ${YELLOW}⚠️  AI Assistant directory exists but no active processes${NC}"
        fi
        
        echo -e "   ${BLUE}Sessions:${NC} $session_count"
        
        if [[ "$verbose" == "true" ]]; then
            local last_activity="${ASSISTANT_STATE[last_activity]:-0}"
            if [[ "$last_activity" != "0" ]]; then
                local activity_date
                activity_date=$(date -d "@$last_activity" 2>/dev/null || echo "unknown")
                echo -e "   ${BLUE}Last activity:${NC} $activity_date"
            fi
        fi
    else
        echo -e "   ${RED}❌ No AI Assistant session directory${NC}"
        if [[ "${WORKTREE_STATE[exists]:-false}" == "true" ]]; then
            echo -e "   ${YELLOW}💡 Suggestion: Launch Claude Code from the worktree directory${NC}"
        fi
    fi
    echo
    
    # Recommendations
    generate_recommendations
    
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════════════════════${NC}"
}

# Generate actionable recommendations
generate_recommendations() {
    echo -e "${CYAN}💡 RECOMMENDATIONS${NC}"
    
    local has_recommendations=false
    
    # Issue-related recommendations
    if [[ "${ISSUE_STATE[exists]:-false}" == "false" ]] && [[ "${ISSUE_STATE[github_available]:-false}" == "true" ]]; then
        echo -e "   ${YELLOW}⚠️  Verify issue number and repository access${NC}"
        has_recommendations=true
    fi
    
    # Worktree-related recommendations
    if [[ "${WORKTREE_STATE[exists]:-false}" == "false" ]]; then
        if [[ -n "${ISSUE_STATE[number]:-}" ]]; then
            echo -e "   ${YELLOW}📋 Create worktree: \`./worktree.sh create --from-issue ${ISSUE_STATE[number]}\`${NC}"
        else
            echo -e "   ${YELLOW}📋 Create worktree manually once issue is resolved${NC}"
        fi
        has_recommendations=true
    fi
    
    # Git-related recommendations
    if [[ "${GIT_STATE[available]:-false}" == "true" ]]; then
        if [[ "${GIT_STATE[working_clean]:-false}" == "false" ]]; then
            echo -e "   ${YELLOW}🔄 Commit or stash uncommitted changes${NC}"
            has_recommendations=true
        fi
        
        case "${GIT_STATE[sync_status]:-}" in
            "behind")
                echo -e "   ${YELLOW}⬇️  Pull latest changes: \`git pull\`${NC}"
                has_recommendations=true
                ;;
            "ahead")
                echo -e "   ${YELLOW}⬆️  Push local changes: \`git push\`${NC}"
                has_recommendations=true
                ;;
            "diverged")
                echo -e "   ${YELLOW}🔄 Resolve divergent branches (rebase or merge)${NC}"
                has_recommendations=true
                ;;
            "no_tracking")
                echo -e "   ${YELLOW}🔗 Set up tracking branch: \`git push -u origin ${WORKTREE_STATE[branch]:-current-branch}\`${NC}"
                has_recommendations=true
                ;;
        esac
    fi
    
    # Assistant-related recommendations
    if [[ "${WORKTREE_STATE[exists]:-false}" == "true" ]] && [[ "${ASSISTANT_STATE[directory_exists]:-false}" == "false" ]]; then
        echo -e "   ${YELLOW}🤖 Start AI Assistant: Launch Claude Code from worktree directory${NC}"
        has_recommendations=true
    elif [[ "${ASSISTANT_STATE[directory_exists]:-false}" == "true" ]] && [[ "${ASSISTANT_STATE[active_processes]:-0}" == "0" ]]; then
        echo -e "   ${YELLOW}🤖 Restart AI Assistant (stale session detected)${NC}"
        has_recommendations=true
    fi
    
    if [[ "$has_recommendations" == "false" ]]; then
        echo -e "   ${GREEN}✅ All systems operational - no recommendations${NC}"
    fi
    
    echo
}

# Generate JSON output
generate_json_output() {
    # Build comprehensive JSON structure
    local json_output
    
    # Use jq to build proper JSON structure
    json_output=$(jq -n \
        --arg spec "${ISSUE_STATE[original_spec]:-""}" \
        --arg spec_type "${ISSUE_STATE[spec_type]:-""}" \
        --arg github_available "${ISSUE_STATE[github_available]:-false}" \
        --arg issue_exists "${ISSUE_STATE[exists]:-false}" \
        --arg issue_number "${ISSUE_STATE[number]:-""}" \
        --arg issue_title "${ISSUE_STATE[title]:-""}" \
        --arg issue_state "${ISSUE_STATE[state]:-""}" \
        --arg issue_url "${ISSUE_STATE[url]:-""}" \
        --arg issue_assignees "${ISSUE_STATE[assignees]:-""}" \
        --arg issue_labels "${ISSUE_STATE[labels]:-""}" \
        --arg worktree_exists "${WORKTREE_STATE[exists]:-false}" \
        --arg worktree_path "${WORKTREE_STATE[path]:-""}" \
        --arg worktree_branch "${WORKTREE_STATE[branch]:-""}" \
        --arg worktree_size "${WORKTREE_STATE[size]:-""}" \
        --arg worktree_git_valid "${WORKTREE_STATE[git_valid]:-false}" \
        --arg worktree_last_modified "${WORKTREE_STATE[last_modified]:-0}" \
        --arg git_available "${GIT_STATE[available]:-false}" \
        --arg git_working_clean "${GIT_STATE[working_clean]:-false}" \
        --arg git_uncommitted_changes "${GIT_STATE[uncommitted_changes]:-0}" \
        --arg git_sync_status "${GIT_STATE[sync_status]:-""}" \
        --arg git_commits_ahead "${GIT_STATE[commits_ahead]:-0}" \
        --arg git_commits_behind "${GIT_STATE[commits_behind]:-0}" \
        --arg git_current_commit "${GIT_STATE[current_commit]:-""}" \
        --arg git_has_tracking "${GIT_STATE[has_tracking]:-false}" \
        --arg git_tracking_branch "${GIT_STATE[tracking_branch]:-""}" \
        --arg git_stash_count "${GIT_STATE[stash_count]:-0}" \
        --arg git_last_commit_hash "${GIT_STATE[last_commit_hash]:-""}" \
        --arg git_last_commit_message "${GIT_STATE[last_commit_message]:-""}" \
        --arg git_last_commit_author "${GIT_STATE[last_commit_author]:-""}" \
        --arg git_last_commit_date "${GIT_STATE[last_commit_date]:-""}" \
        --arg assistant_directory_exists "${ASSISTANT_STATE[directory_exists]:-false}" \
        --arg assistant_active_processes "${ASSISTANT_STATE[active_processes]:-0}" \
        --arg assistant_session_count "${ASSISTANT_STATE[session_count]:-0}" \
        --arg assistant_last_activity "${ASSISTANT_STATE[last_activity]:-0}" \
        '{
            "specification": {
                "input": $spec,
                "type": $spec_type,
                "resolved_successfully": (($issue_exists == "true") or ($worktree_exists == "true"))
            },
            "github": {
                "cli_available": ($github_available == "true"),
                "issue": {
                    "exists": ($issue_exists == "true"),
                    "number": $issue_number,
                    "title": $issue_title,
                    "state": $issue_state,
                    "url": $issue_url,
                    "assignees": ($issue_assignees | split(",") | map(select(. != ""))),
                    "labels": ($issue_labels | split(",") | map(select(. != "")))
                }
            },
            "worktree": {
                "exists": ($worktree_exists == "true"),
                "path": $worktree_path,
                "branch": $worktree_branch,
                "size": $worktree_size,
                "git_repository_valid": ($worktree_git_valid == "true"),
                "last_modified_timestamp": ($worktree_last_modified | tonumber)
            },
            "git": {
                "available": ($git_available == "true"),
                "working_directory": {
                    "clean": ($git_working_clean == "true"),
                    "uncommitted_changes_count": ($git_uncommitted_changes | tonumber)
                },
                "sync": {
                    "status": $git_sync_status,
                    "commits_ahead": ($git_commits_ahead | tonumber),
                    "commits_behind": ($git_commits_behind | tonumber),
                    "has_tracking_branch": ($git_has_tracking == "true"),
                    "tracking_branch": $git_tracking_branch
                },
                "commit": {
                    "current_hash": $git_current_commit,
                    "last_commit": {
                        "hash": $git_last_commit_hash,
                        "message": $git_last_commit_message,
                        "author": $git_last_commit_author,
                        "date": $git_last_commit_date
                    }
                },
                "stash_count": ($git_stash_count | tonumber)
            },
            "ai_assistant": {
                "session_directory_exists": ($assistant_directory_exists == "true"),
                "active_processes": ($assistant_active_processes | tonumber),
                "session_count": ($assistant_session_count | tonumber),
                "last_activity_timestamp": ($assistant_last_activity | tonumber),
                "status": (
                    if ($assistant_directory_exists == "true" and ($assistant_active_processes | tonumber) > 0)
                    then "running"
                    elif ($assistant_directory_exists == "true")
                    then "idle"
                    else "not_initialized"
                    end
                )
            },
            "summary": {
                "overall_status": (
                    if (($worktree_exists == "true") and ($git_working_clean == "true") and ($git_sync_status == "synced"))
                    then "healthy"
                    elif ($worktree_exists == "true")
                    then "needs_attention" 
                    else "not_ready"
                    end
                ),
                "recommendations_count": 0
            }
        }')
    
    echo "$json_output"
}

# Show usage information
show_usage() {
    cat << EOF
Git Worktree Inspect Utility

USAGE:
    ./worktree-inspect.sh <ISSUE_SPEC> [options]

ISSUE_SPEC FORMATS:
    123                     GitHub issue number
    #123                    GitHub issue number (with hash)
    "feature title"         Issue title search (fuzzy matching)
    issue-123-feature       Branch name pattern

OPTIONS:
    --json, -j              Output in JSON format
    --verbose, -v           Show detailed information
    --help, -h              Show this help message

DESCRIPTION:
    Provides comprehensive analysis of worktree state for issue workflow management.
    Analyzes worktree existence, git state, AI assistant status, and GitHub integration.

EXAMPLES:
    ./worktree-inspect.sh 115
    ./worktree-inspect.sh --json 115
    ./worktree-inspect.sh --verbose "add worktree inspect"
    ./worktree-inspect.sh issue-115-worktree-inspect

OUTPUT SECTIONS:
    - Issue Information: GitHub issue metadata and validation
    - Worktree Status: Directory existence and git repository validity
    - Git Status: Working directory, sync status, and commit information
    - AI Assistant Status: Session directory and active process detection
    - Recommendations: Actionable suggestions for workflow optimization

EOF
}

# Main execution function
main() {
    local issue_spec=""
    local json_output=false
    local verbose=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --json|-j)
                json_output=true
                shift
                ;;
            --verbose|-v)
                verbose=true
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                if [[ -z "$issue_spec" ]]; then
                    issue_spec="$1"
                else
                    print_error "Multiple issue specifications provided. Use only one."
                    show_usage
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # Validate required arguments
    if [[ -z "$issue_spec" ]]; then
        print_error "Missing required ISSUE_SPEC argument"
        show_usage
        exit 1
    fi
    
    # Store original specification for reporting
    ISSUE_STATE["original_spec"]="$issue_spec"
    
    # Ensure we're in a git repository
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        print_error "Not in a git repository"
        exit 1
    fi
    
    # Move to main repository for consistent git operations
    cd "$MAIN_REPO" || {
        print_error "Unable to change to main repository directory: $MAIN_REPO"
        exit 1
    }
    
    # Phase 1: Resolve issue specification
    if ! resolve_issue_spec "$issue_spec"; then
        if [[ "$json_output" == "true" ]]; then
            # Still output JSON even on resolution failure
            generate_json_output
        else
            print_error "Unable to resolve issue specification: $issue_spec"
            echo
            print_info "Supported formats:"
            print_info "  • GitHub issue number: 123, #123"
            print_info "  • Branch name: issue-123-feature, feature/branch-name"
            print_info "  • Issue title search: \"add new feature\""
        fi
        exit 1
    fi
    
    # Phase 2: Find worktree
    find_worktree_path || true  # Don't fail if worktree doesn't exist
    
    # Phase 3: Analyze states
    analyze_worktree_directory || true
    analyze_assistant_state || true
    analyze_git_state || true
    
    # Phase 4: Generate output
    if [[ "$json_output" == "true" ]]; then
        generate_json_output
    else
        generate_summary_output "$verbose"
    fi
    
    # Exit with appropriate code
    if [[ "${WORKTREE_STATE[exists]:-false}" == "true" ]]; then
        exit 0  # Success: worktree exists
    else
        exit 2  # Informational: worktree doesn't exist but analysis completed
    fi
}

# Check arguments
if [[ $# -lt 1 ]] || [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    show_usage
    exit 0
fi

# Execute main function
main "$@"