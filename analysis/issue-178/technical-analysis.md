# Issue #178 Technical Analysis: Worktree Watch Regression

## Problem Summary

The `worktree watch` command has regressed functionality where:
1. **Missing PR Association Display**: Fails to display pull requests associated with issues/branches
2. **Incomplete Process Display**: Only shows Claude Code processes instead of all processes working in a branch

## Current Behavior Analysis

Based on testing the current implementation (`./scripts/worktree/worktree-watch.sh --test`):

### What Works Correctly
- ✅ Issue detection and GitHub API integration
- ✅ Issue title, labels, and URL display
- ✅ Claude process detection (`pgrep -f "claude"`)
- ✅ Process metrics (CPU, memory, working directory)
- ✅ Branch and worktree path display
- ✅ Visual formatting and emojis

### What's Broken/Missing

#### 1. PR Association Display Issue
**Root Cause**: Code IS fetching PR data correctly, but NO PRs exist for current test issues.

**Evidence**:
```bash
# Checked issue 178 directly:
gh api repos/ondrasek/ai-code-forge/issues/178 | jq -r '.pull_request.url // "no-pr"'
# Result: "no-pr"

# Checked for PRs matching issue numbers:
gh pr list --repo ondrasek/ai-code-forge --search "178 OR 191 OR 195" --json number,title,headRefName,state
# Result: []
```

**Conclusion**: The PR association logic works correctly. Issues 178, 191, 195 simply don't have associated PRs yet. This is a **misidentification of regression**.

#### 2. Process Monitoring Limitation
**Root Cause**: `find_worktree_processes()` function only searches for "claude" processes.

**Current Implementation** (lines 213-234):
```bash
# Find Claude processes associated with a worktree
find_worktree_processes() {
    local worktree_path="$1"
    local associated_pids=""
    
    # Get all Claude processes - LIMITATION: Only "claude" processes
    local claude_pids
    if claude_pids=$(pgrep -f "claude" 2>/dev/null); then
        while IFS= read -r pid; do
            [[ -z "$pid" ]] && continue
            
            local cwd=$(get_process_cwd "$pid")
            
            # Check if process working directory is within this worktree
            if [[ "$cwd" == "$worktree_path"* ]]; then
                associated_pids="$associated_pids $pid"
            fi
        done <<< "$claude_pids"
    fi
    
    echo "$associated_pids"
}
```

**Identified Issue**: The function name suggests it should find "worktree processes" but only searches for processes matching "claude".

## Architecture Overview

### File Structure
```
/workspace/worktrees/ai-code-forge/issue-178/
├── scripts/worktree/
│   ├── worktree.sh                    # Main command dispatcher  
│   ├── worktree-watch.sh              # Watch implementation (MAIN FILE)
│   ├── worktree-inspect.sh            # Process inspection utilities
│   └── tests/test-worktree-inspect.sh # Test suite
│
├── cli/src/ai_code_forge/data/acf/scripts/worktree/
│   └── worktree-watch.sh              # Duplicate CLI version (identical)
```

### Key Components

#### 1. Main Entry Point
- **File**: `/scripts/worktree/worktree.sh`
- **Line**: 143-149 (watch command routing)
- **Function**: Dispatches `watch` subcommand to `worktree-watch.sh`

#### 2. Core Watch Implementation
- **File**: `/scripts/worktree/worktree-watch.sh`
- **Key Functions**:
  - `get_issue_info()` (lines 81-163): GitHub API integration with caching
  - `find_worktree_processes()` (lines 213-234): Process discovery (REGRESSION HERE)
  - `display_worktree_info()` (lines 275-391): Main display logic
  - `show_worktree_status()` (lines 236-273): Orchestrates display

#### 3. PR Association Logic
- **Location**: `get_issue_info()` function, lines 124-142
- **Logic**: Uses progressive discovery - only fetches PR data if issue has associated PR
- **Status**: **WORKING CORRECTLY** - no regression here

#### 4. Process Detection Logic  
- **Location**: `find_worktree_processes()` function, lines 213-234
- **Current Search**: `pgrep -f "claude"`
- **Status**: **LIMITED SCOPE** - only finds Claude processes

## Historical Context Analysis

### Recent Changes
From git history analysis:

#### Commit 58ea417 (Aug 10, 2025)
- **Enhancement**: Progressive discovery and rich status display
- **Changes**: Improved GitHub API integration, caching, visual display
- **Impact**: No regression in PR logic - this was enhancement only

#### Commit 19d1d33 (Aug 10, 2025)  
- **Integration**: Migrated monitoring from standalone tool to worktree subcommand
- **Original Implementation**: Already had `pgrep -f "claude"` limitation
- **Impact**: The process scope limitation existed from the original integration

### Process Monitoring Evolution
1. **Original Design**: Focused specifically on "Claude Code Monitoring Dashboard"
2. **Integration**: Became worktree watch subcommand but retained Claude-only focus
3. **Current State**: Function name suggests broader scope but implementation is Claude-specific

## Root Cause Analysis

### Issue 1: PR Association "Regression"
**Finding**: **NOT A REGRESSION** - PR association logic works correctly
- Code properly checks for PR associations via `pull_request.url` field
- Progressive discovery correctly fetches PR data when available  
- Current issues (178, 191, 195) simply don't have PRs created yet
- Expected behavior: PR info appears when PRs exist

### Issue 2: Process Display Limitation  
**Finding**: **DESIGN LIMITATION** from original implementation
- Function was designed for "Claude Code Monitoring Dashboard"
- Retained Claude-specific focus when integrated into worktree system
- Function name `find_worktree_processes()` suggests broader scope but implementation is narrow
- Should monitor all development processes in worktree, not just Claude

## Recommended Solutions

### Issue 1: PR Association (No Action Needed)
- PR association works correctly
- PRs will appear when issues have associated PRs
- Consider creating PRs for issues to validate display

### Issue 2: Expand Process Monitoring Scope

**Current Limited Search**:
```bash
if claude_pids=$(pgrep -f "claude" 2>/dev/null); then
```

**Proposed Expanded Search**:
```bash
# Find all development-related processes in worktree
find_worktree_processes() {
    local worktree_path="$1"
    local associated_pids=""
    
    # Search patterns for development processes
    local process_patterns=(
        "claude"           # Claude Code
        "code"            # VS Code
        "vim\|nvim"       # Vim/Neovim
        "emacs"           # Emacs
        "node"            # Node.js processes
        "python"          # Python processes
        "bash\|zsh\|fish" # Shell processes
        "git"             # Git processes
    )
    
    for pattern in "${process_patterns[@]}"; do
        local pids
        if pids=$(pgrep -f "$pattern" 2>/dev/null); then
            while IFS= read -r pid; do
                [[ -z "$pid" ]] && continue
                
                local cwd=$(get_process_cwd "$pid")
                
                # Check if process working directory is within this worktree
                if [[ "$cwd" == "$worktree_path"* ]]; then
                    # Avoid duplicates
                    if [[ " $associated_pids " != *" $pid "* ]]; then
                        associated_pids="$associated_pids $pid"
                    fi
                fi
            done <<< "$pids"
        fi
    done
    
    echo "$associated_pids"
}
```

## Dependencies and Integration Points

### External Dependencies
- **GitHub CLI (`gh`)**: Required for issue/PR data
- **jq**: JSON processing for API responses  
- **git**: Worktree listing and repository operations
- **ps**: Process metrics and information
- **proc filesystem**: Process working directory detection

### Internal Integration
- **worktree.sh**: Command routing and argument parsing
- **worktree-inspect.sh**: Process inspection utilities (different scope)
- **CLI packaging**: Identical copy in `cli/src/ai_code_forge/data/acf/`

### GitHub API Integration
- **Rate Limiting**: 1-minute cache TTL (configurable via --ttl)
- **Progressive Discovery**: Only fetches PR data for issues with PRs
- **Fallback**: Graceful degradation when GitHub API unavailable

## Testing Strategy

### Validation Steps
1. **PR Association Testing**: Create a PR for issue 178 and verify display
2. **Process Monitoring Testing**: Start various development processes in worktree and verify detection
3. **Regression Testing**: Ensure existing Claude process detection still works
4. **Cache Testing**: Verify GitHub API caching behavior
5. **Error Handling**: Test behavior with network issues, missing dependencies

### Test Cases
```bash
# Test current behavior
./scripts/worktree/worktree-watch.sh --test

# Test with PR (after creating PR for issue 178)
./scripts/worktree/worktree-watch.sh --test

# Test process detection expansion (after fix)
# Start vim in worktree and verify detection
```

## Conclusion

**Issue #178 Analysis Summary**:
1. **PR Association**: NOT a regression - works correctly, PRs just don't exist for current issues
2. **Process Display**: Design limitation requiring expansion beyond Claude-only processes
3. **Priority**: Medium - functional system with scope limitation rather than broken functionality
4. **Solution**: Expand `find_worktree_processes()` to detect broader range of development processes

The "regression" is actually a misunderstanding of expected behavior combined with a legitimate design limitation that needs addressing.