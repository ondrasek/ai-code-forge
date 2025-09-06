"""Tests for OpenAI client implementation."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import json
import os

from openai_structured_mcp.client import OpenAIStructuredClient


class TestOpenAIStructuredClient:
    """Test OpenAI structured client functionality."""
    
    def test_client_initialization_with_api_key(self):
        """Test client initialization with provided API key."""
        with patch.dict(os.environ, {}, clear=True):  # Clear environment
            client = OpenAIStructuredClient(api_key="test-key")
            assert client.api_key == "test-key"
            assert client.default_model == "gpt-5"  # Default value
    
    def test_client_initialization_from_env(self):
        """Test client initialization from environment variable."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"}):
            client = OpenAIStructuredClient()
            assert client.api_key == "env-key"
    
    def test_client_initialization_no_api_key(self):
        """Test client initialization without API key raises error."""
        with patch.dict(os.environ, {}, clear=True):  # Clear environment
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                OpenAIStructuredClient()
    
    def test_client_configuration_from_env(self):
        """Test client configuration from environment variables."""
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-key",
            "OPENAI_DEFAULT_MODEL": "gpt-4o",
            "OPENAI_DEFAULT_TEMPERATURE": "0.3",
            "OPENAI_DEFAULT_MAX_TOKENS": "2000"
        }):
            client = OpenAIStructuredClient()
            assert client.default_model == "gpt-4o"
            assert client.default_temperature == 0.3
            assert client.default_max_tokens == 2000
    
    @pytest.mark.asyncio
    async def test_structured_completion_success(self, mock_openai_response):
        """Test successful structured completion."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIStructuredClient()
            
            # Mock the OpenAI client
            mock_completion = MagicMock()
            mock_completion.model_dump.return_value = mock_openai_response
            
            with patch.object(client.client.chat.completions, 'create', return_value=mock_completion):
                result = await client.structured_completion(
                    prompt="Extract data from this text",
                    schema_name="data_extraction"
                )
                
                assert result["success"] is True
                assert "data" in result
                assert "metadata" in result
                assert "timestamp" in result
                assert "processing_time_ms" in result
                assert result["data"]["entities"] == ["OpenAI", "Python", "JSON Schema"]
    
    @pytest.mark.asyncio
    async def test_structured_completion_invalid_schema(self):
        """Test structured completion with invalid schema name."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIStructuredClient()
            
            result = await client.structured_completion(
                prompt="Test prompt",
                schema_name="invalid_schema"
            )
            
            assert "error" in result
            assert result["error_type"] == "invalid_schema"
            assert "available_schemas" in result
    
    @pytest.mark.asyncio
    async def test_structured_completion_api_error(self):
        """Test structured completion with API error."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIStructuredClient()
            
            # Mock API error
            api_error = Exception("API Error")
            api_error.response = MagicMock()
            api_error.response.status_code = 401
            api_error.response.text = "Unauthorized"
            
            with patch.object(client.client.chat.completions, 'create', side_effect=api_error):
                result = await client.structured_completion(
                    prompt="Test prompt",
                    schema_name="data_extraction"
                )
                
                assert "error" in result
                assert result["error_type"] == "authentication"
    
    @pytest.mark.asyncio
    async def test_structured_completion_validation_error(self, mock_openai_client):
        """Test structured completion with validation error."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIStructuredClient()
            
            # Mock response with invalid data
            invalid_response = {
                "choices": [{
                    "message": {
                        "content": json.dumps({
                            "entities": ["Test"],
                            "key_facts": [],  # Invalid: min_length=1
                            "summary": "Short",  # Invalid: min_length=10
                            "confidence_score": 1.5  # Invalid: max=1.0
                        })
                    },
                    "finish_reason": "stop"
                }],
                "usage": {"total_tokens": 50}
            }
            
            mock_completion = MagicMock()
            mock_completion.model_dump.return_value = invalid_response
            
            with patch.object(client.client.chat.completions, 'create', return_value=mock_completion):
                result = await client.structured_completion(
                    prompt="Test prompt",
                    schema_name="data_extraction",
                    validate_response=True
                )
                
                assert "error" in result
                assert result["error_type"] == "validation_error"
                assert "validation_errors" in result
                assert "raw_response" in result
    
    @pytest.mark.asyncio
    async def test_extract_data_success(self, mock_openai_response):
        """Test successful data extraction."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIStructuredClient()
            
            mock_completion = MagicMock()
            mock_completion.model_dump.return_value = mock_openai_response
            
            with patch.object(client.client.chat.completions, 'create', return_value=mock_completion):
                result = await client.extract_data(
                    text="OpenAI provides API access for Python developers.",
                    custom_instructions="Focus on technology mentions."
                )
                
                assert result["success"] is True
                assert "data" in result
                assert result["data"]["entities"] == ["OpenAI", "Python", "JSON Schema"]
    
    @pytest.mark.asyncio
    async def test_analyze_code_success(self, mock_code_analysis_response):
        """Test successful code analysis."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIStructuredClient()
            
            mock_completion = MagicMock()
            mock_completion.model_dump.return_value = mock_code_analysis_response
            
            with patch.object(client.client.chat.completions, 'create', return_value=mock_completion):
                result = await client.analyze_code(
                    code="def hello(): print('hello')",
                    language_hint="python"
                )
                
                assert result["success"] is True
                assert "data" in result
                assert result["data"]["language"] == "python"
                assert result["data"]["complexity_score"] == 3
    
    @pytest.mark.asyncio
    async def test_create_configuration_task_success(self, mock_configuration_task_response):
        """Test successful configuration task creation."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIStructuredClient()
            
            mock_completion = MagicMock()
            mock_completion.model_dump.return_value = mock_configuration_task_response
            
            with patch.object(client.client.chat.completions, 'create', return_value=mock_completion):
                result = await client.create_configuration_task(
                    description="Setup Docker development environment"
                )
                
                assert result["success"] is True
                assert "data" in result
                assert result["data"]["task_name"] == "Setup Docker Development Environment"
                assert result["data"]["priority"] == "high"
                assert len(result["data"]["steps"]) == 4
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment_success(self, mock_sentiment_analysis_response):
        """Test successful sentiment analysis."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIStructuredClient()
            
            mock_completion = MagicMock()
            mock_completion.model_dump.return_value = mock_sentiment_analysis_response
            
            with patch.object(client.client.chat.completions, 'create', return_value=mock_completion):
                result = await client.analyze_sentiment(
                    text="This was a great experience! Highly recommend."
                )
                
                assert result["success"] is True
                assert "data" in result
                assert result["data"]["overall_sentiment"] == "positive"
                assert result["data"]["confidence"] == 0.87
    
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIStructuredClient()
            
            # Mock successful health check response
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "healthy"
            
            with patch.object(client.client.chat.completions, 'create', return_value=mock_response):
                result = await client.health_check()
                
                assert result is True
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test health check failure."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIStructuredClient()
            
            # Mock API error
            with patch.object(client.client.chat.completions, 'create', side_effect=Exception("API Error")):
                result = await client.health_check()
                
                assert result is False
    
    def test_get_available_schemas(self):
        """Test getting available schemas information."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIStructuredClient()
            
            schemas = client.get_available_schemas()
            
            assert isinstance(schemas, dict)
            assert "data_extraction" in schemas
            assert "code_analysis" in schemas
            assert "configuration_task" in schemas
            assert "sentiment_analysis" in schemas
            
            # Check descriptions are meaningful
            for schema_name, description in schemas.items():
                assert isinstance(description, str)
                assert len(description) > 10  # Meaningful description
    
    @pytest.mark.asyncio
    async def test_model_validation_and_fallback(self, mock_openai_response):
        """Test that invalid model names fall back to default."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIStructuredClient()
            
            mock_completion = MagicMock()
            mock_completion.model_dump.return_value = mock_openai_response
            
            with patch.object(client.client.chat.completions, 'create', return_value=mock_completion) as mock_create:
                await client.structured_completion(
                    prompt="Test",
                    schema_name="data_extraction",
                    model="invalid-model"
                )
                
                # Should call with default model, not invalid model
                call_args = mock_create.call_args[1]
                assert call_args["model"] == client.default_model
    
    @pytest.mark.asyncio
    async def test_json_parse_error_handling(self):
        """Test handling of invalid JSON responses."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIStructuredClient()
            
            # Mock response with invalid JSON
            invalid_json_response = {
                "choices": [{
                    "message": {
                        "content": "invalid json content"
                    },
                    "finish_reason": "stop"
                }],
                "usage": {"total_tokens": 50}
            }
            
            mock_completion = MagicMock()
            mock_completion.model_dump.return_value = invalid_json_response
            
            with patch.object(client.client.chat.completions, 'create', return_value=mock_completion):
                result = await client.structured_completion(
                    prompt="Test",
                    schema_name="data_extraction"
                )
                
                assert "error" in result
                assert result["error_type"] == "json_parse_error"
                assert "raw_content" in result
    
    @pytest.mark.asyncio
    async def test_empty_response_handling(self):
        """Test handling of empty API responses."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIStructuredClient()
            
            # Mock empty response
            empty_response = {
                "choices": [{
                    "message": {"content": None},
                    "finish_reason": "stop"
                }]
            }
            
            mock_completion = MagicMock()
            mock_completion.model_dump.return_value = empty_response
            
            with patch.object(client.client.chat.completions, 'create', return_value=mock_completion):
                result = await client.structured_completion(
                    prompt="Test",
                    schema_name="data_extraction"
                )
                
                assert "error" in result
                assert result["error_type"] == "empty_response"
    
    @pytest.mark.asyncio
    async def test_no_choices_response_handling(self):
        """Test handling of responses with no choices."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIStructuredClient()
            
            # Mock response with no choices
            no_choices_response = {
                "choices": [],
                "usage": {"total_tokens": 0}
            }
            
            mock_completion = MagicMock()
            mock_completion.model_dump.return_value = no_choices_response
            
            with patch.object(client.client.chat.completions, 'create', return_value=mock_completion):
                result = await client.structured_completion(
                    prompt="Test",
                    schema_name="data_extraction"
                )
                
                assert "error" in result
                assert result["error_type"] == "no_choices"
    
    @pytest.mark.asyncio
    async def test_dynamic_model_fetching(self, mock_openai_models_response):
        """Test dynamic model fetching from OpenAI API."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIStructuredClient()
            
            # Create an async mock that returns the models response
            async def mock_list():
                return mock_openai_models_response
            
            # Mock the models.list() call
            with patch.object(client.client.models, 'list', side_effect=mock_list):
                models = await client.get_available_models()
                
                expected_models = ["gpt-5", "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
                assert models == expected_models
                
    @pytest.mark.asyncio
    async def test_model_fetching_with_api_failure(self):
        """Test model fetching fallback when API fails."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIStructuredClient()
            
            # Mock API failure
            with patch.object(client.client.models, 'list', side_effect=Exception("API Error")):
                models = await client.get_available_models()
                
                expected_fallback = ["gpt-5", "gpt-4o", "gpt-4o-mini"]
                assert models == expected_fallback