#!/bin/bash
set -euo pipefail

# Master Test Runner for Launcher Scripts
# Runs all launcher test suites and provides comprehensive reporting
# Usage: ./run-all-tests.sh [--verbose] [--stop-on-fail]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Test configuration
VERBOSE=false
STOP_ON_FAIL=false
TEST_START_TIME=""
TOTAL_TESTS=0
TOTAL_PASSED=0
TOTAL_FAILED=0

# Test suites to run
TEST_SUITES=(
    "Security Tests:test-launcher-security.sh:Critical security validation for launcher utilities"
    "Unit Tests:test-launcher-units.sh:Core functionality testing for individual functions"
    "Integration Tests:test-launcher-integration.sh:CLI interface and workflow validation"
)

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -s|--stop-on-fail)
            STOP_ON_FAIL=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Show help function
show_help() {
    cat << EOF
Launcher Test Runner - Comprehensive testing for AI launcher scripts

USAGE:
    ./run-all-tests.sh [OPTIONS]

OPTIONS:
    -v, --verbose       Enable verbose output from individual test suites
    -s, --stop-on-fail  Stop execution on first test suite failure
    -h, --help          Show this help message

TEST SUITES:
    Security Tests      Critical security validation (command injection, file validation)
    Unit Tests          Core functionality testing for individual functions
    Integration Tests   CLI interface and workflow validation

EXAMPLES:
    ./run-all-tests.sh                    # Run all tests with summary output
    ./run-all-tests.sh --verbose          # Run with detailed test output
    ./run-all-tests.sh --stop-on-fail     # Stop on first failure for debugging

FEATURES:
    - Comprehensive test coverage for launcher ecosystem
    - Color-coded output with clear pass/fail indicators
    - Detailed timing and performance metrics
    - Test result aggregation across all suites
    - Support for CI/CD integration with proper exit codes

EOF
}

# Print header
print_header() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}${BOLD}              Launcher Test Suite Runner                     ${NC}${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${BLUE}Testing launcher ecosystem components:${NC}"
    echo -e "${BLUE}• Security validation and injection prevention${NC}"
    echo -e "${BLUE}• Core functionality and edge case handling${NC}"
    echo -e "${BLUE}• CLI interface consistency and workflows${NC}"
    echo
}

# Print test suite header
print_suite_header() {
    local suite_name="$1"
    local description="$2"
    
    echo -e "${CYAN}┌────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}│${NC} ${BOLD}$suite_name${NC}${CYAN}$(printf "%*s" $((58 - ${#suite_name})) "")│${NC}"
    echo -e "${CYAN}│${NC} $description${CYAN}$(printf "%*s" $((58 - ${#description})) "")│${NC}"
    echo -e "${CYAN}└────────────────────────────────────────────────────────────┘${NC}"
}

# Run a single test suite
run_test_suite() {
    local suite_name="$1"
    local script_name="$2"
    local description="$3"
    local script_path="$SCRIPT_DIR/$script_name"
    
    print_suite_header "$suite_name" "$description"
    
    if [[ ! -f "$script_path" ]]; then
        echo -e "${RED}❌ ERROR: Test script not found: $script_path${NC}"
        return 1
    fi
    
    if [[ ! -x "$script_path" ]]; then
        echo -e "${RED}❌ ERROR: Test script not executable: $script_path${NC}"
        return 1
    fi
    
    local start_time
    start_time=$(date +%s)
    
    local test_output
    local test_exit_code
    
    # Run the test suite
    if [[ "$VERBOSE" == "true" ]]; then
        # Show all output in verbose mode
        if "$script_path"; then
            test_exit_code=0
        else
            test_exit_code=$?
        fi
    else
        # Capture output and show summary only
        if test_output=$("$script_path" 2>&1); then
            test_exit_code=0
        else
            test_exit_code=$?
        fi
    fi
    
    local end_time
    end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Parse test results from output
    local tests_run=0
    local tests_passed=0
    local tests_failed=0
    
    if [[ -n "${test_output:-}" ]]; then
        tests_run=$(echo "$test_output" | grep -o "Tests run: [0-9]*" | grep -o "[0-9]*" || echo "0")
        tests_passed=$(echo "$test_output" | grep -o "Passed: [0-9]*" | grep -o "[0-9]*" || echo "0")
        tests_failed=$(echo "$test_output" | grep -o "Failed: [0-9]*" | grep -o "[0-9]*" || echo "0")
    fi
    
    # Update totals
    TOTAL_TESTS=$((TOTAL_TESTS + tests_run))
    TOTAL_PASSED=$((TOTAL_PASSED + tests_passed))
    TOTAL_FAILED=$((TOTAL_FAILED + tests_failed))
    
    # Print results
    if [[ $test_exit_code -eq 0 ]]; then
        echo -e "${GREEN}✅ SUITE PASSED${NC} - $tests_passed/$tests_run tests passed (${duration}s)"
        if [[ "$VERBOSE" == "false" && $tests_failed -gt 0 ]]; then
            echo -e "${YELLOW}⚠️  Note: $tests_failed tests failed but suite completed${NC}"
        fi
    else
        echo -e "${RED}❌ SUITE FAILED${NC} - $tests_failed/$tests_run tests failed (${duration}s)"
        if [[ "$VERBOSE" == "false" && -n "${test_output:-}" ]]; then
            echo -e "${YELLOW}Failed test details:${NC}"
            echo "$test_output" | grep -A 1 "✗ FAIL" || echo "No specific failure details available"
        fi
    fi
    
    echo
    
    return $test_exit_code
}

# Print final summary
print_summary() {
    local end_time
    end_time=$(date +%s)
    local total_duration=$((end_time - $(date -d "$TEST_START_TIME" +%s) ))
    
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}${BOLD}                    TEST SUMMARY                             ${NC}${CYAN}║${NC}"
    echo -e "${CYAN}╠══════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${CYAN}║${NC} Total Tests: $(printf "%3d" $TOTAL_TESTS)                                          ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC} ${GREEN}Passed:      $(printf "%3d" $TOTAL_PASSED)${NC}                                          ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC} ${RED}Failed:      $(printf "%3d" $TOTAL_FAILED)${NC}                                          ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC} Duration:    ${total_duration}s                                           ${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    if [[ $TOTAL_FAILED -eq 0 ]]; then
        echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
        echo -e "${GREEN}Launcher ecosystem is functioning correctly${NC}"
        echo
        echo -e "${BLUE}Ready for production deployment with:${NC}"
        echo -e "${BLUE}• Comprehensive security validation${NC}"
        echo -e "${BLUE}• Verified core functionality${NC}"
        echo -e "${BLUE}• Consistent CLI interfaces${NC}"
    else
        echo -e "${RED}⚠️  SOME TESTS FAILED${NC}"
        echo -e "${RED}Critical issues detected in launcher ecosystem${NC}"
        echo
        echo -e "${YELLOW}Recommended actions:${NC}"
        echo -e "${YELLOW}• Review failed test details above${NC}"
        echo -e "${YELLOW}• Fix security and functionality issues${NC}"
        echo -e "${YELLOW}• Re-run tests before deployment${NC}"
        
        # Show failure breakdown by category
        echo
        echo -e "${YELLOW}Test suite status:${NC}"
        if [[ $TOTAL_FAILED -gt 0 ]]; then
            echo -e "${YELLOW}• Check security tests for injection vulnerabilities${NC}"
            echo -e "${YELLOW}• Review unit tests for core function failures${NC}"
            echo -e "${YELLOW}• Verify integration tests for CLI inconsistencies${NC}"
        fi
    fi
}

# Main execution
main() {
    TEST_START_TIME=$(date)
    
    print_header
    
    local suite_failures=0
    
    # Run each test suite
    for suite_info in "${TEST_SUITES[@]}"; do
        IFS=':' read -r suite_name script_name description <<< "$suite_info"
        
        if ! run_test_suite "$suite_name" "$script_name" "$description"; then
            ((suite_failures++))
            if [[ "$STOP_ON_FAIL" == "true" ]]; then
                echo -e "${RED}Stopping execution due to --stop-on-fail flag${NC}"
                break
            fi
        fi
    done
    
    print_summary
    
    # Exit with appropriate code
    if [[ $TOTAL_FAILED -eq 0 ]]; then
        exit 0
    else
        exit 1
    fi
}

# Run if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi