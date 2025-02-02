#!/usr/bin/env python3
import pkg_resources
import sys
import subprocess
from pathlib import Path
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RequirementsValidator:
    """Validates project requirements and dependencies"""

    def __init__(self):
        self.requirements_file = Path('requirements.txt')
        self.constraints_file = Path('constraints.txt')

    def validate_requirements(self) -> List[str]:
        """Validate all requirements"""
        issues = []
        try:
            requirements = pkg_resources.parse_requirements(
                self.requirements_file.read_text()
            )

            for requirement in requirements:
                try:
                    pkg_resources.require(str(requirement))
                except (pkg_resources.VersionConflict,
                       pkg_resources.DistributionNotFound) as e:
                    issues.append(str(e))

        except Exception as e:
            logger.error(f"Failed to validate requirements: {str(e)}")
            issues.append(str(e))

        return issues

    def check_security_vulnerabilities(self):
        """Check for known security vulnerabilities"""
        try:
            subprocess.check_call([
                sys.executable, '-m', 'safety', 'check',
                '-r', str(self.requirements_file)
            ])
            logger.info("Security check passed")
        except subprocess.CalledProcessError as e:
            logger.error("Security vulnerabilities found!")
            sys.exit(1)

if __name__ == "__main__":
    validator = RequirementsValidator()

    issues = validator.validate_requirements()
    if issues:
        print("\nRequirement validation issues found:")
        for issue in issues:
            print(f"  • {issue}")
        sys.exit(1)

    validator.check_security_vulnerabilities()
