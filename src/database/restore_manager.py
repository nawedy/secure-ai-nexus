import logging
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
import os
from typing import Optional, List, Dict
from google.cloud import storage
import tempfile
from ..monitoring.backup_metrics import BackupMetricsManager

logger = logging.getLogger(__name__)

class RestoreManager:
    def __init__(self):
        self.storage_client = storage.Client()
        self.bucket_name = os.getenv("BACKUP_BUCKET", "secureai-backups")
        self.bucket = self.storage_client.bucket(self.bucket_name)
        self.metrics = BackupMetricsManager()
        self.restore_dir = Path("/app/restore")
        self.restore_dir.mkdir(exist_ok=True)

    async def list_available_backups(self) -> List[Dict]:
        """List all available backups with metadata"""
        try:
            backups = []
            blobs = self.bucket.list_blobs(prefix="backups/")

            for blob in blobs:
                backup_info = {
                    'name': blob.name,
                    'size': blob.size,
                    'created': blob.time_created,
                    'checksum': blob.metadata.get('checksum') if blob.metadata else None
                }
                backups.append(backup_info)

            return sorted(backups, key=lambda x: x['created'], reverse=True)

        except Exception as e:
            logger.error(f"Failed to list backups: {str(e)}")
            raise

    async def restore_backup(self, backup_name: str, target_db: str) -> bool:
        """Restore a specific backup to target database"""
        temp_dir = None
        try:
            temp_dir = tempfile.mkdtemp()
            local_file = Path(temp_dir) / backup_name

            # Download backup
            blob = self.bucket.blob(f"backups/{backup_name}")
            blob.download_to_filename(str(local_file))

            # Verify backup before restore
            if not await self._verify_backup(local_file, blob.metadata.get('checksum')):
                raise Exception("Backup verification failed")

            # Create target database if it doesn't exist
            await self._create_database(target_db)

            # Restore backup
            cmd = [
                "pg_restore",
                "-h", os.getenv("DB_HOST"),
                "-U", os.getenv("DB_USER"),
                "-d", target_db,
                "-c",  # Clean (drop) database objects before recreating
                "-v",  # Verbose mode
                str(local_file)
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                env={"PGPASSWORD": os.getenv("DB_PASSWORD")},
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise Exception(f"Restore failed: {stderr.decode()}")

            # Verify restoration
            if not await self._verify_restoration(target_db):
                raise Exception("Restoration verification failed")

            logger.info(f"Backup {backup_name} restored successfully to {target_db}")
            return True

        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            return False

        finally:
            # Cleanup
            if temp_dir and os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir)

    async def _verify_backup(self, backup_file: Path, expected_checksum: str) -> bool:
        """Verify backup file integrity"""
        try:
            # Verify backup structure
            test_cmd = ["pg_restore", "--list", str(backup_file)]
            process = await asyncio.create_subprocess_exec(
                *test_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                raise Exception(f"Backup structure verification failed: {stderr.decode()}")

            # Verify checksum if provided
            if expected_checksum:
                import hashlib
                sha256 = hashlib.sha256()
                with open(backup_file, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256.update(chunk)
                if sha256.hexdigest() != expected_checksum:
                    raise Exception("Checksum verification failed")

            return True

        except Exception as e:
            logger.error(f"Backup verification failed: {str(e)}")
            return False

    async def _create_database(self, db_name: str):
        """Create database if it doesn't exist"""
        try:
            cmd = [
                "psql",
                "-h", os.getenv("DB_HOST"),
                "-U", os.getenv("DB_USER"),
                "-d", "postgres",
                "-c", f"CREATE DATABASE {db_name}"
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                env={"PGPASSWORD": os.getenv("DB_PASSWORD")},
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            # Ignore error if database already exists
            if process.returncode != 0 and "already exists" not in stderr.decode():
                raise Exception(f"Database creation failed: {stderr.decode()}")

        except Exception as e:
            logger.error(f"Database creation failed: {str(e)}")
            raise

    async def _verify_restoration(self, db_name: str) -> bool:
        """Verify database restoration"""
        try:
            cmd = [
                "psql",
                "-h", os.getenv("DB_HOST"),
                "-U", os.getenv("DB_USER"),
                "-d", db_name,
                "-c", "SELECT COUNT(*) FROM information_schema.tables"
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                env={"PGPASSWORD": os.getenv("DB_PASSWORD")},
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise Exception(f"Restoration verification failed: {stderr.decode()}")

            return True

        except Exception as e:
            logger.error(f"Restoration verification failed: {str(e)}")
            return False
