#!/bin/bash

# Prepare repository workspace
set -e

# Environment variables are loaded by postCreate.sh and exported to child processes
echo -n "📋 Cloning repository into workspace: "
mkdir -p $workingCopy

if [ -d $workingCopy/.git ]; then
  echo "syncing $workingCopy"
  cd $workingCopy
  gh repo sync
  cd -
else
  echo "cloning into $workingCopy"
  gh repo clone $repositoryNameWithOwner $workingCopy
fi

# Set up worktree directories
mkdir -p $worktreesDir
git config --global --add safe.directory $worktreesDir

echo "✅ Repository preparation completed"
