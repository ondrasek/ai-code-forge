#!/bin/bash

# Setup environment variables for development
set -e

echo "⚙️ Setting up environment variables..."

# Add repository-specific environment variables to shell profiles
cat >> /home/vscode/.zshrc << 'EOF'

# Repository-specific environment variables
export REPOSITORY_NAME=test-repo
export WORKTREES=/workspace/worktrees/test-repo

EOF

cat >> /home/vscode/.bashrc << 'EOF'

# Repository-specific environment variables
export REPOSITORY_NAME=test-repo
export WORKTREES=/workspace/worktrees/test-repo

EOF

# Set for current session
export REPOSITORY_NAME=test-repo
export WORKTREES=/workspace/worktrees/test-repo

echo "✅ Environment variables setup completed"
echo "   REPOSITORY_NAME=test-repo"
echo "   WORKTREES=/workspace/worktrees/test-repo"