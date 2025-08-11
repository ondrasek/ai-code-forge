#!/bin/bash

# Prepare repository workspace
set -e

echo "📋 Preparing repository workspace..."

# Load environment variables
devcontainerDir=/tmp/.devcontainer
eval "$(grep -v '^#' $devcontainerDir/postCreate.env.tmp | sed 's/^/export /')"
workingCopy=/workspace/$repositoryName

echo "Configuration from initializeCommand:"
echo "repositoryName: $repositoryName"
echo "repositoryNameWithOwner: $repositoryNameWithOwner"
echo "gitUserName: $gitUserName"
echo "gitUserEmail: $gitUserEmail"
echo "workingCopy: $workingCopy"

echo "📋 Cloning repository into workspace:"
if [ -d $workingCopy/.git ]; then
  cd $workingCopy
  gh repo sync
  cd -
else
  gh repo clone $repositoryNameWithOwner $workingCopy
fi

# Set up worktree directories
worktreesDir=/workspace/worktrees/$repositoryName
mkdir -p $worktreesDir
git config --global -add safe.directory $worktreesDir

echo "✅ Repository preparation completed"