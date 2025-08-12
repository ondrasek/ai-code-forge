# Issue Delivery Workflow

You are working in a dedicated git worktree for development work. **DO YOUR HOMEWORK FIRST - gather all information and research before asking any questions.**

## Repository Configuration
**Project**: AI Code Forge  
**Working Directory**: {{WORKTREE_PATH}}  
**Configuration**: {{CLAUDE_CONFIG}}  
**Operational Rules**: {{CLAUDE_MD}}  

You have access to:
- CLAUDE.md with mandatory operational rules
- .claude/settings.json with model and permission configuration  
- Complete agent system (.claude/agents/) for specialized tasks
- Custom slash commands (.claude/commands/) for workflow automation
- File structure guidelines for proper organization

## Development Context
{{ISSUE_CONTEXT}}

## MANDATORY: Complete All Homework Before Any Questions

### 1. Gather Complete GitHub Context (Use Bash Tool)
Use the Bash tool to execute these GitHub CLI commands to understand the full issue ecosystem:

- Get complete issue details: `gh issue view [ISSUE_NUMBER] --json title,body,state,labels,comments,assignees,milestone --jq '.'`
- Get all comments: `gh issue view [ISSUE_NUMBER] --comments`
- Find related issues: `gh issue list --search "is:issue" --limit 20 --json number,title,state,labels`
- Search git history: `git log --grep="fix\|feat\|issue" --oneline -10`
- Check existing branches: `git branch -a | head -20`
- Get repository context: `gh repo view --json name,description,topics,languages`

*Extract the issue number from the {{ISSUE_CONTEXT}} above and substitute into commands*

### 2. Build Complete Technical Context
1. **Task(context)** - Understand complete codebase context and constraints
2. **Task(stack-advisor)** - Load all relevant technology guidelines  
3. **Task(researcher)** - Research current best practices for the specific problem domain
4. **Task(researcher)** - Investigate latest API documentation and technical specifications
5. **Task(researcher)** - Find similar implementations and community solutions
6. **Task(researcher)** - Research security considerations and performance implications
7. **Task(researcher)** - Research testing approaches and quality standards

### 3. Analyze and Synthesize Everything
- Cross-reference all GitHub data with external research
- **Task(options-analyzer)** - Compare different implementation approaches
- **Task(patterns)** - Identify existing code patterns to follow
- **Task(principles)** - Validate against SOLID principles
- Identify optimal implementation approach
- Note any conflicts between research and project constraints

## Development Flow (After Homework is Complete)

**Only start implementing after you've gathered all context above:**

### Implementation Loop
1. **Start coding** with your research-backed approach
2. **Task(researcher)** for specific technical details as you encounter them
3. **Task(test-strategist)** for comprehensive test design
4. **Task(code-cleaner)** for improvements and completion
5. **Continuous validation** with **Task(critic)** and **Task(performance-optimizer)**
6. **Documentation updates** following researched standards
7. **Task(git-workflow)** for proper git operations

### Quality Gates
Before finishing, ensure:
- ✅ Security considerations addressed (from research)
- ✅ Performance implications considered  
- ✅ Tests written using researched methodologies
- ✅ Documentation updated to researched standards
- ✅ Code follows project patterns and principles

## Agent Usage Guidelines

### Primary Agents (Use Heavily)
- **Task(researcher)** - Your main external knowledge source. Research everything: APIs, best practices, security, performance, testing approaches
- **Task(context)** - Always use first to understand codebase
- **Task(stack-advisor)** - Load technology-specific guidelines before any file modifications

### Supporting Agents  
- **Task(options-analyzer)** - Compare implementation approaches
- **Task(patterns)** - Find existing code patterns to follow
- **Task(principles)** - Validate architectural decisions
- **Task(test-strategist)** - Design comprehensive testing
- **Task(code-cleaner)** - Improve code quality and completion
- **Task(critic)** - Review implementation for issues
- **Task(performance-optimizer)** - Optimize performance when needed
- **Task(constraint-solver)** - Resolve conflicting requirements
- **Task(git-workflow)** - Handle git operations

## Only Ask Questions After Complete Homework

**ONLY ask questions if critical information remains unclear after:**
✅ Complete GitHub issue analysis using Bash + gh CLI
✅ Comprehensive external research using Task(researcher)
✅ Technical feasibility validation using Task(stack-advisor)
✅ Implementation approach analysis using Task(options-analyzer)

When you do ask questions, make them highly specific and research-informed.

## Remember
- **Front-load everything** - research, analysis, context gathering
- **Question as last resort** - only after thorough homework
- **Iterate naturally** - no artificial phases, just good development flow
- **Use agents extensively** - they are your external knowledge and analysis tools
- **Follow project standards** - CLAUDE.md rules, file structure, coding conventions