import pytest
import asyncio
import time
from typing import Dict, List
from src.monitoring.system import system_monitor
from src.monitoring.metrics_detail import metrics_detail

class PerformanceBenchmark:
    """Performance benchmark test suite"""

    def __init__(self):
        self.thresholds = {
            'api_latency': 200,  # ms
            'model_inference': 1000,  # ms
            'database_query': 100,  # ms
            'memory_usage': 85,  # percent
            'cpu_usage': 80  # percent
        }

    async def run_api_benchmarks(self, endpoint: str, requests: int = 1000) -> Dict:
        """Run API performance benchmarks"""
        latencies = []
        errors = 0

        async with aiohttp.ClientSession() as session:
            for _ in range(requests):
                start_time = time.time()
                try:
                    async with session.get(endpoint) as response:
                        await response.text()
                        latency = (time.time() - start_time) * 1000
                        latencies.append(latency)
                except Exception:
                    errors += 1

        return {
            'average_latency': sum(latencies) / len(latencies),
            'p95_latency': sorted(latencies)[int(len(latencies) * 0.95)],
            'error_rate': errors / requests * 100,
            'passed': (sum(latencies) / len(latencies)) < self.thresholds['api_latency']
        }

    async def run_model_benchmarks(self, model_name: str, iterations: int = 100) -> Dict:
        """Run model performance benchmarks"""
        inference_times = []
        memory_usage = []

        for _ in range(iterations):
            start_time = time.time()
            metrics = await metrics_detail._get_performance_metrics()
            inference_times.append((time.time() - start_time) * 1000)
            memory_usage.append(metrics['model_memory_usage'].get(model_name, 0))

        return {
            'average_inference_time': sum(inference_times) / len(inference_times),
            'p95_inference_time': sorted(inference_times)[int(len(inference_times) * 0.95)],
            'average_memory_usage': sum(memory_usage) / len(memory_usage),
            'passed': (sum(inference_times) / len(inference_times)) < self.thresholds['model_inference']
        }

@pytest.mark.asyncio
async def test_api_performance():
    benchmark = PerformanceBenchmark()
    results = await benchmark.run_api_benchmarks('http://localhost:8000/health')
    assert results['passed']
    assert results['error_rate'] < 1

@pytest.mark.asyncio
async def test_model_performance():
    benchmark = PerformanceBenchmark()
    results = await benchmark.run_model_benchmarks('default_model')
    assert results['passed']
    assert results['average_memory_usage'] < benchmark.thresholds['memory_usage']
