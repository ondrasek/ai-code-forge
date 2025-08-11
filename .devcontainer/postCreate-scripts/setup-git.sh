#!/bin/bash

# Set up Git configuration
set -e

echo "🔧 Setting up Git configuration..."

# Environment variables are loaded by postCreate.sh and exported to child processes

# Set up Git configuration (if not already configured)
if [ -z "$(git config --global user.name)" ]; then
    echo "⚙️ Setting up basic Git configuration..."
    git config --global init.defaultBranch main
    git config --global pull.rebase false
    git config --global user.name $gitUserName
    git config --global user.email $gitUserEmail
fi

# Set up Git configuration and aliases
echo "1. Credential Helper"
git config --global credential.helper "!gh auth git-credential"
echo "2. Safe Directory: /workspace"
git config --global --add safe.directory $workingCopy

echo "✅ Git configuration completed"