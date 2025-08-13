# Technical Analysis: Codex CLI MCP Server Implementation

**Issue**: #170 - feat: implement codex-cli-mcp server for OpenAI Codex CLI integration  
**Date**: 2025-08-13  
**Analyst**: Technology Guidelines Agent

## Repository-Level Technology Analysis

**Primary Technology**: Python (MCP server implementation)  
**Secondary Technologies**: Subprocess Management, JSON Schema Validation, Async/Await Patterns  
**Context**: Wrapping OpenAI Codex CLI as MCP tools within existing MCP server ecosystem

## Technology Stack Guidelines Loaded

### Python Development Standards
**Guidelines**: `cli/src/ai_code_forge/data/acf/templates/stacks/python.md`

**Key Mandatory Patterns for this Implementation**:
- **MANDATORY**: Use uv exclusively for package management (NO pip, poetry, conda)
- **REQUIRED**: Type hints for all functions and methods
- **ENFORCE**: PEP 8 compliance with ruff formatting
- **MANDATORY**: Explicit error handling - never bare except clauses
- **REQUIRED**: Context managers for resource management
- **ENFORCE**: pathlib for all file operations
- **MANDATORY**: Dataclasses for data structures
- **REQUIRE**: Test coverage minimum 80%

## Technology-Specific Implementation Guidelines

### 1. Python MCP Server Development Patterns

Based on existing implementations (`openai-structured-mcp`, `perplexity-mcp`):

**MANDATORY Architecture Pattern**:
```python
from fastmcp import FastMCP
from .client import CodexClient
from .utils.logging import setup_logging, get_logger, debug_decorator

mcp = FastMCP("Codex CLI Server")

@mcp.tool(annotations={...})
@debug_decorator
async def codex_query(prompt: str, ...) -> str:
    # Implementation follows existing pattern
```

**ENFORCE Consistent Structure**:
- `src/codex_cli_mcp/server.py` - Main FastMCP server
- `src/codex_cli_mcp/client.py` - Subprocess wrapper for Codex CLI
- `src/codex_cli_mcp/utils/logging.py` - Consistent logging patterns
- `src/codex_cli_mcp/schemas.py` - JSON schema definitions (if needed)

### 2. Subprocess Management and Process Control

**MANDATORY Subprocess Security Patterns**:
```python
import asyncio
import subprocess
from pathlib import Path
from typing import Optional

async def execute_codex_command(
    args: list[str], 
    timeout: float = 60.0,
    cwd: Optional[Path] = None
) -> subprocess.CompletedProcess:
    """Execute Codex CLI with proper security and timeout handling."""
    try:
        # ENFORCE input sanitization
        sanitized_args = [str(arg) for arg in args if is_safe_arg(arg)]
        
        # MANDATORY timeout and security
        process = await asyncio.create_subprocess_exec(
            *sanitized_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(), 
            timeout=timeout
        )
        
        return subprocess.CompletedProcess(
            args=sanitized_args,
            returncode=process.returncode,
            stdout=stdout,
            stderr=stderr
        )
        
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        raise TimeoutError(f"Codex CLI command timed out after {timeout}s")
```

### 3. Async/Await Patterns for MCP Servers

**MANDATORY Async Tool Implementation**:
```python
@mcp.tool(annotations={
    "title": "Codex Query",
    "description": "Execute Codex CLI query with structured output",
    "readOnlyHint": True,
    "openWorldHint": False
})
@debug_decorator
async def codex_query(
    prompt: str,
    context: Optional[str] = None,
    model: Optional[str] = None,
    timeout: float = 60.0
) -> str:
    """Execute Codex CLI query with proper async handling."""
    logger.info(f"Codex query request: {len(prompt)} characters")
    
    try:
        result = await codex_client.query(
            prompt=prompt,
            context=context,
            model=model,
            timeout=timeout
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.decode()
            logger.error(f"Codex CLI error: {error_msg}")
            return f"Codex CLI failed: {error_msg}"
        
        # Parse and structure output
        output = result.stdout.decode()
        logger.info("Codex query completed successfully")
        return output
        
    except Exception as e:
        error_msg = f"Error during Codex query: {str(e)}"
        logger.error(error_msg)
        return error_msg
```

### 4. Error Handling and Logging Best Practices

**MANDATORY Error Handling Pattern** (from existing MCP servers):
```python
# Initialize logging with environment configuration
try:
    logger = setup_logging(
        log_level=os.getenv("CODEX_CLI_LOG_LEVEL", "INFO"),
        logger_name="codex_cli_mcp"
    )
except (ValueError, OSError, PermissionError) as e:
    import sys
    print(f"FATAL: Logging configuration error: {e}", file=sys.stderr)
    sys.exit(1)

# ENFORCE structured error responses
def handle_cli_error(result: subprocess.CompletedProcess, operation: str) -> str:
    """Convert CLI errors to structured MCP responses."""
    if result.returncode == 0:
        return result.stdout.decode()
    
    stderr_output = result.stderr.decode()
    logger.error(f"Codex CLI {operation} failed: {stderr_output}")
    
    # MANDATORY: Filter sensitive information from logs
    filtered_error = filter_sensitive_info(stderr_output)
    return f"Error in {operation}: {filtered_error}"
```

### 5. Security Patterns for Credential Handling

**MANDATORY Secure Authentication**:
```python
import os
from dotenv import load_dotenv

load_dotenv()

class CodexClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable required")
        
        # ENFORCE: Never log credentials
        logger.info("Codex client initialized")
        # FORBIDDEN: logger.debug(f"Using API key: {self.api_key}")

    async def execute_with_auth(self, args: list[str]) -> subprocess.CompletedProcess:
        """Execute Codex CLI with secure credential handling."""
        env = os.environ.copy()
        env["OPENAI_API_KEY"] = self.api_key
        
        # ENFORCE input sanitization
        if not all(self.is_safe_arg(arg) for arg in args):
            raise ValueError("Unsafe command arguments detected")
        
        return await execute_codex_command(args, env=env)

    def is_safe_arg(self, arg: str) -> bool:
        """Validate command line arguments for safety."""
        # MANDATORY: Prevent command injection
        dangerous_chars = [";", "&", "|", "`", "$", "(", ")", "<", ">"]
        return not any(char in str(arg) for char in dangerous_chars)
```

### 6. Testing Patterns for Subprocess-Based Integrations

**MANDATORY Testing Structure**:
```python
import pytest
import asyncio
from unittest.mock import Mock, patch
from codex_cli_mcp.client import CodexClient

@pytest.mark.asyncio
async def test_codex_query_success():
    """Test successful Codex CLI execution."""
    mock_process = Mock()
    mock_process.returncode = 0
    mock_process.stdout = b"Generated code output"
    mock_process.stderr = b""
    
    with patch('asyncio.create_subprocess_exec') as mock_exec:
        mock_exec.return_value.communicate.return_value = (b"output", b"")
        mock_exec.return_value.returncode = 0
        
        client = CodexClient()
        result = await client.query("test prompt")
        
        assert "Generated code output" in result

@pytest.mark.asyncio
async def test_codex_query_timeout():
    """Test timeout handling."""
    with patch('asyncio.wait_for', side_effect=asyncio.TimeoutError):
        client = CodexClient()
        
        with pytest.raises(TimeoutError):
            await client.query("test prompt", timeout=1.0)
```

### 7. JSON Schema and Type Validation

**MANDATORY Type Definitions**:
```python
from dataclasses import dataclass
from typing import Optional, Dict, Any
import jsonschema

@dataclass
class CodexRequest:
    prompt: str
    context: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

@dataclass
class CodexResponse:
    content: str
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

# ENFORCE JSON schema validation
CODEX_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "prompt": {"type": "string", "minLength": 1},
        "context": {"type": "string"},
        "model": {"type": "string"},
        "temperature": {"type": "number", "minimum": 0, "maximum": 2}
    },
    "required": ["prompt"]
}

def validate_request(data: dict) -> None:
    """Validate request against schema."""
    try:
        jsonschema.validate(data, CODEX_REQUEST_SCHEMA)
    except jsonschema.ValidationError as e:
        raise ValueError(f"Invalid request format: {e.message}")
```

### 8. Configuration Management Patterns

**MANDATORY Configuration Structure**:
```python
import os
from dataclasses import dataclass
from pathlib import Path

@dataclass
class CodexConfig:
    api_key: str
    log_level: str = "INFO"
    log_path: Optional[Path] = None
    timeout: float = 60.0
    max_tokens: int = 2048
    default_model: str = "gpt-4"

def load_config() -> CodexConfig:
    """Load configuration from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable required")
    
    return CodexConfig(
        api_key=api_key,
        log_level=os.getenv("CODEX_CLI_LOG_LEVEL", "INFO"),
        log_path=Path(path) if (path := os.getenv("CODEX_CLI_LOG_PATH")) else None,
        timeout=float(os.getenv("CODEX_CLI_TIMEOUT", "60.0")),
        max_tokens=int(os.getenv("CODEX_CLI_MAX_TOKENS", "2048")),
        default_model=os.getenv("CODEX_CLI_DEFAULT_MODEL", "gpt-4")
    )
```

## Integration with Existing MCP Infrastructure

### Project Structure Consistency
**ENFORCE** alignment with existing MCP servers:
```
mcp-servers/codex-cli-mcp/
├── src/codex_cli_mcp/
│   ├── __init__.py
│   ├── main.py
│   ├── server.py          # FastMCP server definition
│   ├── client.py          # Codex CLI subprocess wrapper
│   ├── schemas.py         # JSON schemas and validation
│   └── utils/
│       ├── __init__.py
│       └── logging.py     # Consistent logging setup
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_server.py
│   ├── test_client.py
│   ├── test_error_handling.py
│   └── test_security.py
├── pyproject.toml         # uv-managed dependencies
├── README.md
└── uv.lock
```

### Required Dependencies
**MANDATORY** (following existing patterns):
```toml
[project]
dependencies = [
    "fastmcp>=2.0",
    "httpx",
    "python-dotenv",
    "pydantic>=2.0",
    "jsonschema>=4.0"
]

[tool.uv]
dev-dependencies = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "pytest-mock>=3.12",
    "pytest-cov>=4.0",
    "psutil>=5.9.0"
]
```

## Critical Implementation Considerations

### Security Risks to Address
1. **Command Injection**: Strict input sanitization for CLI arguments
2. **Credential Exposure**: Never log API keys or sensitive data
3. **Process Isolation**: Proper subprocess cleanup and resource management
4. **Output Filtering**: Sanitize CLI outputs before returning to user

### Performance Considerations
1. **Timeout Management**: Configurable timeouts for different operations
2. **Resource Cleanup**: Proper subprocess termination and cleanup
3. **Async Efficiency**: Non-blocking subprocess execution
4. **Memory Management**: Handle large CLI outputs appropriately

### Testing Strategy
1. **Unit Tests**: Mock subprocess calls for isolated testing
2. **Integration Tests**: Test with actual Codex CLI (if available)
3. **Security Tests**: Validate input sanitization and credential handling
4. **Performance Tests**: Timeout and resource usage validation

## Conclusion

This implementation must follow existing MCP server patterns while adding robust subprocess management and security measures specific to CLI tool wrapping. The Python stack guidelines mandate uv usage, comprehensive type hints, and 80% test coverage. Security considerations are paramount when wrapping external CLI tools with API access.

**Next Steps**: Create the MCP server following this technical analysis and existing implementation patterns.