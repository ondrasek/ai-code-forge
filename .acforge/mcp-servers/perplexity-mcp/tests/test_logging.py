"""Tests for logging utilities."""

import pytest
import logging
import tempfile
import os
from unittest.mock import patch

from perplexity_mcp.utils.logging import setup_logging, get_logger


class TestLoggingUtils:
    """Test cases for logging utilities."""
    
    def test_setup_logging_default(self):
        """Test setup_logging with default parameters."""
        logger = setup_logging()
        
        assert logger.name == "perplexity_mcp"
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1  # Console handler only
        assert isinstance(logger.handlers[0], logging.StreamHandler)
    
    def test_setup_logging_custom_level(self):
        """Test setup_logging with custom log level."""
        logger = setup_logging(log_level="DEBUG")
        
        assert logger.level == logging.DEBUG
    
    def test_setup_logging_invalid_level(self):
        """Test setup_logging with invalid log level falls back to INFO."""
        logger = setup_logging(log_level="INVALID")
        
        # Should fall back to INFO level
        assert logger.level == logging.INFO
    
    def test_setup_logging_with_file(self):
        """Test setup_logging with file handler."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            log_file = tmp_file.name
        
        try:
            logger = setup_logging(log_file=log_file)
            
            assert len(logger.handlers) == 2  # Console + file handlers
            assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)
            assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
            
            # Test that we can write to the log file
            logger.info("Test message")
            
            with open(log_file, 'r') as f:
                content = f.read()
                assert "Test message" in content
                
        finally:
            # Clean up
            if os.path.exists(log_file):
                os.unlink(log_file)
    
    def test_setup_logging_file_creation_error(self):
        """Test setup_logging with invalid file path."""
        # Use an invalid path that should fail
        invalid_path = "/invalid/path/that/does/not/exist/log.txt"
        
        # Should not raise exception, but should warn
        logger = setup_logging(log_file=invalid_path)
        
        # Should still have console handler
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)
    
    def test_setup_logging_custom_logger_name(self):
        """Test setup_logging with custom logger name."""
        logger = setup_logging(logger_name="custom_logger")
        
        assert logger.name == "custom_logger"
    
    def test_setup_logging_clears_existing_handlers(self):
        """Test that setup_logging clears existing handlers."""
        # Create logger with a handler
        logger_name = "test_clear_handlers"
        logger = logging.getLogger(logger_name)
        logger.addHandler(logging.StreamHandler())
        
        assert len(logger.handlers) == 1
        
        # Setup logging should clear existing handlers
        logger = setup_logging(logger_name=logger_name)
        
        assert len(logger.handlers) == 1  # Only the new console handler
    
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
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp_file:
            log_file = tmp_file.name
        
        try:
            logger = setup_logging(log_file=log_file, log_level="DEBUG")
            logger.info("Test message with formatting")
            
            with open(log_file, 'r') as f:
                content = f.read()
                
                # Check that the format includes timestamp, logger name, level, and message
                assert "perplexity_mcp" in content
                assert "INFO" in content
                assert "Test message with formatting" in content
                # Check timestamp format (YYYY-MM-DD HH:MM:SS)
                import re
                timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
                assert re.search(timestamp_pattern, content)
                
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)
    
    def test_file_handler_directory_creation(self):
        """Test that log file directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_file = os.path.join(tmp_dir, "subdir", "test.log")
            
            # Directory doesn't exist yet
            assert not os.path.exists(os.path.dirname(log_file))
            
            logger = setup_logging(log_file=log_file)
            logger.info("Test message")
            
            # Directory should be created
            assert os.path.exists(os.path.dirname(log_file))
            assert os.path.exists(log_file)
    
    @patch.dict(os.environ, {"PERPLEXITY_LOG_LEVEL": "DEBUG", "PERPLEXITY_LOG_FILE": "/tmp/test.log"})
    def test_environment_variable_integration(self):
        """Test integration with environment variables."""
        # This would typically be tested in the server module, but we can verify
        # the logging utils work with environment-provided values
        log_level = os.getenv("PERPLEXITY_LOG_LEVEL", "INFO")
        log_file = os.getenv("PERPLEXITY_LOG_FILE")
        
        logger = setup_logging(log_level=log_level, log_file=log_file)
        
        assert logger.level == logging.DEBUG