#!/bin/bash

# Setup workspace directories and configuration
set -e

echo "🏗️ Setting up workspace directories..."

# Set up worktree directories
mkdir -p /workspace/worktrees/ai-code-forge
git config --global --add safe.directory /workspace/worktrees/ai-code-forge

echo "✅ Workspace setup completed"
echo "   Worktrees directory: /workspace/worktrees/ai-code-forge"