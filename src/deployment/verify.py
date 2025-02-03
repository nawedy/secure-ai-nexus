import logging
import shutil
import psutil
import asyncio
from typing import Dict, List, Tuple
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class SystemRequirements:
    min_cpu_cores: int = 4
    min_memory_gb: int = 8
    min_storage_gb: int = 100
    min_network_mbps: int = 1000
    required_tools: List[str] = (
        "kubectl", "docker", "gcloud", "psql", "python3"
    )

class DeploymentVerifier:
    def __init__(self):
        self.requirements = SystemRequirements()
        self.fixes_applied = []

    async def verify_all(self) -> Tuple[bool, List[str]]:
        """
        Verify all deployment requirements and attempt fixes
        Returns: (success, applied_fixes)
        """
        checks = [
            self.verify_system_resources(),
            self.verify_tools(),
            self.verify_permissions(),
            self.verify_connectivity()
        ]

        results = await asyncio.gather(*checks, return_exceptions=True)
        success = all(not isinstance(r, Exception) and r for r in results)
        return success, self.fixes_applied

    async def verify_system_resources(self) -> bool:
        """Verify and fix system resource requirements"""
        try:
            # Check CPU
            cpu_cores = psutil.cpu_count()
            if cpu_cores < self.requirements.min_cpu_cores:
                if await self._request_more_cpu():
                    self.fixes_applied.append("Increased CPU allocation")
                else:
                    logger.error(f"Insufficient CPU cores: {cpu_cores}")
                    return False

            # Check Memory
            memory_gb = psutil.virtual_memory().total / (1024**3)
            if memory_gb < self.requirements.min_memory_gb:
                if await self._request_more_memory():
                    self.fixes_applied.append("Increased memory allocation")
                else:
                    logger.error(f"Insufficient memory: {memory_gb}GB")
                    return False

            # Check Storage
            storage_gb = shutil.disk_usage("/").total / (1024**3)
            if storage_gb < self.requirements.min_storage_gb:
                if await self._expand_storage():
                    self.fixes_applied.append("Expanded storage")
                else:
                    logger.error(f"Insufficient storage: {storage_gb}GB")
                    return False

            return True

        except Exception as e:
            logger.error(f"Resource verification failed: {str(e)}")
            return False

    async def verify_tools(self) -> bool:
        """Verify and install required tools"""
        missing_tools = []
        for tool in self.requirements.required_tools:
            if not shutil.which(tool):
                missing_tools.append(tool)

        if missing_tools:
            logger.warning(f"Missing tools: {missing_tools}")
            if await self._install_missing_tools(missing_tools):
                self.fixes_applied.extend(f"Installed {tool}" for tool in missing_tools)
                return True
            return False

        return True

    async def verify_permissions(self) -> bool:
        """Verify and fix required permissions"""
        try:
            # Check GCP permissions
            if not await self._verify_gcp_permissions():
                if await self._fix_gcp_permissions():
                    self.fixes_applied.append("Fixed GCP permissions")
                else:
                    return False

            # Check Kubernetes permissions
            if not await self._verify_k8s_permissions():
                if await self._fix_k8s_permissions():
                    self.fixes_applied.append("Fixed Kubernetes permissions")
                else:
                    return False

            return True

        except Exception as e:
            logger.error(f"Permission verification failed: {str(e)}")
            return False

    async def verify_connectivity(self) -> bool:
        """Verify and fix network connectivity"""
        try:
            # Check database connectivity
            if not await self._verify_db_connection():
                if await self._fix_db_connection():
                    self.fixes_applied.append("Fixed database connectivity")
                else:
                    return False

            # Check storage connectivity
            if not await self._verify_storage_connection():
                if await self._fix_storage_connection():
                    self.fixes_applied.append("Fixed storage connectivity")
                else:
                    return False

            return True

        except Exception as e:
            logger.error(f"Connectivity verification failed: {str(e)}")
            return False

    async def _request_more_cpu(self) -> bool:
        """Request CPU allocation increase"""
        try:
            # For cloud environments
            if self._is_cloud_environment():
                return await self._scale_cloud_resources("cpu")
            # For Kubernetes
            elif self._is_kubernetes():
                return await self._scale_kubernetes_resources("cpu")
            return False
        except Exception as e:
            logger.error(f"CPU allocation failed: {str(e)}")
            return False

    async def _request_more_memory(self) -> bool:
        """Request memory allocation increase"""
        try:
            if self._is_cloud_environment():
                return await self._scale_cloud_resources("memory")
            elif self._is_kubernetes():
                return await self._scale_kubernetes_resources("memory")
            return False
        except Exception as e:
            logger.error(f"Memory allocation failed: {str(e)}")
            return False

    async def _expand_storage(self) -> bool:
        """Expand storage allocation"""
        try:
            if self._is_cloud_environment():
                return await self._scale_cloud_resources("storage")
            elif self._is_kubernetes():
                return await self._expand_pvc()
            return False
        except Exception as e:
            logger.error(f"Storage expansion failed: {str(e)}")
            return False

    async def _install_missing_tools(self, tools: List[str]) -> bool:
        """Install missing tools"""
        try:
            for tool in tools:
                if tool == "kubectl":
                    await self._install_kubectl()
                elif tool == "docker":
                    await self._install_docker()
                elif tool == "gcloud":
                    await self._install_gcloud()
                elif tool == "psql":
                    await self._install_psql()
            return True
        except Exception as e:
            logger.error(f"Tool installation failed: {str(e)}")
            return False

    async def generate_report(self) -> Dict:
        """Generate deployment verification report"""
        success, fixes = await self.verify_all()
        return {
            "success": success,
            "fixes_applied": fixes,
            "system_status": {
                "cpu_cores": psutil.cpu_count(),
                "memory_gb": psutil.virtual_memory().total / (1024**3),
                "storage_gb": shutil.disk_usage("/").total / (1024**3)
            },
            "tools_status": {
                tool: bool(shutil.which(tool))
                for tool in self.requirements.required_tools
            },
            "timestamp": datetime.utcnow().isoformat()
        }
