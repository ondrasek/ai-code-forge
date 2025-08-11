#!/bin/bash

# Set up GitHub CLI authentication
set -e

echo "🔐 Setting up authentication..."

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