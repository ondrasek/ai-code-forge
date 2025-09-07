"""Comprehensive error handling tests for Perplexity MCP server."""

import pytest
import asyncio
import os
from unittest.mock import patch, AsyncMock, MagicMock

# Import shared testing utilities
from tests.shared.base_test_classes import AsyncTestBase, ErrorSimulationMixin
from tests.shared.mock_factories import PerplexityMockFactory, ErrorScenarioFactory

# Import server with mock API key
with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"}):
    from perplexity_mcp import server


class TestPerplexityErrorHandling(AsyncTestBase, ErrorSimulationMixin):
    """Test comprehensive error handling for Perplexity MCP server."""
    
    def setup_method(self):
        super().setup_method()
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test handling of various network errors."""
        network_errors = self.create_network_errors()
        
        for error in network_errors:
            mock_client = PerplexityMockFactory.create_client_mock()
            mock_client.query.side_effect = error
            
            with patch.object(server, 'perplexity_client', mock_client):
                result = await server.perplexity_search(query="test query")
                
                # Should handle network errors gracefully
                assert isinstance(result, str)
                assert "failed" in result.lower() or "error" in result.lower()
                assert str(error).lower() in result.lower() or type(error).__name__.lower() in result.lower()
    
    @pytest.mark.asyncio
    async def test_api_error_responses(self):
        """Test handling of various API error responses."""
        api_errors = self.create_api_errors()
        
        for error_response in api_errors:
            mock_client = PerplexityMockFactory.create_client_mock([error_response])
            
            with patch.object(server, 'perplexity_client', mock_client):
                result = await server.perplexity_search(query="test query")
                
                # Should handle API errors gracefully
                assert isinstance(result, str)
                assert "Research failed:" in result
                assert error_response["error"] in result
    
    @pytest.mark.asyncio
    async def test_malformed_response_handling(self):
        """Test handling of malformed API responses."""
        # Test various malformed response scenarios
        malformed_scenarios = [
            {},  # Empty response
            {"choices": []},  # No choices
            {"choices": [{"message": {}}]},  # No content
            {"choices": [{"message": {"content": None}}]},  # Null content
            {"invalid": "structure"},  # Completely wrong structure
        ]
        
        for malformed_response in malformed_scenarios:
            mock_client = PerplexityMockFactory.create_client_mock([malformed_response])
            
            with patch.object(server, 'perplexity_client', mock_client):
                result = await server.perplexity_search(query="test query")
                
                # Should handle malformed responses gracefully
                assert isinstance(result, str)
                # Should either extract what's available or provide error message
                assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_timeout_error_handling(self):
        """Test handling of timeout errors."""
        mock_client = PerplexityMockFactory.create_client_mock()
        mock_client.query.side_effect = asyncio.TimeoutError("Request timeout")
        
        with patch.object(server, 'perplexity_client', mock_client):
            result = await server.perplexity_search(query="test query")
            
            # Should handle timeout gracefully
            assert isinstance(result, str)
            assert "timeout" in result.lower() or "failed" in result.lower()
    
    @pytest.mark.asyncio
    async def test_edge_case_input_handling(self):
        """Test handling of edge case inputs."""
        edge_cases = ErrorScenarioFactory.create_edge_case_inputs()
        
        mock_response = PerplexityMockFactory.create_successful_response(
            content="Test response"
        )
        mock_client = PerplexityMockFactory.create_client_mock([mock_response])
        
        with patch.object(server, 'perplexity_client', mock_client):
            for case in edge_cases:
                result = await server.perplexity_search(query=case["input"])
                
                # Should handle all edge cases without crashing
                assert isinstance(result, str)
                # For empty input, might return error or process it
                if case["input"] == "":
                    # Either processes empty string or returns error
                    assert len(result) > 0
                else:
                    # Should process non-empty inputs
                    assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_error_isolation(self):
        """Test that errors in concurrent requests don't affect each other."""
        # Create mix of successful and failing responses
        responses = []
        for i in range(20):
            if i % 3 == 0:  # Every 3rd request fails
                responses.append(PerplexityMockFactory.create_error_response(
                    error_message=f"Error {i}",
                    error_type="test_error"
                ))
            else:
                responses.append(PerplexityMockFactory.create_successful_response(
                    content=f"Success {i}"
                ))
        
        mock_client = PerplexityMockFactory.create_client_mock(responses)
        
        with patch.object(server, 'perplexity_client', mock_client):
            # Run concurrent requests
            tasks = []
            for i in range(20):
                task = server.perplexity_search(query=f"Query {i}")
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Analyze results
            successes = [r for r in results if "Success" in str(r)]
            errors = [r for r in results if "Research failed:" in str(r)]
            exceptions = [r for r in results if isinstance(r, Exception)]
            
            # Should have roughly 2/3 successes and 1/3 handled errors
            assert len(successes) >= 10  # At least ~2/3 should succeed
            assert len(errors) >= 5     # At least ~1/3 should be handled errors
            assert len(exceptions) == 0  # No unhandled exceptions
    
    @pytest.mark.asyncio
    async def test_health_check_error_scenarios(self):
        """Test health check behavior under various error conditions."""
        # Test health check with client failure
        mock_client = PerplexityMockFactory.create_client_mock()
        mock_client.health_check.return_value = False
        
        with patch.object(server, 'perplexity_client', mock_client):
            result = await server.health_check()
            assert "❌" in result
            assert "not responding correctly" in result
        
        # Test health check with exception
        mock_client.health_check.side_effect = Exception("Connection failed")
        
        with patch.object(server, 'perplexity_client', mock_client):
            result = await server.health_check()
            assert "❌" in result
            assert "Health check failed" in result
            assert "Connection failed" in result
    
    @pytest.mark.asyncio
    async def test_deep_research_error_handling(self):
        """Test error handling in deep research operations."""
        # Test with API error
        api_error = PerplexityMockFactory.create_error_response(
            error_message="Research quota exceeded",
            error_type="quota"
        )
        mock_client = PerplexityMockFactory.create_client_mock([api_error])
        
        with patch.object(server, 'perplexity_client', mock_client):
            result = await server.perplexity_deep_research(
                topic="AI research",
                focus_areas=["machine learning"]
            )
            
            # Should handle deep research errors gracefully
            assert isinstance(result, str)
            assert "failed" in result.lower() or "error" in result.lower()
        
        # Test with network exception
        mock_client.research_topic.side_effect = ConnectionError("Network unavailable")
        
        with patch.object(server, 'perplexity_client', mock_client):
            result = await server.perplexity_deep_research(
                topic="AI research",
                focus_areas=["machine learning"]
            )
            
            # Should handle exceptions gracefully
            assert isinstance(result, str)
            assert "failed" in result.lower() or "error" in result.lower()
    
    @pytest.mark.asyncio
    async def test_quick_query_error_handling(self):
        """Test error handling in quick query operations."""
        # Test with various error types
        error_scenarios = [
            PerplexityMockFactory.create_error_response("Rate limit exceeded", "rate_limit"),
            PerplexityMockFactory.create_error_response("Invalid model", "model_error"),
            PerplexityMockFactory.create_error_response("Service unavailable", "service_error")
        ]
        
        for error_response in error_scenarios:
            mock_client = PerplexityMockFactory.create_client_mock([error_response])
            
            with patch.object(server, 'perplexity_client', mock_client):
                result = await server.perplexity_quick_query(
                    question="What is AI?",
                    domain_filter=["example.com"]
                )
                
                # Quick queries should handle all error types
                assert isinstance(result, str)
                # For quick queries, errors might be returned directly or as error messages
                assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_parameter_validation_error_handling(self):
        """Test handling of invalid parameter combinations."""
        mock_response = PerplexityMockFactory.create_successful_response(
            content="Valid response"
        )
        mock_client = PerplexityMockFactory.create_client_mock([mock_response])
        
        with patch.object(server, 'perplexity_client', mock_client):
            # Test with potentially problematic parameter combinations
            test_cases = [
                {"query": "test", "max_tokens": -1},  # Negative max_tokens
                {"query": "test", "temperature": 2.5},  # High temperature
                {"query": "test", "model": "invalid-model"},  # Invalid model
            ]
            
            for params in test_cases:
                # These should either be handled gracefully or passed through
                # The server should not crash regardless
                try:
                    result = await server.perplexity_search(**params)
                    assert isinstance(result, str)
                    assert len(result) > 0
                except Exception as e:
                    # If exceptions occur, they should be handled appropriately
                    assert isinstance(e, (ValueError, TypeError)), f"Unexpected exception type: {type(e)}"
    
    @pytest.mark.asyncio
    async def test_resource_cleanup_after_errors(self):
        """Test that resources are properly cleaned up after errors."""
        # Test multiple consecutive errors
        error_responses = [PerplexityMockFactory.create_error_response(
            f"Error {i}", "test_error"
        ) for i in range(10)]
        
        mock_client = PerplexityMockFactory.create_client_mock(error_responses)
        
        with patch.object(server, 'perplexity_client', mock_client):
            # Run multiple failing requests
            for i in range(10):
                result = await server.perplexity_search(query=f"Error test {i}")
                assert "Research failed:" in result
                assert f"Error {i}" in result
            
            # After errors, successful request should still work
            success_response = PerplexityMockFactory.create_successful_response(
                content="Recovery successful"
            )
            mock_client.query.return_value = success_response
            
            result = await server.perplexity_search(query="Recovery test")
            assert "Recovery successful" in result
    
    @pytest.mark.asyncio
    async def test_error_message_formatting(self):
        """Test that error messages are properly formatted and informative."""
        test_errors = [
            {"error": "Authentication failed", "error_type": "auth"},
            {"error": "Rate limit exceeded. Try again later.", "error_type": "rate_limit"},
            {"error": "Model temporarily unavailable", "error_type": "model_error"},
            {"error": "Request validation failed: invalid parameters", "error_type": "validation"}
        ]
        
        for error_data in test_errors:
            mock_client = PerplexityMockFactory.create_client_mock([error_data])
            
            with patch.object(server, 'perplexity_client', mock_client):
                result = await server.perplexity_search(query="test")
                
                # Error messages should be well-formatted and informative
                assert "Research failed:" in result
                assert error_data["error"] in result
                
                # Should not contain internal debugging information
                assert "traceback" not in result.lower()
                assert "exception" not in result.lower()
                
                # Should be user-friendly
                assert len(result) < 500  # Not overly verbose
                assert result.isprintable()  # No control characters
