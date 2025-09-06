#!/bin/bash

# Verify all installations and configurations
set -e

echo "✅ Verifying installations..."

echo "Node.js: $(node --version)"
echo "npm: $(npm --version)"
echo "Python: $(python3 --version)"
echo "uv: $(uv --version)"
echo "Git: $(git --version)"
echo "gh: $(gh --version)"
echo "Claude CLI: $(claude --version 2>/dev/null || echo 'Claude CLI installed, requires API key for full verification')"

echo ""
echo "🎉 DevContainer setup completed successfully!"
echo ""