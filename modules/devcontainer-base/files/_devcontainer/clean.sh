#!/bin/bash

# DevContainer Cleanup Script
# Removes all stale devcontainers, images, and volumes for the current repository
# Handles the common issue where volumes can't be deleted due to container dependencies
# Supports --dry-run mode to preview operations without executing them

set -e

# Parse command line arguments
DRY_RUN=false
for arg in "$@"; do
    case $arg in
        --dry-run|-n)
            DRY_RUN=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dry-run, -n    Show what would be done without executing destructive operations"
            echo "  --help, -h       Show this help message"
            echo ""
            echo "Cleans up all DevContainer resources (containers, images, volumes) for the current repository."
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Helper function to execute or simulate commands based on dry-run mode
execute_command() {
    local cmd="$1"
    local description="$2"
    
    if [ "$DRY_RUN" = true ]; then
        echo "  [DRY-RUN] Would execute: $cmd"
    else
        eval "$cmd"
    fi
}

# Dynamically determine repository name
if ! command -v git &> /dev/null; then
    echo "❌ Error: git is not installed or not in PATH"
    exit 1
fi

# Get the repository root directory
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Extract repository name from the path
REPO_NAME=$(basename "$REPO_ROOT")

# Try to get the full repository name (org/repo) using gh CLI if available
if command -v gh &> /dev/null; then
    # Get the remote repository name in format owner/repo
    GH_REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || true)
    if [ -n "$GH_REPO" ]; then
        # Use just the repo name part for container/volume naming
        REPO_NAME=$(echo "$GH_REPO" | cut -d'/' -f2)
        echo "📦 Detected GitHub repository: $GH_REPO"
    fi
else
    echo "⚠️  Warning: gh CLI not available, using local repository name: $REPO_NAME"
fi

# Use the same name for volume as repository
VOLUME_NAME="$REPO_NAME"

if [ "$DRY_RUN" = true ]; then
    echo "🧹 DevContainer Cleanup Script for $REPO_NAME [DRY-RUN MODE]"
    echo "============================================================"
    echo "⚠️  DRY-RUN: No destructive operations will be performed"
else
    echo "🧹 DevContainer Cleanup Script for $REPO_NAME"
    echo "================================================"
fi

# Skip confirmation for automated use

echo "🔍 Finding containers and volumes..."

# Function to stop and remove containers using a volume
cleanup_volume_containers() {
    local volume_name="$1"
    echo "🔍 Finding containers using volume: $volume_name"
    
    # Get container IDs that use this volume by inspecting their mounts
    local container_ids=$(docker ps -a --format "{{.ID}}" | while read id; do
        docker inspect "$id" --format '{{range .Mounts}}{{if eq .Type "volume"}}{{if eq .Name "'"$volume_name"'"}}{{$.ID}}{{end}}{{end}}{{end}}' 2>/dev/null | grep -v '^$'
    done || true)
    
    if [ -n "$container_ids" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo "  [DRY-RUN] Would stop containers using volume $volume_name:"
            echo "$container_ids" | while read id; do
                echo "    - Container ID: $id"
            done
            echo "  [DRY-RUN] Would remove containers using volume $volume_name"
        else
            echo "🛑 Stopping containers using volume $volume_name..."
            echo "$container_ids" | xargs -r docker stop 2>/dev/null || true
            
            echo "🗑️  Removing containers using volume $volume_name..."
            echo "$container_ids" | xargs -r docker rm -f 2>/dev/null || true
        fi
    else
        echo "✅ No containers found using volume $volume_name"
    fi
}

# 1. Stop and remove all containers related to this repo
echo
echo "📦 Step 1: Cleaning up containers..."
CONTAINERS=$(docker ps -a --filter "label=devcontainer.local_folder" --format "{{.ID}} {{.Label \"devcontainer.local_folder\"}}" 2>/dev/null | grep "$REPO_NAME" | cut -d' ' -f1 || true)

if [ -n "$CONTAINERS" ]; then
    if [ "$DRY_RUN" = true ]; then
        echo "  [DRY-RUN] Would stop and remove devcontainers for $REPO_NAME:"
        echo "$CONTAINERS" | while read id; do
            echo "    - Container ID: $id"
        done
    else
        echo "🛑 Stopping devcontainers for $REPO_NAME..."
        echo "$CONTAINERS" | xargs -r docker stop 2>/dev/null || true
        
        echo "🗑️  Removing devcontainers for $REPO_NAME..."
        echo "$CONTAINERS" | xargs -r docker rm -f 2>/dev/null || true
        echo "✅ Devcontainers cleaned up"
    fi
else
    echo "✅ No devcontainers found for $REPO_NAME"
fi

# 2. Remove any additional containers that might be using our volume
cleanup_volume_containers "$VOLUME_NAME"

# 3. Remove images related to devcontainers
echo
echo "🖼️  Step 2: Cleaning up images..."
# Look for images with devcontainer label OR images whose repository contains the repo name
# Check for images whose repository name contains our repo name (VSCode devcontainer naming convention)
IMAGES=$(docker images --format "{{.Repository}}:{{.Tag}} {{.ID}}" 2>/dev/null | grep -i "vsc-${REPO_NAME}-" | cut -d' ' -f2 | sort -u || true)

if [ -n "$IMAGES" ]; then
    if [ "$DRY_RUN" = true ]; then
        echo "  [DRY-RUN] Would remove devcontainer images for $REPO_NAME:"
        echo "$IMAGES" | while read id; do
            echo "    - Image ID: $id"
        done
    else
        echo "🗑️  Removing devcontainer images for $REPO_NAME..."
        echo "$IMAGES" | xargs -r docker rmi -f 2>/dev/null || true
        echo "✅ Images cleaned up"
    fi
else
    echo "✅ No devcontainer images found for $REPO_NAME"
fi

# 4. Remove the volume (this should work now that containers are gone)
echo
echo "💾 Step 3: Cleaning up volumes..."
if docker volume ls --format "{{.Name}}" | grep -q "^${VOLUME_NAME}$"; then
    if [ "$DRY_RUN" = true ]; then
        echo "  [DRY-RUN] Would remove volume: $VOLUME_NAME"
    else
        echo "🗑️  Removing volume: $VOLUME_NAME..."
        if docker volume rm "$VOLUME_NAME" 2>/dev/null; then
            echo "✅ Volume $VOLUME_NAME removed successfully"
        else
            echo "❌ Failed to remove volume $VOLUME_NAME"
            echo "   Checking for remaining containers..."
            
            # Last resort - find any container still using the volume
            docker ps -a --format "{{.ID}}" | while read id; do
                if docker inspect "$id" --format '{{range .Mounts}}{{if eq .Type "volume"}}{{if eq .Name "'"$VOLUME_NAME"'"}}found{{end}}{{end}}{{end}}' 2>/dev/null | grep -q "found"; then
                    docker ps -a --filter "id=$id" --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}"
                fi
            done
            echo "   Try inspecting containers manually to find which are using volume: $VOLUME_NAME"
            echo "   Then manually remove those containers and retry"
            exit 1
        fi
    fi
else
    echo "✅ Volume $VOLUME_NAME not found (already cleaned)"
fi

# 5. Clean up any dangling volumes and images
echo
echo "🧽 Step 4: Cleaning up dangling resources..."
if [ "$DRY_RUN" = true ]; then
    echo "  [DRY-RUN] Would remove dangling volumes with: docker volume prune -f"
    echo "  [DRY-RUN] Would remove dangling images with: docker image prune -f"
else
    echo "🗑️  Removing dangling volumes..."
    docker volume prune -f >/dev/null 2>&1 || true
    
    echo "🗑️  Removing dangling images..."
    docker image prune -f >/dev/null 2>&1 || true
fi

echo
if [ "$DRY_RUN" = true ]; then
    echo "🔍 Dry-run completed!"
    echo "   No changes were made. Re-run without --dry-run to execute the cleanup."
else
    echo "🎉 Cleanup completed successfully!"
    echo "   All containers, images, and volumes for $REPO_NAME have been removed"
    echo "   Next devcontainer build will start fresh"
fi
