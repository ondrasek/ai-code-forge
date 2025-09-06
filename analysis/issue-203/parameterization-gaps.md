# Parameterization Gaps Analysis

## CRITICAL FINDING: CLI Works But Missing Key Templates

### CLI Functionality Status: ✅ **WORKING**

The CLI actually works correctly! Test results:
- ✅ Template discovery functional (27 templates found)
- ✅ Parameter detection working (detected "ondrasek" as GitHub owner)
- ✅ Deployment process functional (would create 27 files)
- ✅ Repository detection working (found git repository correctly)

### PRIMARY GAP: Missing DevContainer Template

**CRITICAL ISSUE**: The most important template for dogfooding is missing:

**Current**: `.devcontainer/devcontainer.json` contains hardcoded values:
```json
{
  "name": "AI Code Forge DevContainer",
  "runArgs": [
    "--label", "my.repositoryName=${localWorkspaceFolderBasename}"
  ],
  "workspaceFolder": "/workspace",
  "mounts": [
    "source=${localWorkspaceFolderBasename},target=/workspace,type=volume"
  ]
}
```

**Missing**: No `.devcontainer/devcontainer.json.template` exists in templates directory.

**Impact**: CLI can deploy 27 templates but cannot parameterize the most critical configuration for repository portability.

### Template Coverage Analysis

**Existing Templates (27 files)**:
- ✅ Guidelines (12 files)
- ✅ Stacks (9 files) 
- ✅ Prompts (2 files)
- ✅ README templates (3 files)
- ✅ Root CLAUDE.md (1 file)

**Missing Templates for Dogfooding**:
- ❌ `.devcontainer/devcontainer.json.template`
- ❌ `.devcontainer/Dockerfile.template` 
- ❌ `.devcontainer/postCreate.sh.template`
- ❌ Agent definitions (12+ files in `.claude/agents/`)
- ❌ Command definitions (40+ files in `.claude/commands/`)
- ❌ Settings (`settings.json` template)

### Parameter Substitution Assessment

**Current Parameter Discovery**: ✅ Working correctly
```python
# Detected parameters for ai-code-forge:
{
    "GITHUB_OWNER": "ondrasek",           # ✅ Correctly detected
    "PROJECT_NAME": "ai-code-forge",      # ✅ Correctly detected  
    "REPO_URL": "...",                    # ✅ Would be detected
    "CREATION_DATE": "2025-09-02T...",    # ✅ Generated correctly
    "ACF_VERSION": "3.0.0",               # ✅ Working
    "TEMPLATE_VERSION": "a1b2c3d4",       # ✅ Working
}
```

**Template Usage Assessment**: Limited parameter usage
- Only 1 template uses substitution: `templates/prompts/worktree-deliver.template.md`
- All other templates are static files with no parameters

### DevContainer Parameterization Requirements

For dogfooding ai-code-forge, DevContainer needs these parameters:

1. **Repository Name**: 
   - Current: hardcoded to work only with "ai-code-forge" basename
   - Template: `{{PROJECT_NAME}}` or `{{REPOSITORY_NAME}}`

2. **Container Name**:
   - Current: "AI Code Forge DevContainer" 
   - Template: "{{PROJECT_NAME}} DevContainer"

3. **Volume Mounts**:
   - Current: `${localWorkspaceFolderBasename}` assumes repository name
   - Template: `{{REPOSITORY_NAME}}` for explicit control

4. **Repository Labels**:
   - Current: `my.repositoryName=${localWorkspaceFolderBasename}`
   - Template: `my.repositoryName={{REPOSITORY_NAME}}`

### Implementation Priority

**HIGH PRIORITY (Blocks Dogfooding)**:
1. Create `.devcontainer/devcontainer.json.template` with repository parameterization
2. Add DevContainer templates to CLI bundle via build process
3. Test `acf init` creates working DevContainer for any repository name

**MEDIUM PRIORITY (Enhances Functionality)**:
4. Create Dockerfile and postCreate.sh templates with parameters
5. Add agent/command templates for complete configuration coverage
6. Enhance parameter schema with validation

### Validation Test for Dogfooding

Required test sequence:
```bash
# 1. Backup current configuration
mv .devcontainer .devcontainer.backup

# 2. Test CLI initialization with DevContainer template
acf init --force --github-owner=ondrasek --project-name=ai-code-forge

# 3. Verify DevContainer works correctly
# - Container name shows "ai-code-forge DevContainer" 
# - Repository labels contain correct values
# - Volume mounts work with repository name
# - All functionality preserved from original

# 4. Test external repository compatibility
cd /tmp && mkdir test-repo && cd test-repo && git init
acf init --github-owner=testuser --project-name=test-repo
# Should create DevContainer that works with "test-repo" name
```

## Conclusion

CLI is functional but missing the most critical template for dogfooding. Creating DevContainer template is the minimum viable implementation to validate Issue #203's template-first approach.