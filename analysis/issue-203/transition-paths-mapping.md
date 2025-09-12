# Source-to-Target Transition Paths Mapping

## Architecture Overview

### **Simplified Distribution Model**
- **Source**: `templates/` + `dist/` directories in ai-code-forge
- **Target**: Everything goes to `.acforge/` in target repository
- **Processing**: Templates get parameter substitution, dist content copied directly

## Complete Transition Path Mapping

### **1. Current Templates Directory → .acforge/**

**Source Path** | **Target Path** | **Processing** | **File Count**
---|---|---|---
`templates/prompts/` | `.acforge/prompts/` | Template processing | 2 files
`templates/guidelines/` | `.acforge/guidelines/` | Template processing | 12 files  
`templates/stacks/` | `.acforge/stacks/` | Template processing | 9 files
`templates/readme/` | `.acforge/readme/` | Template processing | 3 files
`templates/CLAUDE.md.template` | `.acforge/CLAUDE.md` | Template processing | 1 file
`templates/_devcontainer/` | `.devcontainer/` | Template processing | 23 files

**Total from templates/**: 50 files (30 to .acforge/ + 20 to .devcontainer/)

### **2. Scripts Directory → dist/scripts/ → .acforge/scripts/**

**Source Path** | **Target Path** | **Processing** | **File Count**
---|---|---|---
`scripts/*.sh` | `.acforge/scripts/*.sh` | Direct copy | 13 files
`scripts/lib/` | `.acforge/scripts/lib/` | Direct copy | 1 file
`scripts/worktree/` | `.acforge/scripts/worktree/` | Direct copy | 7 files
`scripts/tests/` | `.acforge/scripts/tests/` | Direct copy | 2 files
`scripts/README.md` | `.acforge/scripts/README.md` | Direct copy | 1 file

**Total from scripts/**: 24 files → **dist/scripts/** → `.acforge/scripts/`

### **3. MCP Servers Directory → dist/mcp-servers/ → .acforge/mcp-servers/**

**Source Path** | **Target Path** | **Processing** | **File Count**
---|---|---|---
`mcp-servers/mcp-config.json` | `.acforge/mcp-servers/mcp-config.json` | Direct copy | 1 file
`mcp-servers/README.md` | `.acforge/mcp-servers/README.md` | Direct copy | 1 file
`mcp-servers/openai-structured-mcp/` | `.acforge/mcp-servers/openai-structured-mcp/` | Direct copy | ~10 files
`mcp-servers/perplexity-mcp/` | `.acforge/mcp-servers/perplexity-mcp/` | Direct copy | ~10 files
`mcp-servers/tests/` | `.acforge/mcp-servers/tests/` | Direct copy | ~15 files

**Total from mcp-servers/**: ~37 files → **dist/mcp-servers/** → `.acforge/mcp-servers/`

## Complete Source → Target Mapping Summary

### **Templates Processing** (Parameter Substitution)
```
ai-code-forge/templates/prompts/           → target-repo/.acforge/prompts/
ai-code-forge/templates/guidelines/        → target-repo/.acforge/guidelines/
ai-code-forge/templates/stacks/            → target-repo/.acforge/stacks/
ai-code-forge/templates/readme/            → target-repo/.acforge/readme/
ai-code-forge/templates/CLAUDE.md.template → target-repo/.acforge/CLAUDE.md
ai-code-forge/templates/_devcontainer/      → target-repo/.devcontainer/
```

### **Dist Processing** (Direct Copy)
```
ai-code-forge/scripts/                     → ai-code-forge/dist/scripts/      → target-repo/.acforge/scripts/
ai-code-forge/mcp-servers/                 → ai-code-forge/dist/mcp-servers/  → target-repo/.acforge/mcp-servers/
```

## Target Repository Final Structure

After `acf init --force --github-owner=user --project-name=repo`:

```
target-repo/
├── .acforge/                              # Main AI Code Forge directory
│   ├── prompts/                          # From templates/ (processed)
│   │   ├── master-prompt.md
│   │   └── worktree-deliver.md
│   ├── guidelines/                       # From templates/ (processed)
│   │   ├── CLAUDE.md
│   │   ├── claude-agents-guidelines.md
│   │   ├── [10+ more guidelines]
│   │   └── stack-mapping.md
│   ├── stacks/                           # From templates/ (processed)
│   │   ├── python.md
│   │   ├── docker.md
│   │   ├── [7+ more stacks]
│   │   └── rust.md
│   ├── readme/                           # From templates/ (processed)
│   │   ├── general-project-template.md
│   │   ├── library-package-template.md
│   │   └── mcp-server-template.md
│   ├── scripts/                          # From dist/scripts/ (copied)
│   │   ├── launch-claude.sh
│   │   ├── launch-codex.sh
│   │   ├── analyze-jsonl.sh
│   │   ├── [10+ more scripts]
│   │   ├── lib/
│   │   │   └── launcher-utils.sh
│   │   ├── worktree/
│   │   │   ├── worktree-init.sh
│   │   │   ├── [6+ more worktree scripts]
│   │   │   └── tests/
│   │   └── tests/
│   ├── mcp-servers/                      # From dist/mcp-servers/ (copied)
│   │   ├── mcp-config.json
│   │   ├── README.md
│   │   ├── openai-structured-mcp/
│   │   ├── perplexity-mcp/
│   │   └── tests/
│   └── CLAUDE.md                         # From templates/CLAUDE.md.template (processed)
├── .devcontainer/                        # DevContainer (separate from .acforge)
│   ├── devcontainer.json
│   ├── Dockerfile
│   ├── postCreate.sh
│   ├── [3+ utility scripts]
│   └── postCreate-scripts/
│       └── [17+ setup scripts]
└── .acforge/                             # State management (created by CLI)
    └── state.json
```

## Implementation Requirements

### **Directory Restructure in ai-code-forge**

**Current**:
```
ai-code-forge/
├── templates/                            # ✅ Exists
├── scripts/                              # ❌ Move to dist/scripts/
└── mcp-servers/                          # ❌ Move to dist/mcp-servers/
```

**Target**:
```
ai-code-forge/
├── templates/                            # ✅ Keep (parameter processing)
└── dist/                                 # ❌ New directory
    ├── scripts/                          # ❌ Moved from root
    └── mcp-servers/                      # ❌ Moved from root
```

### **CLI Bundle Structure Update**

**Current Build**:
```bash
cp -r ../templates src/ai_code_forge_cli/templates
```

**New Build**:
```bash
cp -r ../templates src/ai_code_forge_cli/templates
cp -r ../dist src/ai_code_forge_cli/dist
```

### **Deployer Update**

**Current Deployment**:
- Templates → `.claude/` (WRONG - should be `.acforge/`)
- DevContainer templates → `.devcontainer/` (CORRECT)

**New Deployment**:
- Templates → `.acforge/` (EXCEPT devcontainer → `.devcontainer/`)
- Dist content → `.acforge/`

## File Count Summary

**Total Deployment**:
- **Templates**: 30 files to `.acforge/` + 23 files to `.devcontainer/` = 53 files
- **Dist Scripts**: 24 files to `.acforge/scripts/`  
- **Dist MCP**: 37 files to `.acforge/mcp-servers/`
- **Grand Total**: ~114 files deployed per `acf init`

## Critical Path Dependencies

### **1. Directory Restructure** (FIRST)
- Move `scripts/` → `dist/scripts/`
- Move `mcp-servers/` → `dist/mcp-servers/`

### **2. CLI System Update** (SECOND)  
- Update build script to copy `dist/` 
- Update deployer to handle `templates/` → `.acforge/` + `dist/` → `.acforge/`
- Fix current `.claude/` deployment to `.acforge/`

### **3. Target Path Correction** (CRITICAL)
- Current templates deploy to `.claude/` - should be `.acforge/`
- Only DevContainer templates should go to `.devcontainer/`

This mapping shows we need to fix the current deployment target AND add dist content distribution.