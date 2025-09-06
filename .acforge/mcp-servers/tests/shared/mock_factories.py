"""Mock factories for MCP server testing."""

import json
import time
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, MagicMock


class PerplexityMockFactory:
    """Factory for creating Perplexity API mocks."""
    
    @staticmethod
    def create_successful_response(content: str = "Test response", 
                                 related_questions: Optional[List[str]] = None,
                                 citations: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a successful Perplexity API response."""
        response = {
            "choices": [{"message": {"content": content}}],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": len(content.split()),
                "total_tokens": 10 + len(content.split())
            }
        }
        
        if related_questions:
            response["related_questions"] = related_questions
        
        if citations:
            response["citations"] = citations
        
        return response
    
    @staticmethod
    def create_error_response(error_message: str = "API Error", error_type: str = "generic") -> Dict[str, Any]:
        """Create an error response from Perplexity API."""
        return {
            "error": error_message,
            "error_type": error_type
        }
    
    @staticmethod
    def create_client_mock(responses: Optional[List[Dict[str, Any]]] = None) -> AsyncMock:
        """Create a mock Perplexity client with configurable responses."""
        mock_client = AsyncMock()
        mock_client.AVAILABLE_MODELS = ["sonar", "sonar-pro", "sonar-reasoning", "sonar-deep-research"]
        
        # Default response
        default_response = PerplexityMockFactory.create_successful_response()
        
        if responses:
            mock_client.query.side_effect = responses
            mock_client.research_topic.side_effect = responses
        else:
            mock_client.query.return_value = default_response
            mock_client.research_topic.return_value = default_response
        
        mock_client.health_check.return_value = True
        return mock_client


class OpenAIMockFactory:
    """Factory for creating OpenAI structured API mocks."""
    
    @staticmethod
    def create_successful_structured_response(data: Optional[Dict[str, Any]] = None,
                                            schema_name: str = "data_extraction",
                                            processing_time_ms: float = 150.0) -> Dict[str, Any]:
        """Create a successful structured response."""
        if data is None:
            data = {
                "entities": ["Test", "Entity"],
                "key_facts": ["This is a test fact"],
                "summary": "Test summary",
                "confidence_score": 0.85
            }
        
        return {
            "success": True,
            "data": data,
            "metadata": {
                "schema_name": schema_name,
                "model": "gpt-4o-mini",
                "temperature": 0.0
            },
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "processing_time_ms": processing_time_ms
        }
    
    @staticmethod
    def create_error_response(error_message: str = "API Error", 
                            error_type: str = "generic") -> Dict[str, Any]:
        """Create an error response from OpenAI API."""
        return {
            "error": error_message,
            "error_type": error_type
        }
    
    @staticmethod
    def create_client_mock(responses: Optional[List[Dict[str, Any]]] = None) -> AsyncMock:
        """Create a mock OpenAI structured client."""
        mock_client = AsyncMock()
        mock_client.get_available_schemas.return_value = {
            "data_extraction": "Extract structured data from unstructured text",
            "code_analysis": "Analyze code structure, complexity, and quality",
            "configuration_task": "Create structured configuration tasks",
            "sentiment_analysis": "Analyze sentiment with emotional breakdown"
        }
        
        # Default response
        default_response = OpenAIMockFactory.create_successful_structured_response()
        
        if responses:
            mock_client.structured_completion.side_effect = responses
            mock_client.extract_data.side_effect = responses
            mock_client.analyze_code.side_effect = responses
            mock_client.create_configuration_task.side_effect = responses
            mock_client.analyze_sentiment.side_effect = responses
        else:
            mock_client.structured_completion.return_value = default_response
            mock_client.extract_data.return_value = default_response
            mock_client.analyze_code.return_value = default_response
            mock_client.create_configuration_task.return_value = default_response
            mock_client.analyze_sentiment.return_value = default_response
        
        mock_client.health_check.return_value = True
        return mock_client


class GenericMockFactory:
    """Factory for creating generic test utilities."""
    
    @staticmethod
    def create_sample_data() -> Dict[str, Any]:
        """Create sample data for testing."""
        return {
            "unstructured_text": (
                "OpenAI's GPT-4 model offers enhanced structured output capabilities, "
                "allowing developers to get reliable JSON Schema-validated responses. "
                "This breakthrough in AI technology ensures more accurate and consistent "
                "data extraction for enterprise applications."
            ),
            "sample_code": '''
def calculate_fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

result = calculate_fibonacci(10)
print(f"Fibonacci(10) = {result}")
''',
            "sentiment_text": (
                "This was an excellent service! I highly recommend it to anyone "
                "looking for a great experience. The team was professional and "
                "the results exceeded my expectations."
            ),
            "configuration_description": (
                "Setup continuous integration and deployment pipeline using GitHub Actions, "
                "Docker containers, and automated testing with deployment to staging and production environments."
            )
        }
    
    @staticmethod
    def create_performance_test_data(size: str = "medium") -> Dict[str, Any]:
        """Create test data of various sizes for performance testing."""
        sizes = {
            "small": {"text_length": 100, "array_size": 10},
            "medium": {"text_length": 1000, "array_size": 100},
            "large": {"text_length": 10000, "array_size": 1000}
        }
        
        config = sizes.get(size, sizes["medium"])
        
        return {
            "text": "Sample text. " * (config["text_length"] // 13),  # Approximate length
            "array": [f"item_{i}" for i in range(config["array_size"])],
            "nested_data": {
                "level1": {
                    "level2": {
                        "data": [f"nested_item_{i}" for i in range(config["array_size"] // 10)]
                    }
                }
            }
        }
    
    @staticmethod
    def create_concurrent_test_data(num_requests: int = 10) -> List[Dict[str, Any]]:
        """Create test data for concurrent request testing."""
        return [
            {
                "id": i,
                "query": f"Test query {i}",
                "expected_response": f"Test response {i}"
            }
            for i in range(num_requests)
        ]


class ErrorScenarioFactory:
    """Factory for creating various error scenarios for testing."""
    
    @staticmethod
    def create_network_errors() -> List[Exception]:
        """Create various network error scenarios."""
        return [
            ConnectionError("Connection refused"),
            TimeoutError("Request timeout"),
            OSError("Network is unreachable"),
            Exception("SSL handshake failed")
        ]
    
    @staticmethod
    def create_api_errors() -> List[Dict[str, Any]]:
        """Create various API error responses."""
        return [
            {"error": "Invalid API key", "error_type": "authentication"},
            {"error": "Rate limit exceeded", "error_type": "rate_limit"},
            {"error": "Quota exceeded", "error_type": "quota_exceeded"},
            {"error": "Model not available", "error_type": "model_error"},
            {"error": "Invalid request format", "error_type": "validation_error"}
        ]
    
    @staticmethod
    def create_malformed_responses() -> List[str]:
        """Create malformed response scenarios for testing."""
        return [
            "{invalid json",  # Invalid JSON
            "null",  # Null response
            "",  # Empty response
            "{'single_quotes': True}",  # Invalid JSON with single quotes
            json.dumps({"incomplete": True})[:10]  # Truncated JSON
        ]
    
    @staticmethod
    def create_edge_case_inputs() -> List[Dict[str, Any]]:
        """Create edge case inputs for robust testing."""
        return [
            {"description": "empty_string", "input": ""},
            {"description": "very_long_string", "input": "A" * 10000},
            {"description": "unicode_characters", "input": "测试 🔥 émojis ñ"},
            {"description": "special_characters", "input": "!@#$%^&*(){}[]|\\:';\"<>,.?/~`"},
            {"description": "html_content", "input": "<script>alert('test')</script>"},
            {"description": "json_content", "input": '{"nested": {"json": "content"}}'}
        ]
