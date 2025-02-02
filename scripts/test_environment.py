#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path
import logging
import json
from typing import Dict, List, Optional
import platform

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnvironmentTester:
    """Automated environment testing and validation"""

    def __init__(self):
        self.test_results: Dict[str, Dict] = {}
        self.environment_snapshot = Path('.env_snapshot.json')

    async def run_all_tests(self) -> Dict[str, Dict]:
        """Run comprehensive environment tests"""
        try:
            # System tests
            self.test_results['system'] = self._test_system_requirements()

            # Python environment tests
            self.test_results['python'] = self._test_python_environment()

            # Dependencies tests
            self.test_results['dependencies'] = await self._test_dependencies()

            # Configuration tests
            self.test_results['config'] = self._test_configurations()

            # Permissions tests
            self.test_results['permissions'] = self._test_permissions()

            return self.test_results
        except Exception as e:
            logger.error(f"Environment testing failed: {str(e)}")
            raise

    def _test_system_requirements(self) -> Dict:
        """Test system requirements"""
        return {
            'memory': self._check_memory(),
            'disk_space': self._check_disk_space(),
            'cpu_cores': self._check_cpu_cores(),
            'os_compatibility': self._check_os_compatibility()
        }

    def _test_python_environment(self) -> Dict:
        """Test Python environment"""
        return {
            'version': self._check_python_version(),
            'pip_version': self._check_pip_version(),
            'virtualenv': self._check_virtualenv(),
            'required_modules': self._check_required_modules()
        }

    async def _test_dependencies(self) -> Dict:
        """Test project dependencies"""
        return {
            'conflicts': await self._check_dependency_conflicts(),
            'versions': self._check_dependency_versions(),
            'security': await self._check_dependency_security()
        }

    def _test_configurations(self) -> Dict:
        """Test environment configurations"""
        return {
            'env_vars': self._check_environment_variables(),
            'paths': self._check_path_configurations(),
            'settings': self._check_settings_files()
        }

    def create_environment_snapshot(self):
        """Create a snapshot of current environment"""
        snapshot = {
            'timestamp': datetime.utcnow().isoformat(),
            'system': self._capture_system_info(),
            'python': self._capture_python_info(),
            'dependencies': self._capture_dependency_info(),
            'configurations': self._capture_config_info()
        }

        self.environment_snapshot.write_text(
            json.dumps(snapshot, indent=2)
        )
        logger.info("Environment snapshot created")

    def verify_against_snapshot(self) -> List[str]:
        """Verify current environment against snapshot"""
        if not self.environment_snapshot.exists():
            return ["No snapshot found"]

        snapshot = json.loads(self.environment_snapshot.read_text())
        current = self._capture_system_info()

        differences = []
        self._compare_states(snapshot, current, "", differences)

        return differences

    def _compare_states(self, snapshot: Dict, current: Dict, path: str, differences: List[str]):
        """Compare two environment states recursively"""
        for key in snapshot:
            if key not in current:
                differences.append(f"Missing: {path}{key}")
            elif isinstance(snapshot[key], dict):
                self._compare_states(
                    snapshot[key],
                    current.get(key, {}),
                    f"{path}{key}.",
                    differences
                )
            elif snapshot[key] != current.get(key):
                differences.append(
                    f"Changed: {path}{key} "
                    f"({snapshot[key]} → {current.get(key)})"
                )

if __name__ == "__main__":
    import asyncio

    async def main():
        tester = EnvironmentTester()
        results = await tester.run_all_tests()

        print("\n=== Environment Test Results ===")
        for category, result in results.items():
            status = "✅" if all(result.values()) else "❌"
            print(f"\n{status} {category.upper()}:")
            print(json.dumps(result, indent=2))

        # Create new snapshot if all tests pass
        if all(all(r.values()) for r in results.values()):
            tester.create_environment_snapshot()

    asyncio.run(main())
