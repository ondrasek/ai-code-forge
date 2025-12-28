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
src/acforge/
├── __init__.py
├── cli/                    # Typer CLI commands (ONE FILE PER NAMESPACE)
│   ├── __init__.py
│   ├── main.py            # Entry point, Typer app creation
│   ├── module.py          # acforge module add/remove/list/update
│   ├── workflow.py        # acforge workflow start-from-scratch/tech-stack
│   ├── issue.py           # acforge issue create/start
│   ├── pr.py              # acforge pr create
│   ├── devcontainer.py    # acforge devcontainer build/rebuild
│   └── docs.py            # acforge docs readme/changelog/gitignore
├── core/                   # Core functionality (NO CLI CODE)
│   ├── __init__.py
│   ├── git.py             # GitManager: subprocess + GitPython
│   ├── config.py          # Pydantic models for .acforge.yaml
│   ├── merge.py           # MergeStrategy base class, MergeResult
│   └── registry.py        # Module discovery and registry management
└── strategies/             # Merge strategy implementations
    ├── __init__.py
    ├── union.py           # UnionStrategy (.gitignore merging)
    ├── template.py        # TemplateStrategy (structured file merging)
    ├── append.py          # AppendStrategy (separate file appending)
    └── resolution.py      # UserResolutionStrategy (conflict handling)
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

</acforge_technical_requirements>
