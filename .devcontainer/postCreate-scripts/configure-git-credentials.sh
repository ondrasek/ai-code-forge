#!/bin/bash

# Configure Git credential helper
set -e

echo "🔑 Setting up Git credentials..."

# Set up Git credential helper
echo "Setting up credential helper with GitHub CLI..."
git config --global credential.helper "!gh auth git-credential"

echo "✅ Git credentials configuration completed"