import pytest
import asyncio
from src.security.testing.playbook_testing_engine import PlaybookTestingEngine

@pytest.mark.asyncio
async def test_playbook_testing_engine_test_playbook():
    testing_engine = PlaybookTestingEngine()
    playbook = {
        "id": "playbook1"
    }

    result = await testing_engine.testPlaybook(playbook)

    assert "scenarios" in result
    assert "coverage" in result
    assert "validation" in result
    assert "recommendations" in result
    assert "improvements" in result