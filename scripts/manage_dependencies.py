#!/usr/bin/env python3
import subprocess
import sys
import pkg_resources
from pathlib import Path
import logging
import json
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DependencyManager:
    """Manages project dependencies and conflicts"""

    def __init__(self):
        self.requirements_file = Path('requirements.txt')
        self.constraints_file = Path('constraints.txt')
        self.dependency_cache = Path('.dependency_cache.json')

    def check_conflicts(self) -> List[str]:
        """Check for dependency conflicts"""
        conflicts = []
        try:
            working_set = pkg_resources.working_set
            distributions = {d.key: d for d in working_set}

            for dist in distributions.values():
                for req in dist.requires():
                    if req.key in distributions:
                        installed = distributions[req.key]
                        if installed.version not in req.specifier:
                            conflicts.append(
                                f"Conflict: {dist.key} requires {req}, "
                                f"but {installed.version} is installed"
                            )
        except Exception as e:
            logger.error(f"Failed to check conflicts: {str(e)}")

        return conflicts

    def generate_constraints(self):
        """Generate constraints file from current environment"""
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'freeze',
                '--all', '--exclude-editable',
                '-o', str(self.constraints_file)
            ])
            logger.info(f"Constraints file generated: {self.constraints_file}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to generate constraints: {str(e)}")

    def update_dependencies(self):
        """Update dependencies while respecting constraints"""
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install',
                '-r', str(self.requirements_file),
                '-c', str(self.constraints_file),
                '--upgrade'
            ])
            logger.info("Dependencies updated successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to update dependencies: {str(e)}")

    def cache_dependencies(self):
        """Cache current dependency state"""
        try:
            deps = {
                pkg.key: pkg.version
                for pkg in pkg_resources.working_set
            }
            self.dependency_cache.write_text(json.dumps(deps, indent=2))
            logger.info("Dependency state cached")
        except Exception as e:
            logger.error(f"Failed to cache dependencies: {str(e)}")

    def verify_cache(self) -> bool:
        """Verify current state against cache"""
        try:
            if not self.dependency_cache.exists():
                return False

            cached = json.loads(self.dependency_cache.read_text())
            current = {
                pkg.key: pkg.version
                for pkg in pkg_resources.working_set
            }

            return cached == current
        except Exception as e:
            logger.error(f"Failed to verify cache: {str(e)}")
            return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Manage project dependencies')
    parser.add_argument('--check', action='store_true', help='Check for conflicts')
    parser.add_argument('--update', action='store_true', help='Update dependencies')
    parser.add_argument('--constraints', action='store_true', help='Generate constraints')
    args = parser.parse_args()

    manager = DependencyManager()

    if args.check:
        conflicts = manager.check_conflicts()
        if conflicts:
            print("\nDependency conflicts found:")
            for conflict in conflicts:
                print(f"  • {conflict}")
            sys.exit(1)

    if args.constraints:
        manager.generate_constraints()

    if args.update:
        manager.update_dependencies()
        manager.cache_dependencies()
