#!/usr/bin/env python3
import pytest
import asyncio
from unittest.mock import Mock, patch
from src.monitoring.auto_remediation import AutoRemediation
from src.monitoring.predictive_analytics import PredictiveAnalytics
from src.monitoring.compliance_reporting import ComplianceReporting
from src.monitoring.advanced_monitoring import AdvancedMonitoring
from src.config.config_manager import ConfigurationManager

class SystemIntegrationTest:
    """System-wide integration testing"""

    @pytest.fixture
    async def system_components(self):
        """Initialize all system components"""
        config = ConfigurationManager()
        await config.load_configuration()

        return {
            'remediation': AutoRemediation(),
            'analytics': PredictiveAnalytics(),
            'compliance': ComplianceReporting(),
            'monitoring': AdvancedMonitoring(),
            'config': config
        }

    @pytest.mark.asyncio
    async def test_remediation_monitoring_integration(self, system_components):
        """Test remediation and monitoring integration"""
        remediation = system_components['remediation']
        monitoring = system_components['monitoring']

        # Start monitoring
        monitor_task = asyncio.create_task(monitoring.start_monitoring())

        # Trigger remediation
        with patch('src.monitoring._get_system_metrics') as mock_metrics:
            mock_metrics.return_value = {'cpu_usage': 95}
            await remediation.monitor_and_remediate()

        # Verify monitoring captured remediation
        assert monitoring.remediation_counter._value.get() > 0
        monitor_task.cancel()

    @pytest.mark.asyncio
    async def test_analytics_compliance_integration(self, system_components):
        """Test analytics and compliance integration"""
        analytics = system_components['analytics']
        compliance = system_components['compliance']

        # Generate predictions
        predictions = await analytics.predict_issues()

        # Verify compliance report includes predictions
        report = await compliance.generate_compliance_report()
        assert 'predictions' in report['performance']
        assert len(report['performance']['predictions']) > 0

    @pytest.mark.asyncio
    async def test_config_system_integration(self, system_components):
        """Test configuration changes propagation"""
        config = system_components['config']
        monitoring = system_components['monitoring']

        # Update configuration
        new_config = {'monitoring': {'interval': 30}}
        await config.update_configuration(new_config)

        # Verify monitoring adapted to new config
        assert monitoring.check_interval == 30

    @pytest.mark.asyncio
    async def test_full_system_workflow(self, system_components):
        """Test complete system workflow"""
        try:
            # Start all components
            tasks = []
            for component in system_components.values():
                if hasattr(component, 'start'):
                    tasks.append(asyncio.create_task(component.start()))

            # Simulate system activity
            await self._simulate_system_activity(system_components)

            # Verify system state
            await self._verify_system_state(system_components)

        finally:
            # Cleanup
            for task in tasks:
                task.cancel()

    async def _simulate_system_activity(self, components):
        """Simulate real system activity"""
        # Simulate high CPU usage
        with patch('src.monitoring._get_system_metrics') as mock_metrics:
            mock_metrics.return_value = {'cpu_usage': 95}
            await asyncio.sleep(2)

        # Simulate configuration change
        await components['config'].update_configuration({'test': True})

        # Simulate compliance check
        await components['compliance'].generate_compliance_report()

    async def _verify_system_state(self, components):
        """Verify overall system state"""
        monitoring = components['monitoring']

        # Verify metrics
        assert monitoring.remediation_counter._value.get() > 0
        assert monitoring.prediction_accuracy._value.get() > 0
        assert monitoring.compliance_score._value.get() > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
