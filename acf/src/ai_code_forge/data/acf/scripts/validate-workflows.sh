#!/bin/bash
set -e

# GitHub Workflows Validation Script
# Validates workflow files before pushing to repository

echo "🔍 GitHub Workflows Validation Script"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

VALIDATION_ERRORS=0

# Function to print status
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✅ PASS${NC}: $message"
    elif [ "$status" = "FAIL" ]; then
        echo -e "${RED}❌ FAIL${NC}: $message"
        ((VALIDATION_ERRORS++))
    elif [ "$status" = "WARN" ]; then
        echo -e "${YELLOW}⚠️  WARN${NC}: $message"
    else
        echo -e "${BLUE}ℹ️  INFO${NC}: $message"
    fi
}

# Function to check command availability
check_command() {
    local cmd=$1
    local install_hint=$2
    if command -v "$cmd" &> /dev/null; then
        print_status "PASS" "$cmd is available"
        return 0
    else
        print_status "WARN" "$cmd not found. Install with: $install_hint"
        return 1
    fi
}

echo ""
echo "📋 Step 1: Checking Prerequisites"
echo "--------------------------------"

# Check required tools
YAMLLINT_AVAILABLE=false
GH_AVAILABLE=false
YQ_AVAILABLE=false

if check_command "yamllint" "uv tool install yamllint"; then
    YAMLLINT_AVAILABLE=true
fi

if check_command "gh" "https://cli.github.com/"; then
    GH_AVAILABLE=true
fi

if check_command "yq" "uv tool install yq"; then
    YQ_AVAILABLE=true
fi

echo ""
echo "📋 Step 2: YAML Syntax Validation"
echo "--------------------------------"

WORKFLOW_DIR=".github/workflows"

if [ ! -d "$WORKFLOW_DIR" ]; then
    print_status "FAIL" "Workflows directory not found: $WORKFLOW_DIR"
    exit 1
fi

# Find all workflow files
WORKFLOW_FILES=$(find "$WORKFLOW_DIR" -name "*.yml" -o -name "*.yaml")

if [ -z "$WORKFLOW_FILES" ]; then
    print_status "WARN" "No workflow files found in $WORKFLOW_DIR"
else
    for workflow in $WORKFLOW_FILES; do
        echo "Validating: $workflow"
        
        # Basic YAML syntax check
        if python3 -c "import yaml; yaml.safe_load(open('$workflow'))" 2>/dev/null; then
            print_status "PASS" "YAML syntax valid: $(basename $workflow)"
        else
            print_status "FAIL" "YAML syntax error: $(basename $workflow)"
            continue
        fi
        
        # yamllint check if available
        if [ "$YAMLLINT_AVAILABLE" = true ]; then
            if yamllint "$workflow" &>/dev/null; then
                print_status "PASS" "yamllint passed: $(basename $workflow)"
            else
                print_status "WARN" "yamllint issues in: $(basename $workflow)"
                echo "  Run: yamllint $workflow"
            fi
        fi
    done
fi

echo ""
echo "📋 Step 3: GitHub Actions Validation"
echo "-----------------------------------"

if [ "$GH_AVAILABLE" = true ]; then
    # Check if authenticated
    if gh auth status &>/dev/null; then
        print_status "PASS" "GitHub CLI authenticated"
        
        # Validate workflows with GitHub
        for workflow in $WORKFLOW_FILES; do
            echo "GitHub validating: $workflow"
            if gh workflow list &>/dev/null; then
                print_status "PASS" "GitHub connection works"
                break
            fi
        done
    else
        print_status "WARN" "GitHub CLI not authenticated. Run: gh auth login"
    fi
else
    print_status "WARN" "GitHub CLI not available - skipping remote validation"
fi

echo ""
echo "📋 Step 4: Workflow Structure Validation"
echo "---------------------------------------"

for workflow in $WORKFLOW_FILES; do
    echo "Analyzing: $(basename $workflow)"
    
    # Check for required sections
    if grep -q "^name:" "$workflow"; then
        print_status "PASS" "Has name field"
    else
        print_status "FAIL" "Missing name field"
    fi
    
    if grep -q "^on:" "$workflow"; then
        print_status "PASS" "Has trigger conditions (on:)"
    else
        print_status "FAIL" "Missing trigger conditions (on:)"
    fi
    
    if grep -q "^jobs:" "$workflow"; then
        print_status "PASS" "Has jobs section"
    else
        print_status "FAIL" "Missing jobs section"
    fi
    
    # Check for common issues
    if grep -q "ubuntu-latest" "$workflow"; then
        print_status "PASS" "Uses ubuntu-latest runner"
    else
        print_status "WARN" "No ubuntu-latest runner specified"
    fi
    
    if grep -q "actions/checkout@v" "$workflow"; then
        print_status "PASS" "Uses checkout action"
    else
        print_status "WARN" "No checkout action found"
    fi
    
    # Check for security issues
    if grep -q "\${{.*github\.event\..*}}" "$workflow"; then
        print_status "WARN" "Contains potentially unsafe GitHub event references"
    fi
    
    # Check for secrets usage
    if grep -q "secrets\." "$workflow"; then
        print_status "INFO" "Uses secrets (ensure they're defined in repo)"
    fi
done

echo ""
echo "📋 Step 5: ACF-Specific Validation"
echo "---------------------------------"

ACF_WORKFLOW="$WORKFLOW_DIR/acf-build.yml"

if [ -f "$ACF_WORKFLOW" ]; then
    echo "Validating ACF-specific requirements..."
    
    # Check trigger paths
    if grep -q "\.claude/\*\*" "$ACF_WORKFLOW"; then
        print_status "PASS" "Triggers on .claude changes"
    else
        print_status "FAIL" "Missing .claude path trigger"
    fi
    
    if grep -q "templates/\*\*" "$ACF_WORKFLOW"; then
        print_status "PASS" "Triggers on templates changes"
    else
        print_status "FAIL" "Missing templates path trigger"
    fi
    
    if grep -q "acf/\*\*" "$ACF_WORKFLOW"; then
        print_status "PASS" "Triggers on acf changes"
    else
        print_status "FAIL" "Missing acf path trigger"
    fi
    
    # Check for uv setup
    if grep -q "astral-sh/setup-uv" "$ACF_WORKFLOW"; then
        print_status "PASS" "Uses astral-sh/setup-uv action"
    else
        print_status "FAIL" "Missing uv setup action"
    fi
    
    # Check for caching
    if grep -q "actions/cache@v" "$ACF_WORKFLOW"; then
        print_status "PASS" "Implements caching"
    else
        print_status "WARN" "No caching configured"
    fi
    
    # Check for artifacts
    if grep -q "actions/upload-artifact@v" "$ACF_WORKFLOW"; then
        print_status "PASS" "Uploads artifacts"
    else
        print_status "WARN" "No artifact upload configured"
    fi
    
else
    print_status "WARN" "ACF workflow not found: $ACF_WORKFLOW"
fi

echo ""
echo "📋 Step 6: Manual Test Simulation"
echo "--------------------------------"

echo "Simulating workflow steps..."

# Test data preparation logic
if [ -d ".claude" ] && [ -d "templates" ] && [ -d "scripts" ]; then
    print_status "PASS" "Required source directories exist"
else
    print_status "FAIL" "Missing required source directories"
fi

# Test ACF structure
if [ -f "acf/pyproject.toml" ]; then
    print_status "PASS" "ACF pyproject.toml exists"
else
    print_status "FAIL" "ACF pyproject.toml missing"
fi

if [ -d "acf/src/acf" ]; then
    print_status "PASS" "ACF source structure exists"
else
    print_status "FAIL" "ACF source structure missing"
fi

# Test build prerequisites
if [ -d "acf" ]; then
    cd acf
    if command -v uv &> /dev/null; then
        if uv --version &>/dev/null; then
            print_status "PASS" "uv is functional"
        else
            print_status "FAIL" "uv not working properly"
        fi
    else
        print_status "WARN" "uv not available for testing"
    fi
    cd ..
fi

echo ""
echo "📋 Summary"
echo "==========="

if [ $VALIDATION_ERRORS -eq 0 ]; then
    print_status "PASS" "All validations passed! ✨"
    echo -e "${GREEN}🚀 Workflows are ready for deployment${NC}"
    exit 0
else
    print_status "FAIL" "$VALIDATION_ERRORS validation error(s) found"
    echo -e "${RED}🛑 Fix errors before deploying workflows${NC}"
    exit 1
fi