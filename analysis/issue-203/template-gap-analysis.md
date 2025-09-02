# Template Coverage Gap Analysis
## Issue #203: Reverse Self-Hosting Architecture

### Current State Assessment

**Template Files**: 27 files in `/templates/`
**Claude Configuration Files**: 53 files in `/.claude/`
**Coverage Gap**: 26+ files need to be converted to templates

### Template System Coverage Analysis

#### Currently Templated (✅)
1. **CLAUDE.md.template** - Project instructions with parameter substitution
2. **prompts/worktree-deliver.template.md** - Workflow prompt template
3. **guidelines/** - 8 documentation templates (reusable across projects)
4. **readme/** - 3 README templates for different project types

#### Missing from Template System (❌)

**Critical Infrastructure Missing:**
- **Agent Definitions**: 0/12 agent files templated
  - `/claude/agents/foundation/` (6 agents) - Core AI workflow agents
  - `/claude/agents/specialists/` (6 agents) - Specialized workflow agents
- **Commands System**: 0/41 command files templated  
  - `/claude/commands/` (22 root commands)
  - `/claude/commands/issue/` (12 issue management commands) 
  - `/claude/commands/agents/` (3 agent management commands)
  - `/claude/commands/commands/` (2 command management commands)

**DevContainer Configuration Missing:**
- `.devcontainer/devcontainer.json` - Development environment setup
- `.devcontainer/Dockerfile` - Container image configuration  
- `.devcontainer/postCreate.sh` - Environment initialization
- `.devcontainer/postCreate-scripts/` - Setup script collection

**Repository Configuration Missing:**
- `.gitignore` - Git ignore patterns
- `.github/workflows/` - CI/CD pipeline definitions
- Various root-level configuration files

### Parameter Substitution Needs Analysis

#### Currently Supported Parameters
- `{{GITHUB_OWNER}}` - Repository owner
- `{{PROJECT_NAME}}` - Project name
- `{{REPO_URL}}` - Repository URL
- `{{CREATION_DATE}}` - Template deployment date
- `{{ACF_VERSION}}` - CLI version
- `{{TEMPLATE_VERSION}}` - Template bundle checksum

#### Additional Parameters Needed
- `{{CLI_DIRECTORY}}` - CLI tool directory (currently hardcoded as "cli")
- `{{GITHUB_REPO}}` - Repository name (separate from project name)
- `{{CONTAINER_REGISTRY}}` - Docker registry for DevContainer
- `{{PYTHON_VERSION}}` - Python version specification
- `{{NODE_VERSION}}` - Node.js version specification

### Self-Hosting Conversion Requirements

#### High Priority (Blocks Template-First Architecture)

1. **Agent Template Conversion**
   - Convert all 12 agent definitions to templates
   - Maintain agent functionality while adding parameterization
   - Preserve agent orchestration patterns

2. **Command Template Conversion** 
   - Convert all 41 command definitions to templates
   - Parameterize repository-specific references
   - Maintain command namespace structure

3. **Self-Bootstrap Command**
   - Add `acforge init --self` for repository self-deployment
   - Integrate with existing DevContainer workflow
   - Handle parameter detection for self-hosting scenario

#### Medium Priority (Enhances Template System)

4. **DevContainer Template Conversion**
   - Convert DevContainer configuration to templates
   - Parameterize container image versions
   - Maintain development workflow compatibility

5. **Enhanced Parameter System**
   - Support conditional template sections
   - Add template composition capabilities
   - Implement parameter validation

6. **Template Organization**
   - Group templates by deployment context (minimal, full, development)
   - Create template profiles for different project types
   - Support selective template deployment

#### Low Priority (Future Enhancements)

7. **Advanced Template Features**
   - Template inheritance and composition
   - Dynamic parameter resolution
   - Template dependency management

### Implementation Strategy

#### Phase 1: Core Template Migration
- **Agent System**: Convert all agent definitions to parameterized templates
- **Command System**: Convert all command definitions to parameterized templates
- **Self-Bootstrap**: Implement `acforge init --self` command

#### Phase 2: Infrastructure Template Migration  
- **DevContainer**: Convert development environment to templates
- **CI/CD**: Convert GitHub workflows to templates
- **Repository Config**: Convert root-level configuration files

#### Phase 3: Enhanced Template System
- **Conditional Templates**: Support project-type-specific template sections
- **Template Profiles**: Create deployment profiles (minimal, standard, full)
- **Validation System**: Add comprehensive template validation

### Risk Mitigation

#### Development Workflow Continuity
- **Gradual Migration**: Keep existing `.claude/` during transition
- **Validation Layer**: Prevent direct `.claude/` modifications
- **Developer Training**: Comprehensive documentation and examples

#### Template System Robustness  
- **Parameter Validation**: Ensure all required parameters are provided
- **Template Testing**: Automated testing of template deployment
- **Rollback Capability**: Support for deployment rollback on errors

#### Backward Compatibility
- **Legacy Support**: Maintain support for existing `.claude/` configurations
- **Migration Tools**: Automated conversion from self-hosted to template-based
- **Documentation**: Clear migration guide for existing repositories

### Success Metrics

#### Technical Metrics
- **Template Coverage**: 100% of `.claude/` configuration templated
- **Parameter Substitution**: All repository-specific values parameterized
- **Self-Bootstrap Success**: Repository can bootstrap itself from templates
- **Development Workflow**: No disruption to existing development processes

#### Quality Metrics
- **Template Validation**: 100% of templates pass validation
- **Deployment Success**: Templates deploy successfully to external repositories
- **Parameter Detection**: Automatic detection of all required parameters
- **Error Handling**: Graceful handling of template deployment errors

### Dependencies and Blockers

#### Technical Dependencies
- **CLI Enhancement**: `acforge init --self` command implementation
- **Parameter System**: Enhanced parameter substitution capabilities
- **Template Validation**: Comprehensive template validation system
- **State Management**: Enhanced ACForgeState for self-hosting tracking

#### Process Dependencies
- **Documentation**: Template development and migration guides
- **Testing**: Template deployment and validation test suite
- **Migration Strategy**: Phased rollout plan for existing repositories
- **Developer Training**: Team education on template-first workflow

### Next Steps

1. **Immediate**: Begin agent template conversion (highest impact, lowest risk)
2. **Short-term**: Implement `acforge init --self` command for self-bootstrap
3. **Medium-term**: Convert command system to templates
4. **Long-term**: Enhanced template system with conditional sections and profiles

This gap analysis reveals that while the template infrastructure exists, the majority of the Claude Code configuration (agents and commands) still needs to be converted to the template system to achieve the template-first architecture goal of Issue #203.