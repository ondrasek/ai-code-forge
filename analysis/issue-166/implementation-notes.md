# Implementation Notes for launch-codex.sh

## Project Context
- **Issue**: #166 - Implement launch-codex.sh script
- **GitHub Issue State**: OPEN (enhancement, feat labels)
- **Branch**: issue-166-implement-launch-codex-sh
- **Target**: Create OpenAI Codex CLI integration following launch-claude.sh patterns

## Research Summary
Based on comprehensive research documented in research-findings.md and technical-analysis.md:

### Key Findings
1. **OpenAI Codex CLI** - Production-ready Rust-based tool with ChatGPT subscription auth
2. **Architecture Pattern** - launch-claude.sh provides 900-line reference implementation
3. **Security Requirements** - Must follow established input validation and environment handling
4. **Integration Points** - Session logging, .env loading, environment detection, MCP support

### Critical Engineering Decisions (from decision-rationale.md)
- **Approach**: Hybrid Modular-Minimal (200-line implementation with shared components)
- **Security**: Zero duplication of authentication/validation logic
- **Architecture**: Extract shared components, refactor both launchers

## Implementation Plan

### High Priority: Core Implementation

1. **Create shared utility library** 
   - Extract common functions from launch-claude.sh
   - Environment detection, .env loading, security validation
   - Logging setup, configuration management
   - Location: `scripts/lib/launcher-utils.sh`

2. **Implement launch-codex.sh**
   - Mirror launch-claude.sh CLI interface
   - Use shared utilities for security and configuration
   - Codex-specific features: ChatGPT auth, TOML config
   - Session-based logging with codex-specific patterns

3. **Refactor launch-claude.sh**
   - Update to use shared utilities
   - Maintain backward compatibility
   - Reduce code duplication

### Medium Priority: Integration Features

4. **Environment integration**
   - Devcontainer/codespace detection
   - Permission handling patterns
   - MCP server support

5. **Configuration management**
   - Codex TOML config parsing
   - Profile management
   - Environment variable handling

6. **Logging and debugging**
   - Session-based logging in .support/logs/codex/
   - Debug mode with RUST_LOG support
   - Agent analysis integration

### Low Priority: Advanced Features

7. **Multi-agent analysis**
   - Log analysis commands (--analyze-logs)
   - Troubleshooting capabilities (--troubleshoot-codex)
   - Performance monitoring

8. **Documentation**
   - Usage documentation following launch-claude patterns
   - Integration guides
   - Security guidelines

## Technical Specifications

### File Structure
```
scripts/
├── lib/
│   └── launcher-utils.sh       # Shared utilities (NEW)
├── launch-claude.sh            # Refactored to use shared utils
└── launch-codex.sh             # New implementation (200 lines)
```

### CLI Interface (Mirror launch-claude.sh)
```bash
launch-codex [OPTIONS] [QUERY]

Options:
-h, --help                 Show help
-q, --quiet               Disable verbose mode  
-m, --model MODEL         Set model
--log-file FILE           Custom log file
-c, --continue            Continue conversation
-r, --resume [ID]         Resume session
--analyze-logs            Analyze existing logs
--clean-logs              Clean all logs  
--troubleshoot-codex      Troubleshoot Codex issues
--skip-permissions        Skip permission checks
--dry-run                 Show command without execution
```

### Security Requirements
- Input validation and sanitization
- Command injection prevention  
- Environment variable masking
- File permission validation
- Process isolation

### Integration Requirements
- Session-based logging in .support/logs/codex/[SESSION]/
- Environment auto-detection (devcontainer, codespace)
- .env file loading with security validation
- Shared authentication patterns
- MCP server integration support

## Progress Tracking

### Completed Tasks
- ✅ Comprehensive research (OpenAI Codex CLI capabilities)
- ✅ Technical context analysis (codebase patterns) 
- ✅ Architecture decision (Hybrid Modular-Minimal approach)
- ✅ Shell scripting guidelines integration
- ✅ Implementation planning and specification

### Next Steps
1. **Start implementation** - Create shared utilities library
2. **Core development** - Implement launch-codex.sh using shared components
3. **Integration testing** - Validate with existing infrastructure
4. **Documentation** - Create usage guides and integration docs
5. **Quality validation** - Security testing, performance testing

### Dependencies and Constraints
- Must maintain backward compatibility with launch-claude.sh
- Follow CLAUDE.md mandatory operational rules
- Implement security-first design patterns
- Use git-workflow agent for all commits
- No artificial timeline constraints

## Agent Collaboration Notes
- **context agent**: Provided comprehensive codebase analysis
- **researcher agent**: Delivered complete OpenAI Codex CLI research
- **stack-advisor agent**: Loaded Shell/Bash technology guidelines  
- **options-analyzer agent**: Recommended Hybrid Modular-Minimal approach

All agents referenced and updated analysis files for coordinated development approach.