#!/bin/bash
set -e

# ACF CI Build Trigger Script
# Manually triggers the automated GitHub Actions workflow from CLI

echo "🚀 Triggering ACF CI Build Workflow..."

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is required but not installed"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI"
    echo "Run: gh auth login"
    exit 1
fi

# Get current repository
REPO=$(gh repo view --json owner,name --jq '.owner.login + "/" + .name')
echo "Repository: $REPO"

# Get current branch
BRANCH=$(git branch --show-current)
echo "Branch: $BRANCH"

# Trigger the workflow
echo "Triggering workflow dispatch..."
if gh workflow run "ACF CLI Build" --repo "$REPO" --ref "$BRANCH"; then
    echo "✅ Workflow triggered successfully!"
    echo ""
    echo "Monitor progress:"
    echo "  GitHub UI: https://github.com/$REPO/actions"
    echo "  CLI: gh workflow list --repo $REPO"
    echo "  CLI: gh run watch --repo $REPO"
else
    echo "❌ Failed to trigger workflow"
    echo "Make sure the 'ACF CLI Build' workflow exists in .github/workflows/"
    exit 1
fi

echo ""
echo "💡 This triggers the CI/CD build with:"
echo "  - Proper caching"
echo "  - Security scanning" 
echo "  - Artifact generation"
echo "  - Multi-environment testing"