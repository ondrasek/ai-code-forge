# Implementation Notes - Issue #178 Worktree Watch Regression

## Current Status: Analysis Phase Complete

### Key Discoveries
1. **Issue #1 (PR Association)**: NOT a regression - functionality works correctly, test issues simply lack PRs
2. **Issue #2 (Process Display)**: Real design limitation - only shows Claude processes instead of all development processes

### Critical Security Requirements Identified
- **Sensitive Data Filtering**: Process command lines may expose passwords, tokens, API keys
- **Permission Checking**: Graceful degradation when insufficient privileges
- **Process Relevance Filtering**: Exclude system/kernel processes from monitoring
- **Privacy Controls**: User consent mechanisms for expanded monitoring

## Implementation Plan (Security-First Approach)

### Phase 1: Validation and Security Foundation
**Priority**: HIGH (Blocking)

1. **Validate PR Regression Claim**
   - Create test PR for issue #178 to verify if PR association actually fails
   - Test current worktree watch behavior with actual PRs
   - Document real vs perceived regression

2. **Implement Security Framework** 
   ```bash
   # Add to worktree-watch.sh
   filter_sensitive_data() {
       # Remove passwords, tokens, keys from command lines
       # Pattern matching for common sensitive patterns
   }
   
   check_process_permissions() {
       # Verify read access to /proc entries
       # Graceful degradation for restricted environments
   }
   ```

3. **Create Safe Process Patterns**
   ```bash
   # Expand from current:
   pgrep -f "claude"
   
   # To secure multi-pattern (Phase 1 - minimal expansion):
   SAFE_PATTERNS=("claude" "code" "vim" "nano")
   for pattern in "${SAFE_PATTERNS[@]}"; do
       pgrep -f "$pattern" | xargs -I {} check_process_safety {}
   done
   ```

### Phase 2: Process Discovery Expansion  
**Priority**: MEDIUM (After security validation)

1. **Multi-Pattern Discovery**
   - Implement comprehensive process type detection
   - Add working directory validation using `/proc/PID/cwd`
   - Cross-platform compatibility (Linux, macOS, Windows)

2. **Performance Optimization**
   - Batch process operations to minimize system calls
   - Implement intelligent caching (extend from current 1-minute TTL)
   - Background refresh with async updates

3. **Enhanced Display Logic**
   - Group processes by type (editors, shells, languages, tools)
   - Color coding and emoji indicators for process categories
   - Resource usage display (memory, CPU) if available

### Phase 3: Advanced Features
**Priority**: LOW (Enhancement)

1. **Interactive Mode**
   - Real-time updates with keyboard shortcuts
   - Filter controls for process types
   - Detailed process inspection

2. **Testing Framework Integration**
   - ShellSpec test suite for regression prevention
   - Mock process environments for CI/CD testing
   - Performance benchmarking

## File Locations and Responsibilities

### Primary Implementation Files
- **Main**: `/scripts/worktree/worktree-watch.sh` (lines 213-234 for process discovery)
- **CLI Duplicate**: `/cli/src/ai_code_forge/data/acforge/scripts/worktree/worktree-watch.sh` (keep synchronized)
- **Entry Point**: `/scripts/worktree/worktree.sh` (lines 143-149 for command routing)

### Key Functions to Modify
```bash
# Current function at line 213:
find_worktree_processes() {
    # Current: pgrep -f "claude"
    # Target: secure multi-pattern discovery
}

# Current function at line 81:  
get_issue_info() {
    # Already functional - may need PR display enhancement
}
```

### Dependencies and Integration Points
- **GitHub CLI**: Already configured with proper caching
- **jq**: JSON processing for API responses  
- **git**: Worktree operations and branch detection
- **System Tools**: `pgrep`, `lsof`, `/proc` filesystem access

## Security Implementation Details

### Sensitive Data Patterns to Filter
```bash
SENSITIVE_PATTERNS=(
    "-p [A-Za-z0-9]{8,}"           # Passwords
    "token=[A-Za-z0-9-]+"          # API tokens  
    "key=[A-Za-z0-9-]+"            # API keys
    "password=[^[:space:]]+"       # Password parameters
    "secret=[^[:space:]]+"         # Secret parameters
    "Authorization: Bearer [^[:space:]]+" # Auth headers
)
```

### Permission Checking Strategy
```bash
check_process_access() {
    local pid=$1
    if [[ -r "/proc/$pid/cmdline" ]] && [[ -r "/proc/$pid/cwd" ]]; then
        return 0  # Safe to read
    else
        return 1  # Skip this process
    fi
}
```

## Testing Strategy

### Validation Tests (Immediate)
1. Create actual PR for issue #178 and verify PR association display
2. Test current process discovery with various Claude Code configurations
3. Verify security filtering with mock sensitive processes

### Regression Prevention (Phase 2)
1. ShellSpec test suite covering:
   - Process discovery accuracy
   - Security filtering effectiveness  
   - Performance benchmarks
   - Cross-platform compatibility

### Integration Tests (Phase 3)
1. CI/CD pipeline with automated worktree testing
2. Performance regression detection
3. Security vulnerability scanning

## Progress Tracking

### Completed ✅
- Complete technical analysis and architecture understanding
- Security requirements identification and framework design
- Implementation approach validation through multiple agent perspectives
- Comprehensive analysis documentation in `analysis/issue-178/` directory

### In Progress 🟡
- Final documentation consolidation
- Validation test preparation

### Pending ⏳
- Create test PR to validate PR association regression claim
- Implement security framework for process discovery
- Expand process monitoring with security-first approach
- Add comprehensive testing suite with ShellSpec

### Blocked 🔴
- Implementation cannot proceed until security framework is validated
- Process expansion blocked pending sensitive data filtering implementation

## Risk Mitigation

### High Priority Risks
1. **Data Exposure**: Sensitive information in process command lines
   - **Mitigation**: Comprehensive pattern-based filtering before display
   
2. **Performance Impact**: Broader process scanning overhead
   - **Mitigation**: Batch operations, intelligent caching, async updates

3. **Permission Failures**: Insufficient access to process information
   - **Mitigation**: Graceful degradation, informative error messages

### Medium Priority Risks  
1. **Cross-Platform Compatibility**: Different process monitoring approaches
   - **Mitigation**: Progressive feature detection with fallbacks

2. **Maintenance Overhead**: Dual file synchronization requirement
   - **Mitigation**: Automated sync verification in CI/CD pipeline

## Dependencies and Constraints

### System Requirements
- Linux/macOS/Windows with `/proc` or equivalent process information
- Git worktree support (Git 2.5+)
- GitHub CLI for PR association functionality
- Shell environment with `pgrep`, `jq` availability

### Project Constraints
- Must maintain backward compatibility with existing command interface
- Cannot break existing Claude process monitoring functionality  
- Must update both script locations simultaneously
- Security-first approach required due to development environment data sensitivity