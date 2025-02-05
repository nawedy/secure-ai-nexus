import pytest
from src.types.security import (
    SecurityEventType,
    SecurityEventSeverity,
    SecurityEvent,
    SecurityAlert,
    SecurityAlertAction,
    SecurityMetrics,
)


def test_security_event_creation():
    event = SecurityEvent(
        id="1",
        type="authentication",
        severity="low",
        timestamp="2023-10-27",
        source="test",
        details="Login attempt",
        status="detected",
    )
    assert event.id == "1"
    assert event.type == "authentication"
    assert event.subtype is None
    assert event.severity == "low"
    assert event.timestamp == "2023-10-27"
    assert event.userId is None
    assert event.sessionId is None
    assert event.source == "test"
    assert event.details == "Login attempt"
    assert event.metadata is None
    assert event.relatedEvents is None
    assert event.ipAddress is None
    assert event.userAgent is None
    assert event.status == "detected"
    assert event.resolution is None


def test_security_alert_creation():
    action = SecurityAlertAction(
        id="1",
        alertId="alert-1",
        type="notification",
        status="pending",
        timestamp="2023-10-27",
        details="Notify admin",
    )
    alert = SecurityAlert(
        id="alert-1",
        eventId="1",
        timestamp="2023-10-27",
        severity="medium",
        status="new",
        description="High number of login attempts",
        actions=[action],
    )
    assert alert.id == "alert-1"
    assert alert.eventId == "1"
    assert alert.timestamp == "2023-10-27"
    assert alert.severity == "medium"
    assert alert.status == "new"
    assert alert.assignedTo is None
    assert alert.description == "High number of login attempts"
    assert len(alert.actions) == 1
    assert alert.metadata is None


def test_security_alert_action_creation():
    action = SecurityAlertAction(
        id="1",
        alertId="alert-1",
        type="notification",
        status="pending",
        timestamp="2023-10-27",
        details="Notify admin",
    )
    assert action.id == "1"
    assert action.alertId == "alert-1"
    assert action.type == "notification"
    assert action.status == "pending"
    assert action.timestamp == "2023-10-27"
    assert action.details == "Notify admin"
    assert action.performedBy is None
    assert action.result is None


def test_security_metrics_creation():
    metrics = SecurityMetrics(
        eventCounts={"authentication": 10, "authorization": 5},
        severityCounts={"low": 5, "medium": 3, "high": 2},
        timeBasedMetrics={"hourly": [1, 2, 3], "daily": [24, 48], "weekly": [100, 200]},
        topSources=[{"source": "source1", "count": 10}, {"source": "source2", "count": 5}],
        responseMetrics={"averageResponseTime": 2.5, "resolutionRate": 0.8, "falsePositiveRate": 0.1}
    )
    assert metrics.eventCounts == {"authentication": 10, "authorization": 5}
    assert metrics.severityCounts == {"low": 5, "medium": 3, "high": 2}
    assert metrics.timeBasedMetrics == {"hourly": [1, 2, 3], "daily": [24, 48], "weekly": [100, 200]}
    assert metrics.topSources == [{"source": "source1", "count": 10}, {"source": "source2", "count": 5}]
    assert metrics.responseMetrics == {"averageResponseTime": 2.5, "resolutionRate": 0.8, "falsePositiveRate": 0.1}


def test_security_event_invalid_type():
    with pytest.raises(ValueError):
        SecurityEvent(
            id="1",
            type="invalid_type",
            severity="low",
            timestamp="2023-10-27",
            source="test",
            details="Login attempt",
            status="detected",
        )


def test_security_event_invalid_severity():
    with pytest.raises(ValueError):
        SecurityEvent(
            id="1",
            type="authentication",
            severity="invalid_severity",
            timestamp="2023-10-27",
            source="test",
            details="Login attempt",
            status="detected",
        )


def test_security_event_invalid_status():
    with pytest.raises(ValueError):
        SecurityEvent(
            id="1",
            type="authentication",
            severity="low",
            timestamp="2023-10-27",
            source="test",
            details="Login attempt",
            status="invalid_status",
        )


def test_security_alert_invalid_status():
    action = SecurityAlertAction(
        id="1",
        alertId="alert-1",
        type="notification",
        status="pending",
        timestamp="2023-10-27",
        details="Notify admin",
    )
    with pytest.raises(ValueError):
        SecurityAlert(
            id="alert-1",
            eventId="1",
            timestamp="2023-10-27",
            severity="medium",
            status="invalid_status",
            description="High number of login attempts",
            actions=[action],
        )

def test_security_alert_action_invalid_type():
    with pytest.raises(ValueError):
        SecurityAlertAction(
            id="1",
            alertId="alert-1",
            type="invalid_type",
            status="pending",
            timestamp="2023-10-27",
            details="Notify admin",
        )

def test_security_alert_action_invalid_status():
    with pytest.raises(ValueError):
        SecurityAlertAction(
            id="1",
            alertId="alert-1",
            type="notification",
            status="invalid_status",
            timestamp="2023-10-27",
            details="Notify admin",
        )