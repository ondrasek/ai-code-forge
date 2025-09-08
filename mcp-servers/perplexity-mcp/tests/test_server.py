"""Tests for FastMCP server implementation."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import os

# Import server components
with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"}):
    from perplexity_mcp import server


@pytest.fixture
def mock_perplexity_client():
    """Mock Perplexity client for testing."""
    mock_client = AsyncMock()
    mock_client.AVAILABLE_MODELS = ["sonar", "sonar-pro", "sonar-reasoning", "sonar-deep-research"]
    return mock_client


class TestMCPTools:
    """Test cases for MCP server tools."""
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"})
    async def test_perplexity_search_success(self, mock_perplexity_client):
        """Test successful perplexity search."""
        # Mock successful API response
        mock_response = {
            "choices": [{"message": {"content": "Research result"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            "related_questions": ["Question 1", "Question 2"]
        }
        mock_perplexity_client.query.return_value = mock_response
        
        with patch.object(server, 'perplexity_client', mock_perplexity_client):
            result = await server.perplexity_search.fn(
                query="test query",
                model="sonar",
                system_prompt="Custom prompt",
                max_tokens=500,
                temperature=0.8
            )
        
        # Verify the result
        assert "Research result" in result
        assert "Related Questions:" in result
        assert "Question 1" in result
        assert "Question 2" in result
        
        # Verify client was called correctly
        mock_perplexity_client.query.assert_called_once_with(
            prompt="test query",
            model="sonar",
            system_message="Custom prompt",
            max_tokens=500,
            temperature=0.8,
            top_p=1.0,
            presence_penalty=0.0,
            frequency_penalty=0.0,
            search_domain_filter=None,
            search_recency_filter=None,
            return_citations=True,
            return_related_questions=True
        )
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"})
    async def test_perplexity_search_with_defaults(self, mock_perplexity_client):
        """Test perplexity search with default parameters."""
        mock_response = {
            "choices": [{"message": {"content": "Default result"}}]
        }
        mock_perplexity_client.query.return_value = mock_response
        
        with patch.object(server, 'perplexity_client', mock_perplexity_client):
            result = await server.perplexity_search.fn(query="test query")
        
        assert "Default result" in result
        
        # Verify default system message was used
        call_args = mock_perplexity_client.query.call_args
        assert "comprehensive research response" in call_args[1]["system_message"].lower()
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"})
    async def test_perplexity_search_api_error(self, mock_perplexity_client):
        """Test perplexity search with API error."""
        mock_response = {"error": "API authentication failed"}
        mock_perplexity_client.query.return_value = mock_response
        
        with patch.object(server, 'perplexity_client', mock_perplexity_client):
            result = await server.perplexity_search.fn(query="test query")
        
        assert "Research failed:" in result
        assert "API authentication failed" in result
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"})
    async def test_perplexity_deep_research_success(self, mock_perplexity_client):
        """Test successful deep research."""
        mock_response = {
            "choices": [{"message": {"content": "Deep research result"}}],
            "citations": ["Source 1", "Source 2"],
            "related_questions": ["Deep question 1"]
        }
        mock_perplexity_client.query.return_value = mock_response
        
        with patch.object(server, 'perplexity_client', mock_perplexity_client):
            result = await server.perplexity_deep_research.fn(
                topic="AI research",
                search_domain_filter=["arxiv.org"],
                search_filter="month",
                max_tokens=2000
            )
        
        # Verify the result includes all components
        assert "Deep research result" in result
        assert "Related Research Questions:" in result
        assert "Deep question 1" in result
        
        # Verify client was called correctly
        expected_prompt = "Conduct comprehensive research on: AI research"
        call_args = mock_perplexity_client.query.call_args
        assert call_args[1]["prompt"] == expected_prompt
        assert call_args[1]["model"] == "sonar-deep-research"
        assert call_args[1]["max_tokens"] == 2000
        assert call_args[1]["temperature"] == 0.3
        assert call_args[1]["search_domain_filter"] == ["arxiv.org"]
        assert call_args[1]["search_filter"] == "month"
        assert call_args[1]["return_citations"] == True
        assert call_args[1]["return_related_questions"] == True
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"})
    async def test_perplexity_quick_query_success(self, mock_perplexity_client):
        """Test successful quick query."""
        mock_response = {
            "choices": [{"message": {"content": "Quick answer"}}]
        }
        mock_perplexity_client.query.return_value = mock_response
        
        with patch.object(server, 'perplexity_client', mock_perplexity_client):
            result = await server.perplexity_quick_query.fn(
                question="What is Python?",
                search_domain_filter=["python.org"],
                search_recency_filter="week"
            )
        
        assert result == "Quick answer"
        
        # Verify client was called with quick query parameters
        call_args = mock_perplexity_client.query.call_args
        assert call_args[1]["model"] == "sonar"
        assert call_args[1]["max_tokens"] == 500
        assert call_args[1]["temperature"] == 0.3
        assert "concise" in call_args[1]["system_message"].lower()
        assert call_args[1]["search_domain_filter"] == ["python.org"]
        assert call_args[1]["search_recency_filter"] == "week"
    
    @pytest.mark.asyncio
    async def test_list_models(self):
        """Test list models functionality."""
        result = await server.list_models.fn()
        
        # Verify all models are listed
        assert "sonar" in result
        assert "sonar-pro" in result
        assert "sonar-reasoning" in result
        assert "sonar-deep-research" in result
        
        # Verify descriptions are present
        assert "Fast, general-purpose" in result
        assert "Enhanced version" in result
        assert "Usage Tips:" in result
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"})
    async def test_health_check_success(self, mock_perplexity_client):
        """Test successful health check."""
        mock_perplexity_client.health_check.return_value = True
        
        with patch.object(server, 'perplexity_client', mock_perplexity_client):
            result = await server.health_check.fn()
        
        assert "✅" in result
        assert "accessible and working correctly" in result
        mock_perplexity_client.health_check.assert_called_once()
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"})
    async def test_health_check_failure(self, mock_perplexity_client):
        """Test failed health check."""
        mock_perplexity_client.health_check.return_value = False
        
        with patch.object(server, 'perplexity_client', mock_perplexity_client):
            result = await server.health_check.fn()
        
        assert "❌" in result
        assert "not responding correctly" in result
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"})
    async def test_health_check_exception(self, mock_perplexity_client):
        """Test health check with exception."""
        mock_perplexity_client.health_check.side_effect = Exception("Connection error")
        
        with patch.object(server, 'perplexity_client', mock_perplexity_client):
            result = await server.health_check.fn()
        
        assert "❌" in result
        assert "Health check failed" in result
        assert "Connection error" in result


class TestServerInitialization:
    """Test cases for server initialization."""
    
    @patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"})
    def test_server_initialization_success(self):
        """Test successful server initialization."""
        # This test ensures the module can be imported without errors
        # when the API key is present
        assert server.mcp is not None
        assert hasattr(server, 'perplexity_client')
    
    def test_server_initialization_no_api_key(self):
        """Test server initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="PERPLEXITY_API_KEY"):
                # Re-import to trigger initialization error
                import importlib
                importlib.reload(server)
    
    @patch('perplexity_mcp.server.FastMCP')
    def test_main_function(self, mock_fastmcp):
        """Test main function execution."""
        mock_mcp_instance = MagicMock()
        mock_fastmcp.return_value = mock_mcp_instance
        
        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"}):
            server.main()
        
        mock_mcp_instance.run.assert_called_once()
    
    @patch('perplexity_mcp.server.FastMCP')
    def test_main_function_keyboard_interrupt(self, mock_fastmcp):
        """Test main function with keyboard interrupt."""
        mock_mcp_instance = MagicMock()
        mock_mcp_instance.run.side_effect = KeyboardInterrupt()
        mock_fastmcp.return_value = mock_mcp_instance
        
        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"}):
            # Should not raise exception
            server.main()
        
        mock_mcp_instance.run.assert_called_once()