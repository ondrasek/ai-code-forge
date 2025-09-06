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

print_status "$BLUE" "🔍 Validating version consistency across all version-bearing files..."

# Expected version (optional parameter)
EXPECTED_VERSION="${1:-}"

# Auto-discover all version-bearing files in the repository
print_status "$BLUE" "🔍 Auto-discovering version-bearing files..."

# Define exclusion patterns for files that should NOT be synchronized
EXCLUDE_PATTERNS=(
    "*/node_modules/*"
    "*/venv/*"
    "*/.venv/*"
    "*/env/*"
    "*/.env/*"
    "*/site-packages/*"
    "*/dist/*"
    "*/build/*"
    "*/target/*"
    "*/.git/*"
    "*/examples/*"
    "*/demo/*"
    "*/test/*"
    "*/tests/*"
    "*/.pytest_cache/*"
    "*/temp/*"
    "*/tmp/*"
    "*/.cache/*"
)

# Find all pyproject.toml files
ALL_PYPROJECT_FILES=($(find . -name "pyproject.toml" -type f | sort))

# Filter out excluded files
PYPROJECT_FILES=()
for file in "${ALL_PYPROJECT_FILES[@]}"; do
    # Remove leading ./ from path for cleaner display
    clean_file="${file#./}"
    
    # Check if file matches any exclusion pattern
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
        print_status "$YELLOW" "⏭️  Excluding: $clean_file (matches exclusion pattern)"
    fi
done

# Check if we found any files to validate
if [[ ${#PYPROJECT_FILES[@]} -eq 0 ]]; then
    print_status "$RED" "❌ ERROR: No pyproject.toml files found for validation"
    print_status "$BLUE" "Searched in: $(pwd)"
    print_status "$BLUE" "Exclusion patterns applied: ${#EXCLUDE_PATTERNS[@]} patterns"
    exit 2
fi

# Find all __init__.py files with __version__ (exclude .venv and site-packages directories)  
print_status "$BLUE" "📋 Discovering __init__.py files with version info..."
ALL_INIT_FILES=($(find . -path "*/.venv" -prune -o -path "*/site-packages" -prune -o -name "__init__.py" -type f -exec grep -l '^__version__ = ' {} \; | sort))

INIT_FILES=()
for file in "${ALL_INIT_FILES[@]}"; do
    # Remove leading ./ from path for cleaner display
    clean_file="${file#./}"
    
    # Check if file matches any exclusion pattern
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
        print_status "$YELLOW" "⏭️  Excluding: $clean_file (matches exclusion pattern)"
    fi
done

# Combine all files
ALL_FILES=("${PYPROJECT_FILES[@]}" "${INIT_FILES[@]}")

print_status "$BLUE" "📋 Found ${#PYPROJECT_FILES[@]} pyproject.toml file(s) for validation:"
for file in "${PYPROJECT_FILES[@]}"; do
    print_status "$BLUE" "  - $file"
done

print_status "$BLUE" "📋 Found ${#INIT_FILES[@]} __init__.py file(s) for validation:"
for file in "${INIT_FILES[@]}"; do
    print_status "$BLUE" "  - $file"
done

# Function to get version from __init__.py
get_version_from_init_py() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        echo ""
        return 1
    fi
    grep '^__version__ = ' "$file" | sed 's/__version__ = "//; s/"//' || echo ""
}

# Extract versions from all files
declare -A FILE_VERSIONS
REFERENCE_VERSION=""
REFERENCE_FILE=""

print_status "$BLUE" "📋 Extracting versions from all version-bearing files:"

# Process pyproject.toml files
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

# Process __init__.py files  
for file in "${INIT_FILES[@]}"; do
    version=$(get_version_from_init_py "$file")
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

# Check all files (both pyproject.toml and __init__.py)
for file in "${PYPROJECT_FILES[@]}" "${INIT_FILES[@]}"; do
    version="${FILE_VERSIONS[$file]}"
    if [[ "$version" != "$REFERENCE_VERSION" ]]; then
        INCONSISTENT_FILES+=("$file:$version")
    fi
done

# Report results
if [[ ${#INCONSISTENT_FILES[@]} -eq 0 ]]; then
    print_status "$GREEN" "✅ SUCCESS: All version-bearing files have consistent version: $REFERENCE_VERSION"
    
    # Additional validation for semantic versioning format
    if [[ "$REFERENCE_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?$ ]]; then
        print_status "$GREEN" "✅ Version follows semantic versioning format"
    else
        print_status "$YELLOW" "⚠️  WARNING: Version does not follow semantic versioning format (x.y.z)"
    fi
    
    print_status "$BLUE" "📦 Validated files:"
    for file in "${PYPROJECT_FILES[@]}" "${INIT_FILES[@]}"; do
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
    print_status "$YELLOW" "   1. Update all version-bearing files to use version: $REFERENCE_VERSION"
    print_status "$YELLOW" "   2. Or use the /tag command which automatically synchronizes versions"
    print_status "$YELLOW" "   3. Commit the version changes before creating releases"
    
    exit 1
fi