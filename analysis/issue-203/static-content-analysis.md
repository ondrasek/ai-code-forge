# Static Content Distribution Analysis

## Problem Statement

The template-first architecture handles **parameterized content** well, but there's a significant category of **static content** that needs distribution to external repositories but doesn't require parameterization.

## Content Categories Identified

### 1. **Scripts Directory** - HIGH PRIORITY
**Location**: `scripts/` (17 shell scripts + subdirectories)
**Nature**: Utility scripts for development workflow
**Distribution Need**: HIGH - External repositories need these for full ai-code-forge functionality

**Key Scripts**:
- `launch-claude.sh` (33KB) - Enhanced Claude Code wrapper
- `launch-codex.sh` (21KB) - Codex analysis wrapper  
- `analyze-*.sh` (multiple) - JSONL, MCP, usage analysis tools
- `worktree/*.sh` (7 scripts) - Git worktree management
- `validate-*.sh` (multiple) - Validation and testing utilities
- `lib/launcher-utils.sh` - Shared utility functions

**Parameterization Assessment**: 
- ✅ **Mostly Static** - Scripts work generically across repositories
- ⚠️ **Some Repository References** - Found "claude", "worktree" hardcoded references
- ✅ **No Critical Parameterization** - Work correctly without modification

### 2. **MCP Servers Directory** - MEDIUM PRIORITY  
**Location**: `mcp-servers/` 
**Nature**: Model Context Protocol server implementations
**Distribution Need**: MEDIUM - Useful for external repositories using MCP

**Content Assessment**: Need to examine structure for distribution requirements

### 3. **Documentation Directory** - LOW PRIORITY
**Location**: `docs/`
**Nature**: Project documentation and guides  
**Distribution Need**: LOW - Primarily ai-code-forge specific

**Rationale**: External repositories would create their own documentation

### 4. **Analysis Directory** - NO DISTRIBUTION
**Location**: `analysis/` 
**Nature**: Issue-specific analysis and research
**Distribution Need**: NONE - Specific to ai-code-forge issues

## Distribution Strategy Requirements

### **Static Content != Templates**
**Key Insight**: These files need **direct copying** not **parameter substitution**
- No `{{PARAMETER}}` placeholders
- Preserve file permissions (executable scripts)
- Maintain directory structure  
- No processing required

### **CLI Enhancement Needed**
Current CLI system only handles:
- ✅ Template processing (with parameters)
- ❌ Static file distribution (missing capability)

**Required Enhancement**: Add static content deployment alongside template system

### **Directory Structure Impact**
External repositories would gain:
```
target-repo/
├── .claude/          ✅ From templates (30 files)
├── .devcontainer/    ✅ From templates (23 files)  
├── scripts/          ❌ Missing - needs static distribution
├── mcp-servers/      ❌ Missing - needs static distribution
└── docs/             ❌ Optional - repository-specific
```

## Implementation Requirements

### **CLI Deployer Enhancement**
**Current**: `TemplateDeployer` handles only parameterized templates
**Needed**: `StaticContentDeployer` for direct file copying

**Integration Points**:
1. **Detection**: Identify static vs template content in CLI bundle
2. **Deployment**: Copy static files without processing
3. **Permissions**: Preserve executable permissions for scripts
4. **Structure**: Maintain source directory hierarchy

### **Template vs Static Distribution**
**Templates** (parameter processing):
- `.claude/` directory → from `templates/` 
- `.devcontainer/` directory → from `templates/devcontainer/`

**Static Content** (direct copying):
- `scripts/` directory → from `scripts/`
- `mcp-servers/` directory → from `mcp-servers/`

### **CLI Bundle Structure Update**
**Current Bundle**:
```
cli/src/ai_code_forge_cli/
├── templates/          ✅ Template files (processed)
└── [no static content] ❌ Missing static files
```

**Required Bundle**:
```
cli/src/ai_code_forge_cli/
├── templates/     ✅ Template files (processed) 
└── static/        ❌ Static files (copied directly)
    ├── scripts/
    └── mcp-servers/
```

## Validation Requirements

### **Dogfooding Test Enhancement**
**Current Test**: `acf init --force` deploys 53 template files
**Required Test**: Should also deploy ~17 script files + MCP servers

**Expected Result**:
```bash
acf init --force --github-owner=testuser --project-name=test-repo
# Should create:
# - 30 .claude/ files (templates)
# - 23 .devcontainer/ files (templates)  
# - 17 scripts/ files (static)
# - N mcp-servers/ files (static)
```

### **Static Content Validation**
**Verification Points**:
- ✅ Scripts deploy with executable permissions
- ✅ Directory structure preserved (scripts/worktree/, scripts/lib/)
- ✅ File content identical to source (no parameter processing)
- ✅ External repository functionality maintained

## Priority Assessment

### **HIGH PRIORITY: Scripts Directory**
**Justification**: Scripts provide critical workflow functionality that external repositories need for full ai-code-forge benefits.

**Impact**: Without scripts, external repositories get configuration but miss utility tools.

### **MEDIUM PRIORITY: MCP Servers** 
**Justification**: MCP servers enhance functionality but aren't core requirements.

**Analysis Needed**: Examine mcp-servers/ structure to determine distribution requirements.

## Contrarian Questions

1. **Distribution Scope**: Should we distribute ALL scripts or only the universally useful ones?
2. **Versioning**: How do we handle static content updates vs template updates?
3. **Repository Contamination**: Are we adding too much ai-code-forge-specific content to external repositories?
4. **Maintenance Burden**: Who maintains these scripts when they're distributed across multiple repositories?

The template-first architecture needs this static content distribution capability to provide complete functionality to external repositories.