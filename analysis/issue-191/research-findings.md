RESEARCH ANALYSIS REPORT
=======================

RESEARCH CONTEXT:
Topic: Current Official Claude Code Environment Variables and CLI Arguments (2025)
Category: API Documentation + Best Practices Research
Approach: Web-First Mandatory
Confidence: High (Tier 1 sources + cross-validation)

WEB RESEARCH PHASE (PRIMARY):
╭─ WebSearch Results:
│  ├─ Query Terms: "Claude Code CLI official environment variables 2025", "--verbose --mcp-debug flags", "CLAUDE_CODE_ENABLE_TELEMETRY 2025"
│  ├─ Key Findings: Official CLI flags and environment variables documented at docs.anthropic.com
│  ├─ Trend Analysis: OpenTelemetry support is in beta as of 2025, indicating active development
│  └─ Search Date: 2025-08-18
│
╰─ WebFetch Analysis:
   ├─ Official Sources: docs.anthropic.com CLI reference, settings, and monitoring docs (current)
   ├─ Authority Validation: Direct from Anthropic documentation (highest credibility)
   ├─ Version Information: 2025 documentation, OpenTelemetry in beta status
   └─ Cross-References: 3/3 official documentation sources confirmed findings

LOCAL INTEGRATION PHASE (SECONDARY):
╭─ Codebase Analysis:
│  ├─ Existing Patterns: launch-claude.sh uses outdated/incorrect environment variables
│  ├─ Version Alignment: Several deprecated variables found in current implementation
│  └─ Usage Context: Script sets ANTHROPIC_DEBUG, ANTHROPIC_LOG_LEVEL (not officially supported)
│
╰─ Integration Assessment:
   ├─ Compatibility: Current script uses non-standard variables
   ├─ Migration Needs: Major environment variable updates required
   └─ Implementation Complexity: Medium - requires environment variable replacement and CLI flag updates

SYNTHESIS & RECOMMENDATIONS:

╭─ Official Claude Code Environment Variables (2025):
│
│  ├─ **AUTHENTICATION**:
│  │   ├─ ANTHROPIC_API_KEY - Primary authentication method
│  │   ├─ CLAUDE_CODE_USE_BEDROCK=1 - Enable AWS Bedrock integration
│  │   ├─ CLAUDE_CODE_USE_VERTEX=1 - Enable Google Vertex AI integration
│  │   └─ AWS_REGION - Required for Bedrock (not read from .aws config)
│  │
│  ├─ **TELEMETRY & MONITORING**:
│  │   ├─ CLAUDE_CODE_ENABLE_TELEMETRY=1 - Enable OpenTelemetry export
│  │   ├─ OTEL_METRICS_EXPORTER - Options: console, otlp, prometheus
│  │   ├─ OTEL_LOGS_EXPORTER - Options: console, otlp
│  │   ├─ OTEL_EXPORTER_OTLP_PROTOCOL - Options: grpc, http/json, http/protobuf
│  │   ├─ OTEL_LOG_USER_PROMPTS=1 - Enable logging of user prompt content
│  │   ├─ OTEL_METRIC_EXPORT_INTERVAL - Metrics export interval (default: 60000ms)
│  │   ├─ OTEL_LOGS_EXPORT_INTERVAL - Logs export interval (default: 5000ms)
│  │   ├─ OTEL_METRICS_INCLUDE_SESSION_ID - Include session ID (default: true)
│  │   ├─ OTEL_METRICS_INCLUDE_VERSION - Include app version (default: false)
│  │   ├─ OTEL_METRICS_INCLUDE_ACCOUNT_UUID - Include user UUID (default: true)
│  │   └─ OTEL_EXPORTER_OTLP_HEADERS - Set authentication headers
│  │
│  ├─ **PRIVACY & REPORTING CONTROLS**:
│  │   ├─ DISABLE_TELEMETRY=1 - Opt out of Statsig telemetry
│  │   ├─ DISABLE_ERROR_REPORTING=1 - Opt out of Sentry error reporting
│  │   ├─ CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC - Disable all non-essential traffic
│  │   └─ DISABLE_NON_ESSENTIAL_MODEL_CALLS=1 - Disable non-critical model calls
│  │
│  ├─ **PERFORMANCE & LIMITS**:
│  │   ├─ CLAUDE_CODE_MAX_OUTPUT_TOKENS - Max output tokens for requests
│  │   ├─ BASH_MAX_OUTPUT_LENGTH - Max characters in bash outputs before truncation
│  │   ├─ BASH_DEFAULT_TIMEOUT_MS - Default timeout for bash commands
│  │   ├─ BASH_MAX_TIMEOUT_MS - Maximum timeout model can set
│  │   └─ MCP_TIMEOUT - MCP server startup timeout (e.g., MCP_TIMEOUT=10000)
│  │
│  ├─ **DISPLAY & UX**:
│  │   ├─ CLAUDE_CODE_VERBOSE - Show full bash and command outputs
│  │   └─ CLAUDE_CODE_DISABLE_TERMINAL_TITLE=1 - Disable terminal title updates
│  │
│  └─ **DEPRECATED/NON-STANDARD (found in current script)**:
│      ├─ ❌ ANTHROPIC_DEBUG - Not officially documented
│      ├─ ❌ ANTHROPIC_LOG_LEVEL - Not officially documented
│      ├─ ❌ CLAUDE_DEBUG - Not officially documented
│      └─ ❌ MCP_LOG_LEVEL - Not officially documented
│
├─ **Official Claude Code CLI Arguments (2025)**:
│   ├─ --verbose - Enable verbose logging (shows full turn-by-turn output)
│   ├─ --mcp-debug - Troubleshoot MCP configuration issues
│   ├─ --output-format - Options: text, json, stream-json
│   ├─ --input-format - Options: text, stream-json
│   ├─ --max-turns - Limit agentic turns in non-interactive mode
│   ├─ --dangerously-skip-permissions - Skip all permission checks
│   └─ --allowedTools - Session-specific tool permissions
│
╰─ **Key Issues in Current launch-claude.sh Script**:
   ├─ Uses ANTHROPIC_DEBUG=1 (not officially supported)
   ├─ Uses ANTHROPIC_LOG_LEVEL=debug (not officially supported)  
   ├─ Uses MCP_LOG_LEVEL=debug (not officially supported)
   ├─ Uses CLAUDE_DEBUG=1 (not officially supported)
   ├─ Missing official CLAUDE_CODE_ENABLE_TELEMETRY configuration
   └─ OTEL_* variables improperly configured for telemetry collection

ACTIONABLE OUTCOME:
Replace non-standard environment variables in launch-claude.sh with official Claude Code variables:

1. **High Priority Fixes**:
   - Replace ANTHROPIC_DEBUG=1 with --verbose CLI flag
   - Replace CLAUDE_DEBUG=1 with CLAUDE_CODE_VERBOSE environment variable
   - Replace ANTHROPIC_LOG_LEVEL=debug with proper OTEL_LOGS_EXPORTER configuration
   - Add CLAUDE_CODE_ENABLE_TELEMETRY=1 for proper telemetry enablement

2. **OpenTelemetry Configuration**:
   - Configure OTEL_LOGS_EXPORTER=console for local logging
   - Set OTEL_METRIC_EXPORT_INTERVAL and OTEL_LOGS_EXPORT_INTERVAL appropriately
   - Remove conflicting OTEL exporters that disable output

3. **CLI Flag Updates**:
   - Ensure --mcp-debug flag is properly used for MCP troubleshooting
   - Maintain --verbose flag for general debugging

4. **Environment Variable Migration**:
   - Remove: ANTHROPIC_DEBUG, ANTHROPIC_LOG_LEVEL, CLAUDE_DEBUG, MCP_LOG_LEVEL
   - Add: CLAUDE_CODE_ENABLE_TELEMETRY, CLAUDE_CODE_VERBOSE, proper OTEL_* variables

SOURCE ATTRIBUTION:
╭─ Primary Sources (Web):
│  ├─ Official Documentation: docs.anthropic.com/en/docs/claude-code/cli-reference (2025)
│  ├─ Settings Documentation: docs.anthropic.com/en/docs/claude-code/settings (2025)
│  ├─ Monitoring Documentation: docs.anthropic.com/en/docs/claude-code/monitoring-usage (2025)
│  └─ MCP Documentation: docs.anthropic.com/en/docs/claude-code/mcp (2025)
│
╰─ Supporting Sources:
   ├─ Local Context: /workspace/worktrees/ai-code-forge/issue-191/scripts/launch-claude.sh
   ├─ GitHub Issues: Various Claude Code repository issues confirming environment variable usage
   └─ Community Resources: Developer blogs and guides (Tier 3 validation)

VALIDATION METRICS:
├─ Web-First Protocol: ✓ Complete (WebSearch + WebFetch)
├─ Source Authority: Tier 1 Official (Direct from Anthropic documentation)
├─ Information Currency: Recent (< 3mo, actively maintained docs)
├─ Local Compatibility: ⚠ Major Changes (environment variable migration required)
└─ Confidence Level: High (Official docs + multiple source confirmation)

IMPLEMENTATION PRIORITY:
This is a critical fix for issue #191 as the current script uses deprecated/non-standard environment variables that may not provide proper logging and debugging capabilities. The migration to official Claude Code environment variables will ensure reliable functionality and proper telemetry collection.