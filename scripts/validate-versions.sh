#!/bin/bash
#
# Version Consistency Validation Script
# Ensures all pyproject.toml files have synchronized versions
#
# Usage:
#   ./scripts/validate-versions.sh [expected_version]
#
# Exit codes:
#   0 - All versions are consistent
#   1 - Version mismatch found
#   2 - Missing required files
#

set -euo pipefail

# ANSI color codes for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to extract version from pyproject.toml
get_version_from_pyproject() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        echo ""
        return 1
    fi
    grep '^version = ' "$file" | sed 's/version = "//; s/"//' || echo ""
}

# Function to print colored output
print_status() {
    local color="$1"
    local message="$2"
    echo -e "${color}${message}${NC}"
}

print_status "$BLUE" "🔍 Validating version consistency across all pyproject.toml files..."

# Expected version (optional parameter)
EXPECTED_VERSION="${1:-}"

# Define all pyproject.toml files that should have synchronized versions
PYPROJECT_FILES=(
    "cli/pyproject.toml"
    "mcp-servers/perplexity-mcp/pyproject.toml"
    "mcp-servers/openai-structured-mcp/pyproject.toml"
)

# Check if all required files exist
MISSING_FILES=()
for file in "${PYPROJECT_FILES[@]}"; do
    if [[ ! -f "$file" ]]; then
        MISSING_FILES+=("$file")
    fi
done

if [[ ${#MISSING_FILES[@]} -gt 0 ]]; then
    print_status "$RED" "❌ ERROR: Missing required pyproject.toml files:"
    for file in "${MISSING_FILES[@]}"; do
        print_status "$RED" "  - $file"
    done
    exit 2
fi

# Extract versions from all files
declare -A FILE_VERSIONS
REFERENCE_VERSION=""
REFERENCE_FILE=""

print_status "$BLUE" "📋 Extracting versions from pyproject.toml files:"

for file in "${PYPROJECT_FILES[@]}"; do
    version=$(get_version_from_pyproject "$file")
    if [[ -z "$version" ]]; then
        print_status "$RED" "❌ ERROR: Could not extract version from $file"
        exit 1
    fi
    
    FILE_VERSIONS["$file"]="$version"
    print_status "$BLUE" "  $file: $version"
    
    # Set first file as reference
    if [[ -z "$REFERENCE_VERSION" ]]; then
        REFERENCE_VERSION="$version"
        REFERENCE_FILE="$file"
    fi
done

print_status "$BLUE" "🎯 Using reference version: $REFERENCE_VERSION (from $REFERENCE_FILE)"

# Check if expected version is provided and matches
if [[ -n "$EXPECTED_VERSION" ]]; then
    print_status "$BLUE" "🔍 Validating against expected version: $EXPECTED_VERSION"
    if [[ "$REFERENCE_VERSION" != "$EXPECTED_VERSION" ]]; then
        print_status "$RED" "❌ ERROR: Reference version ($REFERENCE_VERSION) does not match expected version ($EXPECTED_VERSION)"
        exit 1
    fi
    print_status "$GREEN" "✅ Reference version matches expected version"
fi

# Validate all versions against reference
INCONSISTENT_FILES=()

for file in "${PYPROJECT_FILES[@]}"; do
    version="${FILE_VERSIONS[$file]}"
    if [[ "$version" != "$REFERENCE_VERSION" ]]; then
        INCONSISTENT_FILES+=("$file:$version")
    fi
done

# Report results
if [[ ${#INCONSISTENT_FILES[@]} -eq 0 ]]; then
    print_status "$GREEN" "✅ SUCCESS: All pyproject.toml files have consistent version: $REFERENCE_VERSION"
    
    # Additional validation for semantic versioning format
    if [[ "$REFERENCE_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?$ ]]; then
        print_status "$GREEN" "✅ Version follows semantic versioning format"
    else
        print_status "$YELLOW" "⚠️  WARNING: Version does not follow semantic versioning format (x.y.z)"
    fi
    
    print_status "$BLUE" "📦 Validated files:"
    for file in "${PYPROJECT_FILES[@]}"; do
        print_status "$BLUE" "  - $file"
    done
    
    exit 0
else
    print_status "$RED" "❌ ERROR: Version inconsistency detected!"
    print_status "$RED" "📋 Reference version: $REFERENCE_VERSION (from $REFERENCE_FILE)"
    print_status "$RED" "📋 Inconsistent files:"
    
    for entry in "${INCONSISTENT_FILES[@]}"; do
        IFS=':' read -r file version <<< "$entry"
        print_status "$RED" "  - $file: $version (should be $REFERENCE_VERSION)"
    done
    
    print_status "$YELLOW" "💡 To fix this issue:"
    print_status "$YELLOW" "   1. Update all pyproject.toml files to use version: $REFERENCE_VERSION"
    print_status "$YELLOW" "   2. Or use the /tag command which automatically synchronizes versions"
    print_status "$YELLOW" "   3. Commit the version changes before creating releases"
    
    exit 1
fi