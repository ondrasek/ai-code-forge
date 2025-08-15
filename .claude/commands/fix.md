---
description: Implement targeted solutions for identified issues, bugs, or improvements.
argument-hint: Optional issue description or FILES to fix.
allowed-tools: Task, Read, Edit, MultiEdit, Bash, Grep
---

# Issue Fix Implementation

!`git status`
!`git diff --name-only`

Implement targeted solutions for identified issues, bugs, or improvements with focused implementation rather than broad refactoring.

## Instructions

1. Parse $ARGUMENTS for fix parameters:
   - --issue "description" (specific issue to fix)
   - --safe (implement only low-risk fixes)
   - --test (include test implementation for fixes)
   - --memory (include historical fix patterns)
   - FILES... (specific files to fix)

2. Execute parallel clusters for fix implementation
1. **Fix Context Analysis**: context agent for understanding the issue and system impact
2. **Implementation Strategy**: code-cleaner for gap analysis and implementation approach
3. **Quality Validation**: patterns + principles for ensuring fix quality
4. **Risk Assessment**: critic for evaluating fix safety and side effects

PARAMETERS:
--issue "description" (specific issue to fix)
--safe (implement only low-risk fixes)
--test (include test implementation for fixes)
--memory (include historical fix patterns)
FILES... (specific files to fix)

INTELLIGENT_FIX_DETECTION:
1. **Issue parsing**: Extract specific problems from user description ("fix the memory leak", "resolve the security vulnerability")
2. **Error analysis**: Parse error messages, stack traces, or failure descriptions
3. **Context inference**: Understand the scope and impact of the fix needed
4. **Safety assessment**: Evaluate risk level of proposed fixes

OPTIMIZED_PARALLEL_CLUSTERS:
Implementation (2 agents): code-cleaner + context
Quality & Safety (3 agents): patterns + principles + critic

COORDINATION_PROTOCOL: All clusters execute simultaneously via single message with multiple Task() calls for efficient fix implementation. Total agents: 5 (focused on safe, quality fixes)

INTELLIGENT_OUTPUT:
- **Issue Analysis**: Clear understanding of the problem to be fixed
- **Implementation Plan**: Step-by-step approach to implementing the fix
- **Risk Assessment**: Safety evaluation and potential side effects
- **Quality Validation**: Adherence to code quality and design principles
- **Testing Strategy**: How to verify the fix works correctly
- **Documentation Updates**: Any documentation changes needed

## Fix Categories

### Bug Fixes
- **Logic Errors**: Incorrect algorithms or business logic
- **Runtime Errors**: Exceptions, crashes, null pointer issues
- **Edge Cases**: Handling of boundary conditions and error states
- **Data Issues**: Incorrect data handling or validation

### Security Fixes
- **Vulnerability Patches**: Address security weaknesses
- **Input Validation**: Sanitization and validation improvements
- **Access Control**: Permission and authorization fixes
- **Data Protection**: Encryption and privacy improvements

### Performance Fixes
- **Memory Leaks**: Resource cleanup and management
- **Inefficient Algorithms**: Performance optimization fixes
- **Database Issues**: Query optimization and connection fixes
- **Caching Problems**: Cache invalidation and strategy fixes

### Integration Fixes
- **API Issues**: External service integration problems
- **Dependency Problems**: Library conflicts and version issues
- **Configuration Errors**: Environment and setup fixes
- **Deployment Issues**: Production environment fixes

## Execution Workflow

### Phase 1: Fix Analysis & Planning
```
Task: "Analyze issue context and system impact" (context)
Task: "Plan implementation approach and identify gaps" (code-cleaner)
```

### Phase 2: Quality & Safety Validation
```
Task: "Validate fix quality and design adherence" (patterns + principles + critic)
```

**FOCUSED AGENT COUNT**: 5 agents total (implementation-focused coordination)

**MEMORY INTEGRATION**: Foundation agents store fix patterns and outcomes for continuous improvement

## Fix Output Structure

### Fix Summary
- **Issue**: Clear description of the problem being addressed
- **Scope**: Files and components affected by the fix
- **Risk Level**: Safety assessment of the proposed fix
- **Implementation Strategy**: Approach and methodology for the fix

### Implementation Details
- **Code Changes**: Specific modifications to implement
- **Configuration Updates**: Any settings or environment changes needed
- **Database Changes**: Schema or data modifications if required
- **Documentation Updates**: README, API docs, or comment changes

### Validation Plan
- **Testing Strategy**: How to verify the fix works correctly
- **Regression Testing**: Ensure the fix doesn't break existing functionality
- **Performance Impact**: Assessment of any performance changes
- **Rollback Plan**: How to revert if issues arise

### Quality Assurance
- **Code Review Points**: Key areas for review focus
- **Design Principle Adherence**: How the fix aligns with good practices
- **Security Considerations**: Any security implications of the fix
- **Maintainability**: Long-term implications and maintenance needs

## Safety Guidelines

### Low-Risk Fixes (Safe by Default)
- **Logging Improvements**: Adding debugging or monitoring
- **Documentation Updates**: Comments, README, API docs
- **Code Cleanup**: Removing dead code, formatting fixes
- **Test Additions**: Adding test coverage without changing logic

### Medium-Risk Fixes (Requires Careful Review)
- **Bug Fixes**: Logic corrections that might have side effects
- **Performance Optimizations**: Changes that alter execution patterns
- **Refactoring**: Code structure changes that maintain functionality
- **Configuration Changes**: Settings that affect system behavior

### High-Risk Fixes (Expert Review Required)
- **Security Patches**: Changes affecting authentication, authorization, or data protection
- **Database Schema Changes**: Structural modifications to data storage
- **API Changes**: Modifications that affect external interfaces
- **Core Algorithm Changes**: Fundamental logic modifications

## Related Commands

- `/review` - Comprehensive analysis to identify issues needing fixes
- `/refactor` - Broader code improvements and restructuring
- `/test` - Implement testing for fixes and validation
- `/security` - Security-focused fixes and vulnerability patches
- `/performance` - Performance-specific fixes and optimizations