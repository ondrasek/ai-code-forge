# Decision Rationale: Issue 177 Worktree Branch Resolution

## Principle-Based Validation Summary

This document provides a comprehensive validation of the proposed worktree branch resolution implementation against fundamental software engineering principles.

## Principle Compliance Assessment

### SOLID Principles Analysis

#### Single Responsibility Principle (SRP) - ⚠️ VIOLATION
**Current State**: The `find_worktree_dir()` function in `worktree-launch.sh` handles multiple responsibilities:
- Directory name pattern matching
- Repository name resolution  
- Error messaging and user feedback
- Multiple match conflict resolution

**Proposed Change Impact**: Adding branch resolution will further violate SRP by adding git command execution and branch parsing responsibilities.

**Architectural Recommendation**: Implement strategy pattern with separate resolution functions:
```bash
resolve_worktree_path() {
    local input="$1"
    
    if [[ -d "$input" ]]; then
        resolve_by_directory "$input"
    elif git check-ref-format "refs/heads/$input" 2>/dev/null; then
        resolve_by_branch "$input"  
    else
        resolve_by_pattern "$input"
    fi
}
```

#### Open/Closed Principle (OCP) - ✗ CRITICAL VIOLATION
**Current State**: Adding branch resolution requires modifying core `find_worktree_dir()` function rather than extending existing behavior.

**Risk Assessment**: Future lookup methods (tags, commits, refs) will require continuous modifications to core logic, violating OCP fundamentally.

**Architectural Decision**: **BLOCK** current approach. Require strategy pattern implementation that allows extension without modification.

#### Liskov Substitution Principle (LSP) - ✓ COMPLIANT
**Assessment**: Branch arguments can substitute for directory arguments with identical function signatures and return behaviors.

**Validation**: Users can use branch names wherever directory names work without behavior changes.

#### Interface Segregation Principle (ISP) - ✓ COMPLIANT  
**Current Architecture**: Each worktree script maintains focused interfaces:
- `worktree-launch.sh`: Launch operations only
- `worktree-path.sh`: Path resolution only (security-restricted)
- `worktree-list.sh`: Listing operations only

**Recommendation**: Maintain separation. Do not merge branch resolution into `worktree-path.sh` due to security restrictions.

#### Dependency Inversion Principle (DIP) - ⚠️ VIOLATION
**Current State**: Direct dependency on git command output format parsing without abstraction layer.

**Risk**: Git version changes could break all worktree scripts simultaneously.

**Mitigation Required**: Implement git abstraction layer:
```bash
# High-level abstractions
get_worktree_by_branch() { ... }
get_all_worktrees() { ... }

# Implementation details isolated
parse_git_worktree_porcelain() { ... }
```

### Security Principles Assessment

#### Security by Design - ⚠️ ENHANCEMENT REQUIRED
**Current Security Model**: `worktree-path.sh` demonstrates excellent security practices:
- Strict input validation (issue numbers only)
- Path traversal prevention
- Symlink validation
- Canonical path enforcement

**Security Gap**: `worktree-launch.sh` lacks equivalent security validations despite accepting arbitrary user input.

**Critical Security Requirements**:
1. **Input Validation**: Branch names MUST be validated against `git check-ref-format`
2. **Path Security**: Resolved paths MUST stay within WORKTREE_BASE boundaries
3. **Command Injection Prevention**: Git operations MUST use proper argument arrays
4. **Race Condition Prevention**: Branch resolution should be atomic

#### Fail Fast Principle - ✓ PARTIALLY COMPLIANT
**Current Implementation**: Scripts use `set -euo pipefail` for early error detection.

**Enhancement Needed**: Add comprehensive input validation at function entry points rather than during processing.

#### Backward Compatibility - ✓ COMPLIANT
**Assessment**: Proposed changes maintain existing directory path behavior while adding branch resolution capability.

**Validation**: All current usage patterns continue to work unchanged.

### Additional Engineering Principles

#### Least Surprise Principle - ⚠️ NEEDS ATTENTION
**Current Behavior**: `./worktree-launch.sh main` fails unexpectedly because users assume branch name support.

**Expected Behavior**: Branch names should work intuitively alongside directory paths.

**Implementation Requirement**: Clear disambiguation between directory and branch arguments with intuitive fallback behavior.

## Principle Conflicts and Resolutions

### Security vs Functionality Conflict
**Conflict**: `worktree-path.sh` security restrictions vs branch resolution functionality needs.

**Analysis**: Security-focused `worktree-path.sh` intentionally restricts inputs to issue numbers only, while `worktree-launch.sh` needs broader input support.

**Resolution**: **Security takes precedence**. Maintain `worktree-path.sh` restrictions while implementing enhanced validation in `worktree-launch.sh`.

### Performance vs Maintainability Conflict  
**Conflict**: Strategy pattern may require additional git operations vs single optimized function.

**Analysis**: Current monolithic approach is harder to maintain, test, and extend.

**Resolution**: **Maintainability takes precedence**. One additional git call for branch resolution is acceptable for cleaner architecture.

## Architectural Decision

### RECOMMENDATION: REJECT Current Extension Approach

**Blocking Issues**:
1. **Open/Closed Principle Violation**: Modifying core function instead of extending behavior
2. **Single Responsibility Violation**: Adding complexity to already overloaded function  
3. **Security Inconsistency**: Different validation standards across similar scripts

### RECOMMENDED: Strategy Pattern Implementation

**New Architecture**:
```bash
#!/bin/bash
set -euo pipefail

# Strategy-based worktree resolution
resolve_worktree_strategy() {
    local input="$1"
    
    # Input classification with security validation
    if validate_directory_input "$input" && [[ -d "$input" ]]; then
        resolve_by_directory "$input"
    elif validate_branch_input "$input"; then
        resolve_by_branch "$input"
    elif validate_pattern_input "$input"; then
        resolve_by_pattern "$input"
    else
        print_error "Invalid input: $input"
        return 1
    fi
}

# Security-first validation functions
validate_branch_input() {
    local branch="$1"
    
    # Length validation
    if [[ ${#branch} -gt 256 ]]; then
        return 1
    fi
    
    # Git format validation
    if git check-ref-format "refs/heads/$branch" 2>/dev/null; then
        return 0
    fi
    
    return 1
}

# Isolated git operations
resolve_by_branch() {
    local branch="$1"
    
    # Use git abstraction
    local worktree_path
    worktree_path=$(git_find_worktree_by_branch "$branch") || return 1
    
    # Security validation of resolved path
    validate_worktree_path "$worktree_path" || return 1
    
    echo "$worktree_path"
}

# Git abstraction layer
git_find_worktree_by_branch() {
    local branch="$1"
    
    git worktree list --porcelain | awk -v branch="$branch" '
        /^worktree / { path = substr($0, 10) }
        /^branch refs\/heads\// && substr($0, 19) == branch { print path; exit }
    '
}
```

**Benefits**:
- ✅ Open/Closed Principle: New strategies don't modify existing code
- ✅ Single Responsibility: Each strategy has focused responsibility
- ✅ Dependency Inversion: Git operations abstracted away
- ✅ Security by Design: Each strategy validates its own inputs
- ✅ Testability: Each strategy can be unit tested independently

## Implementation Priority

### High Priority (Architecture Compliance)
1. **Implement Strategy Pattern**: Address OCP and SRP violations
2. **Create Git Abstraction Layer**: Address DIP violation and version brittleness
3. **Enhance Security Validation**: Achieve consistency with `worktree-path.sh` patterns

### Medium Priority (Feature Completion)
1. **Comprehensive Input Validation**: Branch name format validation
2. **Edge Case Handling**: Detached HEAD, missing branches, multiple matches
3. **Error Message Enhancement**: Clear user guidance for resolution failures

### Low Priority (Polish)
1. **Performance Optimization**: Minimize git command calls
2. **Documentation Updates**: Reflect new strategy-based architecture
3. **Integration Testing**: Validate across different worktree configurations

## Risk Mitigation

### Technical Risks
- **Git Version Compatibility**: Abstraction layer isolates version-specific implementations
- **Performance Impact**: Strategy overhead is minimal compared to git operations
- **Complexity Increase**: Better architecture simplifies long-term maintenance

### Security Risks
- **Input Validation**: Each strategy validates its specific input patterns
- **Path Security**: Centralized path validation prevents traversal attacks
- **Command Injection**: Abstracted git operations use safe argument passing

## Final Assessment

**Principle Adherence Score**: Current approach 4/10, Recommended approach 9/10

**Deployment Recommendation**: **BLOCK** current extension approach, **APPROVE** strategy pattern implementation

**Justification**: While the current extension would work functionally, it violates fundamental design principles and creates technical debt. The strategy pattern approach addresses all principle violations while providing better security, maintainability, and extensibility.

The additional implementation effort for proper architecture is justified by:
- Elimination of principle violations
- Enhanced security consistency  
- Future extensibility for new resolution methods
- Improved testability and maintenance
- Better separation of concerns

This represents the difference between a quick fix and a proper engineering solution.