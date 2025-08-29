# Technical Analysis: CLI Phase 1 Rewrite (Issue #205)

## SITUATIONAL CONTEXT ANALYSIS
============================

**SITUATION UNDERSTANDING:**
Need comprehensive codebase context for CLI Phase 1 rewrite implementing `acf status`, `acf init`, and `acf update` commands. This is a complete rebuild from scratch, replacing the existing CLI implementation.

**RELEVANT CODEBASE CONTEXT:**

### Current CLI Implementation Analysis

#### 1. Current CLI Directory Structure (`cli/`)
```
cli/
├── pyproject.toml              # Current package config (v2.92.0)
├── src/ai_code_forge/
│   ├── main.py                 # Click-based CLI with install/status commands
│   ├── core/installer.py       # ACFInstaller class with file operations
│   └── data/                   # Bundled template data
│       ├── CLAUDE.md           # Operational rules template
│       ├── claude/             # .claude directory contents
│       └── acf/                # .acforge directory contents (duplicated)
└── tests/                      # Basic test structure
```

#### 2. Current Package Configuration
- **Package Name**: `ai-code-forge` (v2.92.0)
- **CLI Entry Point**: `ai-code-forge = "ai_code_forge.main:main"`
- **Dependencies**: Only `click>=8.1`
- **Python Version**: `>=3.13`
- **Build System**: `hatchling`

#### 3. Current Command Analysis
**`acf install` Command:**
- Creates `.claude/` and `.acforge/` directories
- Copies bundled data from `src/ai_code_forge/data/`
- Installs `CLAUDE.md` to project root
- Has force overwrite option (`--force`)
- Validates target directory existence

**`acf status` Command:**
- Checks for `.claude/`, `.acforge/`, and `CLAUDE.md` presence
- Lists files in each directory
- Provides installation completeness assessment
- Uses ACFInstaller.get_installation_status()

#### 4. Template Data Bundling Strategy
Current implementation bundles templates in `src/ai_code_forge/data/`:
- **`claude/`**: Contains `.claude` directory structure (agents, commands, settings.json)
- **`acf/`**: Contains duplicated templates and documentation
- **`CLAUDE.md`**: Project-specific operational rules

### Template Directory Analysis (`templates/`)

#### Template Structure for Bundling:
```
templates/
├── CLAUDE.md.template          # Template with placeholders {{GITHUB_OWNER}}, {{GITHUB_REPO}}
├── guidelines/                 # 11 guideline files (.md)
│   ├── CLAUDE.md
│   ├── claude-agents-guidelines.md
│   ├── claude-commands-guidelines.md
│   └── ... (8 more guideline files)
├── prompts/                    # 2 prompt template files
│   ├── master-prompt.md
│   └── worktree-deliver.template.md
├── readme/                     # 3 README templates
│   ├── general-project-template.md
│   ├── library-package-template.md
│   └── mcp-server-template.md
└── stacks/                     # 9 technology stack guides
    ├── bash.md
    ├── python.md
    └── ... (7 more stack files)
```

**Total Files to Bundle**: 26 template files across 4 categories

### Configuration Management Patterns

#### Current `.claude` Structure (from data/claude/):
```
.claude/
├── agents/
│   ├── foundation/             # 6 core agents (context.md, critic.md, etc.)
│   └── specialists/            # 11 specialist agents
├── commands/                   # Nested command structure
│   ├── agents/, commands/, issue/
│   └── 20+ individual command files
└── settings.json               # Claude Code configuration
```

#### Settings.json Configuration:
```json
{
  "model": "claude-sonnet-4-20250514",
  "permissions": {
    "defaultMode": "bypassPermissions"
  },
  "includeCoAuthoredBy": true,
  "cleanupPeriodDays": 30
}
```

### State Management Requirements

#### Current Installation State Tracking:
The existing `ACFInstaller.get_installation_status()` tracks:
- `claude_dir_exists`: Boolean for `.claude/` presence
- `acf_dir_exists`: Boolean for `.acforge/` presence  
- `claude_md_exists`: Boolean for `CLAUDE.md` presence
- `claude_files`: List of files in `.claude/`
- `acf_files`: List of files in `.acforge/`

#### Required State Management for Phase 1:
Based on issue requirements, need **3 JSON files in `.acforge/`**:
1. **`installation.json`** - Track what's installed and versions
2. **`customizations.json`** - User modifications to preserve during updates
3. **`templates.json`** - Template source tracking and metadata

### Python Packaging Constraints

#### Current Dependencies:
- **Core**: `click>=8.1` (only production dependency)
- **Dev**: `pytest>=8.0`
- **Build**: `hatchling` with custom package inclusion
- **Distribution**: TestPyPI configured

#### Packaging Challenges:
- **Template Bundling**: Current uses manual copying in `data/` directory
- **Resource Access**: Uses `importlib.resources` with fallback to development paths
- **Path Resolution**: Complex logic for finding bundled data

### Existing Script Ecosystem Analysis

#### Scripts Directory (`scripts/`):
- **19 shell scripts** for worktree management, launching, validation
- **Complex bash utilities** in `lib/launcher-utils.sh`
- **Test infrastructure** with security and integration tests
- **Worktree management system** with terminal title integration

#### Key Integration Points:
- **`worktree-init.sh`**: 566-line script with shell configuration generation
- **Security patterns**: Input validation, absolute paths, sanitization
- **Terminal integration**: Title management, multi-shell support

## HISTORICAL CONTEXT:

### Past Decisions:
1. **Click Framework**: Chosen for CLI implementation (established pattern)
2. **Hatchling Build**: Selected over setuptools for modern Python packaging
3. **Data Directory**: Bundled templates in `src/ai_code_forge/data/`
4. **Dual Directory**: Both `.claude/` and `.acforge/` created by installer

### Evolution:
- **Version Progression**: Currently at v2.92.0
- **Command Expansion**: Started with install/status, needs init/update
- **Template Growth**: 26+ template files to manage
- **Script Ecosystem**: Extensive bash infrastructure developed

### Lessons Learned:
- **Resource Loading**: Complex path resolution needed for development vs installed
- **Template Duplication**: Current `acf/` directory duplicates some template content
- **State Tracking**: Simple boolean tracking insufficient for update operations

## SITUATIONAL RECOMMENDATIONS:

### Suggested Approach:
1. **Complete CLI Rebuild**: Delete `cli/` directory and start fresh
2. **Simplified Package Structure**: Clean pyproject.toml with proper hatchling configuration
3. **State-First Design**: Implement 3 JSON state files before commands
4. **Template Bundling**: Use hatchling force-include from `/templates` directly
5. **Resource Access**: Modern `importlib.resources` with proper fallbacks

### Key Considerations:
1. **Breaking Change**: Complete rewrite will break existing installations
2. **Template Synchronization**: Update command needs diff detection
3. **Customization Preservation**: Critical for user adoption
4. **Testing Strategy**: Need validation against real ai-code-forge repository

### Implementation Notes:
1. **Command Priority**: Start with `status` (simplest), then `init`, then `update`
2. **State Management**: JSON files must be atomic operations
3. **Template Processing**: Handle placeholders like `{{GITHUB_OWNER}}`
4. **Path Security**: Follow existing script patterns for absolute paths

### Testing Strategy:
- **Unit Tests**: Each command and state manager
- **Integration Tests**: Test against ai-code-forge repository itself
- **Template Validation**: Ensure all 26 template files bundle correctly
- **State Management**: Test customization preservation scenarios

## IMPACT ANALYSIS:

### Affected Systems:
- **Existing CLI Users**: Complete command signature changes
- **Template Distribution**: New bundling mechanism
- **Documentation**: CLI usage examples need updates
- **CI/CD**: Build and test processes need adjustments

### Risk Assessment:
- **User Migration**: No backward compatibility path
- **Template Integrity**: Risk of corruption during bundling
- **State Consistency**: JSON state files could become inconsistent
- **Resource Loading**: Platform-specific importlib.resources behavior

### Documentation Needs:
- **CLI Reference**: Complete rewrite of usage documentation
- **Migration Guide**: How to transition from old CLI
- **State File Format**: JSON schema documentation
- **Template Customization**: How preservation works

### Migration Requirements:
- **Package Rename**: Consider `ai-code-forge` → `acf` transition
- **Command Migration**: `ai-code-forge install` → `acf init`
- **Data Migration**: Convert existing installations to new state format
- **Breaking Change Communication**: Version bump to 3.0.0

## ANALYSIS DOCUMENTATION:

### Context Sources:
- `/workspace/worktrees/ai-code-forge/issue-205/cli/` - Current implementation
- `/workspace/worktrees/ai-code-forge/issue-205/templates/` - Templates to bundle
- `/workspace/worktrees/ai-code-forge/issue-205/scripts/` - Shell script patterns
- `/workspace/worktrees/ai-code-forge/issue-205/analysis/issue-205/research-findings.md` - Issue context

### Key Discoveries:
1. **Template Scale**: 26 files across 4 categories need bundling
2. **State Complexity**: Current boolean tracking insufficient for updates
3. **Script Integration**: Extensive bash ecosystem with security patterns
4. **Resource Challenges**: Complex path resolution for bundled data

### Decision Factors:
1. **Complete Rewrite Justified**: Current architecture doesn't support update operations
2. **State Management Critical**: JSON files are foundation for all operations
3. **Template Bundling**: Must handle 26+ files reliably across platforms
4. **Security Patterns**: Follow established absolute path and validation patterns

## TECHNICAL CONSTRAINTS:

### Python Version:
- **Minimum**: Python 3.13+ (established constraint)
- **Packaging**: Modern hatchling build system
- **Resources**: importlib.resources for template access

### Template Management:
- **Source**: 26 files in `/templates` directory
- **Processing**: Handle `{{PLACEHOLDER}}` substitution
- **Bundling**: Force-include via hatchling configuration
- **Access**: Runtime loading via importlib.resources

### State Consistency:
- **Atomic Operations**: JSON file updates must be transactional
- **Schema Validation**: JSON structure must be validated
- **Error Handling**: Graceful degradation for corrupted state

### CLI Design:
- **Framework**: Click (established pattern)
- **Commands**: 3 commands only (status, init, update)
- **Options**: Minimal flags, focus on simplicity
- **Output**: User-friendly with clear status indicators

This analysis provides comprehensive context for the CLI Phase 1 rewrite, identifying what needs to be replaced, what templates need bundling, current configuration patterns, and technical constraints that will guide the implementation.