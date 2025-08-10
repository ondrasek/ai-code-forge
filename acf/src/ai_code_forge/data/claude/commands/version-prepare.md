---
description: Analyze completed TODOs and prepare version release with automatic CHANGELOG generation.
argument-hint: Optional version type (auto|major|minor|patch) - defaults to auto.
allowed-tools: Task(github-issues-workflow), Task(git-workflow), Read, Edit, Write, Bash(git status), Bash(git log), Bash(git tag)
---

# Version Release Preparation

Analyze completed TODOs and prepare version release with automatic CHANGELOG generation.

## Instructions

1. **Parse Arguments**: Determine version type from $ARGUMENTS
   - `auto` (default): Automatically detect version bump based on completed GitHub Issues
   - `major`: Force major version bump (x.0.0)
   - `minor`: Force minor version bump (0.x.0)
   - `patch`: Force patch version bump (0.0.x)

2. **Analyze Completed Issues**: 
   ```
   Task(github-issues-workflow): Analyze completed GitHub Issues since last release
   - Categorize by type (feat/fix/break/docs/chore)
   - Extract completion status and impact assessment
   - Return clean summary for version determination
   ```

3. **Calculate Version Bump**: Based on issue analysis
   - Any `break` or breaking change issues → MAJOR version
   - Any `feat` or new feature issues → MINOR version  
   - Only `fix`/`docs`/`perf`/`refactor`/`test`/`chore` → PATCH version

4. **Execute Version Preparation**:
   ```
   Task(git-workflow): Prepare version release with parameters:
   - Version type: [determined from analysis]
   - CHANGELOG entries: [from completed issues]
   - Tag preparation and release commit creation
   ```

## Error Handling

- **No completed issues**: Report no changes warrant version bump
- **Invalid version argument**: Default to `auto` with warning
- **Git repository issues**: Delegate to git-workflow agent for resolution

## Automatic Version Detection

The system scans completed TODOs since the last release:

```
MAJOR (x.0.0): Any `break` type tasks found
MINOR (0.x.0): Any `feat` type tasks found (if no MAJOR)
PATCH (0.0.x): Only maintenance tasks found
```

## CHANGELOG Generation

Completed TODOs are converted to CHANGELOG entries:

### Task Type → CHANGELOG Section Mapping
- `feat` → "### Added"
- `fix` → "### Fixed"
- `break` (removing features) → "### Removed"
- `break` (changing behavior) → "### Changed"
- `docs` → "### Changed" (if user-facing)
- `perf` → "### Changed"
- `refactor` → Usually excluded from user-facing changelog
- `test`, `chore` → Usually excluded

### Entry Format
```markdown
## [1.2.3] - 2024-01-28

### Added
- New feature description from feat TODO
  - Additional implementation details
  - TODO reference: #task-1

### Fixed  
- Bug fix description from fix TODO
  - TODO reference: #task-3
```

## Release Preparation Steps

1. **Version Calculation**: Determine new version number
2. **CHANGELOG Update**: Generate entries from completed TODOs
3. **Archive Cleanup**: Move completed TODOs from archive to CHANGELOG
4. **Version Commit**: Create commit with version bump
5. **Tag Preparation**: Prepare annotated git tag command

## Files Updated

- `CHANGELOG.md`: Add new version section with entries
- `TODO.md`: Clear completed tasks from archive section
- Any version files (package.json, etc.) if present

## Integration with Git Workflow

Following trunk-based development and CLAUDE.md Rule 1 compliance:
1. All changes committed to main branch via git-workflow agent
2. Version tag created with proper annotation
3. Automatic push to origin with tag

## Expected Outcomes

- Accurate semantic version determination
- Comprehensive CHANGELOG.md updates from completed issues
- Proper git tag creation with release notes
- Clean main context with complex processing isolated to specialist agents

## Related Commands

- `/git` - Execute git workflow after version preparation
- `/issue/cleanup` - Clean completed issues before version preparation