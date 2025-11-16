# Creating Claude Skills for AI Code Forge

## Skills Development Guide

This guide covers creating Claude Skills that integrate with AI Code Forge modules.

## Skill Structure

Every skill follows Claude's standard structure:

```
skills/category/skill-name/
├── SKILL.md                # Skill definition (required)
├── templates/              # Optional templates
├── examples/               # Optional examples
├── scripts/                # Optional executable scripts
└── README.md              # Skill documentation
```

## Skill Definition (SKILL.md)

### YAML Frontmatter
```yaml
---
name: skill-name
version: 1.0.0
description: "Brief description of skill functionality"
category: development | documentation | workflow
compatibility:
  modules:                  # Compatible modules
    - python
    - typescript
  claude-code: ">=2.78.0"
dependencies:               # Optional dependencies
  claude-code: ">=2.78.0"
---
```

### Skill Instructions
```markdown
# Skill Name

Brief description of what this skill does and when to use it.

## Purpose

Detailed explanation of the skill's purpose and capabilities.

## Usage

How Claude should use this skill, including trigger conditions.

## Examples

Provide examples of when and how this skill should be activated.
```

## Skill Categories

### development
Code analysis, testing, and development assistance:
- Code review and quality analysis
- Language-specific linting and suggestions
- Testing strategy and test generation
- Architecture and design guidance

### documentation
Documentation creation and maintenance:
- README generation and updates
- API documentation creation
- Code commenting assistance
- Changelog generation

### workflow
Development process and workflow assistance:
- Git workflow guidance
- CI/CD pipeline assistance
- Deployment guidance
- Project structure recommendations

## Progressive Disclosure

Skills leverage Claude's progressive disclosure mechanism:

1. **Metadata Loading**: Name and description loaded at startup
2. **Skill Activation**: Full SKILL.md loaded when needed
3. **Resource Loading**: Additional files loaded on demand
4. **Script Execution**: Executable scripts run without loading into context

## Templates and Resources

### Template Files
```
templates/
├── readme-template.md
├── api-docs-template.md
└── test-template.py
```

### Reference Materials
```
examples/
├── good-examples/
├── bad-examples/
└── best-practices.md
```

### Executable Scripts
```
scripts/
├── analyze-code.py
├── generate-docs.sh
└── check-quality.js
```

## Integration with Modules

### M:N Relationships
Skills can be used by multiple modules:

```yaml
# manifests/bundles.yaml
python:
  skills:
    - python-linting        # Python-specific
    - code-review          # Shared
    - architecture-advisor # Shared

typescript:
  skills:
    - typescript-analysis  # TypeScript-specific
    - code-review          # Shared (same skill)
    - architecture-advisor # Shared (same skill)
```

### Skill Compatibility
```yaml
# skills/development/code-review/SKILL.md frontmatter
compatibility:
  modules:
    - python
    - typescript
    - rust
    - java
  requirements:
    - "Source code files present"
    - "Git repository initialized"
```

## Development Workflow

### 1. Skill Planning
- Identify specific use case
- Define trigger conditions
- Plan integration with modules
- Consider reusability across technologies

### 2. Skill Creation
```bash
# Create skill structure
mkdir -p skills/development/my-skill
cd skills/development/my-skill

# Create SKILL.md
cat > SKILL.md << 'EOF'
---
name: my-skill
version: 1.0.0
description: "Description of skill functionality"
category: development
compatibility:
  modules:
    - python
    - typescript
---

# My Skill

Detailed skill implementation...
EOF
```

### 3. Template Development
```bash
# Add templates if needed
mkdir templates
cat > templates/example-template.md << 'EOF'
# Template content
EOF
```

### 4. Documentation
```bash
# Document skill
cat > README.md << 'EOF'
# My Skill

## Purpose
What this skill does

## Integration
Which modules use this skill

## Usage
How Claude activates and uses this skill
EOF
```

## Best Practices

### Skill Design
- **Clear Purpose**: Single, well-defined responsibility
- **Trigger Conditions**: Clear activation criteria
- **Context Awareness**: Understand when skill is relevant
- **Resource Efficiency**: Minimal context window usage

### Progressive Disclosure
- **Metadata Only**: Essential info in frontmatter
- **Load on Demand**: Additional resources when needed
- **Script Execution**: Use scripts for processing without loading code
- **Context Preservation**: Don't pollute context unnecessarily

### Cross-Module Compatibility
- **Generic Design**: Work across multiple technologies
- **Configuration Awareness**: Adapt to different project structures
- **Graceful Degradation**: Work even when some resources unavailable
- **Clear Dependencies**: Document requirements explicitly

## Skill Types

### Technology-Specific Skills
```yaml
---
name: python-linting
category: development
compatibility:
  modules: [python]
---

# Python Linting Skill

Provides Python-specific code analysis and linting suggestions.

## Activation
- Python files present (.py extension)
- Python module installed
- Code review or quality analysis requested

## Capabilities
- PEP 8 compliance checking
- Type hint suggestions
- Import optimization
- Security vulnerability detection
```

### Generic Skills
```yaml
---
name: code-review
category: development
compatibility:
  modules: [python, typescript, rust, java]
---

# Code Review Skill

Provides language-agnostic code review and quality analysis.

## Activation
- Code review requested
- Pull request analysis needed
- Quality assessment requested

## Capabilities
- Code structure analysis
- Best practices checking
- Performance considerations
- Security review
```

### Documentation Skills
```yaml
---
name: readme-generator
category: documentation
compatibility:
  modules: [python, typescript, rust, java, all]
---

# README Generator Skill

Creates comprehensive README files for projects.

## Activation
- README creation requested
- Documentation update needed
- New project initialization

## Capabilities
- Project description generation
- Installation instructions
- Usage examples
- Contributing guidelines
```

## Testing Skills

### Manual Testing
```bash
# Install skill with module
acforge module install python  # Includes python skills

# Test skill activation
# Use Claude Code with Python project
# Verify skill triggers appropriately
```

### Automated Testing
```bash
# Create test cases
mkdir tests
cat > tests/test-skill.sh << 'EOF'
#!/bin/bash
# Test skill installation and activation
EOF
```

## Skill Distribution

### Module Bundling
Skills are distributed as part of modules via manifests:

```yaml
# manifests/bundles.yaml
python:
  skills:
    - python-linting
    - python-testing
    - code-review

# Users get skills automatically with module
acforge module install python
```

### Cross-Platform Sync
```bash
# Sync skills to Claude platforms
acforge skills sync

# Platform-specific installation
acforge skills install my-skill --platform claude-code
acforge skills install my-skill --platform claude-api
```

## Advanced Features

### Conditional Logic
```markdown
# In SKILL.md
## Activation Conditions

This skill activates when:
- Python files are present AND
- Testing is requested OR
- Test files need generation

Use the following logic to determine activation...
```

### Resource References
```markdown
# Load additional resources
For detailed examples, see examples/best-practices.md
For templates, use templates/test-template.py
For analysis scripts, run scripts/analyze-tests.py
```

### Script Integration
```markdown
# Execute analysis script
To analyze test coverage:
1. Run scripts/coverage-analysis.py
2. Use output to provide suggestions
3. Don't load script content into context
```

## Troubleshooting

### Common Issues

**Skill Not Activating**
- Check compatibility with installed modules
- Verify trigger conditions are met
- Review skill name in module bundles

**Skills Not Syncing**
- Check Claude platform connectivity
- Verify skill format compliance
- Review platform-specific requirements

**Context Window Overflow**
- Reduce skill instruction length
- Use progressive disclosure patterns
- Move large content to separate files

### Debug Commands
```bash
# List installed skills
acforge skills list

# Check skill status
acforge skills status my-skill

# Validate skill format
acforge skills validate ./skills/category/skill-name

# Test skill installation
acforge skills install my-skill --dry-run
```

## Migration from Templates

### Converting Template Logic
```bash
# Old template approach
# Static files with hardcoded logic

# New skills approach
# Dynamic AI assistance with context awareness
```

### Preserving Functionality
- Move static templates to skill templates/
- Convert logic to skill instructions
- Add progressive disclosure patterns
- Test with multiple project types

## Contributing Skills

### Submission Guidelines
1. Follow skill structure requirements
2. Include comprehensive documentation
3. Test with multiple modules
4. Provide clear activation criteria
5. Consider cross-module compatibility

### Review Process
- Code quality assessment
- Documentation review
- Compatibility testing
- Performance evaluation
- Integration testing

### Maintenance
- Monitor skill performance
- Update for Claude platform changes
- Respond to user feedback
- Maintain module compatibility