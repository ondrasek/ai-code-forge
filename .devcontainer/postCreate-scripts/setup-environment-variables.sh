#!/bin/bash

# Setup environment variables for development
set -e

echo "⚙️ Setting up environment variables..."

# Add repository-specific environment variables to shell profiles
cat >> /home/vscode/.zshrc << 'EOF'

# Repository-specific environment variables
export REPOSITORY_NAME=ai-code-forge
export WORKTREES=/workspace/worktrees/ai-code-forge

EOF

cat >> /home/vscode/.bashrc << 'EOF'

# Repository-specific environment variables
export REPOSITORY_NAME=ai-code-forge
export WORKTREES=/workspace/worktrees/ai-code-forge

EOF

# Set for current session
export REPOSITORY_NAME=ai-code-forge
export WORKTREES=/workspace/worktrees/ai-code-forge

echo "✅ Environment variables setup completed"
echo "   REPOSITORY_NAME=ai-code-forge"
echo "   WORKTREES=/workspace/worktrees/ai-code-forge"