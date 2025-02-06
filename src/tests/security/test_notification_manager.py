import pytest
import asyncio
from src.security.reporting.notification_manager import NotificationManager

@pytest.mark.asyncio
async def test_notification_manager_send_alerts():
    manager = NotificationManager()
    config = {
        "channels": [
            {"type": "pagerduty", "priority": "P1"},
            {"type": "slack", "channel": "security-alerts"},
            {"type": "email", "to": "test@test.com"},
            {"type": "sms", "to": "+11111111"},
            {"type": "teams", "channel": "Security Alerts"},
        ],
        "event": {"type": "login_attempt", "user": "testuser"},
        "risk": "high"
    }

    result = await manager.sendAlerts(config)

    assert "successful" in result
    assert "failed" in result
    assert "deliveryMetrics" in result

@pytest.mark.asyncio
async def test_notification_manager_send_alerts_wrong_data():
    manager = NotificationManager()
    config = "wrong data"
    with pytest.raises(AttributeError):
        await manager.sendAlerts(config)