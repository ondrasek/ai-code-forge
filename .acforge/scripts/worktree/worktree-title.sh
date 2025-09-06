#!/bin/bash
# Worktree Terminal Title Management
# Shared functions for updating terminal titles with issue context
# Usage: source this file in other worktree scripts

# Update terminal title with issue context
# Usage: update_terminal_title [issue_number] [context]
update_terminal_title() {
    local issue_number="$1"
    local context="${2:-worktree}"

    # Only update title in interactive terminals
    if [[ ! -t 1 ]] && [[ -z "${PS1:-}" ]]; then
        return 0
    fi

    local title=""

    if [[ -n "$issue_number" && "$issue_number" =~ ^[0-9]+$ ]]; then
        title="Issue #${issue_number} - ${context}"
    else
        # Try to extract issue number from current directory or branch
        local extracted_issue
        if extracted_issue=$(extract_issue_from_context); then
            title="#${extracted_issue}/${context}"
        else
            # Fallback to generic worktree title
            title="${context}"
        fi
    fi

    # Set terminal title using ANSI escape sequence (works in most terminals)
    printf '\033]0;%s\007' "$title"
}

# Extract issue number from current context (directory path, branch name, etc.)
extract_issue_from_context() {
    local issue_num=""

    # Method 1: Extract from current directory path
    local current_dir
    current_dir=$(pwd 2>/dev/null || echo "")
    if [[ "$current_dir" =~ /issue-([0-9]+)(/|$) ]]; then
        issue_num="${BASH_REMATCH[1]}"
        echo "$issue_num"
        return 0
    fi

    # Method 2: Extract from current git branch
    if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        local branch_name
        branch_name=$(git symbolic-ref --short HEAD 2>/dev/null || echo "")
        if [[ "$branch_name" =~ issue-([0-9]+)- ]]; then
            issue_num="${BASH_REMATCH[1]}"
            echo "$issue_num"
            return 0
        fi
    fi

    # Method 3: Extract from worktree directory structure
    if [[ "$current_dir" =~ worktrees/[^/]+/issue-([0-9]+) ]]; then
        issue_num="${BASH_REMATCH[1]}"
        echo "$issue_num"
        return 0
    fi

    return 1
}

# Update title based on current context (no parameters needed)
# Useful for shell prompts or when context changes
update_title_from_context() {
    local context="${1:-worktree}"
    local issue_num

    if issue_num=$(extract_issue_from_context); then
        update_terminal_title "$issue_num" "$context"
    else
        update_terminal_title "" "$context"
    fi
}

# Clear terminal title (restore default)
clear_terminal_title() {
    # Only clear title in interactive terminals
    if [[ ! -t 1 ]] && [[ -z "${PS1:-}" ]]; then
        return 0
    fi

    # Reset to default terminal title
    printf '\033]0;\007'
}