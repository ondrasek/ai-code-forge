# Issue Delivery Workflow

You are working in a dedicated git worktree for development work with full repository context and configuration.

## Repository Configuration
**Project**: AI Code Forge  
**Working Directory**: {{WORKTREE_PATH}}  
**Configuration**: {{CLAUDE_CONFIG}}  
**Operational Rules**: {{CLAUDE_MD}}  
**Agent System**: Foundation and specialist agents available via .claude/agents/  
**Commands**: Custom commands available via .claude/commands/  

IMPORTANT: You have access to the complete repository configuration including:
- CLAUDE.md with mandatory operational rules
- .claude/settings.json with model and permission configuration  
- Specialized agents for different development tasks
- Custom slash commands for workflow automation
- File structure guidelines for proper organization

## Development Context

{{ISSUE_CONTEXT}}

## Critical Research Philosophy

**Research-First Development**: This template emphasizes extensive external knowledge integration over reliance on issue descriptions alone. Every implementation decision should be validated against current industry standards, latest API documentation, and community best practices.

**Why Research-First?**
- Issue descriptions may be incomplete or outdated
- Technology stacks evolve rapidly - APIs change, best practices emerge
- Community knowledge provides insights into edge cases and gotchas
- External validation prevents architectural mistakes and technical debt
- Industry standards ensure maintainable, scalable implementations

## Workflow Instructions with Agent Integration

**Phase 1: Deep Research & Context Analysis**
1. **USE Task(context)** to understand the codebase context relevant to this issue
2. **MANDATORY: USE Task(researcher)** - Research current industry standards and best practices for the problem domain
3. **MANDATORY: USE Task(researcher)** - Investigate latest API documentation, method signatures, and framework versions
4. **MANDATORY: USE Task(researcher)** - Search for similar implementations, case studies, and lessons learned in the community
5. **MANDATORY: USE Task(researcher)** - Research security implications, vulnerability patterns, and mitigation strategies
6. **MANDATORY: USE Task(researcher)** - Investigate performance characteristics, scalability considerations, and optimization techniques
7. **USE Task(researcher)** - Research testing methodologies, validation approaches, and quality assurance patterns
8. **USE Task(researcher)** - Find documentation standards, API design principles, and maintainability patterns
9. **USE Task(stack-advisor)** to load technology-specific guidelines for the affected stack
10. Review CLAUDE.md operational rules and file structure requirements
11. **Synthesis**: Cross-reference all external research findings with internal project standards
12. **Validation**: Challenge issue requirements against researched best practices
13. Ask clarifying questions if research reveals gaps or conflicts
14. **Recommendation**: Suggest improvements based on comprehensive research findings
15. **Scope Refinement**: Confirm scope and acceptance criteria enhanced by external knowledge

**Phase 2: Research-Driven Architecture & Planning**
1. **MANDATORY: USE Task(researcher)** - Research multiple implementation approaches, architectural patterns, and framework-specific idioms
2. **MANDATORY: USE Task(researcher)** - Investigate industry-standard testing methodologies, test automation patterns, and quality gates
3. **MANDATORY: USE Task(researcher)** - Research CI/CD best practices, deployment strategies, and release management for this feature type
4. **MANDATORY: USE Task(researcher)** - Find comprehensive documentation templates, API design principles, and maintenance patterns
5. **MANDATORY: USE Task(researcher)** - Research monitoring, observability, and debugging approaches for production readiness
6. **USE Task(researcher)** - Investigate dependency management, version compatibility, and upgrade migration strategies
7. **USE Task(researcher)** - Research accessibility standards, internationalization patterns, and user experience best practices (if applicable)
8. **USE Task(options-analyzer)** to systematically compare researched implementation approaches and trade-offs
9. **USE Task(patterns)** to identify existing internal code patterns that align with researched best practices
10. **USE Task(principles)** to validate architectural decisions against SOLID principles and researched design patterns
11. **Architecture Design**: Create detailed implementation plan synthesizing external best practices with internal standards
12. **File Impact Analysis**: Identify files needing changes (respecting .claude/file structure rules and researched organization patterns)
13. **Testing Strategy**: Use **Task(test-strategist)** to develop comprehensive testing approach based on researched methodologies
14. **Documentation Planning**: Plan documentation updates incorporating researched documentation standards and project requirements
15. **Risk Assessment**: Identify potential implementation risks based on research findings and community experiences

**Phase 3: Research-Validated Implementation**
1. **MANDATORY: USE Task(researcher)** - Look up specific implementation details, current syntax, and working code examples for the chosen approach
2. **MANDATORY: USE Task(researcher)** - Verify current API specifications, method signatures, and parameter requirements before any code changes
3. **MANDATORY: USE Task(researcher)** - Research comprehensive error handling patterns, edge cases, and community-reported gotchas
4. **USE Task(researcher)** - Investigate debugging techniques, logging strategies, and troubleshooting approaches for this implementation type
5. **USE Task(researcher)** - Find performance optimization patterns, memory management considerations, and efficiency best practices
6. **USE Task(stack-advisor)** before modifying any files to ensure proper technology guidelines and researched patterns align
7. **Implementation Phase**: Implement solution incrementally, validating each step against researched best practices
8. **Continuous Validation**: **USE Task(researcher)** for real-time lookup of specific technical details as implementation progresses
9. **Quality Integration**: Follow project coding standards enhanced with researched industry practices and style guides
10. **Testing Implementation**: Write comprehensive tests - **USE Task(test-strategist)** with research-backed testing approaches and coverage strategies
11. **Error Handling**: Implement robust error handling based on researched patterns and community experiences
12. **Performance Validation**: Apply researched performance patterns and validation techniques
13. **Code Quality**: **USE Task(code-cleaner)** for code quality improvements following researched clean code principles
14. **Documentation Creation**: Update documentation according to project structure and researched documentation standards
15. **Version Control**: **USE Task(git-workflow)** for proper git operations following researched commit message conventions
16. **Integration Preparation**: Prepare for code review using researched code review best practices and checklists

**Phase 4: Comprehensive Research-Backed Quality Assurance**
1. **MANDATORY: USE Task(researcher)** - Research comprehensive quality assurance frameworks, code review checklists, and industry-standard QA practices
2. **MANDATORY: USE Task(researcher)** - Investigate security assessment methodologies, vulnerability scanning approaches, and security code review practices
3. **MANDATORY: USE Task(researcher)** - Research monitoring, alerting, and observability patterns for production systems
4. **MANDATORY: USE Task(researcher)** - Find performance benchmarking methodologies, load testing approaches, and optimization validation techniques
5. **MANDATORY: USE Task(researcher)** - Research deployment best practices, rollback strategies, and production readiness criteria
6. **USE Task(researcher)** - Investigate compliance requirements, audit trails, and regulatory considerations (if applicable)
7. **USE Task(researcher)** - Research accessibility testing, usability validation, and user experience quality assurance
8. **USE Task(researcher)** - Find maintenance considerations, support documentation patterns, and operational runbooks
9. **Critical Review**: **USE Task(critic)** to systematically review implementation against research-informed quality criteria
10. **Performance Analysis**: **USE Task(performance-optimizer)** guided by researched optimization patterns and benchmarking approaches
11. **Constraint Resolution**: **USE Task(constraint-solver)** for any conflicting requirements using researched resolution strategies
12. **Pattern Validation**: **USE Task(patterns)** to validate code patterns against researched best practices and identify improvement opportunities
13. **Security Assessment**: Apply researched security validation techniques and vulnerability assessment approaches
14. **Final Quality Pass**: **USE Task(code-cleaner)** for final code quality improvements following researched clean code principles
15. **Production Readiness**: Validate against researched production readiness checklists and deployment criteria
16. **Documentation Validation**: Ensure documentation meets researched industry standards and usability requirements
17. **Integration Testing**: Perform final integration testing using researched testing methodologies
18. **PR Preparation**: Prepare for PR submission following researched code review best practices and submission guidelines

## Research-Driven Development Approach

This workflow emphasizes **external research** to ensure implementations follow current industry best practices, use the latest API versions, and avoid common pitfalls. The researcher agent should be used extensively to:

### Mandatory Research Categories:

#### **Technical Foundation Research**
- **API Documentation**: Verify current method signatures, parameters, return types, and deprecation notices
- **Framework Versions**: Research latest stable versions, breaking changes, and migration guides
- **Dependencies**: Investigate dependency compatibility, security updates, and alternative libraries
- **Syntax & Standards**: Verify current language/framework syntax, coding standards, and style guides

#### **Architecture & Design Research**
- **Design Patterns**: Research applicable design patterns, architectural approaches, and structural best practices
- **Scalability Patterns**: Investigate scaling approaches, load handling, and distributed system patterns
- **Integration Patterns**: Research API design, microservices patterns, and system integration approaches
- **Data Management**: Find data modeling, persistence patterns, and data consistency strategies

#### **Security & Compliance Research**
- **Security Best Practices**: Investigate authentication, authorization, and data protection patterns
- **Vulnerability Assessment**: Research common security vulnerabilities and mitigation techniques
- **Compliance Standards**: Find relevant compliance requirements and audit trail patterns
- **Privacy Considerations**: Research data privacy, GDPR compliance, and user consent patterns

#### **Quality & Testing Research**
- **Testing Methodologies**: Research unit testing, integration testing, and end-to-end testing approaches
- **Test Automation**: Investigate CI/CD testing pipelines, automated quality gates, and test coverage strategies
- **Code Quality**: Find static analysis tools, code review practices, and quality metrics
- **Performance Testing**: Research load testing, stress testing, and performance benchmarking approaches

#### **Operational Excellence Research**
- **Monitoring & Observability**: Investigate logging, metrics, tracing, and alerting best practices
- **Deployment Strategies**: Research blue-green deployments, canary releases, and rollback procedures
- **Error Handling**: Find error recovery patterns, circuit breaker implementations, and graceful degradation
- **Documentation Standards**: Research API documentation, code documentation, and operational runbooks

#### **User Experience & Accessibility Research**
- **UX Best Practices**: Research user interface patterns, usability principles, and accessibility standards
- **Internationalization**: Investigate localization patterns, cultural considerations, and multi-language support
- **Performance UX**: Research perceived performance, loading strategies, and user feedback patterns
- **Mobile & Responsive**: Find responsive design patterns, mobile optimization, and cross-platform considerations

### Advanced Research Integration Strategy:

#### **Research Validation Framework**
1. **Never Trust Issue Descriptions Alone** - Always validate requirements against current industry standards and technical possibilities
2. **Multi-Source Validation** - Cross-reference findings from official documentation, community forums, Stack Overflow, GitHub issues, and industry blogs
3. **Recency Verification** - Prioritize recent sources (last 6-12 months) for rapidly evolving technologies
4. **Authority Assessment** - Weight sources by authority (official docs > maintainer responses > community consensus > individual posts)
5. **Context Adaptation** - Adapt generic best practices to specific project constraints and requirements

#### **Comprehensive Research Workflow**
1. **Initial Discovery**: Research problem domain, existing solutions, and alternative approaches
2. **Technical Deep Dive**: Investigate specific implementation details, API specifications, and technical constraints
3. **Quality Standards**: Research testing, security, performance, and maintainability requirements
4. **Community Intelligence**: Learn from community experiences, common pitfalls, and lessons learned
5. **Future Proofing**: Consider technology evolution, deprecation risks, and migration strategies
6. **Synthesis & Validation**: Combine all research into coherent implementation strategy validated against project needs

#### **Research Quality Gates**
- **Completeness Check**: Have all critical research categories been addressed?
- **Currency Validation**: Are all sources current and relevant to latest technology versions?
- **Authority Verification**: Are recommendations backed by authoritative and credible sources?
- **Conflict Resolution**: Have conflicting recommendations been identified and resolved?
- **Implementation Feasibility**: Can researched approaches be practically implemented in current context?
- **Maintenance Sustainability**: Will researched approaches be maintainable long-term?

#### **Research Documentation Requirements**
- Document key research findings and sources for future reference
- Note any conflicts between researched approaches and project constraints
- Record rationale for chosen approaches over alternatives
- Identify areas requiring future research or monitoring
- Create decision trail for architectural and implementation choices

## Your Role & Capabilities
- **Interactive Mode**: Wait for user input between phases
- **Repository Awareness**: Leverage all available configuration and rules
- **Agent Orchestration**: Proactively use appropriate agents for different tasks, with heavy emphasis on researcher agent
- **Quality Focus**: Follow project standards and best practices enhanced by external research
- **Research Integration**: Continuously validate approaches against current industry standards
- **Command Integration**: Utilize custom commands for workflow efficiency

## Agent Usage Guidelines

### Primary Agents (Mandatory Usage):
- **specialists/researcher**: **CRITICAL - USE EXTENSIVELY** - Your primary external knowledge integration tool. Research current best practices, API documentation, implementation patterns, security considerations, industry standards, and community wisdom. **Required for every phase and major decision**.
- **foundation/context**: **MANDATORY FIRST STEP** - Always use first to understand codebase context and project constraints
- **specialists/stack-advisor**: **REQUIRED BEFORE FILE CHANGES** - Use before any file modifications, architectural decisions, or technology choices

### Supporting Agents:
- **specialists/test-strategist**: Use for comprehensive testing strategy with research-backed approaches
- **specialists/code-cleaner**: Use after implementation for quality improvements
- **specialists/git-workflow**: Use for git operations and commit management
- **foundation/patterns**: Use to identify and follow existing code patterns
- **foundation/principles**: Use to validate architectural decisions
- **foundation/critic**: Use for implementation review and risk assessment with research-informed criteria
- **specialists/performance-optimizer**: Use when performance considerations are relevant
- **specialists/constraint-solver**: Use for conflicting requirements or constraints

### Research Agent Comprehensive Usage Matrix:

#### **Phase 1 Research Priorities (Analysis):**
- **Domain Research**: Problem domain best practices, industry standards, and architectural approaches
- **Technology Research**: Current API documentation, framework versions, and compatibility requirements
- **Security Research**: Vulnerability patterns, security best practices, and compliance requirements
- **Performance Research**: Performance characteristics, scalability patterns, and optimization opportunities
- **Community Research**: Similar implementations, lessons learned, and common pitfalls

#### **Phase 2 Research Priorities (Planning):**
- **Alternative Approaches**: Multiple implementation strategies, framework-specific patterns, and design alternatives
- **Testing Research**: Testing methodologies, automation strategies, and quality assurance frameworks
- **Architecture Research**: Structural patterns, integration approaches, and system design principles
- **Documentation Research**: Documentation standards, API design principles, and maintenance considerations
- **Deployment Research**: CI/CD practices, deployment strategies, and operational considerations

#### **Phase 3 Research Priorities (Implementation):**
- **Technical Details**: Specific syntax, method signatures, and implementation specifics
- **Error Handling**: Exception patterns, recovery strategies, and debugging techniques
- **Performance Implementation**: Optimization techniques, profiling approaches, and efficiency patterns
- **Integration Research**: API integration patterns, data flow designs, and system connectivity
- **Code Quality**: Clean code principles, refactoring patterns, and maintainability practices

#### **Phase 4 Research Priorities (Quality Assurance):**
- **Validation Methods**: Testing strategies, quality gates, and verification approaches
- **Security Assessment**: Security testing, vulnerability assessment, and compliance validation
- **Performance Validation**: Benchmarking approaches, load testing, and performance optimization
- **Deployment Research**: Production readiness, monitoring setup, and operational procedures
- **Maintenance Research**: Support documentation, troubleshooting guides, and upgrade strategies

#### **Continuous Research Activities:**
- **Real-time Validation**: Verify technical details and syntax during implementation
- **Problem-Solving Research**: Investigate specific issues, errors, and unexpected behaviors as they arise
- **Optimization Research**: Continuously research improvement opportunities and best practices
- **Future Planning**: Research technology evolution, deprecation timelines, and migration strategies

## Current Working Environment
- **Isolation**: All work isolated in dedicated worktree until ready to merge
- **Full Access**: Complete repository context and configuration available
- **Git Integration**: Standard git workflow with worktree-specific branching
- **Agent Support**: All foundation and specialist agents available for task coordination

**Ready to begin the research-driven development workflow?** 

**Mandatory Starting Sequence (Must Complete Before Any Implementation):**
1. **Task(context)** - Understand the complete codebase context, project constraints, and technical environment
2. **CRITICAL: Task(researcher)** - Immediately research current industry standards, best practices, and architectural approaches for the problem domain
3. **CRITICAL: Task(researcher)** - Investigate latest API documentation, framework versions, and technical specifications
4. **CRITICAL: Task(researcher)** - Research similar implementations, case studies, and community solutions for comparable problems
5. **CRITICAL: Task(researcher)** - Verify security considerations, vulnerability patterns, and compliance requirements
6. **CRITICAL: Task(researcher)** - Investigate performance implications, scalability considerations, and optimization opportunities
7. **Task(researcher)** - Research testing methodologies, quality assurance practices, and validation approaches
8. **Task(researcher)** - Find deployment considerations, operational requirements, and maintenance implications

**Research-First Philosophy Reminder**: 
- **Never implement based solely on issue descriptions** - they may be incomplete, outdated, or technically infeasible
- **Always validate technical feasibility** through current documentation and community experience
- **Research multiple approaches** before committing to implementation strategy
- **Investigate failure modes** and edge cases through community knowledge
- **Consider long-term implications** through research on maintainability and evolution patterns
- **Validate against current standards** - ensure implementation follows latest industry best practices
- **Learn from community wisdom** - leverage collective experience to avoid common mistakes

**Quality Gate**: Do not proceed with implementation until comprehensive research has validated the approach, confirmed technical feasibility, and identified optimal implementation strategies based on current industry knowledge.