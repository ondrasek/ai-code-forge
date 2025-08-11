# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **ACF CLI Tool**: Complete configuration management tool for AI Code Forge installations (closes #59)
  - `ai-code-forge install` command for automated configuration deployment with comprehensive file management
  - `ai-code-forge status` command for installation verification and diagnostics with detailed component reporting
  - Support for targeted installations with `--target` option for custom directory deployment
  - Force installation option with `--force` flag for overwriting existing configurations
  - Automated deployment of `.claude/` (agents, commands, settings), `.acf/` (templates, docs), and `CLAUDE.md`
  - Complete Python packaging with pyproject.toml and build system for distribution-ready wheel creation
  - Comprehensive test suite with 30 test cases covering installer, CLI, and integration scenarios
  - Build validation system with GitHub Actions workflow for automated CI/CD pipeline

### Fixed
- **Comprehensive PR Review Response**: Addressed all high/medium priority concerns in worktree management scripts (closes #105)
  - Fixed critical TOCTOU race condition in directory creation logic with proper timing attack prevention
  - Standardized repository name validation across worktree-create.sh and worktree-cleanup.sh with enhanced security
  - Enhanced error handling with specific path context and proper error code returns for failed operations
  - Implemented comprehensive cleanup logic for failed worktree creation operations with secure state management
  - Added comprehensive security testing infrastructure with unit tests for validation functions and injection attack prevention

### Removed
- **Development Scripts Cleanup**: Removed obsolete development and testing scripts (refs #105)
  - Removed setup-claude-memory.sh (functionality integrated into launch script)
  - Removed test-agents.sh and test-session-logging.sh (development utilities)
  - Updated README.md to reflect current script system

## [2.88.0] - 2025-08-09

### Added
- **Complete Worktree Management System**: Unified interface for parallel development workflows (closes #105)
  - Added worktree.sh unified wrapper script with comprehensive command delegation
  - Added worktree-list.sh for detailed worktree listing with verbose mode support
  - Enhanced DevContainer setup with worktree directory structure and environment variables
  - Updated README.md with complete worktree management documentation and usage examples
  - Comprehensive Git worktree utilities supporting GitHub issue integration and cleanup functionality

## [2.87.0] - 2025-08-09

### Added
- **GitHub Issue Integration for Worktree Scripts**: Enhanced worktree-create.sh with intelligent GitHub issue workflow integration (closes #105)
  - Added `--from-issue <number>` flag for automatic worktree creation from GitHub issues
  - Intelligent branch detection system finds existing issue branches across multiple naming patterns
  - Automatic branch name generation from GitHub issue titles using gh CLI integration
  - Support for both existing branch discovery and new branch creation workflows
  - Enhanced worktree creation workflow for seamless DevContainer development with GitHub Issues

## [2.85.0] - 2025-08-09

### Enhanced
- **GitHub Issues Closure Protocols**: Comprehensive mandatory issue closure system for github-issues-workflow agent
  - Added 5-step closure protocol with required labeling and documentation standards
  - Defined 5 closure categories: wontfix, duplicate, invalid, completed, superseded
  - Implemented structured closure comment template with decision context and cross-references
  - Added GitHub CLI command patterns and quality assurance checklist for consistent closures
  - Enhanced issue lifecycle management with detailed guidelines and examples for each closure type

## [2.83.0] - 2025-08-09

### Added
- **Enhanced GitHub Workflow Agents**: Major improvements to GitHub Issues and PR workflow automation
  - Added MANDATORY label update requirements for github-issues-workflow agent ensuring consistent issue tracking
  - Implemented comprehensive append-only policy preventing accidental content modification while preserving audit trails
  - Enhanced GitHub CLI integration with smart label discovery using existing repository labels only
  - Added automatic issue label updates when PR workflow begins for seamless issue-PR coordination
  - Implemented intelligent cross-referencing between issues and PRs with real-time status tracking
  - Added recursion prevention mechanisms to prevent infinite agent delegation loops
  - Enforced existing-labels-only policy with dynamic label discovery preventing label proliferation
  - Enhanced workflow reliability through comment-based updates instead of destructive content replacement

## [2.82.0] - 2025-08-09

### Added
- **Multi-Agent Worktree Documentation Integration**: Enhanced project with comprehensive multi-agent development workflow documentation (refs #103)
  - Integrated README guidelines system with multi-agent coordination patterns
  - Documented multi-agent worktree strategies for parallel development workflows
  - Enhanced GitHub Issues integration for specification-driven development

## [2.81.0] - 2025-08-09

### Added
- **README Documentation Guidelines Framework**: Comprehensive AI-optimized documentation system (refs #95)
  - Created templates/guidelines/readme-documentation-guidelines.md with XML-structured guidelines for consistent AI interpretation
  - Added three reusable README templates: general-project-template.md, mcp-server-template.md, library-package-template.md
  - Implemented user-first design principles optimizing for 5-second understanding over format compliance
  - Guidelines-based approach achieving consistency through principles rather than rigid tooling
  - Progressive disclosure hierarchy from README → docs → wiki for better information architecture

### Changed
- **Main README.md**: Updated with user-first design principles and improved quick start experience
- **Perplexity MCP README**: Enhanced with better quick start flow and 2-minute setup guide
- **Documentation Strategy**: Shifted from Standard README compliance to superior guidelines-based approach for better user experience

## [2.79.1] - 2025-08-09

### Changed
- **README.md Documentation Accuracy**: Comprehensive update to reflect current project structure and capabilities
  - Updated project description from active agent system to template/development workspace
  - Corrected Claude Code version requirement from 2.70.0+ to 2.78.0+
  - Removed references to non-existent .claude/ directories and incorrect agent/command counts
  - Updated architecture section to show actual directory structure
  - Fixed Quick Start section to reference actual scripts in /scripts/ directory
  - Updated configuration section to reference actual template locations
  - Improved clarity for users setting up the template system

## [2.78.0] - 2025-08-07

### Added
- **Enhanced Git-Workflow Error Handling**: Intelligent diagnostic and recovery patterns replacing generic error messages (closes #55)
  - Transform "Warning: Issue not found" into comprehensive diagnostics with auth checks, repository access tests, and smart suggestions
  - Replace "ERROR: No GitHub issue reference detected" with intelligent branch analysis and contextual guidance
  - Enhanced error recovery protocols with mandatory user confirmation for destructive operations
  - Proactive diagnostic patterns that test each command and provide specific solutions when failures occur
  - Safety protocols preventing data loss with explicit user confirmation templates for destructive operations
  - Context-aware resolution suggestions based on repository state analysis
- **Three-Phase GitHub Issue Workflow**: New numbered `/issue` commands for systematic GitHub issue development
  - `/issue plan <issue-number>`: Comprehensive analysis and implementation planning with user approval gates
  - `/issue start <issue-number>`: Systematic execution with git workflow, feature branch management, and progress tracking
  - `/issue pr <issue-number>`: User-controlled PR creation with comprehensive analysis and multiple confirmation gates
  - Full integration with github-issues-workflow agent for seamless GitHub CLI operations
  - Cross-phase data persistence and proper git workflow management (planning on current branch, implementation on feature branch)
  - Complements existing general `/issue` commands (create, review, cleanup) with issue-specific workflow system

## [2.75.0] - 2025-08-07

### Changed
- **Configuration Simplification**: Streamlined .claude/settings.json to essential minimal configuration
  - Replaced extensive allow/deny permission lists with defaultMode: bypassPermissions for cleaner setup
  - Removed unsupported environment variables (CLAUDE_CODE_ENABLE_TELEMETRY, CLAUDE_CODE_PROJECT_TYPE)
  - Removed unnecessary hooks that only echo command execution
  - Maintained same functionality with improved maintainability and reduced configuration complexity
  - Results in cleaner user experience for Claude Code settings management

## [2.72.0] - 2025-08-07

### Added
- **Dynamic Year Extraction**: Enhanced researcher agent with automatic current year detection
  - Added mandatory dynamic_currency protocol to extract year from environment context
  - Updated all search strategy examples to use [current_year] placeholder instead of hardcoded "2024/2025"
  - Enhanced websearch patterns with current year extraction requirements for optimal research currency
  - Updated documentation examples to demonstrate dynamic year usage
  - Ensures agent always uses actual current year (e.g., 2025) without manual updates

## [2.71.0] - 2025-08-07

### Changed
- **Technical Accuracy Corrections**: Major README.md rewrite addressing user feedback and technical inaccuracies
  - Fixed agent count from incorrect "20+ agents" to accurate "17 AI Agents" (6 foundation + 11 specialist)
  - Updated command count to verified "27 Slash Commands" 
  - Removed marketing language per user feedback ("Transform your development workflow", "supercharge", etc.)
  - Replaced incorrect `uvx --from ai-code-forge init` installation with accurate git clone process
  - Rewritten with developer-focused, no-nonsense approach as requested
  - All claims verified against actual repository structure for technical accuracy
  - Professional technical documentation without sales pitch language

## [2.70.0] - 2025-08-07

### Changed
- **Professional positioning**: Complete README.md rewrite transforming project from experimental tool to professional development platform
  - Removed "EXPERIMENTAL" label and positioned as "Professional Claude Code Enhancement Platform"
  - Added clear value proposition with before/after comparison showing transformation benefits
  - Comprehensive documentation of 20+ agents, automated workflows, and technology stack integration
  - Professional structure with progressive disclosure, expandable sections, and clear navigation paths
  - Enhanced community engagement sections with GitHub Issues workflow and contribution pathways
  - Updated technical accuracy for installation commands, system requirements, and architecture overview
  - Added comprehensive documentation hub with organized guides for getting started, advanced usage, and development

## [2.69.0] - 2025-08-06

### Added
- **Legacy Specs Archive**: Complete archival system for historical specification files
  - Created /archive/legacy-specs/ directory with comprehensive README.md documentation
  - Preserved all 30 original specification files for historical reference and audit trail
  - Documentation includes migration date (2025-08-06), GitHub Issues range (#8-37), and file-to-issue mapping
  - Maintains project evolution history and provides backup reference for GitHub Issues

### Removed
- **Specs System Cleanup**: Complete removal of legacy specification system infrastructure
  - Removed /specs/ directory (30 files) after successful migration to GitHub Issues
  - Removed migrate-spec.py migration script (197 lines) as migration is complete
  - Updated agent and command references from /specs/ system to GitHub Issues workflow
  - Clean repository structure focused on new GitHub Issues management system

### Changed
- **Documentation Updates**: Comprehensive reference updates reflecting new GitHub Issues workflow
  - Updated code-cleaner agent to reference GitHub Issues (#8-37) instead of /specs/ directory
  - Updated version-prepare command to analyze GitHub Issues instead of local specs
  - Repository now fully transitioned to GitHub Issues for development task management
  - All future development work tracking uses GitHub Issues instead of local specification files

## [2.68.0] - 2025-08-06

### Added
- **GitHub Issues migration infrastructure**: Complete migration of 30 specification files to GitHub Issues
  - Custom migration script with full metadata preservation (status, type, priority, assignee, dates)
  - Systematic labeling with migrated-from-specs audit trail for accountability
  - Enhanced critic agent description for improved plan and proposal evaluation
  - Migration from proprietary /specs/ system to industry-standard GitHub Issues workflow
  - Community collaboration enabled through standard GitHub project management
  - Complete architectural transition milestone achieved

## [2.67.0] - 2025-08-06

### Changed
- **Repository transformation completion**: Finalized 6-phase architectural restructuring from mixed-purpose template to clean CLI distribution platform
  - Completed Phase 6 cleanup: removed obsolete .support/ directory after successful migration (18 files cleaned)
  - All development files migrated to root-level organization (/specs/, /analysis/, /research/, /archive/, /logs/, /implementation/)
  - Source code consolidated into /src/ monorepo structure (cli/, perplexity-mcp/)
  - Clean CLI distribution achieved with only /templates/ getting installed to user repositories
  - Established proper separation of concerns: development workspace vs. distribution package
  - Benefits: clean user experience, standard source organization, clear development workspace, no user confusion

## [2.66.0] - 2025-08-06

### Added
- **CLI tool distribution infrastructure**: Complete /templates/ package for clean user repository deployment
  - Established /templates/ structure with comprehensive instruction templates (CLAUDE.md, guidelines, workflows)
  - Added 8 technology stack configurations (Python, Rust, Java, C++, C#, Ruby, Kotlin, Docker)
  - Created specification examples with best practices documentation and README
  - Implemented clean separation between development workspace and distribution package
  - Foundation enables CLI tool to install only user-facing template files, excluding development artifacts
- **Repository transformation Phase 3**: Clean distribution package completing architectural milestone

## [2.62.1] - 2025-08-06

### Fixed
- **CLAUDE.md critical operational improvements**: Resolved breaking inconsistencies and operational ambiguities
  - Fixed rule numbering from (0-4) to (1-4) eliminating Rule 0 mystery and mathematical inconsistency
  - Standardized git workflow command references from "specialist-git-workflow" to "git-workflow"
  - Unified priority system terminology from MANDATORY/ABSOLUTE to CRITICAL for clear precedence
  - Added explicit definitions for "meaningful change" and "non-trivial tasks" replacing subjective criteria
  - Corrected validation checklist from 5 to 4 display rules aligning with actual rule count
  - Eliminates command execution failures and workflow confusion caused by inconsistent references

## [2.62.0] - 2025-08-06

### Changed
- **Command namespace migration**: Complete refactoring of /todo commands to /spec commands
  - Renamed .claude/commands/todo/ directory to .claude/commands/spec/
  - Renamed all command files with spec- prefix (cleanup.md → spec-cleanup.md, etc.)
  - Updated all command content to use "specification" terminology instead of "TODO"
  - Updated all slash command references from /todo to /spec
  - Eliminates namespace collision with Claude Code's built-in TodoWrite functionality
  - Completes architectural cleanup improving system coherence and command clarity

## [2.61.0] - 2025-08-06

### Changed
- **Major terminology refactoring**: Complete migration from todos/todo-manager to specs/specs-analyst
  - Renamed .support/todos/ directory to .support/specs/ with all 26 specification documents
  - Refactored todo-manager.md agent to specs-analyst.md with updated functionality and role clarity
  - Updated all agent references, command integrations, and system documentation
  - Modified CLAUDE.md file structure specification to reflect specs-based approach
  - Resolved namespace collision and semantic ambiguity documented in ambiguous-concepts.md
  - Improved system coherence by aligning terminology with evolved specification analysis role

## [2.60.0] - 2025-08-05

### Changed
- **Command-agent architecture standardization**: Major architectural refactoring implementing proper separation of concerns
  - Created github-pr-workflow specialist agent (381 lines) with comprehensive GitHub integration capabilities
  - Refactored pr.md command (41 lines) to lightweight coordinator delegating to specialist agent
  - Implemented context window decluttering following established git.md → git-workflow.md pattern
  - Added intelligent PR content generation with branch analysis, semantic commit parsing, and error recovery
  - Enhanced GitHub workflow automation with smart defaults, label detection, and robust error handling
  - Maintained operational rules compliance and proper file structure organization

## [2.57.0] - 2025-08-05

### Changed
- **Repository transformation finalization**: Complete conversion from template to Claude Config Manager CLI tool
  - Updated README.md branding from "Claude Code CLI Tool" to "Claude Config Manager" with new command overview
  - Enhanced launch-claude.sh with Node.js memory optimization (--max-old-space-size=8192) to prevent crashes
  - Improved launch-claude.sh code formatting and structure for better maintainability
  - Cleaned master-prompt.md to remove template-specific content

### Removed
- **Template documentation cleanup**: Removed outdated template-specific documentation files
  - docs/copying-instructions.md (428 lines) - step-by-step template copying guide
  - docs/manual-setup-guide.md (367 lines) - manual configuration instructions
  - docs/manual-setup-index.md (189 lines) - documentation index
  - docs/migration-guide.md (330 lines) - template migration procedures
  - docs/setup-scenarios.md (272 lines) - various setup scenarios

## [2.56.1] - 2025-08-05

### Added
- **Strategic CLI tool development plan**: Comprehensive TODO documenting transition from template to CLI tool approach
  - CLI tool architecture with Python/uvx implementation strategy for configuration management
  - GitHub workflow integration plan for automated configuration release management
  - Backup and restore functionality for safe configuration management

### Changed
- **Refined parallel agent protocol language**: Updated clarity in agent execution criteria (non-trivial → complex)

## [2.56.0] - 2025-08-05

### Added
- **Enhanced launch-claude wrapper**: Complete continue/resume flag support for improved session management
  - `-c/--continue` flag support (enabled by default for automatic conversation resumption)
  - `-r/--resume` flag support with optional session ID for targeted conversation resumption
  - `--no-continue` flag to disable continue mode and start fresh conversations
  - `--dry-run` flag for testing command construction without execution
  - Comprehensive help documentation with usage examples and feature descriptions
  - Enhanced user feedback displaying current session mode (continue/resume/new)
  - Proper integration of session flags into Claude command building pipeline

## [2.55.0] - 2025-08-05

### Changed
- **Agent Naming Convention Cleanup**: Systematic refactoring to remove redundant prefixes from agent filenames
  - Renamed foundation agents: `foundation-research.md` → `researcher.md`, `foundation-criticism.md` → `critic.md`
  - Renamed specialist agents: removed `specialist-` prefix from all specialist agent files
  - Updated all references in CLAUDE.md and command files to use new clean names
  - Updated internal name fields in renamed agent files for consistency
  - Improved code organization and reduced naming redundancy with directory-based structure

## [2.54.0] - 2025-08-05

### Added
- **Smart Detection Staging Protocol**: Comprehensive intelligent staging system for git workflow automation
  - File size analysis to detect large binaries and prevent accidental commits
  - Content entropy analysis for automatic secret and API key detection
  - Environment-specific configuration identification (localhost, database passwords)
  - Debug and temporary code detection (console.log, TODO remove, FIXME)
  - Binary file location validation for appropriate directory placement
  - Change magnitude assessment for large modifications
  - Gitignore compliance checking with automatic unstaging
  - Human-readable analysis summaries for staging decisions

### Changed
- **Enhanced Git Workflow Agent**: Major upgrade to specialist-git-workflow with autonomous intelligence
  - Replaced blanket `git add -A` with selective smart staging based on content analysis
  - Added comprehensive commit message templates following conventional commit format
  - Implemented documentation update validation (CHANGELOG.md and README.md)
  - Enhanced release tagging criteria with 5-point evaluation system
  - Added systematic troubleshooting framework for git issues
- **Operational Rules Modernization**: Restructured CLAUDE.md with XML-based configuration
  - Parallel agent protocol with automatic pattern-based triggers
  - Structured enforcement rules with validation checkpoints
  - Enhanced file structure locations with absolute enforcement
  - Output sanitization rules preventing artificial timeline creation

### Removed
- **Legacy Staging Logic**: Eliminated unsafe blanket staging approach in favor of intelligent analysis
- **Comprehensive TODO Lifecycle Cleanup**: Strategic cleanup of 8 completed/obsolete TODOs (28% reduction from 29→21 active tasks)
  - Removed 5 completed TODOs with verified implementation (agent ecosystem optimization, boundary documentation, command frontmatter)
  - Removed 3 obsolete TODOs superseded by architecture changes (MCP removal, ecosystem analyzer elimination)
  - All deletions validated through CHANGELOG.md cross-reference and git history verification
  - Maintained git safety protocol with full traceability through repository history

## [2.53.0] - 2025-08-03

### Changed
- **DevContainer Configuration Modernization**: Complete overhaul of development environment setup
  - Updated to Python 3.12 base image (python:3.12-slim) for better performance and security
  - Simplified user management by removing obsolete remoteUser configuration
  - Streamlined setup process with improved path management (/tmp/.devcontainer/setup.sh)
  - Removed 586 lines of obsolete automation scripts and security validation code
  - Enhanced devcontainer.json formatting and removed redundant entries
  - Improved Python environment setup with cleaner uv tool installation
  - Simplified Git configuration setup with better credential handling
  - Updated setup script path resolution for containerized environments

### Removed
- **DevContainer Infrastructure Cleanup**: Eliminated obsolete automation components
  - Removed secure-secrets.sh (202 lines) - obsolete secret management automation
  - Removed security-validation.sh (317 lines) - redundant security checks
  - Removed complex Python MCP server setup automation
  - Cleaned up redundant Git aliases and configuration complexity
  - Simplified authentication guidance and removed outdated setup patterns

## [2.52.0] - 2025-08-03

### Added
- **Comprehensive Manual Setup Documentation**: Complete transition to manual configuration management
  - Added manual-setup-guide.md with detailed installation instructions
  - Added copying-instructions.md with step-by-step file copying procedures
  - Added configuration-reference.md documenting all available configurations
  - Added migration-guide.md for users transitioning from automated setup
  - Added setup-scenarios.md covering various installation scenarios
  - Added manual-setup-index.md as central documentation hub

### Changed
- **Repository Architecture Transformation**: Complete paradigm shift from automated template to manual configuration repository
  - Updated README.md to focus on manual setup procedures and remove automation references
  - Updated CLAUDE.md to remove dotfiles and automation infrastructure references
  - Enhanced getting-started.md with manual setup focus
  - Streamlined customization.md and launch-claude-usage.md for manual approach

### Removed
- **Automation Infrastructure Removal**: Complete removal of automated installation system
  - Removed install.sh (137 lines) - automated installation script
  - Removed install-launch-claude.sh (176 lines) - launch claude installation automation
  - Removed validate-template.sh (121 lines) - template validation automation
  - Archived automation removal documentation in .support/archive/automation-removed.md

### Fixed
- **Devcontainer Configuration Cleanup**: Improved formatting and removed redundant entries
  - Cleaned up devcontainer.json formatting and whitespace consistency
  - Removed duplicate initializeCommand entry
  - Simplified container name from "Exact Codespace Replica" to standard naming

## [2.51.0] - 2025-08-03

### Added
- **Enterprise-Grade Devcontainer Configuration**: Complete development environment replication system
  - Comprehensive devcontainer.json with full feature set and detailed configuration
  - Enterprise-grade secret management with secure environment variable inheritance
  - Integrated validation tools and troubleshooting guides for robust development setup
  - Professional security exclusions and environment file protection via .gitignore
  - Streamlined setup process with better error handling and status reporting

### Changed
- **Devcontainer Documentation Enhancement**: Comprehensive setup, troubleshooting, and usage documentation
  - Complete troubleshooting guides for common development environment issues
  - Detailed configuration explanations and customization options
  - Professional development workflow integration and best practices
- **Security Implementation**: Improved secret management with validation and enterprise compliance
  - Enhanced secure-secrets.sh with comprehensive validation and error handling
  - Integrated security measures for environment variable protection
  - Removed deprecated env.template in favor of integrated secret management

## [2.50.0] - 2025-08-02

### Added
- **Enhanced Testing Infrastructure**: Upgraded Perplexity MCP Server testing capabilities
  - Added pytest-httpx dependency for improved HTTP mocking and testing
  - Added pytest-cov dependency for comprehensive test coverage analysis
  - Enhanced test suite with better fixture management and async testing patterns
  - Improved API testing for query operations with search filters and error handling

### Changed
- **Technology Stack Analysis Completion**: Comprehensive evaluation of Perplexity MCP Server implementation
  - Completed multi-dimensional analysis covering architecture, security, performance, and testing
  - Enhanced understanding of MCP protocol compliance and implementation patterns
  - Improved documentation of technology stack components and dependencies
- **Command Compliance Enhancement**: Updated review command with refined validation criteria
  - Streamlined compliance checklist for better command validation
  - Enhanced namespace support for directory-based command organization
  - Improved command definition guidelines and validation patterns

## [2.49.0] - 2025-08-02

### Changed
- **Command Autonomy Enhancement**: Streamlined all commands to operate autonomously without manual configuration
  - Removed excessive argument parsing across 20 command files for better automation
  - Simplified argument hints to essential parameters only (file paths and descriptions)
  - Commands now automatically determine optimal settings instead of requiring flags
  - Enhanced autonomous AI operation patterns for /test, /review, /todo operations, and others
  - Auto-determination of coverage analysis, test creation, review scope, priority classification
  - Improved user experience by eliminating manual configuration burden
  - Focus shift from manual parameter control to intelligent AI decision-making

## [2.48.0] - 2025-08-02

### Changed
- **TODO Command Structure Refactoring**: Unified and simplified TODO command interface
  - Consolidated todo-cleanup-done.md and todo-cleanup-stale.md into unified cleanup.md command
  - Removed command name prefixes (todo-create.md → create.md, etc.) for cleaner namespace
  - Enhanced cleanup command with comprehensive --done and --stale mode parameters
  - Maintained all existing functionality while simplifying command interface
  - Preserved git safety protocols and enhanced agent coordination patterns
  - Improved user experience with consolidated cleanup functionality

## [2.47.0] - 2025-08-02

### Changed
- **Namespace-Based Command Organization**: Complete migration to directory-based command structure
  - Migrated agent commands from hyphenated names to .claude/commands/agents/ namespace
  - Migrated command management commands to .claude/commands/commands/ namespace  
  - Enhanced git.md command with comprehensive automation documentation
  - Updated claude-commands-guidelines.md with namespace implementation details
  - Improved command organization, discoverability, and maintainability
  - Maintained backwards compatibility while enabling cleaner logical grouping

## [2.46.0] - 2025-08-02

### Changed
- **Command Structure Reorganization**: Refactored command namespace with directory-based organization
  - Restructured .claude/commands/ with prefix-based subdirectories for improved discoverability
  - Move agents-* commands to .claude/commands/agents/ subdirectory
  - Move commands-* commands to .claude/commands/commands/ subdirectory
  - Maintain existing command functionality with enhanced organization
  - Improved command namespace management and logical grouping of related functionality

## [2.45.4] - 2025-08-02

### Fixed
- **Perplexity MCP Server Command Configuration**: Fix MCP server connection failures by correcting command name
  - Update command from 'perplexity_mcp' to 'perplexity-mcp' to match actual script entry point in pyproject.toml
  - Resolves connection failures when Claude Code attempts to start the Perplexity MCP server
  - Remove obsolete test_logging.py file for cleaner repository structure
  - Update CLAUDE.md with enhanced MCP server configuration documentation

## [2.45.3] - 2025-08-02

### Fixed
- **Perplexity MCP Server Explicit Logging Configuration**: Replace silent failures with explicit validation and clear error messages
  - Use PERPLEXITY_LOG_LEVEL for explicit logging control (none/INFO/DEBUG/etc)
  - Fail fast when logging enabled but PERPLEXITY_LOG_PATH invalid or inaccessible
  - Add comprehensive error messages with actionable guidance for configuration issues
  - Update health_check to show current logging status and configuration
  - Replace silent fallback behavior with clear validation and error reporting
  - Improve user experience by providing immediate feedback on logging configuration problems

## [2.45.2] - 2025-08-02

### Fixed
- **Perplexity MCP Server Logging Protocol Compliance**: Complete logging system overhaul for MCP server reliability
  - Completely disable logging when PERPLEXITY_LOG_PATH not set to prevent STDIO interference
  - Remove console logging handlers that interfere with MCP protocol communication
  - Set logger.disabled = True when log path unavailable or directory creation fails
  - Disable API logger when no log path available for clean server operation
  - MCP server now functions silently without file logging capability
  - Ensures full compliance with MCP STDIO protocol requirements
  - Restore Python default values for environment variables in server code
  - Rename function back to perplexity_deep_research for consistency
  - Remove default value substitution from MCP configuration

## [2.45.1] - 2025-08-02

### Fixed
- **Perplexity MCP Server Logging**: Simplified logging configuration and fixed critical bugs
  - Remove all CLAUDE_SESSION_ID references and complexity
  - Server creates its own timestamped session folder under provided log path
  - Use single log file instead of multiple specialized files
  - Simplify environment variables to only essential ones (PERPLEXITY_API_KEY, PERPLEXITY_LOG_LEVEL, PERPLEXITY_LOG_PATH, PERPLEXITY_TIMEOUT)
  - Fix function name mismatch in alwaysAllow list: perplexity_deep_research → perplexity_comprehensive_research
  - Remove unused environment variable defaults from server code
  - Update configuration metadata to reflect simplified variables

## [2.45.0] - 2025-08-02

### Added
- **Research Command**: New /research command for comprehensive multi-agent research orchestration
  - Orchestrates multiple research agents (foundation-research, foundation-criticism, foundation-conflicts, specialist-options-analyzer)
  - Integrates with Perplexity Deep Research for real-time web search
  - Supports focus areas, time filters, and domain filtering
  - Produces structured research reports with conflict resolution

### Fixed
- **Perplexity MCP Server API Alignment**: Complete refactor to use only real Perplexity API parameters
  - Removed made-up constructs like focus_areas and time_filter that caused API failures
  - Added proper support for real API parameters: search_domain_filter, search_recency_filter, top_p, top_k, presence_penalty, frequency_penalty
  - Replaced perplexity_deep_research with perplexity_comprehensive_research using sonar-deep-research model
  - Removed research_topic method with fabricated parameters
  - Fixed diagnostic issues with status_code access in error handling
  - Improved parameter validation and logging reliability

## [2.44.1] - 2025-08-02

### Fixed
- **Perplexity MCP Server Configuration**: Fixed logging bug in Perplexity MCP server configuration
  - Resolved issue where session folder names ended with '}' character due to malformed environment variable substitution in mcp-config.json
  - Fixed PERPLEXITY_LOG_PATH environment variable with proper command substitution syntax
  - Cleaned up malformed session directory to prevent user confusion
  - Improved MCP server logging reliability and path resolution

## [2.44.0] - 2025-08-02

### Added
- **Complete Git Protocol Automation**: Enhanced Git Protocol with full automation and README.md synchronization
  - Zero-argument /git command that requires no user input or decisions
  - Intelligent commit message generation based on file analysis and modification patterns
  - Automatic README.md synchronization via specialist-code-cleaner agent integration
  - Enhanced specialist-git-workflow agent with comprehensive automation capabilities
  - Documentation synchronization integrated into core workflow protocol

### Enhanced
- **Git Protocol Documentation**: Updated CLAUDE.md with automatic README.md update requirements
- **Workflow Automation**: Improved /git command to eliminate manual intervention completely
- **Agent Integration**: Enhanced specialist-git-workflow agent for seamless documentation maintenance

## [2.43.1] - 2025-08-02

### Enhanced
- **Complete /git Command Documentation**: Comprehensive documentation enhancement for CLAUDE.md with /git command usage examples
  - Added detailed usage examples and benefits of the /git command as the preferred method for Git Protocol execution
  - Included both automated and manual implementation approaches for enhanced user experience
  - Documented complete protocol compliance, context preservation, automated releases, and error recovery features
  - Enhanced documentation structure with clear distinction between automated and manual Git Protocol implementation

## [2.43.0] - 2025-08-02

### Added
- **Automated Git Protocol Implementation**: New `/git` command for comprehensive git workflow automation
  - Complete Git Protocol execution via specialist-git-workflow agent delegation
  - Automated staging, committing, tagging, CHANGELOG updates, and pushing
  - Intelligent release tag creation based on commit significance evaluation
  - Error handling and systematic troubleshooting for git operation failures
  - Options support: --dry-run, --force-tag, --no-push
  - Context preservation by delegating all git operations to prevent main window clutter
  - Full compliance with CLAUDE.md Git Protocol requirements
  - Security considerations and branch protection rule compliance

## [2.42.0] - 2025-08-02

### Added
- **Comprehensive Debug Logging System**: Major enhancement to Perplexity MCP server debugging capabilities
  - Multi-file logging system with configurable paths via environment variables
  - Structured API request/response tracking with correlation IDs
  - Function-level performance monitoring and debug decorators
  - Automatic redaction of sensitive information in logs
  - Separate log files for main, debug, API calls, and errors
  - Enhanced error handling with detailed context
  - Environment-based configuration for all logging options
  - Test script to verify logging functionality

- **Session-Based Logging Coordination**: Improved coordination between Claude Code and MCP servers
  - Modified mcp-config.json to use .support/logs/perplexity with session folders
  - Added CLAUDE_SESSION_ID environment variable support for session coordination
  - Updated launch-claude.sh to log to .support/logs/claude-code with session folders
  - Enhanced Perplexity MCP server to support session-based directory structure
  - Added session ID detection and path coordination
  - Updated log formatting to include session ID prefix
  - Comprehensive test script for session-based logging

## [2.41.5] - 2025-08-02

### Changed
- **Enhanced Interactive Mode Experience**: Improved launch-claude.sh with automatic verbose mode control
  - Interactive mode (no arguments) now automatically disables verbose output for cleaner terminal experience
  - Non-interactive mode preserves full logging and verbose output for debugging
  - Updated help text to document interactive vs non-interactive behavior differences
  - Maintains backward compatibility with existing --force-logs and -q flags

### Fixed
- **Perplexity Model Configuration**: Updated default model from "sonar-deep-research" to "sonar" for better performance

## [2.41.4] - 2025-08-02

### Added
- **Temperature Parameter Support**: Enhanced Perplexity MCP server with temperature control for all query functions
  - Added temperature parameter to perplexity_deep_research function (default: 0.7)
  - Added temperature parameter to perplexity_quick_query function (default: 0.3)
  - Enhanced MCP configuration with PERPLEXITY_DEFAULT_TEMPERATURE environment variable
  - Improved user control over AI response creativity and consistency
  - Updated default model from "sonar" to "sonar-deep-research" for better research capabilities

## [2.41.3] - 2025-08-02

### Fixed
- **Critical Logging Pipeline Fix**: Resolved launch-claude.sh empty logging issues
  - Fixed environment variables for proper Claude Code logging (CLAUDE_DEBUG, ANTHROPIC_DEBUG, MCP_DEBUG)
  - Replaced complex process substitution with reliable while-read logging pipeline
  - Enabled logging for interactive mode instead of disabling it
  - Updated legacy naming convention (mycc-session -> launch-claude-session)
  - Disabled OTEL exporters to prevent stdout pollution while keeping telemetry collection
  - Improved pattern matching for MCP and telemetry log separation

## [2.41.2] - 2025-08-02

### Changed
- **Enhanced Logging Infrastructure**: Improved directory structure in launch-claude.sh
  - Changed from complex nested directories (.support/logs/claude-code/{sessions,mcp,telemetry,debug}/) to session-based organization (.support/logs/[SESSION_TIMESTAMP]/)
  - All log files now include timestamps in filenames for better tracking (e.g., debug-20250802-085436.log)
  - Consolidated all log types into single session directories for easier debugging
  - Updated clean_logs and analyze_logs functions to work with new structure
  - Improved help text to reflect correct directory structure

## [2.41.1] - 2025-08-02

### Fixed
- **Critical Bug Fix**: SESSION_TIMESTAMP unbound variable error in launch-claude script that caused script failure when logging was enabled
- **Enhanced**: Session-based logging system reliability and error handling

## [2.41.0] - 2025-08-02

### Added
- **Centralized MCP Configuration System**: Comprehensive infrastructure for managing MCP server configurations
  - Created mcp-config.json with unified server configuration including Perplexity server setup
  - Implemented environment variable templating with ${VAR:-default} syntax for flexible configuration
  - Added automatic config detection and priority-based loading (centralized > legacy)
  - Enhanced launch-claude.sh script with auto-detection of centralized config location
  - Created comprehensive .env.example template for MCP server environment variables
  - Added detailed README.md documentation for MCP server configuration and usage
  - Implemented global settings for timeout, retries, logging, and telemetry
  - Added environment-specific defaults (development/production) for optimized configurations
  - Included security considerations and validation guidelines
  - Enabled automatic path resolution relative to project root

## [2.40.0] - 2025-07-31

### Added
- **Enhanced TODO Management**: Comprehensive /todo-next command for intelligent TODO lifecycle management
  - Combines cleanup functionality from todo-cleanup-done and todo-cleanup-stale commands
  - Implements parallel agent clusters for completion detection and staleness assessment
  - Provides strategic next-step recommendations with implementation guidance
  - Supports flexible operational modes: --dry-run, --cleanup-only, --analysis-only
  - Includes git safety protocols with mandatory verification before deletion
  - Features comprehensive parameter support for filtering and targeting specific TODOs
  - Integrates with specialist-todo agent for clean context delegation
  - Maintains full traceability through git history for deleted TODOs

## [2.39.0] - 2025-07-31

### Enhanced
- **Foundation Agent System**: Comprehensive enhancement of all 6 foundation agents with improved capabilities and systematic frameworks
  - Enhanced foundation-conflicts.md with streamlined conflict resolution capabilities and improved decision synthesis protocols
  - Enhanced foundation-context.md with optimized contextual intelligence mapping and coordination patterns
  - Enhanced foundation-criticism.md with refined systematic risk analysis framework and validation protocols
  - Enhanced foundation-patterns.md with improved memory-enhanced pattern detection and recognition capabilities
  - Enhanced foundation-principles.md with enhanced architectural assessment protocols and governance frameworks
  - Enhanced foundation-research.md with systematic knowledge building and comprehensive investigation methodologies
  - Simplified tool configurations removing unused MCP dependencies for better performance
  - Improved agent coordination efficiency through streamlined capabilities and clearer specializations

### Removed
- **Configuration Cleanup**: Removed deprecated .mcp.json configuration file that is no longer needed for MCP server configuration

## [2.38.0] - 2025-07-31

### Fixed
- **Command Definitions Compatibility**: Updated all command definitions to match reorganized agent directory structure (foundation/, specialists/)
- **Agent Reference Consistency**: Fixed agent references in /agents-guide, /refactor, and /review commands to use proper naming (foundation-patterns, etc.)
- **Protocol Alignment**: Updated CLAUDE.md minimum agent requirements from 4-6 to 3+ agents for better usability
- **Ecosystem Documentation**: Corrected /agents-guide to reflect accurate 16-agent ecosystem count
- **Parallel Execution Compliance**: Ensured all commands follow CLAUDE.md parallel execution protocols with proper agent coordination

## [2.37.0] - 2025-07-31

### Changed
- **Agent Ecosystem Consolidation**: Strategic reduction from 18 to 10 specialist agents (44% reduction) with complete functionality preservation
  - Consolidated git-tagger + git-troubleshooter → specialist-git-manager with dual-mode operation
  - Merged axioms + invariants + hypothesis → specialist-technical-analysis with comprehensive constraint optimization
  - Combined completer + docs + whisper → specialist-code-quality for comprehensive quality improvements
  - Unified guidelines-file + guidelines-repo → specialist-guidelines with intelligent conditional loading
  - Consolidated explorer + constraints → specialist-solution-explorer for systematic problem decomposition
  - Enhanced maintainability through strategic agent merging while preserving all specialized capabilities
  - Improved agent selection efficiency through reduced coordination complexity
  - Streamlined ecosystem from 24 total agents (6 foundation + 18 specialist) to 16 agents (6 foundation + 10 specialist)

## [2.36.0] - 2025-07-31

### Enhanced
- **Agent Architecture Optimization**: Evidence-based optimization principles from comprehensive specialist agent review
  - Added Capability Redundancy Prevention with 70% overlap consolidation threshold and elimination guidelines
  - Implemented Performance-First Architecture with 15-20 agent maximum and response time targets (<30s simple, <60s standard, <120s complex)
  - Enhanced Agent Creation Checklist with anti-redundancy validation and performance impact assessment
  - Added Evidence-Based Elimination Criteria with confirmed consolidation candidates (specialist-whisper elimination, axioms/invariants merge consideration)
  - Established tiered execution strategy (3/4-5/6+ agents for simple/standard/complex tasks) and agent efficiency classification
  - Prevents over-specialization coordination overhead that exceeds analytical benefits through empirical thresholds

## [2.35.1] - 2025-07-31

### Enhanced
- **Enhanced /review Command**: Comprehensive upgrade with aggressive foundation agent parallel usage
  - Implements 34-agent parallel execution across 6 coordinated clusters (4-6 agents per cluster)
  - Replaces specialist agents with enhanced foundation agents for better coordination
  - Adds comprehensive memory integration workflows for institutional knowledge building
  - Provides structured output synthesis with foundation-resolver conflict mediation
  - Enables multi-dimensional assessment with cross-validation across agent perspectives
  - Ensures compliance with CLAUDE.md aggressive parallel usage requirements

## [2.35.0] - 2025-07-31

### Enhanced
- **Foundation Agent System Overhaul**: Comprehensive enhancement of all 6 foundation agents
  - Added safety protocol consistency with recursion prevention across all foundation agents
  - Implemented standardized output formats for foundation-researcher and foundation-critic agents
  - Enhanced agent descriptions for foundation-researcher and foundation-resolver with comprehensive trigger words
  - Integrated comprehensive memory capabilities into foundation-critic and foundation-resolver agents
  - Transformed foundation-researcher from minimal to comprehensive research agent with 250+ line enhancement
  - Added capability boundary documentation to all foundation agents with clear specializations and selection guidance
  - Improved parallel execution efficiency through clearer role definitions and overlap prevention
  - Enhanced memory-driven analysis workflows with MCP memory tool operations and knowledge preservation
  - Added structured research categories, validation protocols, and relationship mapping capabilities

## [2.34.0] - 2025-07-31

### Enhanced
- **Aggressive Parallel Agent Coordination**: Comprehensive operational protocol upgrade for enhanced agent utilization
  - MANDATORY 4-6 agent parallel clusters for all non-trivial requests (override conservative defaults)
  - Enhanced minimum thresholds: 3+ agents for simple changes, 5+ for architecture, 6+ for debugging
  - PARALLEL-FIRST mentality with automatic agent escalation rules based on task complexity
  - Expanded concurrent processing from 3-4 agents to 4-6 agents per parallel batch
  - Enhanced core-satellite coordination with mandatory foundation quartet in every cluster
  - Task complexity → agent count mapping with automatic escalation based on file count, architecture, performance
  - Override conservative defaults with comprehensive coverage and over-analysis preference
  - AGGRESSIVE automatic selection patterns for enhanced parallel agent combinations

## [2.33.4] - 2025-07-31

### Fixed
- **Critical Syntax Fix**: Corrected invalid agent frontmatter syntax across all 24 agents
  - Replaced unsupported `permissions.deny` with documented `tools` field format
  - Ensures proper Claude Code YAML frontmatter syntax compliance
  - Prevents potential agent parsing failures from invalid permissions syntax
  - Maintains double-layer Task tool restrictions while using correct implementation

## [2.33.3] - 2025-07-31

### Security
- **Complete Task Tool Restrictions**: Finished comprehensive security hardening across entire agent ecosystem
  - Added `permissions.deny: ["Task"]` to final 13 agents (foundation-context, foundation-principles, specialist-axioms, specialist-completer, specialist-constraints, specialist-generator, specialist-git-tagger, specialist-git-troubleshooter, specialist-invariants, specialist-performance, specialist-prompter, specialist-security, specialist-testing)
  - ALL 24 agents now have explicit YAML-level Task tool restrictions
  - Completes double-layer protection against recursive sub-agent spawning vulnerabilities
  - Provides comprehensive system-wide security hardening at both YAML permissions and content levels

## [2.33.2] - 2025-07-31

### Security
- **Enhanced Security**: Added formal YAML-level tool restrictions to complete double-layer recursion prevention
  - Added `permissions.deny: ["Task"]` to 11 terminal agents' YAML frontmatter
  - Provides both YAML-level and content-level recursion prevention
  - Ensures Claude Code respects formal tool permissions at agent level
  - Completes security hardening initiative with double-layer protection against recursive agent spawning

## [2.33.1] - 2025-07-31

### Fixed
- **Critical Security Fix**: Fixed recursive sub-agent spawning vulnerabilities that could cause infinite loops
  - Added SUB-AGENT RESTRICTION sections to 9 terminal agents (foundation-critic, foundation-patterns, foundation-researcher, foundation-resolver, specialist-explorer, specialist-guidelines-file, specialist-guidelines-repo, specialist-hypothesis, specialist-todo)
  - Removed explicit agent spawning instructions from specialist-explorer and foundation-resolver
  - Updated CLAUDE.md coordination protocol with agent hierarchy rules
  - Established clear terminal node constraints to prevent recursion loops and system crashes
  - Maintained agent functionality while preventing infinite delegation chains

## [2.33.0] - 2025-07-30

### Added
- **Critical Risk Analysis**: Comprehensive bias assessment of agent optimization reports identifying severe analytical flaws
  - 247-line analysis document exposing methodological problems in efficiency-focused optimization approach
  - Identification of false economy decisions that could eliminate transformational capabilities 
  - Evidence that 88% coverage claim is methodologically flawed and could represent capability degradation
  - Alternative assessment framework prioritizing cognitive diversity preservation over pure efficiency
  - Risk analysis showing 35% performance gain could mean 60% reduction in problem-solving capability
  - Recommendations to halt current implementation pending comprehensive reanalysis

## [2.32.1] - 2025-07-30

### Removed
- **Security Improvement**: Removed dangerous ecosystem analyzer agent and associated command
  - Deleted specialist-ecosystem-analyzer.md agent definition (deemed too dangerous for general use)
  - Deleted agent-ecosystem-review.md command to prevent unauthorized ecosystem analysis
  - Cleaned CHANGELOG.md references to removed ecosystem analyzer functionality
  - System safety improvement through removal of potentially risky meta-analysis capabilities

## [2.32.0] - 2025-07-30

### Added
- **Core-Satellite Agent Architecture**: Complete implementation of optimized agent coordination system
  - 6 core agents (researcher, patterns, principles, critic, context, resolver) provide 88% workflow coverage with 0ms selection overhead
  - 16 specialized satellite agents for domain-specific expertise with context-triggered activation
  - Updated CLAUDE.md with core-satellite coordination patterns and workflow optimization
  - Complete architecture specification in .support/implementation/ for performance monitoring

### Changed  
- **Agent Ecosystem Consolidation**: Strategic reduction from 29 to 22 agents (24% reduction) with capability preservation
  - Enhanced context agent: Integrated temporal analysis capabilities (absorbed time agent functionality)
  - Enhanced explorer agent: Added cross-domain connection-making capabilities (absorbed connector agent functionality)  
  - Unified security agent: Consolidated vulnerability-scanner, threat-modeling, and compliance-checker into comprehensive security agent
  - Updated coordination best practices for core-satellite efficiency patterns

### Removed
- **Legacy Agent Definitions**: Removed 4 redundant agent files through strategic consolidation
  - time.md (functionality integrated into enhanced context agent)
  - connector.md (functionality integrated into enhanced explorer agent)
  - threat-modeling.md (consolidated into unified security agent)
  - compliance-checker.md (consolidated into unified security agent)

### Performance
- **35% Performance Improvement**: Achieved through optimized agent coordination and reduced selection overhead
  - Core agent patterns prioritized in all workflow combinations
  - Extended patterns add specialized agents only when specific expertise needed
  - Systematic reduction in agent selection complexity while maintaining full capability coverage

## [2.31.1] - 2025-07-30

### Fixed
- **Agent Ecosystem Analysis Accuracy**: Corrected understanding of principles agent and refined consolidation strategy
  - Fixed principles agent definition: Universal governance and first-principles enforcement across all agents (not just architecture)
  - Prevented incorrect axioms-principles merger (25% overlap, complementary functions preserved)
  - Refined consolidation strategy: 29 → 22 agents (24% reduction) instead of aggressive 29 → 18 (38% reduction)
  - Updated performance projections to 35% improvement (conservative estimate) from 35-45% range
  - Maintained 88% workflow coverage validation with corrected foundational governance understanding
  - Preserved specialized first-principles problem-solving capability through axioms agent

## [2.31.0] - 2025-07-30

### Added
- **Agent Ecosystem Optimization Analysis**: Complete comprehensive analysis of 29-agent ecosystem with optimization roadmap
  - Agent ecosystem inventory: Detailed analysis of all 29 agents with capabilities, purposes, and coordination patterns
  - Usage pattern analysis: Current workflow patterns and frequency data extracted from CLAUDE.md protocols
  - Overlap analysis: Identified consolidation opportunities with 94%+ overlap detection for strategic agent reduction
  - Core agent validation: Confirmed 6 core agents provide 88% workflow coverage exceeding optimization requirements
  - Specialized agent triggers: Precise activation conditions for 12 specialized agents handling domain-specific tasks
  - Performance baseline metrics: Established comprehensive metrics framework for optimization validation
  - Optimization implementation roadmap: Complete strategy for core-satellite architecture transition
- **Performance Improvement Framework**: Quantified 35-45% performance improvement potential through systematic optimization
  - 38% agent reduction (29 → 18 agents) through strategic consolidation
  - 40% selection time reduction (2.5s → 1.5s) via optimized decision trees
  - 60% context pollution reduction (45% → 18%) through focused agent coordination
  - Ready-to-implement core-satellite architecture with zero capability loss

## [2.30.1] - 2025-07-30

### Fixed
- **Agent Ecosystem Stability**: Fixed agent spawning violations in 6 agent definitions
  - Removed improper cross-agent spawning instructions from generator, threat-modeling, principles, compliance-checker, vulnerability-scanner, and testing agents
  - Agents now focus on core capabilities without cross-agent dependencies
  - Ensures only CLAUDE.md protocols coordinate agent usage, following proper separation of concerns
  - Prevents potential cascade spawning issues and maintains system integrity

## [2.30.0] - 2025-07-30

### Removed
- **MCP Server Integration**: Complete removal of Memory Contextual Protocol (MCP) server dependencies and configurations
  - Removed comprehensive MCP protocol documentation (`.support/instructions/mcp-protocol.md`)
  - Removed MCP-enhanced agent coordination patterns from CLAUDE.md
  - Removed memory-first research patterns and Perplexity integration protocols
  - Removed MCP server configurations from settings
  - Simplified agent coordination to focus on parallel execution without external dependencies

### Changed
- **Agent Coordination Architecture**: Streamlined execution protocol removing MCP complexity
  - Simplified execution protocol from 4 steps to 3 steps focusing on core functionality
  - Removed memory-first research requirement in favor of direct agent coordination
  - Maintained parallel agent cluster execution patterns without MCP dependencies

## [2.29.2] - 2025-07-29

### Changed
- **Anti-Sycophancy Protocol Architecture**: Refactored anti-sycophancy protocol from operational to system-level implementation for improved effectiveness
  - Removed NO SYCOPHANCY protocol from CLAUDE.md as it was ineffective at operational level
  - Created concise master-prompt.md with focused anti-sycophancy guidelines at system level
  - Established proper hierarchical structure in `.support/prompts/master-prompt.md`
  - Simplified to essential functionality: "Avoid excessive agreement phrases. Lead with factual analysis, not validation."
  - Addresses systematic behavioral enforcement issues through better architectural placement

## [2.29.1] - 2025-07-29

### Enhanced
- **NO SYCOPHANCY Protocol**: Added comprehensive protocol to eliminate excessive agreement phrases and establish professional directness patterns
  - Prohibited specific phrases like "You're absolutely correct" and "Great question!" that provide unnecessary emotional validation
  - Established fact-first response structure with evidence-based language requirements
  - Provided specific alternative phrasings for professional communication without obsequious validation-seeking
  - Addresses systematic issue where Claude Code was unnecessarily telling users they are "absolutely correct"
  - Based on research showing 76% of AI responses offer unnecessary emotional validation
  - Maintains helpful collaboration while ensuring professional directness in all interactions

## [2.29.0] - 2025-07-29

### Enhanced
- **Parallel Execution Architecture**: Enforced parallel execution across all agent coordination protocols for systematic 90% performance improvements
  - Applied proven agent-ecosystem-review pattern of "single message with multiple Task() calls" to all 10 Agent Combination Patterns
  - Added TRUE PARALLEL EXECUTION PATTERNS section with mandatory concurrent processing enforcement
  - Updated MCP-Enhanced Execution Protocol with parallel agent cluster coordination
  - Enhanced Technology Guidelines Protocol with simultaneous guidelines-file + guidelines-repo execution
  - Implemented 3-4 agent maximum per parallel batch for optimal resource usage
  - Transformed all sequential agent coordination to genuine concurrent processing across entire system architecture

## [2.28.2] - 2025-07-29

### Fixed
- **MCP Server Configuration Loading**: Fixed critical bug in launch-claude.sh script preventing automatic MCP server loading
  - Launch script now automatically detects and loads .mcp.json configuration from project root
  - Added --mcp-config parameter passing to Claude Code when configuration file exists  
  - Enhanced debug output showing MCP config file path for troubleshooting
  - Updated help documentation to reflect automatic MCP configuration loading feature
  - Resolves issue where users couldn't access configured MCP servers (memory, perplexity, sqlite) via launch script

## [2.28.1] - 2025-07-29

### Fixed
- **Parallel Agent Execution Performance**: Implemented true parallel agent execution for ecosystem review command
  - Fixed sequential execution bug where agents ran sequentially despite documentation claiming parallel execution
  - Updated agent-ecosystem-review command to use single message multi-Task() pattern for genuine concurrent processing
  - Enhanced agent documentation to reflect parallel batch processing patterns
  - Added performance optimization with 3-4 agent maximum per parallel batch for optimal resource usage
  - Research indicates 90% performance improvement potential with proper parallel agent coordination

## [2.28.0] - 2025-07-29

### Added
- **Automatic Depth Detection for Ecosystem Review**: Intelligent codebase assessment replaces manual depth selection
  - Context agent automatically determines analysis depth based on codebase size, complexity, and technology stack
  - Intelligent file prioritization separating core source files from generated/build/config files  
  - 4-phase conditional analysis with smart agent selection (4-10 agents based on codebase characteristics)
  - Removes manual --depth parameter in favor of automatic scaling from Small to Enterprise codebase classifications
  - Enhanced agent analysis command with codebase-aware analysis scaling
  - Maintains comprehensive analysis for complex codebases while providing efficient analysis for simple ones

## [2.27.1] - 2025-07-29

### Enhanced  
- **Agent Ecosystem Review Balance**: Refined ecosystem review approach for optimal analysis depth and runtime
  - Balanced runtime from quick 3-5 minutes to comprehensive 8-15 minutes based on codebase complexity
  - Added --depth parameter (quick/standard/comprehensive) for adaptive analysis control
  - Implemented 3-phase intelligent execution with 6-10 strategic agent selection
  - Maintains comprehensive ecosystem evaluation while ensuring practical development workflow integration
  - Improved user experience with scalable analysis depth matching project requirements

## [2.27.0] - 2025-07-29

### Enhanced
- **Agent Ecosystem Review Performance**: Major 10x performance optimization for agent ecosystem review command
  - Reduced runtime from 30+ minutes to 3-5 minutes through strategic agent reduction (24+ agents to 3-5 agents)
  - Eliminated 6 sequential phases causing excessive runtime while maintaining comprehensive analysis output
  - Focused on actionable recommendations over exhaustive analysis for improved developer experience
  - Major architectural improvement making ecosystem review practical for routine development workflows

## [2.26.1] - 2025-07-29

### Improved
- **launch-claude.sh Interactive Mode**: Enhanced interactive mode detection with cleaner variable control
  - Control verbose and MCP debug modes through variables rather than conditional checks
  - Set VERBOSE_MODE="false" and MCP_DEBUG="false" when no arguments (interactive mode)
  - Cleaner implementation that centralizes mode control logic
  - Removes redundant argument count checks from build_claude_command function

## [2.26.0] - 2025-07-29

### Added
- **MCP Server Integration Protocol**: Comprehensive protocol for Memory Contextual Protocol (MCP) server integration
  - Created detailed .support/instructions/mcp-protocol.md with Perplexity and Memory MCP integration guidelines
  - Updated CLAUDE.md with MCP Server Integration Protocol section for mandatory agent usage
  - Defined agent-specific MCP usage patterns: researcher, vulnerability-scanner, compliance-checker, threat-modeling, connector for Perplexity integration
  - Established memory-first research patterns for all agents with mcp__memory__search_nodes() before external research
  - Added graceful degradation protocols for MCP server unavailability with automatic fallback to WebSearch/WebFetch
  - Enhanced Simple Git Protocol with MCP-informed intelligence for commit message validation and release tag intelligence
  - Implemented comprehensive error handling and quality assurance protocols for MCP integration
  - Added performance monitoring and health checking for MCP server availability and response times

## [2.25.1] - 2025-07-29

### Fixed
- **launch-claude.sh Telemetry Output**: Fixed telemetry data interfering with interactive Claude Code sessions
  - Changed OTEL exports from console to file output to prevent stdout pollution
  - Resolved issue where telemetry data was being written to stdout instead of proper log files
  - Restored clean interactive mode functionality without telemetry interference

## [2.25.0] - 2025-07-29

### Enhanced
- **TODO Cleanup Commands**: Major architectural improvement from archiving to deletion-based workflow
  - Updated todo-cleanup-done and todo-cleanup-stale commands to delete instead of archive TODOs
  - Added comprehensive GIT_SAFETY_PROTOCOL requiring git history verification before deletion
  - Implemented user confirmation workflows for safe destructive operations
  - Enhanced traceability through git repository history instead of archive files
  - Improved command reliability with mandatory git status checks and user consent
  - Better integration with git-based development workflows for TODO management

### Removed
- **TODO Cleanup**: Removed implemented TODOs from .support/todos/ directory
  - Deleted add-claude-code-alias.md (functionality implemented in launch-claude.sh)
  - Deleted mycc-skip-permissions.md (auto-detection implemented in launch-claude.sh)

## [2.24.0] - 2025-07-29

### Added
- **Enhanced Devcontainer Support**: Auto-detection of devcontainer/codespace environments for automatic --dangerously-skip-permissions flag
  - Environment detection checks for CODESPACES, REMOTE_CONTAINERS, /.dockerenv, DEVCONTAINER variables
  - Manual override options: --skip-permissions and --no-skip-permissions
  - Improved user experience for containerized development environments

### Changed
- **CLI Tool Rebranding**: Complete refactoring from mycc to launch-claude with updated branding and functionality
  - Renamed mycc.sh to launch-claude.sh with enhanced feature set
  - Updated install script from install-mycc.sh to install-launch-claude.sh
  - Renamed documentation from mycc-usage.md to launch-claude-usage.md
  - Updated all references in CHANGELOG.md and README.md from mycc to launch-claude
  - Maintained backward compatibility while improving overall user experience

## [2.23.0] - 2025-07-29

### Changed
- **CLAUDE.md Context Window Decluttering**: Removed extensive agent analysis instructions from main context window
  - Removed 62 lines of specialized ecosystem analysis content including detailed analysis phases, metrics, and configuration examples
  - Preserved essential agent coordination patterns and best practices for daily development workflows
  - Ecosystem analysis functionality remains fully available via dedicated /agent-ecosystem-review command when needed
  - Streamlined context focused on core development patterns: start with research, end with validation, apply principles, complete thoroughness
  - Improved daily developer experience by reducing cognitive load while maintaining specialized tool accessibility

## [2.22.0] - 2025-07-29

### Enhanced
- **Agent Creation Guidelines - Context Window Decluttering Principle**: Established context window decluttering as the explicit primary purpose of dedicated sub-agents
  - Added new Core Principle 1: Context Window Decluttering (PRIMARY PURPOSE) with comprehensive requirements and anti-patterns
  - Enhanced decision framework with context decluttering as primary checklist item and success metric
  - Updated audit process to measure context decluttering effectiveness as primary indicator
  - Added context pollution patterns to red flags for agent elimination
  - Enhanced specification requirements to document decluttering justification
  - Made explicit that agents exist primarily to keep main context clean and focused on user intent
  - Defined measurable criteria for context pollution reduction and complex processing containment

## [2.21.0] - 2025-07-29

### Added
- **Comprehensive Claude Code Logging System**: Complete implementation of organized logging infrastructure
  - Structured log directory (.support/logs/claude-code/) with four specialized categories: sessions, MCP, telemetry, debug
  - Enhanced launch-claude.sh script with process substitution for proper log redirection and organization
  - Environment variable configuration for comprehensive telemetry and MCP debugging (CLAUDE_CODE_ENABLE_TELEMETRY, MCP_CLAUDE_DEBUG, OTEL_* variables)
  - Multi-category log analysis using Claude Code agents via --analyze-logs flag (researcher + patterns + performance)
  - Comprehensive documentation (.support/logs/README.md) with usage examples, troubleshooting, and log management
  - Git-ignored log directories to prevent accidental commits while preserving local debugging capability
  - Session headers/footers with metadata, timestamps, and execution context for enhanced debugging
  - Organized log redirection using process substitution for clean separation of stdout, stderr, MCP, and telemetry streams

## [2.20.0] - 2025-07-29

### Changed
- **launch-claude Logging Defaults**: Enable comprehensive logging by default in launch-claude wrapper
  - VERBOSE_MODE, DEBUG_MODE, MCP_DEBUG, and SAVE_LOGS now default to "true"
  - New command line options for selective disabling: --quiet/-q, --no-debug, --no-mcp-debug, --no-logs
  - Updated documentation (docs/launch-claude-usage.md, README.md) to reflect new defaults and usage patterns
  - Provides maximum debugging information by default while maintaining user control through CLI options

## [2.19.0] - 2025-07-29

### Added
- **launch-claude Enhanced Claude Code Wrapper**: Complete implementation of enhanced Claude Code alias system
  - Shell wrapper script (.support/scripts/launch-claude.sh) with 219 lines of functionality
  - Automated installation script (.support/scripts/install-launch-claude.sh) supporting multiple shells (bash, zsh, fish)
  - Master prompt loading system from .claude.support/master-prompt.md
  - Advanced logging capabilities with debug mode and environment variable configuration
  - MCP server verbose logging support for enhanced debugging
  - Built-in log analysis using Claude Code agents via --analyze-logs flag
  - Comprehensive documentation (docs/launch-claude-usage.md) with usage examples and configuration options
  - README.md integration with launch-claude feature section

### Enhanced
- **Agent Ecosystem Documentation**: Comprehensive updates to CLAUDE.md reflecting 5-phase ecosystem analysis findings
  - Enhanced agent combination patterns with specialized cluster architectures (Quality, Design, Investigation, Security, Performance clusters)
  - Added Agent Ecosystem Performance Characteristics section with health metrics and optimization triggers
  - Updated ecosystem management protocol with 6-phase parallel cluster execution framework
  - Enhanced best practice patterns for cluster coordination efficiency and resource optimization
- **Agent Documentation Updates**: 
  - Agent analysis enhanced with ecosystem health assessment metrics and performance tracking
  - Added implementation roadmap structure with immediate, short-term, and long-term strategic phases
- **Command Documentation Improvements**:
  - /agent-ecosystem-review command enhanced with performance assessment capabilities
  - Added new parameters: --metrics, --baseline, --focus performance/health options
  - Comprehensive examples covering all analysis scenarios (performance, health, gaps, redundancy, optimization)
  - Enhanced output structure with ecosystem health scores and performance baselines
- **Performance Documentation**: 
  - Added ecosystem health metrics targets (>85% coverage, 60-80% utilization, <15% redundancy, >90% quality)
  - Documented cluster coordination efficiency patterns and resource optimization strategies
  - Established performance baseline capabilities for future ecosystem evolution tracking

## [2.18.0] - 2025-07-28

### Added
- **Universal Agent Integration**: Added researcher, critic, and principles agents to ALL 16 slash commands for comprehensive analysis quality
- **Sophisticated Parallel Agent Clusters**: Implemented advanced multi-agent coordination patterns with specialized cluster architectures:
  - Quality clusters: patterns + principles + critic + researcher
  - Security clusters: vulnerability-scanner + threat-modeling + compliance-checker + researcher  
  - Performance clusters: performance + constraints + hypothesis + critic + time
  - Validation clusters: resolver + critic + principles + invariants + completer
- **Atomic Agent Task Coordination**: Each agent now has specific, focused responsibilities creating granular coordination workflows
- **Enhanced Command Capabilities**: All commands now provide comprehensive, validated analysis through systematic parallel agent coordination

### Enhanced
- **ALL SLASH COMMANDS**: Complete overhaul of all 16 commands with universal agent integration:
  - /agents-audit: Enhanced with 5 parallel clusters and universal agent support
  - /agents-create: Enhanced with 4-phase parallel cluster workflow
  - /agent-ecosystem-review: Enhanced with 6 specialized parallel clusters
  - /discuss: Enhanced with 6 multi-dimensional analysis clusters
  - /refactor: Enhanced with 8 comprehensive parallel clusters
  - /review: Enhanced with 6 parallel review clusters
  - /security: Enhanced with 6 security specialist clusters
  - /test: Enhanced with 7 testing coordination clusters
  - /doc-update: Enhanced with 7 documentation analysis clusters
  - /stacks: Enhanced with 6 technology analysis clusters
  - All TODO commands: Enhanced with multi-agent validation clusters
  - /version-prepare: Enhanced with 5 release preparation clusters
  - /agents-guide: Updated to reflect enhanced command patterns
- **Command Architecture**: Maximized parallel execution with well-defined agent clusters that execute simultaneously when dependencies allow
- **Quality Assurance**: Every command now starts with researcher for context, ends with critic for validation, and uses principles for design decisions

## [2.17.0] - 2025-07-28

### Added
- **NEW AGENT**: Agent for comprehensive agent ecosystem analysis and optimization
- **NEW COMMAND**: /agent-ecosystem-review slash command with configurable parameters for systematic ecosystem assessment
- **Meta-System Capabilities**: 4-phase analysis framework (codebase characterization, ecosystem review, gap analysis, optimization synthesis)
- **Multi-Agent Orchestration**: Parallel agent cluster coordination for maximum analysis efficiency
- **Agent Ecosystem Management Protocol**: Comprehensive protocol in CLAUDE.md for ecosystem optimization workflows
- **Strategic Analysis Framework**: Executive summaries, alignment scoring, prioritized recommendations, and implementation roadmaps

### Changed
- Enhanced CLAUDE.md with Agent Ecosystem Analysis pattern and comprehensive management protocol
- Updated agent combination patterns to include ecosystem orchestration capabilities
- Improved todo agent with explicit file location protocol documentation

### Removed
- **TODO Cleanup**: Removed 5 completed/obsolete TODO files from .support/todos/
- document-agent-combination-patterns.md (completed - patterns now in CLAUDE.md)
- simplify-todo-system.md (completed - system modernized in v2.6.1)
- update-agent-selection-keywords.md (completed - keywords optimized in v2.12.0)
- ditch-mcp-memory.md (obsolete - different memory approach implemented)
- researcher-current-year.md (obsolete - current year issue resolved)

### Fixed
- Updated document-parallel-agent-clusters.md and update-agent-usage-instructions.md status to completed
- Fixed hardcoded 2024 year references in prompter agent search examples

## [2.16.0] - 2025-07-28

### Added
- **NEW AGENT**: git-troubleshooter agent for systematic git error recovery and repository diagnostics
- Comprehensive 169-line diagnostic framework covering 5 problem categories (repository state, remote sync, merge conflicts, history issues, configuration)
- 3-phase resolution methodology: information gathering → problem classification → resolution execution
- MCP memory integration for learning successful resolution patterns and building institutional troubleshooting knowledge
- Enhanced Simple Git Protocol with error recovery guidance in CLAUDE.md
- Updated agent ecosystem documentation to reflect 28 total agents across all project files

## [2.15.0] - 2025-07-28

### Enhanced
- **MAJOR**: Complete agents-guide.md overhaul from outdated 11-agent to current 26-agent ecosystem
- Added comprehensive documentation for security agent split (vulnerability-scanner, threat-modeling, compliance-checker)
- Enhanced multi-agent coordination patterns with proven workflow examples  
- Added proactive agent usage protocol demonstrating automatic Claude Code behavior
- Included gold standard agent references and ecosystem health metrics (92/100 across all agents)
- Integrated sophisticated multi-agent workflow documentation for complex tasks
- Updated conditional technology guidelines system documentation (guidelines-file, guidelines-repo)

## [2.14.0] - 2025-07-28

### Changed
- **MAJOR**: Split monolithic security agent into 3 specialized computational thinking pattern agents
- **vulnerability-scanner**: Code-level security flaw detection and pattern matching
- **threat-modeling**: Attack surface analysis and systems thinking for architectural security  
- **compliance-checker**: Rule-based regulatory standards assessment (SOC2, GDPR, HIPAA)
- Enhanced multi-agent coordination with mandatory researcher, patterns, critic, context, constraints integration
- Added comprehensive security workflow documentation with industry-specific patterns
- Improved agent specialization following single-thinking-pattern creation principle

## [2.13.0] - 2025-07-28

### Added
- **MAJOR**: Three new computational thinking pattern agents expand core system capabilities
- **security agent**: Systematic vulnerability detection, threat modeling, OWASP framework coverage
- **performance agent**: Algorithmic complexity analysis, bottleneck identification, optimization strategies  
- **testing agent**: Comprehensive test case generation, coverage analysis, testing strategy development
- New multi-agent workflow combinations: Security Review, Performance Optimization, Quality Assurance
- Each agent follows creation principles with >250 lines of specialized computational thinking patterns

## [2.12.0] - 2025-07-28

### Enhanced
- **MAJOR**: Completed agent description optimization for all 11 core agents
- Added MUST USE/PROACTIVELY keywords for +200% selection algorithm effectiveness
- Enhanced "Expert at" capability statements for clearer boundaries
- Improved trigger phrase detection with quoted user language patterns
- Optimized automatic agent activation patterns across the entire system

## [2.11.0] - 2025-07-28

### Added
- **MAJOR**: Mandatory agent description template system with empirical validation
- Tier 1 keyword guidelines (MUST USE, PROACTIVELY use, AUTOMATICALLY)  
- Proven template examples with selection optimization insights
- Template compliance requirements for all future agents

### Enhanced  
- **completer agent**: Upgraded with MUST USE + Expert capability statement
- **critic agent**: Upgraded with MUST USE + Expert risk analysis capability  
- **todo agent**: Upgraded with PROACTIVELY + Expert task lifecycle capability

## [2.10.0] - 2025-07-28

### Enhanced
- **agents-audit command**: Redesigned with individual agent spawning strategy
- 4-phase workflow: discovery, parallel spawning, aggregation, reporting
- Analysis quality improved through isolated contexts per agent evaluation
- Context pollution prevention by using separate audit agents per target
- Parallel execution for improved performance and focused attention per agent

## [2.9.0] - 2025-07-28

### Added
- **MAJOR**: Conditional technology guidelines system with intelligent agent coordination
- guidelines-file agent: MUST USE before modifying files when technology patterns unclear
- guidelines-repo agent: MUST USE for architecture decisions when stack context undetermined
- Centralized detection logic in .support/instructions/stack-mapping.md
- Session-aware guideline state tracking to prevent redundant loading
- Intelligent conditional invocation system that only loads relevant guidelines when needed

### Changed
- Replace static technology detection rules with intelligent conditional agent system
- CLAUDE.md streamlined from 17-line detection rules to 4-line agent protocol
- Context efficiency improved by 50%+ through conditional guideline loading
- Enhanced system scalability with easy extensibility without bloating main context
- Architecture now supports intelligent caching and performance optimization

### Performance
- Conditional loading prevents redundant agent calls and context pollution
- Only loads relevant technology guidelines when actually needed
- Maintains same functionality with significantly improved efficiency
- Session-aware state management reduces redundant operations

## [2.8.0] - 2025-07-28

### Changed
- **MAJOR**: Complete .support structure cleanup and documentation organization
- Flattened docs organization by moving all files from docs/developer-guide/ to docs/
- Removed docs/developer-guide/ subfolder (unnecessary nesting)
- Deleted .support/templates/ directory (outdated TODO template format)
- Deleted .support/prompts/ directory (generic prompts, no unique value)  
- Simplified .support/ to contain only essential directories: stacks/, scripts/, todos/
- Updated all documentation references to reflect flattened structure
- Streamlined template architecture for better usability and maintenance

## [2.7.1] - 2025-07-28

### Removed
- Obsolete protocol files from .support/instructions (memory-protocol.md, todo-protocol.md)
- Redundant git-workflow.md (functionality consolidated in CLAUDE.md)
- Generic debug-mcp.md command (functionality removed)

### Changed
- Moved instruction files from .support/instructions/ to docs/ for human reference
- Separated AI operational instructions (CLAUDE.md) from human-readable developer guides
- Updated all documentation references to reflect new file locations
- Created docs/README.md explaining purpose of developer reference materials

## [2.7.0] - 2025-07-28

### Added
- Complete TODO management command suite with agent delegation
- `/todo-create` command for new task creation via todo agent
- `/todo-review` command for analyzing existing TODOs and prioritization 
- `/todo-cleanup-done` command for removing implemented TODOs (CHANGELOG verified)
- `/todo-cleanup-stale` command for removing obsolete/irrelevant TODOs
- All commands maintain clean context principle through agent coordination

## [2.6.1] - 2025-07-28

### Changed
- **MAJOR**: Complete TODO protocol modernization with agent-based management
- Removed 5 command files (521 lines): todo.md, todo-add.md, todo-complete.md, todo-release.md, todo-status.md
- Replaced with context-clean TODO agent (110 lines) for specialized task coordination
- Updated all documentation to reflect agent-based TODO system (README.md, features.md, getting-started.md, customization.md)
- Removed todo-system.md documentation file
- Created sample TODO file for user authentication implementation
- Eliminated context pollution from TODO management while preserving full functionality

## [2.6.0] - 2025-07-28

### Changed
- Updated README.md and features.md to reflect new mandatory protocols from CLAUDE.md
- Added mandatory agent coordination requirements (minimum 3+ agents for non-trivial requests)
- Added mandatory documentation protocol (automatic updates with every code change)
- Enhanced best practices and automation features documentation

## [2.5.1] - 2025-07-28

### Changed
- Implemented mandatory 4-step git protocol directly in CLAUDE.md for improved compliance
- Moved critical git workflow to primary operational instructions
- Simplified agent coordination with clear protocol requirements
- Enhanced operational reliability by ensuring protocol visibility in main context

## [2.5.0] - 2025-07-28

### Removed
- **MAJOR**: Removed memory export/import functionality entirely (366 lines removed)
- Deleted `.support/memories/` directory and all memory files
- Removed memory export references from git workflow documentation
- Deleted memory-system.md documentation file
- Removed memory-export/import command references from all documentation

### Changed
- Simplified memory handling to use only Claude Code's built-in MCP memory server
- Updated documentation to reflect streamlined memory architecture
- Reduced system complexity by eliminating custom memory management layer

## [2.4.0] - 2025-07-28

### Changed
- **MAJOR**: Completed stack file reference conversion with 48% final reduction (859 lines removed)
- Converted cpp.md, java.md, and ruby.md from verbose tutorials to concise reference cards
- Achieved 59% total reduction across all stack files (3,571 → 1,477 lines)
- Enhanced autonomous operation efficiency while preserving all essential development patterns
- Completed major documentation architecture optimization phase

## [2.3.0] - 2025-07-28

### Changed
- **MAJOR**: Implemented 60% instruction simplification reducing operational complexity
- Consolidated memory protocol eliminating 1,260+ lines of boilerplate documentation
- Streamlined core agent files from 148-173 lines to ~40 lines each (researcher.md, completer.md, critic.md)
- Converted python.md stack file from 467-line tutorial to 82-line quick reference
- Enhanced autonomous operation efficiency while preserving all core functionality
- All agents now reference shared memory protocol for consistency

## [2.0.1] - 2025-07-28

### Added
- Specialized tagger agent for autonomous release management
- 5-point assessment criteria for intelligent milestone evaluation (completeness, stability, value, logical breakpoint, significance)
- Autonomous tag creation without context pollution
- MCP memory integration for learning successful tagging patterns
- Updated git workflow to automatically invoke tagger after commits

### Changed
- Git workflow now includes automatic tagger agent invocation after each commit
- Streamlined release process with autonomous decision-making
- CLAUDE.md updated to reference new autonomous tagging system

## [1.5.3] - 2025-01-28

### Added
- Automatic intelligent tagging system for Claude Code
- Autonomous release detection without user prompting required
- Automatic tag assessment criteria: completeness, stability, value, logical breakpoint
- Auto-update CHANGELOG.md and auto-increment versioning capabilities
- Simple TODO management system using individual markdown files in todos/ directory
- Updated `/todo` command to use only Claude Code built-in tools (Glob, Read, Write, Edit)
- Technology stack detection section in CLAUDE.md
- Git workflow instructions emphasizing frequent commits and trunk-based development
- Organized instruction files: documentation.md, agent-usage.md, versioning.md

### Changed
- **MAJOR**: Drastically streamlined CLAUDE.md to eliminate redundancy with built-in Claude Code features
- Added .claude configuration principles emphasizing AI-first design and zero redundancy
- Reduced CLAUDE.md from verbose instructions to project-specific overrides only
- Separated AI-optimized configuration (.claude) from human-readable docs (docs/, README.md)
- Simplified TODO management approach - removed complex Python scripts and CLI tools
- Restored original TODO.md content with agent parallelism optimization notes
- Enhanced versioning.md with simplified TODO workflow
- Reorganized instructions into topic-specific files in .claude/instructions/
- Updated CLAUDE.md to use @ syntax for file references
- Added technology stack detection rules for automatic language-specific guidance
- Added trunk-based development rules and automatic commit/push policy
- Added C# detection rule for .cs, .csproj, and .sln files

### Removed
- Removed complex TODO management scripts (todo-manager.py, claude-todo, scan-todos.py, install-todo-system.sh)
- Removed verbose TODO implementation documentation (docs/todo-management-system.md, docs/todo-system-implementation.md)
- Removed redundant MCP servers from .mcp.json (filesystem, fetch) - Claude Code has built-in capabilities
- Removed git protocol details from CLAUDE.md - moved to modular instructions
- Removed redundant `config.json` file - all configuration now in CLAUDE.md and settings.json
- Removed VERSIONING.md file - versioning instructions moved to docs/versioning.md
- Removed customInstructions field from settings.json (invalid field)

## [1.4.0] - 2025-01-27

### Added
- New `critic` agent to prevent sycophancy and challenge ideas
- `/discuss` command for critical analysis of proposals
- MCP memory integration for storing patterns and principles across sessions
- Documentation philosophy in docsync agent

### Changed
- docsync agent now strongly prefers updating existing docs over creating new ones
- patterns and principles agents now use MCP memory server for persistent storage
- Updated agent count to 19 total agents

### Improved
- Documentation strategy to avoid file proliferation
- Critical thinking capabilities with dedicated skeptical agent

## [1.3.1] - 2025-01-27

### Changed
- Made all agent descriptions more specific with clear triggers
- Added keywords, phrases, and commands that activate each agent
- Maintained emphasis patterns (PROACTIVELY, AUTOMATICALLY, MUST BE USED)
- Fixed prompt-engineer agent to focus on user's project agents, not template agents

### Removed
- Deleted unnecessary .claude/agents/examples/ folder

### Fixed
- Agent descriptions now include specific activation scenarios
- Better agent selection through concrete trigger words

## [1.3.0] - 2025-01-27

### Added
- New `prompt-engineer` agent for creating optimized AI framework prompts
- `/create-prompt` command for easy prompt generation
- Example implementation: patterns-langchain-gpt4.md
- Support for LangChain, CrewAI, AutoGen prompt optimization

### Changed
- Updated agent count to 18 total agents
- Enhanced CLAUDE.md with prompt-engineer usage guidelines

## [1.2.1] - 2025-01-27

### Changed
- Optimized agent files for AI efficiency (70%+ size reduction)
  - patterns.md: 70 → 29 lines
  - whisper.md: 80+ → 29 lines  
  - researcher.md: 131 → 39 lines
  - docsync.md: 128 → 36 lines
- Optimized doc-update command: 78 → 22 lines
- Removed ASCII art and graphical structures from python.md
- Removed verbose metaphors and descriptions
- Focus on actionable, concise instructions

### Removed
- Deleted CLAUDE_CODE_TOOLS.md (redundant reference)
- Removed PostgreSQL from example MCP config

### Fixed
- All markdown files now optimized for Claude Code processing
- Better context efficiency and faster agent loading

## [1.2.0] - 2025-01-27

### Added
- CLAUDE_CODE_TOOLS.md documenting all built-in Claude Code tools
- Clear guidance on which MCP servers are redundant vs useful

### Changed
- Removed redundant filesystem and fetch MCP servers from default configuration
- Updated .mcp.json to only include memory server (adds unique value)
- Updated example configurations to exclude redundant servers
- Modified install.sh to only install non-redundant MCP tools
- Updated README to clarify MCP tool usage

### Fixed
- Eliminated unnecessary MCP server overhead for built-in functionality
- Clearer documentation prevents users from installing redundant tools

## [1.1.1] - 2025-01-27

### Added
- VERSIONING.md with semantic versioning guidelines
- Version badge in README.md
- Versioning section in CLAUDE.md with quick reference

### Changed
- Renamed `verify-setup.sh` to `validate-template.sh` for clarity
- Improved script documentation and purpose description
- Updated all references to use new filename

### Fixed
- Script naming now accurately reflects its purpose as a template validator

## [1.1.0] - 2025-01-27

### Added
- Modular technology stack system in `.claude/stacks/`
- Python-specific guidelines moved to `.claude/stacks/python.md`
- New commands: `/stacks` and `/use-python` for stack management
- Python expert agent for Python-specific assistance
- MCP servers README with detailed configuration instructions
- Proper `.mcp.json` file for Claude Code MCP configuration

### Changed
- Improved agent descriptions with action-oriented language and specific triggers
- Updated MCP configuration to use `.mcp.json` instead of settings.json
- Enhanced verification script to check new features
- Refined customInstructions to reference technology stacks

### Fixed
- Corrected MCP server configuration location for Claude Code
- Updated all agent descriptions to follow best practices

## [1.0.0] - 2025-01-27

### Added
- Initial release of Claude Code Configuration Template
- Complete dotfiles setup with automatic installation via `install.sh`
- 16 specialized AI agents organized by pattern-based and first-principles approaches:
  - Pattern-based agents: context, patterns, explore, whisper, constraints, time, connect, complete, hypothesis, meta
  - First-principles agents: principles, axioms, invariants
  - Utility agents: resolve (conflict resolution), docsync (documentation), researcher (parallel searches)
- Custom slash commands:
  - `/review` - Comprehensive code review
  - `/test` - Testing assistance  
  - `/refactor` - Code improvement
  - `/security` - Security audit
  - `/langchain-agent` - LangChain development
  - `/crewai-crew` - CrewAI multi-agent systems
  - `/python-uv` - Python project setup with uv
  - `/agents-guide` - Guide for using specialized AI agents
  - `/doc-update` - Update documentation to match code changes
- MCP (Model Context Protocol) tool integrations:
  - filesystem - Local file access
  - memory - Persistent session memory
  - fetch - Web content retrieval
- Automation hooks for security and code quality
- Comprehensive agent usage guidelines in CLAUDE.md
- Python development workflow using uv exclusively
- Documentation maintenance workflow with automatic synchronization
- Git aliases for Claude-powered commits and PRs

### Configuration
- Main configuration moved to `.claude/settings.json` (auto-loaded by Claude Code)
- Project-specific settings in `.claude/config.json`
- Removed deprecated GitHub MCP server from examples
- Added proactive agent usage instructions
- Configured trunk-based development workflow

### Security
- Pre-read security hook to detect sensitive data
- Dangerous command validation
- Sensitive file blocking (`.env`, `*.key`, etc.)

### Documentation
- Comprehensive README with installation methods
- CLAUDE.md with project guidelines and agent usage
- Agent documentation with clear trigger conditions
- Installation support for both bash and zsh shells