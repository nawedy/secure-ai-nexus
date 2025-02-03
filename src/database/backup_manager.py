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
    def __init__(self):
        self.backup_dir = Path("/app/backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.storage_client = storage.Client()
        self.bucket_name = os.getenv("BACKUP_BUCKET", "secureai-backups")
        self.retention_days = int(os.getenv("BACKUP_RETENTION_DAYS", "7"))
        self.metrics = BackupMetricsManager()

        # Ensure bucket exists
        self.bucket = self.storage_client.bucket(self.bucket_name)
        if not self.bucket.exists():
            self.bucket.create()

    async def create_backup(self) -> Optional[str]:
        """Create a database backup"""
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
        """Verify backup integrity"""
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
        """Remove backups older than retention period"""
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
        """Calculate SHA256 checksum of file"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
