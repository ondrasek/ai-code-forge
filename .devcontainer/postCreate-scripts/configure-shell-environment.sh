#!/bin/bash

# Configure shell environment variables and navigation
set -e

echo "🐚 Configuring shell environment variables..."

# Load environment variables
devcontainerDir=/tmp/.devcontainer
eval "$(grep -v '^#' $devcontainerDir/postCreate.env.tmp | sed 's/^/export /')"
worktreesDir=/workspace/worktrees/$repositoryName

# Set up shell aliases and environment for both bash and zsh
cat >> ~/.bashrc << 'EOF'

# Environment variables for Claude Code
export PYTHONIOENCODING=UTF-8

# Add local bin to PATH
export PATH="$HOME/.local/bin:$PATH"
EOF

# ...this time with variable substitution
cat >> ~/.bashrc << EOF
# Devcontainer folder structure
export REPOSITORY_NAME=$repositoryName
export WORKING_COPY=$workingCopy
export WORKTREES=$worktreesDir

# Go to workspace
cd /workspace/$repositoryName
EOF

# Configure zsh with same environment
cat >> ~/.zshrc << 'EOF'

# Environment variables for Claude Code
export PYTHONIOENCODING=UTF-8

# Add local bin to PATH
export PATH="$HOME/.local/bin:$PATH"
EOF

# ...this time with variable substitution
cat >> ~/.zshrc << EOF
# Devcontainer folder structure
export REPOSITORY_NAME=$repositoryName
export WORKING_COPY=$workingCopy
export WORKTREES=$worktreesDir

# Go to workspace
cd /workspace/$repositoryName
EOF

echo "✅ Shell environment configuration completed"