import pytest
import asyncio
import os
from ...database.restore_manager import RestoreManager
from ...monitoring.backup_metrics import BackupMetricsManager

@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_restore_flow():
    """Test complete restore flow with actual database"""
    if not os.getenv("INTEGRATION_TESTS"):
        pytest.skip("Integration tests not enabled")

    restore_manager = RestoreManager()

    # List available backups
    backups = await restore_manager.list_available_backups()
    assert len(backups) > 0

    # Attempt restore
    latest_backup = backups[0]['name']
    test_db = f"test_restore_{int(datetime.now().timestamp())}"

    success = await restore_manager.restore_backup(latest_backup, test_db)
    assert success

    # Verify database exists and has tables
    assert await restore_manager._verify_restoration(test_db)

    # Cleanup test database
    await restore_manager._drop_database(test_db)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_restore_performance():
    """Test restore performance with metrics"""
    if not os.getenv("INTEGRATION_TESTS"):
        pytest.skip("Integration tests not enabled")

    restore_manager = RestoreManager()
    metrics_manager = BackupMetricsManager()

    backups = await restore_manager.list_available_backups()
    assert len(backups) > 0

    # Test restore time
    start_time = time.time()
    latest_backup = backups[0]['name']
    test_db = f"test_restore_perf_{int(datetime.now().timestamp())}"

    await restore_manager.restore_backup(latest_backup, test_db)

    duration = time.time() - start_time
    assert duration < 300  # Should complete within 5 minutes

    # Cleanup
    await restore_manager._drop_database(test_db)
