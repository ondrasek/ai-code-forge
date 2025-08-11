#!/bin/bash

# Prepare repository workspace for DevContainer
set -e

echo "📋 Preparing repository workspace for DevContainer..."

echo "📋 Cloning repository into workspace:"
if [ -d $workingCopy/.git ]; then
  cd $workingCopy
  gh repo sync
  cd -
else
  gh repo clone $repositoryNameWithOwner $workingCopy
fi

# Set up worktree directories
mkdir -p $worktreesDir
git config --global --add safe.directory $worktreesDir

echo "✅ Repository preparation completed"
