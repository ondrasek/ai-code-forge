#!/bin/bash

# Setup workspace directories and configuration
set -e

echo "🏗️ Setting up workspace directories..."

# Set up worktree directories
mkdir -p /workspace/worktrees/test-repo
git config --global --add safe.directory /workspace/worktrees/test-repo

echo "✅ Workspace setup completed"
echo "   Worktrees directory: /workspace/worktrees/test-repo"