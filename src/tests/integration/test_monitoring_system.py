"""
Integration Tests for Monitoring System Components
Implements comprehensive testing of monitoring functionality
"""

import pytest
import numpy as np
from pathlib import Path
import yaml
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Generator, List
import tensorflow as tf
import json
import pandas as pd

from monitoring.metrics import MetricsCollector
from monitoring.analyzer import MonitoringAnalyzer
from ml.anomaly_detection import AnomalyDetector
from monitoring.alerts import AlertManager

class TestMonitoringSystem:
    """Integration tests for monitoring system components"""

    @pytest.fixture(autouse=True)
    async def setup(self) -> Generator:
        """Setup test environment"""
        # Load test configuration
        config_path = Path("src/tests/ml/training/config.yaml")
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Initialize components
        self.metrics_collector = MetricsCollector()
        self.monitoring_analyzer = MonitoringAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        self.alert_manager = AlertManager()

        # Create test directories
        test_dirs = ["logs", "models", "data", "metrics"]
        for dir_name in test_dirs:
            Path(dir_name).mkdir(exist_ok=True)

        # Generate test data and models
        await self._setup_test_environment()

        yield

        # Cleanup
        await self._cleanup_test_environment()

    async def test_metrics_collection(self) -> None:
        """Test metrics collection functionality"""
        # Create test metrics
        test_metrics = {
            "response_time": 0.5,
            "cpu_usage": 45.2,
            "memory_usage": 512.8,
            "request_count": 1000,
            "error_rate": 0.01
        }

        # Record metrics
        session_id = "test_session_1"
        timestamp = datetime.now()

        for metric_name, value in test_metrics.items():
            await self.metrics_collector.record_metric(
                session_id,
                metric_name,
                value,
                {"timestamp": timestamp}
            )

        # Retrieve and validate metrics
        collected_metrics = await self.metrics_collector.get_metrics(
            session_id,
            start_time=timestamp - timedelta(minutes=5),
            end_time=timestamp + timedelta(minutes=5)
        )

        # Validate collected metrics
        assert isinstance(collected_metrics, dict)
        assert all(metric in collected_metrics for metric in test_metrics)
        assert all(isinstance(collected_metrics[metric], (int, float))
                  for metric in test_metrics)

    async def test_performance_monitoring(self) -> None:
        """Test performance monitoring functionality"""
        # Generate performance data
        performance_data = {
            "cpu_metrics": [
                {
                    "timestamp": datetime.now() - timedelta(seconds=i),
                    "usage": 45.0 + np.random.random() * 10,
                    "cores": 8
                }
                for i in range(100)
            ],
            "memory_metrics": [
                {
                    "timestamp": datetime.now() - timedelta(seconds=i),
                    "usage": 4096 + np.random.random() * 1024,
                    "total": 8192
                }
                for i in range(100)
            ]
        }

        # Record performance metrics
        session_id = "test_session_2"
        for cpu_metric in performance_data["cpu_metrics"]:
            await self.metrics_collector.record_metric(
                session_id,
                "cpu_usage",
                cpu_metric["usage"],
                {"timestamp": cpu_metric["timestamp"], "cores": cpu_metric["cores"]}
            )

        # Analyze performance
        analysis_result = await self.monitoring_analyzer.analyze_performance(
            session_id,
            self._get_monitoring_config()
        )

        # Validate analysis results
        assert isinstance(analysis_result, dict)
        assert "cpu_analysis" in analysis_result
        assert "memory_analysis" in analysis_result
        assert "recommendations" in analysis_result

    async def test_error_monitoring(self) -> None:
        """Test error monitoring functionality"""
        # Generate error events
        error_events = [
            {
                "timestamp": datetime.now() - timedelta(seconds=i),
                "error_type": "API_ERROR",
                "message": f"Test error {i}",
                "stack_trace": f"Stack trace {i}",
                "severity": "high" if i % 3 == 0 else "medium"
            }
            for i in range(10)
        ]

        # Record error events
        session_id = "test_session_3"
        for event in error_events:
            await self.metrics_collector.record_error(
                session_id,
                event
            )

        # Analyze errors
        error_analysis = await self.monitoring_analyzer.analyze_errors(
            session_id,
            self._get_monitoring_config()
        )

        # Validate error analysis
        assert isinstance(error_analysis, dict)
        assert "error_patterns" in error_analysis
        assert "severity_distribution" in error_analysis
        assert "trend_analysis" in error_analysis

    async def test_resource_monitoring(self) -> None:
        """Test resource monitoring functionality"""
        # Generate resource usage data
        resource_data = {
            "cpu": [
                {
                    "timestamp": datetime.now() - timedelta(seconds=i),
                    "usage": 45.0 + np.random.random() * 10
                }
                for i in range(100)
            ],
            "memory": [
                {
                    "timestamp": datetime.now() - timedelta(seconds=i),
                    "usage": 4096 + np.random.random() * 1024
                }
                for i in range(100)
            ],
            "disk": [
                {
                    "timestamp": datetime.now() - timedelta(seconds=i),
                    "usage": 51200 + np.random.random() * 1024
                }
                for i in range(100)
            ]
        }

        # Record resource metrics
        session_id = "test_session_4"
        for resource_type, metrics in resource_data.items():
            for metric in metrics:
                await self.metrics_collector.record_metric(
                    session_id,
                    f"{resource_type}_usage",
                    metric["usage"],
                    {"timestamp": metric["timestamp"]}
                )

        # Analyze resource usage
        resource_analysis = await self.monitoring_analyzer.analyze_resources(
            session_id,
            self._get_monitoring_config()
        )

        # Validate resource analysis
        assert isinstance(resource_analysis, dict)
        assert "cpu_analysis" in resource_analysis
        assert "memory_analysis" in resource_analysis
        assert "disk_analysis" in resource_analysis
        assert "recommendations" in resource_analysis

    async def test_alert_generation(self) -> None:
        """Test alert generation functionality"""
        # Generate test metrics that should trigger alerts
        test_metrics = {
            "cpu_usage": 95.0,  # High CPU usage
            "memory_usage": 7800.0,  # High memory usage
            "error_rate": 0.15,  # High error rate
            "response_time": 5.0  # Slow response time
        }

        # Record metrics that should trigger alerts
        session_id = "test_session_5"
        timestamp = datetime.now()

        for metric_name, value in test_metrics.items():
            await self.metrics_collector.record_metric(
                session_id,
                metric_name,
                value,
                {"timestamp": timestamp}
            )

        # Check for alerts
        alerts = await self.alert_manager.check_alerts(
            session_id,
            self._get_monitoring_config()
        )

        # Validate alerts
        assert isinstance(alerts, list)
        assert len(alerts) > 0
        for alert in alerts:
            assert "type" in alert
            assert "severity" in alert
            assert "message" in alert
            assert "timestamp" in alert

    async def test_ml_monitoring_insights(self) -> None:
        """Test ML-driven monitoring insights"""
        # Generate test monitoring data
        monitoring_data = {
            "metrics": np.random.random((100, 10)),
            "timestamps": [
                datetime.now() - timedelta(seconds=i)
                for i in range(100)
            ]
        }

        # Generate monitoring insights
        insights = await self.monitoring_analyzer.generate_ml_insights(
            monitoring_data,
            self._get_ml_config()
        )

        # Validate insights
        assert isinstance(insights, dict)
        assert "patterns" in insights
        assert "anomalies" in insights
        assert "trends" in insights
        assert "recommendations" in insights

    async def test_comprehensive_monitoring(self) -> None:
        """Test comprehensive monitoring functionality"""
        # Generate comprehensive test data
        test_data = {
            "metrics": {
                "cpu_usage": 75.0,
                "memory_usage": 6144.0,
                "disk_usage": 51200.0,
                "response_time": 0.8,
                "error_rate": 0.02
            },
            "errors": [
                {
                    "type": "API_ERROR",
                    "message": "Test error",
                    "severity": "medium"
                }
            ],
            "performance": {
                "throughput": 1000,
                "latency": 0.05
            }
        }

        # Record comprehensive monitoring data
        session_id = "test_session_6"
        timestamp = datetime.now()

        # Record metrics
        for metric_name, value in test_data["metrics"].items():
            await self.metrics_collector.record_metric(
                session_id,
                metric_name,
                value,
                {"timestamp": timestamp}
            )

        # Record errors
        for error in test_data["errors"]:
            await self.metrics_collector.record_error(
                session_id,
                {**error, "timestamp": timestamp}
            )

        # Perform comprehensive analysis
        analysis_result = await self.monitoring_analyzer.analyze_monitoring_data(
            session_id,
            self._get_monitoring_config()
        )

        # Validate comprehensive results
        assert isinstance(analysis_result, dict)
        assert "metrics_analysis" in analysis_result
        assert "error_analysis" in analysis_result
        assert "performance_analysis" in analysis_result
        assert "resource_analysis" in analysis_result
        assert "ml_insights" in analysis_result
        assert "recommendations" in analysis_result

    async def _setup_test_environment(self) -> None:
        """Setup test environment with necessary data and models"""
        # Create dummy ML models for testing
        input_shape = (self.config["input_dim"],)

        # Create and save monitoring analyzer model
        monitoring_model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=input_shape),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        monitoring_model.save("models/monitoring_analyzer.h5")

        # Create test monitoring data
        test_data = {
            "metrics": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "cpu_usage": 45.0 + np.random.random() * 10,
                    "memory_usage": 4096 + np.random.random() * 1024,
                    "response_time": 0.1 + np.random.random() * 0.5
                }
                for _ in range(100)
            ]
        }

        # Save test data
        with open("data/test_monitoring_data.json", "w") as f:
            json.dump(test_data, f)

    async def _cleanup_test_environment(self) -> None:
        """Clean up test environment"""
        import shutil

        # Remove test directories
        test_dirs = ["logs", "models", "data", "metrics"]
        for dir_name in test_dirs:
            shutil.rmtree(dir_name, ignore_errors=True)

    def _get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration"""
        return {
            "metrics": {
                "collection_interval": 1.0,
                "retention_period": 7 * 24 * 3600,
                "aggregation_window": 300
            },
            "alerts": {
                "cpu_threshold": 80.0,
                "memory_threshold": 7168.0,
                "error_rate_threshold": 0.05,
                "response_time_threshold": 2.0
            },
            "analysis": {
                "window_size": 3600,
                "trend_detection": True,
                "pattern_recognition": True
            },
            "resources": {
                "cpu_warning_threshold": 70.0,
                "cpu_critical_threshold": 90.0,
                "memory_warning_threshold": 6144.0,
                "memory_critical_threshold": 7168.0
            }
        }

    def _get_ml_config(self) -> Dict[str, Any]:
        """Get ML configuration"""
        return {
            "model_paths": {
                "monitoring": "models/monitoring_analyzer.h5"
            },
            "inference_batch_size": 32,
            "confidence_threshold": 0.8,
            "analysis_window": 3600
        }
