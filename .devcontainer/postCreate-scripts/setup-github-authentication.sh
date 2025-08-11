#!/bin/bash

# Set up GitHub CLI authentication
set -e

echo "🔐 Setting up authentication..."

# Skip authentication in Codespaces (pre-authenticated)
if [ "$RUNTIME_ENV" = "codespaces" ]; then
    echo "🌐 Codespaces: GitHub CLI pre-authenticated"
    if gh auth status >/dev/null 2>&1; then
        echo "✅ GitHub CLI authentication verified"
        gh auth status
    else
        echo "❌ Expected GitHub CLI authentication missing in Codespaces"
        exit 1
    fi
else
    # GitHub CLI authentication setup for DevContainer
    if gh auth status >/dev/null 2>&1; then
        echo "✅ GitHub CLI is already authenticated"
        gh auth status
    else
        echo "⚠️  GitHub CLI not authenticated"
        echo "   Run 'gh auth login' after container setup completes"
        echo "   This will authenticate both GitHub CLI and git operations"
    fi
fi

echo "✅ Authentication setup completed"