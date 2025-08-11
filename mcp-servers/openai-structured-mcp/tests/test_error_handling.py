"""Comprehensive error handling tests for OpenAI Structured MCP server."""

import pytest
import asyncio
import json
import os
from unittest.mock import patch, AsyncMock, MagicMock

# Import shared testing utilities
from tests.shared.base_test_classes import AsyncTestBase, ErrorSimulationMixin
from tests.shared.mock_factories import OpenAIMockFactory, ErrorScenarioFactory, GenericMockFactory

# Import server with mock API key
with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
    from openai_structured_mcp import server


class TestOpenAIErrorHandling(AsyncTestBase, ErrorSimulationMixin):
    """Test comprehensive error handling for OpenAI Structured MCP server."""
    
    def setup_method(self):
        super().setup_method()
        self.sample_data = GenericMockFactory.create_sample_data()
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test handling of various network errors."""
        network_errors = self.create_network_errors()
        
        for error in network_errors:
            mock_client = OpenAIMockFactory.create_client_mock()
            mock_client.extract_data.side_effect = error
            
            with patch.object(server, 'openai_client', mock_client):
                result = await server.extract_data(text="test text")
                
                # Should handle network errors gracefully
                assert isinstance(result, str)
                assert "Error during data extraction:" in result
                assert str(error) in result or type(error).__name__ in result
    
    @pytest.mark.asyncio
    async def test_api_error_responses(self):
        """Test handling of various API error responses."""
        api_errors = self.create_api_errors()
        
        for error_response in api_errors:
            mock_client = OpenAIMockFactory.create_client_mock([error_response])
            
            with patch.object(server, 'openai_client', mock_client):
                result = await server.extract_data(text="test text")
                
                # Should handle API errors gracefully
                assert isinstance(result, str)
                assert "Error extracting data:" in result
                assert error_response["error"] in result
    
    @pytest.mark.asyncio
    async def test_malformed_json_response_handling(self):
        """Test handling of malformed JSON responses."""
        malformed_scenarios = [
            {},  # Empty response
            {"success": True},  # Missing data
            {"data": "not an object"},  # Invalid data type
            {"success": True, "data": None},  # Null data
            {"invalid": "structure"},  # Wrong structure entirely
        ]
        
        for malformed_response in malformed_scenarios:
            mock_client = OpenAIMockFactory.create_client_mock([malformed_response])
            
            with patch.object(server, 'openai_client', mock_client):
                result = await server.extract_data(text="test text")
                
                # Should handle malformed responses gracefully
                assert isinstance(result, str)
                
                # Should either provide a valid JSON response or error message
                if result.startswith('{'):
                    # If it returns JSON, it should be valid
                    try:
                        parsed = json.loads(result)
                        assert isinstance(parsed, dict)
                    except json.JSONDecodeError:
                        pytest.fail("Invalid JSON returned")
                else:
                    # If not JSON, should be error message
                    assert "Error extracting data:" in result
    
    @pytest.mark.asyncio
    async def test_schema_validation_errors(self):
        """Test handling of schema validation errors."""
        # Test with invalid schema response
        invalid_schema_error = OpenAIMockFactory.create_error_response(
            error_message="Schema validation failed",
            error_type="validation_error"
        )
        
        mock_client = OpenAIMockFactory.create_client_mock([invalid_schema_error])
        
        with patch.object(server, 'openai_client', mock_client):
            result = await server.custom_structured_query(
                prompt="test prompt",
                schema_name="invalid_schema"
            )
            
            # Should handle schema validation errors
            assert isinstance(result, str)
            assert "Error in custom query:" in result
            assert "Schema validation failed" in result
    
    @pytest.mark.asyncio
    async def test_code_analysis_error_handling(self):
        """Test error handling in code analysis operations."""
        # Test with various error scenarios
        error_scenarios = [
            OpenAIMockFactory.create_error_response("Code parsing failed", "parsing_error"),
            OpenAIMockFactory.create_error_response("Language detection failed", "language_error"),
            OpenAIMockFactory.create_error_response("Analysis timeout", "timeout_error")
        ]
        
        for error_response in error_scenarios:
            mock_client = OpenAIMockFactory.create_client_mock([error_response])
            
            with patch.object(server, 'openai_client', mock_client):
                result = await server.analyze_code(
                    code=self.sample_data["sample_code"],
                    language_hint="python"
                )
                
                # Should handle code analysis errors gracefully
                assert isinstance(result, str)
                assert "Error analyzing code:" in result
                assert error_response["error"] in result
    
    @pytest.mark.asyncio
    async def test_sentiment_analysis_error_handling(self):
        """Test error handling in sentiment analysis operations."""
        # Test with network exception
        mock_client = OpenAIMockFactory.create_client_mock()
        mock_client.analyze_sentiment.side_effect = ConnectionError("Connection lost")
        
        with patch.object(server, 'openai_client', mock_client):
            result = await server.analyze_sentiment(
                text=self.sample_data["sentiment_text"]
            )
            
            # Should handle sentiment analysis errors gracefully
            assert isinstance(result, str)
            assert "Error analyzing sentiment:" in result
            assert "Connection lost" in result
    
    @pytest.mark.asyncio
    async def test_configuration_task_error_handling(self):
        """Test error handling in configuration task creation."""
        # Test with API quota error
        quota_error = OpenAIMockFactory.create_error_response(
            error_message="API quota exceeded for configuration tasks",
            error_type="quota_exceeded"
        )
        
        mock_client = OpenAIMockFactory.create_client_mock([quota_error])
        
        with patch.object(server, 'openai_client', mock_client):
            result = await server.create_configuration_task(
                description=self.sample_data["configuration_description"]
            )
            
            # Should handle configuration task errors gracefully
            assert isinstance(result, str)
            assert "Error creating configuration task:" in result
            assert "API quota exceeded" in result
    
    @pytest.mark.asyncio
    async def test_edge_case_input_handling(self):
        """Test handling of edge case inputs."""
        edge_cases = ErrorScenarioFactory.create_edge_case_inputs()
        
        mock_response = OpenAIMockFactory.create_successful_structured_response(
            data={"test": "response"}
        )
        mock_client = OpenAIMockFactory.create_client_mock([mock_response])
        
        with patch.object(server, 'openai_client', mock_client):
            for case in edge_cases:
                result = await server.extract_data(text=case["input"])
                
                # Should handle all edge cases without crashing
                assert isinstance(result, str)
                assert len(result) > 0
                
                # For valid inputs, should return JSON or error message
                if case["input"] and case["description"] != "html_content":
                    # Most inputs should be processed
                    if result.startswith('{'):
                        # Valid JSON response
                        parsed = json.loads(result)
                        assert isinstance(parsed, dict)
                    else:
                        # Error message
                        assert "Error" in result
    
    @pytest.mark.asyncio
    async def test_concurrent_error_isolation(self):
        """Test that errors in concurrent requests don't affect each other."""
        # Create mix of successful and failing responses
        responses = []
        for i in range(15):
            if i % 4 == 0:  # Every 4th request fails
                responses.append(OpenAIMockFactory.create_error_response(
                    error_message=f"Processing error {i}",
                    error_type="processing_error"
                ))
            else:
                responses.append(OpenAIMockFactory.create_successful_structured_response(
                    data={"request_id": i, "status": "success"}
                ))
        
        mock_client = OpenAIMockFactory.create_client_mock(responses)
        
        with patch.object(server, 'openai_client', mock_client):
            # Run concurrent requests
            tasks = []
            for i in range(15):
                task = server.extract_data(text=f"Test text {i}")
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Analyze results
            successes = [r for r in results if not isinstance(r, Exception) and "success" in str(r)]
            errors = [r for r in results if "Error extracting data:" in str(r)]
            exceptions = [r for r in results if isinstance(r, Exception)]
            
            # Should have roughly 3/4 successes and 1/4 handled errors
            assert len(successes) >= 9   # At least ~3/4 should succeed
            assert len(errors) >= 3      # At least ~1/4 should be handled errors
            assert len(exceptions) == 0  # No unhandled exceptions
    
    @pytest.mark.asyncio
    async def test_health_check_error_scenarios(self):
        """Test health check behavior under various error conditions."""
        # Test basic health check failure
        mock_client = OpenAIMockFactory.create_client_mock()
        mock_client.health_check.return_value = False
        
        with patch.object(server, 'openai_client', mock_client):
            result = await server.health_check()
            assert "❌" in result
            assert "not responding correctly" in result
        
        # Test structured output failure
        mock_client.health_check.return_value = True
        mock_client.structured_completion.return_value = OpenAIMockFactory.create_error_response(
            "Structured output test failed", "structured_error"
        )
        
        with patch.object(server, 'openai_client', mock_client):
            result = await server.health_check()
            assert "❌" in result
            assert "structured output failed" in result
        
        # Test health check exception
        mock_client.health_check.side_effect = Exception("Health check crashed")
        
        with patch.object(server, 'openai_client', mock_client):
            result = await server.health_check()
            assert "❌" in result
            assert "Health check failed" in result
            assert "Health check crashed" in result
    
    @pytest.mark.asyncio
    async def test_json_parsing_error_recovery(self):
        """Test recovery from JSON parsing errors."""
        # Test malformed JSON responses
        malformed_json_strings = ErrorScenarioFactory.create_malformed_responses()
        
        for malformed_json in malformed_json_strings:
            # Mock a response that would cause JSON parsing issues
            mock_client = OpenAIMockFactory.create_client_mock()
            mock_client.extract_data.return_value = malformed_json
            
            with patch.object(server, 'openai_client', mock_client):
                # This simulates internal JSON parsing issues
                # The actual error handling depends on implementation
                try:
                    result = await server.extract_data(text="test")
                    # If no exception, result should be handled gracefully
                    assert isinstance(result, str)
                    assert len(result) > 0
                except Exception as e:
                    # If exception occurs, it should be a controlled one
                    assert "JSON" in str(e) or "parsing" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_parameter_validation_error_handling(self):
        """Test handling of invalid parameter combinations."""
        mock_response = OpenAIMockFactory.create_successful_structured_response(
            data={"valid": "response"}
        )
        mock_client = OpenAIMockFactory.create_client_mock([mock_response])
        
        with patch.object(server, 'openai_client', mock_client):
            # Test custom structured query with invalid parameters
            test_cases = [
                {"prompt": "test", "temperature": -0.5},  # Invalid temperature
                {"prompt": "test", "max_tokens": 0},      # Invalid max_tokens
                {"prompt": "", "schema_name": "data_extraction"},  # Empty prompt
            ]
            
            for params in test_cases:
                try:
                    result = await server.custom_structured_query(**params)
                    # Should handle gracefully
                    assert isinstance(result, str)
                    assert len(result) > 0
                except Exception as e:
                    # If exceptions occur, they should be appropriate validation errors
                    assert isinstance(e, (ValueError, TypeError))
    
    @pytest.mark.asyncio
    async def test_large_input_error_handling(self):
        """Test handling of extremely large inputs."""
        # Create very large input
        large_text = "Large input text. " * 10000  # ~180KB input
        
        # Test with potential timeout or size limit error
        size_error = OpenAIMockFactory.create_error_response(
            error_message="Input too large",
            error_type="size_limit"
        )
        
        mock_client = OpenAIMockFactory.create_client_mock([size_error])
        
        with patch.object(server, 'openai_client', mock_client):
            result = await server.extract_data(text=large_text)
            
            # Should handle large input errors gracefully
            assert isinstance(result, str)
            assert "Error extracting data:" in result
            assert "Input too large" in result
    
    @pytest.mark.asyncio
    async def test_resource_cleanup_after_errors(self):
        """Test that resources are properly cleaned up after errors."""
        # Test multiple consecutive errors across different operations
        error_response = OpenAIMockFactory.create_error_response(
            "Service temporarily unavailable", "service_error"
        )
        
        mock_client = OpenAIMockFactory.create_client_mock([error_response])
        
        with patch.object(server, 'openai_client', mock_client):
            # Run multiple different operations that fail
            operations = [
                server.extract_data(text="test"),
                server.analyze_code(code="def test(): pass"),
                server.analyze_sentiment(text="test sentiment"),
                server.create_configuration_task(description="test task")
            ]
            
            for operation in operations:
                result = await operation
                assert "Error" in result
                assert "Service temporarily unavailable" in result
            
            # After errors, successful operations should still work
            success_response = OpenAIMockFactory.create_successful_structured_response(
                data={"recovery": "successful"}
            )
            mock_client.extract_data.return_value = success_response
            
            result = await server.extract_data(text="Recovery test")
            parsed_result = json.loads(result)
            assert parsed_result["success"] is True
            assert parsed_result["data"]["recovery"] == "successful"
    
    @pytest.mark.asyncio
    async def test_error_message_consistency(self):
        """Test that error messages follow consistent patterns."""
        operations_and_errors = [
            ("extract_data", "Error extracting data:"),
            ("analyze_code", "Error analyzing code:"),
            ("analyze_sentiment", "Error analyzing sentiment:"),
            ("create_configuration_task", "Error creating configuration task:"),
            ("custom_structured_query", "Error in custom query:")
        ]
        
        test_error = OpenAIMockFactory.create_error_response(
            "Consistent error message", "test_error"
        )
        
        for operation_name, expected_prefix in operations_and_errors:
            mock_client = OpenAIMockFactory.create_client_mock([test_error])
            
            with patch.object(server, 'openai_client', mock_client):
                if operation_name == "extract_data":
                    result = await server.extract_data(text="test")
                elif operation_name == "analyze_code":
                    result = await server.analyze_code(code="test")
                elif operation_name == "analyze_sentiment":
                    result = await server.analyze_sentiment(text="test")
                elif operation_name == "create_configuration_task":
                    result = await server.create_configuration_task(description="test")
                elif operation_name == "custom_structured_query":
                    result = await server.custom_structured_query(prompt="test", schema_name="data_extraction")
                
                # Check error message consistency
                assert expected_prefix in result
                assert "Consistent error message" in result
                
                # Error messages should be clean and user-friendly
                assert len(result) < 200  # Not overly verbose
                assert result.isprintable()  # No control characters
                assert "traceback" not in result.lower()  # No debug info
