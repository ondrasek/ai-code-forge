# ACF Repository Layout - AI Instructions

## DIRECTORY_STRUCTURE_RULES

```yaml
REQUIRED_SEPARATION:
  acf_directory: ".acf/"     # ACF tool state and templates
  claude_directory: ".claude/" # Claude Code recognized files only
  constraint: "no_overlap_between_directories"

PROJECT_STRUCTURE:
  root: "PROJECT_ROOT/"
  directories:
    - path: ".acf/"
      purpose: "acf_tool_state"
    - path: ".claude/" 
      purpose: "claude_recognized_files"
      constraint: "claude_code_compatible_only"
```

## ACF_DIRECTORY_STRUCTURE

```yaml
CREATE_ACF_STRUCTURE:
  base_path: ".acf/"
  subdirectories:
    config:
      files: ["acf.json", "deployment.json", "overrides.json"]
      purpose: "tool_configuration"
    templates:
      subdirs: ["agents/", "commands/", "guidelines/", "prompts/", "stacks/"]
      purpose: "deployment_sources"
    backups:
      subdirs: ["claude/", "acf/"]
      purpose: "configuration_history"
    state:
      files: ["installed.json", "versions.json", "migrations.json", "checksums.json", "conflicts.log"]
      purpose: "tool_state_tracking"
    cache:
      subdirs: ["downloads/", "staging/"]
      purpose: "working_files"
      gitignore: true

CREATE_CLAUDE_STRUCTURE:
  base_path: ".claude/"
  constraint: "claude_code_recognized_only"
  subdirectories:
    agents:
      subdirs: ["foundation/", "specialists/"]
      purpose: "active_agent_definitions"
    commands:
      subdirs: ["issue/", "commands/", "agents/"]
      purpose: "active_slash_commands"
  files: ["settings.json"]
  purpose: "claude_runtime_config"

CREATE_PROJECT_INTEGRATION:
  root_files: ["CLAUDE.md"]
  directories: [".acf/", ".claude/"]
  preserve_existing: true
```

## CONFIGURATION_PRECEDENCE

```yaml
APPLY_CONFIG_HIERARCHY:
  priority_order:
    1:
      source: [".claude/settings.json", "CLAUDE.md"]
      level: "project"
      override_all: true
    2:
      source: ".acf/config/overrides.json"
      level: "user_override"
    3:
      source: ".acf/config/deployment.json" 
      level: "acf_deployment"
    4:
      source: ".acf/config/acf.json"
      level: "acf_defaults"
    5:
      source: "system_claude_config"
      level: "global"
      fallback: true
```

## DEPLOYMENT_ALGORITHM

```yaml
PRE_DEPLOYMENT_VALIDATION:
  - EXECUTE: check_directory_exists
    path: ".claude/"
    action_if_exists:
      - EXECUTE: create_backup
        source: ".claude/"
        target: ".acf/backups/{timestamp}/"
      - EXECUTE: analyze_conflicts
        existing: ".claude/"
        incoming: ".acf/templates/"
      - EXECUTE: prompt_user_conflict_resolution
        conflicts: "analysis_result"

TEMPLATE_PROCESSING:
  - EXECUTE: iterate_templates
    source: ".acf/templates/"
    for_each_template:
      - EXECUTE: check_target_exists
        target: ".claude/{template_path}"
        action_if_exists:
          - EXECUTE: apply_merge_strategy
            strategy: "file_type_based"
          - EXECUTE: log_conflicts
            destination: ".acf/state/conflicts.log"
        action_if_not_exists:
          - EXECUTE: deploy_template
            source: ".acf/templates/{template}"
            target: ".claude/{template_path}"

POST_DEPLOYMENT_ACTIONS:
  - EXECUTE: update_versions
    file: ".acf/state/versions.json"
  - EXECUTE: generate_checksums
    file: ".acf/state/checksums.json"
  - EXECUTE: validate_claude_config
    directory: ".claude/"
```

## COMPONENT_PLACEMENT_RULES

```yaml
ACF_DIRECTORY_RULES:
  path: ".acf/"
  management: "acf_tool_only"
  contents:
    config: "acf_tool_configuration"
    templates: "deployment_sources" 
    backups: "automatic_backups"
    state: "tool_state_tracking"
    cache: "working_files"
  version_control:
    include: ["config/", "templates/"]
    exclude: ["state/", "cache/"]

CLAUDE_DIRECTORY_RULES:
  path: ".claude/"
  management: "user_editable"
  constraint: "claude_code_recognized_only"
  contents:
    agents: "active_agent_definitions"
    commands: "active_slash_commands"
    settings: "claude_runtime_config"
  populated_by: "acf_templates"
  user_modifications: "preserved"
```

## CONFLICT_RESOLUTION_RULES

```yaml
MERGE_STRATEGIES:
  agents:
    source: ".acf/templates/agents/"
    target: ".claude/agents/"
    strategy: "type_based_merge"
    preserve_user: true
  commands:
    source: ".acf/templates/commands/"
    target: ".claude/commands/"
    strategy: "user_precedence"
    log_updates: ".acf/state/conflicts.log"
  settings:
    source: ".acf/templates/settings.json"
    target: ".claude/settings.json"
    strategy: "deep_merge"
    priority: "user"
  guidelines:
    source: ".acf/templates/guidelines/"
    target: "CLAUDE.md"
    strategy: "additive_merge"
    conflict_markers: true

LEGACY_MIGRATION:
  - EXECUTE: check_conditions
    condition: "exists(.claude/) AND not_exists(.acf/)"
    actions:
      - EXECUTE: create_backup
        source: ".claude/"
        target: ".acf/backups/migration-{timestamp}/"
      - EXECUTE: analyze_existing_config
        path: ".claude/"
      - EXECUTE: apply_templates
        strategy: "preservation"
      - EXECUTE: log_migration
        file: ".acf/state/migrations.json"
```

## INTEGRATION_WORKFLOWS

```yaml
NEW_PROJECT_SETUP:
  - EXECUTE: initialize_acf
    action: create_acf_structure
    templates: "default"
  - EXECUTE: deploy_base_config
    source: ".acf/templates/"
    target: ".claude/"
  - EXECUTE: generate_project_instructions
    file: "CLAUDE.md"
  - EXECUTE: setup_version_control
    gitignore: ['.acf/state/', '.acf/cache/']

EXISTING_PROJECT_INTEGRATION:
  - EXECUTE: backup_existing
    source: ".claude/"
    target: ".acf/backups/{timestamp}/"
  - EXECUTE: merge_configurations
    strategy: "intelligent"
    existing: ".claude/"
    templates: ".acf/templates/"
  - EXECUTE: resolve_conflicts
    method: "user_prompt"
  - EXECUTE: gradual_migration
    mode: "incremental"

PROJECT_TYPE_DETECTION:
  - EXECUTE: detect_project_type
    rules:
      - condition: "exists(package.json)"
        type: "node"
        templates: "node_specific"
      - condition: "exists(Cargo.toml)"
        type: "rust" 
        templates: "rust_specific"
      - condition: "exists(pom.xml) OR exists(build.gradle)"
        type: "java"
        templates: "java_specific"
```

## CONFIGURATION_SCHEMAS

```yaml
ACF_CONFIG_SCHEMA:
  file: ".acf/config/acf.json"
  required_fields:
    version: "string"
    auto_update: "boolean"
    backup_enabled: "boolean"
    backup_retention_days: "integer"
    template_sources: "array[string]"
    deployment:
      merge_strategy: "string"
      conflict_resolution: "string"
      preserve_customizations: "boolean"
  defaults:
    version: "1.0.0"
    auto_update: false
    backup_enabled: true
    backup_retention_days: 30
    template_sources: ["https://github.com/ondrasek/ai-code-forge/templates"]
    deployment:
      merge_strategy: "intelligent"
      conflict_resolution: "prompt"
      preserve_customizations: true

USER_OVERRIDE_SCHEMA:
  file: ".acf/config/overrides.json"
  optional_fields:
    disabled_components: "array[string]"
    custom_templates:
      agents: "array[string]"
      commands: "array[string]"
    claude_settings_override: "object"
```

STATE_TRACKING_SCHEMAS:
  installed_components:
    file: ".acf/state/installed.json"
    schema:
      acf_version: "string"
      installed_at: "iso_timestamp"
      components:
        agents: "array[string]"
        commands: "array[string]"
        templates: "array[string]"
      user_modifications: "object[filepath: timestamp]"
  
  version_management:
    file: ".acf/state/versions.json"
    schema:
      acf_version: "string"
      template_versions:
        agents: "string"
        commands: "string"
        guidelines: "string"
      last_update: "iso_timestamp"
      update_available: "boolean"

## VERSION_CONTROL_RULES

```yaml
GITIGNORE_PATTERNS:
  - ".acf/state/"
  - ".acf/backups/"
  - ".acf/cache/"
  - ".acf/tmp/"
  - ".acf/.cache/"
  - ".acf/config/overrides.json"

VERSION_CONTROL_STRATEGY:
  include:
    - ".acf/config/acf.json"
    - ".acf/config/deployment.json"
    - ".acf/templates/"
    - ".claude/"
    - "CLAUDE.md"
  exclude:
    - ".acf/state/"
    - ".acf/backups/"
    - ".acf/cache/"
    - ".acf/config/overrides.json"
```

## OPERATIONAL_WORKFLOWS

```yaml
DEPLOYMENT_WORKFLOW:
  - EXECUTE: detect_project
    analyze: ["type", "existing_configs"]
  - EXECUTE: select_templates
    based_on: "project_stack"
  - EXECUTE: analyze_conflicts
    before: "deployment"
  - EXECUTE: confirm_with_user
    show: "deployment_plan"
  - EXECUTE: create_backups
    comprehensive: true
  - EXECUTE: deploy_templates
    target: ".claude/"
  - EXECUTE: generate_config
    files: ["CLAUDE.md", "tool_config"]
  - EXECUTE: track_state
    update: ["deployment_state", "versions"]

UPDATE_WORKFLOW:
  - EXECUTE: check_updates
    source: "acf_templates"
  - EXECUTE: analyze_impact
    on: "user_configuration"
  - EXECUTE: plan_merge
    strategy: "intelligent"
  - EXECUTE: notify_user
    show: ["update_summary", "conflicts"]
  - EXECUTE: selective_update
    allow_user_choice: true
  - EXECUTE: backup_and_apply
    updates: "selected"
  - EXECUTE: verify_application
    validate: "success"

MIGRATION_FROM_CLAUDE:
  - EXECUTE: analyze_existing
    scan: ".claude/"
    detect: "customizations"
  - EXECUTE: create_backup
    target: ".acf/backups/{timestamp}/"
  - EXECUTE: match_templates
    identify: "acf_equivalent_components"
  - EXECUTE: flag_custom_components
    user_created: true
  - EXECUTE: create_merge_plan
    for_review: true
  - EXECUTE: apply_plan
    require_confirmation: true

MIGRATION_FROM_LEGACY_ACF:
  - EXECUTE: detect_version
    from: ".acf/state/"
  - EXECUTE: run_migration_scripts
    version_specific: true
  - EXECUTE: update_templates
    to: "latest_versions"
  - EXECUTE: migrate_config_format
    handle: "format_changes"
  - EXECUTE: validate_migration
    check: ["completeness", "functionality"]
```

## SECURITY_AND_VALIDATION

```yaml
FILE_PERMISSIONS:
  acf_directory: "755"
  claude_directory: "755"
  acf_config: "600"
  acf_backups: "600"
  sensitive_files: "600"

VALIDATION_RULES:
  - ENFORCE: no_executable_permissions
    on: "configuration_files"
  - EXECUTE: json_schema_validation
    on: "all_config_files"
  - EXECUTE: template_syntax_validation
    before: "deployment"
  - EXECUTE: detect_circular_dependencies
    in: "agent_configurations"
  - EXECUTE: validate_permissions
    for: "file_operations"
  - EXECUTE: scan_malicious_content
    in: "templates"
  - EXECUTE: verify_acf_signatures
    on: "template_downloads"

SENSITIVE_DATA_RULES:
  - NEVER: store_secrets
    in: ".acf/config/"
  - USE: environment_variables
    for: "secret_management"
  - EXCLUDE: sensitive_files
    from: "git"
  - PROVIDE: documentation
    on: "secret_management"

ERROR_HANDLING:
  critical_failures:
    backup_creation_fails:
      - EXECUTE: abort_deployment
      - EXECUTE: report_error
        to: "user"
    claude_corruption_detected:
      - EXECUTE: restore_from_backup
        source: ".acf/backups/latest/"
      - EXECUTE: report_restoration
        to: "user"
    template_integrity_fails:
      - EXECUTE: refuse_deployment
      - EXECUTE: prompt_manual_verification
        to: "user"
```

## EXTENSIBILITY_RULES

```yaml
FUTURE_CAPABILITIES:
  plugin_system:
    - SUPPORT: custom_acf_components
  external_integration:
    - SUPPORT: external_template_repositories
    - SUPPORT: programmatic_api
    - SUPPORT: cicd_integration
  multi_repository:
    - SUPPORT: shared_configurations
    - SUPPORT: organization_repositories
    - SUPPORT: team_customizations
    - SUPPORT: cross_project_sync
```

## IMPLEMENTATION_METADATA

```yaml
PRIORITY: "high"
BLOCKS: ["acf_tool_implementation", "user_onboarding"]
DEPENDENCIES:
  - "acf_tool_implementation"
  - "template_repository_structure"
  - "user_migration_tooling"
GITHUB_ISSUE: "#61"
GENERATED_BY: "claude_code"
```