"""Performance testing utilities for MCP servers."""

import time
import asyncio
import statistics
import json
import os
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PerformanceMetric:
    """Container for performance measurement data."""
    operation: str
    duration_ms: float
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PerformanceBaseline:
    """Performance baseline definition."""
    operation: str
    max_duration_ms: float
    percentile_95_ms: Optional[float] = None
    description: str = ""


class PerformanceTracker:
    """Track and analyze performance metrics for MCP servers."""
    
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.baselines: Dict[str, PerformanceBaseline] = self._load_default_baselines()
    
    def _load_default_baselines(self) -> Dict[str, PerformanceBaseline]:
        """Load default performance baselines for MCP operations."""
        return {
            'health_check': PerformanceBaseline(
                operation='health_check',
                max_duration_ms=100,
                percentile_95_ms=50,
                description='Health check should be very fast'
            ),
            'simple_query': PerformanceBaseline(
                operation='simple_query', 
                max_duration_ms=500,
                percentile_95_ms=300,
                description='Simple queries should complete quickly'
            ),
            'complex_query': PerformanceBaseline(
                operation='complex_query',
                max_duration_ms=2000,
                percentile_95_ms=1500,
                description='Complex queries may take longer but should be bounded'
            ),
            'structured_extraction': PerformanceBaseline(
                operation='structured_extraction',
                max_duration_ms=1000,
                percentile_95_ms=800,
                description='Structured data extraction with OpenAI'
            ),
            'code_analysis': PerformanceBaseline(
                operation='code_analysis',
                max_duration_ms=1500,
                percentile_95_ms=1200,
                description='Code analysis operations'
            ),
            'batch_operation': PerformanceBaseline(
                operation='batch_operation',
                max_duration_ms=5000,
                percentile_95_ms=4000,
                description='Batch operations on multiple items'
            )
        }
    
    def record(self, operation: str, duration_ms: float, metadata: Optional[Dict[str, Any]] = None):
        """Record a performance metric."""
        metric = PerformanceMetric(
            operation=operation,
            duration_ms=duration_ms,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        self.metrics.append(metric)
    
    def get_metrics(self, operation: Optional[str] = None) -> List[PerformanceMetric]:
        """Get recorded metrics, optionally filtered by operation."""
        if operation:
            return [m for m in self.metrics if m.operation == operation]
        return self.metrics
    
    def get_statistics(self, operation: str) -> Dict[str, float]:
        """Get statistical summary for an operation."""
        durations = [m.duration_ms for m in self.get_metrics(operation)]
        if not durations:
            return {}
        
        return {
            'min': min(durations),
            'max': max(durations),
            'mean': statistics.mean(durations),
            'median': statistics.median(durations),
            'std_dev': statistics.stdev(durations) if len(durations) > 1 else 0,
            'p95': statistics.quantiles(durations, n=20)[18] if len(durations) > 4 else max(durations),
            'count': len(durations)
        }
    
    def check_baseline(self, operation: str) -> Dict[str, Any]:
        """Check if operation performance meets baseline requirements."""
        if operation not in self.baselines:
            return {'status': 'unknown', 'message': f'No baseline defined for {operation}'}
        
        baseline = self.baselines[operation]
        stats = self.get_statistics(operation)
        
        if not stats:
            return {'status': 'no_data', 'message': f'No metrics recorded for {operation}'}
        
        violations = []
        
        if stats['max'] > baseline.max_duration_ms:
            violations.append(f"Max duration {stats['max']:.1f}ms exceeds limit {baseline.max_duration_ms}ms")
        
        if baseline.percentile_95_ms and stats['p95'] > baseline.percentile_95_ms:
            violations.append(f"95th percentile {stats['p95']:.1f}ms exceeds limit {baseline.percentile_95_ms}ms")
        
        if violations:
            return {
                'status': 'fail',
                'violations': violations,
                'stats': stats,
                'baseline': baseline
            }
        else:
            return {
                'status': 'pass',
                'message': f'{operation} performance meets baseline requirements',
                'stats': stats,
                'baseline': baseline
            }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        operations = set(m.operation for m in self.metrics)
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_metrics': len(self.metrics),
            'operations': {}
        }
        
        for operation in operations:
            stats = self.get_statistics(operation)
            baseline_check = self.check_baseline(operation)
            
            report['operations'][operation] = {
                'statistics': stats,
                'baseline_check': baseline_check
            }
        
        return report
    
    def export_baselines(self, filepath: Path):
        """Export current performance baselines to JSON file."""
        baseline_data = {
            operation: {
                'max_duration_ms': baseline.max_duration_ms,
                'percentile_95_ms': baseline.percentile_95_ms,
                'description': baseline.description
            }
            for operation, baseline in self.baselines.items()
        }
        
        with open(filepath, 'w') as f:
            json.dump(baseline_data, f, indent=2)
    
    def import_baselines(self, filepath: Path):
        """Import performance baselines from JSON file."""
        if not filepath.exists():
            return
        
        with open(filepath, 'r') as f:
            baseline_data = json.load(f)
        
        for operation, data in baseline_data.items():
            self.baselines[operation] = PerformanceBaseline(
                operation=operation,
                max_duration_ms=data['max_duration_ms'],
                percentile_95_ms=data.get('percentile_95_ms'),
                description=data.get('description', '')
            )


class AsyncPerformanceTimer:
    """Context manager for timing async operations."""
    
    def __init__(self, tracker: PerformanceTracker, operation: str, metadata: Optional[Dict[str, Any]] = None):
        self.tracker = tracker
        self.operation = operation
        self.metadata = metadata or {}
        self.start_time = None
    
    async def __aenter__(self):
        self.start_time = time.time()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            self.tracker.record(self.operation, duration_ms, self.metadata)


class PerformanceTester:
    """High-level performance testing utilities."""
    
    def __init__(self, tracker: Optional[PerformanceTracker] = None):
        self.tracker = tracker or PerformanceTracker()
    
    async def time_async_operation(self, operation: str, coro, metadata: Optional[Dict[str, Any]] = None):
        """Time an async operation and record results."""
        async with AsyncPerformanceTimer(self.tracker, operation, metadata):
            return await coro
    
    async def run_load_test(self, operation_name: str, async_operation: Callable, 
                          concurrent_requests: int = 10, total_requests: int = 100) -> Dict[str, Any]:
        """Run load test with concurrent requests."""
        semaphore = asyncio.Semaphore(concurrent_requests)
        
        async def run_single_request(request_id: int):
            async with semaphore:
                metadata = {'request_id': request_id, 'concurrent_limit': concurrent_requests}
                return await self.time_async_operation(f"{operation_name}_load", async_operation(), metadata)
        
        # Run all requests
        start_time = time.time()
        tasks = [run_single_request(i) for i in range(total_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_duration = time.time() - start_time
        
        # Analyze results
        successes = [r for r in results if not isinstance(r, Exception)]
        failures = [r for r in results if isinstance(r, Exception)]
        
        return {
            'total_requests': total_requests,
            'concurrent_requests': concurrent_requests,
            'successes': len(successes),
            'failures': len(failures),
            'failure_rate': len(failures) / total_requests,
            'total_duration_sec': total_duration,
            'requests_per_sec': total_requests / total_duration,
            'failure_details': [str(f) for f in failures[:5]]  # First 5 failures
        }
    
    async def stress_test_memory(self, operation_name: str, async_operation: Callable,
                               duration_seconds: int = 30) -> Dict[str, Any]:
        """Run stress test to check for memory leaks."""
        import psutil
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < duration_seconds:
            try:
                await self.time_async_operation(f"{operation_name}_stress", async_operation())
                request_count += 1
                
                # Brief pause to prevent overwhelming
                await asyncio.sleep(0.01)
            except Exception as e:
                print(f"Stress test error: {e}")
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        return {
            'duration_seconds': duration_seconds,
            'total_requests': request_count,
            'requests_per_second': request_count / duration_seconds,
            'initial_memory_mb': initial_memory,
            'final_memory_mb': final_memory,
            'memory_growth_mb': final_memory - initial_memory,
            'memory_growth_per_request_kb': ((final_memory - initial_memory) * 1024) / request_count if request_count > 0 else 0
        }


# Global performance tracker instance for easy access
_global_tracker = PerformanceTracker()

def get_global_tracker() -> PerformanceTracker:
    """Get the global performance tracker instance."""
    return _global_tracker

def reset_global_tracker():
    """Reset the global performance tracker."""
    global _global_tracker
    _global_tracker = PerformanceTracker()
