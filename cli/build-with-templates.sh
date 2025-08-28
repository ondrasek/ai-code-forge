#!/bin/bash
set -e

echo "🔧 Building AI Code Forge CLI with templates..."

# Ensure we're in the CLI directory
cd "$(dirname "$0")"

# Copy templates temporarily for build (avoid symlink issues)
echo "📂 Copying templates for build..."
if [ -d "src/ai_code_forge_cli/templates" ]; then
    rm -rf src/ai_code_forge_cli/templates
fi
cp -r ../templates src/ai_code_forge_cli/templates

# Build the package
echo "📦 Building package..."
uv build

# Clean up copied templates (maintain single source of truth)
echo "🧹 Cleaning up temporary template copy..."
rm -rf src/ai_code_forge_cli/templates

echo "✅ Build complete! Package available in dist/"
echo "🧪 Test with: uvx --from dist/ai_code_forge-3.0.0-py3-none-any.whl acf status"
echo ""
echo "⚠️  Remember: /templates is the source of truth - never modify cli/src/ai_code_forge_cli/templates/"