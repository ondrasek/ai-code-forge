<acforge_technical_requirements>
<critical_constraints>
MANDATORY REQUIREMENT 0: Python 3.14+ ONLY. NEVER use features from older Python versions as compatibility target.
MANDATORY REQUIREMENT 1: ALL configuration MUST use Pydantic models serialized to YAML. NEVER use JSON or TOML.
MANDATORY REQUIREMENT 2: ALL CLI commands MUST use Typer with type hints. NEVER use argparse or plain Click.
MANDATORY REQUIREMENT 3: File merging MUST use Strategy Pattern. NEVER implement merge logic inline.
MANDATORY REQUIREMENT 4: ALL code MUST pass MyPy strict mode. NEVER commit code with type errors.
</critical_constraints>

<language priority="CRITICAL">
<python_version>3.14+</python_version>
<enforcement>
  - Use latest Python features (pattern matching, enhanced type hints)
  - Leverage async/await for concurrent operations
  - NEVER add compatibility code for Python <3.14
</enforcement>
</language>

<cli_framework priority="CRITICAL">
<primary>Typer</primary>
<integration>Rich (built-in with Typer[all])</integration>
<structure>
  - Command structure: `acforge <namespace> <command> [args]`
  - Namespaces: module, workflow, issue, pr, devcontainer, docs
  - ALL commands MUST use type hints for automatic validation
  - ALL commands MUST use Rich for output formatting
</structure>
<enforcement>
  - Entry point: `src/acforge/cli/main.py`
  - One file per namespace: module.py, workflow.py, issue.py, pr.py, devcontainer.py, docs.py
  - NEVER use print() - ALWAYS use Rich Console
</enforcement>
</cli_framework>

<configuration_management priority="CRITICAL">
<format>YAML ONLY</format>
<models>Pydantic v2+</models>
<file_location>.acforge/acforge.yaml</file_location>
<requirements>
  - ALL configuration MUST be defined as Pydantic BaseModel subclasses
  - Models location: `src/acforge/core/config.py`
  - MUST validate on load, MUST fail fast on invalid config
  - NEVER use dictionaries for configuration
  - NEVER serialize to JSON or TOML
</requirements>
<structure>
<![CDATA[
class ModuleConfig(BaseModel):
    name: str
    repo_url: str
    version: str
    subtree_prefix: str
    installed_files: list[str]

class AcforgeConfig(BaseModel):
    version: str
    modules: dict[str, ModuleConfig]
    registry_sources: list[str]
]]>
</structure>
</configuration_management>

<git_integration priority="CRITICAL">
<strategy>HYBRID</strategy>
<rules>
  - Git subtree operations: MUST use subprocess + git CLI directly
  - Standard git operations: MUST use GitPython
  - NEVER use GitPython for git subtree commands
  - ALWAYS capture and parse git CLI output for subtree operations
</rules>
<implementation>
  - Location: `src/acforge/core/git.py`
  - Class: GitManager (handles both subprocess and GitPython)
  - Subtree operations: add, pull, push, split
  - GitPython operations: status, diff, branch, log
</implementation>
</git_integration>

<file_merging_system priority="CRITICAL">
<pattern>Strategy Pattern</pattern>
<strategies>
  - UnionStrategy: .gitignore, .dockerignore (merge all unique entries)
  - TemplateStrategy: pyproject.toml, structured configs (AST-based merge)
  - AppendStrategy: .claude/agents/ (separate files, append mode)
  - UserResolutionStrategy: conflicts require interactive resolution
</strategies>
<enforcement>
  - Base class: `src/acforge/core/merge.py::MergeStrategy`
  - Implementations: `src/acforge/strategies/`
  - ALL strategies MUST implement: `can_merge()`, `merge()`, `validate()`
  - Strategy registration: automatic via class decorator
  - NEVER implement merge logic outside strategy classes
</enforcement>
<interface>
<![CDATA[
class MergeStrategy(ABC):
    @abstractmethod
    def can_merge(self, file_path: Path) -> bool: ...

    @abstractmethod
    def merge(self, base: Path, incoming: Path, target: Path) -> MergeResult: ...

    @abstractmethod
    def validate(self, result: Path) -> bool: ...
]]>
</interface>
</file_merging_system>

<testing priority="CRITICAL">
<framework>pytest</framework>
<property_testing>Hypothesis</property_testing>
<coverage>pytest-cov (minimum 80% coverage)</coverage>
<structure>
  - tests/unit/ - Unit tests for individual functions
  - tests/integration/ - Integration tests for workflows
  - tests/property/ - Hypothesis property-based tests
</structure>
<requirements>
  - ALL merge strategies MUST have Hypothesis tests
  - ALL CLI commands MUST have integration tests
  - ALL Pydantic models MUST have validation tests
  - NEVER skip tests, NEVER commit failing tests
</requirements>
</testing>

<packaging priority="CRITICAL">
<manager>UV</manager>
<configuration>pyproject.toml (PEP 517/518)</configuration>
<requirements>
  - Package name: "acforge"
  - Entry point: "acforge" command
  - MUST support: pip install acforge
  - MUST support: uvx acforge
  - Lock file: uv.lock (MUST be committed)
</requirements>
</packaging>

<dependencies priority="CRITICAL">
<runtime>
  - typer[all]>=0.12.0  # Includes Rich integration
  - rich>=13.0.0        # Terminal formatting
  - pydantic>=2.0.0     # Data validation
  - pyyaml>=6.0         # YAML parsing
  - gitpython>=3.1.0    # Git operations
</runtime>
<development>
  - pytest>=8.0.0
  - pytest-cov>=4.0.0
  - hypothesis>=6.0.0
  - mypy>=1.8.0
  - ruff>=0.2.0
</development>
<enforcement>
  - NEVER add dependencies without justification
  - PREFER standard library when possible
  - AVOID heavy dependencies (pandas, numpy, etc.)
</enforcement>
</dependencies>

<code_quality priority="CRITICAL">
<linting>Ruff (replaces flake8, black, isort)</linting>
<type_checking>MyPy (strict mode)</type_checking>
<requirements>
  - ALL code MUST pass: ruff check src/
  - ALL code MUST pass: mypy --strict src/
  - Configuration in pyproject.toml
  - NEVER disable type checking with # type: ignore without comment
  - NEVER commit unformatted code
</requirements>
</code_quality>

<project_structure priority="CRITICAL">
<layout>
- src/acforge/
  - __init__.py
  - cli/ - Typer CLI commands (ONE FILE PER NAMESPACE)
    - __init__.py
    - main.py - Entry point, Typer app creation
    - module.py - acforge module add/remove/list/update
    - workflow.py - acforge workflow start-from-scratch/tech-stack
    - issue.py - acforge issue create/start
    - pr.py - acforge pr create
    - devcontainer.py - acforge devcontainer build/rebuild
    - docs.py - acforge docs readme/changelog/gitignore
  - core/ - Core functionality (NO CLI CODE)
    - __init__.py
    - git.py - GitManager: subprocess + GitPython
    - config.py - Pydantic models for .acforge.yaml
    - merge.py - MergeStrategy base class, MergeResult
    - registry.py - Module discovery and registry management
  - strategies/ - Merge strategy implementations
    - __init__.py
    - union.py - UnionStrategy (.gitignore merging)
    - template.py - TemplateStrategy (structured file merging)
    - append.py - AppendStrategy (separate file appending)
    - resolution.py - UserResolutionStrategy (conflict handling)
</layout>
<enforcement>NEVER deviate from this structure without updating this document</enforcement>
</project_structure>

<implementation_rules>
<type_safety>
  - ALL functions MUST have type hints (parameters and return values)
  - ALL Pydantic models MUST use strict typing
  - NEVER use Any type without explicit justification in comment
  - Use NewType for domain-specific types (ModuleName, RepoUrl, etc.)
</type_safety>

<error_handling>
  - ALWAYS use Rich Console for error output
  - NEVER use sys.exit() - raise exceptions and handle at CLI boundary
  - ALL exceptions MUST be logged with context
  - User-facing errors MUST be clear and actionable
</error_handling>

<git_operations>
  - Git subtree add: subprocess.run(["git", "subtree", "add", ...])
  - Git subtree pull: subprocess.run(["git", "subtree", "pull", ...])
  - ALWAYS check return codes from git commands
  - ALWAYS capture stderr for error reporting
  - Parse git output to extract commit SHAs, file lists, etc.
</git_operations>

<module_operations>
  - Module metadata MUST be stored in .acforge/acforge.yaml
  - Module files MUST be stored in .acforge/modules/<module-name>/
  - Ephemeral modules: Install → Run Claude Code → Remove directory
  - Long-lived modules: Install → Merge files → Keep for updates
  - NEVER modify user files outside of explicit merge operations
</module_operations>

<cli_ux>
  - ALL commands MUST show progress with Rich Progress
  - ALL tables MUST use Rich Table
  - ALL syntax highlighting MUST use Rich Syntax
  - Interactive prompts MUST use Rich Prompt
  - ALWAYS use emoji sparingly and contextually
</cli_ux>
</implementation_rules>

<forbidden_practices>
<never>
  - NEVER use global state
  - NEVER use mutable default arguments
  - NEVER catch Exception without re-raising
  - NEVER use shell=True in subprocess calls
  - NEVER hardcode paths (use Path objects)
  - NEVER commit secrets or API keys
  - NEVER use deprecated Pydantic v1 syntax
  - NEVER use print() instead of Rich Console
</never>
</forbidden_practices>

<development_workflow>
<steps>
1. Create feature branch from main
2. Implement with full type hints
3. Run: ruff check src/ && ruff format src/
4. Run: mypy --strict src/
5. Run: pytest tests/ --cov=src
6. Ensure 80%+ coverage
7. Commit with conventional commit message
8. Push and create PR
</steps>
</development_workflow>

<architectural_rationale priority="CRITICAL">
<purpose>
This section explains WHY each technology was chosen. Use this to:
- Make consistent decisions when alternatives arise
- Understand trade-offs when constraints conflict
- Explain technical decisions to users
- Maintain architectural coherence
</purpose>

<python_314>
<rationale>Latest features and performance improvements</rationale>
<trade_offs>
  - BENEFIT: Modern type hints, pattern matching, async improvements
  - BENEFIT: Best performance (3.14 is faster than 3.13)
  - COST: Requires recent Python installation
  - DECISION: Speed and modern features outweigh compatibility concerns
</trade_offs>
<when_to_reconsider>If users cannot install Python 3.14+ (unlikely for CLI tools)</when_to_reconsider>
</python_314>

<typer_rich>
<rationale>Type-safe CLI with beautiful output</rationale>
<trade_offs>
  - BENEFIT: Type hints generate automatic validation and help
  - BENEFIT: Rich integration provides excellent UX
  - BENEFIT: Namespace support perfect for acforge command structure
  - COST: Slightly larger dependency than argparse
  - DECISION: UX and type safety worth dependency size
</trade_offs>
<alternatives>
  - Click: Typer is built on Click, so we get Click's stability
  - argparse: No type safety, poor UX, manual help generation
</alternatives>
</typer_rich>

<pydantic_yaml>
<rationale>Type-safe configuration with validation</rationale>
<trade_offs>
  - BENEFIT: Pydantic catches config errors at load time
  - BENEFIT: YAML is human-readable (vs JSON)
  - BENEFIT: Type safety prevents runtime errors
  - COST: Pydantic v2 is a dependency
  - DECISION: Early error detection worth the dependency
</trade_offs>
<why_not_json>JSON less human-friendly, no comments</why_not_json>
<why_not_toml>YAML more widely used for config, better nested structures</why_not_toml>
</pydantic_yaml>

<git_hybrid>
<rationale>Use best tool for each job</rationale>
<trade_offs>
  - subprocess for subtrees: Git subtree not well-supported by GitPython
  - GitPython for other ops: Cleaner API than parsing CLI output
  - BENEFIT: Reliability for complex subtree operations
  - BENEFIT: Clean code for simple operations
  - COST: Two approaches to learn/maintain
  - DECISION: Reliability of subtrees critical, worth complexity
</trade_offs>
</git_hybrid>

<strategy_pattern_merging>
<rationale>Extensible, testable file merging</rationale>
<trade_offs>
  - BENEFIT: Easy to add new file types
  - BENEFIT: Each strategy independently testable
  - BENEFIT: Clear separation of concerns
  - COST: More files/classes than inline logic
  - DECISION: Testability and extensibility worth extra structure
</trade_offs>
<why_critical>File merging is core functionality, must be bulletproof</why_critical>
</strategy_pattern_merging>

<hypothesis_testing>
<rationale>Find edge cases automatically</rationale>
<trade_offs>
  - BENEFIT: Discovers bugs traditional tests miss
  - BENEFIT: Perfect for testing merge strategies (complex inputs)
  - BENEFIT: Generates test cases you wouldn't think of
  - COST: Slower than unit tests
  - COST: Requires different testing mindset
  - DECISION: Critical for file merging reliability
</trade_offs>
<when_to_use>ALL merge strategies, config parsing, git operations</when_to_use>
</hypothesis_testing>

<uv_packaging>
<rationale>Modern, fast, aligns with uvx usage</rationale>
<trade_offs>
  - BENEFIT: Extremely fast (Rust-based)
  - BENEFIT: Lock files for reproducibility
  - BENEFIT: uvx acforge works seamlessly
  - COST: UV is newer, less established than pip/poetry
  - DECISION: Speed and uvx alignment critical for CLI tool
</trade_offs>
<why_not_poetry>UV faster, better uvx integration</why_not_poetry>
<why_not_pip>UV provides lock files, faster resolution</why_not_pip>
</uv_packaging>

<ruff_mypy>
<rationale>Fast, comprehensive code quality</rationale>
<trade_offs>
  - BENEFIT: Ruff is 100x faster than flake8/black/isort
  - BENEFIT: MyPy catches type errors before runtime
  - BENEFIT: Both configured via pyproject.toml
  - COST: Another dependency
  - DECISION: Development speed and type safety non-negotiable
</trade_offs>
</ruff_mypy>

<decision_framework>
<when_adding_dependencies>
1. Is it in standard library? USE STANDARD LIBRARY
2. Does it solve critical problem? EVALUATE TRADE-OFFS
3. Is it well-maintained? CHECK GITHUB ACTIVITY
4. Is it fast? PREFER RUST-BASED TOOLS
5. Does it reduce code complexity? WORTH THE DEPENDENCY
</when_adding_dependencies>

<when_choosing_approaches>
1. Does it improve type safety? STRONG PREFERENCE
2. Does it improve UX? HIGH PRIORITY
3. Does it improve testability? REQUIRED FOR CORE LOGIC
4. Does it improve performance? NICE TO HAVE
5. Does it reduce complexity? TIE-BREAKER
</when_choosing_approaches>
</decision_framework>

</architectural_rationale>

</acforge_technical_requirements>
