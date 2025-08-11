#!/bin/bash

# DevContainer Cleanup Script
# Removes all stale devcontainers, images, and volumes for ai-code-forge
# Handles the common issue where volumes can't be deleted due to container dependencies

set -e

REPO_NAME="ai-code-forge"
VOLUME_NAME="ai-code-forge"

echo "🧹 DevContainer Cleanup Script for $REPO_NAME"
echo "================================================"

# Skip confirmation for automated use

echo "🔍 Finding containers and volumes..."

# Function to stop and remove containers using a volume
cleanup_volume_containers() {
    local volume_name="$1"
    echo "🔍 Finding containers using volume: $volume_name"
    
    # Get container IDs that use this volume
    local container_ids=$(docker ps -a --filter volume="$volume_name" --format "{{.ID}}" 2>/dev/null || true)
    
    if [ -n "$container_ids" ]; then
        echo "🛑 Stopping containers using volume $volume_name..."
        echo "$container_ids" | xargs -r docker stop 2>/dev/null || true
        
        echo "🗑️  Removing containers using volume $volume_name..."
        echo "$container_ids" | xargs -r docker rm -f 2>/dev/null || true
    else
        echo "✅ No containers found using volume $volume_name"
    fi
}

# 1. Stop and remove all containers related to this repo
echo
echo "📦 Step 1: Cleaning up containers..."
CONTAINERS=$(docker ps -a --filter "label=devcontainer.local_folder" --format "{{.ID}} {{.Label \"devcontainer.local_folder\"}}" 2>/dev/null | grep "$REPO_NAME" | cut -d' ' -f1 || true)

if [ -n "$CONTAINERS" ]; then
    echo "🛑 Stopping devcontainers for $REPO_NAME..."
    echo "$CONTAINERS" | xargs -r docker stop 2>/dev/null || true
    
    echo "🗑️  Removing devcontainers for $REPO_NAME..."
    echo "$CONTAINERS" | xargs -r docker rm -f 2>/dev/null || true
    echo "✅ Devcontainers cleaned up"
else
    echo "✅ No devcontainers found for $REPO_NAME"
fi

# 2. Remove any additional containers that might be using our volume
cleanup_volume_containers "$VOLUME_NAME"

# 3. Remove images related to devcontainers
echo
echo "🖼️  Step 2: Cleaning up images..."
IMAGES=$(docker images --filter "label=devcontainer" --format "{{.Repository}}:{{.Tag}} {{.ID}}" 2>/dev/null | grep -i "$REPO_NAME" | cut -d' ' -f2 || true)

if [ -n "$IMAGES" ]; then
    echo "🗑️  Removing devcontainer images for $REPO_NAME..."
    echo "$IMAGES" | xargs -r docker rmi -f 2>/dev/null || true
    echo "✅ Images cleaned up"
else
    echo "✅ No devcontainer images found for $REPO_NAME"
fi

# 4. Remove the volume (this should work now that containers are gone)
echo
echo "💾 Step 3: Cleaning up volumes..."
if docker volume ls --format "{{.Name}}" | grep -q "^${VOLUME_NAME}$"; then
    echo "🗑️  Removing volume: $VOLUME_NAME..."
    if docker volume rm "$VOLUME_NAME" 2>/dev/null; then
        echo "✅ Volume $VOLUME_NAME removed successfully"
    else
        echo "❌ Failed to remove volume $VOLUME_NAME"
        echo "   Checking for remaining containers..."
        
        # Last resort - find any container still using the volume
        docker ps -a --filter volume="$VOLUME_NAME" --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}"
        echo "   Try running: docker ps -a --filter volume=$VOLUME_NAME"
        echo "   Then manually remove those containers and retry"
        exit 1
    fi
else
    echo "✅ Volume $VOLUME_NAME not found (already cleaned)"
fi

# 5. Clean up any dangling volumes and images
echo
echo "🧽 Step 4: Cleaning up dangling resources..."
echo "🗑️  Removing dangling volumes..."
docker volume prune -f >/dev/null 2>&1 || true

echo "🗑️  Removing dangling images..."
docker image prune -f >/dev/null 2>&1 || true

echo
echo "🎉 Cleanup completed successfully!"
echo "   All containers, images, and volumes for $REPO_NAME have been removed"
echo "   Next devcontainer build will start fresh"
