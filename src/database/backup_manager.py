"""
Database Backup Manager Module

This module provides functionalities to manage database backups, including creating,
verifying, and cleaning up old backups. It interacts with PostgreSQL for database operations
and Google Cloud Storage for storing backups.
"""
"""
This module manages database backups, including creating, verifying, and cleaning up old backups.

It uses PostgreSQL's pg_dump for creating backups and interacts with Google Cloud Storage for storing and retrieving backups.
The module also manages backup verification using pg_restore and implements a retention policy for old backups.
"""

import logging
import asyncio
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import os
from typing import Optional
from google.cloud import storage
import gzip
import hashlib
import time
from ..monitoring.backup_metrics import BackupMetricsManager

logger = logging.getLogger(__name__)

class DatabaseBackupManager:
    """
    Manages the creation, verification, and cleanup of database backups.
    
    Attributes:
        backup_dir (Path): The local directory where backups are temporarily stored.
        storage_client (storage.Client): Client for interacting with Google Cloud Storage.
        bucket_name (str): The name of the GCS bucket used for backups.
        retention_days (int): The number of days backups are retained.
        metrics (BackupMetricsManager): Manager for recording backup metrics.
        bucket (storage.Bucket): The GCS bucket object.
    """
    def __init__(self):
        """
        Initializes the DatabaseBackupManager.

        Sets up the local backup directory, GCS client, bucket, retention period, and metrics manager.
        """
        self.backup_dir = Path("/app/backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.storage_client = storage.Client()
        """Initialize the DatabaseBackupManager with configurations and setup."""
        self.bucket_name = os.getenv("BACKUP_BUCKET", "secureai-backups")
        self.retention_days = int(os.getenv("BACKUP_RETENTION_DAYS", "7"))
        self.metrics = BackupMetricsManager()

        # Ensure bucket exists
        self.bucket = self.storage_client.bucket(self.bucket_name)
        if not self.bucket.exists():
            self.bucket.create()

    async def create_backup(self) -> Optional[str]:
        """
        Creates a compressed database backup using pg_dump and uploads it to Google Cloud Storage.

        The backup is stored in a custom format with maximum compression.
        It calculates a checksum for the backup file and includes it as metadata in the cloud storage object.
        
        Returns:
            Optional[str]: The local file path of the created backup if successful, otherwise None.
        
        Raises:
            Exception: If the pg_dump process fails or any other error occurs during the backup process.        """
        start_time = time.time()
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"backup_{timestamp}.sql.gz"

            # Create backup using pg_dump
            cmd = [
                "pg_dump",
                "-h", os.getenv("DB_HOST"),
                "-U", os.getenv("DB_USER"),
                "-d", os.getenv("DB_NAME"),
                "-F", "c",  # Custom format
                "-Z", "9",  # Maximum compression
                "-f", str(backup_file)
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                env={"PGPASSWORD": os.getenv("DB_PASSWORD")},
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise Exception(f"Backup failed: {stderr.decode()}")

            # Calculate checksum
            checksum = self._calculate_checksum(backup_file)

            # Upload to GCS
            blob = self.bucket.blob(f"backups/{backup_file.name}")
            blob.metadata = {"checksum": checksum}
            blob.upload_from_filename(str(backup_file))

            # Record metrics
            duration = time.time() - start_time
            size = os.path.getsize(backup_file)
            self.metrics.record_backup_completion(
                duration=duration,
                size=size,
                success=True
            )
            self.metrics.update_backup_age(datetime.utcnow())

            logger.info(f"Backup created successfully: {backup_file.name}")
            return str(backup_file)

        except Exception as e:
            self.metrics.record_backup_completion(
                duration=time.time() - start_time,
                size=0,
                success=False
            )
            logger.error(f"Backup failed: {str(e)}")
            return None
        finally:
            # Cleanup local file
            if backup_file.exists():
                backup_file.unlink()

    async def verify_backup(self, backup_file: str) -> bool:
        """
        Verifies the integrity of a backup file downloaded from Google Cloud Storage.

        It downloads the specified backup file from GCS, calculates its checksum, and compares it to the stored checksum.
        It also attempts a test restore using pg_restore to ensure the backup can be restored.
        
        Args:
            backup_file (str): The name of the backup file to verify.
        
        Returns:
            bool: True if the backup is verified successfully, False otherwise.
        """
        try:
            # Download backup
            blob = self.bucket.blob(f"backups/{backup_file}")
            local_file = self.backup_dir / backup_file
            blob.download_to_filename(str(local_file))

            # Verify checksum
            calculated_checksum = self._calculate_checksum(local_file)
            stored_checksum = blob.metadata.get("checksum")

            if calculated_checksum != stored_checksum:
                raise Exception("Checksum verification failed")

            # Test restore
            test_cmd = [
                "pg_restore",
                "--list",
                str(local_file)
            ]

            process = await asyncio.create_subprocess_exec(
                *test_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise Exception(f"Backup verification failed: {stderr.decode()}")

            self.metrics.record_verification(success=True)
            logger.info(f"Backup verified successfully: {backup_file}")
            return True

        except Exception as e:
            self.metrics.record_verification(success=False)
            logger.error(f"Backup verification failed: {str(e)}")
            return False
        finally:
            # Cleanup
            if local_file.exists():
                local_file.unlink()

    async def cleanup_old_backups(self):
        """
        Cleans up old backup files in Google Cloud Storage that are older than the retention period.

        Iterates through all backup files in the GCS bucket, determines their creation dates based on file names,
        and deletes those older than the specified retention period.
        """
        try:
            blobs = self.bucket.list_blobs(prefix="backups/")
            retention_date = datetime.utcnow() - timedelta(days=self.retention_days)

            for blob in blobs:
                # Extract date from filename
                try:
                    date_str = blob.name.split("_")[1].split(".")[0]
                    backup_date = datetime.strptime(date_str, "%Y%m%d")

                    if backup_date < retention_date:
                        blob.delete()
                        logger.info(f"Deleted old backup: {blob.name}")
                except Exception as e:
                    logger.warning(f"Failed to process backup {blob.name}: {str(e)}")

        except Exception as e:
            logger.error(f"Backup cleanup failed: {str(e)}")

    def _calculate_checksum(self, file_path: Path) -> str:
        """
        Calculates the SHA256 checksum of a given file.

        Reads the file in chunks to handle large files and calculates the checksum.
        
        Args:
            file_path (Path): The path to the file for which to calculate the checksum.

        Returns:
            str: The SHA256 checksum of the file as a hexadecimal string.
        """
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()


