"""Tests for Perplexity API client."""

import pytest
import os
from unittest.mock import patch, AsyncMock
import httpx

from perplexity_mcp.client import PerplexityClient


class TestPerplexityClient:
    """Test cases for PerplexityClient."""
    
    def test_init_with_api_key(self):
        """Test client initialization with API key."""
        client = PerplexityClient(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.base_url == "https://api.perplexity.ai/chat/completions"
    
    def test_init_without_api_key_raises_error(self):
        """Test client initialization without API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="PERPLEXITY_API_KEY environment variable is required"):
                PerplexityClient()
    
    @patch.dict(os.environ, {"PERPLEXITY_API_KEY": "env-test-key"})
    def test_init_from_environment(self):
        """Test client initialization from environment variable."""
        client = PerplexityClient()
        assert client.api_key == "env-test-key"
    
    @pytest.mark.asyncio
    async def test_query_success(self, httpx_mock):
        """Test successful API query."""
        # Mock successful response
        httpx_mock.add_response(
            method="POST",
            url="https://api.perplexity.ai/chat/completions",
            json={
                "choices": [
                    {
                        "message": {
                            "content": "Test response content"
                        }
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 20,
                    "total_tokens": 30
                }
            },
            status_code=200
        )
        
        client = PerplexityClient(api_key="test-key")
        result = await client.query("test prompt")
        
        assert "error" not in result
        assert result["choices"][0]["message"]["content"] == "Test response content"
        assert result["usage"]["total_tokens"] == 30
    
    @pytest.mark.asyncio
    async def test_query_with_custom_parameters(self, httpx_mock):
        """Test query with custom parameters."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.perplexity.ai/chat/completions",
            json={
                "choices": [{"message": {"content": "Custom response"}}],
                "usage": {"total_tokens": 25}
            },
            status_code=200
        )
        
        client = PerplexityClient(api_key="test-key")
        result = await client.query(
            prompt="test",
            model="sonar-deep-research",
            system_message="Custom system message",
            max_tokens=500,
            temperature=0.5,
            search_domain_filter=["example.com"],
            search_recency_filter="week"
        )
        
        assert "error" not in result
        assert result["choices"][0]["message"]["content"] == "Custom response"
        
        # Verify request was made with correct parameters
        request = httpx_mock.get_request()
        request_data = request.json()
        
        assert request_data["model"] == "sonar-deep-research"
        assert request_data["max_tokens"] == 500
        assert request_data["temperature"] == 0.5
        assert request_data["search_domain_filter"] == ["example.com"]
        assert request_data["search_recency_filter"] == "week"
        assert len(request_data["messages"]) == 2
        assert request_data["messages"][0]["role"] == "system"
        assert request_data["messages"][0]["content"] == "Custom system message"
    
    @pytest.mark.asyncio
    async def test_query_invalid_model_fallback(self, httpx_mock):
        """Test query with invalid model falls back to sonar."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.perplexity.ai/chat/completions",
            json={"choices": [{"message": {"content": "Response"}}]},
            status_code=200
        )
        
        client = PerplexityClient(api_key="test-key")
        await client.query("test", model="invalid-model")
        
        request = httpx_mock.get_request()
        request_data = request.json()
        assert request_data["model"] == "sonar"
    
    @pytest.mark.asyncio
    async def test_query_auth_error(self, httpx_mock):
        """Test query with authentication error."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.perplexity.ai/chat/completions",
            status_code=401,
            text="Unauthorized"
        )
        
        client = PerplexityClient(api_key="invalid-key")
        result = await client.query("test")
        
        assert "error" in result
        assert "Authentication failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_query_rate_limit_error(self, httpx_mock):
        """Test query with rate limit error."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.perplexity.ai/chat/completions",
            status_code=429,
            text="Rate limit exceeded"
        )
        
        client = PerplexityClient(api_key="test-key")
        result = await client.query("test")
        
        assert "error" in result
        assert "Rate limit exceeded" in result["error"]
    
    @pytest.mark.asyncio
    async def test_query_network_error(self, httpx_mock):
        """Test query with network error."""
        httpx_mock.add_exception(httpx.RequestError("Network error"))
        
        client = PerplexityClient(api_key="test-key")
        result = await client.query("test")
        
        assert "error" in result
        assert "Network error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_query_with_search_filters(self, httpx_mock):
        """Test query with search domain and recency filters."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.perplexity.ai/chat/completions",
            json={
                "choices": [{"message": {"content": "Research response"}}],
                "usage": {"total_tokens": 50},
                "related_questions": ["Related question 1", "Related question 2"]
            },
            status_code=200
        )
        
        client = PerplexityClient(api_key="test-key")
        result = await client.query(
            prompt="AI research applications and challenges",
            model="sonar-deep-research",
            temperature=0.3,
            search_domain_filter=["arxiv.org"],
            search_recency_filter="month"
        )
        
        assert "error" not in result
        assert result["choices"][0]["message"]["content"] == "Research response"
        assert "related_questions" in result
        
        # Verify request parameters
        request = httpx_mock.get_request()
        request_data = request.json()
        
        assert request_data["model"] == "sonar-deep-research"
        assert request_data["temperature"] == 0.3
        assert "AI research applications and challenges" in request_data["messages"][0]["content"]
        assert request_data["search_domain_filter"] == ["arxiv.org"]
        assert request_data["search_recency_filter"] == "month"
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, httpx_mock):
        """Test successful health check."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.perplexity.ai/chat/completions",
            json={"choices": [{"message": {"content": "OK"}}]},
            status_code=200
        )
        
        client = PerplexityClient(api_key="test-key")
        is_healthy = await client.health_check()
        
        assert is_healthy is True
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, httpx_mock):
        """Test failed health check."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.perplexity.ai/chat/completions",
            status_code=401
        )
        
        client = PerplexityClient(api_key="invalid-key")
        is_healthy = await client.health_check()
        
        assert is_healthy is False