"""MCP protocol compliance tests for OpenAI Structured MCP server."""

import pytest
import json
import os
from unittest.mock import patch, AsyncMock

# Import shared testing utilities
from tests.shared.base_test_classes import AsyncTestBase, ProtocolComplianceMixin
from tests.shared.mock_factories import OpenAIMockFactory, ErrorScenarioFactory, GenericMockFactory

# Import server with mock API key
with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
    from openai_structured_mcp import server


class TestOpenAIMCPProtocolCompliance(AsyncTestBase, ProtocolComplianceMixin):
    """Test OpenAI Structured MCP server compliance with MCP protocol."""
    
    def setup_method(self):
        super().setup_method()
        self.mock_client = OpenAIMockFactory.create_client_mock()
        self.sample_data = GenericMockFactory.create_sample_data()
    
    @pytest.mark.asyncio
    async def test_tool_registration_compliance(self):
        """Test that all OpenAI tools are properly registered."""
        # Expected tools based on server implementation
        expected_tools = [
            'extract_data',
            'analyze_code',
            'create_configuration_task',
            'analyze_sentiment',
            'custom_structured_query',
            'list_schemas',
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
        # Test extract_data schema
        if hasattr(server, 'mcp') and hasattr(server.mcp, 'tools'):
            extract_tool = server.mcp.tools.get('extract_data')
            if extract_tool and hasattr(extract_tool, 'schema'):
                schema = extract_tool.schema
                self.assert_tool_schema_compliance(schema)
    
    @pytest.mark.asyncio
    async def test_successful_structured_response_format(self):
        """Test that successful responses follow MCP format and return valid JSON."""
        mock_response = OpenAIMockFactory.create_successful_structured_response(
            data={
                "entities": ["OpenAI", "GPT-4"],
                "key_facts": ["Structured output capability"],
                "summary": "Test extraction",
                "confidence_score": 0.95
            }
        )
        
        with patch.object(server, 'openai_client',
                         OpenAIMockFactory.create_client_mock([mock_response])):
            
            result = await server.extract_data(
                text=self.sample_data["unstructured_text"],
                custom_instructions="Extract key information"
            )
            
            # Result should be valid JSON string
            parsed_result = self.assert_valid_json_response(result)
            
            # Should follow MCP response structure
            self.assert_mcp_response_structure(parsed_result)
            assert parsed_result["success"] is True
            assert "data" in parsed_result
            assert "metadata" in parsed_result
    
    @pytest.mark.asyncio
    async def test_error_response_format(self):
        """Test that error responses follow MCP format."""
        error_response = OpenAIMockFactory.create_error_response(
            error_message="Invalid API key",
            error_type="authentication"
        )
        
        with patch.object(server, 'openai_client',
                         OpenAIMockFactory.create_client_mock([error_response])):
            
            result = await server.extract_data(text="test text")
            
            # Error should be handled gracefully
            assert isinstance(result, str)
            assert "Error extracting data:" in result
            assert "Invalid API key" in result
    
    @pytest.mark.asyncio
    async def test_json_schema_compliance(self):
        """Test that structured responses comply with JSON Schema requirements."""
        mock_response = OpenAIMockFactory.create_successful_structured_response(
            schema_name="data_extraction"
        )
        
        with patch.object(server, 'openai_client',
                         OpenAIMockFactory.create_client_mock([mock_response])):
            
            result = await server.extract_data(text="Sample text for extraction")
            parsed_result = self.assert_valid_json_response(result)
            
            # Verify required fields for structured response
            required_fields = ["success", "data", "metadata", "timestamp"]
            for field in required_fields:
                assert field in parsed_result, f"Missing required field: {field}"
            
            # Verify metadata structure
            metadata = parsed_result["metadata"]
            assert "schema_name" in metadata
            assert metadata["schema_name"] == "data_extraction"
    
    @pytest.mark.asyncio
    async def test_code_analysis_protocol_compliance(self):
        """Test code analysis tool follows MCP protocol."""
        mock_response = OpenAIMockFactory.create_successful_structured_response(
            data={
                "language": "python",
                "complexity_score": 3,
                "issues": ["Missing docstrings"],
                "strengths": ["Clear naming"],
                "functions_count": 1,
                "lines_of_code": 10
            },
            schema_name="code_analysis"
        )
        
        with patch.object(server, 'openai_client',
                         OpenAIMockFactory.create_client_mock([mock_response])):
            
            result = await server.analyze_code(
                code=self.sample_data["sample_code"],
                language_hint="python"
            )
            
            parsed_result = self.assert_valid_json_response(result)
            self.assert_mcp_response_structure(parsed_result)
            
            # Verify code analysis specific structure
            data = parsed_result["data"]
            assert "language" in data
            assert "complexity_score" in data
            assert data["language"] == "python"
    
    @pytest.mark.asyncio
    async def test_configuration_task_protocol_compliance(self):
        """Test configuration task creation follows MCP protocol."""
        mock_response = OpenAIMockFactory.create_successful_structured_response(
            data={
                "task_name": "Setup CI/CD Pipeline",
                "priority": "high",
                "steps": ["Create workflow", "Configure stages"],
                "prerequisites": ["GitHub access"],
                "estimated_duration": "4 hours",
                "validation_criteria": ["Pipeline runs successfully"]
            },
            schema_name="configuration_task"
        )
        
        with patch.object(server, 'openai_client',
                         OpenAIMockFactory.create_client_mock([mock_response])):
            
            result = await server.create_configuration_task(
                description=self.sample_data["configuration_description"]
            )
            
            parsed_result = self.assert_valid_json_response(result)
            self.assert_mcp_response_structure(parsed_result)
            
            # Verify configuration task specific structure
            data = parsed_result["data"]
            required_task_fields = ["task_name", "priority", "steps"]
            for field in required_task_fields:
                assert field in data, f"Missing task field: {field}"
    
    @pytest.mark.asyncio
    async def test_sentiment_analysis_protocol_compliance(self):
        """Test sentiment analysis follows MCP protocol."""
        mock_response = OpenAIMockFactory.create_successful_structured_response(
            data={
                "overall_sentiment": "positive",
                "confidence": 0.89,
                "key_phrases": ["excellent", "highly recommend"],
                "emotions": {
                    "joy": 0.8,
                    "satisfaction": 0.9
                },
                "reasoning": "Positive language indicators detected"
            },
            schema_name="sentiment_analysis"
        )
        
        with patch.object(server, 'openai_client',
                         OpenAIMockFactory.create_client_mock([mock_response])):
            
            result = await server.analyze_sentiment(
                text=self.sample_data["sentiment_text"]
            )
            
            parsed_result = self.assert_valid_json_response(result)
            self.assert_mcp_response_structure(parsed_result)
            
            # Verify sentiment analysis specific structure
            data = parsed_result["data"]
            sentiment_fields = ["overall_sentiment", "confidence", "emotions"]
            for field in sentiment_fields:
                assert field in data, f"Missing sentiment field: {field}"
    
    @pytest.mark.asyncio
    async def test_custom_query_protocol_compliance(self):
        """Test custom structured query follows MCP protocol."""
        mock_response = OpenAIMockFactory.create_successful_structured_response(
            data={"custom": "result"},
            schema_name="data_extraction"
        )
        
        with patch.object(server, 'openai_client',
                         OpenAIMockFactory.create_client_mock([mock_response])):
            
            result = await server.custom_structured_query(
                prompt="Extract custom information",
                schema_name="data_extraction",
                system_message="Custom system prompt",
                model="gpt-4o-mini",
                temperature=0.3,
                max_tokens=500
            )
            
            parsed_result = self.assert_valid_json_response(result)
            self.assert_mcp_response_structure(parsed_result)
            
            # Verify custom query maintains structure
            assert "metadata" in parsed_result
            assert parsed_result["metadata"]["schema_name"] == "data_extraction"
    
    @pytest.mark.asyncio
    async def test_input_validation_compliance(self):
        """Test input validation follows MCP patterns."""
        mock_response = OpenAIMockFactory.create_successful_structured_response()
        
        with patch.object(server, 'openai_client',
                         OpenAIMockFactory.create_client_mock([mock_response])):
            
            # Test with edge case inputs
            edge_cases = ErrorScenarioFactory.create_edge_case_inputs()
            
            for case in edge_cases[:3]:  # Test first 3 edge cases
                result = await server.extract_data(text=case["input"])
                
                # Should handle edge cases gracefully
                if "Error" in result:
                    assert isinstance(result, str)
                else:
                    parsed_result = json.loads(result)
                    assert isinstance(parsed_result, dict)
    
    @pytest.mark.asyncio
    async def test_schema_parameter_validation(self):
        """Test schema parameter validation in custom queries."""
        mock_response = OpenAIMockFactory.create_successful_structured_response()
        mock_client = OpenAIMockFactory.create_client_mock([mock_response])
        
        with patch.object(server, 'openai_client', mock_client):
            # Test with valid schema names
            valid_schemas = ["data_extraction", "code_analysis", "sentiment_analysis"]
            
            for schema_name in valid_schemas:
                result = await server.custom_structured_query(
                    prompt="test prompt",
                    schema_name=schema_name
                )
                
                # Should succeed with valid schemas
                parsed_result = self.assert_valid_json_response(result)
                assert parsed_result["metadata"]["schema_name"] == schema_name
    
    @pytest.mark.asyncio
    async def test_exception_handling_compliance(self):
        """Test that exceptions are handled according to MCP protocol."""
        # Test with client that raises exceptions
        mock_client = OpenAIMockFactory.create_client_mock()
        mock_client.extract_data.side_effect = Exception("Network error")
        
        with patch.object(server, 'openai_client', mock_client):
            result = await server.extract_data(text="test text")
            
            # Exception should be caught and returned as error message
            assert isinstance(result, str)
            assert "Error during data extraction:" in result
            assert "Network error" in result
    
    @pytest.mark.asyncio
    async def test_health_check_protocol_compliance(self):
        """Test health check follows MCP protocol patterns."""
        # Test successful health check
        mock_client = OpenAIMockFactory.create_client_mock()
        mock_client.health_check.return_value = True
        mock_client.structured_completion.return_value = OpenAIMockFactory.create_successful_structured_response()
        
        with patch.object(server, 'openai_client', mock_client):
            result = await server.health_check()
            
            assert isinstance(result, str)
            assert "✅" in result
            assert "accessible and structured outputs are working correctly" in result
        
        # Test failed basic health check
        mock_client.health_check.return_value = False
        
        with patch.object(server, 'openai_client', mock_client):
            result = await server.health_check()
            
            assert isinstance(result, str)
            assert "❌" in result
            assert "not responding correctly" in result
    
    @pytest.mark.asyncio
    async def test_list_schemas_protocol_compliance(self):
        """Test list schemas follows MCP protocol patterns."""
        mock_client = OpenAIMockFactory.create_client_mock()
        
        with patch.object(server, 'openai_client', mock_client):
            result = await server.list_schemas()
            
            # Should return formatted string with schema information
            assert isinstance(result, str)
            assert "data_extraction" in result
            assert "code_analysis" in result
            assert "configuration_task" in result
            assert "sentiment_analysis" in result
            assert "Usage Tips:" in result
            
            # Should include schema descriptions
            assert "Extract structured data" in result
            assert "Analyze code" in result
    
    @pytest.mark.asyncio
    async def test_response_timing_metadata(self):
        """Test that responses include timing metadata when available."""
        mock_response = OpenAIMockFactory.create_successful_structured_response(
            processing_time_ms=250.5
        )
        
        with patch.object(server, 'openai_client',
                         OpenAIMockFactory.create_client_mock([mock_response])):
            
            result = await server.extract_data(text="test")
            parsed_result = self.assert_valid_json_response(result)
            
            # Should include timing information
            assert "processing_time_ms" in parsed_result
            assert parsed_result["processing_time_ms"] == 250.5
    
    @pytest.mark.asyncio
    async def test_structured_vs_error_response_format(self):
        """Test distinction between structured responses and error responses."""
        # Test successful structured response
        success_response = OpenAIMockFactory.create_successful_structured_response()
        
        with patch.object(server, 'openai_client',
                         OpenAIMockFactory.create_client_mock([success_response])):
            
            result = await server.extract_data(text="test")
            parsed_result = self.assert_valid_json_response(result)
            assert parsed_result["success"] is True
        
        # Test error response
        error_response = OpenAIMockFactory.create_error_response()
        
        with patch.object(server, 'openai_client',
                         OpenAIMockFactory.create_client_mock([error_response])):
            
            result = await server.extract_data(text="test")
            # Error responses are returned as error strings, not JSON
            assert isinstance(result, str)
            assert "Error extracting data:" in result
