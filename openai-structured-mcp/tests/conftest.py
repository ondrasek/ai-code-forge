"""Pytest configuration and fixtures for OpenAI Structured MCP server tests."""

import pytest
import os
from unittest.mock import patch, AsyncMock, MagicMock
import asyncio
from datetime import datetime


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for all tests."""
    with patch.dict(os.environ, {
        "OPENAI_API_KEY": "sk-test-key-123",
        "OPENAI_STRUCTURED_LOG_LEVEL": "DEBUG",
        "OPENAI_DEFAULT_MODEL": "gpt-4o-mini",
        "OPENAI_DEFAULT_TEMPERATURE": "0.7",
        "OPENAI_DEFAULT_MAX_TOKENS": "1000"
    }):
        yield


@pytest.fixture
def mock_openai_response():
    """Sample OpenAI API response for structured output."""
    return {
        "choices": [{
            "message": {
                "content": '''{
                    "entities": ["OpenAI", "Python", "JSON Schema"],
                    "key_facts": ["OpenAI provides structured output", "JSON Schema ensures data validation"],
                    "summary": "This text discusses OpenAI's structured output capabilities using JSON Schema for validation.",
                    "confidence_score": 0.95
                }'''
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 100,
            "total_tokens": 150
        },
        "model": "gpt-4o-mini"
    }


@pytest.fixture
def mock_code_analysis_response():
    """Sample code analysis response."""
    return {
        "choices": [{
            "message": {
                "content": '''{
                    "language": "python",
                    "complexity_score": 3,
                    "issues": ["Missing docstrings", "Long function names"],
                    "strengths": ["Clear variable names", "Good error handling"],
                    "recommendations": ["Add type hints", "Break down complex functions"],
                    "functions_count": 5,
                    "lines_of_code": 45
                }'''
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 75,
            "completion_tokens": 80,
            "total_tokens": 155
        }
    }


@pytest.fixture
def mock_configuration_task_response():
    """Sample configuration task response."""
    return {
        "choices": [{
            "message": {
                "content": '''{
                    "task_name": "Setup Docker Development Environment",
                    "priority": "high",
                    "steps": [
                        "Install Docker Desktop",
                        "Create Dockerfile",
                        "Build container image",
                        "Test container startup"
                    ],
                    "prerequisites": ["System admin access", "Minimum 8GB RAM"],
                    "estimated_duration": "2 hours",
                    "validation_criteria": ["Container starts without errors", "Application accessible on port 8080"]
                }'''
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 60,
            "completion_tokens": 90,
            "total_tokens": 150
        }
    }


@pytest.fixture
def mock_sentiment_analysis_response():
    """Sample sentiment analysis response."""
    return {
        "choices": [{
            "message": {
                "content": '''{
                    "overall_sentiment": "positive",
                    "confidence": 0.87,
                    "key_phrases": ["great experience", "highly recommend", "excellent service"],
                    "emotions": {
                        "joy": 0.8,
                        "satisfaction": 0.9,
                        "trust": 0.7
                    },
                    "reasoning": "The text contains multiple positive indicators and enthusiastic language suggesting a very positive overall sentiment."
                }'''
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 40,
            "completion_tokens": 70,
            "total_tokens": 110
        }
    }


@pytest.fixture
def mock_error_response():
    """Sample error response for testing."""
    return {
        "error": {
            "message": "Invalid API key provided",
            "type": "invalid_request_error",
            "code": "invalid_api_key"
        }
    }


@pytest.fixture
def sample_code():
    """Sample code for testing code analysis."""
    return '''def calculate_total(items):
    total = 0
    for item in items:
        if item.get('price') and item.get('quantity'):
            total += item['price'] * item['quantity']
    return total

class ShoppingCart:
    def __init__(self):
        self.items = []
    
    def add_item(self, item):
        self.items.append(item)
    
    def get_total(self):
        return calculate_total(self.items)
'''


@pytest.fixture
def sample_unstructured_text():
    """Sample unstructured text for testing data extraction."""
    return '''OpenAI has released GPT-4 with improved capabilities for structured output generation.
The new model can follow JSON Schema specifications more accurately than previous versions.
Developers can now build more reliable AI applications with predictable response formats.
This advancement is particularly beneficial for data extraction and API integration tasks.
'''


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI async client for testing."""
    mock_client = AsyncMock()
    
    # Mock the chat.completions.create method
    mock_completion = MagicMock()
    mock_completion.model_dump.return_value = {
        "choices": [{
            "message": {"content": '{"test": "data"}'},
            "finish_reason": "stop"
        }],
        "usage": {"total_tokens": 50}
    }
    
    mock_client.chat.completions.create.return_value = mock_completion
    return mock_client


@pytest.fixture
def mock_openai_models_response():
    """Mock OpenAI models API response."""
    from types import SimpleNamespace
    
    # Mock model objects
    models_data = [
        SimpleNamespace(id="gpt-5"),
        SimpleNamespace(id="gpt-4o"),
        SimpleNamespace(id="gpt-4o-mini"),
        SimpleNamespace(id="gpt-4-turbo"),
        SimpleNamespace(id="gpt-3.5-turbo")
    ]
    
    # Mock the models response
    return SimpleNamespace(data=models_data)