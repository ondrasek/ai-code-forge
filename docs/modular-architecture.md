# AI Code Forge Modular Architecture (v4.0+)

## Overview

AI Code Forge v4.0+ introduces a revolutionary modular architecture that eliminates the atomic deployment limitations of previous versions. Everything is now a **module** with optional **skills** integration, providing granular control over development environment setup.

## Core Principles

### 1. Everything is a Module
- Unified conceptual model: all functionality packaged as modules
- Modules can contain files, skills, or both
- Independent versioning and lifecycle management
- M:N relationship between modules and skills

### 2. Git-Native Operations
- Leverages Git for rollback, state management, and atomicity
- `git commit` boundaries ensure installation consistency
- `git reset --hard` provides instant rollback capability
- Git history serves as complete installation audit trail

### 3. Separate Development, Bundled Distribution
- Modules and skills maintained separately in repository
- Distributed together via manifest-defined bundles
- Clear separation of concerns during development
- Unified user experience during installation

## Repository Structure

```
ai-code-forge/
├── modules/                      # Module definitions (flat structure)
│   ├── claude-config/           # Basic Claude Code setup
│   ├── scripts-core/            # Essential automation scripts
│   ├── devcontainer-base/       # Common devcontainer patterns
│   ├── python/                  # Complete Python development
│   ├── typescript/              # Complete TypeScript development
│   ├── rust/                    # Complete Rust development
│   ├── java/                    # Complete Java development
│   ├── cloudflare-workers/      # Cloudflare Workers platform
│   ├── worktree/               # Git worktree management
│   ├── github-integration/      # GitHub workflow automation
│   └── readme-generation/       # Documentation generation
├── skills/                       # Skill definitions (flat structure)
│   ├── code-review/            # AI-powered code analysis
│   ├── python-linting/         # Python-specific assistance
│   ├── typescript-analysis/    # TypeScript-specific assistance
│   ├── readme-generator/       # README creation skill
│   ├── architecture-advisor/   # System design guidance
│   └── git-helper/            # Git workflow assistance
├── manifests/                    # M:N relationship definitions
│   └── bundles.yaml             # Module → Skills mappings
└── cli/                         # Enhanced CLI tool
```

## Module Types

### Full-Stack Modules
Contains both filesystem components and AI assistance skills:
- **python**: Complete Python development setup with AI assistance
- **typescript**: Complete TypeScript setup with analysis skills
- **rust**: Rust environment with Rust-specific AI assistance

### Skills-Only Modules
Pure AI enhancement without filesystem changes:
- **readme-generation**: Documentation creation skills
- Skills are bundled with relevant modules via manifests

### Foundation Modules
Essential components required by other modules:
- **claude-config**: Basic Claude Code configuration
- **scripts-core**: Essential automation utilities
- **devcontainer-base**: Common Docker patterns

## Module Metadata

Each module includes `module.yaml` with metadata:

```yaml
name: python
version: 1.2.3
description: "Complete Python development with AI assistance"
category: technology-stack
capabilities:
  files: true                     # Installs filesystem components
  skills: true                    # Includes Claude Skills
dependencies:
  - claude-config: ">=1.0.0"
  - devcontainer-base: ">=2.1.0"
install:
  files:
    - ".devcontainer/ -> .devcontainer/"
    - ".acforge/ -> .acforge/"
  skills:
    - "python-linting"            # Auto-install with module
    - "python-testing"            # Auto-install with module
# conflicts: []                     # Module conflicts - to be implemented later
```

## Installation Process

### Git-Based Atomic Operations

```bash
# Installation with automatic rollback capability
acforge module install python

# Internal process:
# 1. git stash push -m "acforge backup"
# 2. Deploy module files
# 3. git add .
# 4. Deploy module skills
# 5. git commit -m "acforge: install python v1.2.3"
# 6. git stash drop

# On failure: automatic rollback
# git reset --hard HEAD
# git stash pop
```

### State Management

Simple JSON state file tracked in Git:

```json
{
  "version": "4.0.0",
  "modules": {
    "python": {
      "version": "1.2.3",
      "capabilities": ["files", "skills"],
      "files": [".devcontainer/", ".acforge/stacks/python.md"],
      "skills": ["python-linting", "python-testing", "code-review"],
      "installed": "2025-11-16T16:30:00Z"
    }
  },
  "skills": {
    "code-review": {
      "version": "2.1.0",
      "shared_by": ["python", "typescript"]
    }
  }
}
```

## CLI Commands

### Module Management
```bash
# Install modules
acforge module install python typescript worktree
acforge module install --all

# Update modules
acforge module update python
acforge module update --all

# Remove modules
acforge module remove typescript
acforge module remove --all

# Status and information
acforge module list                    # Show installed
acforge module list --available        # Show all available
acforge module status                  # Check for updates
acforge module check                   # Validate installation
```

### Skills Management
```bash
# Skills managed automatically with modules
acforge skills list                    # Show installed skills
acforge skills update python-linting   # Update specific skill
acforge skills sync                    # Sync to Claude platforms
```

### Granular Control
```bash
# Install only specific components
acforge module install python --files-only     # Skip skills
acforge module install python --skills-only    # Skip files
```

## Rollback and Recovery

### Instant Rollback
```bash
# Rollback failed installation
git reset --hard HEAD                   # Instant file rollback
git clean -fd                          # Remove untracked files

# Rollback to previous working state
git checkout HEAD~1 -- .acforge/
git commit -m "acforge: rollback to previous state"
```

### Historical Recovery
```bash
# View installation history
git log --oneline --grep="acforge"

# Rollback to specific configuration
git checkout <commit-hash> -- .acforge/
git commit -m "acforge: restore to working configuration"
```

### Tagged Configurations
```bash
# Tag stable configurations
git tag acforge-python-stable-1.2.3
git tag acforge-full-stack-2024-11-16

# Restore tagged configuration
git checkout acforge-python-stable-1.2.3 -- .
```

## M:N Module-Skills Relationships

### Shared Skills
Skills can be used by multiple modules:
- `code-review` skill shared by Python, TypeScript, Rust modules
- `architecture-advisor` skill used across all technology modules
- `readme-generator` skill available to all modules

### Reference Counting
```yaml
# Automatic cleanup when last module removed
skills:
  code-review:
    shared_by: ["python", "typescript"]  # 2 references

# When typescript removed:
skills:
  code-review:
    shared_by: ["python"]                # 1 reference

# When python removed: skill automatically cleaned up
```

## Migration from v3.x

### No Backward Compatibility
- v4.0+ represents complete architectural change
- No automatic migration from atomic templates
- Users must start fresh with module-based approach
- Benefits justify breaking changes

### Migration Strategy
1. **Backup**: Export current v3.x configuration
2. **Fresh Start**: Initialize v4.0+ in new directory or branch
3. **Module Selection**: Choose relevant modules for your stack
4. **Custom Migration**: Manually apply any customizations
5. **Validation**: Test new modular setup thoroughly

## Benefits Over Atomic Templates

### Granular Control
- Install only needed components
- Independent module versioning
- Selective updates and removals

### Git Integration
- Leverages Git's proven reliability
- No custom transaction management
- Natural rollback capabilities
- Complete audit trail

### Scalability
- Easy addition of new technology modules
- Skills can be developed independently
- M:N relationships support complex workflows

### Maintainability
- Clear separation of concerns
- Independent module development
- Simplified testing and validation

## Future Considerations

### Claude Skills Evolution
- Modular architecture adapts to Claude Skills platform changes
- Skills remain optional enhancements
- Filesystem components work regardless of Skills platform status

### Technology Expansion
- New language modules easily added
- Cloud platform modules (AWS, GCP, Azure)
- Framework-specific modules (Next.js, Django, etc.)

### Enterprise Features
- Module signing and verification
- Private module repositories
- Centralized module management

## Conclusion

The modular architecture represents a fundamental shift from monolithic templates to composable, versioned modules. By leveraging Git's native capabilities and providing clear separation between files and skills, AI Code Forge v4.0+ delivers the granular control and independent lifecycle management that modern development workflows demand.