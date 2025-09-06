SITUATIONAL CONTEXT ANALYSIS
============================

SITUATION UNDERSTANDING:
Issue #203 "Reverse Self-Hosting" requires converting ai-code-forge from direct self-hosting to a template-first architecture where the repository serves as a template that deploys its configuration to external repositories via the acforge CLI tool.

RELEVANT CODEBASE CONTEXT:

**Key Components:**
- **CLI Infrastructure**: `/cli/` - Python package `acforge` (v3.0.3) with template management capabilities
- **Template System**: `/templates/` - Source of truth for all distributable configuration files
- **Claude Configuration**: `/.claude/` - Current self-hosted Claude Code configuration
- **DevContainer Setup**: `/.devcontainer/` - Development environment configuration
- **Build Pipeline**: `/cli/build-with-templates.sh` - Template bundling mechanism
- **Analysis Framework**: `/analysis/` - Issue-specific analysis and documentation

**Related Patterns:**
- **Template Bundling Pattern**: CLI build copies `/templates/` to `cli/src/ai_code_forge_cli/templates/` temporarily for packaging
- **Parameter Substitution Pattern**: Templates use `{{PARAMETER}}` placeholders (e.g., `{{GITHUB_OWNER}}`, `{{PROJECT_NAME}}`)
- **State Management Pattern**: ACForge maintains deployment state in `.acforge/state.json`
- **Fallback Pattern**: TemplateManager tries bundled templates first, falls back to development mode (direct `/templates/` access)
- **Migration Pattern**: CLI supports both `.claude/` and `.acforge/` directory structures

**Dependencies:**
- **Template Source Dependency**: CLI build depends on `/templates/` directory existing
- **Parameter Dependencies**: Templates require GitHub owner, project name, repository URL detection
- **Version Coordination**: CLI version (3.0.3) must stay synchronized with template bundle checksum
- **Development Environment**: DevContainer configuration includes acforge CLI installation via postCreate scripts

**Constraints:**
- **Single Source of Truth**: Templates maintained in `/templates/` only - CLI bundled version is temporary build artifact
- **Template Parameterization**: Limited parameter substitution system - basic `{{VARIABLE}}` replacement
- **CLI Distribution**: Package must be self-contained with bundled templates
- **Configuration Compatibility**: Must support migration from existing `.claude/` to `.acforge/` structures

HISTORICAL CONTEXT:

**Past Decisions:**
1. **Direct Self-Hosting Approach**: Repository originally hosted its own Claude Code configuration directly in `/.claude/`
2. **Template Bundling Strategy**: Build process copies templates into CLI package to avoid symlink issues
3. **Dual Directory Support**: CLI recognizes both `.claude/` and `.acforge/` for backward compatibility
4. **Development Mode Fallback**: TemplateManager falls back to direct `/templates/` access when bundled templates unavailable

**Evolution:**
- **Migration from acf to acforge**: Recent commits show complete renaming from `acf` to `acforge` naming convention
- **Template Parameterization**: Basic parameter substitution system implemented with `{{PARAMETER}}` syntax
- **State Management**: ACForgeState system tracks template versions and deployment history
- **Build Process Evolution**: Build script handles temporary template copying and cleanup

**Lessons Learned:**
- **Template Source Truth**: Build comment emphasizes never modifying `cli/src/ai_code_forge_cli/templates/` - `/templates/` is canonical
- **Symlink Issues**: Build process avoids symlinks due to compatibility issues
- **Version Coordination**: Template bundle checksum provides version coordination between repository and CLI

**Success Patterns:**
- **Atomic Deployment**: TemplateDeployer handles complete template deployment with rollback capability
- **Parameter Detection**: RepositoryDetector automatically detects GitHub owner/project from repository context
- **State Tracking**: JSON-based state management provides deployment history and integrity checking

SITUATIONAL RECOMMENDATIONS:

**Suggested Approach - Template-First Architecture:**

1. **High Priority: Reverse Configuration Dependency**
   - Convert `/.claude/` from canonical to generated/deployed configuration
   - Make `/templates/` the single source of truth for ALL configuration
   - Update DevContainer setup to use `acforge init` instead of direct `.claude/` usage

2. **High Priority: Enhanced Template System**
   - Expand parameter substitution beyond basic variables
   - Add conditional template sections for different project types
   - Implement template composition/inheritance patterns

3. **High Priority: Self-Bootstrap Mechanism**  
   - Create `acforge init --self` command for repository self-deployment
   - Integrate self-deployment into DevContainer postCreate process
   - Maintain development workflow continuity

4. **Medium Priority: Template Validation**
   - Expand TemplateManager validation for template integrity
   - Add pre-deployment validation of parameter substitution
   - Implement template syntax checking

**Key Considerations:**
- **Development Workflow Impact**: Developers must adapt to template-first approach - changes go to `/templates/` first, then deploy
- **CI/CD Integration**: Build/test pipelines may need updates to handle template-first workflow  
- **Migration Strategy**: Existing forks/repositories using direct self-hosting need migration path
- **Template Complexity**: Current parameter system is basic - may need enhancement for complex configurations

**Implementation Notes:**
- **Gradual Migration**: Keep existing `.claude/` during transition, mark as generated/deprecated
- **Validation Layer**: Add checks to prevent direct `.claude/` edits, redirect to templates
- **Documentation Updates**: Update all documentation to reflect template-first approach
- **DevContainer Integration**: Modify postCreate scripts to use `acforge init --self`

**Testing Strategy:**
- **Template Deployment Tests**: Verify templates deploy correctly to fresh repositories
- **Parameter Substitution Tests**: Validate all parameter combinations work correctly  
- **Self-Hosting Tests**: Verify repository can bootstrap itself via templates
- **Migration Tests**: Test conversion of existing self-hosted repositories

IMPACT ANALYSIS:

**Affected Systems:**
- **DevContainer Configuration**: PostCreate scripts, Dockerfile, devcontainer.json
- **CLI Tool**: Enhanced init command, new self-deployment features
- **Template System**: Expanded to include ALL configuration (currently partial)
- **Documentation**: README, setup guides, development workflow docs
- **Build Process**: Integration of self-deployment into build pipeline

**Risk Assessment:**
- **Breaking Changes**: Major workflow change - developers need retraining
- **Template Complexity**: Current parameter system may be insufficient for complex cases
- **Bootstrap Dependency**: Self-deployment creates circular dependency that must be carefully managed
- **Migration Friction**: Existing repositories need migration path

**Documentation Needs:**
- **Template Development Guide**: How to modify/extend templates
- **Self-Hosting Migration Guide**: Converting existing repositories 
- **Parameter Reference**: Available parameters and usage patterns
- **Troubleshooting Guide**: Common template deployment issues

**Migration Requirements:**
- **Gradual Rollout**: Phase conversion to avoid disrupting active development
- **Backward Compatibility**: Maintain support for existing `.claude/` configurations during transition
- **Validation Tools**: Scripts to verify template deployment correctness
- **Developer Training**: Documentation and examples for new workflow

ANALYSIS DOCUMENTATION:

**Context Sources:**
- `/cli/pyproject.toml` - CLI package configuration and dependencies
- `/cli/src/ai_code_forge_cli/core/templates.py` - Template management system
- `/cli/src/ai_code_forge_cli/core/deployer.py` - Template deployment logic  
- `/cli/src/ai_code_forge_cli/commands/init.py` - Repository initialization
- `/cli/build-with-templates.sh` - Template bundling process
- `/templates/CLAUDE.md.template` - Template parameter substitution example
- `/.devcontainer/postCreate.sh` - Development environment setup
- `/CLAUDE.md` vs `/templates/CLAUDE.md.template` - Self-hosting vs template comparison

**Key Discoveries:**
1. **Existing Template Infrastructure**: Sophisticated template management system already exists with parameter substitution, state tracking, and deployment capabilities
2. **Template Bundling Process**: Build system temporarily copies templates into CLI package, emphasizing `/templates/` as source of truth
3. **Development Mode Fallback**: TemplateManager supports development workflow by falling back to direct template access
4. **Parameter Substitution System**: Basic but functional `{{PARAMETER}}` replacement system with common variables
5. **Dual Configuration Support**: CLI already handles both `.claude/` and `.acforge/` directory structures
6. **Self-Hosting Evidence**: Current CLAUDE.md shows resolved parameters vs template shows `{{PARAMETER}}` placeholders

**Decision Factors:**
- **Template System Maturity**: Existing infrastructure reduces implementation complexity
- **Parameter System Limitations**: May need enhancement for complex scenarios
- **Development Workflow**: Must maintain smooth development experience during transition
- **Build Integration**: Template bundling process provides foundation for self-deployment
- **State Management**: Existing ACForgeState system provides deployment tracking foundation

**Architectural Insight:**
The codebase already contains most building blocks needed for template-first architecture. The primary challenge is inverting the dependency relationship: making the repository consume its own templates rather than maintaining direct configuration files. This is more of an orchestration and workflow challenge than a technical implementation challenge.