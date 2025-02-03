import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch
from ...cli.restore_cli import cli, main
from ...database.restore_manager import RestoreManager
from datetime import datetime

@pytest.fixture
def cli_runner():
    return CliRunner()

@pytest.fixture
def mock_restore_manager():
    with patch('src.database.restore_manager.RestoreManager') as mock:
        instance = Mock()
        mock.return_value = instance
        yield instance

@pytest.mark.asyncio
async def test_list_backups(cli_runner, mock_restore_manager):
    """Test listing backups"""
    mock_restore_manager.list_available_backups.return_value = [
        {
            'name': 'backup1.sql.gz',
            'size': 1024 * 1024,  # 1MB
            'created': datetime.now(),
            'checksum': 'test_checksum'
        }
    ]

    result = await cli_runner.invoke(cli, ['list-backups'])
    assert result.exit_code == 0
    assert 'backup1.sql.gz' in result.output

@pytest.mark.asyncio
async def test_restore_command(cli_runner, mock_restore_manager):
    """Test restore command"""
    mock_restore_manager.restore_backup.return_value = True
    mock_restore_manager._verify_restoration.return_value = True

    result = await cli_runner.invoke(cli, ['restore', 'backup1.sql.gz', 'test_db'])
    assert result.exit_code == 0
    assert 'completed successfully' in result.output

@pytest.mark.asyncio
async def test_restore_failure(cli_runner, mock_restore_manager):
    """Test restore failure"""
    mock_restore_manager.restore_backup.return_value = False

    result = await cli_runner.invoke(cli, ['restore', 'backup1.sql.gz', 'test_db'])
    assert result.exit_code == 1
    assert 'failed' in result.output

@pytest.mark.asyncio
async def test_verify_command(cli_runner, mock_restore_manager):
    """Test verify command"""
    mock_restore_manager._verify_backup.return_value = True

    result = await cli_runner.invoke(cli, ['verify', 'backup1.sql.gz'])
    assert result.exit_code == 0
    assert 'successful' in result.output

@pytest.mark.asyncio
async def test_status_command(cli_runner):
    """Test status command"""
    with patch('src.monitoring.restore_metrics.RestoreMetricsManager') as mock:
        instance = Mock()
        instance.get_restore_stats.return_value = {
            'in_progress': 0,
            'total_success': 10,
            'total_failure': 1,
            'verification_success': 9,
            'verification_failure': 1
        }
        mock.return_value = instance

        result = await cli_runner.invoke(cli, ['status'])
        assert result.exit_code == 0
        assert 'Total Success' in result.output
