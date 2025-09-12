#!/bin/bash

# Consolidated Git configuration script
# Combines user, credentials, and safety setup
set -e

echo "🔧 Setting up Git configuration..."

# Git User Configuration
if [ "$CODESPACES" = "true" ]; then
    echo "🌐 Skipping git user configuration - running in Codespaces"
else
    echo "👤 Setting up Git user configuration for DevContainer..."
    
    # Set up Git user configuration (if not already configured)
    if [ -z "$(git config --global user.name)" ]; then
        echo "⚙️ Setting up basic Git user configuration..."
        git config --global init.defaultBranch main
        git config --global pull.rebase false
        git config --global user.name $gitUserName
        git config --global user.email $gitUserEmail
    else
        echo "✅ Git user configuration already exists"
    fi
fi

# Git Credentials Configuration
echo "🔑 Setting up Git credentials..."
echo "Setting up credential helper with GitHub CLI..."
git config --global credential.helper "!gh auth git-credential"

# Git Safety Configuration
echo "🛡️ Setting up Git safety configuration..."
echo "Setting safe directory: $workingCopy"
git config --global --add safe.directory $workingCopy

echo "✅ Git configuration completed"