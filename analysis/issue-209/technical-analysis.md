# GitHub CLI & Bash Scripting Technology Analysis for Issue #209

## Repository Analysis

**Technology Stack Detected:**
- **Primary**: Bash/Shell Scripting (command implementations, GitHub CLI operations)
- **Secondary**: Markdown (agent definitions, command specifications)
- **Infrastructure**: Git operations, GitHub API integration

**Technology Guidelines Loaded:**
- `@templates/stacks/bash.md` - Comprehensive shell scripting standards

## GitHub CLI Integration Patterns

### Current Implementation Analysis

Based on analysis of `.claude/agents/specialists/github-issues-workflow.md` and `.claude/commands/issue/` implementations:

**Established Patterns:**
1. **Dynamic Label Discovery** (MANDATORY):
   ```bash
   gh label list --repo ondrasek/ai-code-forge --json name,color,description
   ```
   - NEVER hardcode label names
   - Always verify labels exist before operations

2. **Issue Operations Pattern**:
   ```bash
   gh issue list --repo ondrasek/ai-code-forge --search "keyword"
   gh issue view $issue_number --repo ondrasek/ai-code-forge --json state,title,body
   gh issue create --repo ondrasek/ai-code-forge --title "..." --body "..."
   gh issue edit --repo ondrasek/ai-code-forge --add-label <label>
   gh issue comment --repo ondrasek/ai-code-forge --body "..."
   ```

3. **Repository Context Pattern**:
   ```bash
   REPO="ondrasek/ai-code-forge"  # Central repository target
   ```

### Error Handling Patterns from Current Architecture

**Authentication Diagnostics**:
```bash
gh auth status
gh auth list  
gh repo view ondrasek/ai-code-forge --json name,owner
```

**Network Connectivity Testing**:
```bash
ping -c 3 github.com
curl -I https://github.com
```

**Issue Validation with Recovery**:
```bash
if ! gh issue view "$ISSUE_NUM" --repo ondrasek/ai-code-forge >/dev/null 2>&1; then
    echo "🔍 Issue #$ISSUE_NUM not accessible. Running diagnostics..."
    # Systematic diagnostic approach
fi
```

## Bash Scripting Standards (from `@templates/stacks/bash.md`)

### Mandatory Security Requirements

**Script Header Pattern**:
```bash
#!/bin/bash
set -euo pipefail  # MANDATORY: Exit on error, undefined vars, pipe failures
```

**Error Handling Framework**:
```bash
cleanup() {
    local exit_code=$?
    echo "Cleaning up..." >&2
    
    # Kill child processes
    for pid in "${CHILD_PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    
    # Remove temp files
    [[ -n "${TEMP_DIR:-}" ]] && rm -rf "$TEMP_DIR"
    exit $exit_code
}

trap cleanup EXIT
trap 'cleanup; exit 130' INT
trap 'cleanup; exit 143' TERM
```

**Input Validation (SECURITY CRITICAL)**:
```bash
validate_input() {
    local input="$1"
    
    # Prevent path traversal
    if [[ "$input" == *".."* ]] || [[ "$input" =~ ^/ ]]; then
        echo "ERROR: Invalid input contains unsafe characters" >&2
        return 1
    fi
    
    # Whitelist allowed characters
    if [[ ! "$input" =~ ^[a-zA-Z0-9._/-]+$ ]]; then
        echo "ERROR: Invalid characters in input" >&2
        return 1
    fi
    
    return 0
}
```

### Variable Handling Standards

**Always Quote Variables**:
```bash
# Correct patterns
echo "$variable"
cp "$source_file" "$destination_dir"
CONFIG_FILE="${CONFIG_FILE:-config.json}"
: "${REQUIRED_VAR:?REQUIRED_VAR must be set}"
```

### API Integration Patterns

**Robust HTTP Operations**:
```bash
api_call() {
    local url="$1"
    local method="${2:-GET}"
    local max_retries=3
    local retry_count=0
    
    while [[ $retry_count -lt $max_retries ]]; do
        local response
        response=$(curl -s -w "%{http_code}" -X "$method" "$url")
        
        local http_code="${response: -3}"
        response="${response%???}"
        
        case "$http_code" in
            200|201|204)
                echo "$response"
                return 0
                ;;
            5*)
                log_warn "Server error ($http_code), retrying..."
                ;;
            *)
                log_error "API call failed with status $http_code"
                return 1
                ;;
        esac
        
        ((retry_count++))
        sleep $((retry_count * 2))
    done
    
    return 1
}
```

## Cross-Repository Portability Patterns

### Repository Detection Framework

**Safe Repository Detection**:
```bash
detect_repository() {
    local repo_url=""
    
    # Try multiple detection methods
    if command -v gh >/dev/null 2>&1; then
        repo_url=$(gh repo view --json owner,name --jq '"owner.login + "/" + .name"' 2>/dev/null)
    fi
    
    if [[ -z "$repo_url" ]] && [[ -d ".git" ]]; then
        repo_url=$(git config --get remote.origin.url | sed -E 's/.*github\.com[:/]([^/]+\/[^/]+)\.git/\1/')
    fi
    
    echo "${repo_url:-unknown}"
}
```

**Environment-Agnostic Configuration**:
```bash
# Detect and adapt to different environments
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
REPO_NAME="$(detect_repository)"

# Flexible configuration loading
CONFIG_FILE="${CONFIG_FILE:-$REPO_ROOT/.claude/config.json}"
```

### Portable GitHub CLI Patterns

**Authentication Detection**:
```bash
ensure_github_auth() {
    if ! gh auth status >/dev/null 2>&1; then
        echo "ERROR: GitHub CLI authentication required" >&2
        echo "Run: gh auth login" >&2
        return 1
    fi
    
    # Verify repository access
    if ! gh repo view "$REPO_NAME" >/dev/null 2>&1; then
        echo "ERROR: Cannot access repository $REPO_NAME" >&2
        echo "Check repository permissions" >&2
        return 1
    fi
}
```

## Agent Architecture Patterns

### Current Agent Structure Analysis

**Agent Definition Pattern** (from analysis):
```yaml
---
name: agent-name
description: "Agent purpose and trigger conditions"  
tools: Bash, Grep, Glob, Read, Edit, MultiEdit
---
```

**Task Delegation Pattern**:
```markdown
Use Task tool to delegate to [agent-name] agent:
- Specific instructions for agent
- Expected outcomes
- Integration requirements
```

### Cross-Agent Communication Standards

**Context Isolation Protocol** (from git-workflow agent):
```markdown
<operational_rules priority="CRITICAL">
<context_separation>All complex analysis MUST happen in agent context</context_separation>
<autonomous_operation>Agent makes independent decisions without requiring main context confirmation</autonomous_operation>
</operational_rules>
```

**Output Format Standardization**:
```
OPERATION RESULT: [SUCCESS/FAILURE]

DETAILS:
- Status: [specific status information]
- Actions: [actions taken]  
- Results: [measurable outcomes]

NEXT STEPS: [clear action items]
```

## Security & Error Handling Recommendations

### GitHub CLI Security Patterns

**Safe Command Execution**:
```bash
safe_gh_command() {
    local cmd="$1"
    shift
    local -a args=("$@")
    
    # Validate GitHub CLI is available
    if ! command -v gh >/dev/null 2>&1; then
        echo "ERROR: GitHub CLI not found" >&2
        return 1
    fi
    
    # Validate authentication
    ensure_github_auth || return 1
    
    # Execute with error handling
    if ! gh "$cmd" "${args[@]}" 2>/dev/null; then
        echo "ERROR: gh $cmd command failed" >&2
        echo "Attempting diagnostic recovery..." >&2
        diagnose_gh_error "$cmd" "${args[@]}"
        return 1
    fi
}
```

### Cross-Repository Error Recovery

**Repository State Validation**:
```bash
validate_repository_state() {
    # Check if we're in a git repository
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        echo "ERROR: Not in a git repository" >&2
        return 1
    fi
    
    # Check for unsaved changes that might interfere
    if [[ -n "$(git status --porcelain)" ]]; then
        echo "WARNING: Unsaved changes detected" >&2
        echo "Commit or stash changes before GitHub operations" >&2
    fi
    
    # Validate remote connectivity
    if ! git fetch --dry-run >/dev/null 2>&1; then
        echo "WARNING: Cannot reach remote repository" >&2
        echo "Check network connectivity and authentication" >&2
    fi
    
    return 0
}
```

## Technology Stack Recommendations

### Required Tools Verification

**Dependency Checking Pattern**:
```bash
check_dependencies() {
    local -a required_tools=("gh" "git" "jq" "curl")
    local missing_tools=()
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        echo "ERROR: Missing required tools: ${missing_tools[*]}" >&2
        echo "Install missing tools and retry" >&2
        return 1
    fi
    
    return 0
}
```

### Version Compatibility Patterns

**GitHub CLI Version Detection**:
```bash
verify_gh_version() {
    local min_version="2.0.0"
    local current_version
    
    current_version=$(gh --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1)
    
    if ! version_compare "$current_version" "$min_version"; then
        echo "WARNING: GitHub CLI version $current_version may not support all features" >&2
        echo "Consider upgrading to $min_version or later" >&2
    fi
}

version_compare() {
    local version1="$1"
    local version2="$2"
    
    # Simple version comparison for major.minor.patch format
    [[ "$(printf '%s\n' "$version1" "$version2" | sort -V | head -n1)" == "$version2" ]]
}
```

## Implementation Priorities

### High Priority Patterns (Apply First)
1. **Strict Error Handling**: All scripts must use `set -euo pipefail`
2. **Input Validation**: Security-critical for all external inputs  
3. **GitHub Authentication**: Mandatory verification before operations
4. **Dynamic Label Discovery**: Never hardcode GitHub labels

### Medium Priority Patterns (Architecture)
1. **Repository Detection**: Portable cross-repository patterns
2. **Agent Communication**: Standardized output formats
3. **Logging Framework**: Comprehensive operation tracking  
4. **Process Management**: Child process tracking and cleanup

### Low Priority Optimizations (Performance)
1. **API Rate Limiting**: Conservative request budgeting
2. **Caching Strategies**: Reduce redundant GitHub API calls
3. **Parallel Processing**: Batch operations for efficiency
4. **Connection Pooling**: Optimize network resource usage

This analysis provides comprehensive technology guidelines for implementing robust GitHub CLI scripting with proper bash standards, error handling, and cross-repository portability patterns suitable for Claude Code agent architecture.