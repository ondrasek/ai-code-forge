# Versioning Guidelines

This project follows **Semantic Versioning (SemVer)**.

## Version Number Format
`MAJOR.MINOR.PATCH`

## When to Increment

### MAJOR (breaking changes)
- Removing features
- Changing configurations incompatibly
- Breaking API changes
- Removing deprecated functionality

### MINOR (new features)
- Adding agents
- Adding commands
- New capabilities
- New optional features
- Deprecating functionality (but not removing)

### PATCH (fixes)
- Bug fixes
- Typos
- Small improvements
- Documentation updates
- Performance improvements

## Versioning Process

### Trunk-Based Release Process
1. Ensure all changes are committed and pushed to main
2. Update version in CHANGELOG.md
3. Commit version update: `git commit -m "Release version 1.2.3"`
4. Create annotated tag on main: `git tag -a v1.2.3 -m "Release version 1.2.3"`
5. Push changes and tag:
   ```bash
   git push origin main
   git push origin v1.2.3
   ```

### Important Notes
- **NO release branches**: Tag releases directly on main
- **Tags are immutable**: Once pushed, never modify a tag
- **Continuous deployment**: Every commit to main should be releasable

## CHANGELOG Format

```markdown
## [1.2.3] - 2024-01-20

### Added
- New feature descriptions

### Changed
- Modified behavior descriptions

### Fixed
- Bug fix descriptions

### Removed
- Removed feature descriptions
```

## Pre-release Versions
- Alpha: `1.0.0-alpha.1`
- Beta: `1.0.0-beta.1`
- Release Candidate: `1.0.0-rc.1`

## Integration with TODO Protocol

This versioning process integrates with the comprehensive TODO/CHANGELOG protocol:

### Automatic Version Detection
- Version bumps are calculated based on completed TODO task types
- `break` tasks → MAJOR version
- `feat` tasks → MINOR version
- `fix`/`docs`/`perf`/`refactor`/`test`/`chore` tasks → PATCH version

### CHANGELOG Integration
- Completed TODOs automatically generate CHANGELOG entries
- Task types map to CHANGELOG sections (Added/Fixed/Changed/Removed)
- Full traceability from TODO to release documentation

### Commands Available
- `/todo:todo-create [type] [priority] "description"` - Add new TODO task
- `/todo:todo-review` - Review and manage existing TODO tasks
- `/version-prepare [auto|major|minor|patch]` - Prepare release

This TODO/CHANGELOG integration is handled automatically by the system agents.