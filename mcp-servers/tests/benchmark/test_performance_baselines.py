"""Performance baseline tests for MCP servers."""

import pytest
import asyncio
import os
import time
from unittest.mock import patch
from pathlib import Path

# Import shared testing utilities
from tests.shared.base_test_classes import AsyncTestBase, PerformanceTestMixin
from tests.shared.performance_utils import PerformanceTracker, PerformanceTester, get_global_tracker
from tests.shared.mock_factories import PerplexityMockFactory, OpenAIMockFactory


class TestPerplexityPerformanceBaselines(AsyncTestBase, PerformanceTestMixin):
    """Performance baseline tests for Perplexity MCP server."""
    
    def setup_method(self):
        super().setup_method()
        self._init_performance_baselines()
        self._test_performance_tracking = True
        
        # Setup Perplexity server import with mock API key
        self.mock_env = patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"})
        self.mock_env.start()
        
        from perplexity_mcp import server as perplexity_server
        self.perplexity_server = perplexity_server
    
    def teardown_method(self):
        super().teardown_method()
        self.mock_env.stop()
    
    @pytest.mark.asyncio
    async def test_health_check_baseline(self):
        """Test health check meets performance baseline."""
        mock_client = PerplexityMockFactory.create_client_mock()
        
        with patch.object(self.perplexity_server, 'perplexity_client', mock_client):
            # Time the health check operation
            tracker = get_global_tracker()
            start_time = time.perf_counter()
            
            result = await self.perplexity_server.health_check()
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            tracker.record('health_check', duration_ms, {'server': 'perplexity'})
            
            # Assert baseline compliance
            self.assert_performance_baseline('health_check', duration_ms)
            assert "✅" in result
    
    @pytest.mark.asyncio
    async def test_simple_query_baseline(self):
        """Test simple query meets performance baseline."""
        mock_response = PerplexityMockFactory.create_successful_response(
            content="Simple test response",
            related_questions=["What is this?"]
        )
        mock_client = PerplexityMockFactory.create_client_mock([mock_response])
        
        with patch.object(self.perplexity_server, 'perplexity_client', mock_client):
            tracker = get_global_tracker()
            start_time = time.perf_counter()
            
            result = await self.perplexity_server.perplexity_search(query="Simple test query")
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            tracker.record('simple_query', duration_ms, {'server': 'perplexity', 'query_type': 'basic'})
            
            # Assert baseline compliance
            self.assert_performance_baseline('simple_query', duration_ms)
            assert "Simple test response" in result
    
    @pytest.mark.asyncio
    async def test_complex_query_baseline(self):
        """Test complex query meets performance baseline."""
        mock_response = PerplexityMockFactory.create_successful_response(
            content="Complex research response with detailed analysis",
            related_questions=["Question 1", "Question 2", "Question 3"],
            citations=["Source 1", "Source 2"]
        )
        mock_client = PerplexityMockFactory.create_client_mock([mock_response])
        
        with patch.object(self.perplexity_server, 'perplexity_client', mock_client):
            tracker = get_global_tracker()
            start_time = time.perf_counter()
            
            result = await self.perplexity_server.perplexity_deep_research(
                topic="Complex AI research topic",
                focus_areas=["machine learning", "neural networks", "deep learning"],
                max_tokens=2000
            )
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            tracker.record('complex_query', duration_ms, {'server': 'perplexity', 'query_type': 'deep_research'})
            
            # Assert baseline compliance
            self.assert_performance_baseline('complex_query', duration_ms)
            assert "Complex research response" in result
    
    @pytest.mark.asyncio
    async def test_list_models_baseline(self):
        """Test list models meets performance baseline."""
        tracker = get_global_tracker()
        start_time = time.perf_counter()
        
        result = await self.perplexity_server.list_models()
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        tracker.record('simple_query', duration_ms, {'server': 'perplexity', 'operation': 'list_models'})
        
        # List models should be very fast (local operation)
        assert duration_ms < 50, f"List models too slow: {duration_ms:.2f}ms"
        assert "sonar" in result
        assert "Usage Tips:" in result


class TestOpenAIPerformanceBaselines(AsyncTestBase, PerformanceTestMixin):
    """Performance baseline tests for OpenAI Structured MCP server."""
    
    def setup_method(self):
        super().setup_method()
        self._init_performance_baselines()
        self._test_performance_tracking = True
        
        # Setup OpenAI server import with mock API key
        self.mock_env = patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
        self.mock_env.start()
        
        from openai_structured_mcp import server as openai_server
        self.openai_server = openai_server
    
    def teardown_method(self):
        super().teardown_method()
        self.mock_env.stop()
    
    @pytest.mark.asyncio
    async def test_health_check_baseline(self):
        """Test health check meets performance baseline."""
        mock_client = OpenAIMockFactory.create_client_mock()
        
        with patch.object(self.openai_server, 'openai_client', mock_client):
            tracker = get_global_tracker()
            start_time = time.perf_counter()
            
            result = await self.openai_server.health_check()
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            tracker.record('health_check', duration_ms, {'server': 'openai_structured'})
            
            # Assert baseline compliance
            self.assert_performance_baseline('health_check', duration_ms)
            assert "✅" in result
    
    @pytest.mark.asyncio
    async def test_data_extraction_baseline(self):
        """Test data extraction meets performance baseline."""
        mock_response = OpenAIMockFactory.create_successful_structured_response(
            data={
                "entities": ["OpenAI", "GPT-4", "JSON Schema"],
                "key_facts": ["Structured output capability"],
                "summary": "Test extraction summary",
                "confidence_score": 0.92
            },
            processing_time_ms=120.0
        )
        mock_client = OpenAIMockFactory.create_client_mock([mock_response])
        
        with patch.object(self.openai_server, 'openai_client', mock_client):
            tracker = get_global_tracker()
            start_time = time.perf_counter()
            
            result = await self.openai_server.extract_data(
                text="Sample text for data extraction testing",
                custom_instructions="Extract key entities and facts"
            )
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            tracker.record('structured_extraction', duration_ms, {
                'server': 'openai_structured',
                'operation': 'extract_data'
            })
            
            # Assert baseline compliance
            self.assert_performance_baseline('structured_extraction', duration_ms)
            parsed_result = self.assert_valid_json_response(result)
            assert parsed_result["success"] is True
    
    @pytest.mark.asyncio
    async def test_code_analysis_baseline(self):
        """Test code analysis meets performance baseline."""
        mock_response = OpenAIMockFactory.create_successful_structured_response(
            data={
                "language": "python",
                "complexity_score": 3,
                "issues": ["Minor style issue"],
                "strengths": ["Clear naming"],
                "functions_count": 1
            },
            schema_name="code_analysis",
            processing_time_ms=180.0
        )
        mock_client = OpenAIMockFactory.create_client_mock([mock_response])
        
        sample_code = '''
def hello_world():
    print("Hello, World!")
    return True
'''
        
        with patch.object(self.openai_server, 'openai_client', mock_client):
            tracker = get_global_tracker()
            start_time = time.perf_counter()
            
            result = await self.openai_server.analyze_code(
                code=sample_code,
                language_hint="python"
            )
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            tracker.record('code_analysis', duration_ms, {
                'server': 'openai_structured',
                'operation': 'analyze_code',
                'code_length': len(sample_code)
            })
            
            # Assert baseline compliance
            self.assert_performance_baseline('code_analysis', duration_ms)
            parsed_result = self.assert_valid_json_response(result)
            assert parsed_result["data"]["language"] == "python"
    
    @pytest.mark.asyncio
    async def test_list_schemas_baseline(self):
        """Test list schemas meets performance baseline."""
        mock_client = OpenAIMockFactory.create_client_mock()
        
        with patch.object(self.openai_server, 'openai_client', mock_client):
            tracker = get_global_tracker()
            start_time = time.perf_counter()
            
            result = await self.openai_server.list_schemas()
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            tracker.record('simple_query', duration_ms, {
                'server': 'openai_structured',
                'operation': 'list_schemas'
            })
            
            # List schemas should be very fast (local operation)
            assert duration_ms < 50, f"List schemas too slow: {duration_ms:.2f}ms"
            assert "data_extraction" in result
            assert "code_analysis" in result


class TestCrossServerPerformanceComparison(AsyncTestBase):
    """Compare performance across different MCP servers."""
    
    def setup_method(self):
        super().setup_method()
        
        # Setup both servers
        self.perplexity_env = patch.dict(os.environ, {"PERPLEXITY_API_KEY": "test-key"})
        self.openai_env = patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
        
        self.perplexity_env.start()
        self.openai_env.start()
        
        from perplexity_mcp import server as perplexity_server
        from openai_structured_mcp import server as openai_server
        
        self.perplexity_server = perplexity_server
        self.openai_server = openai_server
    
    def teardown_method(self):
        super().teardown_method()
        self.perplexity_env.stop()
        self.openai_env.stop()
    
    @pytest.mark.asyncio
    async def test_health_check_performance_comparison(self):
        """Compare health check performance across servers."""
        tracker = get_global_tracker()
        
        # Test Perplexity health check
        perplexity_mock = PerplexityMockFactory.create_client_mock()
        with patch.object(self.perplexity_server, 'perplexity_client', perplexity_mock):
            perplexity_result = await self.assert_async_performance_threshold(
                self.perplexity_server.health_check(),
                threshold_ms=100
            )
        
        # Test OpenAI health check
        openai_mock = OpenAIMockFactory.create_client_mock()
        with patch.object(self.openai_server, 'openai_client', openai_mock):
            openai_result = await self.assert_async_performance_threshold(
                self.openai_server.health_check(),
                threshold_ms=100
            )
        
        # Both should succeed
        assert "✅" in perplexity_result
        assert "✅" in openai_result
        
        # Check recorded performance data
        health_metrics = tracker.get_metrics('health_check')
        assert len(health_metrics) >= 2, "Should have recorded metrics for both servers"


class TestPerformanceReporting(AsyncTestBase):
    """Test performance reporting and baseline management."""
    
    @pytest.mark.asyncio
    async def test_performance_report_generation(self):
        """Test performance report generation."""
        tracker = PerformanceTracker()
        
        # Record some sample metrics
        tracker.record('health_check', 45.5, {'server': 'perplexity'})
        tracker.record('health_check', 52.3, {'server': 'openai_structured'})
        tracker.record('simple_query', 234.7, {'server': 'perplexity'})
        tracker.record('complex_query', 1456.2, {'server': 'perplexity'})
        
        # Generate report
        report = tracker.generate_report()
        
        assert 'timestamp' in report
        assert report['total_metrics'] == 4
        assert 'operations' in report
        assert 'health_check' in report['operations']
        assert 'simple_query' in report['operations']
        
        # Check health check statistics
        health_stats = report['operations']['health_check']['statistics']
        assert health_stats['count'] == 2
        assert health_stats['min'] == 45.5
        assert health_stats['max'] == 52.3
        
        # Check baseline compliance
        health_baseline = report['operations']['health_check']['baseline_check']
        assert health_baseline['status'] == 'pass'
    
    @pytest.mark.asyncio
    async def test_baseline_violation_detection(self):
        """Test detection of baseline violations."""
        tracker = PerformanceTracker()
        
        # Record metrics that violate baselines
        tracker.record('health_check', 150.0)  # Exceeds 100ms baseline
        tracker.record('simple_query', 800.0)  # Exceeds 500ms baseline
        
        # Check baseline compliance
        health_check = tracker.check_baseline('health_check')
        simple_query_check = tracker.check_baseline('simple_query')
        
        assert health_check['status'] == 'fail'
        assert len(health_check['violations']) > 0
        assert "Max duration" in health_check['violations'][0]
        
        assert simple_query_check['status'] == 'fail'
        assert len(simple_query_check['violations']) > 0
    
    @pytest.mark.asyncio
    async def test_baseline_export_import(self, tmp_path):
        """Test baseline export and import functionality."""
        tracker = PerformanceTracker()
        baseline_file = tmp_path / "test_baselines.json"
        
        # Export baselines
        tracker.export_baselines(baseline_file)
        assert baseline_file.exists()
        
        # Create new tracker and import baselines
        new_tracker = PerformanceTracker()
        new_tracker.import_baselines(baseline_file)
        
        # Verify baselines were imported correctly
        assert 'health_check' in new_tracker.baselines
        assert new_tracker.baselines['health_check'].max_duration_ms == 100
        assert 'simple_query' in new_tracker.baselines
        assert new_tracker.baselines['simple_query'].max_duration_ms == 500
