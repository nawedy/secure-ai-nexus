import pytest
import asyncio
from src.security.response.playbook_version_control import PlaybookVersionControl

@pytest.mark.asyncio
async def test_playbook_version_control_create_version():
    version_control = PlaybookVersionControl()
    playbook = {
        "id": "playbook1"
    }
    changes = {
        "description": "some changes"
    }

    result = await version_control.createVersion(playbook, changes)

    assert "version" in result
    assert "impact" in result
    assert "documentation" in result
    assert "recommendations" in result

@pytest.mark.asyncio
async def test_playbook_version_control_manage_branches_create():
    version_control = PlaybookVersionControl()
    operation = {
      "type": "create"
    }

    result = await version_control.manageBranches(operation)

@pytest.mark.asyncio
async def test_playbook_version_control_manage_branches_merge():
    version_control = PlaybookVersionControl()
    operation = {
      "type": "merge"
    }

    result = await version_control.manageBranches(operation)

@pytest.mark.asyncio
async def test_playbook_version_control_manage_branches_delete():
    version_control = PlaybookVersionControl()
    operation = {
      "type": "delete"
    }

    result = await version_control.manageBranches(operation)

@pytest.mark.asyncio
async def test_playbook_version_control_manage_branches_unknown():
    version_control = PlaybookVersionControl()
    operation = {
      "type": "unknown"
    }

    result = await version_control.manageBranches(operation)