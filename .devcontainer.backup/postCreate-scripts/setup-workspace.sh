#!/bin/bash

# Setup workspace directories and configuration
set -e

echo "🏗️ Setting up workspace directories..."

# Set up worktree directories
mkdir -p $worktreesDir
git config --global --add safe.directory $worktreesDir

echo "✅ Workspace setup completed"
echo "   Worktrees directory: $worktreesDir"