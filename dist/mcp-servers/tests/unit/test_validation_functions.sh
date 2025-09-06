#!/bin/bash
set -euo pipefail

# Unit tests for worktree security validation functions
# Usage: ./test_validation_functions.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source the functions to test
source "$PROJECT_ROOT/scripts/worktree/worktree-create.sh"

# Test framework
TESTS_PASSED=0
TESTS_FAILED=0

test_assert() {
    local description="$1"
    local condition="$2"
    
    if eval "$condition"; then
        echo "✅ PASS: $description"
        ((TESTS_PASSED++))
    else
        echo "❌ FAIL: $description"
        ((TESTS_FAILED++))
    fi
}

test_assert_equals() {
    local description="$1"
    local expected="$2"
    local actual="$3"
    
    if [[ "$expected" == "$actual" ]]; then
        echo "✅ PASS: $description"
        ((TESTS_PASSED++))
    else
        echo "❌ FAIL: $description (expected: '$expected', got: '$actual')"
        ((TESTS_FAILED++))
    fi
}

# Redirect print functions to avoid noise during tests
print_error() { echo "ERROR: $1" >&2; }
print_success() { echo "SUCCESS: $1" >&2; }
print_warning() { echo "WARNING: $1" >&2; }
print_info() { echo "INFO: $1" >&2; }

echo "Running validation function tests..."
echo "=================================="

# Test validate_branch_name function
echo
echo "Testing validate_branch_name..."

# Valid branch names
test_assert "Valid branch name: feature/test" "validate_branch_name 'feature/test'"
test_assert "Valid branch name: hotfix-123" "validate_branch_name 'hotfix-123'"
test_assert "Valid branch name: issue-105-feature" "validate_branch_name 'issue-105-feature'"

# Invalid branch names - path traversal
test_assert "Invalid branch name: ../escape" "! validate_branch_name '../escape'"
test_assert "Invalid branch name: feature/../escape" "! validate_branch_name 'feature/../escape'"
test_assert "Invalid branch name: .." "! validate_branch_name '..'"

# Invalid branch names - special characters
test_assert "Invalid branch name with spaces" "! validate_branch_name 'branch with spaces'"
test_assert "Invalid branch name with semicolon" "! validate_branch_name 'branch;rm -rf'"
test_assert "Invalid branch name with pipe" "! validate_branch_name 'branch|evil'"

# Invalid branch names - length
test_assert "Invalid branch name: too long" "! validate_branch_name '$(printf "%*s" 101 | tr " " "a")'"

# Invalid branch names - git internals
test_assert "Invalid branch name: HEAD" "! validate_branch_name 'HEAD'"
test_assert "Invalid branch name: refs" "! validate_branch_name 'refs'"

# Test validate_no_symlinks function
echo
echo "Testing validate_no_symlinks..."

# Create test directory structure
TEST_BASE="/tmp/worktree-test-$$"
mkdir -p "$TEST_BASE/safe/path"
mkdir -p "$TEST_BASE/unsafe"
ln -s "/etc/passwd" "$TEST_BASE/unsafe/symlink"

# Valid paths (no symlinks)
test_assert "Valid path: no symlinks" "validate_no_symlinks '$TEST_BASE/safe/path'"

# Invalid paths (contains symlinks)
test_assert "Invalid path: contains symlink" "! validate_no_symlinks '$TEST_BASE/unsafe/symlink'"

# Cleanup test directory
rm -rf "$TEST_BASE"

# Test path traversal protection in branch validation
echo
echo "Testing path traversal protection..."

# URL encoded attacks
test_assert "Block URL encoded path traversal: %2e%2e%2f" "! validate_branch_name '%2e%2e%2f'"
test_assert "Block URL encoded path traversal: %2e%2e" "! validate_branch_name 'branch%2e%2e'"

# Various encoding attempts
test_assert "Block path traversal: backslash" "! validate_branch_name 'branch\.\.'"

# Test repository name validation
echo
echo "Testing repository name validation (from get_repo_name)..."

# Mock successful repository name
MAIN_REPO="$PROJECT_ROOT"
export MAIN_REPO

# Test get_repo_name function (basic functionality test)
REPO_NAME=$(get_repo_name 2>/dev/null || echo "test-failed")
test_assert "Repository name returned" "[[ -n '$REPO_NAME' && '$REPO_NAME' != 'test-failed' ]]"

echo
echo "Test Summary"
echo "============"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"
echo "Total tests: $((TESTS_PASSED + TESTS_FAILED))"

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo "✅ All tests passed!"
    exit 0
else
    echo "❌ Some tests failed!"
    exit 1
fi