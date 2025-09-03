"""Resource exhaustion and recovery testing for MCP servers."""

import pytest
import asyncio
import time
import os
from unittest.mock import patch, AsyncMock
from typing import List, Dict, Any

# Import shared testing utilities
from tests.shared.base_test_classes import AsyncTestBase, ErrorSimulationMixin
from tests.shared.performance_utils import PerformanceTester
from tests.shared.mock_factories import (
    PerplexityMockFactory, 
    OpenAIMockFactory, 
    ErrorScenarioFactory
)

# Setup servers with mock keys
with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "sk-test-fake-perplexity-key-do-not-use", "OPENAI_API_KEY": "sk-test-fake-openai-key-do-not-use"}):
    from perplexity_mcp import server as perplexity_server
    from openai_structured_mcp import server as openai_server


class TestResourceExhaustionScenarios(AsyncTestBase, ErrorSimulationMixin):
    """Test MCP server behavior under resource exhaustion."""
    
    def setup_method(self):
        super().setup_method()
        self.performance_tester = PerformanceTester()
    
    @pytest.mark.asyncio
    async def test_memory_pressure_handling(self):
        """Test server behavior under memory pressure."""
        # Simulate memory pressure by creating large response objects
        large_content = "Large response content. " * 1000  # ~25KB per response
        
        large_responses = [PerplexityMockFactory.create_successful_response(
            content=large_content,
            related_questions=[f"Question {i}" for i in range(10)],
            citations=[f"Citation {i}" for i in range(5)]
        ) for _ in range(100)]
        
        mock_client = PerplexityMockFactory.create_client_mock(large_responses)
        
        with patch.object(perplexity_server, 'perplexity_client', mock_client):
            # Run many requests with large responses
            async def memory_intensive_request():
                result = await perplexity_server.perplexity_search(
                    query="Large response test"
                )
                # Ensure response is processed
                assert len(result) > 1000
                return result
            
            # Monitor memory during sustained load
            stress_results = await self.performance_tester.stress_test_memory(
                operation_name="memory_pressure",
                async_operation=memory_intensive_request,
                duration_seconds=15
            )
            
            # Server should handle memory pressure gracefully
            assert stress_results['total_requests'] > 10
            assert stress_results['memory_growth_mb'] < 500  # Should not grow excessively
            assert stress_results['requests_per_second'] > 1  # Should continue processing
    
    @pytest.mark.asyncio
    async def test_connection_pool_exhaustion(self):
        """Test behavior when connection pools are exhausted."""
        concurrent_connections = 100  # High concurrency to stress connection handling
        
        # Setup responses that simulate slow network
        slow_responses = [PerplexityMockFactory.create_successful_response(
            content=f"Slow response {i}"
        ) for i in range(concurrent_connections)]
        
        mock_client = PerplexityMockFactory.create_client_mock(slow_responses)
        
        # Add artificial delay to simulate slow responses
        original_query = mock_client.query
        async def slow_query(*args, **kwargs):
            await asyncio.sleep(0.1)  # 100ms delay per request
            return await original_query(*args, **kwargs)
        mock_client.query = slow_query
        
        with patch.object(perplexity_server, 'perplexity_client', mock_client):
            # Create many concurrent requests
            async def connection_request(request_id: int):
                return await perplexity_server.perplexity_search(
                    query=f"Connection test {request_id}"
                )
            
            start_time = time.time()
            tasks = [connection_request(i) for i in range(concurrent_connections)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            duration = time.time() - start_time
            
            # Analyze connection handling
            successes = [r for r in results if not isinstance(r, Exception)]
            failures = [r for r in results if isinstance(r, Exception)]
            
            # Should handle high concurrency reasonably
            success_rate = len(successes) / len(results)
            assert success_rate > 0.8, f"Success rate too low: {success_rate:.2f}"
            
            # Should complete within reasonable time despite high concurrency
            assert duration < 30, f"Connection handling too slow: {duration:.1f}s"
    
    @pytest.mark.asyncio
    async def test_rate_limit_recovery(self):
        """Test recovery from rate limit scenarios."""
        # Simulate rate limiting by mixing successful and rate-limited responses
        responses = []
        for i in range(50):
            if i % 3 == 0:  # Every 3rd request hits rate limit
                responses.append(PerplexityMockFactory.create_error_response(
                    error_message="Rate limit exceeded",
                    error_type="rate_limit"
                ))
            else:
                responses.append(PerplexityMockFactory.create_successful_response(
                    content=f"Success after rate limit {i}"
                ))
        
        mock_client = PerplexityMockFactory.create_client_mock(responses)
        
        with patch.object(perplexity_server, 'perplexity_client', mock_client):
            # Run requests that will hit rate limits
            async def rate_limited_request(request_id: int):
                return await perplexity_server.perplexity_search(
                    query=f"Rate limit test {request_id}"
                )
            
            # Execute requests with limited concurrency (to avoid overwhelming)
            semaphore = asyncio.Semaphore(5)
            
            async def limited_request(request_id: int):
                async with semaphore:
                    return await rate_limited_request(request_id)
            
            start_time = time.time()
            tasks = [limited_request(i) for i in range(50)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            duration = time.time() - start_time
            
            # Analyze rate limit handling
            successes = [r for r in results if not isinstance(r, Exception) and "Success after" in str(r)]
            rate_limits = [r for r in results if "Rate limit" in str(r)]
            
            # Should handle rate limits gracefully
            assert len(successes) > 30  # Most non-rate-limited should succeed
            assert len(rate_limits) > 10  # Rate limits should be handled as errors
            
            # Should continue processing after rate limits
            assert duration < 20, "Rate limit recovery too slow"
    
    @pytest.mark.asyncio
    async def test_cascading_failure_recovery(self):
        """Test recovery from cascading failure scenarios."""
        # Simulate cascading failures: start with success, then failures, then recovery
        phases = {
            'success': 10,   # First 10 requests succeed
            'failure': 20,   # Next 20 requests fail
            'recovery': 15   # Final 15 requests succeed again
        }
        
        responses = []
        request_count = 0
        
        # Success phase
        for i in range(phases['success']):
            responses.append(PerplexityMockFactory.create_successful_response(
                content=f"Initial success {i}"
            ))
        request_count += phases['success']
        
        # Failure phase
        for i in range(phases['failure']):
            responses.append(PerplexityMockFactory.create_error_response(
                error_message=f"System overload {request_count + i}",
                error_type="system_error"
            ))
        request_count += phases['failure']
        
        # Recovery phase
        for i in range(phases['recovery']):
            responses.append(PerplexityMockFactory.create_successful_response(
                content=f"Recovery success {i}"
            ))
        
        mock_client = PerplexityMockFactory.create_client_mock(responses)
        
        with patch.object(perplexity_server, 'perplexity_client', mock_client):
            # Run requests through all phases
            async def cascading_request(request_id: int):
                return await perplexity_server.perplexity_search(
                    query=f"Cascading test {request_id}"
                )
            
            # Execute requests sequentially to maintain phase order
            results = []
            for i in range(sum(phases.values())):
                result = await cascading_request(i)
                results.append(result)
                await asyncio.sleep(0.01)  # Small delay between requests
            
            # Analyze cascading failure pattern
            success_results = [r for r in results if "success" in str(r).lower()]
            error_results = [r for r in results if "system overload" in str(r).lower()]
            
            # Should handle the complete failure cycle
            assert len(success_results) >= phases['success'] + phases['recovery'] - 5  # Allow some variance
            assert len(error_results) >= phases['failure'] - 5  # Should capture most failures
    
    @pytest.mark.asyncio
    async def test_timeout_handling_under_load(self):
        """Test timeout handling when servers are slow under load."""
        # Create responses that simulate very slow operations
        timeout_responses = [PerplexityMockFactory.create_successful_response(
            content=f"Slow response {i}"
        ) for i in range(30)]
        
        mock_client = PerplexityMockFactory.create_client_mock(timeout_responses)
        
        # Simulate extremely slow responses
        original_query = mock_client.query
        async def very_slow_query(*args, **kwargs):
            await asyncio.sleep(2.0)  # 2 second delay
            return await original_query(*args, **kwargs)
        mock_client.query = very_slow_query
        
        with patch.object(perplexity_server, 'perplexity_client', mock_client):
            # Run requests with timeout pressure
            async def timeout_prone_request():
                try:
                    # Use asyncio.wait_for to simulate timeout handling
                    return await asyncio.wait_for(
                        perplexity_server.perplexity_search(query="Timeout test"),
                        timeout=1.0  # 1 second timeout
                    )
                except asyncio.TimeoutError:
                    return "Request timed out"
            
            # Run concurrent timeout-prone requests
            concurrent_requests = 10
            tasks = [timeout_prone_request() for _ in range(concurrent_requests)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Analyze timeout handling
            timeouts = [r for r in results if "timed out" in str(r)]
            successes = [r for r in results if "Slow response" in str(r)]
            exceptions = [r for r in results if isinstance(r, Exception)]
            
            # Should handle timeouts gracefully
            total_handled = len(timeouts) + len(successes)
            assert total_handled >= concurrent_requests - 2  # Allow some variance
            
            # Should not have unhandled exceptions
            assert len(exceptions) <= 2, f"Too many unhandled exceptions: {len(exceptions)}"


class TestOpenAIResourceExhaustion(AsyncTestBase, ErrorSimulationMixin):
    """Test OpenAI structured MCP server resource exhaustion scenarios."""
    
    @pytest.mark.asyncio
    async def test_large_json_processing_stress(self):
        """Test processing of very large JSON responses under load."""
        # Create very large structured responses
        large_data = {
            "entities": [f"Entity{i}" for i in range(500)],  # Large entity list
            "key_facts": [f"Fact {i}: This is a detailed fact with substantial content." for i in range(100)],
            "detailed_analysis": {
                "sections": {
                    f"section_{i}": {
                        "content": f"Detailed content for section {i}. " * 50,
                        "metrics": {f"metric_{j}": j * 0.1 for j in range(20)}
                    } for i in range(20)
                }
            },
            "confidence_score": 0.95
        }
        
        large_response = OpenAIMockFactory.create_successful_structured_response(
            data=large_data,
            processing_time_ms=500.0
        )
        
        mock_client = OpenAIMockFactory.create_client_mock([large_response] * 50)
        
        with patch.object(openai_server, 'openai_client', mock_client):
            # Process large JSON responses concurrently
            async def large_json_request():
                result = await openai_server.extract_data(
                    text="Large data extraction test"
                )
                # Parse JSON to ensure it's processed correctly
                import json
                parsed = json.loads(result)
                assert len(parsed["data"]["entities"]) == 500
                return parsed
            
            # Run concurrent large JSON processing
            concurrent_requests = 10
            tasks = [large_json_request() for _ in range(concurrent_requests)]
            
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            duration = time.time() - start_time
            
            # Validate large JSON handling
            successes = [r for r in results if not isinstance(r, Exception)]
            assert len(successes) >= concurrent_requests - 1  # Allow minimal failures
            
            # Performance should remain reasonable even with large JSON
            avg_time = duration / concurrent_requests
            assert avg_time < 2.0, f"Large JSON processing too slow: {avg_time:.2f}s"
    
    @pytest.mark.asyncio
    async def test_schema_validation_under_stress(self):
        """Test schema validation performance under concurrent load."""
        # Create responses for different schemas
        schemas = ["data_extraction", "code_analysis", "sentiment_analysis", "configuration_task"]
        
        responses = []
        for i in range(80):
            schema = schemas[i % len(schemas)]
            response = OpenAIMockFactory.create_successful_structured_response(
                data={f"test_field_{j}": f"value_{j}" for j in range(10)},
                schema_name=schema
            )
            responses.append(response)
        
        mock_client = OpenAIMockFactory.create_client_mock(responses)
        
        with patch.object(openai_server, 'openai_client', mock_client):
            # Run mixed schema operations
            async def schema_validation_request(request_id: int):
                schema = schemas[request_id % len(schemas)]
                
                if schema == "data_extraction":
                    return await openai_server.extract_data(text=f"Test {request_id}")
                elif schema == "code_analysis":
                    return await openai_server.analyze_code(code=f"# Code {request_id}")
                elif schema == "sentiment_analysis":
                    return await openai_server.analyze_sentiment(text=f"Sentiment {request_id}")
                else:
                    return await openai_server.create_configuration_task(description=f"Task {request_id}")
            
            # Run concurrent schema validation stress test
            concurrent_requests = 20
            total_requests = 80
            
            semaphore = asyncio.Semaphore(concurrent_requests)
            
            async def limited_schema_request(request_id: int):
                async with semaphore:
                    return await schema_validation_request(request_id)
            
            start_time = time.time()
            tasks = [limited_schema_request(i) for i in range(total_requests)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            duration = time.time() - start_time
            
            # Validate schema handling under stress
            successes = [r for r in results if not isinstance(r, Exception)]
            assert len(successes) >= total_requests - 5  # Allow minimal failures
            
            # Verify different schemas were processed
            parsed_results = []
            for result in successes[:10]:  # Check first 10 successful results
                if not isinstance(result, str):
                    continue
                try:
                    import json
                    parsed = json.loads(result)
                    parsed_results.append(parsed)
                except json.JSONDecodeError:
                    pass
            
            assert len(parsed_results) > 0, "Should have valid JSON responses"
            
            # Performance should remain good under schema validation stress
            avg_time_per_request = duration / total_requests
            assert avg_time_per_request < 0.5, f"Schema validation too slow: {avg_time_per_request:.3f}s"
    
    @pytest.mark.asyncio
    async def test_error_propagation_under_load(self):
        """Test error propagation doesn't cause cascading failures under load."""
        # Mix successful and error responses
        responses = []
        for i in range(60):
            if i % 4 == 0:  # 25% error rate
                responses.append(OpenAIMockFactory.create_error_response(
                    error_message=f"Processing error {i}",
                    error_type="processing_error"
                ))
            else:
                responses.append(OpenAIMockFactory.create_successful_structured_response(
                    data={"request_id": i, "status": "success"}
                ))
        
        mock_client = OpenAIMockFactory.create_client_mock(responses)
        
        with patch.object(openai_server, 'openai_client', mock_client):
            # Run requests with mixed success/failure
            async def error_prone_request(request_id: int):
                return await openai_server.extract_data(
                    text=f"Error test {request_id}"
                )
            
            # Execute with high concurrency to test error isolation
            concurrent_requests = 15
            total_requests = 60
            
            semaphore = asyncio.Semaphore(concurrent_requests)
            
            async def limited_error_request(request_id: int):
                async with semaphore:
                    return await error_prone_request(request_id)
            
            start_time = time.time()
            tasks = [limited_error_request(i) for i in range(total_requests)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            duration = time.time() - start_time
            
            # Analyze error isolation
            successes = [r for r in results if not isinstance(r, Exception) and "success" in str(r)]
            handled_errors = [r for r in results if "Error extracting data:" in str(r)]
            exceptions = [r for r in results if isinstance(r, Exception)]
            
            # Errors should be handled gracefully without causing exceptions
            assert len(exceptions) <= 2, f"Too many unhandled exceptions: {len(exceptions)}"
            
            # Should have appropriate ratio of successes to handled errors
            expected_successes = int(total_requests * 0.75)  # 75% should succeed
            assert len(successes) >= expected_successes - 5, f"Not enough successes: {len(successes)}"
            
            # Error handling shouldn't significantly impact performance
            avg_time = duration / total_requests
            assert avg_time < 0.3, f"Error handling impacts performance: {avg_time:.3f}s"
