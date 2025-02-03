import logging
import asyncio
import httpx
import sys
from typing import Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)

class DeploymentVerifier:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def verify_deployment(self) -> bool:
        """Run all deployment verification checks"""
        try:
            checks = [
                self.verify_health(),
                self.verify_readiness(),
                self.verify_metrics(),
                self.verify_model_service(),
                self.verify_database()
            ]
            results = await asyncio.gather(*checks, return_exceptions=True)

            failed_checks = [i for i, result in enumerate(results) if isinstance(result, Exception)]
            if failed_checks:
                logger.error(f"Failed checks: {failed_checks}")
                return False

            logger.info("All deployment checks passed")
            return True

        except Exception as e:
            logger.error(f"Deployment verification failed: {str(e)}")
            return False

    async def verify_health(self) -> bool:
        """Verify health endpoint"""
        response = await self.client.get(f"{self.base_url}/health")
        if response.status_code != 200:
            raise Exception("Health check failed")
        return True

    async def verify_readiness(self) -> bool:
        """Verify readiness endpoint"""
        response = await self.client.get(f"{self.base_url}/readiness")
        if response.status_code != 200:
            raise Exception("Readiness check failed")
        return True

    async def verify_metrics(self) -> bool:
        """Verify metrics endpoint"""
        response = await self.client.get(f"{self.base_url}/metrics")
        if response.status_code != 200:
            raise Exception("Metrics endpoint check failed")
        return True

    async def verify_model_service(self) -> bool:
        """Verify model service"""
        response = await self.client.get(f"{self.base_url}/api/models/list")
        if response.status_code != 200:
            raise Exception("Model service check failed")
        return True

    async def verify_database(self) -> bool:
        """Verify database connectivity"""
        response = await self.client.get(f"{self.base_url}/api/health/database")
        if response.status_code != 200:
            raise Exception("Database check failed")
        return True

async def main():
    if len(sys.argv) < 2:
        print("Usage: verify_deployment.py <base_url>")
        sys.exit(1)

    base_url = sys.argv[1]
    verifier = DeploymentVerifier(base_url)

    if await verifier.verify_deployment():
        logger.info("Deployment verification successful")
        sys.exit(0)
    else:
        logger.error("Deployment verification failed")
        sys.exit(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
