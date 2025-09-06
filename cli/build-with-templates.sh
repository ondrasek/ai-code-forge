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

# Copy dist directory for build
echo "📦 Copying dist directory for build..."
if [ -d "src/ai_code_forge_cli/dist" ]; then
    rm -rf src/ai_code_forge_cli/dist
fi

# Check if dist directory exists at expected location
if [ -d "../dist" ]; then
    cp -r ../dist src/ai_code_forge_cli/dist
    echo "✅ Copied dist from ../dist"
else
    echo "❌ ERROR: dist directory not found at ../dist"
    echo "Current directory: $(pwd)"
    echo "Available directories:"
    ls -la ../
    exit 1
fi

# Build the package
echo "📦 Building package..."
uv build

# Clean up copied content (maintain single source of truth)
echo "🧹 Cleaning up temporary copies..."
rm -rf src/ai_code_forge_cli/templates
rm -rf src/ai_code_forge_cli/dist

echo "✅ Build complete! Package available in dist/"
echo "🧪 Test with: uvx --from dist/ai_code_forge-3.0.0-py3-none-any.whl acf status"
echo ""
echo "⚠️  Remember: /templates and /dist are the source of truth - never modify cli/src/ai_code_forge_cli/ directories"