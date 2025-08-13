# Specialized Agent Trigger Conditions

## Overview
Defines precise trigger conditions for the 12 specialized agents in the core-satellite architecture. These agents activate automatically based on user input patterns, context, and task requirements.

## Trigger Classification System

### Priority 1: User Intent Keywords (Direct activation)
**High confidence triggers** - User explicitly requests specialized capability

### Priority 2: Context Pattern Detection (Automatic activation)  
**Medium confidence triggers** - Context suggests specialized agent would add value

### Priority 3: Task Complexity Analysis (Conditional activation)
**Low confidence triggers** - Complex scenarios where specialized expertise may help

## Specialized Agent Trigger Definitions

### 1. **explorer** - Solution Space Analysis
**Primary Purpose**: Generate multiple solution alternatives and comprehensive trade-off analysis

#### Priority 1 Triggers (User Intent - Always activate)
- User asks: "what are my options", "alternatives", "different ways to", "compare approaches"
- User requests: "pros and cons", "which approach", "evaluate options"
- Questions containing: "or", "versus", "vs", "alternatives", "options"

#### Priority 2 Triggers (Context Pattern - Auto activate)
- Architecture decisions being made (detected by: "design", "architect", "structure")
- Technology selection scenarios (detected by: "should I use", "better choice")
- Multiple possible implementations identified by core agents

#### Priority 3 Triggers (Complexity - Conditional)
- Core agents identify >3 viable approaches
- **critic** agent identifies significant trade-offs
- **resolver** agent encounters complex conflicts

**Example Activation:**
```
User: "What are the different ways I can implement user authentication?"
→ Triggers explorer (Priority 1: "different ways")
```

### 2. **hypothesis** - Scientific Debugging  
**Primary Purpose**: Systematic hypothesis formation for complex debugging scenarios

#### Priority 1 Triggers (User Intent - Always activate)
- User asks: "why does this happen", "strange behavior", "it should work but doesn't"
- Debugging phrases: "investigation", "root cause", "hypothesis", "theory"
- Performance mysteries: "why is this slow", "unexpected behavior"

#### Priority 2 Triggers (Context Pattern - Auto activate)
- **researcher** finds error messages without clear solutions
- **patterns** detects anomalous code behaviors
- Complex debugging scenarios (>3 potential causes identified)

#### Priority 3 Triggers (Complexity - Conditional)
- Multiple debugging theories proposed by core agents
- System behavior doesn't match expected patterns
- Intermittent or hard-to-reproduce issues

**Example Activation:**
```
User: "My API randomly returns 500 errors but I can't figure out why"
→ Triggers hypothesis (Priority 1: investigation needed)
```

### 3. **whisper** - Code Polishing
**Primary Purpose**: Micro-improvements in code quality through systematic cleanup

#### Priority 1 Triggers (User Intent - Always activate)
- User requests: "clean up code", "fix formatting", "polish the code", "improve code quality"
- Style requests: "consistent naming", "fix typos", "formatting"

#### Priority 2 Triggers (Context Pattern - Auto activate)
- **patterns** agent detects style inconsistencies during analysis
- File reviews reveal formatting issues, typos, or naming inconsistencies
- Code quality issues that don't require architectural changes

#### Priority 3 Triggers (Complexity - Conditional)
- After major code changes (cleanup recommended)
- Before code reviews or releases
- When preparing code for sharing/documentation

**Example Activation:**
```
User: "This code works but looks messy"
→ Triggers whisper (Priority 2: style cleanup needed)
```

### 4. **completer** - Implementation Finishing
**Primary Purpose**: Complete TODOs, partial implementations, and missing functionality

#### Priority 1 Triggers (User Intent - Always activate)
- User asks: "finish this", "complete implementation", "what's missing"
- Direct completion requests: "implement the TODO", "fill in the gaps"

#### Priority 2 Triggers (Context Pattern - Auto activate)
- Code analysis reveals TODO/FIXME/HACK comments
- Functions throwing "not implemented" errors detected
- **patterns** agent identifies incomplete implementations

#### Priority 3 Triggers (Complexity - Conditional)
- Missing error handling identified by core agents
- Incomplete test coverage for critical functionality
- Edge cases not handled in implementation

**Example Activation:**
```
User: "This function has several TODOs that need implementing"
→ Triggers completer (Priority 1: explicit completion request)
```

### 5. **docs** - Documentation Synchronization
**Primary Purpose**: Automatically sync documentation with code changes

#### Priority 1 Triggers (User Intent - Always activate)
- User requests: "update the docs", "sync documentation", "fix the README"
- Documentation-specific: "API docs", "changelog", "documentation"

#### Priority 2 Triggers (Context Pattern - Auto activate)
- Code changes affect public APIs (detected by function signature changes)
- New features added (detected by new file creation or major additions)
- Configuration changes that affect setup/usage

#### Priority 3 Triggers (Complexity - Conditional)
- After completing major implementations
- Breaking changes identified by core agents
- Before releases or when preparing for sharing

**Example Activation:**
```
Context: New API endpoint added to codebase
→ Triggers docs (Priority 2: API change detected)
```

### 6. **constraints** - Multi-Constraint Optimization
**Primary Purpose**: Find solutions within complex, competing constraints

#### Priority 1 Triggers (User Intent - Always activate)
- User mentions: "requirements conflict", "limited resources", "must work with legacy"
- Constraint language: "constraints", "limitations", "requirements", "restrictions"

#### Priority 2 Triggers (Context Pattern - Auto activate)
- **resolver** agent identifies competing requirements
- Performance vs features trade-offs identified
- Resource limitations detected (memory, CPU, time, budget)

#### Priority 3 Triggers (Complexity - Conditional)
- >3 competing requirements identified by core agents
- Complex optimization scenarios
- System design with multiple conflicting goals

**Example Activation:**
```
User: "I need high performance but also maintainable code with limited memory"
→ Triggers constraints (Priority 1: multiple competing constraints)
```

### 7. **performance** - Performance Optimization
**Primary Purpose**: Systematic performance analysis and optimization strategies

#### Priority 1 Triggers (User Intent - Always activate)
- User reports: "performance issues", "slow code", "optimization needed"
- Performance terms: "bottleneck", "latency", "throughput", "memory leak"

#### Priority 2 Triggers (Context Pattern - Auto activate)  
- **patterns** agent detects performance anti-patterns (N+1 queries, unnecessary loops)
- **researcher** finds performance-related error messages
- Algorithmic complexity concerns identified

#### Priority 3 Triggers (Complexity - Conditional)
- System scaling requirements
- Performance regression detected
- Resource usage optimization needed

**Example Activation:**
```
User: "My dashboard is loading slowly"
→ Triggers performance (Priority 1: performance issue reported)
```

### 8. **testing** - Test Strategy Development
**Primary Purpose**: Comprehensive testing strategy and test case generation

#### Priority 1 Triggers (User Intent - Always activate)
- User asks: "test strategy", "how should I test this", "test cases", "testing approach"
- Testing terms: "coverage", "edge cases", "test generation"

#### Priority 2 Triggers (Context Pattern - Auto activate)
- **completer** identifies missing test coverage
- New critical functionality implemented
- **critic** identifies high-risk code requiring testing

#### Priority 3 Triggers (Complexity - Conditional)
- Complex business logic requiring validation
- Integration points needing testing
- Before releases or major deployments

**Example Activation:**
```
User: "What's the best way to test this payment processing code?"
→ Triggers testing (Priority 1: explicit test strategy request)
```

### 9. **git-troubleshooter** - Git Problem Resolution
**Primary Purpose**: Systematic git diagnosis and resolution

#### Priority 1 Triggers (User Intent - Always activate)
- Git errors: "merge conflict", "can't push", "git error", "repository corrupted"
- Git problems: "lost commits", "detached HEAD", "git command failures"

#### Priority 2 Triggers (Context Pattern - Auto activate)
- Git operations fail during Simple Git Protocol execution
- Repository state issues detected
- Version control anomalies identified

#### Priority 3 Triggers (Complexity - Conditional)
- Complex merge scenarios
- Repository history issues
- Collaboration conflicts

**Example Activation:**
```
Error: "git push" fails with authentication error
→ Triggers git-troubleshooter (Priority 2: git operation failure)
```

### 10. **guidelines-file** - Technology-Specific Guidelines
**Primary Purpose**: Load appropriate stack guidelines for file modifications

#### Priority 1 Triggers (User Intent - Always activate)
- Explicit requests for technology best practices
- "How should I structure this [language] code?"

#### Priority 2 Triggers (Context Pattern - Auto activate)
- File modifications when technology patterns unclear
- New file creation in unfamiliar technology stack
- **principles** agent unable to provide technology-specific guidance

#### Priority 3 Triggers (Complexity - Conditional)
- Cross-technology integration scenarios
- Technology migration projects
- Setting up new development environments

**Example Activation:**
```
Context: Modifying Python file with unclear patterns
→ Triggers guidelines-file (Priority 2: technology guidance needed)
```

### 11. **guidelines-repo** - Repository Architecture Guidelines
**Primary Purpose**: Repository-level architectural guidance and stack decisions

#### Priority 1 Triggers (User Intent - Always activate)
- Architecture decisions: "how should I structure this project", "technology choice"
- Repository setup: "best approach", "system design"

#### Priority 2 Triggers (Context Pattern - Auto activate)
- Major architectural decisions being made
- Technology stack selection scenarios
- **principles** agent needs repository-wide context

#### Priority 3 Triggers (Complexity - Conditional)
- Multi-technology repository setup
- Microservices architecture decisions
- Platform migration scenarios

**Example Activation:**
```
User: "Should I use microservices or monolith for this project?"
→ Triggers guidelines-repo (Priority 1: architecture decision)
```

### 12. **vulnerability-scanner** - Security Analysis
**Primary Purpose**: Code-level security flaw detection using OWASP frameworks

#### Priority 1 Triggers (User Intent - Always activate)
- Security requests: "security review", "vulnerability check", "security flaws"
- Security terms: "CVE analysis", "OWASP review", "security issues"

#### Priority 2 Triggers (Context Pattern - Auto activate)
- **patterns** detects potential security anti-patterns
- Authentication/authorization code changes
- Input validation or data handling modifications

#### Priority 3 Triggers (Complexity - Conditional)
- Before production deployments
- After security-sensitive code changes
- Compliance review requirements

**Example Activation:**
```
User: "Can you check this login code for security issues?"
→ Triggers vulnerability-scanner (Priority 1: explicit security review)
```

## Trigger Coordination Rules

### Anti-Spam Prevention
- Maximum 4 specialized agents per request
- Priority 1 triggers override lower priorities
- Conflicting triggers resolved by **resolver** agent

### Core Agent Integration
- Specialized agents always coordinate with relevant core agents
- **researcher** often triggers before specialized agents
- **critic** often triggered after specialized analysis

### Performance Optimization
- Batch similar trigger evaluations
- Cache recent trigger decisions
- Use trigger confidence scoring for optimization

## Implementation Notes

### Trigger Detection Pipeline
1. **User Input Analysis**: Parse user message for Priority 1 triggers
2. **Context Analysis**: Evaluate current context for Priority 2 triggers  
3. **Complexity Evaluation**: Assess if Priority 3 triggers apply
4. **Agent Selection**: Choose appropriate specialized agents based on trigger priorities
5. **Coordination**: Ensure core agents + specialized agents work together effectively

This trigger system provides precise, automatic activation of specialized agents while maintaining performance optimization through targeted usage.