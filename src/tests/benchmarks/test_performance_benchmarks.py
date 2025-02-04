"""
Performance Benchmarks for SecureAI Components
Implements comprehensive performance testing and benchmarking
"""

import pytest
import numpy as np
from pathlib import Path
import yaml
import asyncio
from datetime import datetime
import tensorflow as tf
import json
from typing import Dict, Any, Generator

from e2e.advanced_e2e_suite import AdvancedE2ETestingSuite
from security.validation import SecurityValidator
from monitoring.metrics import MetricsCollector
from ml.anomaly_detection import AnomalyDetector
from ml.training.model_trainer import ModelTrainer

class TestPerformanceBenchmarks:
    """Performance benchmarks for all major components"""

    @pytest.fixture(autouse=True)
    async def setup(self) -> Generator:
        """Setup benchmark environment"""
        # Load test configuration
        config_path = Path("src/tests/ml/training/config.yaml")
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Initialize components
        self.e2e_suite = AdvancedE2ETestingSuite()
        self.security_validator = SecurityValidator()
        self.metrics_collector = MetricsCollector()
        self.anomaly_detector = AnomalyDetector()
        self.model_trainer = ModelTrainer(self.config)

        # Create test directories
        test_dirs = ["logs", "models", "data", "benchmarks"]
        for dir_name in test_dirs:
            Path(dir_name).mkdir(exist_ok=True)

        # Generate benchmark data
        await self._setup_benchmark_data()

        yield

        # Cleanup
        await self._cleanup_benchmark_data()

    @pytest.mark.benchmark(
        group="ml-inference",
        min_rounds=100,
        warmup=True
    )
    async def test_ml_model_inference_performance(self, benchmark) -> None:
        """Benchmark ML model inference performance"""
        # Prepare test data
        test_data = np.random.random((100, self.config["input_dim"]))

        def run_inference():
            """Run model inference"""
            return self.model_trainer.behavior_validator.predict(test_data)

        # Run benchmark
        result = benchmark(run_inference)
        assert result is not None
        assert result.shape == (100, 1)

    @pytest.mark.benchmark(
        group="security",
        min_rounds=50,
        warmup=True
    )
    async def test_security_validation_performance(self, benchmark) -> None:
        """Benchmark security validation performance"""
        # Prepare test data
        security_data = {
            "auth": {
                "token": "test_token",
                "user": {"id": 1, "role": "user"}
            },
            "input": {
                "api_requests": [{"method": "GET", "endpoint": "/test"}]
            },
            "access": {
                "user": {"id": 1, "permissions": ["read"]},
                "resource": {"id": "res_1", "type": "document"}
            }
        }

        def run_validation():
            """Run security validation"""
            return asyncio.run(self.security_validator.validate_security(
                security_data,
                self._get_security_config()
            ))

        # Run benchmark
        result = benchmark(run_validation)
        assert result is not None
        assert result.success is not None

    @pytest.mark.benchmark(
        group="monitoring",
        min_rounds=100,
        warmup=True
    )
    async def test_metrics_collection_performance(self, benchmark) -> None:
        """Benchmark metrics collection performance"""
        # Prepare test data
        session_id = "benchmark_session"
        metrics = {
            "response_time": 0.5,
            "cpu_usage": 45.2,
            "memory_usage": 512.8,
            "request_count": 1000
        }

        def record_metrics():
            """Record metrics"""
            return asyncio.run(self.metrics_collector.record_metric(
                session_id,
                "benchmark_metric",
                metrics,
                {"timestamp": datetime.now()}
            ))

        # Run benchmark
        result = benchmark(record_metrics)
        assert result is not None

    @pytest.mark.benchmark(
        group="anomaly-detection",
        min_rounds=50,
        warmup=True
    )
    async def test_anomaly_detection_performance(self, benchmark) -> None:
        """Benchmark anomaly detection performance"""
        # Prepare test data
        test_data = {
            "metrics": np.random.random((1000, 10)),
            "timestamps": [datetime.now() for _ in range(1000)]
        }

        def detect_anomalies():
            """Detect anomalies"""
            return asyncio.run(self.anomaly_detector.detect_anomalies(test_data))

        # Run benchmark
        result = benchmark(detect_anomalies)
        assert result is not None
        assert "anomalies" in result

    @pytest.mark.benchmark(
        group="e2e",
        min_rounds=20,
        warmup=True
    )
    async def test_e2e_execution_performance(self, benchmark) -> None:
        """Benchmark E2E test execution performance"""
        # Prepare test configuration
        test_config = self._get_test_config()

        def run_e2e_tests():
            """Run E2E tests"""
            return asyncio.run(self.e2e_suite.execute_test_suite(test_config))

        # Run benchmark
        result = benchmark(run_e2e_tests)
        assert result is not None
        assert result.success is not None

    @pytest.mark.benchmark(
        group="ml-training",
        min_rounds=5,
        warmup=True
    )
    async def test_model_training_performance(self, benchmark) -> None:
        """Benchmark model training performance"""
        # Prepare training data
        train_data = {
            "features": np.random.random((1000, self.config["input_dim"])),
            "labels": np.random.randint(2, size=(1000, 1))
        }

        def train_model():
            """Train model"""
            return asyncio.run(self.model_trainer.train_behavior_validator(train_data))

        # Run benchmark
        result = benchmark(train_model)
        assert result is not None
        assert isinstance(result, tf.keras.Model)

    async def _setup_benchmark_data(self) -> None:
        """Setup data for benchmarking"""
        # Create benchmark data
        benchmark_data = {
            "metrics": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "value": np.random.random(),
                    "type": "benchmark"
                }
                for _ in range(1000)
            ],
            "events": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "type": "benchmark_event",
                    "data": {"value": np.random.random()}
                }
                for _ in range(500)
            ]
        }

        # Save benchmark data
        with open("data/benchmark_data.json", "w") as f:
            json.dump(benchmark_data, f)

    async def _cleanup_benchmark_data(self) -> None:
        """Clean up benchmark data"""
        import shutil

        # Remove benchmark directories
        test_dirs = ["logs", "models", "data", "benchmarks"]
        for dir_name in test_dirs:
            shutil.rmtree(dir_name, ignore_errors=True)

    def _get_test_config(self) -> Dict[str, Any]:
        """Get test configuration for benchmarks"""
        return {
            "id": "benchmark_001",
            "name": "Benchmark Test Suite",
            "components": ["api", "database", "auth"],
            "validation_rules": {
                "response_time_threshold": 1.0,
                "error_rate_threshold": 0.01
            }
        }

    def _get_security_config(self) -> Dict[str, Any]:
        """Get security configuration for benchmarks"""
        return {
            "auth_rules": {
                "token_expiry": 3600,
                "session_timeout": 1800
            },
            "validation_rules": {
                "max_request_size": 1024 * 1024
            }
        }
