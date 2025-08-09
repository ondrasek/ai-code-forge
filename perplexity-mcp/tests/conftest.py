"""Pytest configuration and fixtures for Perplexity MCP server tests."""

import pytest
import os
from unittest.mock import patch
import asyncio


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
        "PERPLEXITY_API_KEY": "test-api-key-123",
        "PERPLEXITY_LOG_LEVEL": "DEBUG",
        "PERPLEXITY_DEFAULT_MODEL": "sonar",
        "PERPLEXITY_DEFAULT_SYSTEM": "Test system message"
    }):
        yield


@pytest.fixture
def sample_api_response():
    """Sample API response for testing."""
    return {
        "choices": [
            {
                "message": {
                    "content": "This is a sample response from Perplexity API with comprehensive information about the query."
                }
            }
        ],
        "usage": {
            "prompt_tokens": 15,
            "completion_tokens": 45,
            "total_tokens": 60
        },
        "citations": [
            "https://example.com/source1",
            "https://example.com/source2"
        ],
        "related_questions": [
            "What are the key benefits?",
            "How does this compare to alternatives?",
            "What are the potential drawbacks?"
        ]
    }


@pytest.fixture
def sample_error_response():
    """Sample error response for testing."""
    return {
        "error": "Invalid API key or insufficient credits"
    }


@pytest.fixture
def sample_research_response():
    """Sample research response for testing."""
    return {
        "choices": [
            {
                "message": {
                    "content": """# Comprehensive Research Analysis

## Key Findings
This topic has several important aspects that merit detailed consideration.

## Current State
The current landscape shows significant developments in recent months.

## Multiple Perspectives
Different stakeholders have varying viewpoints on this matter.

## Recent Developments
Latest updates indicate positive trends in the field.

## Practical Implications
The findings suggest several actionable insights for implementation."""
                }
            }
        ],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 120,
            "total_tokens": 170
        },
        "citations": [
            "https://research.example.com/study1",
            "https://academic.example.com/paper2",
            "https://industry.example.com/report3"
        ],
        "related_questions": [
            "What are the long-term implications?",
            "How does this affect different industries?",
            "What are the next steps for implementation?"
        ]
    }