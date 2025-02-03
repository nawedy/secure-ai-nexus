import logging
from alembic import command
from alembic.config import Config
from pathlib import Path
import sys

logger = logging.getLogger(__name__)

class MigrationManager:
    def __init__(self):
        self.alembic_cfg = Config("alembic.ini")
        self.migrations_dir = Path("src/database/migrations/versions")

    def run_migrations(self):
        """Run all pending migrations"""
        try:
            logger.info("Running database migrations...")
            command.upgrade(self.alembic_cfg, "head")
            logger.info("Migrations completed successfully")
            return True
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            return False

    def rollback_migration(self, revision: str):
        """Rollback to a specific revision"""
        try:
            logger.info(f"Rolling back to revision {revision}...")
            command.downgrade(self.alembic_cfg, revision)
            logger.info("Rollback completed successfully")
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
            return False

    def verify_migrations(self):
        """Verify migration history"""
        try:
            logger.info("Verifying migration history...")
            command.check(self.alembic_cfg)
            logger.info("Migration history verified")
            return True
        except Exception as e:
            logger.error(f"Migration verification failed: {str(e)}")
            return False
