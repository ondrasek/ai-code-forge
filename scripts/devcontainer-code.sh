#!/bin/bash

# devcontainer-code.sh - Launch VS Code directly into DevContainer
# This script provides one-command access to containerized development environments
#
# Usage:
#   ./scripts/devcontainer-code.sh [options]
#
# Options:
#   --debug           Enable debug output
#   --force-restart   Force restart container before launch
#   --dry-run         Preview actions without execution
#   --help           Show this help message

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEVCONTAINER_CONFIG="$PROJECT_ROOT/.devcontainer"
DEVCONTAINER_JSON="$DEVCONTAINER_CONFIG/devcontainer.json"

# Color output functions (following existing launch-claude.sh pattern)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }

# Default options
DEBUG="false"
FORCE_RESTART="false"
DRY_RUN="false"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --debug)
            DEBUG="true"
            shift
            ;;
        --force-restart)
            FORCE_RESTART="true"
            shift
            ;;
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        --help|-h)
            echo "DevContainer VS Code Launch Script"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --debug           Enable debug output"
            echo "  --force-restart   Force restart container before launch"
            echo "  --dry-run         Preview actions without execution"
            echo "  --help           Show this help message"
            echo ""
            echo "This script launches VS Code directly into a running DevContainer"
            echo "using the modern DevContainer CLI + VS Code approach."
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            exit 1
            ;;
    esac
done

debug() {
    if [[ "$DEBUG" == "true" ]]; then
        echo -e "${BLUE}🐛 DEBUG: $1${NC}" >&2
    fi
}

execute() {
    local cmd="$1"
    if [[ "$DRY_RUN" == "true" ]]; then
        info "DRY RUN: Would execute: $cmd"
    else
        debug "Executing: $cmd"
        eval "$cmd"
    fi
}

# Validation functions
check_dependencies() {
    info "Checking dependencies..."
    
    local missing_deps=()
    
    # Check VS Code
    if ! command -v code >/dev/null 2>&1; then
        missing_deps+=("VS Code CLI (code command)")
    else
        debug "Found VS Code CLI: $(code --version | head -n1)"
    fi
    
    # Check DevContainer CLI  
    if ! command -v devcontainer >/dev/null 2>&1; then
        warning "DevContainer CLI not found. Installing..."
        if [[ "$DRY_RUN" != "true" ]]; then
            if command -v npm >/dev/null 2>&1; then
                npm install -g @devcontainers/cli
                success "DevContainer CLI installed"
            else
                missing_deps+=("DevContainer CLI (@devcontainers/cli)")
            fi
        fi
    else
        debug "Found DevContainer CLI: $(devcontainer --version)"
    fi
    
    # Check Docker
    if ! command -v docker >/dev/null 2>&1; then
        missing_deps+=("Docker")
    else
        if ! docker info >/dev/null 2>&1; then
            missing_deps+=("Docker (daemon not running)")
        else
            debug "Docker is running: $(docker --version)"
        fi
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        error "Missing dependencies:"
        for dep in "${missing_deps[@]}"; do
            echo "  - $dep"
        done
        echo ""
        echo "Installation instructions:"
        echo "  VS Code: https://code.visualstudio.com/download"
        echo "  DevContainer CLI: npm install -g @devcontainers/cli"
        echo "  Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    success "All dependencies available"
}

check_devcontainer_config() {
    info "Checking DevContainer configuration..."
    
    if [[ ! -f "$DEVCONTAINER_JSON" ]]; then
        error "DevContainer configuration not found at: $DEVCONTAINER_JSON"
        echo ""
        echo "Please create a .devcontainer/devcontainer.json file first."
        echo "See: https://code.visualstudio.com/docs/devcontainers/containers"
        exit 1
    fi
    
    debug "Found DevContainer config: $DEVCONTAINER_JSON"
    
    # Validate JSON syntax
    if ! python3 -m json.tool "$DEVCONTAINER_JSON" >/dev/null 2>&1; then
        if ! node -e "JSON.parse(require('fs').readFileSync('$DEVCONTAINER_JSON', 'utf8'))" >/dev/null 2>&1; then
            error "Invalid JSON in DevContainer configuration"
            exit 1
        fi
    fi
    
    success "DevContainer configuration is valid"
}

get_container_info() {
    local container_name=""
    local container_id=""
    
    # Try to find container by workspace folder
    local workspace_hash
    workspace_hash=$(basename "$PROJECT_ROOT" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]//g')
    
    # Look for containers with the project name or devcontainer labels
    container_id=$(docker ps --format "{{.ID}} {{.Names}} {{.Labels}}" | \
                  grep -E "(${workspace_hash}|devcontainer.local_folder=${PROJECT_ROOT})" | \
                  head -n1 | \
                  awk '{print $1}') || true
    
    if [[ -n "$container_id" ]]; then
        container_name=$(docker inspect "$container_id" --format '{{.Name}}' | sed 's/^///')
        debug "Found running container: $container_name ($container_id)"
        echo "$container_id"
        return 0
    fi
    
    debug "No running DevContainer found"
    return 1
}

start_devcontainer() {
    info "Starting DevContainer..."
    
    cd "$PROJECT_ROOT"
    
    if [[ "$FORCE_RESTART" == "true" ]]; then
        warning "Force restart requested - stopping existing container"
        execute "devcontainer down --workspace-folder ."
    fi
    
    # Start the DevContainer
    execute "devcontainer up --workspace-folder ."
    
    # Wait a moment for container to be fully ready
    if [[ "$DRY_RUN" != "true" ]]; then
        sleep 2
    fi
    
    success "DevContainer started successfully"
}

launch_vscode() {
    info "Launching VS Code in DevContainer..."
    
    cd "$PROJECT_ROOT"
    
    # Use the modern approach: DevContainer CLI manages the container,
    # then launch VS Code normally - it will detect and connect to the container
    execute "code ."
    
    success "VS Code launched! It should automatically detect and connect to the DevContainer."
    
    # Provide helpful information
    echo ""
    info "VS Code DevContainer Integration:"
    echo "  • VS Code should show 'Dev Container: AI Code Forge' in the bottom-left corner"
    echo "  • If not connected, use Command Palette (Ctrl+Shift+P) > 'Dev Containers: Reopen in Container'"
    echo "  • Terminal sessions will run inside the container automatically"
    echo "  • Extensions specified in devcontainer.json will be installed automatically"
}

# Main execution
main() {
    echo "🚀 AI Code Forge DevContainer VS Code Launcher"
    echo ""
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Run validation checks
    check_dependencies
    check_devcontainer_config
    
    # Check if container is already running
    if container_id=$(get_container_info); then
        success "DevContainer is already running (ID: $container_id)"
        if [[ "$FORCE_RESTART" == "true" ]]; then
            start_devcontainer
        fi
    else
        start_devcontainer
    fi
    
    # Launch VS Code
    launch_vscode
    
    echo ""
    success "🎉 VS Code DevContainer launch complete!"
    
    if [[ "$DEBUG" == "true" ]]; then
        echo ""
        info "Debug Information:"
        echo "  Project Root: $PROJECT_ROOT"
        echo "  DevContainer Config: $DEVCONTAINER_JSON"
        echo "  Working Directory: $(pwd)"
        if command -v devcontainer >/dev/null 2>&1; then
            echo "  DevContainer Version: $(devcontainer --version)"
        fi
        if command -v code >/dev/null 2>&1; then
            echo "  VS Code Version: $(code --version | head -n1)"
        fi
    fi
}

# Handle interruption gracefully
trap 'echo ""; warning "Script interrupted by user"; exit 130' INT

# Execute main function
main "$@"