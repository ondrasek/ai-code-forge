#!/bin/bash

# DevContainer Setup Script - Replicates Codespace Environment
# This script sets up the exact same environment as the GitHub Codespace

# Skip the hassle when in GitHub Codespaces
if [ "$CODESPACES" = "true" ]; then
  echo "In Codespaces, exiting..."
  exit 0
fi

set -e

# Load environment variables first - these must be available to all scripts
devcontainerDir=/tmp/.devcontainer
postCreateEnvFile=$devcontainerDir/postCreate.env.tmp
[ -f $postCreateEnvFile ] || {
    echo $postCreateEnvFile does not exist!
    exit 1
}

eval "$(grep -v '^#' $postCreateEnvFile | sed 's/^/export /')"
export workingCopy=/workspace/$repositoryName
export worktreesDir=/workspace/worktrees/$repositoryName

echo "Configuration from initializeCommand:"
echo "repositoryName: $repositoryName"
echo "repositoryNameWithOwner: $repositoryNameWithOwner"
echo "gitUserName: $gitUserName"
echo "gitUserEmail: $gitUserEmail"
echo "workingCopy: $workingCopy"
echo "worktreesDir: $worktreesDir"

# Detect if we're in a container environment
export CONTAINER_ENV=1

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p ~/.claude

echo "🚀 Setting up Claude Code Template DevContainer..."
sudo mkdir -p /workspace && sudo chown vscode:vscode /workspace && cd /workspace

# Get the postCreate-scripts directory relative to this script
POSTCREATE_SCRIPTS_DIR="$(dirname "$0")/postCreate-scripts"

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