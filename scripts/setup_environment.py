#!/usr/bin/env python3
import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(command, check=True):
    """Helper function to run commands and handle errors."""
    logger.info(f"Running: {' '.join(command)}")
    subprocess.run(command, check=check)

def setup_production_environment():
    """Sets up the production environment on the server."""
    logger.info("Setting up the production environment...")

    # Update the system and install necessary packages
    run_command([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])

    logger.info("Production environment setup completed.")
    
if __name__ == "__main__":    
    setup_production_environment()
