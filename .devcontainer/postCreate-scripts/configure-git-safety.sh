#!/bin/bash

# Configure Git safety settings
set -e

echo "🛡️ Setting up Git safety configuration..."

# Set up safe directory configuration
echo "Setting safe directory: $workingCopy"
git config --global --add safe.directory $workingCopy

echo "✅ Git safety configuration completed"