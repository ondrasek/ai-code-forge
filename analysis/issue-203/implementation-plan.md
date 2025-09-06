# Template-First Architecture Implementation Plan

## TECHNICAL IMPLEMENTATION STRATEGY

Based on the decision rationale analysis, this document outlines the specific implementation approach for the Hybrid Template System (Solution Path C).

## CURRENT STATE ANALYSIS

### Existing Components:
- `TemplateManager`: Already has dual-path template access (bundled + development fallback)
- `RepositoryDetector`: Can detect git repository and configuration state
- `ACForgeState`: Tracks template versions and checksums
- Build system: `build-with-templates.sh` copies templates into CLI package

### Self-Hosting Pattern:
- Repository depends on generated `.claude/` directory
- Template changes require CLI rebuild + `acforge init` cycle
- Development workflow friction estimated at 2-3 minutes per iteration

## IMPLEMENTATION APPROACH

### Phase 1: Enhanced Mode Detection

**Extend RepositoryDetector with development mode detection:**

```python
class RepositoryDetector:
    def detect_development_mode(self) -> bool:
        """Detect if running in development mode (ai-code-forge repo)."""
        # Check if we're in the ai-code-forge repository
        # Check if templates/ directory exists with source templates
        # Verify git repository structure matches ai-code-forge
    
    def get_template_access_mode(self) -> TemplateAccessMode:
        """Determine appropriate template access mode."""
        # DEVELOPMENT: Direct template access for ai-code-forge development
        # PRODUCTION: Generated configuration for deployed repositories
        # BUNDLED: Fallback to bundled templates
```

**Template Access Mode Enumeration:**
```python
class TemplateAccessMode(Enum):
    DEVELOPMENT = "development"  # Direct /templates/ access
    PRODUCTION = "production"    # Generated .claude/ access  
    BUNDLED = "bundled"         # CLI-bundled templates
```

### Phase 2: Enhanced TemplateManager

**Extend existing TemplateManager with mode-aware access:**

```python
class TemplateManager:
    def __init__(self, access_mode: Optional[TemplateAccessMode] = None):
        self.access_mode = access_mode or self._detect_access_mode()
    
    def _detect_access_mode(self) -> TemplateAccessMode:
        """Auto-detect appropriate template access mode."""
        detector = RepositoryDetector(Path.cwd())
        return detector.get_template_access_mode()
    
    def get_template_content(self, template_path: str) -> Optional[str]:
        """Get template content using mode-appropriate access."""
        if self.access_mode == TemplateAccessMode.DEVELOPMENT:
            return self._get_development_template(template_path)
        elif self.access_mode == TemplateAccessMode.PRODUCTION:
            return self._get_production_template(template_path) 
        else:
            return self._get_bundled_template(template_path)
```

### Phase 3: Development Mode Template Processing

**Direct template access with parameter substitution:**

```python
def _get_development_template(self, template_path: str) -> Optional[str]:
    """Get template from development source with parameter handling."""
    dev_template_path = Path("templates") / template_path
    if not dev_template_path.exists():
        return None
    
    content = dev_template_path.read_text(encoding="utf-8")
    
    # Handle parameter substitution in development mode
    if template_path.endswith('.template'):
        # Apply parameter substitution for template files
        parameters = self._get_development_parameters()
        content = self._substitute_parameters(content, parameters)
    
    return content

def _get_development_parameters(self) -> Dict[str, str]:
    """Get parameters for development mode template substitution."""
    detector = RepositoryDetector(Path.cwd())
    repo_info = detector.detect_github_info()
    
    return {
        "GITHUB_OWNER": repo_info.get("github_owner", "ondrasek"),
        "PROJECT_NAME": repo_info.get("project_name", "ai-code-forge"), 
        "GITHUB_REPO": repo_info.get("github_repo", "ai-code-forge"),
        "CLI_DIRECTORY": "cli",
        # Add other development-specific parameters
    }
```

### Phase 4: Command Integration

**Update commands to respect template access modes:**

```python
@click.command("init")
@click.option("--mode", type=click.Choice(['auto', 'development', 'production', 'bundled']), 
              default='auto', help="Override template access mode")
def init_command(mode: str, **kwargs):
    """Initialize with mode-aware template access."""
    access_mode = TemplateAccessMode(mode) if mode != 'auto' else None
    template_manager = TemplateManager(access_mode)
    
    # Rest of init logic unchanged
```

**Enhanced status command with mode reporting:**

```python
@click.command("status")
def status_command(**kwargs):
    """Show repository status including template access mode."""
    template_manager = TemplateManager()
    
    click.echo(f"Template Access Mode: {template_manager.access_mode.value}")
    if template_manager.access_mode == TemplateAccessMode.DEVELOPMENT:
        click.echo("🔧 Development mode: Using direct template access")
        click.echo("📁 Template source: /templates/ directory")
    # ... rest of status display
```

## MIGRATION STRATEGY

### Backwards Compatibility
- Existing CLI behavior unchanged for production repositories
- Mode detection is automatic - no user action required
- Existing `acforge init` commands work identically

### Development Workflow Enhancement
- ai-code-forge developers get instant template iteration
- No more CLI rebuild cycle for template changes
- Template changes visible immediately via development mode

### Testing Strategy
- Unit tests for mode detection logic
- Integration tests for each template access mode
- End-to-end tests covering development workflow

## IMPLEMENTATION PRIORITIES

### High Priority: Core Mode Detection (blocks all other work)
- Implement `TemplateAccessMode` enum
- Extend `RepositoryDetector` with development mode detection
- Add mode detection to `TemplateManager` initialization

### High Priority: Development Mode Template Access (enables faster iteration)  
- Implement `_get_development_template()` method
- Add development parameter substitution
- Test template access across all modes

### Medium Priority: Command Integration (depends on core mode detection)
- Update `init` command with mode awareness
- Enhance `status` command with mode reporting
- Add mode override options for debugging

### Medium Priority: Enhanced Testing (depends on template access implementation)
- Mode-specific integration tests
- Template parameter substitution testing
- Bootstrap scenario testing

### Low Priority: Documentation and Tooling (depends on stable implementation)
- Update CLI documentation with mode behavior
- Create development mode troubleshooting guide
- Add mode detection to existing analysis tools

## VALIDATION CRITERIA

### Development Mode Success:
- Template changes visible in <5 seconds without CLI rebuild
- Parameter substitution works correctly in development mode
- ai-code-forge repository bootstrap works from clean state

### Production Mode Integrity:
- Existing user workflows unchanged
- Generated configuration matches previous behavior
- State tracking continues to work correctly

### Bootstrap Safety:
- ai-code-forge can develop and test its own template changes
- No circular dependency issues during development
- Clean separation between development and production concerns

## RISK MITIGATION

### Mode Detection Failures:
- Comprehensive fallback chain: development → production → bundled → error
- Clear error messages for mode detection issues
- Manual mode override capability for edge cases

### Parameter Substitution Issues:
- Validation of parameter completeness before template deployment
- Clear error reporting for missing or invalid parameters
- Consistent parameter handling across all modes

### Development/Production Inconsistencies:
- Automated testing ensures mode parity
- Template validation applies to all access modes
- State tracking works consistently across modes

## EXPECTED OUTCOMES

### For ai-code-forge Development:
- Template iteration time reduced from 2-3 minutes to <5 seconds
- Bootstrap paradox completely eliminated
- Enhanced development velocity for template improvements

### For End Users:
- Transparent operation - no behavior changes for existing workflows
- Improved reliability through better mode detection
- Enhanced CLI status reporting and debugging capabilities

### For Architecture:
- Clean separation between development and production concerns
- Elimination of self-hosting paradox through dual-mode operation
- Foundation for future template system enhancements