#!/bin/bash

# VS Code DevContainer Launch Script
# Launches VS Code directly into existing running DevContainer
# Uses DevContainer CLI - the official Microsoft automation tool

set -e

# ANSI color codes for output formatting
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Configuration
readonly REPOSITORY_NAME="ai-code-forge"
readonly WORKSPACE_PATH="/workspace"

# Print colored output
print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Show usage information
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Launch VS Code directly into running DevContainer"
    echo ""
    echo "Options:"
    echo "  --debug         Enable debug output"
    echo "  --dry-run       Preview actions without execution"
    echo "  --help          Show this help message"
    echo ""
    echo "Requirements:"
    echo "  - DevContainer CLI: npm install -g @devcontainers/cli"
    echo "  - Running DevContainer with repository label"
    echo "  - VS Code installed and available in PATH"
}

# Check if DevContainer CLI is installed
check_devcontainer_cli() {
    if ! command -v devcontainer >/dev/null 2>&1; then
        print_error "DevContainer CLI not found"
        echo ""
        echo "Install with: npm install -g @devcontainers/cli"
        echo "Or see: https://code.visualstudio.com/docs/devcontainers/devcontainer-cli"
        return 1
    fi
    
    local version=$(devcontainer --version 2>/dev/null || echo "unknown")
    print_success "DevContainer CLI found (version: $version)"
    return 0
}

# Check if VS Code is available
check_vscode() {
    if ! command -v code >/dev/null 2>&1; then
        print_error "VS Code CLI 'code' not found in PATH"
        echo ""
        echo "Make sure VS Code is installed and 'code' command is available"
        return 1
    fi
    
    print_success "VS Code CLI found"
    return 0
}

# Find running DevContainer by repository label
find_running_container() {
    local container_id
    
    # Use the exact label from devcontainer.json: my.repositoryName
    container_id=$(docker ps --filter "label=my.repositoryName=$REPOSITORY_NAME" --format "{{.ID}}" | head -1)
    
    if [ -z "$container_id" ]; then
        print_warning "No running DevContainer found with repository label"
        
        # Alternative: try finding any devcontainer-related container
        print_status "Searching for any DevContainer..."
        container_id=$(docker ps --filter "label=devcontainer.metadata" --format "{{.ID}} {{.Image}} {{.Labels}}" | head -1 | cut -d' ' -f1)
        
        if [ -z "$container_id" ]; then
            print_error "No running DevContainer found"
            echo ""
            echo "Make sure your DevContainer is running. You can start it by:"
            echo "1. Opening VS Code in this directory"
            echo "2. Using Command Palette: 'Dev Containers: Reopen in Container'"
            echo ""
            return 1
        else
            print_warning "Found generic DevContainer: $container_id"
        fi
    else
        print_success "Found running DevContainer: $container_id"
    fi
    
    echo "$container_id"
}

# Launch VS Code in DevContainer using DevContainer CLI
launch_vscode() {
    local container_id="$1"
    local current_dir="$(pwd)"
    
    print_status "Launching VS Code in DevContainer..."
    
    if [ "$DRY_RUN" = "true" ]; then
        print_warning "DRY RUN: Would execute:"
        echo "devcontainer exec --workspace-folder '$current_dir' --container-id '$container_id' code '$WORKSPACE_PATH'"
        return 0
    fi
    
    # Use DevContainer CLI to execute code command inside the container
    # This connects VS Code to the running container workspace
    if devcontainer exec --workspace-folder "$current_dir" --container-id "$container_id" code "$WORKSPACE_PATH" 2>/dev/null; then
        print_success "VS Code launched successfully!"
        print_status "VS Code should now be opening with the DevContainer workspace"
        return 0
    else
        print_warning "DevContainer CLI exec failed, trying alternative approach..."
        
        # Fallback: Use docker exec directly
        if docker exec "$container_id" code "$WORKSPACE_PATH" 2>/dev/null; then
            print_success "VS Code launched via docker exec!"
            return 0
        else
            print_error "Failed to launch VS Code in container"
            print_status "Falling back to normal VS Code launch..."
            
            # Final fallback: launch VS Code normally and let user manually connect
            if command -v code >/dev/null 2>&1; then
                code .
                print_warning "Opened VS Code - you may need to manually connect to DevContainer"
                echo ""
                echo "To connect to the running container:"
                echo "1. Use Command Palette (Ctrl+Shift+P)"
                echo "2. Run: 'Dev Containers: Attach to Running Container'"
                echo "3. Select container: $container_id"
                return 0
            else
                return 1
            fi
        fi
    fi
}

# Main function
main() {
    local debug=false
    local dry_run=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --debug)
                debug=true
                set -x
                shift
                ;;
            --dry-run)
                dry_run=true
                export DRY_RUN=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo ""
                show_usage
                exit 1
                ;;
        esac
    done
    
    print_status "Starting VS Code DevContainer launch process..."
    
    # Check prerequisites
    if ! check_vscode; then
        exit 1
    fi
    
    if ! check_devcontainer_cli; then
        print_warning "DevContainer CLI not available, will use fallback methods"
    fi
    
    # Find running container
    local container_id
    if ! container_id=$(find_running_container); then
        exit 1
    fi
    
    # Launch VS Code
    if ! launch_vscode "$container_id"; then
        print_error "Failed to launch VS Code in DevContainer"
        exit 1
    fi
    
    print_success "DevContainer VS Code launch completed!"
}

# Run main function with all arguments
main "$@"