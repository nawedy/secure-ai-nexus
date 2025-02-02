#!/usr/bin/env python3
import logging
from pathlib import Path
import json
from datetime import datetime
import asyncio
from typing import Dict, List
import hashlib

logger = logging.getLogger(__name__)

class EnvironmentMonitor:
    """Monitors environment changes and modifications"""

    def __init__(self):
        self.history_file = Path('.environment_history.json')
        self.checksum_file = Path('.environment_checksums.json')
        self.watch_paths = [
            'requirements.txt',
            '.env',
            'config/',
            'migrations/'
        ]

    async def start_monitoring(self):
        """Start environment monitoring"""
        while True:
            try:
                changes = await self.check_for_changes()
                if changes:
                    await self.record_changes(changes)
                    await self.notify_changes(changes)
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")

    async def check_for_changes(self) -> List[Dict]:
        """Check for environment changes"""
        changes = []
        current_checksums = await self._calculate_checksums()

        if self.checksum_file.exists():
            previous = json.loads(self.checksum_file.read_text())
            changes = self._compare_checksums(previous, current_checksums)

        self.checksum_file.write_text(json.dumps(current_checksums))
        return changes

    async def record_changes(self, changes: List[Dict]):
        """Record environment changes"""
        history = []
        if self.history_file.exists():
            history = json.loads(self.history_file.read_text())

        history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'changes': changes
        })

        self.history_file.write_text(json.dumps(history, indent=2))

    async def notify_changes(self, changes: List[Dict]):
        """Notify about environment changes"""
        for change in changes:
            logger.warning(
                f"Environment change detected: {change['file']} "
                f"({change['type']})"
            )

    async def _calculate_checksums(self) -> Dict[str, str]:
        """Calculate checksums for watched files"""
        checksums = {}
        for path in self.watch_paths:
            p = Path(path)
            if p.exists():
                if p.is_file():
                    checksums[path] = self._file_checksum(p)
                else:
                    checksums[path] = self._directory_checksum(p)
        return checksums

    def _file_checksum(self, path: Path) -> str:
        """Calculate file checksum"""
        sha256 = hashlib.sha256()
        sha256.update(path.read_bytes())
        return sha256.hexdigest()

    def _directory_checksum(self, path: Path) -> str:
        """Calculate directory checksum"""
        sha256 = hashlib.sha256()
        for file in sorted(path.rglob('*')):
            if file.is_file():
                sha256.update(file.read_bytes())
        return sha256.hexdigest()

if __name__ == "__main__":
    monitor = EnvironmentMonitor()
    asyncio.run(monitor.start_monitoring())
