# {MCP_SERVER_NAME}

**{ONE_LINE_DESCRIPTION_WITH_MCP_INTEGRATION}**

{BRIEF_DESCRIPTION_OF_MCP_SERVER_CAPABILITIES}

## Quick Start

```bash
# 1. Navigate to server directory
cd {SERVER_DIRECTORY}

# 2. Install dependencies
uv sync  # or: pip install -e .

# 3. Configure environment
cp .env.example .env
# Edit .env with required API keys/settings
```

**Prerequisites**: Python 3.13+, UV/pip, {SPECIFIC_REQUIREMENTS}

## What You Get

- **🔌 MCP Integration**: Seamless Claude Code integration
- **⚡ {PRIMARY_CAPABILITY}**: {EXPLANATION}
- **🛠️ {SECONDARY_CAPABILITY}**: {EXPLANATION}
- **📊 {MONITORING_CAPABILITY}**: Comprehensive logging and debugging

## Test & Verify

```bash
# Quick health check
uv run python -m {MODULE_NAME}.server health_check

# Test with Claude Code
claude mcp call {SERVER_NAME} health_check
```

## Available Tools

### `{TOOL_NAME_1}`
{TOOL_DESCRIPTION}

**Parameters:**
- `{PARAM_1}` (required): {DESCRIPTION}
- `{PARAM_2}` (optional): {DESCRIPTION}

**Example:**
```bash
claude mcp call {SERVER_NAME} {TOOL_NAME_1} --{PARAM_1} "example"
```

### `{TOOL_NAME_2}`
{TOOL_DESCRIPTION}

**Parameters:**
- `{PARAM_1}` (required): {DESCRIPTION}

## Claude Code Integration

Add to your Claude Code configuration:

```json
{
  "mcpServers": {
    "{SERVER_NAME}": {
      "command": "uv",
      "args": ["run", "python", "-m", "{MODULE_NAME}.server"],
      "cwd": "{ABSOLUTE_PATH_TO_SERVER}",
      "env": {
        "{ENV_VAR}": "{VALUE}"
      }
    }
  }
}
```

## Configuration

### Environment Variables

```env
# {ENV_FILE_DESCRIPTION}
{ENV_VAR_1}=your_value_here
{ENV_VAR_2}=optional_value
```

### Advanced Configuration

{ADVANCED_CONFIG_IF_NEEDED}

## Troubleshooting

### Common Issues

**Issue**: {COMMON_PROBLEM}
**Solution**: {SOLUTION}

**Issue**: {ANOTHER_COMMON_PROBLEM}
**Solution**: {SOLUTION}

### Debug Mode

```bash
# Enable detailed logging
export {DEBUG_ENV_VAR}=true
uv run python -m {MODULE_NAME}.server
```

## Development

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov={MODULE_NAME}

# Type checking
uv run mypy {MODULE_NAME}
```

## Getting Help

- **📚 Documentation**: See main project [README](../../README.md)
- **🐛 Issues**: [Report MCP server issues]({ISSUES_LINK})
- **🔧 MCP Protocol**: [MCP Documentation](https://spec.modelcontextprotocol.io)

## License

{LICENSE_STATEMENT}

---

*MCP server for {DESCRIPTION}. Part of the AI Code Forge template system.*