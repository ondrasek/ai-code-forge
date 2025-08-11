#!/bin/bash

# Configure Git user identity and basic settings
set -e

# Skip in Codespaces (git config set from GitHub account)
if [ "$CODESPACES" = "true" ]; then
    echo "🌐 Skipping git user configuration - running in Codespaces"
    exit 0
fi

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

echo "✅ Git user configuration completed"