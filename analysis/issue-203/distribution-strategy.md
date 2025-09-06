# Static Content Distribution Strategy

## Architecture Overview

### **Dual Distribution System**
The CLI needs to handle **two distinct content types**:

1. **Templates** → Parameter processing → `.claude/`, `.devcontainer/`
2. **Static Content** → Direct copying → `scripts/`, `mcp-servers/`

## Implementation Strategy

### **CLI Bundle Structure Enhancement**

**Current Build Process**: 
```bash
# cli/build-with-templates.sh
cp -r ../templates src/ai_code_forge_cli/templates  # ✅ Templates
```

**Enhanced Build Process**:
```bash
# cli/build-with-templates.sh  
cp -r ../templates src/ai_code_forge_cli/templates     # ✅ Templates
cp -r ../scripts src/ai_code_forge_cli/static/scripts  # ❌ New: Static scripts
cp -r ../mcp-servers src/ai_code_forge_cli/static/mcp-servers  # ❌ New: Static MCP
```

### **Deployer Architecture Enhancement**

**Current**: Single `TemplateDeployer` class
**Proposed**: Dual deployment system

```python
class ContentDeployer:
    def __init__(self, target_path, template_manager, static_manager):
        self.template_deployer = TemplateDeployer(target_path, template_manager)
        self.static_deployer = StaticContentDeployer(target_path, static_manager)
    
    def deploy_all(self, parameters, dry_run=False):
        # Deploy parameterized templates
        template_results = self.template_deployer.deploy_templates(parameters, dry_run)
        
        # Deploy static content (no parameters)
        static_results = self.static_deployer.deploy_static_content(dry_run)
        
        # Merge results
        return merge_deployment_results(template_results, static_results)
```

### **StaticContentDeployer Implementation**

```python
class StaticContentDeployer:
    """Handles deployment of static content (scripts, MCP servers) to repository."""
    
    def __init__(self, target_path: Path, static_manager: StaticContentManager):
        self.target_path = target_path
        self.static_manager = static_manager
    
    def deploy_static_content(self, dry_run: bool = False) -> Dict[str, Any]:
        results = {
            "files_deployed": [],
            "directories_created": [],
            "errors": []
        }
        
        # Get all static files
        static_files = self.static_manager.list_static_files()
        
        for static_path in static_files:
            try:
                # Get content without processing
                content = self.static_manager.get_static_content(static_path)
                
                # Determine target path
                target_file_path = self._get_target_path(static_path)
                
                if not dry_run:
                    # Create parent directories
                    target_file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write file (no parameter substitution)
                    target_file_path.write_bytes(content)
                    
                    # Set executable permissions for shell scripts
                    if target_file_path.suffix == ".sh":
                        target_file_path.chmod(0o755)
                
                relative_path = target_file_path.relative_to(self.target_path)
                results["files_deployed"].append(str(relative_path))
                
            except Exception as e:
                results["errors"].append(f"Failed to deploy {static_path}: {e}")
        
        return results
    
    def _get_target_path(self, static_path: str) -> Path:
        """Convert static content path to target file path."""
        # static/scripts/launch-claude.sh → scripts/launch-claude.sh
        # static/mcp-servers/config.json → mcp-servers/config.json
        relative_path = static_path.replace("static/", "", 1)
        return self.target_path / relative_path
```

### **StaticContentManager Implementation**

```python
class StaticContentManager:
    """Manages static content resource access."""
    
    def __init__(self):
        self.static_package = "ai_code_forge_cli.static"
    
    def list_static_files(self) -> List[str]:
        """List all available static files."""
        static_files = []
        
        try:
            # Use importlib.resources to access bundled static content
            static_root = resources.files(self.static_package)
            self._collect_files_recursive(static_root, "", static_files)
        except (ImportError, FileNotFoundError):
            # Fallback to development mode
            dev_static = Path(__file__).parent.parent.parent.parent.parent / "scripts"
            if dev_static.exists():
                for file_path in dev_static.rglob("*"):
                    if file_path.is_file():
                        relative_path = f"static/scripts/{file_path.relative_to(dev_static)}"
                        static_files.append(relative_path)
                        
            # Also check mcp-servers
            dev_mcp = Path(__file__).parent.parent.parent.parent.parent / "mcp-servers" 
            if dev_mcp.exists():
                for file_path in dev_mcp.rglob("*"):
                    if file_path.is_file():
                        relative_path = f"static/mcp-servers/{file_path.relative_to(dev_mcp)}"
                        static_files.append(relative_path)
        
        return sorted(static_files)
    
    def get_static_content(self, static_path: str) -> bytes:
        """Get content of a static file (as bytes to preserve binary files)."""
        try:
            # Try bundled static content first
            static_root = resources.files(self.static_package)
            static_file = static_root / static_path.replace("static/", "", 1)
            
            if static_file.is_file():
                return static_file.read_bytes()
        except (ImportError, FileNotFoundError):
            pass
        
        # Fallback to development mode
        if static_path.startswith("static/scripts/"):
            dev_file = Path(__file__).parent.parent.parent.parent.parent / "scripts" / static_path.replace("static/scripts/", "", 1)
        elif static_path.startswith("static/mcp-servers/"):
            dev_file = Path(__file__).parent.parent.parent.parent.parent / "mcp-servers" / static_path.replace("static/mcp-servers/", "", 1)
        else:
            return None
            
        if dev_file.exists() and dev_file.is_file():
            return dev_file.read_bytes()
        
        return None
```

## Distribution Scope Decisions

### **HIGH PRIORITY: Scripts Directory** - FULL DISTRIBUTION
**Rationale**: Scripts provide essential workflow functionality
**Files**: All 17 shell scripts + subdirectories (lib/, worktree/, tests/)
**Size**: ~150KB total

### **MEDIUM PRIORITY: MCP Servers** - SELECTIVE DISTRIBUTION
**Assessment Needed**: Examine which MCP servers are universally useful vs ai-code-forge specific
**Initial**: Include mcp-config.json and universally useful servers

### **LOW PRIORITY: Documentation** - NO DISTRIBUTION
**Rationale**: Repository-specific, external repos create their own docs

## CLI Command Enhancement

### **Enhanced Init Command**
```bash
acf init --force --github-owner=testuser --project-name=test-repo
# Results:
# Templates deployed: 53 files (.claude/, .devcontainer/)
# Static content deployed: ~20 files (scripts/, mcp-servers/)
# Total deployment: ~73 files
```

### **Selective Distribution Options**
```bash
acf init --templates-only          # Only templates (current behavior)
acf init --static-only             # Only static content
acf init --no-scripts              # Skip scripts directory
acf init --no-mcp                  # Skip MCP servers
acf init                           # Full deployment (default)
```

## Validation Strategy

### **Dogfooding Enhancement**
**Test Command**: `acf init --force` in ai-code-forge repository
**Expected Results**:
- ✅ 53 template files with parameter substitution
- ✅ ~17 script files with executable permissions
- ✅ MCP server files with correct structure
- ✅ Directory hierarchy preserved (scripts/lib/, scripts/worktree/)

### **External Repository Validation**
**Test Setup**: Apply to clean external repository
**Validation Points**:
- Scripts work without modification
- MCP servers integrate correctly
- No ai-code-forge specific hardcoding breaks functionality
- File permissions preserved correctly

## Build Process Integration

### **Enhanced build-with-templates.sh**
```bash
#!/bin/bash
set -e

echo "🔧 Building AI Code Forge CLI with templates and static content..."

# Ensure we're in the CLI directory
cd "$(dirname "$0")"

# Copy templates for build (existing)
echo "📂 Copying templates for build..."
if [ -d "src/ai_code_forge_cli/templates" ]; then
    rm -rf src/ai_code_forge_cli/templates
fi
cp -r ../templates src/ai_code_forge_cli/templates

# Copy static content for build (NEW)
echo "📦 Copying static content for build..."
if [ -d "src/ai_code_forge_cli/static" ]; then
    rm -rf src/ai_code_forge_cli/static
fi
mkdir -p src/ai_code_forge_cli/static
cp -r ../scripts src/ai_code_forge_cli/static/scripts
cp -r ../mcp-servers src/ai_code_forge_cli/static/mcp-servers

# Build the package
echo "📦 Building package..."
uv build

# Clean up copied content
echo "🧹 Cleaning up temporary copies..."
rm -rf src/ai_code_forge_cli/templates
rm -rf src/ai_code_forge_cli/static

echo "✅ Build complete with templates and static content!"
```

This dual distribution strategy addresses the gap you identified: content that needs distribution but isn't template-based.