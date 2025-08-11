#!/bin/bash
set -e

# ACF complete build script
# 1. Copies source files to package data directory
# 2. Builds the package
# 3. Validates the build

echo "=== ACF Complete Build Process ==="
echo "Step 1: Building package data..."

# Get repository root (parent of acf directory)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGE_DATA="$(cd "$(dirname "${BASH_SOURCE[0]}")/src/ai_code_forge/data" && pwd)"

echo "Repository root: $REPO_ROOT"
echo "Package data dir: $PACKAGE_DATA"

# Clean existing data
rm -rf "$PACKAGE_DATA"/{claude,acf,CLAUDE.md}

# Create data structure
mkdir -p "$PACKAGE_DATA"/{claude,acf}

# Copy .claude directory (Claude Code recognized files)
echo "Copying .claude directory..."
cp -r "$REPO_ROOT/.claude"/* "$PACKAGE_DATA/claude/"

# Copy ACF-managed files (non-Claude Code files)
echo "Copying templates, scripts, docs..."
cp -r "$REPO_ROOT"/templates "$PACKAGE_DATA/acf/"
cp -r "$REPO_ROOT"/scripts "$PACKAGE_DATA/acf/"
cp -r "$REPO_ROOT"/docs "$PACKAGE_DATA/acf/"

# Copy ACF tool documentation
echo "Copying ACF tool documentation..."
cp "$REPO_ROOT/README.md" "$PACKAGE_DATA/acf/"
cp "$REPO_ROOT/CHANGELOG.md" "$PACKAGE_DATA/acf/"

# Copy CLAUDE.md to root
echo "Copying CLAUDE.md..."
cp "$REPO_ROOT/CLAUDE.md" "$PACKAGE_DATA/"

echo "Step 1 complete - Package data prepared!"

echo ""
echo "Step 2: Building ACF package..."
uv build

echo ""
echo "Step 3: Validating build..."
# Check if wheel was created
if ls dist/*.whl >/dev/null 2>&1; then
    echo "✅ Wheel file created successfully"
else
    echo "❌ No wheel file found"
    exit 1
fi

# Test that the package can be imported
echo "Testing package import..."
if uv run python -c "import ai_code_forge; print('✅ Package imports successfully')"; then
    echo "✅ Package validation passed"
else
    echo "❌ Package validation failed"
    exit 1
fi

echo ""
echo "🎉 ACF Complete Build Process Successful!"
echo "Generated files:"
ls -la dist/