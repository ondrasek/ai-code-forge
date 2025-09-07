#!/bin/bash
#
# Version Synchronization Script
# Auto-discovers and updates version numbers across all version-bearing files
#
# Usage:
#   ./scripts/sync-versions.sh <target_version>
#
# Example:
#   ./scripts/sync-versions.sh 2.93.0
#
# Exit codes:
#   0 - All versions synchronized successfully
#   1 - Invalid version format or update failures
#   2 - Missing required parameters or files
#

set -euo pipefail

# ANSI color codes for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color="$1"
    local message="$2"
    echo -e "${color}${message}${NC}"
}

# Function to validate semantic version format
validate_version() {
    local version="$1"
    if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?$ ]]; then
        print_status "$RED" "❌ ERROR: Invalid version format: $version"
        print_status "$BLUE" "Expected format: x.y.z or x.y.z-suffix (semantic versioning)"
        return 1
    fi
    return 0
}

# Function to update pyproject.toml files
update_pyproject_version() {
    local file="$1"
    local version="$2"
    
    if [[ ! -f "$file" ]]; then
        print_status "$YELLOW" "⚠️  File not found: $file"
        return 1
    fi
    
    # Check if version line exists
    if ! grep -q '^version = ' "$file"; then
        print_status "$YELLOW" "⚠️  No version field found in: $file"
        return 1
    fi
    
    # Update version
    sed -i "s/^version = \".*\"/version = \"$version\"/" "$file"
    print_status "$GREEN" "✅ Updated pyproject.toml: $file → $version"
    return 0
}

# Function to update __init__.py files
update_init_py_version() {
    local file="$1"
    local version="$2"
    
    if [[ ! -f "$file" ]]; then
        print_status "$YELLOW" "⚠️  File not found: $file"
        return 1
    fi
    
    # Check if __version__ exists
    if ! grep -q '^__version__ = ' "$file"; then
        print_status "$YELLOW" "⚠️  No __version__ field found in: $file"
        return 1
    fi
    
    # Update __version__
    sed -i "s/^__version__ = \".*\"/__version__ = \"$version\"/" "$file"
    print_status "$GREEN" "✅ Updated __init__.py: $file → $version"
    return 0
}

# Function to get current version from pyproject.toml
get_current_version() {
    local file="$1"
    if [[ -f "$file" ]]; then
        if grep -q '^version = ' "$file"; then
            grep '^version = ' "$file" | sed 's/version = "//; s/"//'
        else
            echo ""
        fi
    else
        echo ""
    fi
}

# Function to get current version from __init__.py
get_init_version() {
    local file="$1"
    if [[ -f "$file" ]]; then
        if grep -q '^__version__ = ' "$file"; then
            grep '^__version__ = ' "$file" | sed 's/__version__ = "//; s/"//'
        else
            echo ""
        fi
    else
        echo ""
    fi
}

# Main script starts here
print_status "$CYAN" "🔄 AI Code Forge Version Synchronization Script"
print_status "$CYAN" "================================================="

# Check if version parameter provided
if [[ $# -eq 0 ]]; then
    print_status "$RED" "❌ ERROR: Target version required"
    print_status "$BLUE" "Usage: $0 <target_version>"
    print_status "$BLUE" "Example: $0 2.93.0"
    exit 2
fi

TARGET_VERSION="$1"

# Validate target version format
if ! validate_version "$TARGET_VERSION"; then
    exit 1
fi

print_status "$BLUE" "🎯 Target version: $TARGET_VERSION"
print_status "$BLUE" "🔍 Auto-discovering version-bearing files..."

# Define exclusion patterns (same as validate-versions.sh)
EXCLUDE_PATTERNS=(
    "*/node_modules/*"
    "*/venv/*" "*/.venv/*" "*/env/*" "*/.env/*"
    "*/site-packages/*" "*/dist/*" "*/build/*" "*/target/*"
    "*/.git/*" "*/examples/*" "*/demo/*" "*/test/*" "*/tests/*"
    "*/.pytest_cache/*" "*/temp/*" "*/tmp/*" "*/.cache/*"
)

# Find all pyproject.toml files
print_status "$BLUE" "📋 Discovering pyproject.toml files..."
ALL_PYPROJECT_FILES=($(find . -name "pyproject.toml" -type f | sort))

PYPROJECT_FILES=()
for file in "${ALL_PYPROJECT_FILES[@]}"; do
    clean_file="${file#./}"
    should_exclude=false
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        if [[ "$clean_file" == $pattern ]]; then
            should_exclude=true
            break
        fi
    done
    
    if [[ "$should_exclude" == false ]]; then
        PYPROJECT_FILES+=("$clean_file")
    else
        print_status "$YELLOW" "⏭️  Excluding pyproject.toml: $clean_file"
    fi
done

# Find all __init__.py files with __version__ (exclude .venv and site-packages directories)
print_status "$BLUE" "📋 Discovering __init__.py files with version info..."
ALL_INIT_FILES=($(find . -path "*/.venv" -prune -o -path "*/site-packages" -prune -o -name "__init__.py" -type f -exec grep -l '^__version__ = ' {} \; | sort))

INIT_FILES=()
for file in "${ALL_INIT_FILES[@]}"; do
    clean_file="${file#./}"
    should_exclude=false
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        if [[ "$clean_file" == $pattern ]]; then
            should_exclude=true
            break
        fi
    done
    
    if [[ "$should_exclude" == false ]]; then
        INIT_FILES+=("$clean_file")
    else
        print_status "$YELLOW" "⏭️  Excluding __init__.py: $clean_file"
    fi
done

# Report discovered files
print_status "$BLUE" "📦 Found ${#PYPROJECT_FILES[@]} pyproject.toml file(s):"
for file in "${PYPROJECT_FILES[@]}"; do
    current_version=$(get_current_version "$file")
    if [[ -n "$current_version" ]]; then
        print_status "$BLUE" "  - $file (currently: $current_version)"
    else
        print_status "$YELLOW" "  - $file (no version found)"
    fi
done

print_status "$BLUE" "📦 Found ${#INIT_FILES[@]} __init__.py file(s) with version:"
for file in "${INIT_FILES[@]}"; do
    current_version=$(get_init_version "$file")
    if [[ -n "$current_version" ]]; then
        print_status "$BLUE" "  - $file (currently: $current_version)"
    else
        print_status "$YELLOW" "  - $file (no __version__ found)"
    fi
done

# Check if any files found
TOTAL_FILES=$((${#PYPROJECT_FILES[@]} + ${#INIT_FILES[@]}))
if [[ $TOTAL_FILES -eq 0 ]]; then
    print_status "$RED" "❌ ERROR: No version-bearing files found for synchronization"
    exit 2
fi

print_status "$CYAN" ""
print_status "$CYAN" "🚀 Starting version synchronization..."
print_status "$CYAN" "======================================"

# Update pyproject.toml files
UPDATED_PYPROJECT=0
FAILED_PYPROJECT=0

if [[ ${#PYPROJECT_FILES[@]} -gt 0 ]]; then
    print_status "$BLUE" "📝 Updating pyproject.toml files..."
    for file in "${PYPROJECT_FILES[@]}"; do
        # Temporarily disable exit on error to handle failures gracefully
        set +e
        update_pyproject_version "$file" "$TARGET_VERSION"
        update_result=$?
        set -e
        
        if [[ $update_result -eq 0 ]]; then
            ((UPDATED_PYPROJECT++))
        else
            ((FAILED_PYPROJECT++))
        fi
    done
fi

# Update __init__.py files
UPDATED_INIT=0
FAILED_INIT=0

if [[ ${#INIT_FILES[@]} -gt 0 ]]; then
    print_status "$BLUE" "📝 Updating __init__.py files..."
    for file in "${INIT_FILES[@]}"; do
        # Temporarily disable exit on error to handle failures gracefully
        set +e
        update_init_py_version "$file" "$TARGET_VERSION"
        update_result=$?
        set -e
        
        if [[ $update_result -eq 0 ]]; then
            ((UPDATED_INIT++))
        else
            ((FAILED_INIT++))
        fi
    done
fi

# Report results
print_status "$CYAN" ""
print_status "$CYAN" "📊 Synchronization Summary"
print_status "$CYAN" "=========================="

TOTAL_UPDATED=$((UPDATED_PYPROJECT + UPDATED_INIT))
TOTAL_FAILED=$((FAILED_PYPROJECT + FAILED_INIT))

print_status "$GREEN" "✅ Successfully updated: $TOTAL_UPDATED files"
if [[ $UPDATED_PYPROJECT -gt 0 ]]; then
    print_status "$GREEN" "   - pyproject.toml files: $UPDATED_PYPROJECT"
fi
if [[ $UPDATED_INIT -gt 0 ]]; then
    print_status "$GREEN" "   - __init__.py files: $UPDATED_INIT"
fi

if [[ $TOTAL_FAILED -gt 0 ]]; then
    print_status "$RED" "❌ Failed to update: $TOTAL_FAILED files"
    if [[ $FAILED_PYPROJECT -gt 0 ]]; then
        print_status "$RED" "   - pyproject.toml files: $FAILED_PYPROJECT"
    fi
    if [[ $FAILED_INIT -gt 0 ]]; then
        print_status "$RED" "   - __init__.py files: $FAILED_INIT"
    fi
fi

print_status "$BLUE" "🎯 Target version: $TARGET_VERSION"

if [[ $TOTAL_FAILED -eq 0 ]]; then
    print_status "$GREEN" "🎉 All versions synchronized successfully!"
    print_status "$BLUE" "💡 Next steps:"
    print_status "$BLUE" "   1. Run './scripts/validate-versions.sh $TARGET_VERSION' to verify"
    print_status "$BLUE" "   2. Review and commit the changes"
    print_status "$BLUE" "   3. Create a release tag if needed"
    exit 0
else
    print_status "$YELLOW" "⚠️  Some files failed to update. Please review and fix manually."
    exit 1
fi