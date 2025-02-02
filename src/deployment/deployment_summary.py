import logging
from datetime import datetime
from typing import Dict, Any
from src.notifications.deployment_notifier import notifier
from src.scripts.rollback_manager import rollback_manager

logger = logging.getLogger(__name__)

class DeploymentSummary:
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.status = {
            'version': os.getenv('VERSION', 'latest'),
            'environment': os.getenv('ENVIRONMENT', 'production'),
            'stages': {},
            'overall_status': 'pending'
        }

    async def record_stage(self, stage: str, status: str, details: Dict[str, Any] = None):
        """Record deployment stage status"""
        self.status['stages'][stage] = {
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details or {}
        }

        # Send notification
        await notifier.notify_deployment_status({
            'stage': stage,
            'status': status,
            'details': details,
            'environment': self.status['environment']
        })

    def get_summary(self) -> Dict[str, Any]:
        """Get deployment summary"""
        return {
            'version': self.status['version'],
            'environment': self.status['environment'],
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.utcnow().isoformat(),
            'stages': self.status['stages'],
            'overall_status': self.status['overall_status']
        }

deployment_summary = DeploymentSummary()
