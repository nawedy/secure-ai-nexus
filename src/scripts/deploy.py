#!/usr/bin/env python3
import asyncio
from src.deployment.deployment_orchestrator import DeploymentOrchestrator
from src.monitoring.system import system_monitor
from src.notifications.deployment_notifier import notifier
import os

# Ensure the correct project is set
os.environ['GOOGLE_CLOUD_PROJECT'] = 'secureai-nexus'

# Use the project ID in deployment logic
project_id = os.getenv('GCP_PROJECT_ID', 'secureai-nexus')

async def main():
    try:
        # Initialize orchestrator
        orchestrator = DeploymentOrchestrator()

        # Start system monitoring
        await system_monitor.start()

        # Deploy with current version
        deployment_result = await orchestrator.deploy_model(
            model_id='secureai-platform',
            version='1.0.0'
        )

        # Notify stakeholders
        await notifier.notify_deployment_status({
            'status': 'success',
            'details': deployment_result
        })

        return deployment_result

    except Exception as e:
        # Notify deployment failure
        await notifier.notify_deployment_status({
            'status': 'failed',
            'error': str(e)
        })
        raise

if __name__ == "__main__":
    asyncio.run(main())
