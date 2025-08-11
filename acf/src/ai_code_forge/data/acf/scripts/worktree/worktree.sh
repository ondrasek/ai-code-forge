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
    create <branch-name> [issue-number]  Create a new worktree
    create --from-issue <issue-number>   Create worktree from GitHub issue
    list                                 List all worktrees
    cleanup [--dry-run] [--force]        Clean up invalid worktrees
    help                                 Show this help message

EXAMPLES:
    ./worktree.sh create feature/new-api
    ./worktree.sh create feature/fix-123 123
    ./worktree.sh create --from-issue 456
    ./worktree.sh list
    ./worktree.sh cleanup --dry-run
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
        create)
            if [[ ! -f "$SCRIPT_DIR/worktree-create.sh" ]]; then
                print_error "worktree-create.sh not found in $SCRIPT_DIR"
                exit 1
            fi
            exec "$SCRIPT_DIR/worktree-create.sh" "$@"
            ;;
        list)
            if [[ ! -f "$SCRIPT_DIR/worktree-list.sh" ]]; then
                print_error "worktree-list.sh not found in $SCRIPT_DIR"
                exit 1
            fi
            exec "$SCRIPT_DIR/worktree-list.sh" "$@"
            ;;
        cleanup)
            if [[ ! -f "$SCRIPT_DIR/worktree-cleanup.sh" ]]; then
                print_error "worktree-cleanup.sh not found in $SCRIPT_DIR"
                exit 1
            fi
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