#!/bin/bash

# VS Code DevContainer Direct Launch Script
# Launches VS Code locally and connects to running DevContainer

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_NAME=$(basename "$PROJECT_ROOT")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Debug flag
DEBUG=false
DRY_RUN=false

show_help() {
    cat << EOF
VS Code DevContainer Direct Launch Script

USAGE:
    $0 [OPTIONS]

DESCRIPTION:
    Launches VS Code locally and connects it directly to a running DevContainer,
    avoiding the manual "Reopen in DevContainer" step.

OPTIONS:
    --debug         Enable debug output
    --dry-run       Show what would be done without executing
    --help         Show this help message

EXAMPLES:
    $0                    # Launch VS Code connected to DevContainer
    $0 --debug           # Launch with debug output
    $0 --dry-run         # Preview actions without execution

REQUIREMENTS:
    - VS Code with Remote-Containers extension installed
    - Docker running with DevContainer already started
    - DevContainer must have label: my.repositoryName=$PROJECT_NAME

EOF
}

log() {
    if [[ "$DEBUG" == true ]]; then
        echo -e "${BLUE}[DEBUG]${NC} $*" >&2
    fi
}

info() {
    echo -e "${GREEN}[INFO]${NC} $*" >&2
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $*" >&2
}

error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --debug)
            DEBUG=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validation functions
check_dependencies() {
    log "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
        return 1
    fi
    
    if ! command -v code &> /dev/null; then
        error "VS Code CLI 'code' command is not installed or not in PATH"
        error "Install VS Code and ensure it's added to PATH"
        return 1
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker is not running or not accessible"
        return 1
    fi
    
    log "All dependencies satisfied"
    return 0
}

# Container detection using project-specific label
detect_devcontainer() {
    log "Detecting DevContainer for project: $PROJECT_NAME"
    
    # Find container with the repository label
    local container_id
    container_id=$(docker ps --filter "label=my.repositoryName=$PROJECT_NAME" --format "{{.ID}}" | head -1)
    
    if [[ -z "$container_id" ]]; then
        log "No container found with label my.repositoryName=$PROJECT_NAME"
        
        # Fallback: look for containers with project name in the name
        container_id=$(docker ps --filter "name=.*$PROJECT_NAME.*" --format "{{.ID}}" | head -1)
        
        if [[ -z "$container_id" ]]; then
            return 1
        fi
        
        warn "Found container by name pattern instead of label: $container_id"
    else
        log "Found container with proper label: $container_id"
    fi
    
    # Get container details
    local container_name
    container_name=$(docker ps --filter "id=$container_id" --format "{{.Names}}")
    local container_image
    container_image=$(docker ps --filter "id=$container_id" --format "{{.Image}}")
    
    info "Found DevContainer:"
    info "  ID: $container_id"
    info "  Name: $container_name"
    info "  Image: $container_image"
    
    echo "$container_id"
    return 0
}

# Test different VS Code connection methods
launch_vscode_method1() {
    local container_id=$1
    log "Method 1: VS Code --remote attached-container"
    
    if [[ "$DRY_RUN" == true ]]; then
        echo "DRY RUN: code --remote attached-container+$container_id /workspace"
        return 0
    fi
    
    code --remote "attached-container+$container_id" /workspace
}

launch_vscode_method2() {
    local container_id=$1
    log "Method 2: VS Code --folder-uri with container scheme"
    
    if [[ "$DRY_RUN" == true ]]; then
        echo "DRY RUN: code --folder-uri \"vscode-remote://attached-container+$container_id/workspace\""
        return 0
    fi
    
    code --folder-uri "vscode-remote://attached-container+$container_id/workspace"
}

launch_vscode_method3() {
    local container_id=$1
    log "Method 3: VS Code with container name"
    
    local container_name
    container_name=$(docker ps --filter "id=$container_id" --format "{{.Names}}")
    
    if [[ "$DRY_RUN" == true ]]; then
        echo "DRY RUN: code --remote attached-container+$container_name /workspace"
        return 0
    fi
    
    code --remote "attached-container+$container_name" /workspace
}

# Main execution function
main() {
    info "VS Code DevContainer Direct Launch"
    info "Project: $PROJECT_NAME"
    info "Working directory: $PROJECT_ROOT"
    
    # Check dependencies
    if ! check_dependencies; then
        exit 1
    fi
    
    # Detect running DevContainer
    local container_id
    if ! container_id=$(detect_devcontainer); then
        error "No running DevContainer found for project '$PROJECT_NAME'"
        error ""
        error "Make sure:"
        error "  1. DevContainer is running (try: code . and reopen in container)"
        error "  2. Container has proper label: my.repositoryName=$PROJECT_NAME"
        error "  3. Docker is running and accessible"
        error ""
        error "To debug, try: docker ps --filter \"label=my.repositoryName=$PROJECT_NAME\""
        exit 1
    fi
    
    info "Attempting to launch VS Code connected to DevContainer..."
    
    # Try different connection methods in order of likelihood to work
    local methods=(launch_vscode_method1 launch_vscode_method2 launch_vscode_method3)
    local success=false
    
    for method in "${methods[@]}"; do
        info "Trying $method..."
        
        if $method "$container_id"; then
            info "Successfully launched VS Code using $method"
            success=true
            break
        else
            warn "$method failed, trying next method..."
        fi
    done
    
    if [[ "$success" != true ]]; then
        error "All VS Code connection methods failed"
        error ""
        error "Manual fallback:"
        error "  1. Run: code ."
        error "  2. Use Command Palette: Remote-Containers: Attach to Running Container"
        error "  3. Select container: $container_id"
        error "  4. Open folder: /workspace"
        exit 1
    fi
    
    info "VS Code should now be connected to your DevContainer!"
    
    if [[ "$DRY_RUN" != true ]]; then
        # Give VS Code a moment to start
        sleep 2
        
        # Optionally show container status
        if [[ "$DEBUG" == true ]]; then
            info "Container status:"
            docker ps --filter "id=$container_id" --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Ports}}"
        fi
    fi
}

# Change to project root before execution
cd "$PROJECT_ROOT"
main "$@"