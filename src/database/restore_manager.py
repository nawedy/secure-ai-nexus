"""
Module: Restore Manager

This module provides functionalities to manage the restoration of database backups.
It interacts with Google Cloud Storage to list available backups, download backups,
and restore them to a target database. It also includes verification checks for backup
integrity and restoration success.
"""
import logging
import asyncio
from pathlib import Path
import os
from typing import List, Dict
import tempfile
import shutil
import hashlib

from google.cloud import storage

from ..monitoring.backup_metrics import BackupMetricsManager

logger = logging.getLogger(__name__)

class RestoreManager:
    """
    Manages the restoration of database backups.
    
    This class handles interactions with Google Cloud Storage for backup operations
    and manages the process of restoring backups to a specified target database.
    """
    def __init__(self):
        """
        Initializes the RestoreManager with necessary configurations.
        
        Sets up the Google Cloud Storage client, specifies the backup bucket,
        initializes the metrics manager, and prepares the restore directory.
        """
        self.storage_client = storage.Client()
        self.bucket_name = os.getenv("BACKUP_BUCKET", "secureai-backups")
        self.bucket = self.storage_client.bucket(self.bucket_name)
        self.metrics = BackupMetricsManager()
        self.restore_dir = Path("/app/restore")
        self.restore_dir.mkdir(exist_ok=True) 

    async def list_available_backups(self) -> List[Dict]:
        """Lists all available backups with metadata.
        Returns a list of dictionaries, each containing metadata of a backup.
        """
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
        """
        Restores a specific backup to the target database.

        Downloads the specified backup from Google Cloud Storage, verifies its integrity,
        creates the target database if it does not exist, and then restores the backup.

        Args:
            backup_name (str): The name of the backup file to restore.
            target_db (str): The name of the database to restore the backup to.

        Returns:
            bool: True if the restoration was successful, False otherwise.
        """
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
        """
        Verifies the integrity of a backup file.

        Checks the backup structure and, if a checksum is provided, verifies it against
        the calculated checksum of the file.

        Args:
            backup_file (Path): The path to the backup file.
            expected_checksum (str): The expected checksum of the backup file.

        Returns:
            bool: True if the backup is valid, False otherwise.
        """
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
        """
        Creates a database if it does not exist.

        Uses psql to attempt to create a database. Ignores the error if the database
        already exists.

        Args:
            db_name (str): The name of the database to create.
        """
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
        """
        Verifies the database restoration by checking for the presence of tables.

        Executes a simple query to count the tables in the database. If the query
        is successful, it indicates that the database restoration was likely successful.

        Args:
            db_name (str): The name of the restored database.
        Returns:
            bool: True if restoration verification is successful, False otherwise.
        """
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
