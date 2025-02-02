import pytest
from src.monitoring.system import SystemMonitor
from src.monitoring.metrics_detail import MetricsDetail
import asyncio

@pytest.fixture
async def system_monitor():
    monitor = SystemMonitor()
    yield monitor

@pytest.fixture
async def metrics_detail():
    metrics = MetricsDetail()
    yield metrics

@pytest.mark.asyncio
async def test_system_metrics_collection(system_monitor):
    metrics = await system_monitor.collect_system_metrics()
    assert 'cpu_usage' in metrics
    assert 'memory_usage' in metrics
    assert 'disk_usage' in metrics
    assert all(isinstance(v, (int, float)) for v in metrics.values())

@pytest.mark.asyncio
async def test_health_check(system_monitor):
    health = await system_monitor.check_health()
    assert 'status' in health
    assert 'timestamp' in health
    assert 'metrics' in health
    assert 'alerts' in health

@pytest.mark.asyncio
async def test_alert_thresholds(system_monitor):
    new_thresholds = {
        'cpu_usage': 90.0,
        'memory_usage': 95.0
    }
    system_monitor.update_alert_thresholds(new_thresholds)
    assert system_monitor.alert_thresholds['cpu_usage'] == 90.0
    assert system_monitor.alert_thresholds['memory_usage'] == 95.0

@pytest.mark.asyncio
async def test_metrics_history_retention(metrics_detail):
    await metrics_detail.collect_detailed_metrics()
    assert len(metrics_detail.metrics_history['system']) > 0
    assert len(metrics_detail.metrics_history['application']) > 0
