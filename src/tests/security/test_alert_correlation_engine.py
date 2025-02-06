import pytest
import asyncio
from src.security.alerts.alert_correlation_engine import AlertCorrelationEngine, SecurityAlert

@pytest.mark.asyncio
async def test_alert_correlation_engine_correlate_alerts():
    engine = AlertCorrelationEngine()
    alerts = [
        {"id": "alert1", "type": "login_attempt", "timestamp": "2023-01-01T00:00:00Z"},
        {"id": "alert2", "type": "failed_login", "timestamp": "2023-01-01T00:00:30Z"},
        {"id": "alert3", "type": "successful_login", "timestamp": "2023-01-01T00:01:00Z"},
    ]

    result = await engine.correlateAlerts(alerts)

    assert "correlatedGroups" in result
    assert "attackChains" in result
    assert "riskAssessment" in result
    assert "recommendations" in result
    assert "mitigationPlan" in result

@pytest.mark.asyncio
async def test_alert_correlation_engine_correlate_alerts_empty():
    engine = AlertCorrelationEngine()
    alerts = []

    result = await engine.correlateAlerts(alerts)

    assert "correlatedGroups" in result
    assert "attackChains" in result
    assert "riskAssessment" in result
    assert "recommendations" in result
    assert "mitigationPlan" in result

@pytest.mark.asyncio
async def test_alert_correlation_engine_correlate_alerts_wrong_data():
    engine = AlertCorrelationEngine()
    alerts = ["wrong data"]

    with pytest.raises(AttributeError):
        result = await engine.correlateAlerts(alerts)