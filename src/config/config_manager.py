#!/usr/bin/env python3
import logging
from pathlib import Path
import yaml
from typing import Dict, Any, Optional
import json
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class ConfigurationManager:
    """Advanced configuration management system"""

    def __init__(self):
        self.config_path = Path('config')
        self.config_path.mkdir(exist_ok=True)
        self.config_history = self.config_path / 'config_history.json'
        self.active_config = {}
        self.validators = {}

    async def load_configuration(self):
        """Load and validate configuration"""
        try:
            # Load base configuration
            base_config = self._load_yaml('base_config.yaml')

            # Load environment overrides
            env_config = self._load_yaml(f"{self.get_environment()}_config.yaml")

            # Merge configurations
            self.active_config = self._merge_configs(base_config, env_config)

            # Validate configuration
            if await self._validate_configuration(self.active_config):
                await self._save_config_history()
                return self.active_config
            else:
                raise ValueError("Configuration validation failed")

        except Exception as e:
            logger.error(f"Configuration loading failed: {str(e)}")
            raise

    def register_validator(self, section: str, validator_func):
        """Register configuration validator"""
        self.validators[section] = validator_func

    async def update_configuration(self, updates: Dict[str, Any]):
        """Update configuration with validation"""
        try:
            # Create new config
            new_config = self._merge_configs(self.active_config, updates)

            # Validate new configuration
            if await self._validate_configuration(new_config):
                # Backup current config
                await self._backup_configuration()

                # Apply new configuration
                self.active_config = new_config
                await self._save_configuration()
                await self._notify_configuration_change()

                return True
            return False

        except Exception as e:
            logger.error(f"Configuration update failed: {str(e)}")
            return False

    async def _validate_configuration(self, config: Dict) -> bool:
        """Validate configuration using registered validators"""
        try:
            for section, validator in self.validators.items():
                if section in config:
                    if not await validator(config[section]):
                        logger.error(f"Validation failed for section: {section}")
                        return False
            return True
        except Exception as e:
            logger.error(f"Configuration validation failed: {str(e)}")
            return False

    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """Deep merge configuration dictionaries"""
        merged = base.copy()
        for key, value in override.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        return merged

    async def _save_config_history(self):
        """Save configuration change history"""
        history = []
        if self.config_history.exists():
            history = json.loads(self.config_history.read_text())

        history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'config': self.active_config,
            'user': self._get_current_user()
        })

        self.config_history.write_text(json.dumps(history, indent=2))

if __name__ == "__main__":
    config_manager = ConfigurationManager()
    asyncio.run(config_manager.load_configuration())
