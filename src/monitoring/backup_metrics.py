from prometheus_client import Counter, Gauge, Histogram
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Backup metrics
BACKUP_DURATION = Histogram(
    'backup_duration_seconds',
    'Time taken to complete backup',
    buckets=(60, 300, 600, 1800, 3600)
)

BACKUP_SIZE = Gauge(
    'backup_size_bytes',
    'Size of backup in bytes',
)

BACKUP_SUCCESS = Counter(
    'backup_success_total',
    'Number of successful backups'
)

BACKUP_FAILURE = Counter(
    'backup_failure_total',
    'Number of failed backups'
)

BACKUP_VERIFICATION = Counter(
    'backup_verification_total',
    'Number of backup verifications',
    ['status']
)

BACKUP_AGE = Gauge(
    'backup_age_seconds',
    'Age of most recent backup in seconds'
)

class BackupMetricsManager:
    @staticmethod
    def record_backup_completion(duration: float, size: int, success: bool):
        """Record backup completion metrics"""
        BACKUP_DURATION.observe(duration)
        BACKUP_SIZE.set(size)

        if success:
            BACKUP_SUCCESS.inc()
        else:
            BACKUP_FAILURE.inc()

    @staticmethod
    def record_verification(success: bool):
        """Record backup verification result"""
        BACKUP_VERIFICATION.labels(
            status="success" if success else "failure"
        ).inc()

    @staticmethod
    def update_backup_age(timestamp: datetime):
        """Update age of most recent backup"""
        age = (datetime.utcnow() - timestamp).total_seconds()
        BACKUP_AGE.set(age)
