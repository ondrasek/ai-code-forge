# Implementation Notes - Codex CLI MCP Integration

## Scope Evolution Decision

**Original GitHub Issue #170 Specification**: Create Python MCP server wrapping OpenAI Codex CLI tool with subprocess management.

**Recommended Implementation Approach**: Extend existing `openai-structured-mcp` server with Codex-optimized tools using OpenAI API directly.

### Rationale for Scope Change

Our comprehensive multi-agent analysis identified critical blockers with the original subprocess approach:

1. **Security Risks**: Command injection attack surface and credential exposure
2. **Performance Impact**: 4-8x latency degradation (200-400ms vs 50-100ms)  
3. **Architecture Coupling**: CLI transition from Node.js to Rust creates fragility
4. **Maintenance Burden**: Subprocess management and error translation complexity

### Technical Validation

**Critical Review Approved**: The extended API approach delivers equivalent capabilities with superior security, performance, and maintainability characteristics.

## Implementation Plan

### Phase 1: Core Codex Tools Extension

**Target**: Extend `mcp-servers/openai-structured-mcp/src/openai_structured_mcp/server.py`

**New Tools to Add**:
```python
@mcp.tool()
async def codex_generate(
    prompt: str, 
    language: Optional[str] = None,
    context: Optional[str] = None
) -> str:
    """Generate code using Codex-optimized prompting"""

@mcp.tool()  
async def codex_review(
    code: str,
    focus: Optional[str] = None
) -> str:
    """Perform code review using Codex capabilities"""

@mcp.tool()
async def codex_refactor(
    code: str, 
    requirements: str
) -> str:
    """Refactor code using Codex intelligence"""

@mcp.tool()
async def codex_explain(
    code: str,
    level: Optional[str] = "detailed"  
) -> str:
    """Explain code functionality and patterns"""
```

### Phase 2: Codex-Optimized Prompting

**Approach**: Create specialized prompt templates for Codex-style interactions:

```python
CODEX_PROMPTS = {
    "generate": "You are OpenAI Codex. Generate {language} code for: {prompt}...",
    "review": "You are OpenAI Codex. Review this {language} code: {code}...",
    "refactor": "You are OpenAI Codex. Refactor this code: {requirements}...",
    "explain": "You are OpenAI Codex. Explain this code at {level} level..."
}
```

### Phase 3: Enhanced Configuration

**Update**: `mcp-servers/mcp-config.json`
```json
{
  "openai-structured": {
    "command": "uv",
    "args": ["run", "openai-structured-mcp"],
    "env": {
      "OPENAI_API_KEY": "${OPENAI_API_KEY}",
      "CODEX_MODE": "enabled"
    }
  }
}
```

### Phase 4: Testing Strategy

**Test Structure**: Follow existing patterns in `mcp-servers/tests/`

1. **Unit Tests**: Tool functionality with mocked OpenAI API
2. **Integration Tests**: End-to-end MCP server communication  
3. **Performance Tests**: Validate 50-100ms response time claims
4. **Security Tests**: Input validation and error handling

## File Structure

```
mcp-servers/openai-structured-mcp/
├── src/openai_structured_mcp/
│   ├── server.py           # Extended with Codex tools
│   ├── codex_prompts.py    # Codex-optimized prompt templates  
│   └── codex_tools.py      # Dedicated Codex tool implementations
└── tests/
    ├── test_codex_tools.py # Codex-specific testing
    └── test_codex_integration.py
```

## Dependencies

**Existing Dependencies** (no additional required):
- `openai >= 1.0.0` (already present)
- `fastmcp >= 2.0` (already present)
- Python 3.13+ (project standard)

## Performance Targets

**Response Time Goals**:
- `codex_generate`: < 100ms for simple prompts
- `codex_review`: < 150ms for code analysis
- `codex_refactor`: < 200ms for transformation tasks

**Benchmarking**: Create performance tests to validate against CLI subprocess baseline.

## Security Considerations

**Input Validation**: 
- Sanitize all user-provided code and prompts
- Implement length limits and content filtering
- Use existing OpenAI client security patterns

**Authentication**:
- Leverage existing OPENAI_API_KEY environment variable handling
- Support same authentication patterns as current server

## Migration Strategy

**CLI Integration Path** (if needed later):
1. Add optional `CODEX_CLI_PATH` environment variable
2. Implement CLI fallback for specific operations
3. Graceful degradation between API and CLI modes

## Success Metrics

1. **Capability Parity**: 80%+ of intended CLI functionality through API
2. **Performance**: Sub-100ms average response times  
3. **Security**: Zero subprocess-related vulnerabilities
4. **Maintenance**: Reuse existing infrastructure patterns

## Progress Tracking

- [ ] Extend openai-structured-mcp server with Codex tools
- [ ] Implement Codex-optimized prompt templates
- [ ] Add comprehensive test coverage
- [ ] Update configuration and documentation
- [ ] Performance validation and benchmarking
- [ ] Security review and validation

## Known Limitations

1. **Workspace Context**: API approach doesn't have local filesystem awareness (same as existing MCP servers)
2. **CLI-Specific Features**: Some advanced CLI options may not translate directly to API calls
3. **Real-time Interaction**: Less interactive than CLI tool's conversation mode

These limitations are acceptable given the security, performance, and maintainability benefits of the API approach.