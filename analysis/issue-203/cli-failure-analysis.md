# CLI Failure Analysis for Issue #203

## CRITICAL FINDINGS: CLI is Completely Broken

### Primary Issue: Missing Templates Package

**ROOT CAUSE**: The CLI expects templates at `ai_code_forge_cli.templates` but no such package exists.

**Evidence from Code Analysis**:

1. **TemplateManager.py Line 22**: `self.template_package = "ai_code_forge_cli.templates"`
2. **build-with-templates.sh**: Temporarily copies `../templates` to `src/ai_code_forge_cli/templates` during build, then DELETES it
3. **Runtime Failure**: CLI cannot find templates when running in development mode

### Specific Failure Points

#### 1. Template Discovery Fails
```python
# In TemplateManager.list_template_files()
templates_root = resources.files(self.template_package)  # FAILS - package doesn't exist
# Falls back to:
dev_templates = Path(__file__).parent.parent.parent.parent.parent / "templates"
# This path is: cli/src/ai_code_forge_cli/core/../../../../../templates
# Which resolves to wrong location in worktree
```

#### 2. Repository Detection Issues
- `ACFContext.find_repo_root()` looks for `.git`, `.acforge`, `.claude` directories
- In worktree, `.git` file points to actual git directory, not a directory itself
- Path resolution fails when run from different contexts

#### 3. Parameter Substitution Gaps
Current parameters in `init.py`:
```python
parameters = {
    "GITHUB_OWNER": repo_info.get("github_owner", "{{GITHUB_OWNER}}"),  # Falls back to placeholder
    "PROJECT_NAME": repo_info.get("project_name", "{{PROJECT_NAME}}"),   # Falls back to placeholder  
    "REPO_URL": repo_info.get("repo_url", "{{REPO_URL}}"),               # Falls back to placeholder
    "CREATION_DATE": datetime.now().isoformat(),
    "ACF_VERSION": __version__,
    "TEMPLATE_VERSION": template_manager.calculate_bundle_checksum()[:8],
}
```

**Problem**: If repository detection fails, parameters contain unresolved `{{PLACEHOLDER}}` values.

#### 4. DevContainer Not Parameterized
- No DevContainer templates exist in current system
- `.devcontainer/devcontainer.json` is not templated at all
- Hard-coded "ai-code-forge" repository references cannot be parameterized

### Dogfooding Failure Scenarios

1. **Templates Missing**: `acf init` fails immediately - no templates found
2. **Parameter Resolution**: If templates were found, parameters would be `{{GITHUB_OWNER}}` instead of actual values
3. **DevContainer Skip**: No DevContainer template to apply
4. **Path Issues**: Template fallback paths incorrect in worktree context

### Required Fixes for Dogfooding

#### Immediate (High Priority)
1. **Fix Template Package**: Templates must be properly bundled or fallback paths fixed
2. **Parameter Detection**: Repository info detection must work in worktree context
3. **DevContainer Templates**: Create parameterized `.devcontainer/devcontainer.json.template`

#### Medium Priority  
4. **Path Resolution**: Fix development mode template discovery
5. **Repository Detection**: Handle git worktree `.git` files correctly
6. **Parameter Validation**: Ensure no `{{PLACEHOLDER}}` values in final output

### Template-First Requirements

To make CLI work for dogfooding ai-code-forge itself:

1. **DevContainer Parameterization**: Convert `.devcontainer/devcontainer.json` to template with:
   - `{{REPOSITORY_NAME}}` -> "ai-code-forge"
   - `{{GITHUB_OWNER}}` -> "ondrasek" 
   - `{{WORKSPACE_FOLDER}}` -> "/workspace"

2. **Template Distribution**: Fix build process to bundle templates OR fix development mode paths

3. **Self-Application Testing**: `acf init` should work when run inside ai-code-forge repository

### Validation Test

The dogfooding test should be:
```bash
cd /workspace/ai-code-forge
acf init --dry-run --verbose  # Should show what files would be created
acf init --force               # Should create working .claude/ configuration
```

Currently this fails at step 1 - template discovery.

## Conclusion

CLI is not just "broken for portability" - it's completely non-functional due to missing template package. Template-first architecture is mandatory to make CLI work at all, not just for portability improvements.

This validates Issue #203 completely - the CLI cannot be used for dogfooding in its current state.