from typing import Dict, Any
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class MetricsDetail:
    """Detailed metrics collection and analysis"""

    def __init__(self):
        self.metrics_history: Dict[str, list] = {
            'system': [],
            'application': [],
            'security': [],
            'performance': []
        }
        self.retention_days = 30

    async def collect_detailed_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive metrics across all components"""
        try:
            current_metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'system': await self._get_system_metrics(),
                'application': await self._get_application_metrics(),
                'security': await self._get_security_metrics(),
                'performance': await self._get_performance_metrics()
            }

            # Store metrics history
            for category in self.metrics_history:
                self.metrics_history[category].append(current_metrics[category])
                # Cleanup old metrics
                self._cleanup_old_metrics(category)

            return current_metrics
        except Exception as e:
            logger.error(f"Error collecting detailed metrics: {str(e)}")
            raise

    async def _get_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level metrics"""
        return await system_monitor.collect_system_metrics()

    async def _get_application_metrics(self) -> Dict[str, Any]:
        """Collect application-specific metrics"""
        return {
            'request_count': self.request_count._value.get(),
            'average_latency': self.request_latency._sum.get() / self.request_latency._count.get() if self.request_latency._count.get() > 0 else 0,
            'cache_hit_ratio': self.cache_hits._value.get() / (self.cache_hits._value.get() + self.cache_misses._value.get()) if (self.cache_hits._value.get() + self.cache_misses._value.get()) > 0 else 0
        }

    async def _get_security_metrics(self) -> Dict[str, Any]:
        """Collect security-related metrics"""
        return {
            'failed_auth_attempts': self.failed_auth_attempts._value.get(),
            'blocked_requests': self.blocked_requests._value.get(),
            'security_incidents': len([a for a in self.alerts if a['type'] == 'security'])
        }

    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Collect performance metrics"""
        return {
            'model_inference_times': {
                model: self.model_inference_time.labels(model_name=model)._sum.get() /
                      self.model_inference_time.labels(model_name=model)._count.get()
                for model in self.model_inference_time._labelvalues
            },
            'model_memory_usage': {
                model: self.model_memory_usage.labels(model_name=model)._value.get()
                for model in self.model_memory_usage._labelvalues
            }
        }

    def _cleanup_old_metrics(self, category: str):
        """Remove metrics older than retention period"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
        self.metrics_history[category] = [
            metric for metric in self.metrics_history[category]
            if datetime.fromisoformat(metric['timestamp']) > cutoff_date
        ]

metrics_detail = MetricsDetail()
