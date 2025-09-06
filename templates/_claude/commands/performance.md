---
description: Analyze performance bottlenecks, optimization opportunities, and scalability concerns.
argument-hint: Optional FILES to analyze, or empty to analyze entire project.
allowed-tools: Task, Read, Grep, Bash
---

# Performance Analysis

Analyze performance bottlenecks, optimization opportunities, and scalability concerns for codebase performance assessment and optimization recommendations.

## Instructions

1. Parse $ARGUMENTS for performance analysis parameters:
   - --commits N (analyze performance changes in last N commits)
   - --profile (include profiling guidance)
   - --memory (include historical performance patterns)
   - FILES... (specific files to analyze for performance)

2. Execute optimized parallel clusters for performance analysis
1. **Performance Context Analysis**: context agent for system architecture understanding
2. **Performance-Focused Analysis**: specialist-performance + specialist-constraints parallel analysis
3. **Pattern & Research Integration**: patterns + researcher for optimization strategies
4. **Critical Assessment**: critic for risk evaluation of proposed optimizations

PARAMETERS:
--commits N (analyze performance changes in last N commits)
--profile (include profiling guidance)
--memory (include historical performance patterns)
FILES... (specific files to analyze for performance)

INTELLIGENT_PERFORMANCE_DETECTION:
1. **Auto-detect bottlenecks**: Parse user requests for performance concerns ("slow", "memory leak", "optimization")
2. **Change analysis**: Examine modified files for performance indicators (algorithms, database queries, loops)
3. **Context clues**: Repository structure and file types suggest performance focus areas
4. **Profiling integration**: Provide guidance on performance measurement and profiling tools

OPTIMIZED_PARALLEL_CLUSTERS:
Performance Analysis (2 agents): specialist-performance + specialist-constraints
Context & Research (2 agents): context + researcher  
Pattern & Quality (2 agents): patterns + critic

COORDINATION_PROTOCOL: All clusters execute simultaneously via single message with multiple Task() calls for efficient analysis. Total agents: 6 (optimized for performance focus)

INTELLIGENT_OUTPUT:
- **Performance Bottleneck Analysis**: Systematic identification of performance issues
- **Optimization Opportunities**: Prioritized recommendations with impact assessment
- **Scalability Assessment**: Growth and load handling evaluation
- **Algorithm Complexity**: Big O analysis and optimization suggestions
- **Resource Usage**: Memory, CPU, I/O efficiency evaluation
- **Implementation Guidance**: Specific optimization techniques and tools

## Performance Focus Areas

### Algorithmic Optimization
- **Complexity Analysis**: Time and space complexity assessment
- **Algorithm Selection**: More efficient algorithms and data structures
- **Caching Opportunities**: Memoization and caching strategies
- **Lazy Loading**: Deferred computation and loading patterns

### System Performance
- **Database Optimization**: Query optimization, indexing strategies
- **Network Efficiency**: API calls, data transfer optimization
- **Concurrency**: Parallel processing and async opportunities
- **Resource Management**: Memory leaks, connection pooling

### Scalability Concerns
- **Load Testing**: Performance under scale
- **Bottleneck Identification**: System constraint analysis
- **Architecture Patterns**: Scalable design recommendations
- **Performance Monitoring**: Metrics and observability guidance

## Execution Workflow

### Phase 1: Performance Context Loading
```
Task: "Analyze system architecture for performance context" (context)
Task: "Research performance best practices for detected technologies" (researcher)
```

### Phase 2: Performance Analysis Clusters
```
Task: "Execute performance bottleneck analysis" (specialist-performance + specialist-constraints)
Task: "Execute pattern and quality analysis" (patterns + critic)
```

**OPTIMIZED AGENT COUNT**: 6 agents total (performance-focused coordination)

**MEMORY INTEGRATION**: Foundation agents store performance findings for continuous optimization learning

## Performance Output Structure

### Performance Summary
- **Scope**: Files/systems analyzed for performance
- **Bottlenecks**: Identified performance constraints and limitations
- **Optimization Opportunities**: Ranked by impact and implementation effort
- **Overall Assessment**: Performance health with specific metrics

### Performance Analysis
- **Algorithmic Issues**: Complexity problems and optimization opportunities
- **System Bottlenecks**: Resource constraints and scalability limits
- **Code Patterns**: Performance anti-patterns and improvement suggestions
- **External Dependencies**: Third-party performance impacts

### Optimization Roadmap
- **Critical**: Performance fixes that significantly impact user experience
- **High**: Major optimization opportunities with clear ROI
- **Medium**: Code improvements that enhance performance
- **Low**: Minor optimizations and cleanup opportunities

### Implementation Guidance
- **Profiling Tools**: Recommended tools for performance measurement
- **Optimization Techniques**: Specific strategies for identified issues
- **Testing Strategy**: Performance regression testing recommendations
- **Monitoring Setup**: Metrics and alerting for ongoing performance health

## Related Commands

- `/review` - Comprehensive code review including performance assessment
- `/refactor` - Implement performance optimizations and improvements
- `/test` - Performance testing and benchmarking strategies
- `/fix` - Implement specific performance fixes