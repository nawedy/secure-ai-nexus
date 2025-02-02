#!/usr/bin/env python3
import pytest
import asyncio
from pathlib import Path
import json
from scripts.test_environment import EnvironmentTester
from scripts.auto_dependency_update import DependencyUpdater
from scripts.environment_migration import EnvironmentMigration
from src.monitoring.environment_monitor import EnvironmentMonitor

class IntegrationTestSuite:
    """Comprehensive integration testing suite"""

    def __init__(self):
        self.env_tester = EnvironmentTester()
        self.dep_updater = DependencyUpdater()
        self.env_migration = EnvironmentMigration()
        self.env_monitor = EnvironmentMonitor()
        self.test_results = {}

    async def run_full_integration_test(self):
        """Run complete integration test suite"""
        try:
            # Test environment setup and validation
            await self._test_environment_setup()

            # Test dependency management
            await self._test_dependency_workflow()

            # Test migration process
            await self._test_migration_workflow()

            # Test monitoring integration
            await self._test_monitoring_integration()

            return self.test_results
        except Exception as e:
            logger.error(f"Integration test failed: {str(e)}")
            raise

    async def _test_environment_setup(self):
        """Test complete environment setup process"""
        # Environment validation
        env_results = await self.env_tester.run_all_tests()
        assert all(all(r.values()) for r in env_results.values())

        # Snapshot creation and verification
        self.env_tester.create_environment_snapshot()
        differences = self.env_tester.verify_against_snapshot()
        assert len(differences) == 0

    async def _test_dependency_workflow(self):
        """Test dependency management workflow"""
        # Check for updates
        updates = await self.dep_updater.check_updates()

        # Test backup creation
        await self.dep_updater._backup_requirements()
        assert Path('requirements.txt.bak').exists()

        # Test update process
        if updates['patch']:
            await self.dep_updater.auto_update('patch')
            # Verify environment still valid
            env_results = await self.env_tester.run_all_tests()
            assert all(all(r.values()) for r in env_results.values())

    async def _test_migration_workflow(self):
        """Test complete migration workflow"""
        test_name = "integration_test_migration"

        # Create migration
        await self.env_migration.create_migration(test_name)

        # Verify migration created
        migration = self.env_migration._find_migration(test_name)
        assert migration is not None
        assert (migration / 'state.json').exists()

        # Test migration apply
        await self.env_migration.apply_migration(test_name)

        # Verify environment after migration
        env_results = await self.env_tester.run_all_tests()
        assert all(all(r.values()) for r in env_results.values())

    async def _test_monitoring_integration(self):
        """Test monitoring system integration"""
        # Start monitoring
        monitor_task = asyncio.create_task(
            self.env_monitor.start_monitoring()
        )

        # Make some environment changes
        await self.dep_updater._backup_requirements()

        # Wait for monitoring to detect changes
        await asyncio.sleep(2)

        # Verify changes detected
        assert self.env_monitor.history_file.exists()
        history = json.loads(self.env_monitor.history_file.read_text())
        assert len(history) > 0

        # Clean up
        monitor_task.cancel()

@pytest.mark.asyncio
async def test_full_integration():
    """Run full integration test suite"""
    suite = IntegrationTestSuite()
    results = await suite.run_full_integration_test()
    assert results is not None
