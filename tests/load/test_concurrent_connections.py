"""Load testing for concurrent MCP server connections."""

import pytest
import asyncio
import time
import os
from unittest.mock import patch, AsyncMock
from typing import List, Dict, Any

# Import shared testing utilities
from tests.shared.base_test_classes import AsyncTestBase, PerformanceTestMixin
from tests.shared.performance_utils import PerformanceTester, get_global_tracker
from tests.shared.mock_factories import (
    PerplexityMockFactory, 
    OpenAIMockFactory, 
    GenericMockFactory,
    ErrorScenarioFactory
)

# Setup servers with mock keys
with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key", "OPENAI_API_KEY": "test-key"}):
    from perplexity_mcp import server as perplexity_server
    from openai_structured_mcp import server as openai_server


class TestPerplexityConcurrentLoad(AsyncTestBase, PerformanceTestMixin):
    """Test Perplexity MCP server under concurrent load."""
    
    def setup_method(self):
        super().setup_method()
        self._init_performance_baselines()
        self.performance_tester = PerformanceTester()
        self.sample_data = GenericMockFactory.create_sample_data()
    
    @pytest.mark.asyncio
    async def test_concurrent_search_requests(self):
        """Test concurrent perplexity search requests."""
        concurrent_requests = 20
        total_requests = 100
        
        # Setup mock responses
        responses = [PerplexityMockFactory.create_successful_response(
            content=f"Research result {i}",
            related_questions=[f"Question {i}"]
        ) for i in range(total_requests)]
        
        mock_client = PerplexityMockFactory.create_client_mock(responses)
        
        with patch.object(perplexity_server, 'perplexity_client', mock_client):
            async def single_request(request_id: int):
                return await perplexity_server.perplexity_search(
                    query=f"Test query {request_id}",
                    model="sonar"
                )
            
            # Run load test
            load_results = await self.performance_tester.run_load_test(
                operation_name="perplexity_search",
                async_operation=lambda: single_request(0),
                concurrent_requests=concurrent_requests,
                total_requests=total_requests
            )
            
            # Validate load test results
            assert load_results['successes'] == total_requests
            assert load_results['failures'] == 0
            assert load_results['failure_rate'] == 0.0
            assert load_results['requests_per_sec'] > 10  # Should handle at least 10 req/sec
            
            # Check performance metrics
            search_stats = get_global_tracker().get_statistics('perplexity_search_load')
            if search_stats:
                assert search_stats['mean'] < 500, f"Mean response time too high: {search_stats['mean']:.1f}ms"
                assert search_stats['p95'] < 1000, f"95th percentile too high: {search_stats['p95']:.1f}ms"
    
    @pytest.mark.asyncio
    async def test_concurrent_health_checks(self):
        """Test concurrent health check requests."""
        concurrent_requests = 50
        total_requests = 200
        
        mock_client = PerplexityMockFactory.create_client_mock()
        mock_client.health_check.return_value = True
        
        with patch.object(perplexity_server, 'perplexity_client', mock_client):
            async def health_check_request():
                return await perplexity_server.health_check()
            
            load_results = await self.performance_tester.run_load_test(
                operation_name="health_check",
                async_operation=health_check_request,
                concurrent_requests=concurrent_requests,
                total_requests=total_requests
            )
            
            # Health checks should handle high concurrency well
            assert load_results['successes'] == total_requests
            assert load_results['failure_rate'] == 0.0
            assert load_results['requests_per_sec'] > 50  # Health checks should be very fast
    
    @pytest.mark.asyncio
    async def test_mixed_operation_load(self):
        """Test mixed operations under concurrent load."""
        concurrent_requests = 15
        
        # Setup different mock responses for different operations
        search_responses = [PerplexityMockFactory.create_successful_response(
            content=f"Search result {i}"
        ) for i in range(50)]
        
        deep_research_responses = [PerplexityMockFactory.create_successful_response(
            content=f"Deep research {i}",
            citations=[f"Source {i}"]
        ) for i in range(30)]
        
        quick_query_responses = [PerplexityMockFactory.create_successful_response(
            content=f"Quick answer {i}"
        ) for i in range(20)]
        
        # Create different mock clients for different methods
        search_mock = PerplexityMockFactory.create_client_mock(search_responses)
        deep_mock = PerplexityMockFactory.create_client_mock(deep_research_responses)
        quick_mock = PerplexityMockFactory.create_client_mock(quick_query_responses)
        
        async def mixed_operations():
            # Randomly choose operation type
            import random
            operation_type = random.choice(['search', 'deep', 'quick'])
            
            if operation_type == 'search':
                with patch.object(perplexity_server, 'perplexity_client', search_mock):
                    return await perplexity_server.perplexity_search(query="test")
            elif operation_type == 'deep':
                with patch.object(perplexity_server, 'perplexity_client', deep_mock):
                    return await perplexity_server.perplexity_deep_research(
                        topic="test topic",
                        focus_areas=["area1"]
                    )
            else:
                with patch.object(perplexity_server, 'perplexity_client', quick_mock):
                    return await perplexity_server.perplexity_quick_query(question="test?")
        
        # Run mixed load test
        semaphore = asyncio.Semaphore(concurrent_requests)
        
        async def limited_operation():
            async with semaphore:
                return await mixed_operations()
        
        start_time = time.time()
        tasks = [limited_operation() for _ in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start_time
        
        # Validate mixed load results
        successes = [r for r in results if not isinstance(r, Exception)]
        failures = [r for r in results if isinstance(r, Exception)]
        
        assert len(successes) >= 90  # Allow some failures under mixed load
        assert len(failures) <= 10
        assert duration < 30  # Should complete within reasonable time
    
    @pytest.mark.asyncio
    async def test_error_recovery_under_load(self):
        """Test error recovery patterns under concurrent load."""
        concurrent_requests = 10
        total_requests = 50
        
        # Create mixed success/failure responses
        responses = []
        for i in range(total_requests):
            if i % 5 == 0:  # 20% failure rate
                responses.append(PerplexityMockFactory.create_error_response(
                    error_message=f"Temporary error {i}",
                    error_type="temporary"
                ))
            else:
                responses.append(PerplexityMockFactory.create_successful_response(
                    content=f"Success {i}"
                ))
        
        mock_client = PerplexityMockFactory.create_client_mock(responses)
        
        with patch.object(perplexity_server, 'perplexity_client', mock_client):
            async def error_prone_request():
                return await perplexity_server.perplexity_search(query="test")
            
            load_results = await self.performance_tester.run_load_test(
                operation_name="error_recovery",
                async_operation=error_prone_request,
                concurrent_requests=concurrent_requests,
                total_requests=total_requests
            )
            
            # All requests should complete (errors handled gracefully)
            assert load_results['successes'] + load_results['failures'] == total_requests
            
            # Should handle errors gracefully without crashing
            assert load_results['failure_rate'] < 1.0  # Not all should fail
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self):
        """Test memory usage during sustained load."""
        test_duration = 10  # seconds
        
        mock_response = PerplexityMockFactory.create_successful_response(
            content="Test response for memory testing"
        )
        mock_client = PerplexityMockFactory.create_client_mock([mock_response])
        
        with patch.object(perplexity_server, 'perplexity_client', mock_client):
            async def memory_test_operation():
                return await perplexity_server.perplexity_search(query="memory test")
            
            # Run stress test
            stress_results = await self.performance_tester.stress_test_memory(
                operation_name="perplexity_search",
                async_operation=memory_test_operation,
                duration_seconds=test_duration
            )
            
            # Validate memory usage
            assert stress_results['total_requests'] > 0
            assert stress_results['requests_per_second'] > 1
            
            # Memory growth should be reasonable
            memory_growth_mb = stress_results['memory_growth_mb']
            memory_per_request_kb = stress_results['memory_growth_per_request_kb']
            
            assert memory_growth_mb < 100, f"Memory growth too high: {memory_growth_mb:.1f}MB"
            assert memory_per_request_kb < 10, f"Memory per request too high: {memory_per_request_kb:.1f}KB"


class TestOpenAIConcurrentLoad(AsyncTestBase, PerformanceTestMixin):
    """Test OpenAI Structured MCP server under concurrent load."""
    
    def setup_method(self):
        super().setup_method()
        self._init_performance_baselines()
        self.performance_tester = PerformanceTester()
        self.sample_data = GenericMockFactory.create_sample_data()
    
    @pytest.mark.asyncio
    async def test_concurrent_data_extraction(self):
        """Test concurrent data extraction requests."""
        concurrent_requests = 15
        total_requests = 75
        
        # Setup mock responses
        responses = [OpenAIMockFactory.create_successful_structured_response(
            data={"extraction_id": i, "entities": [f"Entity{i}"]}
        ) for i in range(total_requests)]
        
        mock_client = OpenAIMockFactory.create_client_mock(responses)
        
        with patch.object(openai_server, 'openai_client', mock_client):
            async def single_extraction(request_id: int):
                return await openai_server.extract_data(
                    text=f"Sample text {request_id}",
                    custom_instructions="Extract key information"
                )
            
            load_results = await self.performance_tester.run_load_test(
                operation_name="data_extraction",
                async_operation=lambda: single_extraction(0),
                concurrent_requests=concurrent_requests,
                total_requests=total_requests
            )
            
            # Validate load test results
            assert load_results['successes'] == total_requests
            assert load_results['failures'] == 0
            assert load_results['requests_per_sec'] > 5  # Should handle reasonable throughput
    
    @pytest.mark.asyncio
    async def test_concurrent_code_analysis(self):
        """Test concurrent code analysis requests."""
        concurrent_requests = 10
        total_requests = 50
        
        responses = [OpenAIMockFactory.create_successful_structured_response(
            data={
                "analysis_id": i,
                "language": "python",
                "complexity_score": i % 10,
                "issues": [f"Issue {i}"]
            },
            schema_name="code_analysis"
        ) for i in range(total_requests)]
        
        mock_client = OpenAIMockFactory.create_client_mock(responses)
        
        with patch.object(openai_server, 'openai_client', mock_client):
            async def single_analysis():
                return await openai_server.analyze_code(
                    code=self.sample_data["sample_code"],
                    language_hint="python"
                )
            
            load_results = await self.performance_tester.run_load_test(
                operation_name="code_analysis",
                async_operation=single_analysis,
                concurrent_requests=concurrent_requests,
                total_requests=total_requests
            )
            
            # Code analysis should handle concurrent requests well
            assert load_results['successes'] == total_requests
            assert load_results['failure_rate'] == 0.0
    
    @pytest.mark.asyncio
    async def test_mixed_structured_operations_load(self):
        """Test mixed structured operations under load."""
        concurrent_requests = 12
        
        # Setup responses for different operations
        extraction_response = OpenAIMockFactory.create_successful_structured_response(
            data={"entities": ["Test"], "summary": "Test extraction"}
        )
        
        analysis_response = OpenAIMockFactory.create_successful_structured_response(
            data={"language": "python", "complexity_score": 3},
            schema_name="code_analysis"
        )
        
        sentiment_response = OpenAIMockFactory.create_successful_structured_response(
            data={"overall_sentiment": "positive", "confidence": 0.8},
            schema_name="sentiment_analysis"
        )
        
        task_response = OpenAIMockFactory.create_successful_structured_response(
            data={"task_name": "Test Task", "priority": "medium"},
            schema_name="configuration_task"
        )
        
        async def mixed_structured_operations():
            import random
            operation = random.choice(['extract', 'analyze', 'sentiment', 'task'])
            
            if operation == 'extract':
                mock_client = OpenAIMockFactory.create_client_mock([extraction_response])
                with patch.object(openai_server, 'openai_client', mock_client):
                    return await openai_server.extract_data(text="test")
            
            elif operation == 'analyze':
                mock_client = OpenAIMockFactory.create_client_mock([analysis_response])
                with patch.object(openai_server, 'openai_client', mock_client):
                    return await openai_server.analyze_code(code="def test(): pass")
            
            elif operation == 'sentiment':
                mock_client = OpenAIMockFactory.create_client_mock([sentiment_response])
                with patch.object(openai_server, 'openai_client', mock_client):
                    return await openai_server.analyze_sentiment(text="Great work!")
            
            else:
                mock_client = OpenAIMockFactory.create_client_mock([task_response])
                with patch.object(openai_server, 'openai_client', mock_client):
                    return await openai_server.create_configuration_task(description="test task")
        
        # Run mixed operations
        semaphore = asyncio.Semaphore(concurrent_requests)
        
        async def limited_operation():
            async with semaphore:
                return await mixed_structured_operations()
        
        start_time = time.time()
        tasks = [limited_operation() for _ in range(80)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start_time
        
        # Validate mixed operations
        successes = [r for r in results if not isinstance(r, Exception)]
        assert len(successes) >= 75  # Most should succeed
        assert duration < 20  # Should complete in reasonable time
    
    @pytest.mark.asyncio
    async def test_json_parsing_under_load(self):
        """Test JSON parsing performance under concurrent load."""
        concurrent_requests = 20
        total_requests = 100
        
        # Create large structured responses to test JSON parsing
        large_response = OpenAIMockFactory.create_successful_structured_response(
            data={
                "entities": [f"Entity{i}" for i in range(50)],
                "key_facts": [f"Fact {i}" for i in range(20)],
                "detailed_analysis": {
                    "sections": [f"Section {i}" for i in range(10)],
                    "metrics": {f"metric{i}": i * 0.1 for i in range(30)}
                }
            }
        )
        
        mock_client = OpenAIMockFactory.create_client_mock([large_response] * total_requests)
        
        with patch.object(openai_server, 'openai_client', mock_client):
            async def json_intensive_operation():
                result = await openai_server.extract_data(
                    text="Large text for complex extraction",
                    custom_instructions="Perform detailed analysis"
                )
                # Parse the JSON to ensure it's valid
                import json
                parsed = json.loads(result)
                return parsed
            
            load_results = await self.performance_tester.run_load_test(
                operation_name="json_parsing",
                async_operation=json_intensive_operation,
                concurrent_requests=concurrent_requests,
                total_requests=total_requests
            )
            
            # JSON parsing should handle concurrent load
            assert load_results['successes'] == total_requests
            assert load_results['failures'] == 0
            
            # Performance should remain reasonable even with large JSON
            json_stats = get_global_tracker().get_statistics('json_parsing_load')
            if json_stats:
                assert json_stats['p95'] < 2000, f"JSON parsing too slow: {json_stats['p95']:.1f}ms"


class TestCrossServerLoadBalancing(AsyncTestBase):
    """Test load balancing across multiple MCP servers."""
    
    @pytest.mark.asyncio
    async def test_distributed_load_handling(self):
        """Test distributing load across both MCP servers."""
        total_requests = 100
        concurrent_limit = 20
        
        # Setup responses for both servers
        perplexity_responses = [PerplexityMockFactory.create_successful_response(
            content=f"Perplexity result {i}"
        ) for i in range(50)]
        
        openai_responses = [OpenAIMockFactory.create_successful_structured_response(
            data={"result_id": i, "server": "openai"}
        ) for i in range(50)]
        
        perplexity_mock = PerplexityMockFactory.create_client_mock(perplexity_responses)
        openai_mock = OpenAIMockFactory.create_client_mock(openai_responses)
        
        async def balanced_request(request_id: int):
            # Distribute requests between servers
            if request_id % 2 == 0:
                with patch.object(perplexity_server, 'perplexity_client', perplexity_mock):
                    return await perplexity_server.perplexity_search(query=f"query {request_id}")
            else:
                with patch.object(openai_server, 'openai_client', openai_mock):
                    return await openai_server.extract_data(text=f"text {request_id}")
        
        # Run distributed load test
        semaphore = asyncio.Semaphore(concurrent_limit)
        
        async def limited_request(request_id: int):
            async with semaphore:
                return await balanced_request(request_id)
        
        start_time = time.time()
        tasks = [limited_request(i) for i in range(total_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start_time
        
        # Validate distributed load handling
        successes = [r for r in results if not isinstance(r, Exception)]
        assert len(successes) == total_requests
        
        # Check that load was distributed
        perplexity_results = [r for r in successes if "Perplexity result" in str(r)]
        openai_results = [r for r in successes if "result_id" in str(r)]
        
        assert len(perplexity_results) == 50
        assert len(openai_results) == 50
        
        # Performance should benefit from distribution
        avg_time_per_request = duration / total_requests
        assert avg_time_per_request < 0.5, f"Distributed requests too slow: {avg_time_per_request:.3f}s"
