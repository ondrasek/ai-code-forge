# AI Code Forge MCP Server Configuration

This directory contains the centralized MCP (Model Context Protocol) server configuration for AI Code Forge. The `launch-claude.sh` script automatically loads this configuration to enable enhanced capabilities in Claude Code.

## Available MCP Servers

### 1. OpenAI Structured Output Server
**Name**: `openai-structured`  
**Purpose**: Provides reliable structured JSON responses with schema validation  
**Location**: `mcp-servers/openai-structured-mcp/`

**Features**:
- Data extraction with confidence scoring
- Code analysis with metrics
- Task breakdown with structured steps
- Sentiment analysis with emotional breakdown
- Guaranteed JSON format compliance

**Setup**:
1. Obtain an OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Set the environment variable: `export OPENAI_API_KEY="your-key-here"`
3. Or create a `.env` file in `mcp-servers/openai-structured-mcp/.env`

### 2. Perplexity Research Server
**Name**: `perplexity`  
**Purpose**: Real-time web research and current information access  
**Location**: `mcp-servers/perplexity-mcp/`

**Features**:
- Real-time web search capabilities
- Multiple AI models (sonar, sonar-pro, sonar-reasoning, sonar-deep-research)
- Current information access
- Comprehensive research tools

**Setup**:
1. Get a Perplexity API key from [Perplexity Settings](https://www.perplexity.ai/settings/api)
2. Set the environment variable: `export PERPLEXITY_API_KEY="your-key-here"`
3. Or create a `.env` file in `mcp-servers/perplexity-mcp/.env`

## Configuration File

The `mcp-config.json` file defines how Claude Code connects to these MCP servers:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "uv",
      "args": ["run", "--directory", "path/to/server", "server-command"],
      "env": {
        "API_KEY": "",
        "MCP_LOG_LEVEL": "info"
      },
      "disabled": false,
      "alwaysAllow": ["*"],
      "description": "Server description"
    }
  }
}
```

### Configuration Options

- **command**: The command to start the server (using `uv` for Python package management)
- **args**: Arguments passed to the command
- **env**: Environment variables (API keys should be set externally)
- **disabled**: Set to `true` to disable a server without removing its configuration
- **alwaysAllow**: Permissions for server actions (`["*"]` allows all)
- **description**: Human-readable description of the server

## Usage

1. **Install Dependencies**: Each MCP server has its own dependencies
   ```bash
   # Install OpenAI Structured server
   cd mcp-servers/openai-structured-mcp
   uv sync
   
   # Install Perplexity server  
   cd ../perplexity-mcp
   uv sync
   ```

2. **Set API Keys**: Configure your API keys as environment variables
   ```bash
   export OPENAI_API_KEY="sk-..."
   export PERPLEXITY_API_KEY="pplx-..."
   ```

3. **Launch Claude Code**: The `launch-claude.sh` script automatically detects and loads the MCP configuration
   ```bash
   ./scripts/launch-claude.sh
   ```

## Troubleshooting

### Server Connection Issues
- Verify API keys are set correctly
- Check server dependencies are installed (`uv sync`)
- Review MCP debug logs in session directories

### Debug Mode
Enable MCP debug logging:
```bash
./scripts/launch-claude.sh --mcp-debug
```

### Troubleshoot MCP Issues
Use the built-in troubleshooting feature:
```bash
./scripts/launch-claude.sh --troubleshoot-mcp
```

## Security Notes

- **API Keys**: Never commit API keys to version control
- **Environment Variables**: Use environment variables or `.env` files for sensitive data
- **Permissions**: The `alwaysAllow: ["*"]` setting grants full permissions - adjust as needed
- **Network**: MCP servers make external API calls - ensure network access is available

## Adding New Servers

1. Create your MCP server in `mcp-servers/your-server-name/`
2. Add entry to `mcp-config.json`
3. Document setup requirements
4. Test with `launch-claude.sh`

## File Locations

- **Primary Config**: `mcp-servers/mcp-config.json` (this file)
- **Legacy Location**: `.mcp.json` (root directory, for backward compatibility)
- **Server Source**: `mcp-servers/` directory
- **Logs**: Session directories created by `launch-claude.sh`

The `launch-claude.sh` script checks for configuration files in priority order and automatically loads the first one found.