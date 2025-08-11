#!/bin/bash

# Set up GitHub CLI authentication
set -e

# Skip in Codespaces (GitHub CLI pre-authenticated)
if [ "$CODESPACES" = "true" ]; then
    echo "🌐 Skipping GitHub authentication - running in Codespaces"
    exit 0
fi

echo "🔐 Setting up GitHub CLI authentication for DevContainer..."

# GitHub CLI authentication setup
if gh auth status >/dev/null 2>&1; then
    echo "✅ GitHub CLI is already authenticated"
    gh auth status
else
    echo "⚠️  GitHub CLI not authenticated"
    echo "   Run 'gh auth login' after container setup completes"
    echo "   This will authenticate both GitHub CLI and git operations"
fi

echo "✅ Authentication setup completed"