"""MCP protocol compliance tests for Perplexity MCP server."""

import pytest
import json
import os
from unittest.mock import patch, AsyncMock

# Import shared testing utilities
from tests.shared.base_test_classes import AsyncTestBase, ProtocolComplianceMixin
from tests.shared.mock_factories import PerplexityMockFactory, ErrorScenarioFactory

# Import server with mock API key
with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"}):
    from perplexity_mcp import server


class TestPerplexityMCPProtocolCompliance(AsyncTestBase, ProtocolComplianceMixin):
    """Test Perplexity MCP server compliance with MCP protocol."""
    
    def setup_method(self):
        super().setup_method()
        self.mock_client = PerplexityMockFactory.create_client_mock()
    
    @pytest.mark.asyncio
    async def test_tool_registration_compliance(self):
        """Test that all Perplexity tools are properly registered."""
        # Expected tools based on server implementation
        expected_tools = [
            'perplexity_search',
            'perplexity_deep_research', 
            'perplexity_quick_query',
            'list_models',
            'health_check'
        ]
        
        # Get registered tools from the FastMCP instance
        tools = []
        if hasattr(server, 'mcp') and hasattr(server.mcp, 'tools'):
            tools = list(server.mcp.tools.keys())
        
        # Assert all required tools are registered
        self.assert_tool_registration(tools, expected_tools)
        
        # Verify each tool has proper structure
        for tool_name in expected_tools:
            assert tool_name in tools, f"Tool {tool_name} not registered"
    
    @pytest.mark.asyncio
    async def test_tool_schema_compliance(self):
        """Test tool schemas comply with MCP protocol."""
        # Test perplexity_search schema
        if hasattr(server, 'mcp') and hasattr(server.mcp, 'tools'):
            search_tool = server.mcp.tools.get('perplexity_search')
            if search_tool and hasattr(search_tool, 'schema'):
                schema = search_tool.schema
                self.assert_tool_schema_compliance(schema)
    
    @pytest.mark.asyncio
    async def test_successful_tool_response_format(self):
        """Test that successful tool responses follow MCP format."""
        mock_response = PerplexityMockFactory.create_successful_response(
            content="Test research result",
            related_questions=["What is AI?"],
            citations=["Source 1"]
        )
        
        with patch.object(server, 'perplexity_client', 
                         PerplexityMockFactory.create_client_mock([mock_response])):
            
            result = await server.perplexity_search(query="test query")
            
            # Result should be a string (MCP tool result format)
            assert isinstance(result, str)
            assert len(result) > 0
            assert "Test research result" in result
    
    @pytest.mark.asyncio
    async def test_error_response_format(self):
        """Test that error responses follow MCP format."""
        error_response = PerplexityMockFactory.create_error_response(
            error_message="API authentication failed",
            error_type="authentication"
        )
        
        with patch.object(server, 'perplexity_client',
                         PerplexityMockFactory.create_client_mock([error_response])):
            
            result = await server.perplexity_search(query="test query")
            
            # Error should be handled gracefully and returned as string
            assert isinstance(result, str)
            assert "Research failed:" in result
            assert "API authentication failed" in result
    
    @pytest.mark.asyncio
    async def test_input_validation_compliance(self):
        """Test input validation follows MCP patterns."""
        # Test with valid inputs
        mock_response = PerplexityMockFactory.create_successful_response()
        
        with patch.object(server, 'perplexity_client',
                         PerplexityMockFactory.create_client_mock([mock_response])):
            
            # Valid query should succeed
            result = await server.perplexity_search(query="valid query")
            assert isinstance(result, str)
            assert len(result) > 0
            
            # Test with edge case inputs
            edge_cases = ErrorScenarioFactory.create_edge_case_inputs()
            
            for case in edge_cases[:3]:  # Test first 3 edge cases
                result = await server.perplexity_search(query=case["input"])
                assert isinstance(result, str), f"Failed for {case['description']}"
    
    @pytest.mark.asyncio
    async def test_model_parameter_validation(self):
        """Test model parameter validation."""
        mock_response = PerplexityMockFactory.create_successful_response()
        
        with patch.object(server, 'perplexity_client',
                         PerplexityMockFactory.create_client_mock([mock_response])):
            
            # Valid models should work
            valid_models = ["sonar", "sonar-pro", "sonar-reasoning"]
            
            for model in valid_models:
                result = await server.perplexity_search(
                    query="test query",
                    model=model
                )
                assert isinstance(result, str)
                assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_parameter_type_compliance(self):
        """Test parameter types follow schema definitions."""
        mock_response = PerplexityMockFactory.create_successful_response()
        
        with patch.object(server, 'perplexity_client',
                         PerplexityMockFactory.create_client_mock([mock_response])):
            
            # Test with correct parameter types
            result = await server.perplexity_search(
                query="test query",  # string
                model="sonar",  # string
                max_tokens=500,  # integer
                temperature=0.7  # float
            )
            assert isinstance(result, str)
    
    @pytest.mark.asyncio
    async def test_exception_handling_compliance(self):
        """Test that exceptions are handled according to MCP protocol."""
        # Test with client that raises exceptions
        mock_client = PerplexityMockFactory.create_client_mock()
        mock_client.query.side_effect = Exception("Network error")
        
        with patch.object(server, 'perplexity_client', mock_client):
            result = await server.perplexity_search(query="test query")
            
            # Exception should be caught and returned as error message
            assert isinstance(result, str)
            assert "failed" in result.lower() or "error" in result.lower()
    
    @pytest.mark.asyncio
    async def test_health_check_protocol_compliance(self):
        """Test health check follows MCP protocol patterns."""
        # Test successful health check
        mock_client = PerplexityMockFactory.create_client_mock()
        mock_client.health_check.return_value = True
        
        with patch.object(server, 'perplexity_client', mock_client):
            result = await server.health_check()
            
            assert isinstance(result, str)
            assert "✅" in result or "working correctly" in result
        
        # Test failed health check
        mock_client.health_check.return_value = False
        
        with patch.object(server, 'perplexity_client', mock_client):
            result = await server.health_check()
            
            assert isinstance(result, str)
            assert "❌" in result or "not responding" in result
    
    @pytest.mark.asyncio
    async def test_deep_research_protocol_compliance(self):
        """Test deep research tool follows MCP protocol."""
        mock_response = PerplexityMockFactory.create_successful_response(
            content="Deep research analysis",
            citations=["Academic Source 1", "Research Paper 2"],
            related_questions=["Follow-up question 1"]
        )
        
        with patch.object(server, 'perplexity_client',
                         PerplexityMockFactory.create_client_mock([mock_response])):
            
            result = await server.perplexity_deep_research(
                topic="AI research",
                focus_areas=["machine learning", "ethics"],
                time_filter="month",
                domain_filter=["arxiv.org"],
                max_tokens=2000
            )
            
            # Verify response structure
            assert isinstance(result, str)
            assert "Deep research analysis" in result
            assert "Sources:" in result or "Citations:" in result
            assert "Related Research Questions:" in result
    
    @pytest.mark.asyncio
    async def test_quick_query_protocol_compliance(self):
        """Test quick query tool follows MCP protocol."""
        mock_response = PerplexityMockFactory.create_successful_response(
            content="Quick answer"
        )
        
        with patch.object(server, 'perplexity_client',
                         PerplexityMockFactory.create_client_mock([mock_response])):
            
            result = await server.perplexity_quick_query(
                question="What is Python?",
                domain_filter=["python.org"],
                recency_filter="week"
            )
            
            assert isinstance(result, str)
            assert result == "Quick answer"  # Should return just the content
    
    @pytest.mark.asyncio
    async def test_list_models_protocol_compliance(self):
        """Test list models follows MCP protocol patterns."""
        result = await server.list_models()
        
        # Should return formatted string with model information
        assert isinstance(result, str)
        assert "sonar" in result
        assert "sonar-pro" in result
        assert "sonar-reasoning" in result
        assert "sonar-deep-research" in result
        assert "Usage Tips:" in result
        
        # Should include model descriptions
        assert "Fast, general-purpose" in result
        assert "Enhanced version" in result
