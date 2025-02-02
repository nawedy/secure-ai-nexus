#!/usr/bin/env python3
import logging
from pathlib import Path
import json
from typing import Dict, List
import asyncio
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import requests

logger = logging.getLogger(__name__)

class AlertManager:
    """Advanced alerting system"""

    def __init__(self):
        self.alert_config = self._load_alert_config()
        self.alert_history = Path('alerts/history.json')
        self.alert_rules = self._load_alert_rules()
        self.notification_channels = {
            'email': self._send_email_alert,
            'slack': self._send_slack_alert,
            'pagerduty': self._send_pagerduty_alert
        }

    async def monitor_and_alert(self):
        """Main alert monitoring loop"""
        while True:
            try:
                # Check all alert conditions
                alerts = await self._check_alert_conditions()

                # Process and send alerts
                for alert in alerts:
                    await self._process_alert(alert)

                # Update alert history
                await self._update_alert_history(alerts)

                await asyncio.sleep(self.alert_config['check_interval'])

            except Exception as e:
                logger.error(f"Alert monitoring failed: {str(e)}")

    async def _check_alert_conditions(self) -> List[Dict]:
        """Check all alert conditions"""
        alerts = []

        # Check system metrics
        system_alerts = await self._check_system_metrics()
        alerts.extend(system_alerts)

        # Check security conditions
        security_alerts = await self._check_security_conditions()
        alerts.extend(security_alerts)

        # Check model performance
        model_alerts = await self._check_model_performance()
        alerts.extend(model_alerts)

        return alerts

    async def _process_alert(self, alert: Dict):
        """Process and send alert"""
        try:
            # Determine alert severity
            severity = self._determine_severity(alert)

            # Get notification channels for severity
            channels = self.alert_config['severity_channels'][severity]

            # Send notifications
            for channel in channels:
                await self.notification_channels[channel](alert)

            # Log alert
            logger.info(f"Alert sent: {alert['message']} (Severity: {severity})")

        except Exception as e:
            logger.error(f"Alert processing failed: {str(e)}")

    async def _send_email_alert(self, alert: Dict):
        """Send email alert"""
        try:
            msg = MIMEText(self._format_alert_message(alert))
            msg['Subject'] = f"Alert: {alert['type']} - {alert['severity']}"
            msg['From'] = self.alert_config['email']['sender']
            msg['To'] = self.alert_config['email']['recipients']

            with smtplib.SMTP(self.alert_config['email']['smtp_server']) as server:
                server.send_message(msg)

        except Exception as e:
            logger.error(f"Email alert failed: {str(e)}")

    def _determine_severity(self, alert: Dict) -> str:
        """Determine alert severity"""
        if alert['type'] == 'security':
            return 'critical'
        elif alert['type'] == 'performance' and alert['value'] > 90:
            return 'high'
        elif alert['type'] == 'model' and alert['accuracy'] < 0.8:
            return 'medium'
        return 'low'

if __name__ == "__main__":
    alert_manager = AlertManager()
    asyncio.run(alert_manager.monitor_and_alert())
