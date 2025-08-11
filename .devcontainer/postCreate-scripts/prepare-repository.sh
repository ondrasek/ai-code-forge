#!/bin/bash

# Prepare repository workspace
set -e

echo "📋 Preparing repository workspace..."

# Environment variables are loaded by postCreate.sh and exported to child processes

# Skip repository operations in Codespaces (automatically handled)
if [ "$RUNTIME_ENV" = "codespaces" ]; then
    echo "🌐 Codespaces: Repository already available at $workingCopy"
    # Verify repository is accessible
    if [ -d "$workingCopy/.git" ]; then
        echo "✅ Repository verified in Codespaces"
    else
        echo "❌ Expected repository not found in Codespaces at $workingCopy"
        exit 1
    fi
else
    echo "📋 Cloning repository into workspace:"
    if [ -d $workingCopy/.git ]; then
      cd $workingCopy
      gh repo sync
      cd -
    else
      gh repo clone $repositoryNameWithOwner $workingCopy
    fi
fi

# Set up worktree directories (needed in both environments)
mkdir -p $worktreesDir
git config --global --add safe.directory $worktreesDir

echo "✅ Repository preparation completed"
