"""Tests for logging utilities."""

import pytest
import logging
import tempfile
import os
from unittest.mock import patch
from pathlib import Path

from perplexity_mcp.utils.logging import setup_logging, get_logger, setup_api_logging


class TestLoggingUtils:
    """Test cases for logging utilities."""
    
    @patch.dict(os.environ, {"PERPLEXITY_LOG_LEVEL": "none"}, clear=True)
    def test_setup_logging_disabled(self):
        """Test setup_logging with logging disabled."""
        logger = setup_logging()
        
        assert logger.name == "perplexity_mcp"
        assert logger.disabled is True

    def test_setup_logging_custom_level(self):
        """Test setup_logging with custom log level."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch.dict(os.environ, {
                "PERPLEXITY_LOG_LEVEL": "DEBUG",
                "PERPLEXITY_LOG_PATH": tmp_dir
            }):
                logger = setup_logging()
                
                assert logger.level == logging.DEBUG
                assert len(logger.handlers) == 1
                assert isinstance(logger.handlers[0], logging.FileHandler)

    def test_setup_logging_invalid_level(self):
        """Test setup_logging with invalid log level raises ValueError."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch.dict(os.environ, {
                "PERPLEXITY_LOG_LEVEL": "INVALID",
                "PERPLEXITY_LOG_PATH": tmp_dir
            }):
                with pytest.raises(ValueError, match="Invalid PERPLEXITY_LOG_LEVEL"):
                    setup_logging()

    def test_setup_logging_with_file(self):
        """Test setup_logging with file handler."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_file = os.path.join(tmp_dir, "test.log")
            
            with patch.dict(os.environ, {
                "PERPLEXITY_LOG_LEVEL": "INFO",
                "PERPLEXITY_LOG_PATH": tmp_dir
            }):
                logger = setup_logging(log_file=log_file)
                
                assert len(logger.handlers) == 1  # File handler only (no console in MCP)
                assert isinstance(logger.handlers[0], logging.FileHandler)
                
                # Verify the handler points to our custom file
                handler = logger.handlers[0]
                assert handler.baseFilename == log_file

    def test_setup_logging_path_creation_error(self):
        """Test setup_logging with invalid log path."""
        # Use an invalid path that should fail
        invalid_path = "/invalid/path/that/does/not/exist"
        
        with patch.dict(os.environ, {
            "PERPLEXITY_LOG_LEVEL": "INFO",
            "PERPLEXITY_LOG_PATH": invalid_path
        }):
            with pytest.raises(OSError, match="Failed to create log directory"):
                setup_logging()

    def test_setup_logging_custom_logger_name(self):
        """Test setup_logging with custom logger name."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch.dict(os.environ, {
                "PERPLEXITY_LOG_LEVEL": "INFO",
                "PERPLEXITY_LOG_PATH": tmp_dir
            }):
                logger = setup_logging(logger_name="custom_logger")
                
                assert logger.name == "custom_logger"

    def test_setup_logging_clears_existing_handlers(self):
        """Test that setup_logging clears existing handlers."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create logger with a handler
            logger_name = "test_clear_handlers"
            logger = logging.getLogger(logger_name)
            logger.addHandler(logging.StreamHandler())
            
            assert len(logger.handlers) == 1
            
            # Setup logging should clear existing handlers
            with patch.dict(os.environ, {
                "PERPLEXITY_LOG_LEVEL": "INFO",
                "PERPLEXITY_LOG_PATH": tmp_dir
            }):
                logger = setup_logging(logger_name=logger_name)
                
                assert len(logger.handlers) == 1  # Only the new file handler

    def test_get_logger_default(self):
        """Test get_logger with default name."""
        logger = get_logger()
        
        assert logger.name == "perplexity_mcp"
        assert isinstance(logger, logging.Logger)

    def test_get_logger_custom_name(self):
        """Test get_logger with custom name."""
        logger = get_logger("custom_name")
        
        assert logger.name == "custom_name"

    def test_get_logger_returns_same_instance(self):
        """Test that get_logger returns the same instance for the same name."""
        logger1 = get_logger("same_name")
        logger2 = get_logger("same_name")
        
        assert logger1 is logger2

    def test_logging_formatter(self):
        """Test that the logging formatter works correctly."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch.dict(os.environ, {
                "PERPLEXITY_LOG_LEVEL": "DEBUG",
                "PERPLEXITY_LOG_PATH": tmp_dir
            }):
                logger = setup_logging()
                
                # Check that the formatter is properly configured
                handler = logger.handlers[0]
                formatter = handler.formatter
                
                # Check formatter format string contains expected elements
                format_string = formatter._fmt
                assert "%(asctime)s" in format_string
                assert "%(name)s" in format_string
                assert "%(levelname)s" in format_string
                assert "%(message)s" in format_string

    def test_file_handler_directory_creation(self):
        """Test that log file directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # The logging system creates timestamped directories automatically
            # so let's test that the logging directory structure is created
            with patch.dict(os.environ, {
                "PERPLEXITY_LOG_LEVEL": "INFO",
                "PERPLEXITY_LOG_PATH": tmp_dir
            }):
                logger = setup_logging()
                logger.info("Test message")
                
                # Flush the handler to ensure data is written
                for handler in logger.handlers:
                    handler.flush()
                
                # Check that some timestamped directory was created under tmp_dir
                subdirs = [d for d in os.listdir(tmp_dir) if d.startswith("perplexity_")]
                assert len(subdirs) >= 1, "Expected timestamped log directory to be created"

    def test_environment_variable_integration(self):
        """Test integration with environment variables."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch.dict(os.environ, {
                "PERPLEXITY_LOG_LEVEL": "DEBUG",
                "PERPLEXITY_LOG_PATH": tmp_dir
            }):
                logger = setup_logging()
                
                assert logger.level == logging.DEBUG
                assert len(logger.handlers) == 1
                assert isinstance(logger.handlers[0], logging.FileHandler)

    def test_setup_api_logging(self):
        """Test setup_api_logging function."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            api_logger = setup_api_logging(tmp_dir)
            
            assert api_logger.name == "perplexity_api"
            assert api_logger.level == logging.DEBUG
            assert len(api_logger.handlers) == 1
            assert isinstance(api_logger.handlers[0], logging.FileHandler)

    def test_setup_api_logging_disabled(self):
        """Test setup_api_logging with None path (disabled)."""
        api_logger = setup_api_logging(None)
        
        assert api_logger.name == "perplexity_api"
        assert api_logger.disabled is True

    def test_missing_log_path_raises_error(self):
        """Test that missing PERPLEXITY_LOG_PATH raises ValueError when logging enabled."""
        with patch.dict(os.environ, {"PERPLEXITY_LOG_LEVEL": "INFO"}, clear=True):
            with pytest.raises(ValueError, match="PERPLEXITY_LOG_PATH must be set"):
                setup_logging()