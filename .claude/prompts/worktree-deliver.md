# Issue Delivery Workflow

## 🚨 CRITICAL REQUIREMENT: ANALYSIS DIRECTORY DOCUMENTATION 🚨
**BEFORE ANY WORK**: Create and use `analysis/issue-[ISSUE_NUMBER]/` directory for ALL research, analysis, and decisions. This is MANDATORY for every issue - no exceptions.

You are working in a dedicated git worktree for development work. **DO YOUR HOMEWORK FIRST - gather all information and research before asking any questions.**

**MANDATORY: Document all research and analysis in `analysis/issue-[ISSUE_NUMBER]/` directory** - Extract the issue number from the context below and create this directory for all notes, findings, and decisions.

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
8. **Task(critic)** - MANDATORY next step after all research is complete: Critically evaluate all research findings, identify potential risks, overlooked complexities, and provide constructive challenges to assumptions

### 3. Analyze and Synthesize Everything
- Cross-reference all GitHub data with external research
- **Task(options-analyzer)** - Compare different implementation approaches
- **Task(patterns)** - Identify existing code patterns to follow
- **Task(principles)** - Validate against SOLID principles
- Identify optimal implementation approach
- Note any conflicts between research and project constraints

**MANDATORY: Update GitHub Issue with Progress**
After completing all research and analysis above, you MUST update the GitHub issue you are working on with a progress comment summarizing:
- Research findings and key discoveries
- Technical approach and implementation plan
- Any risks or challenges identified
- Clear next steps for implementation

### 4. Document Research Findings and Enable Agent Collaboration
**Create shared analysis directory**: `analysis/issue-[ISSUE_NUMBER]/`

**CRITICAL**: This directory serves as the **central information hub** for ALL agents working on this issue. Every agent MUST:
- **READ existing files** before starting their work to understand prior analysis
- **UPDATE files** with their findings and decisions
- **REFERENCE other agents' work** to avoid duplication and build upon insights

Document all research findings and analysis in this directory:
- `research-findings.md` - Key external research discoveries, API documentation, best practices, security considerations
- `technical-analysis.md` - Technical feasibility, implementation approaches, trade-offs, architecture decisions
- `decision-rationale.md` - Why specific approaches were chosen, conflicts resolved, agent consensus
- `implementation-notes.md` - Detailed implementation plan, file changes, dependencies, progress tracking
- `agent-collaboration.md` - Cross-agent findings, handoffs, and shared insights

**Agent Collaboration Protocol**:
1. **ALWAYS** read existing analysis files before Task() invocation
2. **ALWAYS** update relevant files with your agent's findings
3. **EXPLICITLY** reference other agents' work when building upon their analysis
4. Use agent-collaboration.md to document cross-agent insights and decision handoffs

*Extract issue number from {{ISSUE_CONTEXT}} and create appropriate directory*

## Development Flow (After Homework is Complete)

**Only start implementing after you've gathered all context above:**

### Implementation Loop
1. **Read analysis directory** `analysis/issue-[ISSUE_NUMBER]/` to understand all prior research and decisions
2. **Start coding** with your research-backed approach
3. **Task(researcher)** for specific technical details - ensure agents read and update analysis files
4. **Update analysis files** in `analysis/issue-[ISSUE_NUMBER]/` with ALL new findings, decisions, and implementation progress
5. **Task(test-strategist)** - direct agents to use analysis directory for test planning and coordination
6. **Task(code-cleaner)** - ensure agents read implementation-notes.md for context before improvements
7. **Continuous validation** with **Task(critic)** and **Task(performance-optimizer)** - all agents must reference shared analysis
8. **Documentation updates** following researched standards, with findings stored in analysis directory
9. **Task(git-workflow)** for proper git operations

**Inter-Agent Communication**: Every Task() call should instruct agents to:
- Read existing `analysis/issue-[ISSUE_NUMBER]/` files FIRST
- Update relevant analysis files with their contributions
- Reference other agents' work when building upon their findings

### Quality Gates
Before finishing, ensure:
- ✅ Security considerations addressed (from research)
- ✅ Performance implications considered  
- ✅ Tests written using researched methodologies
- ✅ Documentation updated to researched standards
- ✅ Code follows project patterns and principles
- ✅ Analysis directory `analysis/issue-[ISSUE_NUMBER]/` contains complete research documentation
- ✅ All agents have updated analysis files with their findings and decisions
- ✅ Cross-agent insights are documented in `agent-collaboration.md`
- ✅ Implementation progress is tracked in `implementation-notes.md`
- ✅ No conflicting information exists between agent outputs in analysis directory
- ✅ **GitHub issue updated with research summary and implementation plan**
- ✅ **Final summary comment posted to GitHub issue with findings and clear next steps**

## Agent Usage Guidelines

### Primary Agents (Use Heavily)
- **Task(researcher)** - Your main external knowledge source. **INSTRUCT**: Read `analysis/issue-[ISSUE_NUMBER]/research-findings.md` first, then research everything: APIs, best practices, security, performance, testing approaches. Update research-findings.md with all discoveries.
- **Task(context)** - Always use first to understand codebase. **INSTRUCT**: Read `analysis/issue-[ISSUE_NUMBER]/technical-analysis.md` to understand prior context analysis.
- **Task(stack-advisor)** - Load technology-specific guidelines before any file modifications. **INSTRUCT**: Update `technical-analysis.md` with technology stack insights.

### Supporting Agents  
- **Task(options-analyzer)** - **INSTRUCT**: Read `decision-rationale.md` for prior decisions, compare implementation approaches, update with analysis
- **Task(patterns)** - **INSTRUCT**: Read `technical-analysis.md` for existing patterns, update with new pattern discoveries
- **Task(principles)** - **INSTRUCT**: Read all analysis files to understand architectural context, update `decision-rationale.md` with principle validations
- **Task(test-strategist)** - **INSTRUCT**: Read `implementation-notes.md` for testing context, update with comprehensive test design
- **Task(code-cleaner)** - **INSTRUCT**: Read `implementation-notes.md` for improvement context, update with code quality insights
- **Task(critic)** - **INSTRUCT**: Read all analysis files for complete review context, update `agent-collaboration.md` with critical findings
- **Task(performance-optimizer)** - **INSTRUCT**: Read `technical-analysis.md` for performance context, update with optimization insights
- **Task(constraint-solver)** - **INSTRUCT**: Read `decision-rationale.md` for constraint context, update with conflict resolutions
- **Task(git-workflow)** - **INSTRUCT**: Handle git operations, ensure analysis directory is committed with changes

## Only Ask Questions After Complete Homework

**ONLY ask questions if critical information remains unclear after:**
✅ Complete GitHub issue analysis using Bash + gh CLI
✅ Comprehensive external research using Task(researcher)
✅ Technical feasibility validation using Task(stack-advisor)
✅ Implementation approach analysis using Task(options-analyzer)

When you do ask questions, make them highly specific and research-informed.

## Remember
- **🚨 CRITICAL: Document everything in `analysis/issue-[ISSUE_NUMBER]/`** - ALL research and analysis MUST go in this directory. This is the #1 requirement for preserving knowledge and enabling agent collaboration.
- **Front-load everything** - research, analysis, context gathering
- **Question as last resort** - only after thorough homework
- **Iterate naturally** - no artificial phases, just good development flow
- **Use agents extensively** - they are your external knowledge and analysis tools
- **Follow project standards** - CLAUDE.md rules, file structure, coding conventions

---

## 🚨 FINAL REMINDER: ANALYSIS DIRECTORY DOCUMENTATION 🚨

**BEFORE YOU FINISH**: Verify that `analysis/issue-[ISSUE_NUMBER]/` directory exists and contains:
- ✅ All research findings and external knowledge
- ✅ Technical analysis and implementation decisions  
- ✅ Agent collaboration notes and cross-references
- ✅ Implementation progress and lessons learned

**This documentation is CRITICAL** for:
- Future maintenance and debugging
- Knowledge preservation across development sessions
- Agent collaboration and context sharing
- Audit trail of technical decisions

**NO WORK IS COMPLETE** without proper analysis directory documentation.