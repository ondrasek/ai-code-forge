---
description: Review slash command(s) following guidelines with comprehensive compliance analysis.
argument-hint: [command-name] or [namespace/] to review specific commands, or empty to review all commands.
allowed-tools: Task, Read, Glob, Bash
---

# Command Compliance Review

Review slash command definition for compliance with @templates/guidelines/claude-commands-guidelines.md using comprehensive multi-agent analysis.

## Instructions

1. Parse $ARGUMENTS for review parameters:
   - Determine which commands are to be reviewed.
   - When no arguments are passed, review all commands under .claude/commands, including commands in sub-folders
   (namespaces).

2. Validate command exists somewhere in .claude/commands/ directory before proceeding

3. Execute comprehensive parallel compliance analysis clusters:
   - Use agents to review the commands.
   - In case you are reviewing multiple commands, use agents to review each command separately.

4. Compliance Validation Checklist:

**Mandatory Requirements**:
- [ ] File location: .claude/commands/ directory or subdirectories (namespaces)
- [ ] File format: Markdown (.md) extension
- [ ] Frontmatter: Valid YAML with required fields and correct syntax
- [ ] Description: Present and descriptive
- [ ] Argument-hint: Clear parameter guidance
- [ ] Title: Clear, descriptive command title
- [ ] Instructions: Step-by-step AI instructions (not human docs)
- [ ] $ARGUMENTS: Proper parameter reference usage

**Security Requirements**:
- [ ] allowed-tools: Minimal necessary tools only
- [ ] Tool restrictions: Appropriate for command scope
- [ ] Input validation: Parameter validation instructions
- [ ] Security considerations: Appropriate safety measures

**Best Practices**:
- [ ] Single responsibility: One clear purpose
- [ ] Error handling: Common failure scenarios covered
- [ ] Agent coordination: Appropriate agent usage
- [ ] Performance: Efficient execution patterns
- [ ] Maintainability: Clear, sustainable implementation

5. Analysis and Reporting:
   - Generate comprehensive compliance report with specific issues
   - Categorize violations by severity (critical, high, medium, low)
   - Provide specific remediation recommendations for each issue
   - Present before/after comparison for any fixes applied

6. Output structured compliance assessment with actionable recommendations

## Compliance Assessment Categories

**Critical Issues** (Must Fix):
- Missing required frontmatter fields
- Invalid YAML structure
- Missing or incorrect file location
- Security violations in tool permissions
- Completely missing instructions section

**High Priority Issues**:
- Poor $ARGUMENTS usage
- Inadequate security considerations
- Missing error handling
- Unclear or ambiguous instructions
- Tool permission overreach

**Medium Priority Issues**:
- Suboptimal agent coordination patterns
- Minor naming convention violations
- Incomplete argument hints
- Missing best practice implementations

**Low Priority Issues**:
- Style and formatting inconsistencies
- Minor optimization opportunities
- Documentation improvements
- Enhanced user experience suggestions

## Error Handling

- **File Not Found**: Clear error message with available commands list
- **Invalid Format**: Specific parsing error details and fix guidance
- **Access Issues**: Permission or file system error handling
- **Analysis Failures**: Graceful handling of agent coordination issues

## Output Format

Provide structured compliance report including:
- **Overall Compliance Score**: Percentage score with grade (A-F)
- **Critical Issues**: Must-fix violations with specific remediation steps
- **Security Assessment**: Tool restrictions and permission model compliance
- **Best Practices Score**: Adherence to guidelines best practices
- **Improvement Recommendations**: Specific, actionable enhancement suggestions
- **Agent Coordination Analysis**: Efficiency and pattern assessment
- **Fix Summary**: If --fix used, summary of automatic corrections applied