import pytest
import asyncio
from pathlib import Path
import os
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch
from ..database.restore_manager import RestoreManager
from ..monitoring.backup_metrics import BackupMetricsManager

@pytest.fixture
async def restore_manager():
    manager = RestoreManager()
    # Create test backup directory
    manager.restore_dir = Path(tempfile.mkdtemp())
    yield manager
    # Cleanup
    if manager.restore_dir.exists():
        import shutil
        shutil.rmtree(manager.restore_dir)

@pytest.fixture
def mock_storage_client():
    with patch('google.cloud.storage.Client') as mock_client:
        bucket_mock = Mock()
        blob_mock = Mock()
        blob_mock.name = "test_backup.sql.gz"
        blob_mock.size = 1024
        blob_mock.time_created = datetime.now()
        blob_mock.metadata = {'checksum': 'test_checksum'}
        bucket_mock.list_blobs.return_value = [blob_mock]
        mock_client.return_value.bucket.return_value = bucket_mock
        yield mock_client

@pytest.mark.asyncio
async def test_list_backups(restore_manager, mock_storage_client):
    """Test listing available backups"""
    backups = await restore_manager.list_available_backups()
    assert len(backups) > 0
    assert 'name' in backups[0]
    assert 'size' in backups[0]
    assert 'created' in backups[0]
    assert 'checksum' in backups[0]

@pytest.mark.asyncio
async def test_verify_backup(restore_manager):
    """Test backup verification"""
    # Create test backup file
    test_file = restore_manager.restore_dir / "test_backup.sql.gz"
    test_file.write_bytes(b"test backup content")

    # Test with valid checksum
    import hashlib
    sha256 = hashlib.sha256()
    sha256.update(b"test backup content")
    valid_checksum = sha256.hexdigest()

    assert await restore_manager._verify_backup(test_file, valid_checksum)

    # Test with invalid checksum
    assert not await restore_manager._verify_backup(test_file, "invalid_checksum")

@pytest.mark.asyncio
async def test_create_database(restore_manager):
    """Test database creation"""
    with patch('asyncio.create_subprocess_exec') as mock_exec:
        process_mock = Mock()
        process_mock.communicate = Mock(return_value=(b"", b""))
        process_mock.returncode = 0
        mock_exec.return_value = process_mock

        await restore_manager._create_database("test_db")
        mock_exec.assert_called_once()

@pytest.mark.asyncio
async def test_verify_restoration(restore_manager):
    """Test restoration verification"""
    with patch('asyncio.create_subprocess_exec') as mock_exec:
        process_mock = Mock()
        process_mock.communicate = Mock(return_value=(b"42", b""))
        process_mock.returncode = 0
        mock_exec.return_value = process_mock

        assert await restore_manager._verify_restoration("test_db")

@pytest.mark.asyncio
async def test_restore_backup(restore_manager, mock_storage_client):
    """Test full backup restoration"""
    with patch('asyncio.create_subprocess_exec') as mock_exec:
        process_mock = Mock()
        process_mock.communicate = Mock(return_value=(b"", b""))
        process_mock.returncode = 0
        mock_exec.return_value = process_mock

        assert await restore_manager.restore_backup("test_backup.sql.gz", "test_db")

@pytest.mark.asyncio
async def test_restore_backup_failure(restore_manager, mock_storage_client):
    """Test backup restoration failure"""
    with patch('asyncio.create_subprocess_exec') as mock_exec:
        process_mock = Mock()
        process_mock.communicate = Mock(return_value=(b"", b"Error"))
        process_mock.returncode = 1
        mock_exec.return_value = process_mock

        assert not await restore_manager.restore_backup("test_backup.sql.gz", "test_db")

@pytest.mark.asyncio
async def test_restore_backup_invalid_backup(restore_manager, mock_storage_client):
    """Test restoration with invalid backup"""
    mock_storage_client.return_value.bucket.return_value.blob.return_value.exists.return_value = False

    assert not await restore_manager.restore_backup("nonexistent_backup.sql.gz", "test_db")

@pytest.mark.asyncio
async def test_restore_backup_verification_failure(restore_manager, mock_storage_client):
    """Test restoration with verification failure"""
    with patch.object(restore_manager, '_verify_backup', return_value=False):
        assert not await restore_manager.restore_backup("test_backup.sql.gz", "test_db")

@pytest.mark.asyncio
async def test_restore_backup_with_metrics(restore_manager, mock_storage_client):
    """Test backup restoration with metrics recording"""
    with patch('asyncio.create_subprocess_exec') as mock_exec, \
         patch.object(BackupMetricsManager, 'record_restore_completion') as mock_metrics:
        process_mock = Mock()
        process_mock.communicate = Mock(return_value=(b"", b""))
        process_mock.returncode = 0
        mock_exec.return_value = process_mock

        await restore_manager.restore_backup("test_backup.sql.gz", "test_db")
        mock_metrics.assert_called_once()
