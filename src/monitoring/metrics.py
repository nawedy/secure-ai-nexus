from prometheus_client import Counter, Histogram, Gauge
import time
import logging
from typing import Dict, Any
from azure.monitor import MonitorClient
from azure.identity import DefaultAzureCredential

logger = logging.getLogger(__name__)

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

# Model metrics
MODEL_REQUEST_COUNT = Counter(
    'model_request_total',
    'Total number of model inference requests',
    ['model_name', 'status']
)

MODEL_LATENCY = Histogram(
    'model_request_latency_seconds',
    'Model inference latency in seconds',
    ['model_name']
)

# Resource metrics
MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes'
)

GPU_MEMORY_USAGE = Gauge(
    'gpu_memory_usage_bytes',
    'GPU memory usage in bytes',
    ['device']
)

# Security metrics
SECURITY_EVENTS = Counter(
    'security_events_total',
    'Total number of security events',
    ['event_type', 'severity']
)

FAILED_AUTH_ATTEMPTS = Counter(
    'failed_auth_attempts_total',
    'Total number of failed authentication attempts',
    ['auth_type']
)

class MetricsManager:
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.monitor_client = MonitorClient(credential=self.credential)

    @staticmethod
    def record_request(method: str, endpoint: str, status: int, duration: float):
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)

    @staticmethod
    def record_model_request(model_name: str, status: str, duration: float):
        MODEL_REQUEST_COUNT.labels(model_name=model_name, status=status).inc()
        MODEL_LATENCY.labels(model_name=model_name).observe(duration)

    @staticmethod
    def update_memory_usage(bytes_used: int):
        MEMORY_USAGE.set(bytes_used)

    @staticmethod
    def update_gpu_memory(device: str, bytes_used: int):
        GPU_MEMORY_USAGE.labels(device=device).set(bytes_used)

    async def record_security_event(self, event_type: str, severity: str, details: Dict):
        """Record security event metrics"""
        try:
            SECURITY_EVENTS.labels(event_type=event_type, severity=severity).inc()

            # Send to Azure Monitor
            await self._send_to_azure_monitor({
                'security_event': event_type,
                'severity': severity,
                'details': details
            })
        except Exception as e:
            logger.error(f"Failed to record security event: {str(e)}")

    async def record_auth_failure(self, auth_type: str):
        """Record authentication failure metrics"""
        try:
            FAILED_AUTH_ATTEMPTS.labels(auth_type=auth_type).inc()

            # Send to Azure Monitor
            await self._send_to_azure_monitor({
                'failed_auth_attempt': 1,
                'auth_type': auth_type
            })
        except Exception as e:
            logger.error(f"Failed to record auth failure: {str(e)}")

    async def _send_to_azure_monitor(self, metrics: Dict):
        """Send metrics to Azure Monitor"""
        try:
            await self.monitor_client.metrics.create_or_update(
                resource_group_name="secureai-rg",
                service_name="secureai-app",
                metric_name="custom_metrics",
                parameters=metrics
            )
        except Exception as e:
            logger.error(f"Failed to send metrics to Azure Monitor: {str(e)}")
