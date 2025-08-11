#!/bin/bash

# Set up Git configuration
set -e

echo "🔧 Setting up Git configuration..."

# Environment variables are loaded by postCreate.sh and exported to child processes

# Skip basic git config in Codespaces (set from GitHub account)
if [ "$RUNTIME_ENV" = "codespaces" ]; then
    echo "🌐 Codespaces: Git user config from GitHub account"
    # Verify git config is set
    if [ -n "$(git config --global user.name)" ] && [ -n "$(git config --global user.email)" ]; then
        echo "✅ Git user configuration verified: $(git config --global user.name) <$(git config --global user.email)>"
    else
        echo "❌ Expected git user configuration missing in Codespaces"
        exit 1
    fi
    # Still set up additional config
    git config --global credential.helper "!gh auth git-credential"
    git config --global --add safe.directory $workingCopy
else
    # Set up Git configuration for DevContainer (if not already configured)
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
fi

echo "✅ Git configuration completed"