"""
Module: Backup Metrics

This module defines and manages metrics related to backup operations,
including duration, size, success/failure rates, verification status, and backup age.
"""

from prometheus_client import Counter, Gauge, Histogram
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Histogram to track backup duration in seconds, with predefined buckets
BACKUP_DURATION = Histogram(
    'backup_duration_seconds',
    'Time taken to complete a backup operation',
    buckets=(60, 300, 600, 1800, 3600)
)

# Gauge to track the size of backups in bytes
BACKUP_SIZE = Gauge(
    'backup_size_bytes',
    'Size of the backup in bytes',
)

# Counter to track the total number of successful backups
BACKUP_SUCCESS = Counter(
    'backup_success_total',
    'Total number of successful backup operations'
)

# Counter to track the total number of failed backups
BACKUP_FAILURE = Counter(
    'backup_failure_total',
    'Total number of failed backup operations'
)

# Counter to track the number of backup verifications, labeled by status (success/failure)
BACKUP_VERIFICATION = Counter(
    'backup_verification_total',
    'Total number of backup verification attempts',
    ['status']
)

# Gauge to track the age of the most recent backup in seconds
BACKUP_AGE = Gauge(
    'backup_age_seconds',
    'Age of the most recent backup in seconds'
)

class BackupMetricsManager:
    """
    BackupMetricsManager Class

    This class provides static methods to record and manage metrics related to backup operations.
    It handles recording backup completion, verification results, and updating the age of the most recent backup.
    """

    @staticmethod
    def record_backup_completion(duration: float, size: int, success: bool):
        """
        Records metrics upon the completion of a backup operation.

        Args:
            duration (float): The time taken for the backup operation to complete, in seconds.
            size (int): The size of the backup in bytes.
            success (bool): True if the backup was successful, False otherwise.
        """
        BACKUP_DURATION.observe(duration)
        BACKUP_SIZE.set(size)

        if success:
            BACKUP_SUCCESS.inc()
        else:
            BACKUP_FAILURE.inc()        

    @staticmethod
    def record_verification(success: bool):
        """
        Records the result of a backup verification.

        Args:
            success (bool): True if the verification was successful, False otherwise.
        """
        BACKUP_VERIFICATION.labels(
            status="success" if success else "failure"
        ).inc()

    @staticmethod
    def update_backup_age(timestamp: datetime):
        """
        Updates the recorded age of the most recent backup.

        Args:
            timestamp (datetime): The timestamp of the most recent backup.
        """
        age = (datetime.utcnow() - timestamp).total_seconds()
        BACKUP_AGE.set(age)
