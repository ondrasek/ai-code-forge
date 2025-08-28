---
description: Create semantic version tag from commit analysis with automatic version determination, pyproject.toml synchronization, and tag creation (main branch only).
argument-hint: Optional version type (auto|major|minor|patch) - defaults to auto.
allowed-tools: Task(git-workflow), Read, Edit, Write, Bash(git status), Bash(git log), Bash(git tag), Bash(git push)
---

# Tag Creation Command

!`git status`
!`git branch --show-current`
!`git tag --list | tail -5`

Create semantic version tag from commit analysis with automatic version determination, pyproject.toml synchronization, and tag creation. **MAIN BRANCH ONLY.**

**CRITICAL**: This command automatically synchronizes ALL version-bearing files (pyproject.toml AND __init__.py) across all components to match the repository tag before creating the tag, ensuring comprehensive version consistency.

## Instructions

1. **Branch Validation (CRITICAL)**:
   ```bash
   CURRENT_BRANCH=$(git branch --show-current)
   if [[ "$CURRENT_BRANCH" != "main" ]]; then
       echo "❌ ERROR: /tag command only works on main branch"
       echo "Current branch: $CURRENT_BRANCH"
       echo "Switch to main branch: git checkout main"
       exit 1
   fi
   ```

2. **Parse Arguments**: Determine version type from $ARGUMENTS
   - `auto` (default): Automatically detect version bump from recent commits
   - `major`: Force major version bump (x.0.0) 
   - `minor`: Force minor version bump (0.x.0)
   - `patch`: Force patch version bump (0.0.x)

3. **Analyze Recent Commits**: Scan commits since last tag for version determination
   ```bash
   # Get last version tag
   LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
   
   # Analyze commit messages since last tag
   COMMITS=$(git log "$LAST_TAG"..HEAD --oneline --grep="feat:" --grep="fix:" --grep="break:" --grep="BREAKING")
   
   # Categorize commits:
   # - feat: → MINOR version
   # - fix: → PATCH version  
   # - BREAKING/break: → MAJOR version
   # - docs:/refactor:/test:/chore: → PATCH version
   ```

4. **Version Bump Logic**:
   ```
   MAJOR (x.0.0): Any BREAKING changes or "break:" commits found
   MINOR (0.x.0): Any "feat:" commits found (if no MAJOR)
   PATCH (0.0.x): Only "fix:", "docs:", "refactor:", "test:", "chore:" commits
   ```

5. **Calculate Next Version**:
   ```bash
   IFS='.' read MAJOR MINOR PATCH <<< "${LAST_TAG#v}"
   case "$VERSION_TYPE" in
     "major") NEXT_VERSION="v$((MAJOR + 1)).0.0" ;;
     "minor") NEXT_VERSION="v$MAJOR.$((MINOR + 1)).0" ;;
     "patch") NEXT_VERSION="v$MAJOR.$MINOR.$((PATCH + 1))" ;;
   esac
   ```

6. **Generate Tag Message**:
   ```bash
   TAG_MESSAGE="Release $NEXT_VERSION

   Previous Version: $LAST_TAG
   
   Changes in this release:
   $(git log "$LAST_TAG"..HEAD --oneline --pretty="- %s")
   
   📋 Full changelog: https://github.com/ondrasek/ai-code-forge/compare/$LAST_TAG...$NEXT_VERSION"
   ```

7. **Synchronize All Version-Bearing Files** (CRITICAL - Before Tagging):
   ```bash
   # Use comprehensive sync script to update ALL version-bearing files
   echo "📦 Synchronizing all version-bearing files to $NEXT_VERSION..."
   
   # Remove 'v' prefix for version number
   VERSION_NUMBER="${NEXT_VERSION#v}"
   
   # Run comprehensive version synchronization script
   if [ -f "scripts/sync-versions.sh" ]; then
     echo "🔄 Running comprehensive version synchronization..."
     ./scripts/sync-versions.sh "$VERSION_NUMBER"
     echo "✅ All version-bearing files synchronized to $VERSION_NUMBER"
   else
     echo "❌ ERROR: scripts/sync-versions.sh not found"
     echo "Cannot synchronize versions automatically"
     exit 1
   fi
   ```

8. **Commit Version Updates** (CRITICAL - Before Tagging):
   ```bash
   # Stage all version-bearing files that may have been updated
   echo "📝 Staging version-bearing files for commit..."
   git add -A '*.toml' '**/__init__.py'
   
   # Check if there are changes to commit
   if git diff --cached --quiet; then
     echo "ℹ️ No version changes to commit"
   else
     echo "📝 Committing comprehensive version synchronization..."
     git commit -m "chore: synchronize all version-bearing files to $NEXT_VERSION

🔖 Preparing for release $NEXT_VERSION
- Synchronized all pyproject.toml files to $VERSION_NUMBER
- Synchronized all __init__.py files to $VERSION_NUMBER  
- Applied comprehensive version consistency across all components

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
     echo "✅ Comprehensive version synchronization committed"
   fi
   ```

9. **Create and Push Tag**:
   ```bash
   echo "🏷️ Creating tag: $NEXT_VERSION"
   git tag -a "$NEXT_VERSION" -m "$TAG_MESSAGE"
   
   echo "📤 Pushing commits and tag to origin..."
   git push origin main
   git push origin "$NEXT_VERSION"
   
   echo "✅ Tag created and pushed: $NEXT_VERSION"
   echo "📦 All version-bearing files synchronized to version $VERSION_NUMBER"
   echo "🚀 GitHub Actions workflow will now trigger for release"
   ```

## Security Validations

**Pre-Tag Checks (MANDATORY)**:
- ✅ Must be on main branch
- ✅ Working directory must be clean (no uncommitted changes)
- ✅ Must be up-to-date with origin/main
- ✅ Tag name must not already exist
- ✅ Must have commits since last tag
- ✅ Version synchronization script must exist and be executable
- ✅ All version-bearing files must be synchronized before tag creation

## Automatic Version Detection

Scans commit messages since last release:

```
MAJOR (x.0.0): Any commits with:
  - "break:" prefix
  - "BREAKING CHANGE:" in message
  - API removal or major architectural changes
  
MINOR (0.x.0): Any commits with:
  - "feat:" prefix (new features)
  - New commands, agents, or significant functionality
  
PATCH (0.0.x): Only commits with:
  - "fix:" prefix (bug fixes)
  - "docs:" prefix (documentation)
  - "refactor:", "test:", "chore:" prefixes
```

## Integration with Release Workflow

This command triggers the complete release automation:

1. **Comprehensive Version Synchronization**: Updates ALL version-bearing files (pyproject.toml + __init__.py) to match new tag version
2. **Version Commit**: Commits all synchronized version changes with proper commit message
3. **Tag Creation**: `/tag` creates and pushes version tag referencing updated files
4. **GitHub Actions**: Tag push triggers `ai-code-forge-release.yml` workflow
5. **Automated Pipeline**: 
   - Build and test packages with synchronized versions
   - Create GitHub release with assets
   - Publish to PyPI via OIDC with Sigstore attestations
   - Generate build summary

## Error Handling

- **Not on main branch**: Command exits with error and instructions
- **Uncommitted changes**: Must clean working directory first  
- **No commits since last tag**: Reports no changes to release
- **Tag already exists**: Prevents duplicate tag creation
- **Network/push failures**: Provides manual commands for retry

## Example Usage

```bash
# Automatic version detection (recommended)
/tag

# Force specific version type
/tag major
/tag minor  
/tag patch
```

## Expected Outcomes

- **Comprehensive version synchronization** across all version-bearing files (pyproject.toml + __init__.py)
- **Version commit** with standardized commit message
- **Semantic version tag** created based on commit analysis  
- **Tag pushed to origin** triggering GitHub Actions workflow
- **Complete release pipeline** automatically executed
- **PyPI packages published** with synchronized versions and Sigstore attestations
- **GitHub release created** with assets and changelog

## Security Features

- **Main branch restriction**: Prevents accidental releases from feature branches
- **Clean working directory**: Ensures no uncommitted changes in release
- **Tag uniqueness**: Prevents duplicate version tags
- **OIDC Publishing**: Secure PyPI publishing without API keys
- **Sigstore Attestations**: Cryptographic package signing for supply chain security

## Related Commands

- `/issue start` - Start GitHub issue implementation
- `/issue pr` - Create pull request for completed work
- Git workflow commands for commit management