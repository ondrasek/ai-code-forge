"""Enhanced logging utilities for OpenAI Structured MCP server with extensive debug capabilities."""

import logging
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from functools import wraps


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    logger_name: str = "openai_structured_mcp"
) -> logging.Logger:
    """
    Set up logging configuration for the MCP server.
    
    Environment Variables:
        OPENAI_STRUCTURED_LOG_LEVEL: Logging level (INFO, DEBUG, WARNING, ERROR, CRITICAL, none)
                                     Set to "none" to disable logging completely
        OPENAI_STRUCTURED_LOG_PATH: Base directory for log files (required if logging enabled)
    
    Args:
        log_level: Default logging level (overridden by OPENAI_STRUCTURED_LOG_LEVEL)
        log_file: Optional file path for logging output
        logger_name: Name of the logger
        
    Returns:
        Configured logger instance
        
    Raises:
        ValueError: If logging is enabled but OPENAI_STRUCTURED_LOG_PATH is invalid
        OSError: If logging is enabled but log directory cannot be created
        PermissionError: If logging is enabled but log directory is not writable
    """
    logger = logging.getLogger(logger_name)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Check if logging is explicitly disabled
    env_log_level = os.getenv("OPENAI_STRUCTURED_LOG_LEVEL", log_level).upper()
    if env_log_level == "NONE" or not env_log_level:
        # Logging explicitly disabled
        logger.disabled = True
        setup_api_logging(None)
        return logger
    
    # Validate log level
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if env_log_level not in valid_levels:
        raise ValueError(f"Invalid OPENAI_STRUCTURED_LOG_LEVEL '{env_log_level}'. Must be one of: {valid_levels} or 'none'")
    
    logger.setLevel(getattr(logging, env_log_level))
    
    # Logging is enabled - require valid log path
    base_log_path = os.getenv("OPENAI_STRUCTURED_LOG_PATH")
    if not base_log_path:
        raise ValueError("OPENAI_STRUCTURED_LOG_PATH must be set when logging is enabled. Set OPENAI_STRUCTURED_LOG_LEVEL=none to disable logging.")
    
    # Convert relative paths to absolute based on repository root
    if not os.path.isabs(base_log_path):
        # Find repository root by going up from current working directory
        current_dir = Path.cwd()
        repo_root = current_dir
        
        # Walk up until we find .git directory or reach filesystem root
        while repo_root.parent != repo_root:
            if (repo_root / '.git').exists():
                break
            repo_root = repo_root.parent
        
        # If no .git found, assume we're already in repo root
        if not (repo_root / '.git').exists():
            repo_root = current_dir
            
        base_log_path = str(repo_root / base_log_path)
    
    session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = f"{base_log_path.rstrip('/')}/openai_structured_{session_timestamp}"
    
    # Create log directory - fail fast if it cannot be created
    try:
        Path(log_path).mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError) as e:
        raise OSError(f"Failed to create log directory '{log_path}': {e}. Check permissions and disk space.") from e
    
    # Test write permissions
    test_file = Path(log_path) / "write_test.tmp"
    try:
        test_file.write_text("test")
        test_file.unlink()
    except (OSError, PermissionError) as e:
        raise PermissionError(f"Log directory '{log_path}' is not writable: {e}") from e
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Single log file for all logging
    log_file_path = log_file or os.path.join(log_path, "openai_structured.log")
    try:
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(detailed_formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        logger.info(f"Logging to: {log_file_path}")
    except (OSError, IOError) as e:
        logger.warning(f"Could not create log handler for {log_file_path}: {e}")
    
    # Initialize API logging in same directory
    setup_api_logging(log_path)
    
    return logger


def setup_api_logging(log_path: Optional[str]) -> logging.Logger:
    """
    Set up dedicated API request/response logging.
    
    Args:
        log_path: Base directory for log files (None if file logging disabled)
        
    Returns:
        API logger instance
    """
    api_logger = logging.getLogger("openai_structured_api")
    api_logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    api_logger.handlers.clear()
    
    # Only set up file logging if log_path is available
    if log_path:
        api_log_file = os.path.join(log_path, "api.log")
        try:
            api_handler = logging.FileHandler(api_log_file)
            api_formatter = logging.Formatter(
                fmt='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            api_handler.setFormatter(api_formatter)
            api_logger.addHandler(api_handler)
            api_logger.debug(f"API logging to: {api_log_file}")
        except (OSError, IOError) as e:
            main_logger = logging.getLogger("openai_structured_mcp")
            main_logger.warning(f"Could not create API log handler for {api_log_file}: {e}")
    else:
        # Disable API logging if no log path
        api_logger.disabled = True
    
    return api_logger


def get_logger(name: str = "openai_structured_mcp") -> logging.Logger:
    """Get or create a logger instance."""
    return logging.getLogger(name)


def get_api_logger() -> logging.Logger:
    """Get the dedicated API logger instance."""
    return logging.getLogger("openai_structured_api")


def log_api_request(method: str, url: str, headers: Dict[str, Any], data: Dict[str, Any]) -> str:
    """
    Log API request details in structured format.
    
    Args:
        method: HTTP method
        url: Request URL
        headers: Request headers (sensitive data will be redacted)
        data: Request payload
        
    Returns:
        Request ID for correlation
    """
    api_logger = get_api_logger()
    request_id = f"req_{int(time.time() * 1000)}_{id(data) % 10000}"
    
    # Redact sensitive information
    safe_headers = {k: "[REDACTED]" if "authorization" in k.lower() or "key" in k.lower() else v 
                    for k, v in headers.items()}
    
    safe_data = data.copy()
    if "messages" in safe_data and isinstance(safe_data["messages"], list):
        # Log message count and lengths instead of full content for privacy
        safe_data["messages_info"] = {
            "count": len(safe_data["messages"]),
            "lengths": [len(str(msg.get("content", ""))) for msg in safe_data["messages"]]
        }
        safe_data["messages"] = "[CONTENT_REDACTED_FOR_PRIVACY]"
    
    # Redact response_format schema details but keep structure info
    if "response_format" in safe_data and isinstance(safe_data["response_format"], dict):
        response_format = safe_data["response_format"]
        if "json_schema" in response_format:
            safe_data["response_format"]["json_schema_info"] = {
                "name": response_format.get("json_schema", {}).get("name"),
                "strict": response_format.get("json_schema", {}).get("strict"),
                "schema_keys": list(response_format.get("json_schema", {}).get("schema", {}).keys())
            }
            safe_data["response_format"]["json_schema"] = "[SCHEMA_REDACTED_FOR_SIZE]"
    
    request_log = {
        "request_id": request_id,
        "timestamp": datetime.now().isoformat(),
        "type": "request",
        "method": method,
        "url": url,
        "headers": safe_headers,
        "data": safe_data
    }
    
    api_logger.debug(f"API_REQUEST: {json.dumps(request_log, indent=2)}")
    return request_id


def log_api_response(request_id: str, status_code: int, response_data: Dict[str, Any], 
                    duration_ms: float, error: Optional[str] = None) -> None:
    """
    Log API response details in structured format.
    
    Args:
        request_id: Correlation ID from request
        status_code: HTTP status code
        response_data: Response payload
        duration_ms: Request duration in milliseconds
        error: Optional error message
    """
    api_logger = get_api_logger()
    
    safe_response = response_data.copy() if response_data else {}
    
    # Redact potentially large content but keep metadata
    if "choices" in safe_response and isinstance(safe_response["choices"], list):
        safe_response["choices_info"] = {
            "count": len(safe_response["choices"]),
            "content_lengths": [len(str(choice.get("message", {}).get("content", ""))) 
                               for choice in safe_response["choices"]],
            "finish_reasons": [choice.get("finish_reason") for choice in safe_response["choices"]]
        }
        safe_response["choices"] = "[CONTENT_REDACTED_FOR_SIZE]"
    
    response_log = {
        "request_id": request_id,
        "timestamp": datetime.now().isoformat(),
        "type": "response",
        "status_code": status_code,
        "duration_ms": duration_ms,
        "response": safe_response,
        "error": error,
        "success": status_code < 400 and error is None
    }
    
    api_logger.debug(f"API_RESPONSE: {json.dumps(response_log, indent=2)}")


def debug_decorator(func):
    """
    Decorator to add extensive debug logging to functions.
    
    Args:
        func: Function to wrap with debug logging
        
    Returns:
        Wrapped function with debug logging
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        logger = get_logger()
        func_name = f"{func.__module__}.{func.__name__}"
        
        # Log function entry
        logger.debug(f"ENTER {func_name} with args={len(args)}, kwargs={list(kwargs.keys())}")
        
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            logger.debug(f"EXIT {func_name} - SUCCESS - duration={duration:.2f}ms")
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.debug(f"EXIT {func_name} - ERROR - duration={duration:.2f}ms - error={type(e).__name__}: {str(e)}")
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        logger = get_logger()
        func_name = f"{func.__module__}.{func.__name__}"
        
        # Log function entry
        logger.debug(f"ENTER {func_name} with args={len(args)}, kwargs={list(kwargs.keys())}")
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            logger.debug(f"EXIT {func_name} - SUCCESS - duration={duration:.2f}ms")
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.debug(f"EXIT {func_name} - ERROR - duration={duration:.2f}ms - error={type(e).__name__}: {str(e)}")
            raise
    
    # Return appropriate wrapper based on whether function is async
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper