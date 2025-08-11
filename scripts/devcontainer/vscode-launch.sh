#!/bin/bash

# vscode-launch.sh - Launch VS Code directly into running DevContainer
# Usage: vscode-launch.sh [workspace_directory]
#
# This script provides automated VS Code DevContainer integration with:
# - Hybrid container management (DevContainer CLI + direct attachment)
# - Robust error handling and fallback mechanisms
# - Cross-platform compatibility (Linux, macOS, Windows/WSL)
# - Integration with existing project infrastructure
# - Smart container detection and lifecycle management

set -euo pipefail

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Configuration variables
readonly SCRIPT_NAME="vscode-launch"
readonly SCRIPT_VERSION="1.0.0"
readonly MIN_DOCKER_VERSION="20.10.0"
readonly MIN_VSCODE_VERSION="1.60.0"

# Default configuration
WORKSPACE_DIR=""
CONTAINER_TIMEOUT=30
DEBUG_MODE="false"
FORCE_RESTART="false"
DRY_RUN="false"
VERBOSE="false"
FALLBACK_MODE="auto"

# Print functions
print_header() { echo -e "${CYAN}🚀 $SCRIPT_NAME v$SCRIPT_VERSION${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ ERROR: $1${NC}" >&2; }
print_warning() { echo -e "${YELLOW}⚠️  WARNING: $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_debug() { [[ "$DEBUG_MODE" == "true" ]] && echo -e "${CYAN}🔧 DEBUG: $1${NC}"; }
print_step() { echo -e "${CYAN}📝 $1${NC}"; }

# Help function
show_help() {
    cat << EOF
$SCRIPT_NAME - Launch VS Code directly into running DevContainer

USAGE:
    $SCRIPT_NAME [OPTIONS] [WORKSPACE_DIRECTORY]

OPTIONS:
    -h, --help              Show this help message
    -v, --verbose           Enable verbose output
    -d, --debug             Enable debug mode with detailed logging
    -f, --force-restart     Force restart DevContainer if already running
    -t, --timeout SECONDS   Container startup timeout (default: $CONTAINER_TIMEOUT)
    --dry-run              Show what would be executed without running
    --fallback MODE        Fallback behavior: auto, vscode, manual (default: auto)

ARGUMENTS:
    WORKSPACE_DIRECTORY     Directory containing .devcontainer/ (default: current dir)

EXAMPLES:
    $SCRIPT_NAME                    # Launch in current directory
    $SCRIPT_NAME /path/to/project   # Launch in specific project
    $SCRIPT_NAME --debug            # Launch with debug output
    $SCRIPT_NAME --force-restart    # Restart container before launch
    $SCRIPT_NAME --dry-run          # Preview actions without execution

DESCRIPTION:
    This script automatically launches VS Code attached to a running DevContainer:
    
    1. Validates DevContainer configuration and dependencies
    2. Detects or starts the appropriate DevContainer
    3. Launches VS Code with direct container attachment
    4. Provides intelligent fallbacks if direct attachment fails
    
    The script integrates with existing DevContainer infrastructure and follows
    established patterns from the ai-code-forge project for reliability.

REQUIREMENTS:
    - Docker (v$MIN_DOCKER_VERSION+)
    - VS Code (v$MIN_VSCODE_VERSION+) with Dev Containers extension
    - DevContainer CLI (npm install -g @devcontainers/cli)
    - Git (for repository detection)

EOF
}

# Dependency validation functions
check_command() {
    local cmd="$1"
    local description="${2:-$cmd}"
    
    print_debug "Checking for command: $cmd"
    
    if ! command -v "$cmd" &> /dev/null; then
        print_error "$description is not installed or not in PATH"
        return 1
    fi
    
    print_debug "✓ Found $description: $(which "$cmd")"
    return 0
}

check_docker_version() {
    local docker_version
    docker_version=$(docker --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "0.0.0")
    
    print_debug "Docker version: $docker_version"
    
    # Simple version comparison (assumes semantic versioning)
    if [[ $(printf '%s\n' "$MIN_DOCKER_VERSION" "$docker_version" | sort -V | head -1) != "$MIN_DOCKER_VERSION" ]]; then
        print_error "Docker version $docker_version is too old (minimum: $MIN_DOCKER_VERSION)"
        return 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        return 1
    fi
    
    return 0
}

check_vscode_version() {
    local vscode_version
    
    # Try multiple VS Code command variations
    local vscode_cmd=""
    for cmd in "code" "code-insiders" "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"; do
        if command -v "$cmd" &> /dev/null; then
            vscode_cmd="$cmd"
            break
        fi
    done
    
    if [[ -z "$vscode_cmd" ]]; then
        print_error "VS Code is not installed or not in PATH"
        return 1
    fi
    
    vscode_version=$($vscode_cmd --version 2>/dev/null | head -1 || echo "0.0.0")
    print_debug "VS Code version: $vscode_version"
    
    # Check for Dev Containers extension (simplified check)
    if ! $vscode_cmd --list-extensions 2>/dev/null | grep -q "ms-vscode-remote.remote-containers"; then
        print_warning "Dev Containers extension may not be installed"
        print_info "Install with: $vscode_cmd --install-extension ms-vscode-remote.remote-containers"
    fi
    
    return 0
}

validate_dependencies() {
    print_step "Validating dependencies..."
    
    local deps_ok=true
    
    check_command "docker" "Docker" || deps_ok=false
    check_command "git" "Git" || deps_ok=false
    
    # VS Code check
    check_vscode_version || deps_ok=false
    
    # Docker version check
    check_docker_version || deps_ok=false
    
    # DevContainer CLI check (optional but recommended)
    if ! check_command "devcontainer" "DevContainer CLI"; then
        print_warning "DevContainer CLI not found. Install with: npm install -g @devcontainers/cli"
        print_info "Script will use fallback mechanisms without DevContainer CLI"
    fi
    
    if [[ "$deps_ok" == "false" ]]; then
        print_error "Dependency validation failed. Please install missing dependencies."
        exit 1
    fi
    
    print_success "All dependencies validated"
}

# DevContainer validation functions
validate_devcontainer_config() {
    local workspace_dir="$1"
    local devcontainer_config="$workspace_dir/.devcontainer/devcontainer.json"
    
    print_debug "Checking DevContainer config: $devcontainer_config"
    
    if [[ ! -f "$devcontainer_config" ]]; then
        print_error "No devcontainer.json found in $workspace_dir/.devcontainer/"
        print_info "Initialize DevContainer with: code --install-extension ms-vscode-remote.remote-containers"
        return 1
    fi
    
    # Basic JSON validation
    if ! jq empty "$devcontainer_config" 2>/dev/null; then
        print_error "Invalid JSON in $devcontainer_config"
        return 1
    fi
    
    # Extract container name for better error messages
    local container_name
    container_name=$(jq -r '.name // "devcontainer"' "$devcontainer_config" 2>/dev/null || echo "devcontainer")
    print_debug "DevContainer name: $container_name"
    
    print_success "DevContainer configuration valid"
    return 0
}

# Repository and environment detection
detect_repository_info() {
    local workspace_dir="$1"
    local repo_name=""
    local repo_root=""
    
    # Try to get repository information
    if git -C "$workspace_dir" rev-parse --git-dir &>/dev/null; then
        repo_root=$(git -C "$workspace_dir" rev-parse --show-toplevel 2>/dev/null || echo "")
        if [[ -n "$repo_root" ]]; then
            repo_name=$(basename "$repo_root")
            print_debug "Git repository detected: $repo_name at $repo_root"
        fi
    fi
    
    # Fallback to directory name
    if [[ -z "$repo_name" ]]; then
        repo_name=$(basename "$(realpath "$workspace_dir")")
        print_debug "Using directory name as repository: $repo_name"
    fi
    
    echo "$repo_name"
}

# Container detection and management
find_devcontainer() {
    local workspace_dir="$1"
    local repo_name
    repo_name=$(detect_repository_info "$workspace_dir")
    
    print_step "Detecting DevContainer for $repo_name..."
    
    # Multiple detection strategies
    local container_id=""
    
    # Strategy 1: DevContainer CLI if available
    if command -v devcontainer &> /dev/null; then
        print_debug "Using DevContainer CLI for detection"
        local container_info
        if container_info=$(devcontainer exec --workspace-folder "$workspace_dir" echo "container-detected" 2>/dev/null); then
            # Extract container ID from docker ps (DevContainer CLI doesn't expose it directly)
            container_id=$(docker ps --filter "label=devcontainer.local_folder=$(realpath "$workspace_dir")" --format "{{.ID}}" | head -1)
        fi
    fi
    
    # Strategy 2: Label-based detection (following existing patterns)
    if [[ -z "$container_id" ]]; then
        print_debug "Using label-based container detection"
        local workspace_realpath
        workspace_realpath=$(realpath "$workspace_dir")
        
        # Try multiple label patterns for compatibility
        for label_pattern in \
            "devcontainer.local_folder=$workspace_realpath" \
            "my.repositoryName=$repo_name" \
            "devcontainer.config_file=$workspace_realpath/.devcontainer/devcontainer.json"; do
            
            print_debug "Searching with label: $label_pattern"
            container_id=$(docker ps --filter "label=$label_pattern" --format "{{.ID}}" | head -1)
            [[ -n "$container_id" ]] && break
        done
    fi
    
    # Strategy 3: Pattern matching on container names (least reliable)
    if [[ -z "$container_id" ]]; then
        print_debug "Using name pattern matching"
        container_id=$(docker ps --format "{{.ID}} {{.Names}}" | grep -i "$repo_name" | head -1 | cut -d' ' -f1 || true)
    fi
    
    if [[ -n "$container_id" ]]; then
        # Validate container is accessible and has expected structure
        if docker exec "$container_id" test -d "/workspaces" 2>/dev/null; then
            print_success "Found DevContainer: $container_id"
            print_debug "Container validated with /workspaces directory"
            echo "$container_id"
            return 0
        else
            print_warning "Found container $container_id but it doesn't appear to be a DevContainer"
            container_id=""
        fi
    fi
    
    print_info "No running DevContainer found for $repo_name"
    return 1
}

start_devcontainer() {
    local workspace_dir="$1"
    local repo_name
    repo_name=$(detect_repository_info "$workspace_dir")
    
    print_step "Starting DevContainer for $repo_name..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_info "DRY RUN: Would start DevContainer with: devcontainer up --workspace-folder $workspace_dir"
        return 0
    fi
    
    # Use DevContainer CLI if available
    if command -v devcontainer &> /dev/null; then
        print_debug "Starting container with DevContainer CLI"
        
        local start_cmd=("devcontainer" "up" "--workspace-folder" "$workspace_dir")
        if [[ "$VERBOSE" == "true" ]]; then
            start_cmd+=(--log-level "debug")
        fi
        
        print_debug "Executing: ${start_cmd[*]}"
        
        if "${start_cmd[@]}"; then
            print_success "DevContainer started successfully"
            
            # Wait for container to be ready
            print_info "Waiting for container to be ready..."
            local attempts=0
            while [[ $attempts -lt $CONTAINER_TIMEOUT ]]; do
                if find_devcontainer "$workspace_dir" >/dev/null; then
                    break
                fi
                sleep 1
                ((attempts++))
            done
            
            if [[ $attempts -ge $CONTAINER_TIMEOUT ]]; then
                print_error "Container startup timeout after ${CONTAINER_TIMEOUT}s"
                return 1
            fi
            
            return 0
        else
            print_error "Failed to start DevContainer with CLI"
            return 1
        fi
    else
        print_error "DevContainer CLI not available and no running container found"
        print_info "Please install DevContainer CLI: npm install -g @devcontainers/cli"
        return 1
    fi
}

# VS Code launch functions
construct_vscode_uri() {
    local container_id="$1"
    local workspace_dir="$2"
    local workspace_name
    workspace_name=$(basename "$(realpath "$workspace_dir")")
    
    # Construct the remote URI for VS Code
    local workspace_path="/workspaces/$workspace_name"
    local vscode_uri="vscode-remote://attached-container+${container_id}${workspace_path}"
    
    print_debug "Constructed VS Code URI: $vscode_uri"
    echo "$vscode_uri"
}

launch_vscode_in_container() {
    local container_id="$1"
    local workspace_dir="$2"
    
    print_step "Launching VS Code in container $container_id..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        local vscode_uri
        vscode_uri=$(construct_vscode_uri "$container_id" "$workspace_dir")
        print_info "DRY RUN: Would execute: code --folder-uri $vscode_uri"
        return 0
    fi
    
    # Find VS Code command
    local vscode_cmd=""
    for cmd in "code" "code-insiders"; do
        if command -v "$cmd" &> /dev/null; then
            vscode_cmd="$cmd"
            break
        fi
    done
    
    if [[ -z "$vscode_cmd" ]]; then
        print_error "VS Code command not found"
        return 1
    fi
    
    # Validate container is still running
    if ! docker ps --format "{{.ID}}" | grep -q "^$container_id"; then
        print_error "Container $container_id is no longer running"
        return 1
    fi
    
    # Construct and execute VS Code launch
    local vscode_uri
    vscode_uri=$(construct_vscode_uri "$container_id" "$workspace_dir")
    
    print_debug "Launching with command: $vscode_cmd --folder-uri $vscode_uri"
    print_info "Opening VS Code in DevContainer..."
    
    # Launch VS Code in background to avoid blocking
    if "$vscode_cmd" --folder-uri "$vscode_uri" &>/dev/null & then
        print_success "VS Code launched successfully in DevContainer"
        return 0
    else
        print_error "Failed to launch VS Code with container URI"
        return 1
    fi
}

# Fallback mechanisms
execute_fallback() {
    local workspace_dir="$1"
    local fallback_mode="$2"
    
    print_warning "Executing fallback mode: $fallback_mode"
    
    case "$fallback_mode" in
        "vscode")
            print_info "Opening VS Code in standard mode..."
            if [[ "$DRY_RUN" == "true" ]]; then
                print_info "DRY RUN: Would execute: code $workspace_dir"
            else
                code "$workspace_dir"
                print_info "Use 'Remote-Containers: Reopen in Container' from Command Palette (Ctrl+Shift+P)"
            fi
            ;;
        "manual")
            print_info "Manual instructions:"
            echo "1. Open VS Code: code $workspace_dir"
            echo "2. Open Command Palette (Ctrl+Shift+P or Cmd+Shift+P)"
            echo "3. Run: 'Dev Containers: Reopen in Container'"
            echo "4. Wait for container setup to complete"
            ;;
        "auto"|*)
            # Try VS Code first, then manual instructions
            if command -v code &> /dev/null; then
                execute_fallback "$workspace_dir" "vscode"
            else
                execute_fallback "$workspace_dir" "manual"
            fi
            ;;
    esac
}

# Main execution logic
main() {
    print_header
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verbose)
                VERBOSE="true"
                shift
                ;;
            -d|--debug)
                DEBUG_MODE="true"
                VERBOSE="true"
                shift
                ;;
            -f|--force-restart)
                FORCE_RESTART="true"
                shift
                ;;
            -t|--timeout)
                CONTAINER_TIMEOUT="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN="true"
                shift
                ;;
            --fallback)
                FALLBACK_MODE="$2"
                shift 2
                ;;
            -*)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
            *)
                WORKSPACE_DIR="$1"
                shift
                ;;
        esac
    done
    
    # Set default workspace directory
    if [[ -z "$WORKSPACE_DIR" ]]; then
        WORKSPACE_DIR="$(pwd)"
    fi
    
    # Resolve to absolute path
    WORKSPACE_DIR=$(realpath "$WORKSPACE_DIR")
    print_info "Working with directory: $WORKSPACE_DIR"
    
    # Validate inputs
    if [[ ! -d "$WORKSPACE_DIR" ]]; then
        print_error "Workspace directory does not exist: $WORKSPACE_DIR"
        exit 1
    fi
    
    # Main execution flow
    print_step "Starting DevContainer VS Code launch process..."
    
    # 1. Validate dependencies
    validate_dependencies
    
    # 2. Validate DevContainer configuration
    validate_devcontainer_config "$WORKSPACE_DIR"
    
    # 3. Find or start DevContainer
    local container_id=""
    if container_id=$(find_devcontainer "$WORKSPACE_DIR"); then
        print_info "Using existing container: $container_id"
        
        # Force restart if requested
        if [[ "$FORCE_RESTART" == "true" ]]; then
            print_warning "Force restart requested, stopping existing container..."
            if [[ "$DRY_RUN" == "true" ]]; then
                print_info "DRY RUN: Would stop container $container_id"
            else
                docker stop "$container_id" || true
            fi
            container_id=""
        fi
    fi
    
    # Start container if needed
    if [[ -z "$container_id" ]]; then
        if start_devcontainer "$WORKSPACE_DIR"; then
            container_id=$(find_devcontainer "$WORKSPACE_DIR")
        else
            print_error "Failed to start DevContainer"
            execute_fallback "$WORKSPACE_DIR" "$FALLBACK_MODE"
            exit 1
        fi
    fi
    
    # 4. Launch VS Code
    if [[ -n "$container_id" ]]; then
        if launch_vscode_in_container "$container_id" "$WORKSPACE_DIR"; then
            print_success "DevContainer VS Code launch completed successfully!"
        else
            print_warning "VS Code launch failed, trying fallback..."
            execute_fallback "$WORKSPACE_DIR" "$FALLBACK_MODE"
        fi
    else
        print_error "No container available for VS Code launch"
        execute_fallback "$WORKSPACE_DIR" "$FALLBACK_MODE"
        exit 1
    fi
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi