import pytest
import asyncio
from src.security.reporting.advanced_reporting_engine import SecurityReportingEngine, RiskLevel

@pytest.mark.asyncio
async def test_security_reporting_engine_generate_security_report():
    engine = SecurityReportingEngine()
    config = {
        "format": "pdf",
        "period": "daily",
        "detailLevel": "high",
        "distribution": "email"
    }

    result = await engine.generateSecurityReport(config)

    assert isinstance(result, dict)

@pytest.mark.asyncio
async def test_security_reporting_engine_generate_security_report_wrong_data():
    engine = SecurityReportingEngine()
    config = "wrong data"
    with pytest.raises(AttributeError):
        result = await engine.generateSecurityReport(config)


@pytest.mark.asyncio
async def test_security_reporting_engine_process_security_event():
    engine = SecurityReportingEngine()
    event = {"type": "login_attempt", "user": "testuser"}

    await engine.processSecurityEvent(event)

@pytest.mark.asyncio
async def test_security_reporting_engine_process_security_event_wrong_data():
    engine = SecurityReportingEngine()
    event = "wrong data"
    with pytest.raises(AttributeError):
        await engine.processSecurityEvent(event)