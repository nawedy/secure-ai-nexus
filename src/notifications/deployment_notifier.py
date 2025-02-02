import logging
import aiohttp
import json
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class DeploymentNotifier:
    """Handles deployment notifications across multiple channels"""

    def __init__(self):
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        self.teams_webhook = os.getenv('TEAMS_WEBHOOK_URL')
        self.email_config = {
            'smtp_server': os.getenv('SMTP_SERVER'),
            'smtp_port': int(os.getenv('SMTP_PORT', 587)),
            'sender': os.getenv('SMTP_SENDER'),
            'recipients': os.getenv('NOTIFICATION_RECIPIENTS', '').split(',')
        }

    async def notify_deployment_status(self, status: Dict[str, Any]):
        """Send deployment status notifications"""
        try:
            message = self._format_message(status)
            await asyncio.gather(
                self._send_slack_notification(message),
                self._send_teams_notification(message),
                self._send_email_notification(message)
            )
            logger.info(f"Deployment notifications sent successfully: {status['stage']}")
        except Exception as e:
            logger.error(f"Failed to send deployment notifications: {str(e)}")

    async def _send_slack_notification(self, message: Dict):
        """Send notification to Slack"""
        if not self.slack_webhook:
            return

        async with aiohttp.ClientSession() as session:
            await session.post(
                self.slack_webhook,
                json={
                    "text": message['summary'],
                    "blocks": [
                        {
                            "type": "section",
                            "text": {"type": "mrkdwn", "text": message['details']}
                        }
                    ]
                }
            )

    def _format_message(self, status: Dict[str, Any]) -> Dict[str, str]:
        """Format notification message"""
        emoji = "✅" if status.get('success') else "❌"
        return {
            'summary': f"{emoji} Deployment {status['stage']}: {status['status']}",
            'details': f"""
*Deployment Update*
• Stage: {status['stage']}
• Status: {status['status']}
• Environment: {status.get('environment', 'production')}
• Timestamp: {datetime.utcnow().isoformat()}
• Details: {status.get('details', 'No additional details')}
"""
        }

notifier = DeploymentNotifier()
