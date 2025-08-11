#!/bin/bash

# Setup environment variables for both shells
set -e

echo "🔧 Setting up environment variables..."

# Environment variables are loaded by postCreate.sh and exported to child processes

# Set up shell aliases and environment for bash
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
EOF

echo "✅ Environment variables setup completed"