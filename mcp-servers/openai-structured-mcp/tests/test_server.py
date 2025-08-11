"""Tests for FastMCP server implementation."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import os
import json

# Import server components
with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
    from openai_structured_mcp import server


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI structured client for testing."""
    mock_client = AsyncMock()
    mock_client.get_available_schemas.return_value = {
        "data_extraction": "Extract structured data from unstructured text",
        "code_analysis": "Analyze code structure, complexity, and quality",
        "configuration_task": "Create structured configuration tasks",
        "sentiment_analysis": "Analyze sentiment with emotional breakdown"
    }
    return mock_client


class TestMCPTools:
    """Test cases for MCP server tools."""
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    async def test_extract_data_success(self, mock_openai_client, sample_unstructured_text):
        """Test successful data extraction."""
        # Mock successful extraction response
        mock_response = {
            "success": True,
            "data": {
                "entities": ["OpenAI", "GPT-4", "JSON Schema"],
                "key_facts": ["GPT-4 has improved structured output", "JSON Schema ensures accuracy"],
                "summary": "OpenAI's GPT-4 offers enhanced structured output capabilities for developers.",
                "confidence_score": 0.92
            },
            "metadata": {"schema_name": "data_extraction"},
            "timestamp": "2024-01-01T12:00:00",
            "processing_time_ms": 150.0
        }
        mock_openai_client.extract_data.return_value = mock_response
        
        with patch.object(server, 'openai_client', mock_openai_client):
            result = await server.extract_data(
                text=sample_unstructured_text,
                custom_instructions="Focus on AI technology"
            )
        
        # Verify the result is valid JSON
        parsed_result = json.loads(result)
        assert parsed_result["success"] is True
        assert "data" in parsed_result
        assert len(parsed_result["data"]["entities"]) == 3
        assert parsed_result["data"]["confidence_score"] == 0.92
        
        # Verify client was called correctly
        mock_openai_client.extract_data.assert_called_once_with(
            text=sample_unstructured_text,
            custom_instructions="Focus on AI technology"
        )
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    async def test_extract_data_error(self, mock_openai_client):
        """Test data extraction with error."""
        mock_response = {"error": "Invalid API key", "error_type": "authentication"}
        mock_openai_client.extract_data.return_value = mock_response
        
        with patch.object(server, 'openai_client', mock_openai_client):
            result = await server.extract_data(text="Test text")
        
        assert "Error extracting data: Invalid API key" in result
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    async def test_analyze_code_success(self, mock_openai_client, sample_code):
        """Test successful code analysis."""
        mock_response = {
            "success": True,
            "data": {
                "language": "python",
                "complexity_score": 4,
                "issues": ["Missing docstrings", "No type hints"],
                "strengths": ["Clear variable names", "Good error handling"],
                "recommendations": ["Add comprehensive docstrings", "Include type annotations"],
                "functions_count": 2,
                "lines_of_code": 15
            },
            "metadata": {"schema_name": "code_analysis"},
            "timestamp": "2024-01-01T12:00:00",
            "processing_time_ms": 200.0
        }
        mock_openai_client.analyze_code.return_value = mock_response
        
        with patch.object(server, 'openai_client', mock_openai_client):
            result = await server.analyze_code(
                code=sample_code,
                language_hint="python"
            )
        
        parsed_result = json.loads(result)
        assert parsed_result["success"] is True
        assert parsed_result["data"]["language"] == "python"
        assert parsed_result["data"]["complexity_score"] == 4
        assert len(parsed_result["data"]["issues"]) == 2
        assert len(parsed_result["data"]["strengths"]) == 2
        
        mock_openai_client.analyze_code.assert_called_once_with(
            code=sample_code,
            language_hint="python"
        )
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    async def test_create_configuration_task_success(self, mock_openai_client):
        """Test successful configuration task creation."""
        mock_response = {
            "success": True,
            "data": {
                "task_name": "Setup CI/CD Pipeline",
                "priority": "high",
                "steps": [
                    "Create GitHub Actions workflow",
                    "Configure build stages",
                    "Setup deployment targets",
                    "Test pipeline execution"
                ],
                "prerequisites": ["GitHub repository access", "Docker knowledge"],
                "estimated_duration": "4 hours",
                "validation_criteria": [
                    "Pipeline runs without errors",
                    "Automated tests pass",
                    "Deployment succeeds"
                ]
            },
            "metadata": {"schema_name": "configuration_task"},
            "timestamp": "2024-01-01T12:00:00",
            "processing_time_ms": 180.0
        }
        mock_openai_client.create_configuration_task.return_value = mock_response
        
        with patch.object(server, 'openai_client', mock_openai_client):
            result = await server.create_configuration_task(
                description="Setup continuous integration and deployment pipeline"
            )
        
        parsed_result = json.loads(result)
        assert parsed_result["success"] is True
        assert parsed_result["data"]["task_name"] == "Setup CI/CD Pipeline"
        assert parsed_result["data"]["priority"] == "high"
        assert len(parsed_result["data"]["steps"]) == 4
        assert len(parsed_result["data"]["validation_criteria"]) == 3
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    async def test_analyze_sentiment_success(self, mock_openai_client):
        """Test successful sentiment analysis."""
        mock_response = {
            "success": True,
            "data": {
                "overall_sentiment": "positive",
                "confidence": 0.89,
                "key_phrases": ["excellent service", "highly recommend", "great experience"],
                "emotions": {
                    "joy": 0.8,
                    "satisfaction": 0.9,
                    "enthusiasm": 0.7
                },
                "reasoning": "The text contains multiple positive indicators and enthusiastic language suggesting strong positive sentiment."
            },
            "metadata": {"schema_name": "sentiment_analysis"},
            "timestamp": "2024-01-01T12:00:00",
            "processing_time_ms": 120.0
        }
        mock_openai_client.analyze_sentiment.return_value = mock_response
        
        with patch.object(server, 'openai_client', mock_openai_client):
            result = await server.analyze_sentiment(
                text="This was an excellent service! I highly recommend it to anyone looking for a great experience."
            )
        
        parsed_result = json.loads(result)
        assert parsed_result["success"] is True
        assert parsed_result["data"]["overall_sentiment"] == "positive"
        assert parsed_result["data"]["confidence"] == 0.89
        assert len(parsed_result["data"]["key_phrases"]) == 3
        assert "joy" in parsed_result["data"]["emotions"]
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    async def test_custom_structured_query_success(self, mock_openai_client):
        """Test successful custom structured query."""
        mock_response = {
            "success": True,
            "data": {
                "entities": ["Custom", "Query", "Test"],
                "key_facts": ["Custom queries allow flexible schema usage"],
                "summary": "This demonstrates the custom structured query functionality.",
                "confidence_score": 0.85
            },
            "metadata": {
                "schema_name": "data_extraction",
                "model": "gpt-4o-mini",
                "temperature": 0.3
            },
            "timestamp": "2024-01-01T12:00:00",
            "processing_time_ms": 160.0
        }
        mock_openai_client.structured_completion.return_value = mock_response
        
        with patch.object(server, 'openai_client', mock_openai_client):
            result = await server.custom_structured_query(
                prompt="Extract information about custom queries",
                schema_name="data_extraction",
                system_message="Focus on technical concepts",
                model="gpt-4o-mini",
                temperature=0.3,
                max_tokens=500
            )
        
        parsed_result = json.loads(result)
        assert parsed_result["success"] is True
        assert "data" in parsed_result
        assert "metadata" in parsed_result
        
        mock_openai_client.structured_completion.assert_called_once_with(
            prompt="Extract information about custom queries",
            schema_name="data_extraction",
            system_message="Focus on technical concepts",
            model="gpt-4o-mini",
            temperature=0.3,
            max_tokens=500
        )
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    async def test_custom_structured_query_error(self, mock_openai_client):
        """Test custom structured query with error."""
        mock_response = {"error": "Invalid schema name", "error_type": "invalid_schema"}
        mock_openai_client.structured_completion.return_value = mock_response
        
        with patch.object(server, 'openai_client', mock_openai_client):
            result = await server.custom_structured_query(
                prompt="Test",
                schema_name="invalid_schema"
            )
        
        assert "Error in custom query: Invalid schema name" in result
    
    @pytest.mark.asyncio
    async def test_list_schemas(self, mock_openai_client):
        """Test list schemas functionality."""
        with patch.object(server, 'openai_client', mock_openai_client):
            result = await server.list_schemas()
        
        # Verify all expected schemas are listed
        assert "data_extraction" in result
        assert "code_analysis" in result
        assert "configuration_task" in result
        assert "sentiment_analysis" in result
        
        # Verify descriptions and usage tips are present
        assert "Extract structured data" in result
        assert "Analyze source code" in result
        assert "Usage Tips:" in result
        assert "custom_structured_query" in result
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    async def test_health_check_success(self, mock_openai_client):
        """Test successful health check."""
        # Mock successful basic health check
        mock_openai_client.health_check.return_value = True
        
        # Mock successful structured output test
        mock_structured_response = {
            "success": True,
            "data": {"test": "data"},
            "metadata": {"schema_name": "data_extraction"}
        }
        mock_openai_client.structured_completion.return_value = mock_structured_response
        
        with patch.object(server, 'openai_client', mock_openai_client):
            result = await server.health_check()
        
        assert "\u2705" in result  # Check mark emoji
        assert "accessible and structured outputs are working correctly" in result
        
        # Verify both health checks were called
        mock_openai_client.health_check.assert_called_once()
        mock_openai_client.structured_completion.assert_called_once()
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    async def test_health_check_basic_failure(self, mock_openai_client):
        """Test health check with basic API failure."""
        mock_openai_client.health_check.return_value = False
        
        with patch.object(server, 'openai_client', mock_openai_client):
            result = await server.health_check()
        
        assert "\u274c" in result  # X mark emoji
        assert "not responding correctly" in result
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    async def test_health_check_structured_failure(self, mock_openai_client):
        """Test health check with structured output failure."""
        mock_openai_client.health_check.return_value = True
        mock_openai_client.structured_completion.return_value = {"error": "Schema validation failed"}
        
        with patch.object(server, 'openai_client', mock_openai_client):
            result = await server.health_check()
        
        assert "\u274c" in result
        assert "structured output failed" in result
        assert "Schema validation failed" in result
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    async def test_health_check_exception(self, mock_openai_client):
        """Test health check with exception."""
        mock_openai_client.health_check.side_effect = Exception("Connection error")
        
        with patch.object(server, 'openai_client', mock_openai_client):
            result = await server.health_check()
        
        assert "\u274c" in result
        assert "Health check failed" in result
        assert "Connection error" in result
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    async def test_tool_exception_handling(self, mock_openai_client):
        """Test that tool exceptions are properly handled."""
        mock_openai_client.extract_data.side_effect = Exception("Unexpected error")
        
        with patch.object(server, 'openai_client', mock_openai_client):
            result = await server.extract_data(text="Test text")
        
        assert "Error during data extraction: Unexpected error" in result


class TestServerInitialization:
    """Test cases for server initialization."""
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_server_initialization_success(self):
        """Test successful server initialization."""
        # This test ensures the module can be imported without errors
        # when the API key is present
        assert server.mcp is not None
        assert hasattr(server, 'openai_client')
    
    def test_server_initialization_no_api_key(self):
        """Test server initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                # Re-import to trigger initialization error
                import importlib
                importlib.reload(server)
    
    @patch('openai_structured_mcp.server.FastMCP')
    def test_main_function(self, mock_fastmcp):
        """Test main function execution."""
        mock_mcp_instance = MagicMock()
        mock_fastmcp.return_value = mock_mcp_instance
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            server.main()
        
        mock_mcp_instance.run.assert_called_once()
    
    @patch('openai_structured_mcp.server.FastMCP')
    def test_main_function_keyboard_interrupt(self, mock_fastmcp):
        """Test main function with keyboard interrupt."""
        mock_mcp_instance = MagicMock()
        mock_mcp_instance.run.side_effect = KeyboardInterrupt()
        mock_fastmcp.return_value = mock_mcp_instance
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            # Should not raise exception
            server.main()
        
        mock_mcp_instance.run.assert_called_once()


class TestLoggingIntegration:
    """Test logging integration with environment variables."""
    
    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test-key",
        "OPENAI_STRUCTURED_LOG_LEVEL": "INFO"
    })
    def test_logging_configuration_info_level(self):
        """Test logging configuration with INFO level."""
        # Server should initialize without errors
        assert server.logger is not None
    
    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test-key", 
        "OPENAI_STRUCTURED_LOG_LEVEL": "NONE"
    })
    def test_logging_configuration_disabled(self):
        """Test logging configuration with disabled logging."""
        # Server should initialize without errors even with logging disabled
        assert server.logger is not None