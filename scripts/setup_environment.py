#!/usr/bin/env python3
import subprocess
import sys
import pkg_resources
import venv
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REQUIRED_PIP_VERSION = '23.0.0'
REQUIRED_PYTHON_VERSION = (3, 9)
VENV_PATH = '.venv'

class EnvironmentSetup:
    """Manages development environment setup and validation"""

    def __init__(self):
        self.venv_path = Path(VENV_PATH)
        self.requirements_file = Path('requirements.txt')
        self.dev_requirements_file = Path('requirements-dev.txt')

    def check_python_version(self):
        """Verify Python version meets requirements"""
        current_version = sys.version_info[:2]
        if current_version < REQUIRED_PYTHON_VERSION:
            raise RuntimeError(
                f"Python {REQUIRED_PYTHON_VERSION[0]}.{REQUIRED_PYTHON_VERSION[1]} or higher required"
            )
        logger.info(f"Python version check passed: {sys.version}")

    def check_pip_version(self):
        """Verify pip version meets requirements"""
        try:
            import pip
            current_pip = pkg_resources.get_distribution('pip').version
            if pkg_resources.parse_version(current_pip) < pkg_resources.parse_version(REQUIRED_PIP_VERSION):
                logger.warning(f"Upgrading pip from {current_pip} to {REQUIRED_PIP_VERSION}")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        except Exception as e:
            raise RuntimeError(f"Failed to verify pip version: {str(e)}")
        logger.info("Pip version check passed")

    def create_virtual_environment(self):
        """Create virtual environment if it doesn't exist"""
        if not self.venv_path.exists():
            logger.info("Creating virtual environment...")
            venv.create(self.venv_path, with_pip=True)
            logger.info(f"Virtual environment created at {self.venv_path}")
        else:
            logger.info("Virtual environment already exists")

    def install_dependencies(self, dev=False):
        """Install project dependencies"""
        pip_cmd = [
            f"{self.venv_path}/bin/pip" if os.name != 'nt' else f"{self.venv_path}\\Scripts\\pip",
            "install",
            "-r",
            str(self.requirements_file)
        ]

        try:
            logger.info("Installing dependencies...")
            subprocess.check_call(pip_cmd)

            if dev:
                pip_cmd[-1] = str(self.dev_requirements_file)
                logger.info("Installing development dependencies...")
                subprocess.check_call(pip_cmd)

            logger.info("Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to install dependencies: {str(e)}")

    def validate_dependencies(self):
        """Validate installed dependencies"""
        try:
            import pkg_resources
            requirements = pkg_resources.parse_requirements(
                self.requirements_file.read_text()
            )
            for requirement in requirements:
                pkg_resources.require(str(requirement))
            logger.info("All dependencies validated successfully")
        except Exception as e:
            raise RuntimeError(f"Dependency validation failed: {str(e)}")

    def setup(self, dev=False):
        """Run complete environment setup"""
        try:
            self.check_python_version()
            self.check_pip_version()
            self.create_virtual_environment()
            self.install_dependencies(dev)
            self.validate_dependencies()
            logger.info("Environment setup completed successfully")
        except Exception as e:
            logger.error(f"Environment setup failed: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Setup development environment')
    parser.add_argument('--dev', action='store_true', help='Install development dependencies')
    args = parser.parse_args()

    setup = EnvironmentSetup()
    setup.setup(dev=args.dev)
