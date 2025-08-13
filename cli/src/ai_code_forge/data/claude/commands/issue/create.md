---
description: Create new GitHub Issue with intelligent classification and metadata.
argument-hint: Issue description or topic.
allowed-tools: Task
---

# GitHub Issue Creation

Create new GitHub Issue with intelligent classification based on content analysis.

## Instructions

**Two-Agent Priority Classification Workflow**:

1. **Phase 1 - Issue Creation with Confidence Assessment**:
   Use Task tool to delegate to github-issues-workflow agent:
   - Analyze $ARGUMENTS (if provided) or prompt user for issue description
   - Apply BINARY CONFIDENCE SYSTEM with strict 6-criteria assessment
   - Create GitHub issue with best-guess priority assignment
   - Add mandatory Priority Analysis comment with confidence justification
   - Return issue number, URL, and confidence assessment

2. **Phase 2 - Priority Validation**:
   Use Task tool to delegate to critic agent with specialized priority validation prompt:
   
   **Critic Agent Prompt**: "Analyze the GitHub issue priority classification from the github-issues-workflow agent. Focus on validating their binary confidence assessment:

   **VALIDATION CRITERIA**:
   - Verify the agent claimed 'Confident' only if ALL 6 strict criteria were genuinely met
   - Challenge confidence claims that lack sufficient evidence
   - Look for overlooked conflicting indicators (enhancement, nice to have, future, optional)  
   - Validate precedent claims by checking cited similar issues
   - Assess whether reasoning is truly falsifiable with specific evidence
   - Question if 3+ keywords/indicators were actually present and relevant

   **VALIDATION ACTIONS**:
   - If 'Confident' claim is unjustified: Remove priority label (default to medium priority)
   - If 'Uncertain' but strong evidence exists: Consider adding priority label
   - Add Priority Validation comment explaining your assessment and any adjustments
   - Use GitHub CLI to modify labels only when confidence assessment was incorrect

   **SKEPTICAL FOCUS**: Be particularly skeptical of 'Confident' claims - look for evidence AGAINST the priority assignment. The goal is preventing priority inflation through rigorous validation."

   The critic will review, validate, and adjust the priority assignment as needed.

3. **Confirmation**:
   Provide issue details with:
   - Direct GitHub issue link
   - Final priority classification
   - Summary of both agents' assessments