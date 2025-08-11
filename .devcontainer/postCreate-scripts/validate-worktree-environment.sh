#!/bin/bash

# Validate worktree environment prerequisites
set -e

echo "🔍 Validating worktree environment..."

# Environment variables are loaded by postCreate.sh and exported to child processes

# Note: This validates prerequisites within the DevContainer environment only.
# The validation is isolated to the container and does not affect the host system.

# Validate working copy directory and worktree script existence
if [[ -z "$workingCopy" ]]; then
    echo "⚠️ Working copy path not set, worktree environment invalid"
    exit 1
elif [[ ! -d "$workingCopy" ]]; then
    echo "⚠️ Working copy directory not found: $workingCopy, worktree environment invalid"
    exit 1
elif [[ ! -x "$workingCopy/scripts/worktree/worktree.sh" ]]; then
    echo "⚠️ Worktree script not found or not executable, worktree environment invalid"
    exit 1
else
    echo "✅ Worktree environment validation completed"
    echo "   Working copy: $workingCopy"
    echo "   Worktree script: $workingCopy/scripts/worktree/worktree.sh"
fi