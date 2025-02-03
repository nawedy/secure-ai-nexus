from prometheus_client import Counter, Gauge, Histogram
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Restore operation metrics
RESTORE_DURATION = Histogram(
    'restore_duration_seconds',
    'Time taken to complete restore operation',
    buckets=(60, 300, 600, 1800, 3600)
)

RESTORE_SIZE = Gauge(
    'restore_size_bytes',
    'Size of restored database in bytes'
)

RESTORE_SUCCESS = Counter(
    'restore_success_total',
    'Number of successful restore operations'
)

RESTORE_FAILURE = Counter(
    'restore_failure_total',
    'Number of failed restore operations',
    ['failure_reason']
)

RESTORE_VERIFICATION = Counter(
    'restore_verification_total',
    'Number of restore verifications',
    ['status']
)

RESTORE_IN_PROGRESS = Gauge(
    'restore_in_progress',
    'Number of restore operations currently in progress'
)

class RestoreMetricsManager:
    @staticmethod
    def record_restore_start():
        """Record start of restore operation"""
        RESTORE_IN_PROGRESS.inc()

    @staticmethod
    def record_restore_completion(duration: float, size: int, success: bool, failure_reason: str = None):
        """Record restore completion metrics"""
        RESTORE_DURATION.observe(duration)
        RESTORE_SIZE.set(size)
        RESTORE_IN_PROGRESS.dec()

        if success:
            RESTORE_SUCCESS.inc()
        else:
            RESTORE_FAILURE.labels(
                failure_reason=failure_reason or 'unknown'
            ).inc()

    @staticmethod
    def record_verification(success: bool):
        """Record restore verification result"""
        RESTORE_VERIFICATION.labels(
            status="success" if success else "failure"
        ).inc()

    @staticmethod
    def get_restore_stats() -> Dict[str, Any]:
        """Get current restore statistics"""
        return {
            'in_progress': RESTORE_IN_PROGRESS._value.get(),
            'total_success': RESTORE_SUCCESS._value.get(),
            'total_failure': sum(
                RESTORE_FAILURE.labels(failure_reason=reason)._value.get()
                for reason in RESTORE_FAILURE._labelvalues['failure_reason']
            ),
            'verification_success': RESTORE_VERIFICATION.labels(status="success")._value.get(),
            'verification_failure': RESTORE_VERIFICATION.labels(status="failure")._value.get()
        }
