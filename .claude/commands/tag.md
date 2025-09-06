---
description: Create semantic version tag with automatic version determination and tag creation (main branch only)
argument-hint: Optional version type (auto|major|minor|patch) - defaults to auto
allowed-tools: Bash, Task(git-workflow)
---

# Tag Creation Command

!`git status`
!`git branch --show-current`
!`git tag --list | tail -5`

## Execution Steps

### 1. Validate Branch and State
```bash
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "main" ]]; then
    echo "❌ ERROR: Must be on main branch (currently: $CURRENT_BRANCH)"
    exit 1
fi

if ! git diff --quiet || ! git diff --staged --quiet; then
    echo "❌ ERROR: Working directory must be clean"
    exit 1
fi
```

### 2. Parse Arguments and Determine Version Type
```bash
VERSION_TYPE="${ARGUMENTS:-auto}"

if [[ "$VERSION_TYPE" == "auto" ]]; then
    LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
    
    # Check for breaking changes
    if git log "$LAST_TAG"..HEAD --oneline | grep -E "(break:|BREAKING)"; then
        VERSION_TYPE="major"
    # Check for features
    elif git log "$LAST_TAG"..HEAD --oneline | grep "feat:"; then
        VERSION_TYPE="minor"
    # Default to patch
    else
        VERSION_TYPE="patch"
    fi
fi
```

### 3. Calculate Next Version
```bash
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
IFS='.' read -r MAJOR MINOR PATCH <<< "${LAST_TAG#v}"

case "$VERSION_TYPE" in
    "major") NEXT_VERSION="v$((MAJOR + 1)).0.0" ;;
    "minor") NEXT_VERSION="v$MAJOR.$((MINOR + 1)).0" ;;
    "patch") NEXT_VERSION="v$MAJOR.$MINOR.$((PATCH + 1))" ;;
    *) echo "❌ ERROR: Invalid version type: $VERSION_TYPE"; exit 1 ;;
esac

# Check if tag already exists
if git tag --list | grep -q "^$NEXT_VERSION$"; then
    echo "❌ ERROR: Tag $NEXT_VERSION already exists"
    exit 1
fi

echo "🏷️ Next version: $NEXT_VERSION (type: $VERSION_TYPE)"
```

### 4. Generate Tag Message
```bash
TAG_MESSAGE="Release $NEXT_VERSION

Previous Version: $LAST_TAG

Changes in this release:
$(git log "$LAST_TAG"..HEAD --oneline --pretty="- %s")

📋 Full changelog: https://github.com/ondrasek/ai-code-forge/compare/$LAST_TAG...$NEXT_VERSION"
```

### 5. Create and Push Tag
```bash
echo "📦 Note: Version synchronization will happen automatically via GitHub Actions"
echo ""

echo "🏷️ Creating tag: $NEXT_VERSION"
git tag -a "$NEXT_VERSION" -m "$TAG_MESSAGE"

echo "📤 Pushing tag to origin..."
git push origin "$NEXT_VERSION"

echo "✅ Tag created and pushed: $NEXT_VERSION"
echo "🚀 GitHub Actions will now sync versions and create release"
```

## Error Conditions
- Not on main branch → exit 1
- Uncommitted changes → exit 1  
- Tag already exists → exit 1
- No commits since last tag → continue with patch version