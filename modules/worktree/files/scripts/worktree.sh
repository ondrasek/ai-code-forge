#!/bin/bash
set -euo pipefail

# Git Worktree Management Wrapper
# Unified interface for all worktree operations
# Usage: ./worktree.sh <command> [options]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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
Git Worktree Management Wrapper

USAGE:
    ./worktree.sh <command> [options]

COMMANDS:
    init [--shell SHELL]                 Generate shell-specific configuration for eval
    create <branch-name> [issue-number]  Create a new worktree
    create --from-issue <issue-number>   Create worktree from GitHub issue
    deliver <issue-number|branch-name>   Create worktree and launch Claude Code with issue context
    path <issue-number|main>             Output worktree directory path
    launch <issue-number|branch-name>    Launch Claude Code in specified worktree
    list [issue-number]                  List all worktrees or specific issue worktree
    list --verbose [issue-number]        List with detailed information
    inspect <issue-spec> [--json] [-v]   Comprehensive issue and worktree state analysis
    watch [options]                      Monitor Claude Code processes and worktree activity
    remove <worktree-path>               Remove specific worktree by path
    remove <issue-number>                Remove worktree by issue number
    remove-all [--dry-run]               Remove all worktrees (with confirmation)
    prune [--dry-run]                    Remove stale worktree references
    help                                 Show this help message

EXAMPLES:
    ./worktree.sh init                   # Generate shell config (auto-detect)
    eval "\$(./worktree.sh init)"         # Apply configuration to current shell
    ./worktree.sh init --shell zsh       # Generate zsh-specific config
    ./worktree.sh create feature/new-api
    ./worktree.sh create feature/fix-123 123
    ./worktree.sh create --from-issue 456
    ./worktree.sh deliver 123            # Create worktree for issue #123 and launch Claude Code with context
    ./worktree.sh deliver feature/fix-456 # Create worktree for branch and launch
    ./worktree.sh path 123               # Output path for issue #123
    ./worktree.sh path main              # Output path for main branch
    cd \$(./worktree.sh path 123)         # Change to issue #123 worktree
    ./worktree.sh launch 123
    ./worktree.sh launch feature/fix-456
    ./worktree.sh list
    ./worktree.sh list 123               # Show worktree for issue #123
    ./worktree.sh list --verbose
    ./worktree.sh inspect 115            # Analyze issue #115 state
    ./worktree.sh inspect --json 115     # JSON output for scripting
    ./worktree.sh inspect --verbose "add worktree inspect"  # Search by title
    ./worktree.sh watch                  # Monitor Claude processes and worktrees
    ./worktree.sh watch --test           # Test mode with debugging output
    ./worktree.sh remove 123             # Remove worktree for issue #123
    ./worktree.sh remove /path/to/worktree
    ./worktree.sh remove-all --dry-run
    ./worktree.sh prune --dry-run
    ./worktree.sh help

For detailed information about each command, run:
    ./worktree-<command>.sh --help

EOF
}

# Main command dispatcher
main() {
    if [[ $# -eq 0 ]]; then
        print_error "No command specified"
        show_usage
        exit 1
    fi

    local command="$1"
    shift

    case "$command" in
        init)
            if [[ ! -f "$SCRIPT_DIR/worktree-init.sh" ]]; then
                print_error "worktree-init.sh not found in $SCRIPT_DIR"
                exit 1
            fi
            exec "$SCRIPT_DIR/worktree-init.sh" "$@"
            ;;
        create)
            if [[ ! -f "$SCRIPT_DIR/worktree-create.sh" ]]; then
                print_error "worktree-create.sh not found in $SCRIPT_DIR"
                exit 1
            fi
            exec "$SCRIPT_DIR/worktree-create.sh" "$@"
            ;;
        deliver)
            if [[ ! -f "$SCRIPT_DIR/worktree-deliver.sh" ]]; then
                print_error "worktree-deliver.sh not found in $SCRIPT_DIR"
                exit 1
            fi
            exec "$SCRIPT_DIR/worktree-deliver.sh" "$@"
            ;;
        path)
            if [[ ! -f "$SCRIPT_DIR/worktree-path.sh" ]]; then
                print_error "worktree-path.sh not found in $SCRIPT_DIR"
                exit 1
            fi
            exec "$SCRIPT_DIR/worktree-path.sh" "$@"
            ;;
        launch)
            if [[ ! -f "$SCRIPT_DIR/worktree-launch.sh" ]]; then
                print_error "worktree-launch.sh not found in $SCRIPT_DIR"
                exit 1
            fi
            exec "$SCRIPT_DIR/worktree-launch.sh" "$@"
            ;;
        list)
            if [[ ! -f "$SCRIPT_DIR/worktree-list.sh" ]]; then
                print_error "worktree-list.sh not found in $SCRIPT_DIR"
                exit 1
            fi
            exec "$SCRIPT_DIR/worktree-list.sh" "$@"
            ;;
        inspect)
            if [[ ! -f "$SCRIPT_DIR/worktree-inspect.sh" ]]; then
                print_error "worktree-inspect.sh not found in $SCRIPT_DIR"
                exit 1
            fi
            exec "$SCRIPT_DIR/worktree-inspect.sh" "$@"
            ;;
        watch)
            if [[ ! -f "$SCRIPT_DIR/worktree-watch.sh" ]]; then
                print_error "worktree-watch.sh not found in $SCRIPT_DIR"
                exit 1
            fi
            exec "$SCRIPT_DIR/worktree-watch.sh" "$@"
            ;;
        remove)
            if [[ ! -f "$SCRIPT_DIR/worktree-cleanup.sh" ]]; then
                print_error "worktree-cleanup.sh not found in $SCRIPT_DIR"
                exit 1
            fi
            exec "$SCRIPT_DIR/worktree-cleanup.sh" remove "$@"
            ;;
        remove-all)
            if [[ ! -f "$SCRIPT_DIR/worktree-cleanup.sh" ]]; then
                print_error "worktree-cleanup.sh not found in $SCRIPT_DIR"
                exit 1
            fi
            exec "$SCRIPT_DIR/worktree-cleanup.sh" remove-all "$@"
            ;;
        prune)
            if [[ ! -f "$SCRIPT_DIR/worktree-cleanup.sh" ]]; then
                print_error "worktree-cleanup.sh not found in $SCRIPT_DIR"
                exit 1
            fi
            exec "$SCRIPT_DIR/worktree-cleanup.sh" prune "$@"
            ;;
        cleanup)
            # Backward compatibility - default to list command
            if [[ ! -f "$SCRIPT_DIR/worktree-cleanup.sh" ]]; then
                print_error "worktree-cleanup.sh not found in $SCRIPT_DIR"
                exit 1
            fi
            print_warning "The 'cleanup' command is deprecated. Use 'remove', 'remove-all', or 'prune' instead."
            exec "$SCRIPT_DIR/worktree-cleanup.sh" "$@"
            ;;
        help|--help|-h)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown command: $command"
            echo
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"