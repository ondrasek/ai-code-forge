#!/bin/bash
# Simple shell wrapper for the Python test runner
# This provides a more familiar interface for shell users

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_SERVERS_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'  
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BOLD}${BLUE}AI Code Forge MCP Server Test Runner${NC}"
echo -e "${BLUE}Working directory: $MCP_SERVERS_DIR${NC}"
echo

# Check if we're in the right location
if [[ ! -f "$SCRIPT_DIR/run_tests.py" ]]; then
    echo -e "${RED}Error: run_tests.py not found. Make sure you're running this from mcp-servers/tests/${NC}"
    exit 1
fi

# Check Python availability
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}Error: Python not found. Please install Python 3.8+${NC}"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Change to mcp-servers directory for running tests
cd "$MCP_SERVERS_DIR"

# Show help if requested
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  --help, -h          Show this help message"
    echo "  --verbose, -v       Enable verbose output" 
    echo "  --env ENVIRONMENT   Set test environment (local, ci, production)"
    echo "  --include-slow      Include resource-intensive load tests"
    echo "  --coverage          Generate coverage report"
    echo "  --quick             Run only fast unit tests"
    echo
    echo "Examples:"
    echo "  $0                  # Run all tests with default settings"
    echo "  $0 --verbose        # Run with detailed output"
    echo "  $0 --env ci         # Run with CI environment baselines"
    echo "  $0 --quick          # Run only unit tests (fastest)"
    echo "  $0 --coverage       # Run tests and generate coverage report"
    echo
    exit 0
fi

# Pass all arguments to the Python script
echo -e "${YELLOW}Running: $PYTHON_CMD tests/run_tests.py $@${NC}"
echo

exec "$PYTHON_CMD" tests/run_tests.py "$@"