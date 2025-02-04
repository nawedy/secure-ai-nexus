"""
Tests for Incident Response Procedures Implementation
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from docs.incident_response.incident_response_procedures import (
    IncidentResponseProcedures,
    SecurityIncident,
    IncidentResponse
)

@pytest.fixture
def incident_proc():
    """Create IncidentResponseProcedures instance for testing"""
    return IncidentResponseProcedures()

@pytest.fixture
def mock_monitor():
    """Mock incident monitor"""
    return Mock()

@pytest.fixture
def mock_handler():
    """Mock incident handler"""
    return Mock()

@pytest.fixture
def mock_forensics():
    """Mock forensics engine"""
    return Mock()

@pytest.fixture
def sample_security_incident():
    """Create sample security incident for testing"""
    return SecurityIncident(
        id="INC-001",
        type="INTRUSION_ATTEMPT",
        severity="HIGH",
        timestamp=datetime.utcnow(),
        source="external_ip",
        affected_assets=["web_server", "database"],
        indicators=[
            {"type": "ip", "value": "10.0.0.1"},
            {"type": "signature", "value": "SQL_INJECTION"}
        ],
        status="NEW",
        priority="P1"
    )

@pytest.mark.asyncio
async def test_handle_incident(
    incident_proc,
    mock_handler,
    sample_security_incident
):
    """Test incident handling"""
    with patch.object(incident_proc, 'handler', mock_handler):
        result = await incident_proc.handle_incident(sample_security_incident)

        assert isinstance(result, IncidentResponse)
        assert result.success is True
        assert result.incident == sample_security_incident
        assert result.start_time < result.end_time
        assert len(result.response_actions) > 0

@pytest.mark.asyncio
async def test_perform_incident_triage(
    incident_proc,
    sample_security_incident
):
    """Test incident triage"""
    triage_result = await incident_proc.perform_incident_triage(sample_security_incident)

    assert "severity" in triage_result
    assert "impact" in triage_result
    assert "scope" in triage_result
    assert "priority" in triage_result
    assert isinstance(triage_result["timestamp"], datetime)

@pytest.mark.asyncio
async def test_collect_forensics_data(
    incident_proc,
    mock_forensics,
    sample_security_incident
):
    """Test forensics data collection"""
    with patch.object(incident_proc, 'forensics', mock_forensics):
        forensics_data = await incident_proc.collect_forensics_data(sample_security_incident)

        assert "logs" in forensics_data
        assert "network_data" in forensics_data
        assert "memory_dumps" in forensics_data
        assert "artifacts" in forensics_data
        assert "analysis" in forensics_data

@pytest.mark.asyncio
async def test_execute_containment_actions(incident_proc):
    """Test containment action execution"""
    plan = {
        "containment_actions": [
            {
                "type": "BLOCK_IP",
                "target": "10.0.0.1",
                "priority": "high"
            },
            {
                "type": "ISOLATE_SYSTEM",
                "target": "web_server",
                "priority": "high"
            }
        ]
    }

    result = await incident_proc.execute_containment_actions(plan)

    assert result["status"] in ["contained", "partial"]
    assert "actions" in result
    assert isinstance(result["timestamp"], datetime)

@pytest.mark.asyncio
async def test_monitor_incident_status(
    incident_proc,
    mock_monitor
):
    """Test incident status monitoring"""
    incident_id = "INC-001"

    mock_monitor.get_incident_metrics.return_value = {
        "containment_status": "contained",
        "response_time": 300,
        "actions_completed": 5
    }

    with patch.object(incident_proc, 'monitor', mock_monitor):
        status = await incident_proc.monitor_incident_status(incident_id)

        assert status["incident_id"] == incident_id
        assert "status" in status
        assert "metrics" in status
        assert "effectiveness" in status
        assert "recommendations" in status

@pytest.mark.asyncio
async def test_incident_handling_failure(
    incident_proc,
    sample_security_incident
):
    """Test incident handling failure scenarios"""
    error = Exception("Failed to contain threat")

    with pytest.raises(Exception):
        with patch.object(incident_proc, 'execute_containment_actions',
                         side_effect=error):
            await incident_proc.handle_incident(sample_security_incident)

    # Verify error handling
    assert incident_proc.logger.critical.called
    assert incident_proc.notifier.notify_security_team.called
