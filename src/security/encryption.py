"""
This module provides encryption and key rotation functionalities using AES-256 and Azure Key Vault.
"""
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64
import os
from typing import Dict, Optional
from datetime import datetime, timedelta
from azure.keyvault.keys.aio import KeyClient
from azure.identity.aio import DefaultAzureCredential
import json
import logging

logger = logging.getLogger(__name__)

class SecurityException(Exception):
    """
    Custom exception for security-related errors.
    """
    pass


class EncryptionManager:
    """
    Manages encryption and decryption operations.
    """
    def __init__(self):
        """Initializes the EncryptionManager with a KeyRotationManager and an empty key cache."""
        self.key_manager = KeyRotationManager()
        self.key_cache = {}
        
    async def encrypt(self, data: Dict, key_rotation_policy: str) -> Dict:
        """Encrypts sensitive data using AES-256 with key rotation.

        Args:
            data (Dict): The data to encrypt.
            key_rotation_policy (str): The key rotation policy (e.g., '24h' for 24 hours).

        Returns:
            Dict: A dictionary containing the encrypted data, key ID, and encryption timestamp.
        """
        try:
            key = await self.key_manager.get_current_key(key_rotation_policy)
            data_str = json.dumps(data)
            iv = os.urandom(16)
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(data_str.encode()) + padder.finalize()
            encryptor = cipher.encryptor()
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            combined = base64.b64encode(iv + encrypted_data).decode('utf-8')
            
            return {
                'encrypted_data': combined,
                'key_id': self.key_manager.current_key_id,
                'encryption_timestamp': datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise SecurityException("Failed to encrypt data")
            
    async def decrypt(self, encrypted_package: Dict) -> Dict:
        """Decrypts data encrypted with AES-256.

        Args:
            encrypted_package (Dict): A dictionary containing the encrypted data and key ID.

        Returns:
            Dict: The decrypted data.
        """
        try:
            key = await self.key_manager.get_key_by_id(encrypted_package['key_id'])
            combined = base64.b64decode(encrypted_package['encrypted_data'])
            iv, encrypted_data = combined[:16], combined[16:]
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            
            # Decrypt
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # Unpad
            unpadder = padding.PKCS7(128).unpadder()
            data_str = unpadder.update(padded_data) + unpadder.finalize()
            
            # Parse JSON
            return json.loads(data_str.decode())
            
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise SecurityException("Failed to decrypt data")

class KeyRotationManager:
    """
    Manages key rotation and key retrieval from Azure Key Vault.
    """
    def __init__(self):
        """Initializes the KeyRotationManager with Azure credentials and Key Vault client."""
        self.credential = DefaultAzureCredential()  # Use asynchronous credential
        self.key_client = KeyClient(vault_url="https://secureai-kv.vault.azure.net/", credential=self.credential)  # Initialize asynchronous KeyClient
        self.key_cache = {}
        self.current_key_id = None
        
    async def get_current_key(self, rotation_policy: str) -> bytes:
        """Retrieves the current encryption key, rotating if necessary.

        Args:
            rotation_policy (str): The key rotation policy (e.g., '24h').

        Returns:
            bytes: The current encryption key.
        """
        try:
            if await self._should_rotate(rotation_policy):
                await self._rotate_key()
            if not self.current_key_id:
                await self._rotate_key()
                
            return await self.get_key_by_id(self.current_key_id)
        except Exception as e:
            logger.error(f"Key rotation error: {str(e)}")
            raise SecurityException("Failed to get encryption key")
            
    async def get_key_by_id(self, key_id: str) -> bytes:
        """Retrieves a specific key from the cache or Azure Key Vault by its ID.

        Args:
            key_id (str): The ID of the key to retrieve.

        Returns:
            bytes: The key bytes.
        """
        if key_id in self.key_cache:
            return self.key_cache[key_id]
            
        key = self.key_client.get_key(key_id)
        key_bytes = base64.b64decode(key.key.k)
        self.key_cache[key_id] = key_bytes
        
        return key_bytes
        
    async def _should_rotate(self, policy: str) -> bool:
        """Checks if key rotation is needed based on the rotation policy.

        Args:
            policy (str): The key rotation policy (e.g., '24h').

        Returns:
            bool: True if rotation is needed, False otherwise.
        """
        if not self.current_key_id:
            return True
            
        key = await self.key_client.get_key(self.current_key_id)
        age = datetime.utcnow() - key.properties.created_on
        
        rotation_hours = int(policy.replace('h', ''))
        return age > timedelta(hours=rotation_hours)
        
    async def _rotate_key(self):
        """Generates a new encryption key and stores it in Azure Key Vault."""
        new_key = os.urandom(32)
        
        key_name = f"encryption-key-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        key_value = base64.b64encode(new_key).decode('utf-8')
        
        stored_key = self.key_client.create_key(
            key_name,
            "oct-HSM",
            key_value=key_value
        )

        self.current_key_id = stored_key.id
        self.key_cache[stored_key.id] = new_key