# Issue #205 Implementation Notes

## Implementation Priority and Sequence

### Phase 1 Implementation Order (Critical Path)
1. **`acf status`** - Foundation command (State inspection, validation framework)
2. **`acf init`** - Repository bootstrap (Template deployment, state creation)  
3. **`acf update`** - Template synchronization (Customization preservation, conflict resolution)

### Critical Implementation Dependencies
- Status command establishes state management patterns used by init/update
- Init command creates the state structure that status validates
- Update command requires both status and init functionality for conflict resolution

## Detailed Implementation Plan

### 1. Project Structure Setup
```
cli/
├── pyproject.toml              # Hatchling configuration with force-include
├── src/
│   └── ai_code_forge_cli/
│       ├── __init__.py
│       ├── cli.py              # Main Click CLI entry point
│       ├── commands/
│       │   ├── __init__.py
│       │   ├── status.py       # acf status implementation
│       │   ├── init.py         # acf init implementation
│       │   └── update.py       # acf update implementation
│       ├── core/
│       │   ├── __init__.py
│       │   ├── state.py        # State management with dataclasses
│       │   ├── templates.py    # Template resource access
│       │   └── validation.py   # Pydantic validation models
│       └── templates/          # Bundled template resources
└── tests/
    ├── conftest.py
    ├── test_status.py
    ├── test_init.py
    ├── test_update.py
    └── test_integration.py
```

### 2. pyproject.toml Configuration
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "ai-code-forge"
version = "3.0.0"  # Major version bump for breaking changes
description = "CLI for AI Code Forge template management"
requires-python = ">=3.9"  # REVISED: Broader compatibility
dependencies = [
    "click>=8.0.0",
    "pydantic>=2.0.0",
]

[project.scripts]
ai-code-forge = "ai_code_forge_cli.cli:main"
acf = "ai_code_forge_cli.cli:main"

[tool.hatch.build.targets.wheel.force-include]
"../../templates" = "ai_code_forge_cli/templates"
```

### 3. State Management Design (REVISED)

**CRITICAL DECISION CHANGE**: Based on critic agent analysis, implementing **single state file** approach:

```python
# .acf/state.json - Single atomic state file
{
    "version": "1.0",
    "installation": {
        "template_version": "1.2.3",
        "installed_at": "2025-08-28T10:30:00Z",
        "cli_version": "3.0.0"
    },
    "templates": {
        "checksum": "sha256:...",
        "files": {
            "agents/foundation-context.md": {
                "checksum": "sha256:...",
                "customized": false
            }
        }
    },
    "customizations": {
        "preserved_files": [".claude/agents/foundation-context.local.md"],
        "custom_overrides": {}
    }
}
```

**Benefits**: Atomic operations, consistency guarantees, simpler backup/restore

### 4. Template Resource Access Pattern
```python
from importlib import resources
import json
from pathlib import Path

def get_template_content(template_path: str) -> str:
    """Access bundled template content safely."""
    try:
        template_files = resources.files("ai_code_forge_cli.templates")
        template_file = template_files / template_path
        return template_file.read_text(encoding="utf-8")
    except (FileNotFoundError, AttributeError):
        # Fallback for development or edge cases
        dev_path = Path(__file__).parent.parent.parent / "templates" / template_path
        return dev_path.read_text(encoding="utf-8")
```

### 5. Command Implementation Strategy

#### `acf status` Command
**Purpose**: State inspection and validation foundation
**Key Features**:
- Repository configuration state detection
- Template drift analysis (compare local vs bundled)
- State file validation and consistency checking
- Output formats: human-readable and JSON

**Implementation Priority**: HIGH (Foundation for other commands)

#### `acf init` Command  
**Purpose**: Repository bootstrap with template deployment
**Key Features**:
- `.acf/` directory creation
- Template extraction from bundled resources
- Initial state file creation
- .gitignore updates

**Implementation Priority**: MEDIUM (Depends on status patterns)

#### `acf update` Command
**Purpose**: Template synchronization with customization preservation  
**Key Features**:
- Template version comparison
- .local file preservation during updates
- Conflict detection and resolution
- Change reporting

**Implementation Priority**: LOW (Most complex, requires status+init)

## Critical Implementation Considerations

### Error Handling Strategy
```python
from contextlib import contextmanager
from pathlib import Path
import json
from typing import Any, Dict

@contextmanager
def atomic_state_update(state_path: Path):
    """Ensure atomic state file updates."""
    backup_path = state_path.with_suffix('.json.backup')
    
    # Create backup if original exists
    if state_path.exists():
        shutil.copy2(state_path, backup_path)
    
    try:
        yield
    except Exception:
        # Restore backup on failure
        if backup_path.exists():
            shutil.copy2(backup_path, state_path)
        raise
    finally:
        # Clean up backup on success
        if backup_path.exists():
            backup_path.unlink()
```

### Cross-Platform Compatibility
- **Path Handling**: Exclusive pathlib usage for all file operations
- **Encoding**: UTF-8 encoding specification for all text operations
- **Permissions**: Proper file permission handling across Windows/Linux/macOS
- **Environment**: Platform-specific configuration location detection

### Testing Strategy
```python
# Integration testing approach with Click's CliRunner
from click.testing import CliRunner
import tempfile
from pathlib import Path

def test_acf_init_full_workflow():
    """Test complete init workflow with isolated filesystem."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Test init command
        result = runner.invoke(cli, ['init'])
        assert result.exit_code == 0
        
        # Verify state file creation
        state_path = Path('.acf/state.json')
        assert state_path.exists()
        
        # Verify template installation
        assert Path('.claude/agents/').exists()
```

## Risk Mitigation Strategies

### State Corruption Prevention
- **Atomic Operations**: Single state file with backup-restore pattern
- **Validation**: Pydantic schemas for all state data structures  
- **Checksums**: Template integrity verification
- **Recovery**: Automatic backup creation before modifications

### Template Bundling Scalability
- **Lazy Loading**: Load templates only when needed
- **Compression**: Consider template compression for large bundles
- **Selective Bundling**: Future capability for partial template sets

### Distribution Reliability
- **Dual Entry Points**: Both `ai-code-forge` and `acf` aliases
- **Version Detection**: CLI version validation and compatibility checking
- **Fallback Modes**: Development mode resource loading

## Validation and Testing Plan

### Self-Validation on ai-code-forge Repository
1. **Pre-implementation**: Document current `.claude/` structure
2. **Test `acf status`**: Verify detection of current configuration
3. **Test `acf init`**: Verify bootstrap capability in clean directory
4. **Test `acf update`**: Verify template synchronization

### Cross-Repository Testing
- Create test repositories with various configuration states
- Validate CLI behavior across different project structures
- Test edge cases: corrupted state, missing templates, permission issues

## Performance Optimization

### Startup Time Optimization
- **Lazy Imports**: Import heavy modules only when needed
- **Template Caching**: Cache template listing for repeated operations
- **Minimal Dependencies**: Keep dependency footprint small

### Resource Usage
- **Memory Efficiency**: Stream large template processing
- **Disk I/O**: Minimize filesystem operations
- **Network Absence**: No network dependencies for core operations

## Implementation Readiness Checklist

### Prerequisites ✅
- [x] Complete architecture analysis and decision rationale
- [x] Technology stack validation and guidelines
- [x] Risk assessment with mitigation strategies
- [x] Implementation plan with critical path analysis

### Before Starting Implementation
- [ ] Update GitHub issue with research summary and implementation plan
- [ ] Create development branch for CLI rewrite
- [ ] Document current CLI state for comparison
- [ ] Set up testing framework and validation scripts

### Development Milestones
- [ ] **Milestone 1**: `acf status` command with full state management
- [ ] **Milestone 2**: `acf init` command with template deployment
- [ ] **Milestone 3**: `acf update` command with customization preservation
- [ ] **Milestone 4**: Integration testing and self-validation
- [ ] **Milestone 5**: Documentation and packaging for distribution

## Agent Collaboration Notes

### Key Insights from Agent Collaboration
- **Context Agent**: Provided comprehensive codebase understanding
- **Stack-Advisor**: Enforced Python best practices and technology guidelines
- **Researcher**: Validated modern approaches with external sources
- **Critic Agent**: Identified critical risks and recommended course corrections

### Critical Course Corrections Applied
1. **Single State File**: Changed from three-file to single-file approach for atomicity
2. **Python Version**: Lowered requirement from 3.13+ to 3.9+ for broader compatibility
3. **Implementation Order**: Prioritized status command as foundation for others
4. **Error Handling**: Emphasized atomic operations and recovery mechanisms

### Ongoing Collaboration Points
- State management patterns established by status command
- Template resource access patterns for init/update commands
- Testing strategies validated across all three commands
- Performance optimization applied consistently