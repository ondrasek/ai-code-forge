#!/bin/bash

# Setup shell navigation defaults for workspace
set -e

echo "🧭 Setting up shell navigation..."

# Environment variables are loaded by postCreate.sh and exported to child processes

# Set default directory for bash
cat >> ~/.bashrc << EOF
# Go to workspace
cd /workspace/$repositoryName
EOF

# Set default directory for zsh
cat >> ~/.zshrc << EOF
# Go to workspace
cd /workspace/$repositoryName
EOF

echo "✅ Shell navigation setup completed"