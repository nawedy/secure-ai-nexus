from prometheus_client import Counter, Histogram, Gauge
import psutil
import logging
from typing import Dict, Any
from datetime import datetime
import aiohttp
import json
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class SystemMonitor:
    """
    Comprehensive system monitoring for SecureAI Platform.
    Handles metrics collection, health checks, and alerting.
    """

    def __init__(self):
        # System metrics
        self.cpu_usage = Gauge('system_cpu_usage', 'CPU usage percentage')
        self.memory_usage = Gauge('system_memory_usage', 'Memory usage percentage')
        self.disk_usage = Gauge('system_disk_usage', 'Disk usage percentage')

        # Application metrics
        self.request_count = Counter('app_request_total', 'Total requests', ['method', 'endpoint', 'status'])
        self.request_latency = Histogram(
            'app_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint']
        )

        # Model metrics
        self.model_inference_time = Histogram(
            'model_inference_duration_seconds',
            'Model inference duration in seconds',
            ['model_name']
        )
        self.model_memory_usage = Gauge(
            'model_memory_usage_bytes',
            'Model memory usage in bytes',
            ['model_name']
        )

        # Cache metrics
        self.cache_hits = Counter('cache_hits_total', 'Total cache hits')
        self.cache_misses = Counter('cache_misses_total', 'Total cache misses')

        # Security metrics
        self.failed_auth_attempts = Counter(
            'failed_auth_attempts_total',
            'Failed authentication attempts',
            ['ip_address']
        )
        self.blocked_requests = Counter(
            'blocked_requests_total',
            'Blocked malicious requests',
            ['reason']
        )

        # Initialize alert thresholds
        self.alert_thresholds = {
            'cpu_usage': 80.0,  # 80% CPU usage
            'memory_usage': 85.0,  # 85% memory usage
            'disk_usage': 90.0,  # 90% disk usage
            'error_rate': 0.05,  # 5% error rate
            'response_time': 1.0  # 1 second
        }

    async def collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_usage.set(cpu_percent)

            # Memory metrics
            memory = psutil.virtual_memory()
            self.memory_usage.set(memory.percent)

            # Disk metrics
            disk = psutil.disk_usage('/')
            self.disk_usage.set(disk.percent)

            return {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent
            }
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
            raise

    async def record_request_metrics(self, method: str, endpoint: str, status: int, duration: float):
        """Record API request metrics"""
        try:
            self.request_count.labels(
                method=method,
                endpoint=endpoint,
                status=status
            ).inc()

            self.request_latency.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
        except Exception as e:
            logger.error(f"Error recording request metrics: {str(e)}")

    async def record_model_metrics(self, model_name: str, inference_time: float, memory_usage: int):
        """Record model performance metrics"""
        try:
            self.model_inference_time.labels(
                model_name=model_name
            ).observe(inference_time)

            self.model_memory_usage.labels(
                model_name=model_name
            ).set(memory_usage)
        except Exception as e:
            logger.error(f"Error recording model metrics: {str(e)}")

    async def check_health(self) -> Dict[str, Any]:
        """Comprehensive health check of all system components"""
        try:
            metrics = await self.collect_system_metrics()
            status = "healthy"
            alerts = []

            # Check CPU usage
            if metrics['cpu_usage'] > self.alert_thresholds['cpu_usage']:
                alerts.append(f"High CPU usage: {metrics['cpu_usage']}%")
                status = "degraded"

            # Check memory usage
            if metrics['memory_usage'] > self.alert_thresholds['memory_usage']:
                alerts.append(f"High memory usage: {metrics['memory_usage']}%")
                status = "degraded"

            # Check disk usage
            if metrics['disk_usage'] > self.alert_thresholds['disk_usage']:
                alerts.append(f"High disk usage: {metrics['disk_usage']}%")
                status = "degraded"

            return {
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": metrics,
                "alerts": alerts
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Health check failed")

    async def send_alert(self, alert_type: str, message: str):
        """Send alerts to configured notification channels"""
        try:
            alert_data = {
                "type": alert_type,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "severity": "high" if alert_type in ["security", "error"] else "medium"
            }

            # Send to notification service
            async with aiohttp.ClientSession() as session:
                await session.post(
                    "http://notification-service/alerts",
                    json=alert_data
                )

            logger.info(f"Alert sent: {alert_type} - {message}")
        except Exception as e:
            logger.error(f"Failed to send alert: {str(e)}")

    def update_alert_thresholds(self, new_thresholds: Dict[str, float]):
        """Update alert thresholds"""
        try:
            for key, value in new_thresholds.items():
                if key in self.alert_thresholds:
                    self.alert_thresholds[key] = value
            logger.info("Alert thresholds updated successfully")
        except Exception as e:
            logger.error(f"Failed to update alert thresholds: {str(e)}")
            raise

# Initialize global system monitor
system_monitor = SystemMonitor()
