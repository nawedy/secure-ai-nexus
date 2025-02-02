#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path
import logging
import json
from typing import Dict, List
import asyncio
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DependencyUpdater:
    """Automated dependency update management"""

    def __init__(self):
        self.requirements_file = Path('requirements.txt')
        self.update_log = Path('dependency_updates.log')
        self.update_schedule = {
            'major': timedelta(days=90),  # Every 3 months
            'minor': timedelta(days=30),  # Monthly
            'patch': timedelta(days=7)    # Weekly
        }

    async def check_updates(self) -> Dict[str, List[str]]:
        """Check for available updates"""
        updates = {
            'major': [],
            'minor': [],
            'patch': []
        }

        try:
            output = subprocess.check_output([
                sys.executable, '-m', 'pip', 'list', '--outdated',
                '--format=json'
            ])

            for pkg in json.loads(output):
                current = pkg['version']
                latest = pkg['latest_version']

                if self._is_major_update(current, latest):
                    updates['major'].append(pkg['name'])
                elif self._is_minor_update(current, latest):
                    updates['minor'].append(pkg['name'])
                else:
                    updates['patch'].append(pkg['name'])

        except Exception as e:
            logger.error(f"Failed to check updates: {str(e)}")

        return updates

    async def auto_update(self, level: str = 'patch'):
        """Perform automatic updates based on level"""
        try:
            updates = await self.check_updates()
            if not updates[level]:
                logger.info(f"No {level} updates available")
                return

            # Create backup
            await self._backup_requirements()

            # Update packages
            for package in updates[level]:
                try:
                    subprocess.check_call([
                        sys.executable, '-m', 'pip', 'install',
                        '--upgrade', package
                    ])
                    self._log_update(package, level)
                except Exception as e:
                    logger.error(f"Failed to update {package}: {str(e)}")

            # Update requirements.txt
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'freeze',
                '>', str(self.requirements_file)
            ])

            logger.info(f"Successfully updated {len(updates[level])} packages")

        except Exception as e:
            logger.error(f"Auto-update failed: {str(e)}")
            await self._restore_backup()

    def _log_update(self, package: str, level: str):
        """Log dependency updates"""
        with self.update_log.open('a') as f:
            f.write(
                f"{datetime.utcnow().isoformat()}: "
                f"Updated {package} ({level})\n"
            )

    async def _backup_requirements(self):
        """Backup requirements file"""
        backup_file = self.requirements_file.with_suffix('.bak')
        backup_file.write_text(self.requirements_file.read_text())

    async def _restore_backup(self):
        """Restore from backup"""
        backup_file = self.requirements_file.with_suffix('.bak')
        if backup_file.exists():
            self.requirements_file.write_text(backup_file.read_text())
            logger.info("Restored requirements from backup")

if __name__ == "__main__":
    async def main():
        updater = DependencyUpdater()
        await updater.auto_update()

    asyncio.run(main())
