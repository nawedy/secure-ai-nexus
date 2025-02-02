#!/usr/bin/env python3
import pytest
import asyncio
from pathlib import Path
import json
from scripts.test_environment import EnvironmentTester
from scripts.auto_dependency_update import DependencyUpdater
from scripts.environment_migration import EnvironmentMigration

@pytest.fixture
async def env_tester():
    return EnvironmentTester()

@pytest.fixture
async def dep_updater():
    return DependencyUpdater()

@pytest.fixture
async def env_migration():
    return EnvironmentMigration()

@pytest.mark.asyncio
async def test_environment_testing(env_tester):
    """Test environment testing functionality"""
    results = await env_tester.run_all_tests()
    assert isinstance(results, dict)
    assert 'system' in results
    assert 'python' in results
    assert 'dependencies' in results

@pytest.mark.asyncio
async def test_dependency_updates(dep_updater):
    """Test dependency update functionality"""
    updates = await dep_updater.check_updates()
    assert isinstance(updates, dict)
    assert 'major' in updates
    assert 'minor' in updates
    assert 'patch' in updates

@pytest.mark.asyncio
async def test_environment_migration(env_migration):
    """Test environment migration functionality"""
    test_name = "test_migration"
    await env_migration.create_migration(test_name)

    migration = env_migration._find_migration(test_name)
    assert migration is not None
    assert (migration / 'state.json').exists()

@pytest.mark.asyncio
async def test_snapshot_functionality(env_tester):
    """Test environment snapshot functionality"""
    env_tester.create_environment_snapshot()
    differences = env_tester.verify_against_snapshot()
    assert isinstance(differences, list)

@pytest.mark.asyncio
async def test_backup_restore(dep_updater):
    """Test backup and restore functionality"""
    await dep_updater._backup_requirements()
    backup_file = Path('requirements.txt.bak')
    assert backup_file.exists()
