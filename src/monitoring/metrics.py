from prometheus_client import Counter, Histogram, Gauge
import time
import logging
from typing import Dict, Optional
from azure.monitor import MonitorClient
from azure.identity import DefaultAzureCredential

logger = logging.getLogger(__name__)

# Request metrics
REQUEST_COUNT = Counter(
    'model_request_total',
    'Total number of requests',
    ['model_name', 'status']
)

REQUEST_LATENCY = Histogram(
    'model_request_latency_seconds',
    'Request latency in seconds',
    ['model_name'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
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

# Resource metrics
GPU_MEMORY_USAGE = Gauge(
    'gpu_memory_usage_bytes',
    'GPU memory usage in bytes',
    ['device', 'model_name']
)

class MetricsManager:
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.monitor_client = MonitorClient(credential=self.credential)

    async def record_request(self, model_name: str, status: str, duration: float):
        """Record request metrics"""
        try:
            REQUEST_COUNT.labels(model_name=model_name, status=status).inc()
            REQUEST_LATENCY.labels(model_name=model_name).observe(duration)

            # Send to Azure Monitor
            await self._send_to_azure_monitor({
                'request_count': 1,
                'request_latency': duration,
                'model_name': model_name,
                'status': status
            })
        except Exception as e:
            logger.error(f"Failed to record request metrics: {str(e)}")

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
