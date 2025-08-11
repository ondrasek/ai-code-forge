#!/bin/bash

# VS Code DevContainer Direct Launch Script
# Launches VS Code locally and connects to running DevContainer

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# Use gh to get repository name, fallback to basename if gh unavailable
if command -v gh &> /dev/null; then
    PROJECT_NAME=$(gh repo view --json name -q ".name" 2>/dev/null || basename "$PROJECT_ROOT")
else
    PROJECT_NAME=$(basename "$PROJECT_ROOT")
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Debug flag
DEBUG=false
DRY_RUN=false
SPECIFIC_METHOD=""

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
    --method N      Use specific connection method (1-4)
    --list-methods  Show available connection methods
    --help         Show this help message

EXAMPLES:
    $0                    # Try all methods in sequence
    $0 --method 2        # Use only method 2 (direct container ID)
    $0 --list-methods    # Show all available methods
    $0 --debug --method 1 # Debug method 1 specifically

METHODS:
    1: JSON-encoded dev-container configuration
    2: Direct container ID connection
    3: Attached container scheme
    4: Container name with JSON structure

REQUIREMENTS:
    - VS Code with Remote-Containers extension installed
    - Docker running with DevContainer already started
    - DevContainer must have label: my.repositoryName=$PROJECT_NAME

EOF
}

list_methods() {
    cat << EOF
Available VS Code DevContainer Connection Methods:

METHOD 1: JSON-encoded dev-container configuration
  - Creates comprehensive JSON config with hostPath and configFile
  - Hex-encodes the JSON for URI compatibility
  - Most complete but complex approach

METHOD 2: Direct container ID connection
  - Uses container ID directly in URI scheme
  - Simple and often most reliable
  - Format: vscode-remote://dev-container+CONTAINER_ID

METHOD 3: Attached container scheme
  - Uses attached-container URI scheme
  - Alternative approach for direct container access
  - Format: vscode-remote://attached-container+CONTAINER_ID

METHOD 4: Container name with JSON structure
  - Creates JSON config using container name
  - Hex-encodes containerName-based configuration
  - Fallback for name-based container identification

USAGE:
  $0 --method 2    # Use method 2 only
  $0               # Try all methods in sequence (2,1,4,3)

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
        --method)
            if [[ -z "$2" ]] || [[ ! "$2" =~ ^[1-4]$ ]]; then
                error "Method must be 1, 2, 3, or 4"
                exit 1
            fi
            SPECIFIC_METHOD="$2"
            shift 2
            ;;
        --list-methods)
            list_methods
            exit 0
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
    log "Method 1: VS Code --folder-uri with JSON-encoded dev-container"
    
    # Detect devcontainer configuration file
    local config_file="$PROJECT_ROOT/.devcontainer/devcontainer.json"
    if [[ ! -f "$config_file" ]]; then
        config_file="$PROJECT_ROOT/.devcontainer.json"
        if [[ ! -f "$config_file" ]]; then
            warn "No devcontainer.json found, using default configuration"
            config_file="$PROJECT_ROOT/.devcontainer/devcontainer.json"
        fi
    fi
    
    # Create JSON structure for remote authority
    local json_config
    json_config=$(cat <<EOF
{
  "containerName": "$(docker ps --filter "id=$container_id" --format "{{.Names}}")",
  "configFile": {
    "file": "$config_file"
  },
  "workspaceMount": "source=${PROJECT_ROOT},target=/workspace,type=bind,consistency=cached",
  "workspaceFolder": "/workspace"
}
EOF
    )
    
    # Hex-encode the JSON configuration
    local hex_encoded
    hex_encoded=$(printf "%s" "$json_config" | xxd -p | tr -d '\n')
    
    local dev_container_uri="vscode-remote://dev-container+${hex_encoded}/workspace"
    
    if [[ "$DRY_RUN" == true ]]; then
        echo "DRY RUN: code --folder-uri \"$dev_container_uri\""
        echo "JSON Config: $json_config"
        echo "Hex Encoded: $hex_encoded"
        return 0
    fi
    
    code --folder-uri "$dev_container_uri"
}

launch_vscode_method2() {
    local container_id=$1
    log "Method 2: VS Code --folder-uri with container scheme"
    
    if [[ "$DRY_RUN" == true ]]; then
        echo "DRY RUN: code --folder-uri \"vscode-remote://dev-container+$container_id/workspace\""
        return 0
    fi
    
    code --folder-uri "vscode-remote://dev-container+$container_id/workspace"
}

launch_vscode_method3() {
    local container_id=$1
    log "Method 3: VS Code with container ID direct attach"
    
    # Use container ID directly with attach-to-running-container approach
    local dev_container_uri="vscode-remote://attached-container+${container_id}/workspace"
    
    if [[ "$DRY_RUN" == true ]]; then
        echo "DRY RUN: code --folder-uri \"$dev_container_uri\""
        return 0
    fi
    
    code --folder-uri "$dev_container_uri"
}

launch_vscode_method4() {
    local container_id=$1
    log "Method 4: VS Code with proper container name JSON encoding"
    
    local container_name
    container_name=$(docker ps --filter "id=$container_id" --format "{{.Names}}")
    
    # Create proper JSON structure for container name approach
    local json_config
    json_config=$(cat <<EOF
{
  "containerName": "$container_name",
  "localDocker": true,
  "workspaceFolder": "/workspace"
}
EOF
    )
    
    # Hex-encode the JSON configuration
    local hex_encoded
    hex_encoded=$(printf "%s" "$json_config" | xxd -p | tr -d '\n')
    
    local dev_container_uri="vscode-remote://dev-container+${hex_encoded}/workspace"
    
    if [[ "$DRY_RUN" == true ]]; then
        echo "DRY RUN: code --folder-uri \"$dev_container_uri\""
        echo "JSON Config: $json_config"
        echo "Hex Encoded: $hex_encoded"
        return 0
    fi
    
    code --folder-uri "$dev_container_uri"
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
    
    local success=false
    
    if [[ -n "$SPECIFIC_METHOD" ]]; then
        # Use specific method requested by user
        local method_func="launch_vscode_method${SPECIFIC_METHOD}"
        info "Using specific method: $method_func"
        
        if $method_func "$container_id"; then
            info "Successfully launched VS Code using $method_func"
            success=true
        else
            error "Method $SPECIFIC_METHOD failed"
            error ""
            error "Try a different method with --method [1-4] or run --list-methods"
            error "Or run without --method to try all methods sequentially"
            exit 1
        fi
    else
        # Try different connection methods in order of likelihood to work
        # Method 2 (direct container ID) usually works best, followed by JSON approaches
        local methods=(launch_vscode_method2 launch_vscode_method1 launch_vscode_method4 launch_vscode_method3)
        
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
            error "Try a specific method: $0 --method [1-4]"
            error "Or manual fallback:"
            error "  1. Run: code ."
            error "  2. Use Command Palette: Remote-Containers: Attach to Running Container"
            error "  3. Select container: $container_id"
            error "  4. Open folder: /workspace"
            exit 1
        fi
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