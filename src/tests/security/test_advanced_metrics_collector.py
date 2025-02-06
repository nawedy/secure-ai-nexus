import pytest
import asyncio
from src.security.monitoring.advanced_metrics_collector import AdvancedMetricsCollector, SecurityContext

@pytest.mark.asyncio
async def test_advanced_metrics_collector_collect_metrics():
    collector = AdvancedMetricsCollector()
    context = {"user": "testuser", "timestamp": "2023-01-01T00:00:00Z"}

    result = await collector.collectMetrics(context)

    assert "raw" in result
    assert "enriched" in result
    assert "analysis" in result
    assert "insights" in result

@pytest.mark.asyncio
async def test_advanced_metrics_collector_collect_metrics_wrong_data():
    collector = AdvancedMetricsCollector()
    context = ["wrong data"]
    
    with pytest.raises(AttributeError):
        result = await collector.collectMetrics(context)

@pytest.mark.asyncio
async def test_advanced_metrics_collector_generate_dashboards():
    collector = AdvancedMetricsCollector()
    metrics = {
        "raw": [],
        "enriched": [],
        "analysis": {},
        "insights": []
    }
    result = await collector.generateDashboards(metrics)

    assert "overview" in result
    assert "detailed" in result
    assert "trends" in result
    assert "alerts" in result