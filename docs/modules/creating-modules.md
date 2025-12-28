# Creating AI Code Forge Modules

## Module Development Guide

This guide covers creating custom modules for AI Code Forge v4.0+.

## Module Structure

Every module follows a standard structure:

```
modules/category/module-name/
├── module.yaml              # Module metadata
├── VERSION                  # Semantic version
├── files/                   # Files to install (optional)
│   ├── .devcontainer/
│   ├── .acforge/
│   └── scripts/
├── README.md               # Module documentation
└── tests/                  # Module tests (optional)
```

## Module Metadata (module.yaml)

Required metadata for every module:

```yaml
name: module-name
version: 1.0.0
description: "Brief description of module functionality"
category: technology-stack | workflow | enhancement | core
capabilities:
  files: true|false         # Installs filesystem components
  skills: true|false        # Includes Claude Skills
dependencies:               # Optional dependencies
  - claude-config: ">=1.0.0"
  - devcontainer-base: ">=2.1.0"
install:                    # File installation mapping
  files:
    - "source/path -> target/path"
    - ".devcontainer/ -> .devcontainer/"
  skills:                   # Optional skills list
    - "skill-name"
# conflicts: []           # Module conflicts - to be implemented later
compatibility:              # Version requirements
  claude-code: ">=2.78.0"
  ai-code-forge: ">=4.0.0"
```

## Module Naming

Use descriptive, self-explanatory names in flat structure:

### Language Modules
- **python**: Complete Python development setup
- **typescript**: Complete TypeScript development setup
- **rust**: Complete Rust development setup
- **java**: Complete Java development setup

### Platform/Framework Modules
- **cloudflare-workers**: Cloudflare Workers development
- **nextjs**: Next.js framework setup
- **django**: Django framework setup

### Workflow Modules
- **worktree**: Git worktree management
- **github-integration**: GitHub workflow automation

### Foundation Modules
- **claude-config**: Basic Claude Code setup
- **scripts-core**: Essential automation
- **devcontainer-base**: Common patterns

## File Installation

### Source Structure
```
files/
├── .devcontainer/
│   ├── devcontainer.json
│   └── Dockerfile
├── .acforge/
│   ├── stacks/
│   └── guidelines/
└── scripts/
    └── module-script.sh
```

### Installation Mapping
```yaml
install:
  files:
    - ".devcontainer/ -> .devcontainer/"
    - ".acforge/ -> .acforge/"
    - "scripts/ -> scripts/"
```

Target paths are relative to repository root where module is installed.

## Skills Integration

### Bundled Skills
List skills that should be installed with the module:

```yaml
install:
  skills:
    - "technology-linting"    # Technology-specific skill
    - "code-review"          # Shared skill
    - "architecture-advisor" # Generic skill
```

### Skill Dependencies
Skills are maintained separately in `/skills/` directory. Module bundles reference skills by name, enabling M:N relationships.

## Versioning

### Semantic Versioning
- **MAJOR**: Breaking changes to module structure or dependencies
- **MINOR**: New features, additional skills, non-breaking changes
- **PATCH**: Bug fixes, documentation updates, minor improvements

### VERSION File
```
1.2.3
```

Simple text file containing current module version.

## Dependencies

### Module Dependencies
```yaml
dependencies:
  - claude-config: ">=1.0.0"    # Requires specific version range
  - scripts-core: "1.x.x"       # Compatible with 1.x series
  - devcontainer-base: "~2.1.0" # Compatible with 2.1.x
```

### Dependency Resolution
- Dependencies installed automatically before module
- Conflicts checked during installation
- Version compatibility validated

## Testing

### Module Tests
```
tests/
├── test-installation.sh     # Installation testing
├── test-functionality.sh    # Feature validation
└── test-cleanup.sh         # Removal testing
```

### Test Integration
```bash
# Run module tests
cd modules/category/module-name
./tests/test-installation.sh
./tests/test-functionality.sh
./tests/test-cleanup.sh
```

## Development Workflow

### 1. Module Creation
```bash
# Create module structure
mkdir -p modules/my-language
cd modules/my-language

# Create metadata
cat > module.yaml << EOF
name: my-language
version: 1.0.0
description: "Complete My Language development setup"
capabilities:
  files: true
  skills: true
EOF

# Create version
echo "1.0.0" > VERSION
```

### 2. File Development
```bash
# Create files structure
mkdir -p files/.devcontainer
mkdir -p files/.acforge/stacks
mkdir -p files/.acforge/guidelines/my-language

# Develop devcontainer
cat > files/.devcontainer/devcontainer.json << EOF
{
  "name": "My Language Development",
  "image": "my-language:latest"
}
EOF
```

### 3. Testing
```bash
# Test module installation
acforge module install my-language --dev

# Validate functionality
# Test in clean environment
```

### 4. Documentation
```bash
# Document module
cat > README.md << EOF
# My Language Module

Complete development setup for My Language projects.

## Features
- Optimized devcontainer
- Language-specific guidelines
- AI assistance skills

## Requirements
- Docker
- Claude Code 2.78+

## Usage
\`\`\`bash
acforge module install my-language
\`\`\`
EOF
```

## Best Practices

### Module Design
- **Single Responsibility**: Each module should have one clear purpose
- **Minimal Dependencies**: Avoid unnecessary dependencies
- **Clear Documentation**: Comprehensive README and inline comments
- **Version Compatibility**: Test with multiple Claude Code versions

### File Organization
- **Consistent Structure**: Follow standard module layout
- **Relative Paths**: Use relative paths in installation mappings
- **No Hardcoded Paths**: Avoid absolute paths in configuration
- **Platform Independence**: Work across different operating systems

### Skills Integration
- **Logical Grouping**: Bundle related skills with modules
- **Shared Skills**: Use existing skills when possible
- **Clear Naming**: Use descriptive skill names
- **Version Alignment**: Keep skill versions compatible

### Testing Strategy
- **Installation Testing**: Verify clean installation
- **Functionality Testing**: Validate all features work
- **Cleanup Testing**: Ensure complete removal
- **Integration Testing**: Test with other modules

## Common Patterns

### Language Module Template
```yaml
name: language-name
version: 1.0.0
description: "Complete Language Name development setup"
capabilities:
  files: true
  skills: true
dependencies:
  - claude-config: ">=1.0.0"
  - devcontainer-base: ">=2.1.0"
install:
  files:
    - ".devcontainer/ -> .devcontainer/"
    - ".acforge/stacks/technology.md -> .acforge/stacks/"
    - ".acforge/guidelines/technology/ -> .acforge/guidelines/"
  skills:
    - "technology-linting"
    - "technology-testing"
    - "code-review"
# conflicts: []           # Module conflicts - to be implemented later
```

### Workflow Module Template
```yaml
name: workflow-name
version: 1.0.0
description: "Workflow enhancement description"
category: workflow
capabilities:
  files: true
  skills: false
dependencies:
  - scripts-core: ">=1.0.0"
install:
  files:
    - "scripts/ -> scripts/"
    - "docs/ -> docs/"
```

### Skills-Only Module Template
```yaml
name: enhancement-name
version: 1.0.0
description: "Enhancement functionality description"
capabilities:
  files: false
  skills: true
install:
  skills:
    - "enhancement-skill"
    - "helper-skill"
```

## Module Distribution

### Local Development
```bash
# Install from local development
acforge module install ./modules/module-name --dev
```

### Repository Integration
```bash
# Commit module to repository
git add modules/module-name/
git commit -m "feat: add module-name module v1.0.0"
```

### Version Updates
```bash
# Update module version
echo "1.1.0" > VERSION
# Update module.yaml version
# Update CHANGELOG.md
# Commit changes
git commit -m "chore: bump module-name to v1.1.0"
```

## Troubleshooting

### Common Issues

**Module Not Found**
- Verify module exists in correct category directory
- Check module.yaml syntax
- Ensure VERSION file exists

**Installation Fails**
- Check dependencies are available
- Verify file paths in installation mapping
- Test with `--dry-run` flag

**Skills Not Working**
- Verify skills exist in /skills/ directory
- Check manifests/bundles.yaml for correct mapping
- Ensure Claude Code has skills support enabled

**Conflicts During Installation**
- Review conflicts list in module.yaml
- Remove conflicting modules first
- Consider creating alternative module combinations

### Debug Commands
```bash
# Validate module metadata
acforge module validate ./modules/module-name

# Test installation without applying
acforge module install module-name --dry-run

# Verbose installation output
acforge module install module-name --verbose

# Check module dependencies
acforge module deps module-name
```

## Contributing Modules

### Submission Process
1. Follow module creation guidelines
2. Include comprehensive tests
3. Document all features and requirements
4. Submit pull request with module
5. Address review feedback

### Review Criteria
- Code quality and organization
- Documentation completeness
- Test coverage
- Version compatibility
- No conflicts with existing modules

### Maintenance
- Respond to issues and bug reports
- Keep dependencies updated
- Maintain compatibility with Claude Code updates
- Update documentation as needed