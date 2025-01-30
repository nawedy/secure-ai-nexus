from typing import Dict, List, Optional
from pydantic import BaseModel
import logging
from azure.monitor.alert import AlertClient
from azure.identity import DefaultAzureCredential

logger = logging.getLogger(__name__)

class AlertConfig(BaseModel):
    name: str
    description: str
    severity: int  # 0-4, 0 being most critical
    threshold: float
    window_size: str  # e.g., "5m", "1h"
    condition: str  # e.g., "above", "below"
    metric_name: str

class AlertManager:
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.alert_client = AlertClient(credential=self.credential)

        # Default alert configurations
        self.default_alerts = [
            AlertConfig(
                name="high_error_rate",
                description="High error rate detected",
                severity=1,
                threshold=0.05,  # 5% error rate
                window_size="5m",
                condition="above",
                metric_name="error_rate"
            ),
            AlertConfig(
                name="auth_failures",
                description="Multiple authentication failures",
                severity=1,
                threshold=10,  # 10 failures
                window_size="5m",
                condition="above",
                metric_name="failed_auth_attempts"
            ),
            AlertConfig(
                name="high_latency",
                description="High request latency",
                severity=2,
                threshold=1.0,  # 1 second
                window_size="5m",
                condition="above",
                metric_name="request_latency"
            )
        ]

    async def setup_alerts(self):
        """Set up default alerts in Azure Monitor"""
        try:
            for alert_config in self.default_alerts:
                await self.create_alert(alert_config)
            logger.info("Default alerts configured successfully")
        except Exception as e:
            logger.error(f"Failed to set up alerts: {str(e)}")
            raise

    async def create_alert(self, config: AlertConfig):
        """Create a new alert rule"""
        try:
            await self.alert_client.alert_rules.create_or_update(
                resource_group_name="secureai-rg",
                service_name="secureai-app",
                rule_name=config.name,
                parameters={
                    "location": "eastus",
                    "properties": {
                        "description": config.description,
                        "severity": config.severity,
                        "enabled": True,
                        "evaluationFrequency": "PT1M",
                        "windowSize": config.window_size,
                        "criteria": {
                            "metricName": config.metric_name,
                            "operator": config.condition,
                            "threshold": config.threshold,
                            "timeAggregation": "Average"
                        }
                    }
                }
            )
            logger.info(f"Alert rule {config.name} created successfully")
        except Exception as e:
            logger.error(f"Failed to create alert rule {config.name}: {str(e)}")
            raise
