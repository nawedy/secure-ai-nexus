import pytest
import asyncio
from src.security.response.automated_response_engine import AutomatedResponseEngine

@pytest.mark.asyncio
async def test_automated_response_engine_execute_response():
    engine = AutomatedResponseEngine()
    incident = {"type": "login_attempt", "user": "testuser"}

    result = await engine.executeResponse(incident)

    assert "success" in result
    assert "actions" in result
    assert "metrics" in result
    assert "recommendations" in result

@pytest.mark.asyncio
async def test_automated_response_engine_execute_response_wrong_data():
    engine = AutomatedResponseEngine()
    incident = "wrong data"
    with pytest.raises(AttributeError):
        await engine.executeResponse(incident)