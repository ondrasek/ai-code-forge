"""Integration tests for MCP server coordination."""

import pytest
import asyncio
import os
from unittest.mock import patch, AsyncMock
from concurrent.futures import ThreadPoolExecutor

# Import shared testing utilities
from tests.shared.base_test_classes import AsyncTestBase, PerformanceTestMixin
from tests.shared.mock_factories import PerplexityMockFactory, OpenAIMockFactory, GenericMockFactory
from tests.shared.performance_utils import PerformanceTester

# Setup both servers with mock keys
perplexity_env_patch = patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"})
openai_env_patch = patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})

with perplexity_env_patch, openai_env_patch:
    from perplexity_mcp import server as perplexity_server
    from openai_structured_mcp import server as openai_server


class TestMCPServerCoordination(AsyncTestBase, PerformanceTestMixin):
    """Test coordination between multiple MCP servers."""
    
    def setup_method(self):
        super().setup_method()
        PerformanceTestMixin.__init__(self)
        
        # Setup mock clients
        self.perplexity_mock = PerplexityMockFactory.create_client_mock()
        self.openai_mock = OpenAIMockFactory.create_client_mock()
        
        # Setup sample data
        self.sample_data = GenericMockFactory.create_sample_data()
    
    @pytest.mark.asyncio
    async def test_parallel_server_operations(self):
        """Test parallel operations across both MCP servers."""
        # Setup mock responses
        perplexity_response = PerplexityMockFactory.create_successful_response(
            content="Research result from Perplexity"
        )
        
        openai_response = OpenAIMockFactory.create_successful_structured_response(
            data={"extracted": "Data from OpenAI"}
        )
        
        with patch.object(perplexity_server, 'perplexity_client', 
                         PerplexityMockFactory.create_client_mock([perplexity_response])), \
             patch.object(openai_server, 'openai_client',
                         OpenAIMockFactory.create_client_mock([openai_response])):
            
            # Run operations in parallel
            perplexity_task = perplexity_server.perplexity_search(
                query="AI research trends"
            )
            
            openai_task = openai_server.extract_data(
                text=self.sample_data["unstructured_text"]
            )
            
            # Wait for both to complete
            start_time = asyncio.get_event_loop().time()
            perplexity_result, openai_result = await asyncio.gather(
                perplexity_task,
                openai_task
            )
            duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # Verify both operations succeeded
            assert "Research result from Perplexity" in perplexity_result
            assert "extracted" in openai_result
            
            # Parallel execution should be faster than sequential
            # (This is a mock test, but validates the coordination pattern)
            assert duration_ms < 1000, "Parallel execution took too long"
    
    @pytest.mark.asyncio
    async def test_sequential_workflow_integration(self):
        """Test sequential workflow using both servers."""
        # Step 1: Use Perplexity to research a topic
        research_response = PerplexityMockFactory.create_successful_response(
            content="AI is transforming software development through automated code generation and analysis.",
            related_questions=["How does AI help developers?"]
        )
        
        # Step 2: Use OpenAI to extract structured data from the research
        extraction_response = OpenAIMockFactory.create_successful_structured_response(
            data={
                "entities": ["AI", "software development", "code generation"],
                "key_facts": ["AI transforms development", "Automated analysis"],
                "summary": "AI enhances software development productivity"
            }
        )
        
        with patch.object(perplexity_server, 'perplexity_client',
                         PerplexityMockFactory.create_client_mock([research_response])), \
             patch.object(openai_server, 'openai_client',
                         OpenAIMockFactory.create_client_mock([extraction_response])):
            
            # Step 1: Research
            research_result = await perplexity_server.perplexity_search(
                query="AI in software development"
            )
            
            # Verify research succeeded
            assert "AI is transforming" in research_result
            
            # Step 2: Extract structured data from research results
            structured_result = await openai_server.extract_data(
                text="AI is transforming software development",
                custom_instructions="Extract key technologies and benefits"
            )
            
            # Verify extraction succeeded
            parsed_result = self.assert_valid_json_response(structured_result)
            assert parsed_result["success"] is True
            assert "AI" in parsed_result["data"]["entities"]
            
            # Workflow completed successfully
            assert len(parsed_result["data"]["key_facts"]) > 0
    
    @pytest.mark.asyncio
    async def test_cross_server_error_handling(self):
        """Test error handling when one server fails in coordinated operations."""
        # Setup: Perplexity succeeds, OpenAI fails
        perplexity_response = PerplexityMockFactory.create_successful_response(
            content="Successful research result"
        )
        
        openai_error = OpenAIMockFactory.create_error_response(
            error_message="API quota exceeded",
            error_type="quota_exceeded"
        )
        
        with patch.object(perplexity_server, 'perplexity_client',
                         PerplexityMockFactory.create_client_mock([perplexity_response])), \
             patch.object(openai_server, 'openai_client',
                         OpenAIMockFactory.create_client_mock([openai_error])):
            
            # Run both operations
            perplexity_task = perplexity_server.perplexity_search(query="test")
            openai_task = openai_server.extract_data(text="test")
            
            perplexity_result, openai_result = await asyncio.gather(
                perplexity_task,
                openai_task,
                return_exceptions=True
            )
            
            # Perplexity should succeed
            assert isinstance(perplexity_result, str)
            assert "Successful research result" in perplexity_result
            
            # OpenAI should fail gracefully
            assert isinstance(openai_result, str)
            assert "Error extracting data:" in openai_result
            assert "API quota exceeded" in openai_result
    
    @pytest.mark.asyncio
    async def test_server_health_coordination(self):
        """Test coordinated health checks across servers."""
        # Setup healthy responses
        perplexity_mock = PerplexityMockFactory.create_client_mock()
        perplexity_mock.health_check.return_value = True
        
        openai_mock = OpenAIMockFactory.create_client_mock()
        openai_mock.health_check.return_value = True
        openai_mock.structured_completion.return_value = OpenAIMockFactory.create_successful_structured_response()
        
        with patch.object(perplexity_server, 'perplexity_client', perplexity_mock), \
             patch.object(openai_server, 'openai_client', openai_mock):
            
            # Run health checks in parallel
            health_checks = await asyncio.gather(
                perplexity_server.health_check(),
                openai_server.health_check()
            )
            
            # Both should be healthy
            assert all("✅" in result for result in health_checks)
            
            # Verify specific server responses
            perplexity_health, openai_health = health_checks
            assert "accessible and working correctly" in perplexity_health
            assert "accessible and structured outputs are working correctly" in openai_health
    
    @pytest.mark.asyncio
    async def test_concurrent_load_distribution(self):
        """Test load distribution across multiple servers."""
        num_requests = 20
        concurrent_limit = 5
        
        # Setup responses
        perplexity_responses = [PerplexityMockFactory.create_successful_response(
            content=f"Response {i}") for i in range(num_requests)]
        
        openai_responses = [OpenAIMockFactory.create_successful_structured_response(
            data={"response_id": i}) for i in range(num_requests)]
        
        with patch.object(perplexity_server, 'perplexity_client',
                         PerplexityMockFactory.create_client_mock(perplexity_responses)), \
             patch.object(openai_server, 'openai_client',
                         OpenAIMockFactory.create_client_mock(openai_responses)):
            
            # Create mixed workload
            async def perplexity_work(i):
                return await perplexity_server.perplexity_search(query=f"query {i}")
            
            async def openai_work(i):
                return await openai_server.extract_data(text=f"text {i}")
            
            # Create tasks alternating between servers
            tasks = []
            for i in range(num_requests):
                if i % 2 == 0:
                    tasks.append(perplexity_work(i))
                else:
                    tasks.append(openai_work(i))
            
            # Run with concurrency limit
            semaphore = asyncio.Semaphore(concurrent_limit)
            
            async def limited_task(task):
                async with semaphore:
                    return await task
            
            start_time = asyncio.get_event_loop().time()
            results = await asyncio.gather(*[limited_task(task) for task in tasks])
            duration = asyncio.get_event_loop().time() - start_time
            
            # Verify all requests completed successfully
            assert len(results) == num_requests
            
            # Check that results are mixed between servers
            perplexity_results = [r for r in results if "Response" in str(r)]
            openai_results = [r for r in results if "response_id" in str(r)]
            
            assert len(perplexity_results) == num_requests // 2
            assert len(openai_results) == num_requests // 2
            
            # Performance should be reasonable
            avg_time_per_request = duration / num_requests
            assert avg_time_per_request < 1.0, f"Average time per request too high: {avg_time_per_request:.3f}s"
    
    @pytest.mark.asyncio
    async def test_server_capability_discovery(self):
        """Test discovery of server capabilities for coordination."""
        with patch.object(perplexity_server, 'perplexity_client', self.perplexity_mock), \
             patch.object(openai_server, 'openai_client', self.openai_mock):
            
            # Get capabilities from both servers
            perplexity_models = await perplexity_server.list_models()
            openai_schemas = await openai_server.list_schemas()
            
            # Verify Perplexity capabilities
            assert "sonar" in perplexity_models
            assert "sonar-pro" in perplexity_models
            assert "Usage Tips:" in perplexity_models
            
            # Verify OpenAI capabilities
            assert "data_extraction" in openai_schemas
            assert "code_analysis" in openai_schemas
            assert "sentiment_analysis" in openai_schemas
            assert "Usage Tips:" in openai_schemas
            
            # Capabilities should be complementary
            # Perplexity: Research and web search
            # OpenAI: Structured data processing
            assert "research" in perplexity_models.lower() or "search" in perplexity_models.lower()
            assert "structured" in openai_schemas.lower() or "extract" in openai_schemas.lower()


class TestClaudeCodeWorkflowIntegration(AsyncTestBase):
    """Test integration with Claude Code workflows."""
    
    def setup_method(self):
        super().setup_method()
        self.sample_data = GenericMockFactory.create_sample_data()
    
    @pytest.mark.asyncio
    async def test_research_to_analysis_workflow(self):
        """Test workflow from research to structured analysis."""
        # Simulate Claude Code workflow:
        # 1. Research topic with Perplexity
        # 2. Structure findings with OpenAI
        # 3. Generate actionable insights
        
        research_response = PerplexityMockFactory.create_successful_response(
            content="Python async programming enables concurrent execution and improved performance in I/O-bound applications.",
            related_questions=["How to implement async patterns?", "What are async best practices?"]
        )
        
        analysis_response = OpenAIMockFactory.create_successful_structured_response(
            data={
                "entities": ["Python", "async programming", "concurrent execution"],
                "key_facts": ["Async improves I/O performance", "Enables concurrent execution"],
                "summary": "Python async programming provides performance benefits for I/O-bound tasks",
                "confidence_score": 0.92
            }
        )
        
        config_response = OpenAIMockFactory.create_successful_structured_response(
            data={
                "task_name": "Implement Async Patterns",
                "priority": "medium",
                "steps": [
                    "Study async/await syntax",
                    "Identify I/O-bound operations", 
                    "Refactor to async patterns",
                    "Test concurrent performance"
                ],
                "prerequisites": ["Python 3.7+", "Understanding of coroutines"],
                "validation_criteria": ["Performance improvement measured", "No blocking operations"]
            },
            schema_name="configuration_task"
        )
        
        with patch.object(perplexity_server, 'perplexity_client',
                         PerplexityMockFactory.create_client_mock([research_response])), \
             patch.object(openai_server, 'openai_client',
                         OpenAIMockFactory.create_client_mock([analysis_response, config_response])):
            
            # Step 1: Research the topic
            research_result = await perplexity_server.perplexity_search(
                query="Python async programming best practices"
            )
            
            # Step 2: Extract structured insights
            analysis_result = await openai_server.extract_data(
                text="Python async programming enables concurrent execution",
                custom_instructions="Focus on technical benefits and use cases"
            )
            
            # Step 3: Generate implementation tasks
            task_result = await openai_server.create_configuration_task(
                description="Create implementation plan for Python async patterns based on research"
            )
            
            # Verify workflow completed successfully
            assert "async programming" in research_result
            
            analysis_data = self.assert_valid_json_response(analysis_result)
            assert "Python" in analysis_data["data"]["entities"]
            
            task_data = self.assert_valid_json_response(task_result)
            assert "Implement Async Patterns" in task_data["data"]["task_name"]
            assert len(task_data["data"]["steps"]) > 0
    
    @pytest.mark.asyncio
    async def test_code_analysis_workflow(self):
        """Test code analysis workflow integration."""
        # Workflow: Analyze code with OpenAI, research improvements with Perplexity
        
        code_analysis_response = OpenAIMockFactory.create_successful_structured_response(
            data={
                "language": "python",
                "complexity_score": 6,
                "issues": ["High cyclomatic complexity", "Missing error handling"],
                "strengths": ["Good variable naming", "Clear function structure"],
                "recommendations": ["Refactor large functions", "Add try-catch blocks"],
                "functions_count": 3,
                "lines_of_code": 45
            },
            schema_name="code_analysis"
        )
        
        research_response = PerplexityMockFactory.create_successful_response(
            content="Python code complexity can be reduced through function decomposition, early returns, and design patterns like Strategy or Command.",
            related_questions=["How to measure code complexity?", "What are refactoring techniques?"]
        )
        
        with patch.object(openai_server, 'openai_client',
                         OpenAIMockFactory.create_client_mock([code_analysis_response])), \
             patch.object(perplexity_server, 'perplexity_client',
                         PerplexityMockFactory.create_client_mock([research_response])):
            
            # Step 1: Analyze the code
            analysis_result = await openai_server.analyze_code(
                code=self.sample_data["sample_code"],
                language_hint="python"
            )
            
            # Step 2: Research improvement strategies
            research_result = await perplexity_server.perplexity_search(
                query="Python code complexity reduction techniques refactoring"
            )
            
            # Verify analysis identified issues
            analysis_data = self.assert_valid_json_response(analysis_result)
            assert analysis_data["data"]["complexity_score"] == 6
            assert "High cyclomatic complexity" in analysis_data["data"]["issues"]
            
            # Verify research provided solutions
            assert "complexity can be reduced" in research_result
            assert "refactoring" in research_result.lower()
    
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self):
        """Test workflow error recovery and fallback strategies."""
        # Test scenario where primary server fails, workflow continues with available servers
        
        # OpenAI fails, but Perplexity succeeds
        openai_error = OpenAIMockFactory.create_error_response(
            error_message="Service temporarily unavailable",
            error_type="service_error"
        )
        
        perplexity_response = PerplexityMockFactory.create_successful_response(
            content="Fallback research result providing alternative insights"
        )
        
        with patch.object(openai_server, 'openai_client',
                         OpenAIMockFactory.create_client_mock([openai_error])), \
             patch.object(perplexity_server, 'perplexity_client',
                         PerplexityMockFactory.create_client_mock([perplexity_response])):
            
            # Attempt structured analysis (will fail)
            analysis_result = await openai_server.extract_data(text="test")
            
            # Fallback to research-based approach
            research_result = await perplexity_server.perplexity_search(
                query="structured data analysis techniques"
            )
            
            # Verify graceful degradation
            assert "Error extracting data:" in analysis_result
            assert "Service temporarily unavailable" in analysis_result
            
            # Verify fallback succeeded
            assert "Fallback research result" in research_result
            
            # Workflow can continue with available information
            assert len(research_result) > 0
