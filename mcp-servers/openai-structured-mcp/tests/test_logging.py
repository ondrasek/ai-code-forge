"""Tests for logging utilities."""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import logging

from openai_structured_mcp.utils.logging import (
    setup_logging,
    setup_api_logging,
    get_logger,
    get_api_logger,
    log_api_request,
    log_api_response,
    debug_decorator
)


class TestLoggingSetup:
    """Test logging setup functionality."""
    
    def test_setup_logging_disabled(self):
        """Test logging setup when disabled."""
        with patch.dict(os.environ, {"OPENAI_STRUCTURED_LOG_LEVEL": "NONE"}):
            logger = setup_logging()
            assert logger.disabled is True
    
    def test_setup_logging_no_log_level(self):
        """Test logging setup with empty log level."""
        with patch.dict(os.environ, {"OPENAI_STRUCTURED_LOG_LEVEL": ""}):
            logger = setup_logging()
            assert logger.disabled is True
    
    def test_setup_logging_invalid_log_level(self):
        """Test logging setup with invalid log level."""
        with patch.dict(os.environ, {"OPENAI_STRUCTURED_LOG_LEVEL": "INVALID"}):
            with pytest.raises(ValueError, match="Invalid OPENAI_STRUCTURED_LOG_LEVEL"):
                setup_logging()
    
    def test_setup_logging_no_log_path(self):
        """Test logging setup without log path when logging enabled."""
        with patch.dict(os.environ, {
            "OPENAI_STRUCTURED_LOG_LEVEL": "INFO",
            "OPENAI_STRUCTURED_LOG_PATH": ""
        }, clear=True):
            with pytest.raises(ValueError, match="OPENAI_STRUCTURED_LOG_PATH must be set"):
                setup_logging()
    
    def test_setup_logging_with_temp_directory(self):
        """Test logging setup with temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {
                "OPENAI_STRUCTURED_LOG_LEVEL": "DEBUG",
                "OPENAI_STRUCTURED_LOG_PATH": temp_dir
            }):
                logger = setup_logging()
                
                assert logger.disabled is False
                assert logger.level == logging.DEBUG
                assert len(logger.handlers) > 0
                
                # Check that log directory was created
                log_dirs = [d for d in Path(temp_dir).iterdir() if d.is_dir() and d.name.startswith("openai_structured_")]
                assert len(log_dirs) == 1
    
    def test_setup_logging_invalid_directory_permissions(self):
        """Test logging setup with invalid directory permissions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a read-only directory
            readonly_dir = Path(temp_dir) / "readonly"
            readonly_dir.mkdir()
            readonly_dir.chmod(0o444)  # Read-only
            
            try:
                with patch.dict(os.environ, {
                    "OPENAI_STRUCTURED_LOG_LEVEL": "INFO",
                    "OPENAI_STRUCTURED_LOG_PATH": str(readonly_dir / "logs")
                }):
                    with pytest.raises(OSError, match="Failed to create log directory"):
                        setup_logging()
            finally:
                # Restore permissions so cleanup can work
                readonly_dir.chmod(0o755)
    
    def test_setup_logging_relative_path(self):
        """Test logging setup with relative path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory and use relative path
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                with patch.dict(os.environ, {
                    "OPENAI_STRUCTURED_LOG_LEVEL": "INFO",
                    "OPENAI_STRUCTURED_LOG_PATH": "logs"
                }):
                    logger = setup_logging()
                    
                    assert logger.disabled is False
                    assert len(logger.handlers) > 0
            finally:
                os.chdir(original_cwd)


class TestAPILogging:
    """Test API logging functionality."""
    
    def test_setup_api_logging_with_path(self):
        """Test API logging setup with valid path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            api_logger = setup_api_logging(temp_dir)
            
            assert api_logger.disabled is False
            assert len(api_logger.handlers) > 0
            
            # Check that API log file exists
            api_log_file = Path(temp_dir) / "api.log"
            # File might not exist yet, but handler should be configured
            assert any(isinstance(h, logging.FileHandler) for h in api_logger.handlers)
    
    def test_setup_api_logging_without_path(self):
        """Test API logging setup without path (disabled)."""
        api_logger = setup_api_logging(None)
        assert api_logger.disabled is True
    
    def test_log_api_request(self):
        """Test API request logging."""
        headers = {"Authorization": "Bearer secret-key", "Content-Type": "application/json"}
        data = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Test message"}],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "test", "schema": {"type": "object"}}
            }
        }
        
        with patch('openai_structured_mcp.utils.logging.get_api_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            request_id = log_api_request("POST", "https://api.openai.com/v1/chat/completions", headers, data)
            
            # Verify request ID format
            assert request_id.startswith("req_")
            
            # Verify logger was called
            mock_logger.debug.assert_called_once()
            call_args = mock_logger.debug.call_args[0][0]
            
            # Verify sensitive data is redacted
            assert "[REDACTED]" in call_args
            assert "secret-key" not in call_args
            assert "[CONTENT_REDACTED_FOR_PRIVACY]" in call_args
            assert "[SCHEMA_REDACTED_FOR_SIZE]" in call_args
    
    def test_log_api_response(self):
        """Test API response logging."""
        response_data = {
            "choices": [{
                "message": {"content": "Test response content"},
                "finish_reason": "stop"
            }],
            "usage": {"total_tokens": 50}
        }
        
        with patch('openai_structured_mcp.utils.logging.get_api_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            log_api_response("req_123", 200, response_data, 150.5)
            
            # Verify logger was called
            mock_logger.debug.assert_called_once()
            call_args = mock_logger.debug.call_args[0][0]
            
            # Verify response data is properly handled
            assert "req_123" in call_args
            assert "200" in call_args
            assert "150.5" in call_args
            assert "[CONTENT_REDACTED_FOR_SIZE]" in call_args
    
    def test_log_api_response_with_error(self):
        """Test API response logging with error."""
        with patch('openai_structured_mcp.utils.logging.get_api_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            log_api_response("req_456", 401, {}, 50.0, "Authentication failed")
            
            mock_logger.debug.assert_called_once()
            call_args = mock_logger.debug.call_args[0][0]
            
            assert "req_456" in call_args
            assert "401" in call_args
            assert "Authentication failed" in call_args
            assert '"success": false' in call_args


class TestLoggerGetters:
    """Test logger getter functions."""
    
    def test_get_logger_default(self):
        """Test getting default logger."""
        logger = get_logger()
        assert logger.name == "openai_structured_mcp"
    
    def test_get_logger_custom_name(self):
        """Test getting logger with custom name."""
        logger = get_logger("custom_name")
        assert logger.name == "custom_name"
    
    def test_get_api_logger(self):
        """Test getting API logger."""
        logger = get_api_logger()
        assert logger.name == "openai_structured_api"


class TestDebugDecorator:
    """Test debug decorator functionality."""
    
    @pytest.mark.asyncio
    async def test_debug_decorator_async_success(self):
        """Test debug decorator with successful async function."""
        @debug_decorator
        async def test_async_function(arg1, arg2=None):
            return f"result_{arg1}_{arg2}"
        
        with patch('openai_structured_mcp.utils.logging.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            result = await test_async_function("test", arg2="value")
            
            assert result == "result_test_value"
            
            # Verify debug calls were made
            assert mock_logger.debug.call_count >= 2  # ENTER and EXIT calls
            
            # Check for ENTER and EXIT messages
            debug_calls = [call[0][0] for call in mock_logger.debug.call_args_list]
            enter_calls = [call for call in debug_calls if "ENTER" in call]
            exit_calls = [call for call in debug_calls if "EXIT" in call and "SUCCESS" in call]
            
            assert len(enter_calls) >= 1
            assert len(exit_calls) >= 1
    
    @pytest.mark.asyncio
    async def test_debug_decorator_async_exception(self):
        """Test debug decorator with async function that raises exception."""
        @debug_decorator
        async def test_async_function_with_error():
            raise ValueError("Test error")
        
        with patch('openai_structured_mcp.utils.logging.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            with pytest.raises(ValueError, match="Test error"):
                await test_async_function_with_error()
            
            # Verify debug calls were made
            assert mock_logger.debug.call_count >= 2
            
            # Check for ENTER and ERROR EXIT messages
            debug_calls = [call[0][0] for call in mock_logger.debug.call_args_list]
            enter_calls = [call for call in debug_calls if "ENTER" in call]
            error_calls = [call for call in debug_calls if "EXIT" in call and "ERROR" in call]
            
            assert len(enter_calls) >= 1
            assert len(error_calls) >= 1
    
    def test_debug_decorator_sync_success(self):
        """Test debug decorator with successful sync function."""
        @debug_decorator
        def test_sync_function(value):
            return value * 2
        
        with patch('openai_structured_mcp.utils.logging.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            result = test_sync_function(5)
            
            assert result == 10
            
            # Verify debug calls were made
            assert mock_logger.debug.call_count >= 2
            
            # Check for SUCCESS message
            debug_calls = [call[0][0] for call in mock_logger.debug.call_args_list]
            success_calls = [call for call in debug_calls if "SUCCESS" in call]
            assert len(success_calls) >= 1
    
    def test_debug_decorator_sync_exception(self):
        """Test debug decorator with sync function that raises exception."""
        @debug_decorator
        def test_sync_function_with_error():
            raise RuntimeError("Sync error")
        
        with patch('openai_structured_mcp.utils.logging.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            with pytest.raises(RuntimeError, match="Sync error"):
                test_sync_function_with_error()
            
            # Verify debug calls were made
            assert mock_logger.debug.call_count >= 2
            
            # Check for ERROR message
            debug_calls = [call[0][0] for call in mock_logger.debug.call_args_list]
            error_calls = [call for call in debug_calls if "ERROR" in call]
            assert len(error_calls) >= 1


class TestEnvironmentIntegration:
    """Test logging integration with environment variables."""
    
    def test_all_log_levels(self):
        """Test that all valid log levels work."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            for level in valid_levels:
                with patch.dict(os.environ, {
                    "OPENAI_STRUCTURED_LOG_LEVEL": level,
                    "OPENAI_STRUCTURED_LOG_PATH": temp_dir
                }):
                    logger = setup_logging()
                    assert logger.disabled is False
                    assert logger.level == getattr(logging, level)
    
    def test_case_insensitive_log_levels(self):
        """Test that log levels are case insensitive."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {
                "OPENAI_STRUCTURED_LOG_LEVEL": "info",  # lowercase
                "OPENAI_STRUCTURED_LOG_PATH": temp_dir
            }):
                logger = setup_logging()
                assert logger.disabled is False
                assert logger.level == logging.INFO
    
    def test_logging_disabled_states(self):
        """Test various ways logging can be disabled."""
        disabled_values = ["none", "NONE", "None", "", None]
        
        for value in disabled_values:
            env_dict = {"OPENAI_STRUCTURED_LOG_LEVEL": value} if value is not None else {}
            with patch.dict(os.environ, env_dict, clear=True):
                logger = setup_logging()
                assert logger.disabled is True