# Perplexity MCP Server

**Add real-time web research capabilities to Claude Code with Perplexity AI integration.**

Transform Claude Code into a research powerhouse with live web search, current information access, and comprehensive analysis tools. Get up and running in under 2 minutes.

## What You Get

- **🔍 Real-time Web Search**: Access current information through Perplexity's live search
- **🧠 Multiple AI Models**: Choose from sonar, sonar-pro, sonar-reasoning, and sonar-deep-research
- **⚡ Quick Integration**: Plug-and-play setup with Claude Code MCP system
- **🔧 Flexible Configuration**: Custom system prompts and behavior tuning
- **📊 Debug & Monitoring**: Comprehensive logging and request tracking
- **🔒 Secure Setup**: Environment-based API key management

## Quick Start

```bash
# 1. Navigate to server directory
cd src/perplexity-mcp

# 2. Install dependencies
uv sync  # or: pip install -e .

# 3. Configure API key
cp .env.example .env
# Edit .env with your Perplexity API key
```

**Prerequisites**: Python 3.13+, UV/pip, [Perplexity API key](https://www.perplexity.ai/settings/api)

## Test & Verify

```bash
# Quick health check
uv run python -m perplexity_mcp.server health_check

# Test with Claude Code
claude mcp call perplexity-research health_check
```

```bash
# Run health check
uv run python -m perplexity_mcp.server health_check

# Or test directly
uv run python -c "
import asyncio
from perplexity_mcp.client import PerplexityClient

async def test():
    client = PerplexityClient()
    result = await client.health_check()
    print('✅ API accessible' if result else '❌ API not accessible')

asyncio.run(test())
"
```

### 5. Integrate with Claude Code

#### Option A: Command Line Setup

Add the server to your Claude Code configuration:

```bash
# Add server to Claude Code (replace with absolute path)
claude mcp add perplexity-research \
  -e PERPLEXITY_API_KEY=your_api_key_here \
  -- uv --directory /absolute/path/to/.support/mcp-servers/perplexity run src/perplexity_mcp/server.py

# Verify server is registered
claude mcp list

# Test the integration
claude mcp inspect perplexity-research
```

#### Option B: Configuration File Setup

Add this configuration to your Claude Code MCP settings file:

```json
{
  "mcpServers": {
    "perplexity-research": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/.support/mcp-servers/perplexity",
        "run",
        "src/perplexity_mcp/server.py"
      ],
      "env": {
        "PERPLEXITY_API_KEY": "your_api_key_here",
        "PERPLEXITY_LOG_LEVEL": "INFO"
      },
      "alwaysAllow": [
        "perplexity_search",
        "perplexity_deep_research", 
        "perplexity_quick_query",
        "list_models",
        "health_check"
      ]
    }
  }
}
```

**Configuration Notes:**
- Replace `/absolute/path/to/.support/mcp-servers/perplexity` with the actual absolute path to your Perplexity MCP server directory
- Add your actual Perplexity API key to the `PERPLEXITY_API_KEY` environment variable
- The `alwaysAllow` list enables auto-approval for all Perplexity tools
- Set `PERPLEXITY_LOG_LEVEL` to `DEBUG` for troubleshooting

#### Verify Installation

```bash
# Check MCP server status
claude mcp list

# Inspect available tools
claude mcp inspect perplexity-research

# Test basic functionality
claude mcp call perplexity-research health_check
```

## Available Tools

### 1. `perplexity_search`
General-purpose research with real-time web search.

**Parameters:**
- `query` (required): Research question or topic
- `model` (optional): Model to use (default: "sonar")
- `system_prompt` (optional): Custom instructions for response style
- `max_tokens` (optional): Maximum response length (default: 1000)
- `temperature` (optional): Response creativity (0.0-2.0, default: 0.7)

**Example:**
```python
# Quick research query
result = await perplexity_search(
    query="What are the latest developments in AI safety research?",
    model="sonar-pro"
)
```

### 2. `perplexity_deep_research`
Comprehensive multi-perspective research for complex topics.

**Parameters:**
- `topic` (required): Main research topic
- `focus_areas` (optional): Specific aspects to investigate
- `time_filter` (optional): Recency filter ("month", "week", "day")
- `domain_filter` (optional): Specific domains to search
- `max_tokens` (optional): Maximum response length (default: 1500)

**Example:**
```python
# Comprehensive research with focus areas
result = await perplexity_deep_research(
    topic="Quantum computing applications",
    focus_areas=["cryptography", "optimization", "machine learning"],
    time_filter="month",
    domain_filter=["arxiv.org", "nature.com"]
)
```

### 3. `perplexity_quick_query`
Fast, concise answers to specific questions.

**Parameters:**
- `question` (required): Specific question to ask
- `domain_filter` (optional): Limit search to specific domains
- `recency_filter` (optional): Time period for results

**Example:**
```python
# Quick factual query
result = await perplexity_quick_query(
    question="What is the current version of Python?",
    domain_filter=["python.org"],
    recency_filter="week"
)
```

### 4. `list_models`
Get information about available Perplexity models.

**Returns:** List of models with descriptions and usage recommendations.

### 5. `health_check`
Verify API connectivity and authentication.

**Returns:** Status message indicating API accessibility.

## Models Guide

### Available Models

- **sonar**: Fast, general-purpose model for most queries
- **sonar-pro**: Enhanced version with better reasoning capabilities
- **sonar-reasoning**: Optimized for logical reasoning and analysis
- **sonar-deep-research**: Most comprehensive model for in-depth research

### Model Selection Guide

| Use Case | Recommended Model | Why |
|----------|------------------|-----|
| Quick facts | `sonar` | Fast response, good for simple queries |
| General research | `sonar-pro` | Better quality with reasonable speed |
| Problem solving | `sonar-reasoning` | Optimized for step-by-step analysis |
| Comprehensive analysis | `sonar-deep-research` | Highest quality, multiple perspectives |

## Configuration

### Environment Variables

#### Required Configuration
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PERPLEXITY_API_KEY` | Your Perplexity API key | - | Yes |

#### Logging Configuration
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PERPLEXITY_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | INFO | No |
| `PERPLEXITY_LOG_PATH` | Base directory for all log files | ./logs | No |
| `PERPLEXITY_LOG_FILE` | Main application log file name | perplexity_mcp.log | No |
| `PERPLEXITY_DEBUG_LOG_FILE` | Verbose debug log file name | perplexity_debug.log | No |
| `PERPLEXITY_API_LOG_FILE` | API request/response log file name | perplexity_api.log | No |
| `PERPLEXITY_ERROR_LOG_FILE` | Error and exception log file name | perplexity_errors.log | No |

#### API Configuration
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PERPLEXITY_TIMEOUT` | Request timeout in seconds | 60.0 | No |
| `PERPLEXITY_DEFAULT_MODEL` | Default model for queries | sonar | No |
| `PERPLEXITY_DEFAULT_SYSTEM` | Default system message | (built-in) | No |

### Example Configuration

```bash
# .env file - Basic Configuration
PERPLEXITY_API_KEY=pplx-abcd1234567890abcdef
PERPLEXITY_LOG_LEVEL=INFO
PERPLEXITY_DEFAULT_MODEL=sonar-pro

# Enhanced Logging Configuration
PERPLEXITY_LOG_PATH=/var/log/perplexity
PERPLEXITY_LOG_FILE=main.log
PERPLEXITY_DEBUG_LOG_FILE=debug.log
PERPLEXITY_API_LOG_FILE=api_calls.log
PERPLEXITY_ERROR_LOG_FILE=errors.log

# API Customization
PERPLEXITY_TIMEOUT=120.0
PERPLEXITY_DEFAULT_SYSTEM="Provide detailed, technical responses with citations."
```

### Logging System Features

The enhanced logging system provides multiple specialized log files:

#### 1. **Main Log** (`perplexity_mcp.log`)
- Application lifecycle events
- Tool execution status
- Performance metrics
- High-level operation flow

#### 2. **Debug Log** (`perplexity_debug.log`)
- Verbose function entry/exit tracking
- Parameter values and internal state
- Detailed execution flow
- Function duration measurements

#### 3. **API Log** (`perplexity_api.log`)
- Structured request/response logging
- Request correlation IDs
- API timing and performance data
- Rate limiting and error tracking
- Sanitized payload information (sensitive data redacted)

#### 4. **Error Log** (`perplexity_errors.log`)
- Exception stack traces
- Error context and debugging information
- API failure details
- Network and authentication issues

#### Log Format Examples

**Main Log:**
```
2025-08-02 10:30:15.123 - perplexity_mcp - INFO - perplexity_search:65 - Research request: What are the latest AI developments...
```

**API Log (structured JSON):**
```json
{
  "request_id": "req_1722596215123_4567",
  "timestamp": "2025-08-02T10:30:15.123456",
  "type": "request",
  "method": "POST",
  "url": "https://api.perplexity.ai/chat/completions",
  "headers": {"authorization": "[REDACTED]"},
  "data": {"model": "sonar-pro", "messages_info": {"count": 2, "lengths": [45, 234]}}
}
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=perplexity_mcp --cov-report=html

# Run specific test file
uv run pytest tests/test_client.py -v

# Run tests with live API (requires valid API key)
PERPLEXITY_API_KEY=your_key uv run pytest tests/test_integration.py -v
```

### Project Structure

```
.support/mcp-servers/perplexity/
├── src/perplexity_mcp/           # Main package
│   ├── __init__.py               # Package initialization
│   ├── server.py                 # FastMCP server implementation
│   ├── client.py                 # Perplexity API client
│   ├── main.py                   # Entry point
│   └── utils/                    # Utility modules
│       ├── __init__.py
│       └── logging.py            # Logging configuration
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest configuration
│   ├── test_client.py           # Client tests
│   ├── test_server.py           # Server tests
│   └── test_logging.py          # Logging tests
├── pyproject.toml               # Project configuration
├── .env.example                 # Environment template
└── README.md                    # This file
```

### Adding New Features

1. **Add API functionality**: Extend `client.py` with new methods
2. **Create MCP tools**: Add new tools in `server.py` using `@mcp.tool()` decorator
3. **Write tests**: Add comprehensive tests in `tests/` directory
4. **Update documentation**: Update this README and docstrings

### Code Quality

The project follows Python best practices:

- **Type hints**: Full type annotation coverage
- **Error handling**: Comprehensive error handling with logging
- **Testing**: High test coverage with mocks and integration tests
- **Documentation**: Detailed docstrings and comments
- **Logging**: Structured logging with configurable levels

## Troubleshooting

### Common Issues

#### 1. Authentication Errors
```
Error: Authentication failed. Check your API key.
```
**Solution:**
- Verify your API key in `.env` file
- Check that the key is valid on Perplexity's website
- Ensure no extra spaces in the environment variable

#### 2. Rate Limit Exceeded
```
Error: Rate limit exceeded. Please try again later.
```
**Solution:**
- Wait before making additional requests
- Consider upgrading your Perplexity plan
- Implement request throttling in your usage

#### 3. Network Connection Issues
```
Error: Network error: Connection timeout
```
**Solution:**
- Check internet connection
- Verify firewall/proxy settings
- Try with different network if available

#### 4. Claude Code Integration Issues
```
Error: Server not responding
```
**Solution:**
- Ensure absolute path is used in Claude Code configuration
- Verify UV is installed and accessible
- Check that all dependencies are installed
- Test server independently first

### Debug Mode

The enhanced logging system provides comprehensive debugging capabilities:

#### Enable Debug Logging

```bash
# Set environment variables for maximum debugging
export PERPLEXITY_LOG_LEVEL=DEBUG
export PERPLEXITY_LOG_PATH=/tmp/perplexity_debug

# Or in .env file
PERPLEXITY_LOG_LEVEL=DEBUG
PERPLEXITY_LOG_PATH=/tmp/perplexity_debug
PERPLEXITY_DEBUG_LOG_FILE=verbose_debug.log
PERPLEXITY_API_LOG_FILE=api_detailed.log
```

#### Debug Log Analysis

1. **Monitor API Calls:**
```bash
# Watch API request/response flow
tail -f /tmp/perplexity_debug/api_detailed.log | grep -E '(REQUEST|RESPONSE)'
```

2. **Track Function Performance:**
```bash
# Monitor function execution times
tail -f /tmp/perplexity_debug/verbose_debug.log | grep -E '(ENTER|EXIT).*duration'
```

3. **Analyze Errors:**
```bash
# Review error patterns
tail -f /tmp/perplexity_debug/errors.log
```

#### Troubleshooting Network Issues

For deep research tool network errors, enable maximum logging:

```bash
# .env configuration for network debugging
PERPLEXITY_LOG_LEVEL=DEBUG
PERPLEXITY_TIMEOUT=120.0  # Increase timeout
PERPLEXITY_LOG_PATH=/var/log/perplexity/network_debug

# Then monitor logs:
tail -f /var/log/perplexity/network_debug/api_detailed.log | grep 'deep-research'
```

### Health Check

```bash
# Test API connectivity
uv run python -c "
import asyncio
from perplexity_mcp.server import health_check

async def test():
    result = await health_check()
    print(result)

asyncio.run(test())
"
```

## API Costs and Limits

### Pricing Overview
- **Request-based**: ~$5 per 1,000 requests
- **Token-based**: $0.2-$5 per 1M tokens (model dependent)
- **Pro Plan**: $20/month with $5 monthly credits included

### Rate Limits
- **Free tier**: Limited requests per month
- **Pro tier**: Higher limits with burst capacity
- **Rate limit resets**: Typically monthly

### Cost Optimization Tips
1. **Use appropriate models**: `sonar` for simple queries, `sonar-deep-research` only when needed
2. **Set max_tokens**: Limit response length to control costs
3. **Cache results**: Store frequent query results locally
4. **Monitor usage**: Track API calls and token consumption

## Security Considerations

### API Key Security
- **Never commit** API keys to version control
- **Use environment variables** for configuration
- **Rotate keys regularly** as security best practice
- **Limit API key scope** if possible on Perplexity's platform

### Input Validation
- The server validates and sanitizes all inputs
- **Prompt injection** protection through parameterized queries
- **Rate limiting** on the client side to prevent abuse

### Network Security
- **HTTPS only**: All API communications use secure connections
- **No sensitive data logging**: API keys and sensitive content not logged
- **Error handling**: Errors don't expose sensitive information

## Contributing

This MCP server is part of the Claude Code template project. To contribute:

1. **Follow the existing code style** and patterns
2. **Add comprehensive tests** for new features
3. **Update documentation** including this README
4. **Test with Claude Code** integration before submitting
5. **Follow the project's git protocol** for commits

## License

This project is part of the Claude Code template and follows the same licensing terms.

## Support

For support with this MCP server:

1. **Check this README** for common solutions
2. **Review the logs** with debug mode enabled
3. **Test API connectivity** independently
4. **Check Perplexity API status** and documentation
5. **Report issues** through the main project repository

## Changelog

### v0.1.0 (Initial Release)
- ✅ Perplexity API integration with all models
- ✅ FastMCP server implementation
- ✅ Comprehensive tool set (search, research, quick query)
- ✅ Environment-based configuration
- ✅ Comprehensive test suite
- ✅ Claude Code compatibility with stdio transport
- ✅ Detailed documentation and troubleshooting guide

### v0.2.0 (Enhanced Logging)
- ✅ **Enhanced Debug Logging**: Multi-file logging system with configurable paths
- ✅ **API Request Tracking**: Structured JSON logging for all API calls
- ✅ **Performance Monitoring**: Function-level timing and performance metrics
- ✅ **Error Analysis**: Dedicated error logging with full context
- ✅ **Troubleshooting Tools**: Comprehensive debugging capabilities
- ✅ **Environment Configuration**: Extensive configuration options via environment variables
- ✅ **Log Security**: Automatic redaction of sensitive information in logs