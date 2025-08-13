#!/bin/bash
set -euo pipefail

# Git Worktree Shell Initialization
# Generates shell-specific configuration for worktree commands
# Usage: ./worktree-init.sh [--shell bash|zsh|fish] [--help]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_error() { echo -e "${RED}ERROR:${NC} $1" >&2; }
print_success() { echo -e "${GREEN}SUCCESS:${NC} $1" >&2; }
print_warning() { echo -e "${YELLOW}WARNING:${NC} $1" >&2; }
print_info() { echo -e "${BLUE}INFO:${NC} $1" >&2; }

# Check if running from main working copy
check_main_working_copy() {
    # Check if we're in a git repository
    if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        print_warning "Not in a git repository - cannot verify main working copy location"
        return 1  # Return 1 to indicate non-main (safer default)
    fi
    
    # Main working copy has .git as directory, worktrees have .git as file
    if [[ ! -d ".git" ]]; then
        print_warning "Running 'init' from worktree instead of main working copy"
        print_warning "Generated paths will point to: $SCRIPT_DIR"
        print_warning "For consistent behavior, consider running from the main working copy"
        print_warning "Current configuration will only work when scripts are available at the generated paths"
        return 1  # Return 1 to indicate running from worktree
    fi
    
    return 0  # Return 0 to indicate running from main working copy
}

# Show usage information
show_usage() {
    cat << EOF
Git Worktree Shell Initialization

USAGE:
    ./worktree-init.sh [--shell SHELL] [--help]

OPTIONS:
    --shell SHELL    Override automatic shell detection (bash|zsh|fish)
    --help          Show this help message

EXAMPLES:
    # Auto-detect shell and output configuration
    eval "\$(./worktree.sh init)"
    
    # Specify shell explicitly
    eval "\$(./worktree.sh init --shell zsh)"
    
    # Append to shell RC file
    ./worktree.sh init --shell zsh >> ~/.zshrc
    
    # View configuration without applying
    ./worktree.sh init --shell bash

SUPPORTED SHELLS:
    - bash (GNU Bash)
    - zsh (Z Shell)
    - fish (Friendly Interactive Shell)

TERMINAL TITLE MANAGEMENT:
    When using wtcd() to navigate between worktrees, terminal titles will automatically
    update to show the issue number and description (e.g., "Issue #123: Brief title").
    
    This feature works with most terminal emulators but requires special configuration
    for VSCode's integrated terminal.

VSCODE INTEGRATION:
    VSCode's integrated terminal requires additional configuration to display terminal
    titles set by worktree navigation. Follow these steps:

    1. Open VSCode Settings (Ctrl/Cmd + ,)
    2. Search for "terminal.integrated.tabs.title"
    3. Set the value to: \${sequence}
    
    Alternative: Add to settings.json:
        "terminal.integrated.tabs.title": "\${sequence}"
    
    After configuration:
    - Terminal tabs will show "Issue #123: Brief title" when using wtcd()
    - Titles update automatically when switching between worktrees
    - Works across VSCode, VSCode Insiders, and Codespaces
    
    Troubleshooting VSCode:
    - If titles don't appear, restart VSCode after changing settings
    - Ensure "terminal.integrated.tabs.showActiveTerminal" is not "never"
    - Check that OSC sequences aren't disabled in terminal settings

SUPPORTED TERMINALS:
    ✓ iTerm2, Terminal.app (macOS)
    ✓ gnome-terminal, konsole (Linux) 
    ✓ Windows Terminal, Alacritty, Kitty
    ✓ tmux, screen (with proper configuration)
    ⚠ VSCode integrated terminal (requires settings configuration above)
    ✗ Basic terminals without OSC sequence support

SECURITY CONSIDERATIONS:
    - Configuration uses absolute paths to prevent PATH manipulation
    - Shell type input is validated against supported shells only
    - Terminal titles are sanitized to prevent escape sequence injection
    - All generated commands include explanatory comments
    - Users should review output before eval'ing

EOF
}

# Validate shell type to prevent command injection
validate_shell() {
    local shell="$1"
    case "$shell" in
        bash|zsh|fish)
            return 0
            ;;
        *)
            print_error "Unsupported shell: $shell"
            print_error "Supported shells: bash, zsh, fish"
            return 1
            ;;
    esac
}

# Detect current shell
detect_shell() {
    local shell_name
    
    # Try multiple detection methods
    if [[ -n "${ZSH_VERSION:-}" ]]; then
        echo "zsh"
    elif [[ -n "${BASH_VERSION:-}" ]]; then
        echo "bash"
    elif [[ -n "${FISH_VERSION:-}" ]]; then
        echo "fish"
    else
        # Fallback to process name
        shell_name="$(basename "${SHELL:-/bin/bash}")"
        case "$shell_name" in
            zsh|bash|fish)
                echo "$shell_name"
                ;;
            *)
                print_warning "Could not detect shell, defaulting to bash" >&2
                echo "bash"
                ;;
        esac
    fi
}

# Generate bash/zsh configuration
generate_bash_zsh_config() {
    local shell="$1"
    local script_dir="$2"
    local is_worktree="$3"  # 0 = main working copy, 1 = worktree
    
    cat << EOF
# Git Worktree Management - Generated by worktree.sh init for $shell
# This configuration adds worktree commands to your PATH and creates convenient aliases
# Review these changes before applying to your shell configuration
EOF

    # Add warning to stderr if generated from worktree
    if [[ "$is_worktree" == "1" ]]; then
        cat << 'EOF'

# WORKTREE LOCATION WARNING - This will be output to stderr when sourced
if [[ -t 2 ]] || [[ -n "${PS1:-}" ]]; then
    echo "WARNING: Worktree configuration sourced - paths point to worktree location" >&2
    echo "WARNING: Configuration may not work if worktree is removed or unavailable" >&2
fi

EOF
    fi

    cat << EOF
# Add worktree scripts directory to PATH
# WARNING: This modifies your PATH - ensure you trust these scripts
if [[ ":\$PATH:" != *":$script_dir:"* ]]; then
    export PATH="$script_dir:\$PATH"
fi

# Convenient aliases for worktree operations
# These provide shorter commands while maintaining security through absolute paths
alias wt="$script_dir/worktree.sh"                    # Main worktree command
alias wtc="$script_dir/worktree.sh create"            # Create worktree
alias wtl="$script_dir/worktree.sh list"              # List worktrees
alias wti="$script_dir/worktree.sh inspect"           # Inspect worktree
alias wtw="$script_dir/worktree.sh watch"             # Watch processes
alias wtr="$script_dir/worktree.sh remove"            # Remove worktree

# Advanced navigation functions
# Function to check if terminal supports title setting
_supports_terminal_title() {
    # Conservative detection - only enable for well-known terminals
    case "\${TERM:-}" in
        xterm*|screen*|tmux*|rxvt*|gnome*|konsole*|alacritty*|kitty*|iterm*|vte*)
            return 0 ;;
        *)
            return 1 ;;
    esac
}

# Function to safely set terminal title with input sanitization
_set_terminal_title() {
    local title="\$1"
    
    # Security: Remove escape sequences and shell metacharacters
    title="\${title//\$'\e'*/}"           # Remove escape sequences starting with ESC
    title="\${title//\$'\x1b'*/}"         # Remove escape sequences starting with 0x1b
    title="\${title//\$'\\033'*/}"        # Remove escape sequences starting with \\033
    title="\${title//[\$\\\`\;|&]/}"        # Remove shell metacharacters
    title="\${title//[[:cntrl:]]/}"       # Remove all control characters
    
    # Limit length to prevent buffer overflow (conservative 80 char limit)
    title="\${title:0:80}"
    
    # Only set title if terminal supports it and title is not empty
    if _supports_terminal_title && [[ -n "\$title" ]]; then
        printf '\e]0;%s\a' "\$title"
    fi
}

# Function to extract issue context for terminal title
_get_issue_title_for_worktree() {
    local target="\$1"
    local issue_num
    local issue_title
    
    # Extract issue number from target (handles issue-123 or just 123)
    if [[ "\$target" =~ ^issue-?([0-9]+) ]]; then
        issue_num="\${BASH_REMATCH[1]}"
    elif [[ "\$target" =~ ^([0-9]+)\$ ]]; then
        issue_num="\$target"
    else
        # Not an issue number - use branch/target name as-is
        echo "Worktree: \$target"
        return 0
    fi
    
    # Try to get issue title from GitHub CLI
    if command -v gh >/dev/null 2>&1; then
        issue_title="\$(gh issue view "\$issue_num" --json title --jq .title 2>/dev/null)"
        if [[ -n "\$issue_title" ]]; then
            echo "Issue #\$issue_num: \$issue_title"
            return 0
        fi
    fi
    
    # Fallback to generic issue format
    echo "Issue #\$issue_num"
}

# Function to change directory to worktree by issue number or branch
wtcd() {
    local target="\$1"
    if [[ -z "\$target" ]]; then
        echo "Usage: wtcd <issue-number|branch-name>" >&2
        return 1
    fi
    
    local worktree_path
    worktree_path="\$($script_dir/worktree.sh path "\$target" 2>/dev/null)"
    
    if [[ -z "\$worktree_path" ]]; then
        echo "ERROR: Could not find worktree for: \$target" >&2
        return 1
    fi
    
    if [[ ! -d "\$worktree_path" ]]; then
        echo "ERROR: Worktree directory does not exist: \$worktree_path" >&2
        return 1
    fi
    
    if cd "\$worktree_path"; then
        echo "Switched to worktree: \$worktree_path"
        
        # Update terminal title with issue context
        if [[ -f "$script_dir/worktree-title.sh" ]]; then
            source "$script_dir/worktree-title.sh"
            # Try to extract issue number from target or use auto-detection
            if [[ "\$target" =~ ^[0-9]+\$ ]]; then
                update_terminal_title "\$target" "\$(basename "\$worktree_path")"
            else
                update_title_from_context "\$(basename "\$worktree_path")"
            fi
        fi
        return 0
    else
        return 1
    fi
}

# Function to launch Claude Code in specific worktree
wtlaunch() {
    local target="\$1"
    if [[ -z "\$target" ]]; then
        echo "Usage: wtlaunch <issue-number|branch-name>" >&2
        return 1
    fi
    
    "$script_dir/worktree.sh" launch "\$target"
}

EOF
}

# Generate fish shell configuration
generate_fish_config() {
    local script_dir="$1"
    local is_worktree="$2"  # 0 = main working copy, 1 = worktree
    
    cat << EOF
# Git Worktree Management - Generated by worktree.sh init for fish
# This configuration adds worktree commands to your PATH and creates convenient aliases
# Review these changes before applying to your fish configuration
EOF

    # Add warning to stderr if generated from worktree
    if [[ "$is_worktree" == "1" ]]; then
        cat << 'EOF'

# WORKTREE LOCATION WARNING - This will be output to stderr when sourced
if isatty stderr; or set -q PS1
    echo "WARNING: Worktree configuration sourced - paths point to worktree location" >&2
    echo "WARNING: Configuration may not work if worktree is removed or unavailable" >&2
end

EOF
    fi

    cat << EOF
# Add worktree scripts directory to PATH
# WARNING: This modifies your PATH - ensure you trust these scripts
if not contains "$script_dir" \$PATH
    set -gx PATH "$script_dir" \$PATH
end

# Convenient aliases for worktree operations
# These provide shorter commands while maintaining security through absolute paths
alias wt="$script_dir/worktree.sh"                    # Main worktree command
alias wtc="$script_dir/worktree.sh create"            # Create worktree
alias wtl="$script_dir/worktree.sh list"              # List worktrees
alias wti="$script_dir/worktree.sh inspect"           # Inspect worktree
alias wtw="$script_dir/worktree.sh watch"             # Watch processes
alias wtr="$script_dir/worktree.sh remove"            # Remove worktree

# Advanced navigation functions
# Function to check if terminal supports title setting
function _supports_terminal_title
    # Conservative detection - only enable for well-known terminals
    switch "\$TERM"
        case 'xterm*' 'screen*' 'tmux*' 'rxvt*' 'gnome*' 'konsole*' 'alacritty*' 'kitty*' 'iterm*' 'vte*'
            return 0
        case '*'
            return 1
    end
end

# Function to safely set terminal title with input sanitization
function _set_terminal_title
    set title \$argv[1]
    
    # Security: Remove escape sequences and shell metacharacters
    # Fish doesn't support bash parameter expansion, use string replace
    set title (string replace -a -r '\e.*' '' \$title)     # Remove escape sequences
    set title (string replace -a -r '\x1b.*' '' \$title)   # Remove escape sequences
    set title (string replace -a -r '[\$\`\;|&]' '' \$title) # Remove shell metacharacters
    set title (string replace -a -r '[[:cntrl:]]' '' \$title) # Remove control characters
    
    # Limit length to prevent buffer overflow (80 chars)
    if test (string length \$title) -gt 80
        set title (string sub -l 80 \$title)
    end
    
    # Only set title if terminal supports it and title is not empty
    if _supports_terminal_title; and test -n "\$title"
        printf '\e]0;%s\a' "\$title"
    end
end

# Function to extract issue context for terminal title
function _get_issue_title_for_worktree
    set target \$argv[1]
    set issue_num ""
    set issue_title ""
    
    # Extract issue number from target (handles issue-123 or just 123)
    if string match -qr '^issue-?([0-9]+)' \$target
        set issue_num (string replace -r '^issue-?([0-9]+).*' '\$1' \$target)
    else if string match -qr '^([0-9]+)\$' \$target
        set issue_num \$target
    else
        # Not an issue number - use branch/target name as-is
        echo "Worktree: \$target"
        return 0
    end
    
    # Try to get issue title from GitHub CLI
    if command -v gh >/dev/null 2>&1
        set issue_title (gh issue view \$issue_num --json title --jq .title 2>/dev/null)
        if test -n "\$issue_title"
            echo "Issue #\$issue_num: \$issue_title"
            return 0
        end
    end
    
    # Fallback to generic issue format
    echo "Issue #\$issue_num"
end

# Function to change directory to worktree by issue number or branch
function wtcd
    if test (count \$argv) -eq 0
        echo "Usage: wtcd <issue-number|branch-name>" >&2
        return 1
    end
    
    set target \$argv[1]
    set worktree_path ("$script_dir/worktree.sh" path "\$target" 2>/dev/null)
    
    if test -z "\$worktree_path"
        echo "ERROR: Could not find worktree for: \$target" >&2
        return 1
    end
    
    if not test -d "\$worktree_path"
        echo "ERROR: Worktree directory does not exist: \$worktree_path" >&2
        return 1
    end
    
    if cd "\$worktree_path"
        echo "Switched to worktree: \$worktree_path"
        
        # Update terminal title with issue context
        if test -f "$script_dir/worktree-title.sh"
            source "$script_dir/worktree-title.sh"
            # Try to extract issue number from target or use auto-detection
            if string match -qr '^[0-9]+\$' "\$target"
                update_terminal_title "\$target" (basename "\$worktree_path")
            else
                update_title_from_context (basename "\$worktree_path")
            end
        end
        return 0
    else
        return 1
    end
end

# Function to launch Claude Code in specific worktree
function wtlaunch
    if test (count \$argv) -eq 0
        echo "Usage: wtlaunch <issue-number|branch-name>" >&2
        return 1
    end
    
    set target \$argv[1]
    "$script_dir/worktree.sh" launch "\$target"
end

EOF
}

# Main initialization function
main() {
    local shell_override=""
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --shell)
                if [[ $# -lt 2 ]]; then
                    print_error "--shell option requires a shell name"
                    exit 1
                fi
                shell_override="$2"
                shift 2
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Determine target shell
    local target_shell
    if [[ -n "$shell_override" ]]; then
        target_shell="$shell_override"
    else
        target_shell="$(detect_shell)"
    fi
    
    # Validate shell
    if ! validate_shell "$target_shell"; then
        exit 1
    fi
    
    # Verify script directory exists and is accessible
    if [[ ! -d "$SCRIPT_DIR" ]]; then
        print_error "Script directory does not exist: $SCRIPT_DIR" >&2
        exit 1
    fi
    
    if [[ ! -r "$SCRIPT_DIR" ]]; then
        print_error "Script directory is not readable: $SCRIPT_DIR" >&2
        exit 1
    fi
    
    # Verify main worktree.sh script exists
    if [[ ! -f "$SCRIPT_DIR/worktree.sh" ]]; then
        print_error "Main worktree.sh script not found: $SCRIPT_DIR/worktree.sh" >&2
        exit 1
    fi
    
    if [[ ! -x "$SCRIPT_DIR/worktree.sh" ]]; then
        print_error "Main worktree.sh script is not executable: $SCRIPT_DIR/worktree.sh" >&2
        exit 1
    fi
    
    # Check if running from main working copy and warn if not
    local is_worktree=0
    if ! check_main_working_copy; then
        is_worktree=1
    fi
    
    # Generate configuration based on shell type
    case "$target_shell" in
        bash|zsh)
            generate_bash_zsh_config "$target_shell" "$SCRIPT_DIR" "$is_worktree"
            ;;
        fish)
            generate_fish_config "$SCRIPT_DIR" "$is_worktree"
            ;;
        *)
            # This should never happen due to validate_shell, but defensive programming
            print_error "Internal error: unhandled shell type: $target_shell" >&2
            exit 1
            ;;
    esac
    
    # Output success message to stderr (so it doesn't interfere with eval)
    # Only show messages in interactive shells to avoid eval interference
    if [[ -t 0 ]] || [[ -n "${PS1:-}" ]]; then
        print_info "Generated configuration for $target_shell shell" >&2
        print_warning "Review the output before applying with eval or appending to RC files" >&2
    fi
}

# Run main function with all arguments
main "$@"