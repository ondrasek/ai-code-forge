#!/bin/bash

# DevContainer Setup Script - Replicates Codespace Environment
# This script sets up the exact same environment as the GitHub Codespace

# Skip the hassle when in GitHub Codespaces
if [ "$CODESPACES" = "true" ]; then
  echo "In Codespaces, exiting..."
  exit 0
fi

set -e

# Detect if we're in a container environment
export CONTAINER_ENV=1

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p ~/.claude

echo "🚀 Setting up Claude Code Template DevContainer..."
sudo mkdir -p /workspace && sudo chown vscode:vscode /workspace && cd /workspace

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POSTCREATE_SCRIPTS_DIR="$SCRIPT_DIR/postCreate-scripts"

# Execute setup scripts in order
echo "🔄 Running setup scripts..."

"$POSTCREATE_SCRIPTS_DIR/install-dev-tools.sh"
"$POSTCREATE_SCRIPTS_DIR/configure-shell.sh"
"$POSTCREATE_SCRIPTS_DIR/setup-git.sh"
"$POSTCREATE_SCRIPTS_DIR/authenticate-github.sh"
"$POSTCREATE_SCRIPTS_DIR/prepare-repository.sh"
"$POSTCREATE_SCRIPTS_DIR/initialize-worktree.sh"
"$POSTCREATE_SCRIPTS_DIR/configure-shell-environment.sh"
"$POSTCREATE_SCRIPTS_DIR/verify-installation.sh"

echo "🎉 All setup scripts completed successfully!"