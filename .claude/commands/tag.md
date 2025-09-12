---
description: Create semantic version tag with automatic version determination and tag creation (main branch only)
argument-hint: Optional version type (auto|major|minor|patch) - defaults to auto
allowed-tools: Bash, Task(git-workflow)
---

!`git status`
!`git branch --show-current`
!`git tag --list | tail -5`

## Execution Sequence

1. **Validate Branch**
   - Execute: `git branch --show-current`
   - Requirement: Output must be "main"
   - If not "main": Exit with error

2. **Validate Working Directory**
   - Execute: `git diff --quiet`
   - Execute: `git diff --staged --quiet`
   - Requirement: Both must succeed (exit code 0)
   - If either fails: Exit with error

3. **Get Version Type**
   - Parse ARGUMENTS variable
   - If empty or "auto": Set VERSION_TYPE = "auto"
   - If "major|minor|patch": Set VERSION_TYPE = argument value
   - If invalid: Exit with error

4. **Get Last Tag**
   - Execute: `git describe --tags --abbrev=0`
   - If fails: Set LAST_TAG = "v0.0.0"
   - If succeeds: Set LAST_TAG = output

5. **Determine Version Type (if auto)**
   - If VERSION_TYPE != "auto": Skip this step
   - Execute: `git log LAST_TAG..HEAD --oneline`
   - If output contains "break:" or "BREAKING": Set VERSION_TYPE = "major"
   - Else if output contains "feat:": Set VERSION_TYPE = "minor"  
   - Else: Set VERSION_TYPE = "patch"

6. **Calculate Next Version**
   - Parse LAST_TAG to extract MAJOR.MINOR.PATCH (remove 'v' prefix)
   - If VERSION_TYPE = "major": NEXT_VERSION = "v{MAJOR+1}.0.0"
   - If VERSION_TYPE = "minor": NEXT_VERSION = "v{MAJOR}.{MINOR+1}.0"
   - If VERSION_TYPE = "patch": NEXT_VERSION = "v{MAJOR}.{MINOR}.{PATCH+1}"

7. **Validate Tag Uniqueness**
   - Execute: `git tag --list`
   - If NEXT_VERSION exists in output: Exit with error

8. **Generate Tag Message**
   - Execute: `git log LAST_TAG..HEAD --oneline --pretty="- %s"`
   - Build message:
     ```
     Release NEXT_VERSION
     
     Previous Version: LAST_TAG
     
     Changes in this release:
     {commit log output}
     
     Full changelog: https://github.com/ondrasek/ai-code-forge/compare/LAST_TAG...NEXT_VERSION
     ```

9. **Create Tag**
   - Execute: `git tag -a NEXT_VERSION -m "TAG_MESSAGE"`

10. **Push Tag**
    - Execute: `git push origin NEXT_VERSION`
    - Output: "Tag created and pushed: NEXT_VERSION"