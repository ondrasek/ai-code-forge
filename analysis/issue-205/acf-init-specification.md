# ACF Init Command Specification

## Overview

The `acf init` command bootstraps a repository with AI Code Forge configuration by:
1. Creating `.acf/` directory for ACF state management
2. Creating `.claude/` directory with Claude Code configuration from templates
3. Performing template parameter substitution for repository-specific values
4. Initializing state tracking for future template synchronization

## Command Signature

```bash
acf init [OPTIONS] [TARGET_DIR]
```

## Arguments

- `TARGET_DIR` (optional): Target repository directory (defaults to current directory)

## Options

- `--force`, `-f`: Overwrite existing configuration without prompting
- `--dry-run`: Show what would be created without making changes
- `--template-set NAME`: Use specific template set (defaults to 'full')
- `--interactive`, `-i`: Prompt for all template parameters
- `--github-owner OWNER`: Override GitHub owner detection
- `--project-name NAME`: Override project name detection
- `--verbose`, `-v`: Show detailed progress information

## Behavior Specification

### 1. Pre-initialization Validation

**Repository Detection:**
- Verify target directory exists and is writable
- Detect if directory is a git repository
- Extract GitHub owner/project from git remote or prompt user
- Validate repository structure (presence of key files)

**Existing Configuration Detection:**
- Check for existing `.claude/` directory
- Check for existing `.acf/` directory
- If either exists without `--force`:
  - Display current configuration status
  - Prompt: "Configuration exists. Overwrite? [y/N/show]"
  - "show" option displays current vs. new configuration diff
  - Exit gracefully on "N" or Ctrl+C

**Template Validation:**
- Verify bundled templates are accessible
- Validate template integrity (checksums)
- Check for required template files (agents, settings.json, etc.)

### 2. Directory Structure Creation

**`.acf/` State Directory:**
```
.acf/
├── state.json              # ACF state tracking
├── template-metadata.json  # Template versions and checksums
└── customizations.json     # User customization tracking
```

**`.claude/` Configuration Directory (from templates):**
```
.claude/
├── agents/
│   ├── foundation/         # Foundation agents
│   └── specialists/        # Specialist agents  
├── commands/              # Custom slash commands
├── settings.json          # Claude Code settings
```

### 3. Template Parameter Substitution

**Supported Parameters:**
- `{{GITHUB_OWNER}}` - GitHub repository owner/organization
- `{{PROJECT_NAME}}` - Repository/project name
- `{{REPO_URL}}` - Full GitHub repository URL
- `{{CREATION_DATE}}` - ISO timestamp of initialization
- `{{ACF_VERSION}}` - ACF CLI version used for initialization
- `{{TEMPLATE_VERSION}}` - Template bundle version

**Parameter Detection Logic:**
1. **GitHub Owner**: 
   - Extract from `git remote get-url origin`
   - Fallback: Parse from directory path
   - Fallback: Prompt user (if `--interactive`)
   - Fallback: Use "unknown"

2. **Project Name**:
   - Extract from `git remote get-url origin` 
   - Fallback: Use directory name
   - Fallback: Prompt user (if `--interactive`)

3. **Repository URL**:
   - Construct from owner/project if GitHub detected
   - Otherwise: Leave as `{{REPO_URL}}` for manual editing

**Substitution Process:**
- Process all `.md`, `.json`, `.yml`, `.yaml`, `.sh` files in templates
- Use safe string replacement (escape regex special characters)
- Log substitutions made (in verbose mode)
- Preserve original template structure and permissions

### 4. State Initialization

**`.acf/state.json` Initial Content:**
```json
{
  "version": "1.0",
  "installation": {
    "template_version": "1.2.3",
    "installed_at": "2025-08-28T10:30:00Z",
    "cli_version": "3.0.0",
    "github_owner": "ondrasek",
    "project_name": "my-project",
    "parameters_substituted": ["GITHUB_OWNER", "PROJECT_NAME", "CREATION_DATE"]
  },
  "templates": {
    "checksum": "sha256:abc123...",
    "files": {
      "agents/foundation-context.md": {
        "checksum": "sha256:def456...",
        "customized": false,
        "size": 1234
      }
    }
  },
  "customizations": {
    "preserved_files": [],
    "custom_overrides": {}
  }
}
```

### 5. Success Output

**Standard Output:**
```
🎉 ACF initialization complete!

📁 Created directories:
  ✅ .acf/ (ACF state management)
  ✅ .claude/ (Claude Code configuration)

📦 Deployed templates:
  ✅ 12 foundation agents
  ✅ 8 specialist agents  
  ✅ 15 custom commands
  ✅ Claude Code settings

🔧 Parameters substituted:
  ✅ GitHub owner: ondrasek
  ✅ Project name: my-project
  ✅ Creation date: 2025-08-28T10:30:00Z

💡 Next steps:
  - Run 'acf status' to verify configuration
  - Open repository in Claude Code to test setup
  - Customize templates by creating .local files
  - Use 'acf update' to sync with latest templates

🚀 Repository ready for AI-enhanced development!
```

### 6. Error Handling

**Common Error Scenarios:**

1. **Permission Denied:**
   ```
   ❌ Cannot create .acf directory: Permission denied
   💡 Try: sudo chown -R $USER:$USER .
   ```

2. **Git Repository Issues:**
   ```
   ⚠️  Not a git repository - some features may be limited
   💡 Run: git init && git remote add origin <url>
   ```

3. **Template Access Failure:**
   ```
   ❌ Cannot access bundled templates
   💡 Try: acf status --verbose to diagnose
   ```

4. **Existing Configuration Conflict:**
   ```
   ⚠️  Configuration already exists
   💡 Use --force to overwrite or 'acf update' to sync
   ```

## Implementation Architecture

### Core Components

1. **InitCommand Class** - Main command implementation
2. **ParameterSubstitutor** - Template parameter replacement  
3. **RepositoryDetector** - Git/GitHub metadata extraction
4. **TemplateDeployer** - Template file deployment
5. **StateInitializer** - Initial state file creation

### Key Algorithms

**Template Processing Pipeline:**
1. Load template from bundled resources
2. Detect parameters requiring substitution
3. Apply repository-specific parameter values
4. Write processed template to target location
5. Update state tracking with file metadata

**Conflict Resolution:**
1. Detect existing files
2. Compare checksums (if ACF-managed)
3. Prompt user for resolution strategy
4. Apply user choice (overwrite/skip/diff)

### Testing Strategy

**Unit Tests:**
- Parameter substitution with various input formats
- Repository detection across different git configurations
- State file creation and validation
- Error handling for edge cases

**Integration Tests:**
- Full init workflow on clean directories
- Conflict handling with existing configurations
- Template deployment integrity verification
- Cross-platform compatibility validation

## Future Extensions

**Phase 2 Enhancements:**
- `--template-source` option for remote template sources
- `--minimal` option for lightweight configuration
- `--backup` option to preserve existing configuration
- Template preview mode (`--preview`)
- Batch initialization for multiple repositories

**Integration Points:**
- `acf update` command for template synchronization
- `acf merge` command for existing configuration integration  
- `acf customize` command for template modification
- CI/CD integration for automated repository setup

## Security Considerations

**Input Validation:**
- Sanitize all user input for parameter substitution
- Validate file paths to prevent directory traversal
- Check template integrity with checksums

**Permission Handling:**
- Respect existing file permissions
- Create directories with appropriate permissions (755)
- Create files with appropriate permissions (644)

**Template Security:**
- Validate template content before processing  
- Prevent template injection attacks
- Log all template modifications for audit

## Compatibility

**Requirements:**
- Python 3.9+
- Git repository (optional but recommended)
- Write permissions in target directory
- Network access not required (templates bundled)

**Platform Support:**
- Linux/Unix: Full support
- macOS: Full support  
- Windows: Full support (with path handling considerations)

**Claude Code Integration:**
- Compatible with Claude Code v1.0+
- Generates standard `.claude/` configuration
- No Claude Code specific dependencies required