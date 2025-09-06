#!/bin/bash
set -euo pipefail

# Test suite for worktree-inspect.sh
# Basic functionality validation and error handling tests

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE_SCRIPT="$SCRIPT_DIR/../worktree-inspect.sh"

# Color codes for test output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test counters
TEST_COUNT=0
PASS_COUNT=0
FAIL_COUNT=0

# Test result tracking
print_test_header() {
    echo -e "${BLUE}Testing: $1${NC}"
    ((TEST_COUNT++))
}

print_pass() {
    echo -e "  ${GREEN}✅ PASS:${NC} $1"
    ((PASS_COUNT++))
}

print_fail() {
    echo -e "  ${RED}❌ FAIL:${NC} $1"
    ((FAIL_COUNT++))
}

print_summary() {
    echo
    echo -e "${BLUE}=================================================${NC}"
    echo -e "${BLUE}                TEST SUMMARY${NC}"
    echo -e "${BLUE}=================================================${NC}"
    echo -e "${BLUE}Total Tests:${NC} $TEST_COUNT"
    echo -e "${GREEN}Passed:${NC} $PASS_COUNT"
    if [[ $FAIL_COUNT -gt 0 ]]; then
        echo -e "${RED}Failed:${NC} $FAIL_COUNT"
    fi
    echo
    
    if [[ $FAIL_COUNT -eq 0 ]]; then
        echo -e "${GREEN}All tests passed!${NC}"
        return 0
    else
        echo -e "${RED}Some tests failed!${NC}"
        return 1
    fi
}

# Verify script exists and is executable
test_script_accessibility() {
    print_test_header "Script accessibility"
    
    if [[ -f "$WORKTREE_SCRIPT" ]]; then
        print_pass "Script file exists"
    else
        print_fail "Script file not found: $WORKTREE_SCRIPT"
        return 1
    fi
    
    if [[ -x "$WORKTREE_SCRIPT" ]]; then
        print_pass "Script is executable"
    else
        print_fail "Script is not executable"
        return 1
    fi
}

# Test help output
test_help_output() {
    print_test_header "Help output"
    
    local help_output
    if help_output=$("$WORKTREE_SCRIPT" --help 2>&1); then
        if [[ "$help_output" =~ "Git Worktree Inspect Utility" ]]; then
            print_pass "Help output contains expected header"
        else
            print_fail "Help output missing expected header"
        fi
        
        if [[ "$help_output" =~ "USAGE:" ]]; then
            print_pass "Help output contains usage section"
        else
            print_fail "Help output missing usage section"
        fi
    else
        print_fail "Failed to execute --help option"
    fi
}

# Test error handling for missing arguments
test_missing_arguments() {
    print_test_header "Missing arguments error handling"
    
    local output
    local exit_code
    
    # Should fail with no arguments
    if output=$("$WORKTREE_SCRIPT" 2>&1); then
        exit_code=0
    else
        exit_code=$?
    fi
    
    if [[ $exit_code -ne 0 ]]; then
        print_pass "Correctly exits with error when no arguments provided"
    else
        print_fail "Should exit with error when no arguments provided"
    fi
    
    if [[ "$output" =~ "Missing required ISSUE_SPEC argument" ]]; then
        print_pass "Provides helpful error message"
    else
        print_fail "Missing helpful error message for missing arguments"
    fi
}

# Test JSON output format
test_json_output() {
    print_test_header "JSON output format"
    
    local json_output
    local exit_code
    
    # Test with a non-existent issue (should still produce valid JSON)
    if json_output=$("$WORKTREE_SCRIPT" --json 99999 2>/dev/null); then
        exit_code=$?
        
        # Validate JSON structure
        if echo "$json_output" | jq . >/dev/null 2>&1; then
            print_pass "Produces valid JSON output"
        else
            print_fail "Invalid JSON output"
            return 1
        fi
        
        # Check for expected top-level keys
        local required_keys=("specification" "github" "worktree" "git" "ai_assistant" "summary")
        for key in "${required_keys[@]}"; do
            if echo "$json_output" | jq -e "has(\"$key\")" >/dev/null 2>&1; then
                print_pass "JSON contains required key: $key"
            else
                print_fail "JSON missing required key: $key"
            fi
        done
    else
        print_fail "Failed to generate JSON output"
    fi
}

# Test issue number parsing
test_issue_parsing() {
    print_test_header "Issue specification parsing"
    
    # Test with hash prefix
    local output
    if output=$("$WORKTREE_SCRIPT" --json "#115" 2>/dev/null); then
        if echo "$output" | jq -e '.specification.input == "#115"' >/dev/null 2>&1; then
            print_pass "Correctly handles issue number with hash prefix"
        else
            print_fail "Failed to parse issue number with hash prefix"
        fi
    else
        print_fail "Failed to process issue with hash prefix"
    fi
    
    # Test plain number
    if output=$("$WORKTREE_SCRIPT" --json "115" 2>/dev/null); then
        if echo "$output" | jq -e '.specification.type == "number"' >/dev/null 2>&1; then
            print_pass "Correctly identifies plain number as number type"
        else
            print_fail "Failed to identify plain number as number type"
        fi
    else
        print_fail "Failed to process plain issue number"
    fi
}

# Test branch name parsing
test_branch_parsing() {
    print_test_header "Branch name parsing"
    
    local output
    if output=$("$WORKTREE_SCRIPT" --json "main" 2>/dev/null); then
        if echo "$output" | jq -e '.specification.type == "branch"' >/dev/null 2>&1; then
            print_pass "Correctly identifies branch name as branch type"
        else
            print_fail "Failed to identify branch name as branch type"
        fi
    else
        print_fail "Failed to process branch name"
    fi
}

# Test exit codes
test_exit_codes() {
    print_test_header "Exit code behavior"
    
    local exit_code
    
    # Test with help (should exit 0)
    "$WORKTREE_SCRIPT" --help >/dev/null 2>&1
    exit_code=$?
    if [[ $exit_code -eq 0 ]]; then
        print_pass "Help command exits with code 0"
    else
        print_fail "Help command should exit with code 0, got $exit_code"
    fi
    
    # Test with invalid arguments (should exit non-zero)
    "$WORKTREE_SCRIPT" >/dev/null 2>&1
    exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        print_pass "Invalid arguments exit with non-zero code"
    else
        print_fail "Invalid arguments should exit with non-zero code"
    fi
}

# Main test execution
main() {
    echo -e "${BLUE}Running Worktree Inspect Test Suite${NC}"
    echo -e "${BLUE}Script: $WORKTREE_SCRIPT${NC}"
    echo
    
    # Run all tests
    test_script_accessibility
    test_help_output
    test_missing_arguments
    test_json_output
    test_issue_parsing
    test_branch_parsing
    test_exit_codes
    
    # Print summary
    print_summary
}

# Execute tests
main "$@"