from cryptography.fernet import Fernet
from typing import Dict, Optional
import hashlib
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelProtection:
    def __init__(self, key_path: Optional[str] = None):
        self.key = self._load_or_generate_key(key_path)
        self.fernet = Fernet(self.key)
        self.model_registry: Dict[str, Dict] = {}

    def _load_or_generate_key(self, key_path: Optional[str]) -> bytes:
        """Load existing key or generate a new one"""
        if key_path and Path(key_path).exists():
            with open(key_path, 'rb') as f:
                return f.read()

        key = Fernet.generate_key()
        if key_path:
            with open(key_path, 'wb') as f:
                f.write(key)
        return key

    def encrypt_model(self, model_path: str, model_info: Dict) -> str:
        """Encrypt model file and store metadata"""
        try:
            # Read model file
            with open(model_path, 'rb') as f:
                model_data = f.read()

            # Calculate hash before encryption
            original_hash = hashlib.sha256(model_data).hexdigest()

            # Encrypt model
            encrypted_data = self.fernet.encrypt(model_data)

            # Generate encrypted model path
            encrypted_path = f"{model_path}.encrypted"

            # Save encrypted model
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_data)

            # Store metadata
            self.model_registry[model_path] = {
                'hash': original_hash,
                'encrypted_path': encrypted_path,
                'info': model_info,
                'status': 'encrypted'
            }

            logger.info(f"Model encrypted successfully: {model_path}")
            return encrypted_path

        except Exception as e:
            logger.error(f"Failed to encrypt model: {str(e)}")
            raise

    def decrypt_model(self, encrypted_path: str) -> bytes:
        """Decrypt model file and verify integrity"""
        try:
            # Read encrypted model
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()

            # Decrypt model
            decrypted_data = self.fernet.decrypt(encrypted_data)

            # Verify hash
            original_path = encrypted_path.replace('.encrypted', '')
            if original_path in self.model_registry:
                stored_hash = self.model_registry[original_path]['hash']
                current_hash = hashlib.sha256(decrypted_data).hexdigest()

                if stored_hash != current_hash:
                    raise ValueError("Model integrity check failed")

            logger.info(f"Model decrypted successfully: {encrypted_path}")
            return decrypted_data

        except Exception as e:
            logger.error(f"Failed to decrypt model: {str(e)}")
            raise

    def verify_model_integrity(self, model_path: str) -> bool:
        """Verify model integrity using stored hash"""
        try:
            if model_path not in self.model_registry:
                return False

            with open(model_path, 'rb') as f:
                model_data = f.read()

            current_hash = hashlib.sha256(model_data).hexdigest()
            stored_hash = self.model_registry[model_path]['hash']

            return current_hash == stored_hash

        except Exception as e:
            logger.error(f"Failed to verify model integrity: {str(e)}")
            return False

    def save_registry(self, registry_path: str):
        """Save model registry to file"""
        try:
            with open(registry_path, 'w') as f:
                json.dump(self.model_registry, f)
        except Exception as e:
            logger.error(f"Failed to save registry: {str(e)}")
            raise

    def load_registry(self, registry_path: str):
        """Load model registry from file"""
        try:
            with open(registry_path, 'r') as f:
                self.model_registry = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load registry: {str(e)}")
            raise
