from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import os
from typing import Dict, Optional
from datetime import datetime, timedelta
from azure.keyvault.keys import KeyClient
from azure.identity import DefaultAzureCredential
import json

class EncryptionManager:
    def __init__(self):
        self.key_manager = KeyRotationManager()
        self.key_cache = {}
        
    async def encrypt(self, data: Dict, key_rotation_policy: str) -> Dict:
        """Encrypt sensitive data with key rotation"""
        try:
            # Get current encryption key
            key = await self.key_manager.get_current_key(key_rotation_policy)
            
            # Convert data to string
            data_str = json.dumps(data)
            
            # Generate random IV
            iv = os.urandom(16)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            
            # Pad data
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(data_str.encode()) + padder.finalize()
            
            # Encrypt
            encryptor = cipher.encryptor()
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            
            # Combine IV and encrypted data
            combined = base64.b64encode(iv + encrypted_data).decode('utf-8')
            
            return {
                'encrypted_data': combined,
                'key_id': self.key_manager.current_key_id,
                'encryption_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise SecurityException("Failed to encrypt data")
            
    async def decrypt(self, encrypted_package: Dict) -> Dict:
        """Decrypt protected data"""
        try:
            # Get key by ID
            key = await self.key_manager.get_key_by_id(encrypted_package['key_id'])
            
            # Decode combined data
            combined = base64.b64decode(encrypted_package['encrypted_data'])
            iv = combined[:16]
            encrypted_data = combined[16:]
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            
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
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.key_client = KeyClient(
            vault_url="https://secureai-kv.vault.azure.net/",
            credential=self.credential
        )
        self.key_cache = {}
        self.current_key_id = None
        
    async def get_current_key(self, rotation_policy: str) -> bytes:
        """Get current encryption key with rotation"""
        try:
            # Check if we need to rotate
            if await self._should_rotate(rotation_policy):
                await self._rotate_key()
                
            # Get current key
            if not self.current_key_id:
                await self._rotate_key()
                
            return await self.get_key_by_id(self.current_key_id)
            
        except Exception as e:
            logger.error(f"Key rotation error: {str(e)}")
            raise SecurityException("Failed to get encryption key")
            
    async def get_key_by_id(self, key_id: str) -> bytes:
        """Get specific key by ID"""
        if key_id in self.key_cache:
            return self.key_cache[key_id]
            
        key = await self.key_client.get_key(key_id)
        key_bytes = base64.b64decode(key.key.k)
        self.key_cache[key_id] = key_bytes
        
        return key_bytes
        
    async def _should_rotate(self, policy: str) -> bool:
        """Check if key rotation is needed"""
        if not self.current_key_id:
            return True
            
        key = await self.key_client.get_key(self.current_key_id)
        age = datetime.utcnow() - key.properties.created_on
        
        rotation_hours = int(policy.replace('h', ''))
        return age > timedelta(hours=rotation_hours)
        
    async def _rotate_key(self):
        """Generate and store new key"""
        # Generate new key
        new_key = os.urandom(32)
        
        # Store in Key Vault
        key_name = f"encryption-key-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        key_value = base64.b64encode(new_key).decode('utf-8')
        
        stored_key = await self.key_client.create_key(
            key_name,
            "oct-HSM",
            key_value=key_value
        )
        
        self.current_key_id = stored_key.id
        self.key_cache[stored_key.id] = new_key 