---
description: Create new GitHub Issue with comprehensive quality validation through mandatory 8-step workflow.
allowed-tools: Task
---

# GitHub Issue Creation - Mandatory 8-Step Quality Workflow

!`git status`
!`git branch --show-current`

Create new GitHub Issue with comprehensive quality validation using extended actor/critic pattern. All issues go through the complete 8-step refinement process for maximum quality assurance.

## Mandatory 8-Step Workflow Instructions

**Extended Actor/Critic Pattern for Content Quality + Priority Validation**:

### **Step 1: Draft Creation**
Use Task tool to delegate to github-issues-workflow agent:
- Prompt user for initial issue description and gather requirements
- Create comprehensive draft with:
  - Clear problem description
  - Initial acceptance criteria
  - Basic implementation scope
- Focus on completeness over perfection
- Return draft content for refinement review

### **Step 2: Refine Content**  
Use Task tool to delegate to github-issues-workflow agent:
- Improve draft based on GitHub issue best practices
- Enhance clarity, specificity, and actionability
- Add technical details and context
- Structure content for developer comprehension
- Return refined content for criticism

### **Step 3: Criticize Refinement**
Use Task tool to delegate to critic agent with content quality focus:

**Content Critic Prompt**: "Critically analyze this issue content for quality, clarity, and actionability. Challenge generic language and identify improvement opportunities:

**CONTENT QUALITY CRITERIA**:
- **Anti-Generic Detection**: Flag templated language, empty phrases, checklist padding
- **Specificity Challenge**: Demand concrete examples, specific behaviors, measurable outcomes  
- **Actionability Test**: Verify a developer can understand exactly what to build
- **Value Validation**: Confirm clear user/business value articulation
- **Scope Clarity**: Ensure implementation boundaries are well-defined
- **Technical Depth**: Assess if sufficient technical context is provided

**CRITICISM ACTIONS**:
- Identify vague or generic content requiring specificity
- Challenge unclear implementation scope or acceptance criteria  
- Point out missing technical details or context
- Suggest specific improvements for clarity and actionability
- Flag any 'stupid checklists' or meaningless template content

**CONSTRUCTIVE FOCUS**: Provide specific, actionable feedback for content improvement. Challenge the author to be more precise and valuable."

### **Step 4: Adjust Based on Criticism**
Use Task tool to delegate to github-issues-workflow agent:
- Address specific feedback from content critic
- Eliminate vague language and generic phrases
- Add concrete examples and technical specifics
- Clarify implementation scope and acceptance criteria
- Improve overall issue quality and actionability
- Return adjusted content for labeling

### **Step 5: Label Assignment**
Use Task tool to delegate to github-issues-workflow agent:
- Discover repository labels via `gh label list`
- Apply appropriate type labels (feat, bug, docs, refactor, etc.)
- Add workflow labels (dependencies, breaking change, etc.)
- Include quality labels (needs refinement, risky, etc.) if applicable
- Avoid conflicting label combinations
- Return content with proposed labels for validation

### **Step 6: Prioritize with BINARY CONFIDENCE SYSTEM**
Use Task tool to delegate to github-issues-workflow agent:
- Apply existing BINARY CONFIDENCE SYSTEM with strict 6-criteria assessment
- Analyze for priority indicators and conflicting evidence
- Determine confidence level (Confident/Uncertain)
- Assign priority label only if confident (critical/high priority)
- Default to medium priority (no label) if uncertain
- Return content with priority assignment and confidence justification

### **Step 7: Criticize Labels**
Use Task tool to delegate to critic agent with label validation focus:

**Label Critic Prompt**: "Validate the label assignments for appropriateness and accuracy:

**LABEL VALIDATION CRITERIA**:
- **Type Label Accuracy**: Verify feat/bug/docs/refactor matches actual content
- **Conflict Detection**: Identify incompatible label combinations
- **Completeness Check**: Ensure required labels are present
- **Repository Consistency**: Validate against established labeling patterns
- **Workflow Labels**: Assess dependencies, breaking change, risky labels appropriateness

**VALIDATION ACTIONS**:
- Challenge inappropriate or conflicting labels
- Suggest missing required labels
- Validate label consistency with issue content
- Recommend label adjustments if needed

**SKEPTICAL FOCUS**: Question label assignments that don't clearly match issue content."

### **Step 8: Criticize Priority**
Use Task tool to delegate to critic agent with priority validation focus:

**Priority Critic Prompt**: "Analyze the priority classification using the BINARY CONFIDENCE SYSTEM validation:

**VALIDATION CRITERIA**:
- Verify 'Confident' claims only if ALL 6 strict criteria were genuinely met
- Challenge confidence claims that lack sufficient evidence
- Look for overlooked conflicting indicators (enhancement, nice to have, future, optional)
- Validate precedent claims by checking cited similar issues
- Assess whether reasoning is truly falsifiable with specific evidence
- Question if 3+ keywords/indicators were actually present and relevant

**VALIDATION ACTIONS**:
- If 'Confident' claim is unjustified: Remove priority label (default to medium)
- If 'Uncertain' but strong evidence exists: Consider adding priority label
- Provide Priority Validation assessment
- Adjust labels only when confidence assessment was incorrect

**SKEPTICAL FOCUS**: Be particularly skeptical of 'Confident' claims - prevent priority inflation."

### **Step 9: Create Final Issue**
Use Task tool to delegate to github-issues-workflow agent:
- Create GitHub issue with refined content and validated labels/priority
- Add comprehensive analysis comments:
  - Content Quality Assessment with refinement summary
  - Label Assignment Rationale
  - Priority Analysis with confidence justification
  - Validation Results from critic reviews
- Return issue number, URL, and quality assessment summary

## Final Confirmation

Provide comprehensive issue details with:
- Direct GitHub issue link
- Final content quality assessment
- Label assignment summary  
- Priority classification with confidence level
- Summary of all agent assessments and refinements