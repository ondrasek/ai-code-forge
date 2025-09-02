# Issue #213: Enhance issue:create command with fine-grained step-by-step workflow

## SITUATIONAL CONTEXT ANALYSIS

### SITUATION UNDERSTANDING:
Enhancement request to transform the current two-phase issue:create command (issue creation + priority validation) into a comprehensive step-by-step workflow: draft → refine → criticize refinement → adjust → label → prioritize → criticize labels → criticize priority workflow steps.

### RELEVANT CODEBASE CONTEXT:

#### Key Components:
- **Command**: `.claude/commands/issue/create.md` - Current two-phase implementation 
- **Agent**: `.claude/agents/specialists/github-issues-workflow.md` - Core issue management agent
- **Support Commands**: `.claude/commands/issue/refine.md`, `.claude/commands/issue/review.md`
- **Planning System**: `.claude/commands/issue/plan.md`, `.claude/commands/issue/start.md` (three-phase workflow pattern)
- **Label System**: `templates/guidelines/github-labels.md` - Label validation and management

#### Related Patterns:
- **Three-Phase Workflow**: plan → start → pr pattern already implemented
- **BINARY CONFIDENCE SYSTEM**: Strict 6-criteria priority assessment (critical/uncertain)
- **Agent Delegation**: Task tool delegation to github-issues-workflow agent
- **Label Discovery**: Dynamic label discovery prevents hardcoded assumptions
- **Step-by-Step Patterns**: Progressive implementation with validation gates

#### Dependencies:
- **GitHub CLI Integration**: `gh` commands for issue manipulation
- **Agent Coordination**: github-issues-workflow agent handles all GitHub operations
- **Critic Agent**: Already used for priority validation in Phase 2
- **Label Management**: Existing repository labels discovered dynamically

#### Constraints:
- **Agent Isolation**: github-issues-workflow is terminal agent (no sub-agents)
- **Label Restrictions**: ONLY use existing repository labels, no autonomous creation
- **Context Separation**: Keep workflow management off main context
- **Safety Gates**: Human approval required for significant operations

### HISTORICAL CONTEXT:

#### Past Decisions:
- **Two-Phase Approach**: Current create.md uses github-issues-workflow + critic validation
- **BINARY CONFIDENCE**: Strict 6-criteria system prevents priority inflation
- **Agent Delegation**: All GitHub operations delegated to specialized agents
- **Dynamic Labels**: Label discovery prevents hardcoded assumptions
- **Three-Phase Pattern**: plan/start/pr commands already implement step-by-step workflow

#### Evolution:
- **Migration from .acf to .acforge**: Recent codebase-wide naming convention migration
- **Agent Specialization**: Development of specialized agents for focused responsibilities
- **Workflow Sophistication**: Evolution from simple commands to multi-phase workflows
- **Safety Enhancement**: Introduction of validation gates and approval mechanisms

#### Lessons Learned:
- **Agent Terminal Design**: github-issues-workflow is terminal to prevent recursive loops
- **Conservative Priority Assignment**: Default to medium priority when uncertain
- **User Override Capabilities**: Always provide escape hatches for automation
- **Append-Only Updates**: Preserve issue conversation threads during autonomous updates

#### Success Patterns:
- **Task Tool Delegation**: Clean separation of concerns through agent delegation
- **Progressive Workflows**: plan/start/pr pattern provides structured approach
- **Safety Gates**: Human approval requirements prevent over-automation
- **Context Preservation**: Off-context operations keep main conversation clean

### SITUATIONAL RECOMMENDATIONS:

#### Suggested Approach:
**Enhanced Multi-Step Workflow Design** building on existing patterns:

1. **Draft Phase**: Initial issue description gathering and basic validation
2. **Refine Phase**: Leverage existing `/issue:refine` command integration  
3. **Critical Review Phase**: Apply critic agent to refinement output
4. **Adjustment Phase**: Human-guided refinement based on criticism
5. **Label Classification Phase**: Apply existing label discovery and assignment
6. **Priority Assessment Phase**: Use existing BINARY CONFIDENCE SYSTEM
7. **Label Criticism Phase**: Validate label assignments through critic review
8. **Priority Criticism Phase**: Current priority validation from existing Phase 2

#### Key Considerations:
- **Backwards Compatibility**: Preserve existing two-phase functionality as "express mode"
- **Interrupt/Resume Capability**: Allow users to exit and resume workflow at any step
- **State Persistence**: Store workflow state for resume capability
- **Agent Reuse**: Leverage existing github-issues-workflow and critic agents
- **Safety Gates**: Maintain human approval at critical decision points

#### Implementation Notes:
- **Progressive Enhancement**: Add step-by-step mode while preserving current workflow
- **State Management**: Use temporary files or issue comments for workflow state
- **Command Line Interface**: Support both interactive and argument-driven modes
- **Error Recovery**: Provide rollback and restart capabilities at each phase

#### Testing Strategy:
- **Workflow Validation**: Test each step independently and in sequence
- **State Persistence**: Validate interrupt/resume functionality
- **Agent Integration**: Verify proper delegation to existing agents
- **Label Discovery**: Ensure dynamic label discovery works across all steps
- **Safety Mechanisms**: Test all approval gates and override capabilities

### IMPACT ANALYSIS:

#### Affected Systems:
- **issue:create Command**: Primary enhancement target - add step-by-step mode
- **github-issues-workflow Agent**: Enhanced with workflow state management
- **Existing Commands**: issue:refine integration, critic agent coordination
- **Label System**: Expanded usage of existing dynamic discovery system
- **User Experience**: Significant workflow complexity increase (optional)

#### Risk Assessment:
- **Complexity Risk**: Multi-step workflow significantly increases command complexity
- **User Experience Risk**: May overwhelm users who prefer simple issue creation
- **State Management Risk**: Workflow interruption/resume adds persistence complexity
- **Agent Coordination Risk**: Multiple agent interactions increase failure modes
- **Backwards Compatibility Risk**: Must not break existing two-phase workflow

#### Documentation Needs:
- **Enhanced Command Documentation**: Update create.md with step-by-step workflow
- **User Guides**: Document when to use step-by-step vs express modes
- **Agent Coordination**: Document new github-issues-workflow capabilities
- **Workflow State**: Document interrupt/resume functionality
- **Integration Patterns**: Document critic agent integration across multiple steps

#### Migration Requirements:
- **Command Enhancement**: Extend existing create.md without breaking current usage
- **Agent Enhancement**: Add workflow state management to github-issues-workflow
- **State Storage**: Implement workflow state persistence mechanism
- **Testing Infrastructure**: Enhanced test coverage for multi-step workflows

### ANALYSIS DOCUMENTATION:

#### Context Sources:
- `.claude/commands/issue/create.md` - Current two-phase implementation
- `.claude/agents/specialists/github-issues-workflow.md` - Core agent capabilities
- `.claude/commands/issue/plan.md`, `.claude/commands/issue/start.md` - Three-phase pattern
- `.claude/commands/issue/refine.md` - Existing refinement capabilities
- `templates/guidelines/github-labels.md` - Label management system
- GitHub repository labels - Current label ecosystem

#### Key Discoveries:
- **Existing Pattern**: Three-phase plan/start/pr workflow provides proven step-by-step template
- **Agent Architecture**: github-issues-workflow is terminal agent with comprehensive capabilities
- **BINARY CONFIDENCE**: Sophisticated priority assessment system already implemented
- **Label Discovery**: Dynamic label system prevents hardcoded dependencies
- **Safety Mechanisms**: Existing approval gates and override systems provide safety model

#### Decision Factors:
- **User Choice**: Must provide both express and detailed workflow modes
- **State Management**: Workflow interruption requires persistent state storage
- **Agent Reuse**: Leverage existing specialized agents rather than creating new ones
- **Safety First**: Maintain all existing safety gates and approval mechanisms
- **Backwards Compatibility**: Existing usage patterns must continue to work

## CURRENT COMMAND STRUCTURE AND IMPLEMENTATION

### issue:create.md Analysis

**Current Two-Phase Implementation:**
```markdown
Phase 1 - Issue Creation with Confidence Assessment:
- Delegate to github-issues-workflow agent
- Apply BINARY CONFIDENCE SYSTEM (6 strict criteria)
- Create GitHub issue with best-guess priority
- Add mandatory Priority Analysis comment
- Return issue number, URL, confidence assessment

Phase 2 - Priority Validation:
- Delegate to critic agent with priority validation prompt
- Validate confidence claims with skeptical focus
- Adjust labels if confidence assessment incorrect
- Add Priority Validation comment
- Report final priority classification
```

**Key Implementation Details:**
- Uses Task tool for agent delegation
- github-issues-workflow handles GitHub operations
- Critic agent provides validation layer
- BINARY CONFIDENCE SYSTEM: Confident (assign priority label) vs Uncertain (no priority label)
- Six strict criteria for confidence: 3+ indicators, specific evidence, precedent, no conflicts, falsifiable logic, explicit keywords

### BINARY CONFIDENCE SYSTEM Analysis

**Strict Criteria Framework (ALL must be met for "Confident"):**
1. **3+ Clear Indicators**: Specific urgency/impact/scope keywords
2. **Specific Evidence**: Direct quotes supporting priority decision
3. **Clear Precedent**: Reference similar issues with established patterns
4. **No Conflicts**: Verify absence of conflicting low-priority indicators
5. **Falsifiable Logic**: Reasoning that can be proven wrong with evidence
6. **Explicit Keywords**: Technical severity/business impact language present

**Implementation Algorithm:**
```bash
For each issue:
1. Extract keywords and technical concepts from issue content
2. Count urgency/impact indicators (requirement: 3+)  
3. Search for conflicting low-priority indicators
4. Verify precedent by searching similar existing issues
5. Generate falsifiable reasoning with specific evidence
6. If ALL 6 criteria met → Confident (apply priority label)
7. If ANY criteria failed → Uncertain (NO priority label)
```

### Agent Integration Patterns

**github-issues-workflow Agent Capabilities:**
- Terminal agent (no sub-agents) with comprehensive GitHub integration
- Dynamic label discovery: `gh label list --repo ondrasek/ai-code-forge --json name,color,description`
- Priority assignment using BINARY CONFIDENCE SYSTEM
- Cross-referencing and web research integration
- Append-only updates for autonomous operations
- User-requested modifications for explicit changes
- Issue closure protocol with appropriate labels and documentation

**Label Management System:**
- **Discovery First**: Always discover available labels before operations
- **No Hardcoding**: Never assume specific labels exist
- **Repository Only**: Only use existing labels, no autonomous creation
- **Quality Categories**: Type labels (feat/bug/docs), priority labels (critical/high priority/nice to have), workflow labels (dependencies/breaking change)

### Existing Step-by-Step Workflow Patterns

**Three-Phase Pattern (plan/start/pr):**
- **Phase 1 (plan)**: Deep analysis, implementation planning, user approval gate
- **Phase 2 (start)**: Systematic execution, progress tracking, agent coordination  
- **Phase 3 (pr)**: PR creation, review integration, completion

**Key Pattern Elements:**
- **Validation Gates**: Ensure previous phase completion before proceeding
- **State Persistence**: Store phase data for next phase consumption
- **Agent Coordination**: Specialized agents for different concerns
- **Current Branch**: Work directly on current branch (no forced branching)
- **Error Recovery**: Rollback capabilities and recovery options

### Repository Label System Analysis

**Current Label Categories (from gh label list):**
- **Type Labels**: bug, enhancement, feat, fix, docs, test, refactor, chore
- **Priority Labels**: critical, high priority, nice to have  
- **Workflow Labels**: dependencies, breaking change, human feedback needed
- **Quality Labels**: security, risky, needs refinement, over-engineered, quick win
- **Status Labels**: duplicate, invalid, wontfix, obsolete, not-duplicate
- **Community Labels**: good first issue, help wanted

**Priority System Integration:**
- **critical**: Must implement now - critical severity issues
- **high priority**: Important issues affecting user experience  
- **nice to have**: Future enhancements when time permits
- **Default**: No priority label = medium priority

### Workflow Interruption/Resume Capabilities

**Current State Management:**
- Three-phase commands store metadata between phases
- github-issues-workflow agent maintains issue state through GitHub
- Append-only comment system preserves conversation threads
- Label updates track progress and status

**Resume Patterns:**
- **Validation Checks**: Each phase validates prerequisites before proceeding
- **State Recovery**: Load previous phase outputs and validate completeness
- **Error Handling**: Clear error messages when prerequisites missing
- **User Guidance**: Instructions for completing missing prerequisites

## PROPOSED ENHANCEMENT ARCHITECTURE

### Enhanced Multi-Step Workflow Design

**Extended Eight-Step Process:**
1. **Draft Phase**: Initial issue description gathering and basic validation
2. **Refine Phase**: Comprehensive elaboration using existing issue:refine integration
3. **Criticize Refinement**: Apply critic agent to refinement quality and completeness  
4. **Adjust Phase**: Human-guided refinement based on critical feedback
5. **Label Classification**: Apply existing dynamic label discovery and assignment
6. **Prioritize Phase**: Use existing BINARY CONFIDENCE SYSTEM for priority assessment
7. **Criticize Labels**: Validate label assignments through critic agent review
8. **Criticize Priority**: Current priority validation system from existing Phase 2

### Implementation Strategy

**Mode Selection:**
- **Express Mode**: Current two-phase workflow (backwards compatible)
- **Detailed Mode**: New eight-step workflow for comprehensive issue creation
- **Command Line**: `--detailed` or `--express` flags to specify mode
- **Interactive**: Prompt user for mode selection when no flag provided

**State Management:**
- **Workflow State File**: `.acforge/workflows/issue-create-{timestamp}.json`
- **Resume Command**: `issue:create --resume {workflow-id}`
- **State Schema**: Track current step, completed steps, intermediate outputs, user decisions
- **Cleanup**: Automatic cleanup of completed workflow states after 7 days

**Agent Coordination Strategy:**
- **Primary Agent**: github-issues-workflow remains primary GitHub interface
- **Critic Agent**: Used for multiple validation steps (refinement, labels, priority)
- **Existing Integration**: Leverage issue:refine command for comprehensive elaboration
- **Terminal Design**: Maintain github-issues-workflow as terminal agent (no sub-agents)

### User Experience Design

**Interactive Flow:**
```
Step 1: Draft → [Continue] [Save & Exit] [Switch to Express]
Step 2: Refine → [Continue] [Revise] [Save & Exit]  
Step 3: Review Refinement → [Accept] [Request Changes] [Save & Exit]
Step 4: Adjust → [Continue] [Revise Again] [Save & Exit]
Step 5: Label → [Continue] [Modify Labels] [Save & Exit]
Step 6: Prioritize → [Continue] [Challenge Priority] [Save & Exit]
Step 7: Review Labels → [Accept] [Adjust] [Save & Exit]
Step 8: Review Priority → [Accept] [Adjust] [Create Issue]
```

**Workflow Controls:**
- **Save & Exit**: Store current state and exit for later resume
- **Skip to Express**: Convert to two-phase mode at any point
- **Restart Step**: Redo current step with different inputs
- **Previous Step**: Return to previous step for revision
- **Cancel Workflow**: Abandon workflow and cleanup state

**User Guidance:**
- **Step Context**: Clear explanation of current step purpose and options
- **Progress Indicator**: Show current step position in workflow
- **Time Estimation**: Approximate time remaining based on typical usage
- **Help System**: Detailed help for each step with examples

### Safety and Validation Framework

**Approval Gates:**
- **After Refinement Criticism**: Human review required before proceeding to adjustment
- **Before Label Assignment**: Human confirmation of label selection strategy
- **After Priority Assessment**: Human review of priority assignment rationale
- **Before Issue Creation**: Final review of complete issue before GitHub creation

**Override Mechanisms:**
- **Express Mode Switch**: Convert to simpler workflow at any point
- **Step Skip**: Allow skipping non-critical steps with warnings
- **Manual Override**: Direct editing capability for any workflow output
- **Emergency Exit**: Immediate workflow termination with state preservation

**Validation Framework:**
- **Input Validation**: Ensure all required inputs provided at each step
- **State Consistency**: Validate workflow state integrity before each step
- **GitHub Validation**: Verify GitHub connectivity and permissions before creation
- **Label Validation**: Ensure selected labels exist in repository before assignment

### Enhanced Command Interface

**Command Signatures:**
```bash
# New enhanced workflow
/issue:create --detailed "Initial description"
/issue:create --detailed --draft "Draft content"

# Resume capability  
/issue:create --resume {workflow-id}

# Express mode (current behavior)
/issue:create --express "Description"
/issue:create "Description"  # default to express for backwards compatibility

# Workflow management
/issue:create --list-workflows   # Show active workflows
/issue:create --cleanup-workflows  # Clean up old workflows
```

**Argument Processing:**
- **Description Argument**: If provided, use as initial draft
- **Mode Selection**: Default to express mode for backwards compatibility
- **Workflow ID**: Support resume by workflow identifier
- **Interactive Prompts**: When no arguments provided, guide user through mode selection

### Integration with Existing Systems

**issue:refine Integration:**
- **Step 2 Enhancement**: Use existing issue:refine command for comprehensive elaboration
- **Context Passing**: Pass draft content to refine command for enhancement
- **Output Integration**: Integrate refined output back into workflow
- **Command Reuse**: Leverage existing refinement capabilities without duplication

**Critic Agent Enhancement:**
- **Multiple Usage**: Use critic agent for refinement review, label validation, priority validation
- **Specialized Prompts**: Different critic prompts for each validation step
- **Consistent Interface**: Maintain consistent critic agent interaction patterns
- **Quality Assurance**: Ensure consistent criticism quality across workflow steps

**GitHub-Issues-Workflow Enhancement:**
- **State Management**: Add workflow state tracking capabilities
- **Step-by-Step Mode**: Support progressive issue building
- **Label Discovery**: Enhanced label discovery with context-aware recommendations
- **Priority Assessment**: Integrate BINARY CONFIDENCE SYSTEM with step-by-step flow

## CONSTRAINTS AND DEPENDENCIES

### Technical Constraints

**Agent Architecture Constraints:**
- github-issues-workflow must remain terminal agent (no sub-agent spawning)
- All GitHub operations must be delegated to github-issues-workflow
- Critic agent coordination must not create recursive delegation loops
- State management must not pollute main conversation context

**GitHub Integration Constraints:**
- Dynamic label discovery required before all label operations
- Repository permissions must be validated before GitHub operations
- API rate limiting must be considered for multi-step operations
- Issue creation is atomic operation - no partial issues in GitHub

**State Management Constraints:**
- Workflow state must be persistent across Claude Code sessions
- State storage must not interfere with git operations
- Cleanup mechanisms required to prevent state accumulation
- State format must support schema evolution

### Business Constraints

**User Experience Constraints:**
- Must not break existing express workflow (backwards compatibility)
- Learning curve for new workflow must be gradual
- Clear escape hatches required for workflow abandonment
- Performance must not significantly degrade for simple use cases

**Operational Constraints:**
- GitHub repository must exist and be accessible
- User must have appropriate GitHub permissions
- Network connectivity required for GitHub operations
- Claude Code session persistence affects workflow resumability

### Dependencies

**Critical Dependencies:**
- **github-issues-workflow agent**: Core GitHub integration capability
- **critic agent**: Multi-step validation and review capability
- **issue:refine command**: Comprehensive issue elaboration
- **GitHub CLI (gh)**: GitHub repository operations
- **Repository labels**: Dynamic label discovery and management

**Optional Dependencies:**
- **Web search capability**: Enhanced research for refinement phase
- **Cross-reference system**: Related issue discovery and linking
- **Template system**: Issue template integration for structured creation
- **Workflow automation**: GitHub Actions integration for automated workflows

### Risk Mitigation Strategies

**Complexity Management:**
- Progressive disclosure of workflow complexity
- Clear mode selection with guidance
- Escape hatches at every step
- Comprehensive documentation and examples

**State Management Risks:**
- Robust state serialization and deserialization
- State corruption detection and recovery
- Automatic cleanup of abandoned workflows
- Migration strategy for state schema changes

**Agent Coordination Risks:**
- Clear agent responsibility boundaries
- Error handling for agent communication failures
- Timeout mechanisms for long-running agent operations
- Fallback strategies for agent unavailability

**User Experience Risks:**
- Extensive user testing with both modes
- Clear feedback mechanisms for workflow issues
- Progressive enhancement rather than replacement
- Comprehensive error messages and recovery guidance

## RECOMMENDATIONS

### Implementation Priority

**High Priority** (Blocks selection optimization):
- Implement basic eight-step workflow structure
- Add workflow state management system  
- Integrate issue:refine command in refinement step
- Implement critic agent integration for validation steps
- Add mode selection (express vs detailed)

**Medium Priority** (Enhances user experience):
- Implement workflow interruption and resume capability
- Add progress indicators and user guidance
- Implement step navigation (previous/next/skip)
- Add workflow cleanup and management commands
- Enhance error handling and recovery mechanisms

**Low Priority** (Future enhancements):
- Add workflow templates and customization
- Implement advanced state analytics and optimization
- Add workflow sharing and collaboration features
- Integrate with GitHub Actions for automated workflows
- Add machine learning for workflow optimization

### Questions for Clarification

**Contrarian Perspective - Complexity Concerns:**
- **Is the added complexity justified?** The current two-phase workflow is already sophisticated with BINARY CONFIDENCE SYSTEM. Are users actually requesting this level of granularity, or are we over-engineering?

**Critical Questions:**
- **State persistence scope**: Should workflow state persist across Claude Code restarts, or only within session? Cross-session persistence adds significant complexity.
- **Mode default behavior**: Should new installations default to express or detailed mode? Backwards compatibility suggests express, but enhancement value suggests detailed.
- **Validation depth**: How deep should critic agent validation go at each step? Deep validation may slow workflow significantly.
- **Failure handling**: When GitHub operations fail mid-workflow, should the system retry, rollback, or pause for manual intervention?

**Integration Questions:**
- **Existing command integration**: Should issue:refine command be modified to support workflow context, or should workflow call it as-is?
- **Agent enhancement scope**: How much state management should be added to github-issues-workflow without violating its terminal agent constraint?
- **User experience testing**: What user testing approach will validate the step-by-step workflow provides value over express mode?

**Technical Decisions:**
- **State storage format**: JSON files in .acforge directory, or GitHub issue comments, or both?
- **Workflow identification**: Random IDs, timestamps, or user-defined names for workflow identification?
- **Cleanup policies**: Automatic cleanup timeframes and user control over workflow retention?

This analysis provides comprehensive contextual understanding for implementing Issue #213's enhanced step-by-step workflow while maintaining existing functionality and safety mechanisms.