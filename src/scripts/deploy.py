import asyncio
import logging
import subprocess
import os
from typing import Dict, List
from .pre_deployment_check import PreDeploymentCheck

logger = logging.getLogger(__name__)

class Deployment:
    def __init__(self):
        self.pre_deployment = PreDeploymentCheck()
        self.environment = os.getenv('ENVIRONMENT', 'production')
        self.version = os.getenv('VERSION', 'latest')

    async def run_deployment(self) -> bool:
        """Run the complete deployment process"""
        try:
            # 1. Run pre-deployment checks
            check_results = await self.pre_deployment.run_all_checks()
            if not all(result.get('passed', False) for result in check_results.values()):
                logger.error("Pre-deployment checks failed")
                return False

            # 2. Backup current state
            if not await self._backup_current_state():
                return False

            # 3. Deploy new version
            if not await self._deploy_new_version():
                return False

            # 4. Run post-deployment verification
            if not await self._verify_deployment():
                await self._rollback()
                return False

            logger.info("Deployment completed successfully")
            return True

        except Exception as e:
            logger.error(f"Deployment failed: {str(e)}")
            await self._rollback()
            return False

    async def _backup_current_state(self) -> bool:
        """Create backup of current state"""
        try:
            # Backup database
            subprocess.run(["pg_dump", "-Fc", "secureai_db", ">", "backup.dump"], check=True)

            # Backup configurations
            subprocess.run(["tar", "-czf", "config_backup.tar.gz", "config/"], check=True)

            return True
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            return False

    async def _deploy_new_version(self) -> bool:
        """Deploy new version of the application"""
        try:
            # Update Kubernetes deployments
            subprocess.run([
                "kubectl", "apply", "-f", "k8s/",
                "--namespace", self.environment
            ], check=True)

            # Wait for rollout
            subprocess.run([
                "kubectl", "rollout", "status", "deployment/secureai-platform",
                "--namespace", self.environment
            ], check=True)

            return True
        except Exception as e:
            logger.error(f"Deployment failed: {str(e)}")
            return False

    async def _verify_deployment(self) -> bool:
        """Verify the new deployment"""
        try:
            # Check pod status
            result = subprocess.run([
                "kubectl", "get", "pods",
                "--namespace", self.environment,
                "-l", "app=secureai-platform",
                "-o", "jsonpath='{.items[*].status.phase}'"
            ], capture_output=True, text=True, check=True)

            if "Running" not in result.stdout:
                return False

            # Run health checks
            health_check = await self.pre_deployment._check_system()
            return health_check.get('passed', False)

        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            return False

    async def _rollback(self):
        """Rollback to previous version"""
        try:
            logger.info("Initiating rollback...")

            # Restore database
            subprocess.run(["pg_restore", "-d", "secureai_db", "backup.dump"], check=True)

            # Restore configurations
            subprocess.run(["tar", "-xzf", "config_backup.tar.gz"], check=True)

            # Rollback Kubernetes deployment
            subprocess.run([
                "kubectl", "rollout", "undo", "deployment/secureai-platform",
                "--namespace", self.environment
            ], check=True)

            logger.info("Rollback completed successfully")
        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
            raise

async def main():
    deployment = Deployment()
    success = await deployment.run_deployment()
    if success:
        print("✅ Deployment completed successfully")
    else:
        print("❌ Deployment failed")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
