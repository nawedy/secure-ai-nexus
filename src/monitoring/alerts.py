"""
This module defines the AlertManager class and related configurations for setting up
alerts in Azure Monitor. It includes functionalities to create and manage alerts
based on predefined configurations.
"""


from pydantic import BaseModel
import logging
from azure.monitor.alert import AlertClient
from azure.identity import DefaultAzureCredential

logger = logging.getLogger(__name__)


class AlertConfig(BaseModel):
    """
    Represents the configuration for a single alert.

    Attributes:
        name (str): The name of the alert.
        description (str): A brief description of the alert.
        severity (int): The severity level of the alert (0-4, 0 being most critical).
        threshold (float): The threshold value for triggering the alert.
        window_size (str): The time window for evaluating the alert condition (e.g., "5m", "1h").
        condition (str): The condition to trigger the alert (e.g., "above", "below").
        metric_name (str): The name of the metric being monitored.
    """
    name: str
    description: str
    severity: int  # 0-4, 0 being most critical
    threshold: float
    window_size: str  # e.g., "5m", "1h"
    condition: str  # e.g., "above", "below"
    metric_name: str


class AlertManager:
    """
    Manages the creation and setup of alerts in Azure Monitor.

    This class handles the interaction with Azure Monitor to create and configure alert rules.
    """
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
        """
        Sets up the default alerts in Azure Monitor.

        This method iterates through the `default_alerts` configurations and attempts to create each alert rule
        in Azure Monitor.

        Raises:
            Exception: If any error occurs during the alert setup process.
        """
        try:
            for alert_config in self.default_alerts:
                await self.create_alert(alert_config)
            logger.info("Default alerts configured successfully")
        except Exception as e:
            logger.error(f"Failed to set up alerts: {str(e)}")
            raise

    async def create_alert(self, config: AlertConfig):
        """
        Creates a new alert rule in Azure Monitor based on the provided configuration.

        Args:
            config (AlertConfig): The configuration for the alert rule to be created.

        Raises:
            Exception: If any error occurs during the creation of the alert rule.

        """
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
