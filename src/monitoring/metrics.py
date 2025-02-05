import logging
import os
import time
from typing import Any, Dict
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from prometheus_client import multiprocess

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
    """
    Manages the recording of metrics.
    """
    def start_prometheus_server(self, port: int = 8000) -> None:
        """Starts the Prometheus metrics server."""
        logger.info(f"Starting Prometheus metrics server on port {port}")
        
        try:
            start_http_server(port)
        except Exception as e:
            logger.error(f"Error starting Prometheus server: {e}")
            
    
    def __init__(self):
        """
        Records HTTP request metrics.

        Args:
            method (str): HTTP method (e.g., GET, POST).
            endpoint (str): The endpoint of the request.
            status (int): HTTP status code.
            duration (float): Request duration in seconds.
        """
    def record_request(self, method: str, endpoint: str, status: int, duration: float) -> None:
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)
        logger.info(f"Recording request: method={method}, endpoint={endpoint}, status={status}, duration={duration}")
    def record_model_request(self, model_name: str, status: str, duration: float) -> None:
        """
        Records model inference request metrics.

        Args:
            model_name (str): Name of the model.
            status (str): Status of the request (e.g., success, failure).
            duration (float): Request duration in seconds.
        """
        MODEL_REQUEST_COUNT.labels(model_name=model_name, status=status).inc()
        MODEL_LATENCY.labels(model_name=model_name).observe(duration)
        pass

    def update_memory_usage(self, bytes_used: int) -> None:
        """
        Updates the memory usage metric.

        Args:
            bytes_used (int): Memory usage in bytes.
        """
        MEMORY_USAGE.set(bytes_used)
        logger.info(f"Updating memory usage: bytes_used={bytes_used}")
        pass

    def update_gpu_memory(self, device: str, bytes_used: int) -> None:
        Updates the GPU memory usage metric.

        Args:
            device (str): Name of the GPU device.
            bytes_used (int): GPU memory usage in bytes.
        """
        GPU_MEMORY_USAGE.labels(device=device).set(bytes_used)
        logger.info(f"Updating GPU memory: device={device}, bytes_used={bytes_used}")
        pass

    def record_security_event(self, event_type: str, severity: str, details: Dict) -> None:
                """
                Records security event metrics.

                Args:
                    event_type (str): Type of the security event.
                    severity (str): Severity of the security event.
                    details (Dict): Additional details about the event.
                """
                SECURITY_EVENTS.labels(event_type=event_type, severity=severity).inc()
                logger.info(f"Recording security event: event_type={event_type}, severity={severity}")
                pass

    def record_auth_failure(self, auth_type: str) -> None:
                """
                Records authentication failure metrics.

                Args:
                    auth_type (str): Type of authentication that failed.
                """
                FAILED_AUTH_ATTEMPTS.labels(auth_type=auth_type).inc()
                logger.info(f"Recording auth failure: auth_type={auth_type}")
                pass
                
